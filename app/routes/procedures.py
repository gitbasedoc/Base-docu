"""
Routes pour les procédures
"""

import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app import db
from app.models import Procedure, Category, Tag, ActionLog, Comment, Favorite
from app.services.file_service import FileService
from app.services.export_service import ExportService

procedures_bp = Blueprint('procedures', __name__)


@procedures_bp.route('/home')
@login_required
def home():
    """
    Page d'accueil
    """
    # Récupérer les procédures récemment modifiées
    recent_procedures = Procedure.query.filter_by(is_archived=False)\
        .order_by(Procedure.updated_at.desc())\
        .limit(10)\
        .all()

    # Récupérer les favoris de l'utilisateur (avec gestion d'erreur si table n'existe pas)
    favorite_procedures = []
    favorite_count = 0
    try:
        favorite_procedures = db.session.query(Procedure)\
            .join(Favorite, Favorite.procedure_id == Procedure.id)\
            .filter(Favorite.user_id == current_user.id)\
            .filter(Procedure.is_archived == False)\
            .order_by(Favorite.created_at.desc())\
            .limit(5)\
            .all()
        favorite_count = Favorite.query.filter_by(user_id=current_user.id).count()
    except Exception as e:
        # Table favorites n'existe pas encore, ignorer silencieusement
        pass

    # Statistiques
    stats = {
        'total_procedures': Procedure.query.filter_by(is_archived=False).count(),
        'total_categories': Category.query.count(),
        'total_tags': Tag.query.count(),
        'my_procedures': Procedure.query.filter_by(created_by=current_user.id, is_archived=False).count(),
        'favorite_count': favorite_count
    }

    return render_template('home.html', recent_procedures=recent_procedures, favorite_procedures=favorite_procedures, stats=stats)


@procedures_bp.route('/procedures')
@login_required
def list_procedures():
    """
    Liste des procédures avec pagination et filtres
    """
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Filtres
    category_id = request.args.get('category', type=int)
    tag_name = request.args.get('tag')
    archived = request.args.get('archived', 'false') == 'true'

    # Query de base
    query = Procedure.query

    # Appliquer les filtres
    if category_id:
        query = query.filter_by(category_id=category_id)

    if tag_name:
        tag = Tag.query.filter_by(name=tag_name).first()
        if tag:
            query = query.filter(Procedure.tags.contains(tag))

    query = query.filter_by(is_archived=archived)

    # Pagination
    procedures = query.order_by(Procedure.updated_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # Récupérer toutes les catégories pour le filtre
    categories = Category.query.order_by(Category.display_order).all()

    return render_template(
        'procedures/list.html',
        procedures=procedures,
        categories=categories,
        current_category=category_id,
        current_tag=tag_name,
        archived=archived
    )


@procedures_bp.route('/procedures/<int:procedure_id>')
@login_required
def view_procedure(procedure_id):
    """
    Vue détaillée d'une procédure
    """
    procedure = Procedure.query.get_or_404(procedure_id)

    # Incrémenter le compteur de vues (avec gestion d'erreur si colonne n'existe pas)
    try:
        procedure.increment_view()
        db.session.commit()
    except Exception:
        pass

    # Vérifier si la procédure est en favoris (avec gestion d'erreur si table n'existe pas)
    is_favorited = False
    try:
        is_favorited = Favorite.is_favorited(current_user.id, procedure.id)
    except Exception:
        pass

    # Récupérer les versions
    versions = procedure.versions.limit(10).all()

    # Récupérer les commentaires (seulement les commentaires parents, pas les réponses)
    comments = Comment.query.filter_by(
        procedure_id=procedure.id,
        parent_id=None
    ).order_by(Comment.created_at.desc()).all()

    return render_template(
        'procedures/detail.html',
        procedure=procedure,
        versions=versions,
        comments=comments,
        is_favorited=is_favorited
    )


@procedures_bp.route('/procedures/new', methods=['GET', 'POST'])
@login_required
def new_procedure():
    """
    Créer une nouvelle procédure
    """
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category_id = request.form.get('category_id', type=int)
        description = request.form.get('description', '').strip()
        estimated_time = request.form.get('estimated_time', type=int)
        tags_input = request.form.getlist('tags[]')

        # Validation
        if not title:
            flash('Le titre est requis', 'error')
            return redirect(url_for('procedures.new_procedure'))

        if not content:
            flash('Le contenu est requis', 'error')
            return redirect(url_for('procedures.new_procedure'))

        if not category_id:
            flash('La catégorie est requise', 'error')
            return redirect(url_for('procedures.new_procedure'))

        # Créer la procédure
        procedure = Procedure(
            title=title,
            content=content,
            category_id=category_id,
            description=description,
            estimated_time=estimated_time,
            created_by=current_user.id
        )

        db.session.add(procedure)
        db.session.flush()  # Pour obtenir l'ID

        # Ajouter les tags
        for tag_name in tags_input:
            tag_name = tag_name.strip().lower()
            if tag_name:
                tag = Tag.get_or_create(tag_name)
                procedure.tags.append(tag)
                tag.increment_usage()

        # Créer la première version
        procedure.create_version(current_user.id)

        # Audit log
        ActionLog.log_action(
            action_type='create',
            entity_type='procedure',
            entity_id=procedure.id,
            entity_name=procedure.title,
            details=json.dumps({'category_id': category_id, 'tags': tags_input}),
            user_id=current_user.id,
            request_obj=request
        )

        db.session.commit()

        flash('Procédure créée avec succès', 'success')
        return redirect(url_for('procedures.view_procedure', procedure_id=procedure.id))

    # GET: Afficher le formulaire
    categories = Category.query.order_by(Category.display_order).all()
    return render_template('procedures/edit.html', procedure=None, categories=categories)


@procedures_bp.route('/procedures/<int:procedure_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_procedure(procedure_id):
    """
    Modifier une procédure existante
    """
    procedure = Procedure.query.get_or_404(procedure_id)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category_id = request.form.get('category_id', type=int)
        description = request.form.get('description', '').strip()
        estimated_time = request.form.get('estimated_time', type=int)
        tags_input = request.form.getlist('tags[]')

        # Validation
        if not title or not content or not category_id:
            flash('Titre, contenu et catégorie sont requis', 'error')
            return redirect(url_for('procedures.edit_procedure', procedure_id=procedure_id))

        # Sauvegarder la version si le contenu a changé
        if procedure.content != content:
            procedure.create_version(current_user.id)

        # Mettre à jour la procédure
        procedure.title = title
        procedure.content = content
        procedure.category_id = category_id
        procedure.description = description
        procedure.estimated_time = estimated_time

        # Mettre à jour les tags
        # Décrémenter usage_count des anciens tags
        for tag in procedure.tags:
            tag.decrement_usage()

        procedure.tags = []

        # Ajouter les nouveaux tags
        for tag_name in tags_input:
            tag_name = tag_name.strip().lower()
            if tag_name:
                tag = Tag.get_or_create(tag_name)
                procedure.tags.append(tag)
                tag.increment_usage()

        # Audit log
        ActionLog.log_action(
            action_type='update',
            entity_type='procedure',
            entity_id=procedure.id,
            entity_name=procedure.title,
            details=json.dumps({'category_id': category_id, 'tags': tags_input}),
            user_id=current_user.id,
            request_obj=request
        )

        db.session.commit()

        flash('Procédure mise à jour avec succès', 'success')
        return redirect(url_for('procedures.view_procedure', procedure_id=procedure.id))

    # GET: Afficher le formulaire
    categories = Category.query.order_by(Category.display_order).all()
    return render_template('procedures/edit.html', procedure=procedure, categories=categories)


@procedures_bp.route('/procedures/<int:procedure_id>/archive', methods=['POST'])
@login_required
def archive_procedure(procedure_id):
    """
    Archiver une procédure
    """
    procedure = Procedure.query.get_or_404(procedure_id)

    procedure.is_archived = True

    # Audit log
    ActionLog.log_action(
        action_type='archive',
        entity_type='procedure',
        entity_id=procedure.id,
        entity_name=procedure.title,
        user_id=current_user.id,
        request_obj=request
    )

    db.session.commit()

    flash('Procédure archivée', 'success')
    return redirect(url_for('procedures.list_procedures'))


@procedures_bp.route('/procedures/<int:procedure_id>/restore', methods=['POST'])
@login_required
def restore_procedure(procedure_id):
    """
    Restaurer une procédure archivée
    """
    procedure = Procedure.query.get_or_404(procedure_id)

    procedure.is_archived = False

    # Audit log
    ActionLog.log_action(
        action_type='restore',
        entity_type='procedure',
        entity_id=procedure.id,
        entity_name=procedure.title,
        user_id=current_user.id,
        request_obj=request
    )

    db.session.commit()

    flash('Procédure restaurée', 'success')
    return redirect(url_for('procedures.view_procedure', procedure_id=procedure.id))


@procedures_bp.route('/procedures/<int:procedure_id>/delete', methods=['POST'])
@login_required
def delete_procedure(procedure_id):
    """
    Supprimer définitivement une procédure (admin uniquement)
    """
    if not current_user.is_admin:
        abort(403)

    procedure = Procedure.query.get_or_404(procedure_id)
    procedure_title = procedure.title  # Sauvegarder avant suppression

    # Supprimer les fichiers associés
    file_service = FileService()
    for attachment in procedure.attachments:
        file_service.delete_file(attachment.storage_path)

    # Décrémenter usage_count des tags
    for tag in procedure.tags:
        tag.decrement_usage()

    # Audit log (avant suppression pour avoir l'ID)
    ActionLog.log_action(
        action_type='delete',
        entity_type='procedure',
        entity_id=procedure.id,
        entity_name=procedure_title,
        user_id=current_user.id,
        request_obj=request
    )

    # Supprimer la procédure (cascade supprimera attachments et versions)
    db.session.delete(procedure)
    db.session.commit()

    flash('Procédure supprimée définitivement', 'success')
    return redirect(url_for('procedures.list_procedures'))


@procedures_bp.route('/procedures/<int:procedure_id>/useful', methods=['POST'])
def mark_useful(procedure_id):
    """
    Marquer une procédure comme utile (AJAX)
    """
    from flask import jsonify

    procedure = Procedure.query.get_or_404(procedure_id)

    # Incrémenter le compteur
    procedure.increment_useful()

    # Audit log (optionnel pour les votes, mais utile pour tracking)
    ActionLog.log_action(
        action_type='useful',
        entity_type='procedure',
        entity_id=procedure.id,
        entity_name=procedure.title,
        user_id=current_user.id if current_user.is_authenticated else None,
        request_obj=request
    )

    db.session.commit()

    return jsonify({
        'success': True,
        'useful_count': procedure.useful_count
    })


@procedures_bp.route('/procedures/<int:procedure_id>/comments', methods=['POST'])
@login_required
def add_comment(procedure_id):
    """
    Ajouter un commentaire à une procédure
    """
    from flask import jsonify

    procedure = Procedure.query.get_or_404(procedure_id)
    content = request.form.get('content', '').strip()
    parent_id = request.form.get('parent_id', type=int)

    if not content:
        return jsonify({'success': False, 'error': 'Le commentaire ne peut pas être vide'}), 400

    comment = Comment(
        procedure_id=procedure.id,
        user_id=current_user.id,
        parent_id=parent_id,
        content=content
    )

    db.session.add(comment)

    # Audit log
    ActionLog.log_action(
        action_type='comment',
        entity_type='procedure',
        entity_id=procedure.id,
        entity_name=procedure.title,
        details=json.dumps({'comment_id': comment.id, 'is_reply': parent_id is not None}),
        user_id=current_user.id,
        request_obj=request
    )

    db.session.commit()

    return jsonify({
        'success': True,
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'user_name': current_user.full_name,
            'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M'),
            'parent_id': comment.parent_id
        }
    })


@procedures_bp.route('/procedures/<int:procedure_id>/comments/<int:comment_id>/edit', methods=['POST'])
@login_required
def edit_comment(procedure_id, comment_id):
    """
    Modifier un commentaire
    """
    from flask import jsonify

    comment = Comment.query.get_or_404(comment_id)

    # Vérifier que l'utilisateur est l'auteur ou admin
    if comment.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403

    content = request.form.get('content', '').strip()

    if not content:
        return jsonify({'success': False, 'error': 'Le commentaire ne peut pas être vide'}), 400

    comment.content = content
    comment.is_edited = True

    # Audit log
    ActionLog.log_action(
        action_type='update',
        entity_type='comment',
        entity_id=comment.id,
        entity_name=f'Comment on {comment.procedure.title}',
        user_id=current_user.id,
        request_obj=request
    )

    db.session.commit()

    return jsonify({
        'success': True,
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'is_edited': True
        }
    })


@procedures_bp.route('/procedures/<int:procedure_id>/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(procedure_id, comment_id):
    """
    Supprimer un commentaire
    """
    from flask import jsonify

    comment = Comment.query.get_or_404(comment_id)

    # Vérifier que l'utilisateur est l'auteur ou admin
    if comment.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403

    # Audit log (avant suppression)
    ActionLog.log_action(
        action_type='delete',
        entity_type='comment',
        entity_id=comment.id,
        entity_name=f'Comment on {comment.procedure.title}',
        user_id=current_user.id,
        request_obj=request
    )

    db.session.delete(comment)
    db.session.commit()

    return jsonify({'success': True})


@procedures_bp.route('/procedures/<int:procedure_id>/export/pdf')
@login_required
def export_pdf(procedure_id):
    """
    Exporter une procédure en PDF
    """
    from flask import send_file
    import re

    procedure = Procedure.query.get_or_404(procedure_id)

    try:
        # Générer le PDF
        pdf_file = ExportService.generate_pdf(procedure)

        # Nettoyer le nom du fichier
        filename = re.sub(r'[^\w\s-]', '', procedure.title)
        filename = re.sub(r'[-\s]+', '-', filename)
        filename = f'{filename}-{procedure.id}.pdf'

        # Audit log
        ActionLog.log_action(
            action_type='export',
            entity_type='procedure',
            entity_id=procedure.id,
            entity_name=procedure.title,
            details=json.dumps({'format': 'pdf'}),
            user_id=current_user.id,
            request_obj=request
        )
        db.session.commit()

        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except ImportError as e:
        flash(f'Erreur: {str(e)}', 'error')
        return redirect(url_for('procedures.view_procedure', procedure_id=procedure_id))
    except Exception as e:
        flash(f'Erreur lors de la génération du PDF: {str(e)}', 'error')
        return redirect(url_for('procedures.view_procedure', procedure_id=procedure_id))


@procedures_bp.route('/procedures/<int:procedure_id>/export/docx')
@login_required
def export_docx(procedure_id):
    """
    Exporter une procédure en DOCX
    """
    from flask import send_file
    import re

    procedure = Procedure.query.get_or_404(procedure_id)

    try:
        # Générer le DOCX
        docx_file = ExportService.generate_docx(procedure)

        # Nettoyer le nom du fichier
        filename = re.sub(r'[^\w\s-]', '', procedure.title)
        filename = re.sub(r'[-\s]+', '-', filename)
        filename = f'{filename}-{procedure.id}.docx'

        # Audit log
        ActionLog.log_action(
            action_type='export',
            entity_type='procedure',
            entity_id=procedure.id,
            entity_name=procedure.title,
            details=json.dumps({'format': 'docx'}),
            user_id=current_user.id,
            request_obj=request
        )
        db.session.commit()

        return send_file(
            docx_file,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        )
    except ImportError as e:
        flash(f'Erreur: {str(e)}', 'error')
        return redirect(url_for('procedures.view_procedure', procedure_id=procedure_id))
    except Exception as e:
        flash(f'Erreur lors de la génération du DOCX: {str(e)}', 'error')
        return redirect(url_for('procedures.view_procedure', procedure_id=procedure_id))


@procedures_bp.route('/procedures/<int:procedure_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(procedure_id):
    """
    Ajouter ou retirer une procédure des favoris (AJAX)
    """
    from flask import jsonify

    procedure = Procedure.query.get_or_404(procedure_id)

    # Toggle favorite
    added, favorite = Favorite.toggle(current_user.id, procedure.id)

    # Audit log
    ActionLog.log_action(
        action_type='favorite' if added else 'unfavorite',
        entity_type='procedure',
        entity_id=procedure.id,
        entity_name=procedure.title,
        user_id=current_user.id,
        request_obj=request
    )

    db.session.commit()

    return jsonify({
        'success': True,
        'favorited': added
    })
