"""
Routes d'authentification
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import re

from app import db
from app.models import User, Setting
# from app.utils.audit_logger import log_action

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Page de connexion

    GET: Affiche le formulaire de connexion
    POST: Traite la soumission du formulaire
    """
    # En mode standalone, rediriger directement vers home
    if current_app.config.get('STANDALONE_MODE', False):
        return redirect(url_for('procedures.home'))

    # Si déjà connecté, rediriger vers home
    if current_user.is_authenticated:
        return redirect(url_for('procedures.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        # Validation
        if not email or not password:
            flash('Email et mot de passe requis', 'error')
            return render_template('login.html')

        # Rechercher l'utilisateur
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password) and user.is_active:
            # Connexion réussie
            login_user(user, remember=remember)

            # Mettre à jour last_login
            user.last_login = datetime.utcnow()
            db.session.commit()

            # Redirection vers la page demandée ou home
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('procedures.home')

            return redirect(next_page)
        else:
            flash('Email ou mot de passe incorrect', 'error')

    # Vérifier si l'auto-inscription est autorisée
    allow_registration = Setting.get('allow_self_registration', 'true') == 'true'

    return render_template('login.html', allow_registration=allow_registration)


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Déconnexion
    """
    logout_user()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Page d'inscription pour nouveaux utilisateurs

    GET: Affiche le formulaire d'inscription
    POST: Traite la soumission du formulaire
    """
    # Vérifier si l'auto-inscription est autorisée
    allow_registration = Setting.get('allow_self_registration', 'true') == 'true'
    if not allow_registration:
        flash('L\'inscription n\'est pas autorisée. Contactez un administrateur.', 'error')
        return redirect(url_for('auth.login'))

    # Si déjà connecté, rediriger vers home
    if current_user.is_authenticated:
        return redirect(url_for('procedures.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        full_name = request.form.get('full_name', '').strip()

        # Validation de base
        if not email or not password or not full_name:
            flash('Tous les champs sont requis', 'error')
            return render_template('register.html')

        # Validation du format email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            flash('Format d\'email invalide', 'error')
            return render_template('register.html')

        # Vérifier que les mots de passe correspondent
        if password != password_confirm:
            flash('Les mots de passe ne correspondent pas', 'error')
            return render_template('register.html')

        # Vérifier la longueur du mot de passe
        if len(password) < 8:
            flash('Le mot de passe doit contenir au moins 8 caractères', 'error')
            return render_template('register.html')

        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Un compte existe déjà avec cet email', 'error')
            return render_template('register.html')

        # Vérifier le domaine email autorisé
        allowed_domains = get_allowed_email_domains()
        if allowed_domains:
            email_domain = email.split('@')[1] if '@' in email else ''
            if email_domain not in allowed_domains:
                flash(f'Seules les adresses email des domaines autorisés peuvent s\'inscrire: {", ".join(allowed_domains)}', 'error')
                return render_template('register.html')

        # Créer le nouvel utilisateur avec le rôle "viewer" par défaut
        try:
            new_user = User(
                email=email,
                full_name=full_name,
                role='viewer',
                is_active=True
            )
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            # Log l'action
            # log_action('user_registered', user_id=new_user.id, details=f'Nouvel utilisateur inscrit: {email}')

            flash('Votre compte a été créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Erreur lors de l\'inscription: {str(e)}')
            flash('Une erreur est survenue lors de la création du compte', 'error')
            return render_template('register.html')

    return render_template('register.html')


def get_allowed_email_domains():
    """
    Récupère la liste des domaines email autorisés depuis les paramètres

    Returns:
        list: Liste des domaines autorisés (ex: ['basedoc.fr', 'gagneraud.fr'])
              ou liste vide si aucune restriction
    """
    try:
        setting = Setting.query.filter_by(key='allowed_email_domains').first()
        if setting and setting.value:
            # La valeur est stockée comme chaîne séparée par des virgules
            domains = [d.strip() for d in setting.value.split(',') if d.strip()]
            return domains
        return []
    except Exception:
        # Si la table n'existe pas encore, retourner une liste vide (pas de restriction)
        return []
