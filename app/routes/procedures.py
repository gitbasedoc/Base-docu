"""
Routes pour les procédures
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app import db
from app.models import Procedure, Category, Tag
from app.services.file_service import FileService

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

    # Statistiques
    stats = {
        'total_procedures': Procedure.query.filter_by(is_archived=False).count(),
        'total_categories': Category.query.count(),
        'total_tags': Tag.query.count(),
        'my_procedures': Procedure.query.filter_by(created_by=current_user.id, is_archived=False).count()
    }

    return render_template('home.html', recent_procedures=recent_procedures, stats=stats)


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

    # Récupérer les versions
    versions = procedure.versions.limit(10).all()

    return render_template(
        'procedures/detail.html',
        procedure=procedure,
        versions=versions
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

    # Supprimer les fichiers associés
    file_service = FileService()
    for attachment in procedure.attachments:
        file_service.delete_file(attachment.storage_path)

    # Décrémenter usage_count des tags
    for tag in procedure.tags:
        tag.decrement_usage()

    # Supprimer la procédure (cascade supprimera attachments et versions)
    db.session.delete(procedure)
    db.session.commit()

    flash('Procédure supprimée définitivement', 'success')
    return redirect(url_for('procedures.list_procedures'))
