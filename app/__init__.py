"""
Application Factory pour KB Support Basedoc
"""

import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


def create_app(config_name=None):
    """
    Factory pour créer l'application Flask

    Args:
        config_name: Nom de la configuration ('development', 'production', 'testing')

    Returns:
        Instance Flask configurée
    """
    app = Flask(__name__)

    # Configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')

    app.config.from_object('config.Config')

    # Initialiser les extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    # Configuration Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'

    # En mode standalone, créer un request_loader pour auto-authentifier
    if app.config.get('STANDALONE_MODE', False):
        @login_manager.request_loader
        def load_user_from_request(request):
            from app.models import User
            # Retourner toujours l'utilisateur standalone
            user = User.query.filter_by(email='standalone@local').first()
            if not user:
                # Créer l'utilisateur standalone s'il n'existe pas
                user = User(
                    email='standalone@local',
                    full_name='Utilisateur',
                    is_admin=True,
                    is_active=True
                )
                user.set_password('standalone')  # Mot de passe non utilisé
                db.session.add(user)
                try:
                    db.session.commit()
                except:
                    db.session.rollback()
            return user

    # Configuration logging
    configure_logging(app)

    # Importer et enregistrer les blueprints
    with app.app_context():
        from app.routes.auth import auth_bp
        from app.routes.procedures import procedures_bp
        from app.routes.search import search_bp
        from app.routes.api_ai import api_ai_bp
        from app.routes.api import api_bp
        from app.routes.admin import admin_bp
        from app.routes.files import files_bp
        from app.routes.scripts import scripts_bp
        from app.routes.faq import faq_bp
        from app.routes.software import software_bp
        from app.routes.suggestions import suggestions_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(procedures_bp)
        app.register_blueprint(search_bp)
        app.register_blueprint(api_ai_bp)
        app.register_blueprint(api_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(files_bp)
        app.register_blueprint(scripts_bp)
        app.register_blueprint(faq_bp)
        app.register_blueprint(software_bp)
        app.register_blueprint(suggestions_bp)

        # Route pour servir les fichiers uploadés
        from flask import send_from_directory

        @app.route('/uploads/<path:filename>')
        def uploaded_file(filename):
            """Servir les fichiers uploadés"""
            upload_folder = app.config.get('UPLOAD_FOLDER', 'storage')
            return send_from_directory(upload_folder, filename)

        # Context processors
        @app.context_processor
        def inject_app_info():
            from app.models import Setting

            # Récupérer les paramètres depuis la base de données avec fallback sur config
            app_name = Setting.get('app_name', app.config.get('APP_NAME', 'KB Support Basedoc'))
            company_name = Setting.get('company_name', app.config.get('COMPANY_NAME', 'Support IT'))
            version = Setting.get('version', app.config.get('VERSION', '1.0.0'))

            return {
                'app_name': app_name,
                'company_name': company_name,
                'version': version
            }

        # Error handlers
        register_error_handlers(app)

    return app


def configure_logging(app):
    """
    Configure le système de logging

    Args:
        app: Instance Flask
    """
    if not app.debug and not app.testing:
        # Créer le répertoire des logs si nécessaire
        log_dir = os.path.dirname(app.config.get('LOG_FILE', '/var/log/kb_basedoc/app.log'))
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Handler fichier avec rotation
        file_handler = RotatingFileHandler(
            app.config.get('LOG_FILE', '/var/log/kb_basedoc/app.log'),
            maxBytes=app.config.get('LOG_MAX_BYTES', 10 * 1024 * 1024),
            backupCount=app.config.get('LOG_BACKUP_COUNT', 10)
        )

        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        ))

        file_handler.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))

        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))

        app.logger.info('KB Support Basedoc startup')


def register_error_handlers(app):
    """
    Enregistre les gestionnaires d'erreurs

    Args:
        app: Instance Flask
    """
    from flask import render_template

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(429)
    def ratelimit_error(error):
        return render_template('errors/429.html'), 429
