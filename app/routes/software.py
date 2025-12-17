"""
Routes pour les Logiciels (outils et logiciels utiles)
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user

from app import db
from app.models import Software, Category

software_bp = Blueprint('software', __name__)


@software_bp.route('/software')
def list_software():
    """
    Liste des logiciels avec filtres et pagination
    """
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Filtres
    category_id = request.args.get('category', type=int)
    platform = request.args.get('platform')
    is_free = request.args.get('free')

    # Query de base
    query = Software.query

    # Appliquer les filtres
    if category_id:
        query = query.filter_by(category_id=category_id)

    if platform:
        query = query.filter_by(platform=platform)

    if is_free == 'true':
        query = query.filter_by(is_free=True)
    elif is_free == 'false':
        query = query.filter_by(is_free=False)

    # Pagination
    software_list = query.order_by(Software.useful_count.desc(), Software.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # Récupérer toutes les catégories pour le filtre
    categories = Category.query.order_by(Category.display_order).all()

    # Récupérer les plateformes uniques
    platforms = db.session.query(Software.platform).distinct().filter(Software.platform.isnot(None)).all()
    platforms = [p[0] for p in platforms]

    return render_template(
        'software/list.html',
        software_list=software_list,
        categories=categories,
        platforms=platforms,
        current_category=category_id,
        current_platform=platform,
        current_free=is_free
    )


@software_bp.route('/software/<int:software_id>')
def view_software(software_id):
    """
    Vue détaillée d'un logiciel
    """
    software = Software.query.get_or_404(software_id)

    return render_template(
        'software/detail.html',
        software=software
    )


@software_bp.route('/software/new', methods=['GET', 'POST'])
@login_required
def new_software():
    """
    Ajouter un nouveau logiciel
    """
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        url = request.form.get('url', '').strip()
        category_id = request.form.get('category_id', type=int)
        platform = request.form.get('platform', '').strip()
        is_free = request.form.get('is_free') == 'on'

        # Validation
        if not name:
            flash('Le nom est requis', 'error')
            return redirect(url_for('software.new_software'))

        if not description:
            flash('La description est requise', 'error')
            return redirect(url_for('software.new_software'))

        if not url:
            flash('L\'URL est requise', 'error')
            return redirect(url_for('software.new_software'))

        if not category_id:
            flash('La catégorie est requise', 'error')
            return redirect(url_for('software.new_software'))

        # Créer le logiciel
        software = Software(
            name=name,
            description=description,
            url=url,
            category_id=category_id,
            platform=platform if platform else None,
            is_free=is_free,
            added_by=current_user.id
        )

        db.session.add(software)
        db.session.commit()

        flash('Logiciel ajouté avec succès', 'success')
        return redirect(url_for('software.view_software', software_id=software.id))

    # GET: Afficher le formulaire
    categories = Category.query.order_by(Category.display_order).all()
    return render_template('software/edit.html', software=None, categories=categories)


@software_bp.route('/software/<int:software_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_software(software_id):
    """
    Modifier un logiciel existant
    """
    software = Software.query.get_or_404(software_id)

    # Vérifier les permissions (contributeur ou admin)
    if software.added_by != current_user.id and not current_user.is_admin:
        flash('Vous n\'avez pas la permission de modifier ce logiciel', 'error')
        return redirect(url_for('software.view_software', software_id=software_id))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        url = request.form.get('url', '').strip()
        category_id = request.form.get('category_id', type=int)
        platform = request.form.get('platform', '').strip()
        is_free = request.form.get('is_free') == 'on'

        # Validation
        if not name or not description or not url or not category_id:
            flash('Nom, description, URL et catégorie sont requis', 'error')
            return redirect(url_for('software.edit_software', software_id=software_id))

        # Mettre à jour le logiciel
        software.name = name
        software.description = description
        software.url = url
        software.category_id = category_id
        software.platform = platform if platform else None
        software.is_free = is_free

        db.session.commit()

        flash('Logiciel mis à jour avec succès', 'success')
        return redirect(url_for('software.view_software', software_id=software_id))

    # GET: Afficher le formulaire
    categories = Category.query.order_by(Category.display_order).all()
    return render_template('software/edit.html', software=software, categories=categories)


@software_bp.route('/software/<int:software_id>/delete', methods=['POST'])
@login_required
def delete_software(software_id):
    """
    Supprimer un logiciel
    """
    software = Software.query.get_or_404(software_id)

    # Vérifier les permissions (contributeur ou admin)
    if software.added_by != current_user.id and not current_user.is_admin:
        flash('Vous n\'avez pas la permission de supprimer ce logiciel', 'error')
        return redirect(url_for('software.view_software', software_id=software_id))

    db.session.delete(software)
    db.session.commit()

    flash('Logiciel supprimé avec succès', 'success')
    return redirect(url_for('software.list_software'))


@software_bp.route('/software/<int:software_id>/useful', methods=['POST'])
def mark_useful(software_id):
    """
    Marquer un logiciel comme utile (AJAX)
    """
    software = Software.query.get_or_404(software_id)

    # Incrémenter le compteur
    software.increment_useful()
    db.session.commit()

    return jsonify({
        'success': True,
        'useful_count': software.useful_count
    })
