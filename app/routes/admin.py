"""
Routes d'administration
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps

from app import db
from app.models import User, Setting, Procedure, Script, FAQ, Software

# Imports optionnels pour mode serveur
try:
    from app.models import Category, ActionLog, Favorite, Suggestion
except ImportError:
    Category = ActionLog = Favorite = Suggestion = None

from sqlalchemy import func
from datetime import datetime, timedelta

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
    Tableau de bord administration avec statistiques complètes
    """
    # Statistiques utilisateurs
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_users = User.query.filter_by(is_admin=True).count()

    # Statistiques contenu
    total_procedures = Procedure.query.filter_by(is_archived=False).count()
    archived_procedures = Procedure.query.filter_by(is_archived=True).count()
    total_scripts = Script.query.filter_by(status='published').count()
    total_faqs = FAQ.query.filter_by(is_published=True).count()
    total_software = Software.query.count()
    total_categories = Category.query.count()

    # Statistiques d'engagement (avec gestion d'erreur si colonnes n'existent pas)
    total_views = 0
    total_likes = 0
    total_favorites = 0
    top_viewed = []
    top_liked = []
    top_favorited = []

    try:
        total_views = db.session.query(func.sum(Procedure.views_count)).scalar() or 0
    except Exception:
        pass

    try:
        total_likes = db.session.query(func.sum(Procedure.useful_count)).scalar() or 0
    except Exception:
        pass

    try:
        total_favorites = Favorite.query.count()
    except Exception:
        pass

    # Top 5 procédures par vues
    try:
        top_viewed = Procedure.query.filter_by(is_archived=False)\
            .order_by(Procedure.views_count.desc())\
            .limit(5)\
            .all()
    except Exception:
        pass

    # Top 5 procédures par likes
    try:
        top_liked = Procedure.query.filter_by(is_archived=False)\
            .order_by(Procedure.useful_count.desc())\
            .limit(5)\
            .all()
    except Exception:
        pass

    # Top 5 procédures les plus favoritées
    try:
        top_favorited = db.session.query(
            Procedure,
            func.count(Favorite.id).label('favorite_count')
        ).join(Favorite, Favorite.procedure_id == Procedure.id)\
         .filter(Procedure.is_archived == False)\
         .group_by(Procedure.id)\
         .order_by(func.count(Favorite.id).desc())\
         .limit(5)\
         .all()
    except Exception:
        pass

    # Activité récente (7 derniers jours)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_actions = ActionLog.query.filter(
        ActionLog.created_at >= week_ago
    ).count()

    # Actions par type
    actions_by_type = db.session.query(
        ActionLog.action_type,
        func.count(ActionLog.id).label('count')
    ).group_by(ActionLog.action_type).all()

    # Utilisateurs les plus actifs
    top_contributors = db.session.query(
        User,
        func.count(Procedure.id).label('procedure_count')
    ).join(Procedure, Procedure.created_by == User.id)\
     .group_by(User.id)\
     .order_by(func.count(Procedure.id).desc())\
     .limit(5)\
     .all()

    return render_template('admin/dashboard.html',
                         # Utilisateurs
                         total_users=total_users,
                         active_users=active_users,
                         admin_users=admin_users,
                         # Contenu
                         total_procedures=total_procedures,
                         archived_procedures=archived_procedures,
                         total_scripts=total_scripts,
                         total_faqs=total_faqs,
                         total_software=total_software,
                         total_categories=total_categories,
                         # Engagement
                         total_views=total_views,
                         total_likes=total_likes,
                         total_favorites=total_favorites,
                         # Tops
                         top_viewed=top_viewed,
                         top_liked=top_liked,
                         top_favorited=top_favorited,
                         top_contributors=top_contributors,
                         # Activité
                         recent_actions=recent_actions,
                         actions_by_type=actions_by_type)


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


@admin_bp.route('/users/<int:user_id>/change-role', methods=['POST'])
@login_required
@admin_required
def change_user_role(user_id):
    """
    Changer le rôle d'un utilisateur
    """
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Vous ne pouvez pas modifier votre propre rôle', 'error')
        return redirect(url_for('admin.list_users'))

    new_role = request.form.get('role', 'viewer')

    # Valider que le rôle est valide
    if new_role not in ['viewer', 'contributor', 'admin']:
        flash('Rôle invalide', 'error')
        return redirect(url_for('admin.list_users'))

    old_role = user.role
    user.role = new_role

    # Synchroniser is_admin avec le nouveau rôle
    user.is_admin = (new_role == 'admin')

    db.session.commit()

    role_labels = {
        'viewer': '👁️ Viewer',
        'contributor': '✍️ Contributor',
        'admin': '👑 Admin'
    }

    flash(f'Rôle de {user.full_name} modifié: {role_labels[old_role]} → {role_labels[new_role]}', 'success')

    # Log l'action
    # log_action('user_role_changed', user_id=user.id, details=f'Rôle modifié de {old_role} à {new_role}')

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


@admin_bp.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    """
    Afficher l'historique d'audit
    """
    # Filtres
    action_type = request.args.get('action_type')
    entity_type = request.args.get('entity_type')
    user_id = request.args.get('user_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 50

    # Construire la requête
    query = ActionLog.query

    if action_type:
        query = query.filter_by(action_type=action_type)
    if entity_type:
        query = query.filter_by(entity_type=entity_type)
    if user_id:
        query = query.filter_by(user_id=user_id)

    # Paginer
    pagination = query.order_by(ActionLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    logs = pagination.items

    # Stats pour le dashboard
    total_logs = ActionLog.query.count()
    recent_actions = ActionLog.query.order_by(ActionLog.created_at.desc()).limit(10).all()

    # Actions par type
    from sqlalchemy import func
    actions_by_type = db.session.query(
        ActionLog.action_type,
        func.count(ActionLog.id).label('count')
    ).group_by(ActionLog.action_type).all()

    return render_template('admin/audit_logs.html',
                         logs=logs,
                         pagination=pagination,
                         total_logs=total_logs,
                         recent_actions=recent_actions,
                         actions_by_type=actions_by_type,
                         action_type_filter=action_type,
                         entity_type_filter=entity_type,
                         user_id_filter=user_id)


@admin_bp.route('/suggestions')
@login_required
@admin_required
def manage_suggestions():
    """
    Gérer toutes les suggestions (admin)
    """
    # Filtres
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')
    page = request.args.get('page', 1, type=int)
    per_page = 30

    # Construire la requête
    query = Suggestion.query

    if status_filter:
        query = query.filter_by(status=status_filter)

    if category_filter:
        query = query.filter_by(category=category_filter)

    # Paginer
    pagination = query.order_by(Suggestion.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    suggestions = pagination.items

    # Statistiques
    stats = {
        'total': Suggestion.query.count(),
        'pending': Suggestion.query.filter_by(status='pending').count(),
        'reviewed': Suggestion.query.filter_by(status='reviewed').count(),
        'accepted': Suggestion.query.filter_by(status='accepted').count(),
        'rejected': Suggestion.query.filter_by(status='rejected').count(),
        'implemented': Suggestion.query.filter_by(status='implemented').count(),
    }

    return render_template('admin/suggestions.html',
                         suggestions=suggestions,
                         pagination=pagination,
                         stats=stats,
                         status_filter=status_filter,
                         category_filter=category_filter)


@admin_bp.route('/suggestions/<int:suggestion_id>/update', methods=['POST'])
@login_required
@admin_required
def update_suggestion(suggestion_id):
    """
    Mettre à jour une suggestion (statut, priorité, réponse admin)
    """
    suggestion = Suggestion.query.get_or_404(suggestion_id)

    old_status = suggestion.status
    suggestion.status = request.form.get('status', suggestion.status)
    suggestion.priority = request.form.get('priority', suggestion.priority)
    suggestion.admin_response = request.form.get('admin_response', suggestion.admin_response)

    db.session.commit()

    # Log l'action
    # log_action('suggestion_updated', user_id=current_user.id,
    #            details=f'Suggestion #{suggestion_id} mise à jour: {old_status} → {suggestion.status}')

    flash('Suggestion mise à jour', 'success')
    return redirect(url_for('admin.manage_suggestions'))
