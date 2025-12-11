"""
Routes pour la recherche
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from sqlalchemy import or_

from app.models import Procedure, Tag

search_bp = Blueprint('search', __name__)


@search_bp.route('/search')
@login_required
def search():
    """
    Page de recherche principale
    """
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20

    if not query or len(query) < 3:
        return render_template('search.html', procedures=None, query=query, error='Requête trop courte (min 3 caractères)')

    # Recherche simple (texte)
    search_pattern = f'%{query}%'

    procedures = Procedure.query.filter(
        Procedure.is_archived == False,
        or_(
            Procedure.title.ilike(search_pattern),
            Procedure.content.ilike(search_pattern),
            Procedure.description.ilike(search_pattern)
        )
    ).order_by(Procedure.updated_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return render_template('search.html', procedures=procedures, query=query)


@search_bp.route('/api/search/suggestions')
@login_required
def search_suggestions():
    """
    API pour l'auto-complétion de recherche

    Query params:
        q: Requête de recherche (min 3 caractères)

    Returns:
        JSON: Liste de suggestions
    """
    query = request.args.get('q', '').strip()

    if not query or len(query) < 3:
        return jsonify([])

    search_pattern = f'%{query}%'

    # Rechercher dans les titres uniquement pour suggestions rapides
    procedures = Procedure.query.filter(
        Procedure.is_archived == False,
        Procedure.title.ilike(search_pattern)
    ).order_by(Procedure.updated_at.desc()).limit(10).all()

    suggestions = [
        {
            'id': p.id,
            'title': p.title,
            'category': p.category.name,
            'url': f'/procedures/{p.id}'
        }
        for p in procedures
    ]

    return jsonify(suggestions)


@search_bp.route('/api/search/tags')
@login_required
def search_tags():
    """
    API pour rechercher des tags

    Query params:
        q: Requête de recherche

    Returns:
        JSON: Liste de tags
    """
    query = request.args.get('q', '').strip()

    if not query:
        # Retourner les tags les plus utilisés
        tags = Tag.query.order_by(Tag.usage_count.desc()).limit(20).all()
    else:
        search_pattern = f'%{query}%'
        tags = Tag.query.filter(Tag.name.ilike(search_pattern))\
            .order_by(Tag.usage_count.desc())\
            .limit(10)\
            .all()

    return jsonify([
        {
            'name': tag.name,
            'usage_count': tag.usage_count
        }
        for tag in tags
    ])
