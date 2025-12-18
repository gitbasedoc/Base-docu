"""
Routes pour les suggestions d'amélioration
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app import db
from app.models import Suggestion
from app.utils.audit_logger import log_action

suggestions_bp = Blueprint('suggestions', __name__, url_prefix='/suggestions')


@suggestions_bp.route('/')
@login_required
def list_suggestions():
    """
    Lister les suggestions de l'utilisateur courant
    """
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Les utilisateurs normaux ne voient que leurs propres suggestions
    # Les admins voient toutes les suggestions
    if current_user.has_permission('admin'):
        suggestions_query = Suggestion.query
    else:
        suggestions_query = Suggestion.query.filter_by(user_id=current_user.id)

    suggestions = suggestions_query.order_by(Suggestion.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return render_template('suggestions/list.html', suggestions=suggestions)


@suggestions_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_suggestion():
    """
    Créer une nouvelle suggestion
    """
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'other')

        # Validation
        if not title or not description:
            flash('Titre et description sont requis', 'error')
            return render_template('suggestions/new.html')

        if len(title) < 10:
            flash('Le titre doit contenir au moins 10 caractères', 'error')
            return render_template('suggestions/new.html')

        if len(description) < 20:
            flash('La description doit contenir au moins 20 caractères', 'error')
            return render_template('suggestions/new.html')

        if category not in ['feature', 'bug', 'improvement', 'other']:
            category = 'other'

        # Créer la suggestion
        suggestion = Suggestion(
            user_id=current_user.id,
            title=title,
            description=description,
            category=category,
            status='pending'
        )

        db.session.add(suggestion)
        db.session.commit()

        # Log l'action
        log_action('suggestion_created', user_id=current_user.id, details=f'Suggestion créée: {title}')

        flash('Votre suggestion a été envoyée avec succès! Merci pour votre contribution.', 'success')
        return redirect(url_for('suggestions.list_suggestions'))

    return render_template('suggestions/new.html')


@suggestions_bp.route('/<int:suggestion_id>')
@login_required
def view_suggestion(suggestion_id):
    """
    Voir les détails d'une suggestion
    """
    suggestion = Suggestion.query.get_or_404(suggestion_id)

    # Vérifier les permissions
    if not current_user.has_permission('admin') and suggestion.user_id != current_user.id:
        flash('Vous n\'avez pas accès à cette suggestion', 'error')
        return redirect(url_for('suggestions.list_suggestions'))

    return render_template('suggestions/view.html', suggestion=suggestion)


@suggestions_bp.route('/<int:suggestion_id>/delete', methods=['POST'])
@login_required
def delete_suggestion(suggestion_id):
    """
    Supprimer une suggestion (seulement son propre ou admin)
    """
    suggestion = Suggestion.query.get_or_404(suggestion_id)

    # Vérifier les permissions
    if not current_user.has_permission('admin') and suggestion.user_id != current_user.id:
        flash('Vous n\'avez pas la permission de supprimer cette suggestion', 'error')
        return redirect(url_for('suggestions.list_suggestions'))

    # Supprimer la suggestion
    title = suggestion.title
    db.session.delete(suggestion)
    db.session.commit()

    # Log l'action
    log_action('suggestion_deleted', user_id=current_user.id, details=f'Suggestion supprimée: {title}')

    flash('Suggestion supprimée', 'success')
    return redirect(url_for('suggestions.list_suggestions'))
