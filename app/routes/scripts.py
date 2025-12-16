"""
Routes pour les scripts collaboratifs
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user

from app import db
from app.models import Script
from app.services.ai_service import AIService

scripts_bp = Blueprint('scripts', __name__)


@scripts_bp.route('/scripts')
@login_required
def list_scripts():
    """
    Liste des scripts avec pagination et filtres
    """
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Filtres
    language = request.args.get('language')
    status_filter = request.args.get('status', 'published')

    # Query de base
    query = Script.query

    # Appliquer les filtres
    if language:
        query = query.filter_by(language=language)

    if status_filter:
        query = query.filter_by(status=status_filter)

    # Pagination
    scripts = query.order_by(Script.updated_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # Récupérer les langages disponibles
    languages = db.session.query(Script.language).distinct().order_by(Script.language).all()
    languages = [lang[0] for lang in languages]

    return render_template(
        'scripts/list.html',
        scripts=scripts,
        languages=languages,
        current_language=language,
        current_status=status_filter
    )


@scripts_bp.route('/scripts/<int:script_id>')
@login_required
def view_script(script_id):
    """
    Vue détaillée d'un script
    """
    script = Script.query.get_or_404(script_id)

    return render_template(
        'scripts/detail.html',
        script=script
    )


@scripts_bp.route('/scripts/new', methods=['GET', 'POST'])
@login_required
def new_script():
    """
    Créer un nouveau script
    """
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        content = request.form.get('content', '').strip()
        language = request.form.get('language', '').strip()
        status = request.form.get('status', 'draft')

        # Validation
        if not title:
            flash('Le titre est requis', 'error')
            return redirect(url_for('scripts.new_script'))

        if not content:
            flash('Le code est requis', 'error')
            return redirect(url_for('scripts.new_script'))

        if not language:
            flash('Le langage est requis', 'error')
            return redirect(url_for('scripts.new_script'))

        # Créer le script
        script = Script(
            title=title,
            description=description,
            content=content,
            language=language,
            author_id=current_user.id,
            status=status
        )

        db.session.add(script)
        db.session.commit()

        flash('Script créé avec succès', 'success')
        return redirect(url_for('scripts.view_script', script_id=script.id))

    # GET: Afficher le formulaire
    return render_template('scripts/edit.html', script=None)


@scripts_bp.route('/scripts/<int:script_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_script(script_id):
    """
    Modifier un script existant
    """
    script = Script.query.get_or_404(script_id)

    # Vérifier que l'utilisateur est l'auteur ou admin
    if script.author_id != current_user.id and not current_user.is_admin:
        flash('Vous n\'avez pas la permission de modifier ce script', 'error')
        return redirect(url_for('scripts.view_script', script_id=script_id))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        content = request.form.get('content', '').strip()
        language = request.form.get('language', '').strip()
        status = request.form.get('status', 'draft')

        # Validation
        if not title or not content or not language:
            flash('Titre, code et langage sont requis', 'error')
            return redirect(url_for('scripts.edit_script', script_id=script_id))

        # Mettre à jour le script
        script.title = title
        script.description = description
        script.content = content
        script.language = language
        script.status = status

        db.session.commit()

        flash('Script mis à jour avec succès', 'success')
        return redirect(url_for('scripts.view_script', script_id=script.id))

    # GET: Afficher le formulaire
    return render_template('scripts/edit.html', script=script)


@scripts_bp.route('/scripts/<int:script_id>/delete', methods=['POST'])
@login_required
def delete_script(script_id):
    """
    Supprimer un script
    """
    script = Script.query.get_or_404(script_id)

    # Vérifier que l'utilisateur est l'auteur ou admin
    if script.author_id != current_user.id and not current_user.is_admin:
        abort(403)

    db.session.delete(script)
    db.session.commit()

    flash('Script supprimé', 'success')
    return redirect(url_for('scripts.list_scripts'))


@scripts_bp.route('/scripts/<int:script_id>/review', methods=['POST'])
@login_required
def review_script(script_id):
    """
    Demander une révision du code par l'IA
    """
    script = Script.query.get_or_404(script_id)

    try:
        ai_service = AIService()
        suggestions = ai_service.review_code(
            code=script.content,
            language=script.language,
            title=script.title
        )

        # Stocker les suggestions
        import json
        script.ai_suggestions = json.dumps(suggestions, ensure_ascii=False)
        db.session.commit()

        return jsonify({
            'success': True,
            'suggestions': suggestions
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@scripts_bp.route('/scripts/<int:script_id>/verify', methods=['POST'])
@login_required
def verify_script(script_id):
    """
    Marquer un script comme vérifié (admin uniquement)
    """
    if not current_user.is_admin:
        abort(403)

    script = Script.query.get_or_404(script_id)
    verification_notes = request.form.get('notes', '').strip()

    script.is_verified = True
    script.verification_notes = verification_notes

    db.session.commit()

    flash('Script vérifié', 'success')
    return redirect(url_for('scripts.view_script', script_id=script_id))
