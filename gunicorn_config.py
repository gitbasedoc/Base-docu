"""
Configuration Gunicorn pour KB Support Basedoc
"""

import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
worker_connections = 1000
timeout = 60
keepalive = 2

# Restart workers after this many requests (prevent memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "kb_basedoc"

# Server mechanics
daemon = False
pidfile = "/var/run/gunicorn/kb_basedoc.pid"
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (si nécessaire, mais généralement géré par Nginx)
keyfile = None
certfile = None

# Logging
logconfig_dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'generic': {
            'format': '[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'class': 'logging.Formatter'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'generic',
            'stream': 'ext://sys.stdout'
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'generic',
            'filename': '/var/log/gunicorn/error.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 10
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'error_file']
    },
    'loggers': {
        'gunicorn.error': {
            'level': 'INFO',
            'handlers': ['error_file'],
            'propagate': False,
            'qualname': 'gunicorn.error'
        },
        'gunicorn.access': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
            'qualname': 'gunicorn.access'
        }
    }
}

# Hook pour le démarrage
def on_starting(server):
    """
    Appelé au démarrage du serveur
    """
    server.log.info("KB Support Basedoc starting...")


def when_ready(server):
    """
    Appelé quand le serveur est prêt
    """
    server.log.info("KB Support Basedoc ready. PID: %s" % os.getpid())


def on_exit(server):
    """
    Appelé à l'arrêt du serveur
    """
    server.log.info("KB Support Basedoc shutting down...")
