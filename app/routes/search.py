"""
Routes pour la recherche
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
from sqlalchemy import or_, func, text

from app import db

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

    # PostgreSQL Full-Text Search avec ranking
    try:
        # Convertir la query en tsquery (français)
        search_query = ' & '.join([word for word in query.split() if len(word) >= 2])

        # Requête avec ts_rank pour le scoring
        procedures = db.session.query(
            Procedure,
            func.ts_rank(
                Procedure.search_vector,
                func.to_tsquery('french', search_query)
            ).label('rank')
        ).filter(
            Procedure.is_archived == False,
            Procedure.search_vector.op('@@')(func.to_tsquery('french', search_query))
        ).order_by(
            text('rank DESC'),
            Procedure.updated_at.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        # Extraire les procédures du résultat (tuple avec rank)
        procedures.items = [item[0] for item in procedures.items]

    except Exception as e:
        # Fallback sur recherche ILIKE si erreur (ex: search_vector pas encore créé)
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
        q: Requête de recherche (min 2 caractères)

    Returns:
        JSON: Liste de suggestions depuis Procedures, Scripts, FAQ, Software
    """
    query = request.args.get('q', '').strip()

    if not query or len(query) < 2:
        return jsonify([])

    # Charger les modèles appropriés selon le mode
    if current_app.config.get('STANDALONE_MODE', False):
        from app.models_standalone import Procedure, Script, FAQ, Software
    else:
        from app.models import Procedure, Script, FAQ, Software

    search_pattern = f'%{query}%'
    suggestions = []

    # Recherche dans les Procédures
    try:
        procedures = Procedure.query.filter(
            Procedure.is_published == True,
            or_(
                Procedure.title.ilike(search_pattern),
                Procedure.description.ilike(search_pattern)
            )
        ).order_by(Procedure.updated_at.desc()).limit(5).all()

        for p in procedures:
            suggestions.append({
                'id': p.id,
                'title': p.title,
                'type': 'Procédure',
                'icon': '📄',
                'url': f'/procedures/{p.id}'
            })
    except:
        pass

    # Recherche dans les Scripts
    try:
        scripts = Script.query.filter(
            Script.status == 'published',
            or_(
                Script.title.ilike(search_pattern),
                Script.description.ilike(search_pattern)
            )
        ).order_by(Script.updated_at.desc()).limit(5).all()

        for s in scripts:
            suggestions.append({
                'id': s.id,
                'title': s.title,
                'type': f'Script {s.language.upper()}',
                'icon': '💻',
                'url': f'/scripts/{s.id}'
            })
    except:
        pass

    # Recherche dans les FAQ
    try:
        faqs = FAQ.query.filter(
            FAQ.is_published == True,
            or_(
                FAQ.question.ilike(search_pattern),
                FAQ.answer.ilike(search_pattern)
            )
        ).order_by(FAQ.updated_at.desc()).limit(5).all()

        for f in faqs:
            suggestions.append({
                'id': f.id,
                'title': f.question,
                'type': 'FAQ',
                'icon': '❓',
                'url': f'/faq/{f.id}'
            })
    except:
        pass

    # Recherche dans les Logiciels
    try:
        software = Software.query.filter(
            Software.is_active == True,
            or_(
                Software.name.ilike(search_pattern),
                Software.description.ilike(search_pattern)
            )
        ).order_by(Software.updated_at.desc()).limit(5).all()

        for sw in software:
            suggestions.append({
                'id': sw.id,
                'title': sw.name,
                'type': 'Logiciel',
                'icon': '⚙️',
                'url': f'/software/{sw.id}'
            })
    except:
        pass

    # Limiter à 10 résultats maximum
    return jsonify(suggestions[:10])


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
