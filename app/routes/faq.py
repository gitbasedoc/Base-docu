"""
Routes pour les FAQ (Questions Fréquemment Posées)
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user

from app import db
from app.models import FAQ

faq_bp = Blueprint('faq', __name__)


@faq_bp.route('/faq')
def list_faqs():
    """
    Liste des FAQs avec filtres et pagination
    """
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Filtres
    show_all = request.args.get('show_all', 'false') == 'true'

    # Query de base
    query = FAQ.query

    # Par défaut, afficher seulement les FAQs publiées
    if not show_all or not (current_user.is_authenticated and current_user.is_admin):
        query = query.filter_by(is_published=True)

    # Pagination
    faqs = query.order_by(FAQ.updated_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return render_template(
        'faq/list.html',
        faqs=faqs,
        show_all=show_all
    )


@faq_bp.route('/faq/<int:faq_id>')
def view_faq(faq_id):
    """
    Vue détaillée d'une FAQ
    """
    faq = FAQ.query.get_or_404(faq_id)

    # Vérifier si publiée ou si admin
    if not faq.is_published and not (current_user.is_authenticated and current_user.is_admin):
        abort(404)

    # Incrémenter le compteur de vues
    faq.increment_view()
    db.session.commit()

    return render_template(
        'faq/detail.html',
        faq=faq
    )


@faq_bp.route('/faq/new', methods=['GET', 'POST'])
@login_required
def new_faq():
    """
    Créer une nouvelle FAQ
    """
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        answer = request.form.get('answer', '').strip()
        is_published = request.form.get('is_published') == 'on'

        # Validation
        if not question:
            flash('La question est requise', 'error')
            return redirect(url_for('faq.new_faq'))

        if not answer:
            flash('La réponse est requise', 'error')
            return redirect(url_for('faq.new_faq'))

        # Créer la FAQ
        faq = FAQ(
            question=question,
            answer=answer,
            created_by=current_user.id,
            is_published=is_published
        )

        db.session.add(faq)
        db.session.commit()

        flash('FAQ créée avec succès', 'success')
        return redirect(url_for('faq.view_faq', faq_id=faq.id))

    # GET: Afficher le formulaire
    return render_template('faq/edit.html', faq=None)


@faq_bp.route('/faq/<int:faq_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_faq(faq_id):
    """
    Modifier une FAQ existante
    """
    faq = FAQ.query.get_or_404(faq_id)

    # Vérifier les permissions (auteur ou admin)
    if faq.created_by != current_user.id and not current_user.is_admin:
        flash('Vous n\'avez pas la permission de modifier cette FAQ', 'error')
        return redirect(url_for('faq.view_faq', faq_id=faq_id))

    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        answer = request.form.get('answer', '').strip()
        is_published = request.form.get('is_published') == 'on'

        # Validation
        if not question or not answer:
            flash('Question et réponse sont requis', 'error')
            return redirect(url_for('faq.edit_faq', faq_id=faq_id))

        # Mettre à jour la FAQ
        faq.question = question
        faq.answer = answer
        faq.is_published = is_published

        db.session.commit()

        flash('FAQ mise à jour avec succès', 'success')
        return redirect(url_for('faq.view_faq', faq_id=faq.id))

    # GET: Afficher le formulaire
    return render_template('faq/edit.html', faq=faq)


@faq_bp.route('/faq/<int:faq_id>/delete', methods=['POST'])
@login_required
def delete_faq(faq_id):
    """
    Supprimer une FAQ (auteur ou admin uniquement)
    """
    faq = FAQ.query.get_or_404(faq_id)

    # Vérifier les permissions
    if faq.created_by != current_user.id and not current_user.is_admin:
        abort(403)

    db.session.delete(faq)
    db.session.commit()

    flash('FAQ supprimée', 'success')
    return redirect(url_for('faq.list_faqs'))


@faq_bp.route('/faq/<int:faq_id>/helpful', methods=['POST'])
def mark_helpful(faq_id):
    """
    Marquer une FAQ comme utile
    """
    faq = FAQ.query.get_or_404(faq_id)

    faq.increment_helpful()
    db.session.commit()

    return jsonify({
        'success': True,
        'helpful_count': faq.helpful_count
    })
