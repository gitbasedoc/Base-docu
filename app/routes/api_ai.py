"""
Routes API pour les fonctionnalités IA
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
import logging

from app.services.ai_service import (
    get_ai_service,
    AIServiceError,
    AIServiceConnectionError,
    AIServiceRateLimitError
)

# Configuration logging
logger = logging.getLogger(__name__)

# Blueprint
api_ai_bp = Blueprint('api_ai', __name__, url_prefix='/api/ai')


@api_ai_bp.route('/generate-tags', methods=['POST'])
@login_required
def generate_tags():
    """
    Génère des tags automatiquement pour une procédure

    Request JSON:
        {
            "title": "Titre de la procédure",
            "content": "Contenu de la procédure",
            "min_tags": 4,  # optionnel
            "max_tags": 8   # optionnel
        }

    Response JSON:
        {
            "success": true,
            "tags": ["tag1", "tag2", ...],
            "count": 5
        }

    Errors:
        400: Données invalides
        429: Rate limit dépassé
        500: Erreur serveur
    """
    try:
        data = request.get_json()

        # Validation
        if not data:
            return jsonify({
                'success': False,
                'error': 'Aucune donnée fournie'
            }), 400

        title = data.get('title', '').strip()
        content = data.get('content', '').strip()

        if not title:
            return jsonify({
                'success': False,
                'error': 'Le titre est requis'
            }), 400

        if not content:
            return jsonify({
                'success': False,
                'error': 'Le contenu est requis'
            }), 400

        if len(content) < 50:
            return jsonify({
                'success': False,
                'error': 'Le contenu doit contenir au moins 50 caractères'
            }), 400

        min_tags = data.get('min_tags', 4)
        max_tags = data.get('max_tags', 8)

        # Appeler le service IA
        ai_service = get_ai_service()
        tags = ai_service.generate_tags(title, content, min_tags, max_tags)

        logger.info(
            f"Tags générés pour '{title[:30]}...' par {current_user.email}: "
            f"{len(tags)} tags"
        )

        return jsonify({
            'success': True,
            'tags': tags,
            'count': len(tags)
        })

    except AIServiceRateLimitError as e:
        logger.warning(f"Rate limit atteint: {e}")
        return jsonify({
            'success': False,
            'error': 'Trop de requêtes. Veuillez réessayer dans quelques instants.',
            'error_type': 'rate_limit'
        }), 429

    except AIServiceConnectionError as e:
        logger.error(f"Erreur connexion API: {e}")
        return jsonify({
            'success': False,
            'error': 'Impossible de se connecter au service IA. Veuillez réessayer.',
            'error_type': 'connection'
        }), 503

    except AIServiceError as e:
        logger.error(f"Erreur service IA: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'ai_service'
        }), 500

    except Exception as e:
        logger.exception(f"Erreur inattendue génération tags: {e}")
        return jsonify({
            'success': False,
            'error': 'Une erreur inattendue est survenue',
            'error_type': 'server'
        }), 500


@api_ai_bp.route('/reformulate', methods=['POST'])
@login_required
def reformulate():
    """
    Reformule le contenu d'une procédure

    Request JSON:
        {
            "title": "Titre de la procédure",
            "content": "Contenu original"
        }

    Response JSON:
        {
            "success": true,
            "reformulated_content": "Contenu reformulé",
            "original_length": 1234,
            "reformulated_length": 1456
        }

    Errors:
        400: Données invalides
        429: Rate limit dépassé
        500: Erreur serveur
    """
    try:
        data = request.get_json()

        # Validation
        if not data:
            return jsonify({
                'success': False,
                'error': 'Aucune donnée fournie'
            }), 400

        title = data.get('title', '').strip()
        content = data.get('content', '').strip()

        if not title:
            return jsonify({
                'success': False,
                'error': 'Le titre est requis'
            }), 400

        if not content:
            return jsonify({
                'success': False,
                'error': 'Le contenu est requis'
            }), 400

        if len(content) < 50:
            return jsonify({
                'success': False,
                'error': 'Le contenu doit contenir au moins 50 caractères'
            }), 400

        # Appeler le service IA
        ai_service = get_ai_service()
        reformulated = ai_service.reformulate_content(title, content)

        logger.info(
            f"Contenu reformulé pour '{title[:30]}...' par {current_user.email}: "
            f"{len(content)} → {len(reformulated)} chars"
        )

        return jsonify({
            'success': True,
            'reformulated_content': reformulated,
            'original_length': len(content),
            'reformulated_length': len(reformulated)
        })

    except AIServiceRateLimitError as e:
        logger.warning(f"Rate limit atteint: {e}")
        return jsonify({
            'success': False,
            'error': 'Trop de requêtes. Veuillez réessayer dans quelques instants.',
            'error_type': 'rate_limit'
        }), 429

    except AIServiceConnectionError as e:
        logger.error(f"Erreur connexion API: {e}")
        return jsonify({
            'success': False,
            'error': 'Impossible de se connecter au service IA. Veuillez réessayer.',
            'error_type': 'connection'
        }), 503

    except AIServiceError as e:
        logger.error(f"Erreur service IA: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'ai_service'
        }), 500

    except Exception as e:
        logger.exception(f"Erreur inattendue reformulation: {e}")
        return jsonify({
            'success': False,
            'error': 'Une erreur inattendue est survenue',
            'error_type': 'server'
        }), 500


@api_ai_bp.route('/layout', methods=['POST'])
@login_required
def layout():
    """
    Réorganise la mise en page d'une procédure

    Request JSON:
        {
            "title": "Titre de la procédure",
            "content": "Contenu original",
            "options": {
                "use_emojis": true,
                "structure_sections": true,
                "number_steps": true,
                "add_troubleshooting": true
            }
        }

    Response JSON:
        {
            "success": true,
            "layout_content": "Contenu réorganisé",
            "original_length": 1234,
            "layout_length": 1567
        }

    Errors:
        400: Données invalides
        429: Rate limit dépassé
        500: Erreur serveur
    """
    try:
        data = request.get_json()

        # Validation
        if not data:
            return jsonify({
                'success': False,
                'error': 'Aucune donnée fournie'
            }), 400

        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        options = data.get('options', {})

        if not title:
            return jsonify({
                'success': False,
                'error': 'Le titre est requis'
            }), 400

        if not content:
            return jsonify({
                'success': False,
                'error': 'Le contenu est requis'
            }), 400

        if len(content) < 50:
            return jsonify({
                'success': False,
                'error': 'Le contenu doit contenir au moins 50 caractères'
            }), 400

        # Appeler le service IA
        ai_service = get_ai_service()
        layout_content = ai_service.layout_content(title, content, options)

        logger.info(
            f"Mise en page pour '{title[:30]}...' par {current_user.email}: "
            f"{len(content)} → {len(layout_content)} chars"
        )

        return jsonify({
            'success': True,
            'layout_content': layout_content,
            'original_length': len(content),
            'layout_length': len(layout_content)
        })

    except AIServiceRateLimitError as e:
        logger.warning(f"Rate limit atteint: {e}")
        return jsonify({
            'success': False,
            'error': 'Trop de requêtes. Veuillez réessayer dans quelques instants.',
            'error_type': 'rate_limit'
        }), 429

    except AIServiceConnectionError as e:
        logger.error(f"Erreur connexion API: {e}")
        return jsonify({
            'success': False,
            'error': 'Impossible de se connecter au service IA. Veuillez réessayer.',
            'error_type': 'connection'
        }), 503

    except AIServiceError as e:
        logger.error(f"Erreur service IA: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'ai_service'
        }), 500

    except Exception as e:
        logger.exception(f"Erreur inattendue mise en page: {e}")
        return jsonify({
            'success': False,
            'error': 'Une erreur inattendue est survenue',
            'error_type': 'server'
        }), 500


@api_ai_bp.route('/semantic-search', methods=['POST'])
@login_required
def semantic_search():
    """
    Recherche sémantique dans les procédures

    Request JSON:
        {
            "query": "Comment configurer le VPN?",
            "procedures": [
                {"id": 1, "title": "...", "content": "..."},
                ...
            ],
            "top_k": 10  # optionnel
        }

    Response JSON:
        {
            "success": true,
            "results": [
                {
                    "procedure_id": 1,
                    "title": "Configuration VPN",
                    "relevance_score": 95
                },
                ...
            ],
            "count": 5
        }

    Errors:
        400: Données invalides
        429: Rate limit dépassé
        500: Erreur serveur
    """
    try:
        data = request.get_json()

        # Validation
        if not data:
            return jsonify({
                'success': False,
                'error': 'Aucune donnée fournie'
            }), 400

        query = data.get('query', '').strip()
        procedures = data.get('procedures', [])
        top_k = data.get('top_k', 10)

        if not query:
            return jsonify({
                'success': False,
                'error': 'La requête de recherche est requise'
            }), 400

        if not procedures:
            return jsonify({
                'success': False,
                'error': 'Aucune procédure à rechercher'
            }), 400

        # Appeler le service IA
        ai_service = get_ai_service()
        results = ai_service.semantic_search(query, procedures, top_k)

        # Formater les résultats
        formatted_results = [
            {
                'procedure_id': proc['id'],
                'title': proc['title'],
                'relevance_score': score
            }
            for proc, score in results
        ]

        logger.info(
            f"Recherche sémantique '{query[:30]}...' par {current_user.email}: "
            f"{len(formatted_results)} résultats"
        )

        return jsonify({
            'success': True,
            'results': formatted_results,
            'count': len(formatted_results)
        })

    except AIServiceRateLimitError as e:
        logger.warning(f"Rate limit atteint: {e}")
        return jsonify({
            'success': False,
            'error': 'Trop de requêtes. Veuillez réessayer dans quelques instants.',
            'error_type': 'rate_limit'
        }), 429

    except AIServiceConnectionError as e:
        logger.error(f"Erreur connexion API: {e}")
        return jsonify({
            'success': False,
            'error': 'Impossible de se connecter au service IA. Veuillez réessayer.',
            'error_type': 'connection'
        }), 503

    except AIServiceError as e:
        logger.error(f"Erreur service IA: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'ai_service'
        }), 500

    except Exception as e:
        logger.exception(f"Erreur inattendue recherche sémantique: {e}")
        return jsonify({
            'success': False,
            'error': 'Une erreur inattendue est survenue',
            'error_type': 'server'
        }), 500


@api_ai_bp.route('/health', methods=['GET'])
def health():
    """
    Vérifie l'état du service IA

    Response JSON:
        {
            "status": "ok",
            "service": "ai",
            "model": "claude-sonnet-4-5-20250929"
        }
    """
    try:
        ai_service = get_ai_service()

        return jsonify({
            'status': 'ok',
            'service': 'ai',
            'model': ai_service.config.model,
            'max_tokens': ai_service.config.max_tokens
        })

    except Exception as e:
        logger.error(f"Erreur health check IA: {e}")
        return jsonify({
            'status': 'error',
            'service': 'ai',
            'error': str(e)
        }), 500
