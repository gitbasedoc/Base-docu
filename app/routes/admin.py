"""
Routes d'administration
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps

from app import db
from app.models import User, Category, Setting

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """
    Décorateur pour restreindre l'accès aux admins
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accès réservé aux administrateurs', 'error')
            return redirect(url_for('procedures.home'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """
    Tableau de bord administration
    """
    # Statistiques
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_users = User.query.filter_by(is_admin=True).count()
    total_categories = Category.query.count()

    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         active_users=active_users,
                         admin_users=admin_users,
                         total_categories=total_categories)


@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    """
    Liste des utilisateurs
    """
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(user_id):
    """
    Activer/Désactiver un utilisateur
    """
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Vous ne pouvez pas désactiver votre propre compte', 'error')
        return redirect(url_for('admin.list_users'))

    user.is_active = not user.is_active
    db.session.commit()

    status = 'activé' if user.is_active else 'désactivé'
    flash(f'Utilisateur {user.full_name} {status}', 'success')
    return redirect(url_for('admin.list_users'))


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_user_admin(user_id):
    """
    Promouvoir/Rétrograder admin
    """
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Vous ne pouvez pas modifier vos propres droits admin', 'error')
        return redirect(url_for('admin.list_users'))

    user.is_admin = not user.is_admin
    db.session.commit()

    status = 'promu administrateur' if user.is_admin else 'rétrogradé utilisateur'
    flash(f'{user.full_name} {status}', 'success')
    return redirect(url_for('admin.list_users'))


@admin_bp.route('/categories')
@login_required
@admin_required
def list_categories():
    """
    Liste des catégories
    """
    categories = Category.query.order_by(Category.display_order).all()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/categories/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_category():
    """
    Créer une nouvelle catégorie
    """
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        color_code = request.form.get('color_code', '#00ff88').strip()
        display_order = request.form.get('display_order', type=int) or 0

        if not name:
            flash('Le nom est requis', 'error')
            return redirect(url_for('admin.new_category'))

        category = Category(
            name=name,
            description=description,
            color_code=color_code,
            display_order=display_order
        )

        db.session.add(category)
        db.session.commit()

        flash(f'Catégorie "{name}" créée', 'success')
        return redirect(url_for('admin.list_categories'))

    return render_template('admin/category_form.html', category=None)


@admin_bp.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(category_id):
    """
    Modifier une catégorie
    """
    category = Category.query.get_or_404(category_id)

    if request.method == 'POST':
        category.name = request.form.get('name', '').strip()
        category.description = request.form.get('description', '').strip()
        category.color_code = request.form.get('color_code', '#00ff88').strip()
        category.display_order = request.form.get('display_order', type=int) or 0

        if not category.name:
            flash('Le nom est requis', 'error')
            return redirect(url_for('admin.edit_category', category_id=category_id))

        db.session.commit()

        flash(f'Catégorie "{category.name}" mise à jour', 'success')
        return redirect(url_for('admin.list_categories'))

    return render_template('admin/category_form.html', category=category)


@admin_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    """
    Supprimer une catégorie
    """
    category = Category.query.get_or_404(category_id)

    # Vérifier si la catégorie a des procédures
    if category.procedures.count() > 0:
        flash(f'Impossible de supprimer "{category.name}" : elle contient {category.procedures.count()} procédure(s)', 'error')
        return redirect(url_for('admin.list_categories'))

    name = category.name
    db.session.delete(category)
    db.session.commit()

    flash(f'Catégorie "{name}" supprimée', 'success')
    return redirect(url_for('admin.list_categories'))


@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """
    Paramètres de l'application
    """
    settings = Setting.query.all()
    settings_dict = {s.key: s.value for s in settings}

    return render_template('admin/settings.html', settings=settings_dict)


@admin_bp.route('/settings/update', methods=['POST'])
@login_required
@admin_required
def update_settings():
    """
    Mettre à jour les paramètres
    """
    for key, value in request.form.items():
        if key == 'csrf_token':
            continue

        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            db.session.add(setting)

    db.session.commit()
    flash('Paramètres mis à jour', 'success')
    return redirect(url_for('admin.settings'))
