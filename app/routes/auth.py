"""
Routes d'authentification
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Page de connexion

    GET: Affiche le formulaire de connexion
    POST: Traite la soumission du formulaire
    """
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

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Déconnexion
    """
    logout_user()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('auth.login'))
