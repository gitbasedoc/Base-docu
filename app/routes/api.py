"""
Routes API pour récupérer les données des différentes sections
"""

from flask import Blueprint, jsonify
from app.models import Procedure, Script, FAQ, Software

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/procedures')
def get_procedures():
    """Récupère la liste des procédures pour la homepage"""
    procedures = Procedure.query.filter_by(is_archived=False).order_by(Procedure.updated_at.desc()).limit(50).all()

    items = []
    for proc in procedures:
        items.append({
            'id': proc.id,
            'title': proc.title,
            'description': proc.description,
            'category': proc.category.name if proc.category else 'Sans catégorie',
            'author': proc.creator.full_name if proc.creator else 'Inconnu',
            'updated_at': proc.updated_at.strftime('%d/%m/%Y')
        })

    return jsonify({'items': items})


@api_bp.route('/scripts')
def get_scripts():
    """Récupère la liste des scripts pour la homepage"""
    scripts = Script.query.filter_by(status='published').order_by(Script.created_at.desc()).limit(50).all()

    items = []
    for script in scripts:
        items.append({
            'id': script.id,
            'title': script.title,
            'description': script.description,
            'language': script.language,
            'author': script.author.full_name if script.author else 'Inconnu',
            'created_at': script.created_at.strftime('%d/%m/%Y')
        })

    return jsonify({'items': items})


@api_bp.route('/faq')
def get_faqs():
    """Récupère la liste des FAQs pour la homepage"""
    faqs = FAQ.query.filter_by(is_published=True).order_by(FAQ.updated_at.desc()).limit(50).all()

    items = []
    for faq in faqs:
        items.append({
            'id': faq.id,
            'question': faq.question,
            'category': faq.category.name if faq.category else 'Sans catégorie',
            'view_count': faq.view_count,
            'helpful_count': faq.helpful_count
        })

    return jsonify({'items': items})


@api_bp.route('/software')
def get_software():
    """Récupère la liste des logiciels pour la homepage"""
    software_list = Software.query.order_by(Software.useful_count.desc(), Software.created_at.desc()).limit(50).all()

    items = []
    for soft in software_list:
        items.append({
            'id': soft.id,
            'name': soft.name,
            'description': soft.description,
            'category': soft.category.name if soft.category else 'Sans catégorie',
            'platform': soft.platform,
            'is_free': soft.is_free,
            'useful_count': soft.useful_count
        })

    return jsonify({'items': items})
