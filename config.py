"""
Configuration pour KB Support Basedoc
"""

import os
from datetime import timedelta


class Config:
    """Configuration de base"""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY doit être définie dans les variables d'environnement")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL doit être définie dans les variables d'environnement")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'connect_args': {
            'options': '-c timezone=utc'
        }
    }

    # Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/var/www/kb_basedoc/storage')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS = {
        'ps1', 'sh', 'bat', 'py',
        'pdf', 'doc', 'docx', 'odt', 'rtf',
        'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'svg',
        'mp4', 'avi', 'mov', 'mkv', 'wmv', 'webm',
        'ini', 'conf', 'xml', 'json', 'yaml', 'yml',
        'txt', 'log', 'md',
        'zip', 'rar', '7z'
    }

    # Session
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_NAME = 'kb_session'

    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    WTF_CSRF_SSL_STRICT = os.environ.get('FLASK_ENV') == 'production'

    # JSON
    JSON_AS_ASCII = False  # Support UTF-8
    JSON_SORT_KEYS = False

    # Claude API
    CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')
    CLAUDE_MODEL = os.environ.get('CLAUDE_MODEL', 'claude-sonnet-4-5-20250929')
    CLAUDE_MAX_TOKENS = int(os.environ.get('CLAUDE_MAX_TOKENS', 4096))
    CLAUDE_TIMEOUT = int(os.environ.get('CLAUDE_TIMEOUT', 60))

    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_STRATEGY = 'fixed-window'
    RATELIMIT_HEADERS_ENABLED = True

    # Caching
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = 'kb_'

    # Application
    APP_NAME = os.environ.get('APP_NAME', 'KB Support Basedoc')
    COMPANY_NAME = os.environ.get('COMPANY_NAME', 'Support IT - Gagneraud')
    VERSION = '1.0.0'

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', '/var/log/kb_basedoc/app.log')
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT = 10

    # Pagination
    ITEMS_PER_PAGE = 20

    # Search
    SEARCH_MIN_LENGTH = 3
    SEARCH_SUGGESTIONS_LIMIT = 10


class DevelopmentConfig(Config):
    """Configuration pour développement"""

    DEBUG = True
    TESTING = False

    # Moins strict en dev
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_SSL_STRICT = False

    # Database locale
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://kb_user:kb_password@localhost/kb_basedoc_dev'
    )

    # Logs plus verbeux
    LOG_LEVEL = 'DEBUG'
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Configuration pour production"""

    DEBUG = False
    TESTING = False

    # Sécurité stricte
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_SSL_STRICT = True


class TestingConfig(Config):
    """Configuration pour tests"""

    DEBUG = False
    TESTING = True

    # Database de test
    SQLALCHEMY_DATABASE_URI = 'postgresql://kb_user:kb_password@localhost/kb_basedoc_test'

    # Désactiver CSRF pour les tests
    WTF_CSRF_ENABLED = False


class StandaloneConfig(Config):
    """Configuration pour version standalone (utilisateur unique)"""

    DEBUG = False
    TESTING = False

    # Database SQLite locale
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(DATA_DIR, "kb_basedoc.db")}'

    # Pas de pool pour SQLite
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
    }

    # Upload dans le dossier data
    UPLOAD_FOLDER = os.path.join(DATA_DIR, 'uploads')

    # Logs dans le dossier data
    LOG_FILE = os.path.join(DATA_DIR, 'logs', 'app.log')

    # Session moins stricte (application locale)
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_SSL_STRICT = False

    # Secret key par défaut (peut être overridée par .env)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me-in-production')

    # API Claude (optionnelle)
    CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', None)

    # Pas de rate limiting en standalone
    RATELIMIT_ENABLED = False

    # Pas d'authentification requise
    STANDALONE_MODE = True


# Map des configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'standalone': StandaloneConfig,
    'default': ProductionConfig
}
