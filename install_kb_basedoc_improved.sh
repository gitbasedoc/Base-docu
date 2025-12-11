#!/bin/bash

################################################################################
# Script d'installation amélioré KB Support Basedoc
# Pour VPS OVH Ubuntu 24.04 LTS
# URL: https://gagneraud.basedoc.fr
# IP: 193.70.41.117
# Version: 2.0
################################################################################

set -euo pipefail  # Exit on error, undefined vars, pipe failures
IFS=$'\n\t'

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables globales
APP_DIR="/var/www/kb_basedoc"
APP_USER="www-data"
DB_NAME="kb_basedoc"
DB_USER="kb_user"
DOMAIN="gagneraud.basedoc.fr"
VENV_PATH="$APP_DIR/venv"
BACKUP_DIR="/var/backups/kb_basedoc"
LOG_FILE="/var/log/kb_basedoc_install.log"

# Fonction de logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    log "SUCCESS: $1"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    log "ERROR: $1"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
    log "INFO: $1"
}

print_step() {
    echo -e "${BLUE}━━━ $1${NC}"
    log "STEP: $1"
}

# Vérification root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Ce script doit être exécuté en tant que root (sudo)"
        exit 1
    fi
}

# Vérification OS
check_os() {
    if [ ! -f /etc/os-release ]; then
        print_error "Impossible de détecter l'OS"
        exit 1
    fi

    . /etc/os-release

    if [ "$ID" != "ubuntu" ]; then
        print_error "Ce script est prévu pour Ubuntu (détecté: $ID)"
        exit 1
    fi

    if [ "${VERSION_ID%%.*}" -lt 22 ]; then
        print_error "Ubuntu 22.04 ou supérieur requis (détecté: $VERSION_ID)"
        exit 1
    fi

    print_success "OS compatible: Ubuntu $VERSION_ID"
}

# Validation email
validate_email() {
    local email=$1
    if [[ ! "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        return 1
    fi
    return 0
}

# Validation mot de passe
validate_password() {
    local password=$1
    if [ ${#password} -lt 8 ]; then
        print_error "Le mot de passe doit contenir au moins 8 caractères"
        return 1
    fi
    return 0
}

# Rollback function
rollback() {
    print_error "Une erreur est survenue. Tentative de rollback..."

    systemctl stop kb_basedoc 2>/dev/null || true
    systemctl disable kb_basedoc 2>/dev/null || true

    if [ -d "$APP_DIR.backup" ]; then
        rm -rf "$APP_DIR"
        mv "$APP_DIR.backup" "$APP_DIR"
        print_info "Application restaurée depuis backup"
    fi

    print_error "Installation échouée. Consultez $LOG_FILE pour plus de détails"
    exit 1
}

trap rollback ERR

# Banner
clear
echo "════════════════════════════════════════════════════════════════"
echo "   📚 Installation KB Support Basedoc v2.0"
echo "   Domaine: $DOMAIN"
echo "   Serveur: VPS OVH Ubuntu 24.04"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Initialiser log
mkdir -p "$(dirname "$LOG_FILE")"
log "=== Début installation KB Support Basedoc ==="

check_root
check_os

# Confirmation
read -p "Continuer l'installation? (o/N): " -r
if [[ ! $REPLY =~ ^[Oo]$ ]]; then
    print_info "Installation annulée"
    exit 0
fi

################################################################################
# COLLECTE DES INFORMATIONS
################################################################################
print_step "Collecte des informations"

# Clé API Claude
while true; do
    read -p "Clé API Claude (sk-ant-...): " CLAUDE_API_KEY
    if [[ "$CLAUDE_API_KEY" =~ ^sk-ant- ]]; then
        break
    else
        print_error "Format de clé invalide. La clé doit commencer par 'sk-ant-'"
    fi
done

# Email admin
while true; do
    read -p "Email admin [dheurtebise@basedoc.fr]: " ADMIN_EMAIL
    ADMIN_EMAIL=${ADMIN_EMAIL:-dheurtebise@basedoc.fr}
    if validate_email "$ADMIN_EMAIL"; then
        break
    else
        print_error "Format d'email invalide"
    fi
done

# Nom admin
read -p "Nom complet admin [David Heurtebise]: " ADMIN_NAME
ADMIN_NAME=${ADMIN_NAME:-David Heurtebise}

# Mot de passe admin
while true; do
    read -sp "Mot de passe admin (min 8 caractères): " ADMIN_PASSWORD
    echo ""
    if validate_password "$ADMIN_PASSWORD"; then
        read -sp "Confirmer le mot de passe: " ADMIN_PASSWORD_CONFIRM
        echo ""
        if [ "$ADMIN_PASSWORD" = "$ADMIN_PASSWORD_CONFIRM" ]; then
            break
        else
            print_error "Les mots de passe ne correspondent pas"
        fi
    fi
done

# Générer mot de passe PostgreSQL sécurisé
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
SECRET_KEY=$(openssl rand -hex 32)

print_success "Informations collectées"

################################################################################
# BACKUP SI INSTALLATION EXISTANTE
################################################################################
if [ -d "$APP_DIR" ]; then
    print_step "Sauvegarde de l'installation existante"
    mv "$APP_DIR" "$APP_DIR.backup.$(date +%Y%m%d_%H%M%S)"
    print_success "Backup créé"
fi

################################################################################
# 1. MISE À JOUR SYSTÈME
################################################################################
print_step "1/14 Mise à jour du système"
apt update -qq
DEBIAN_FRONTEND=noninteractive apt upgrade -y -qq
print_success "Système mis à jour"

################################################################################
# 2. INSTALLATION DÉPENDANCES SYSTÈME
################################################################################
print_step "2/14 Installation des dépendances système"
DEBIAN_FRONTEND=noninteractive apt install -y -qq \
    python3.12 \
    python3.12-venv \
    python3-pip \
    python3-dev \
    build-essential \
    libpq-dev \
    nginx \
    postgresql \
    postgresql-contrib \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    wget \
    libmagic1 \
    supervisor \
    ufw \
    fail2ban \
    unattended-upgrades
print_success "Dépendances installées"

################################################################################
# 3. CONFIGURATION PARE-FEU
################################################################################
print_step "3/14 Configuration du pare-feu"
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw --force reload
print_success "Pare-feu configuré"

################################################################################
# 4. CONFIGURATION POSTGRESQL
################################################################################
print_step "4/14 Configuration PostgreSQL"

# Créer base de données et utilisateur
sudo -u postgres psql <<EOF
-- Supprimer si existe
DROP DATABASE IF EXISTS $DB_NAME;
DROP USER IF EXISTS $DB_USER;

-- Créer avec encoding UTF-8
CREATE DATABASE $DB_NAME
    WITH ENCODING='UTF8'
    LC_COLLATE='fr_FR.UTF-8'
    LC_CTYPE='fr_FR.UTF-8'
    TEMPLATE=template0;

-- Créer utilisateur
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Permissions
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Connexion à la base
\c $DB_NAME

-- PostgreSQL 15+ permissions
GRANT ALL ON SCHEMA public TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO $DB_USER;

-- Installer extension full-text search français
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
EOF

print_success "PostgreSQL configurée"

################################################################################
# 5. CRÉATION STRUCTURE APPLICATION
################################################################################
print_step "5/14 Création de la structure de l'application"

# Créer répertoires
mkdir -p $APP_DIR
mkdir -p $APP_DIR/app/{routes,services,templates/{procedures,admin,components},static/{css,js,fonts,images}}
mkdir -p $APP_DIR/storage/procedures
mkdir -p $APP_DIR/migrations
mkdir -p $BACKUP_DIR
mkdir -p /var/log/gunicorn
mkdir -p /var/log/kb_basedoc

# Permissions temporaires pour créer les fichiers
chmod -R 755 $APP_DIR

print_success "Structure créée"

################################################################################
# 6. CRÉATION FICHIERS APPLICATION
################################################################################
print_step "6/14 Création des fichiers de l'application"

# .gitignore
cat > $APP_DIR/.gitignore << 'GITIGNORE'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Flask
instance/
.webassets-cache

# Database
*.db
*.sqlite

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Storage (files uploadés)
storage/*
!storage/.gitkeep

# Backups
*.backup
*.bak
GITIGNORE

# requirements.txt
cat > $APP_DIR/requirements.txt << 'REQUIREMENTS'
# Core Flask
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
Flask-Migrate==4.0.5

# Database
psycopg2-binary==2.9.9
alembic==1.13.1

# AI
anthropic==0.18.1

# Utilities
requests==2.31.0
markdown==3.5.1
bleach==6.1.0
python-dotenv==1.0.0

# File handling
Pillow==10.2.0
python-magic==0.4.27

# Document processing
PyMuPDF==1.23.8
pdfplumber==0.10.3
python-docx==1.1.0
mammoth==1.6.0

# Security
bcrypt==4.1.2
cryptography==42.0.0

# Server
gunicorn==21.2.0
gevent==24.2.1

# Monitoring & Performance
Flask-Caching==2.1.0
Flask-Limiter==3.5.0

# Date/Time
python-dateutil==2.8.2
REQUIREMENTS

# config.py avec améliorations sécurité
cat > $APP_DIR/config.py << 'PYCONFIG'
import os
from datetime import timedelta

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

    # Upload
    UPLOAD_FOLDER = '/var/www/kb_basedoc/storage'
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
    SESSION_COOKIE_SECURE = True  # HTTPS uniquement
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # JSON
    JSON_AS_ASCII = False  # Support UTF-8

    # Claude API
    CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')
    CLAUDE_MODEL = 'claude-sonnet-4-5-20250929'
    CLAUDE_MAX_TOKENS = 4096
    CLAUDE_TIMEOUT = 60

    # Rate limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_STRATEGY = 'fixed-window'

    # Caching
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

    # Application
    APP_NAME = 'KB Support Basedoc'
    COMPANY_NAME = 'Support IT - Gagneraud'
    VERSION = '1.0.0'

    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/kb_basedoc/app.log'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT = 10
PYCONFIG

# .env (sera rempli avec les vraies valeurs)
cat > $APP_DIR/.env << ENVFILE
# Database
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost/$DB_NAME

# Flask
SECRET_KEY=$SECRET_KEY
FLASK_APP=run.py
FLASK_ENV=production

# Claude AI
CLAUDE_API_KEY=$CLAUDE_API_KEY

# Application
APP_NAME=KB Support Basedoc
ENVFILE

chmod 600 $APP_DIR/.env

# run.py
cat > $APP_DIR/run.py << 'PYRUN'
#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Charger variables d'environnement
load_dotenv()

from app import create_app, db
from app.models import User, Category, Procedure, Tag

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Category': Category,
        'Procedure': Procedure,
        'Tag': Tag
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
PYRUN

chmod +x $APP_DIR/run.py

print_success "Fichiers de configuration créés"

################################################################################
# 7. INSTALLATION DÉPENDANCES PYTHON
################################################################################
print_step "7/14 Installation des dépendances Python"
cd $APP_DIR
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel -qq
pip install -r requirements.txt -qq
print_success "Dépendances Python installées"

################################################################################
# 8. CRÉATION DU CODE APPLICATION (sera fait dans les prochaines étapes)
################################################################################
print_step "8/14 Création du code de l'application"
# Sera complété dans la tâche 1 (développement MVP)
print_info "Squelette créé (sera complété dans le développement)"

################################################################################
# 9. CONFIGURATION GUNICORN
################################################################################
print_step "9/14 Configuration Gunicorn"

cat > $APP_DIR/gunicorn_config.py << 'PYGUNICORN'
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
worker_connections = 1000
timeout = 60
keepalive = 2

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

# SSL (si nécessaire)
# keyfile = None
# certfile = None
PYGUNICORN

# Service systemd
cat > /etc/systemd/system/kb_basedoc.service << SYSTEMD
[Unit]
Description=KB Basedoc Gunicorn Service
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_PATH/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$VENV_PATH/bin/gunicorn --config $APP_DIR/gunicorn_config.py run:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateDevices=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR/storage /var/log/gunicorn /var/log/kb_basedoc

[Install]
WantedBy=multi-user.target
SYSTEMD

# Créer répertoire pour PID
mkdir -p /var/run/gunicorn
chown $APP_USER:$APP_USER /var/run/gunicorn

systemctl daemon-reload
print_success "Gunicorn configuré"

################################################################################
# 10. CONFIGURATION NGINX
################################################################################
print_step "10/14 Configuration Nginx"

cat > /etc/nginx/sites-available/kb_basedoc << 'NGINX'
# Rate limiting
limit_req_zone $binary_remote_addr zone=kb_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=kb_api_limit:10m rate=5r/s;

# Upstream
upstream kb_basedoc_backend {
    server 127.0.0.1:8000 fail_timeout=0;
}

# HTTP - Redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name gagneraud.basedoc.fr;

    # Certbot challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name gagneraud.basedoc.fr;

    # SSL certificates (will be configured by Certbot)
    # ssl_certificate /etc/letsencrypt/live/gagneraud.basedoc.fr/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/gagneraud.basedoc.fr/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Logging
    access_log /var/log/nginx/kb_basedoc_access.log combined;
    error_log /var/log/nginx/kb_basedoc_error.log warn;

    # Max upload size
    client_max_body_size 50M;
    client_body_buffer_size 128k;

    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # Static files
    location /static {
        alias /var/www/kb_basedoc/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Uploaded files (protected by Flask)
    location /storage {
        internal;
        alias /var/www/kb_basedoc/storage;
    }

    # API endpoints with stricter rate limiting
    location /api/ {
        limit_req zone=kb_api_limit burst=10 nodelay;

        proxy_pass http://kb_basedoc_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Main application
    location / {
        limit_req zone=kb_limit burst=20 nodelay;

        proxy_pass http://kb_basedoc_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # WebSocket support (future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
NGINX

# Activer le site
ln -sf /etc/nginx/sites-available/kb_basedoc /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Tester la configuration
nginx -t
systemctl restart nginx

print_success "Nginx configuré"

################################################################################
# 11. CONFIGURATION SSL
################################################################################
print_step "11/14 Configuration SSL Let's Encrypt"

# Vérifier DNS
print_info "Vérification DNS pour $DOMAIN..."
DNS_IP=$(dig +short $DOMAIN | tail -n1 || echo "")

if [ -z "$DNS_IP" ]; then
    print_error "DNS non résolu. Vérifiez la configuration DNS."
    print_info "Vous devrez configurer SSL manuellement :"
    print_info "  sudo certbot --nginx -d $DOMAIN"
elif [ "$DNS_IP" != "193.70.41.117" ]; then
    print_error "DNS pointe vers $DNS_IP au lieu de 193.70.41.117"
    print_info "Attendez la propagation DNS puis exécutez :"
    print_info "  sudo certbot --nginx -d $DOMAIN"
else
    print_success "DNS correctement configuré"

    # Obtenir certificat SSL
    certbot --nginx -d $DOMAIN \
        --non-interactive \
        --agree-tos \
        --email "$ADMIN_EMAIL" \
        --redirect \
        --hsts \
        --staple-ocsp \
        2>&1 | tee -a "$LOG_FILE"

    if [ $? -eq 0 ]; then
        print_success "SSL configuré avec succès"

        # Renouvellement automatique
        systemctl enable certbot.timer
        systemctl start certbot.timer
        print_success "Renouvellement automatique activé"
    else
        print_error "Échec de la configuration SSL"
        print_info "Réessayez manuellement : sudo certbot --nginx -d $DOMAIN"
    fi
fi

################################################################################
# 12. CONFIGURATION FAIL2BAN
################################################################################
print_step "12/14 Configuration Fail2Ban"

cat > /etc/fail2ban/jail.local << 'FAIL2BAN'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/kb_basedoc_error.log
FAIL2BAN

systemctl restart fail2ban
print_success "Fail2Ban configuré"

################################################################################
# 13. SCRIPT DE BACKUP AUTOMATIQUE
################################################################################
print_step "13/14 Configuration du backup automatique"

cat > /etc/cron.daily/kb_basedoc_backup << 'BACKUP'
#!/bin/bash
# Backup quotidien KB Basedoc

BACKUP_DIR="/var/backups/kb_basedoc"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"

# Backup PostgreSQL
pg_dump kb_basedoc | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Backup fichiers uploadés
tar -czf "$BACKUP_DIR/storage_$DATE.tar.gz" /var/www/kb_basedoc/storage/

# Backup configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
    /var/www/kb_basedoc/.env \
    /var/www/kb_basedoc/config.py \
    /etc/nginx/sites-available/kb_basedoc \
    /etc/systemd/system/kb_basedoc.service

# Supprimer les backups de plus de 30 jours
find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete

# Log
echo "[$(date)] Backup completed" >> /var/log/kb_basedoc/backup.log
BACKUP

chmod +x /etc/cron.daily/kb_basedoc_backup

print_success "Backup automatique configuré"

################################################################################
# 14. PERMISSIONS FINALES
################################################################################
print_step "14/14 Configuration des permissions"

chown -R $APP_USER:$APP_USER $APP_DIR
chmod -R 755 $APP_DIR
chmod -R 775 $APP_DIR/storage
chmod 600 $APP_DIR/.env

chown -R $APP_USER:$APP_USER /var/log/gunicorn
chown -R $APP_USER:$APP_USER /var/log/kb_basedoc

print_success "Permissions configurées"

################################################################################
# SAUVEGARDE DES INFORMATIONS
################################################################################
print_step "Sauvegarde des informations d'installation"

cat > /root/kb_basedoc_install_info.txt << INSTALLINFO
════════════════════════════════════════════════════════════════
Installation KB Support Basedoc
Date: $(date)
════════════════════════════════════════════════════════════════

URL: https://$DOMAIN

ADMIN
-----
Email: $ADMIN_EMAIL
Nom: $ADMIN_NAME
Mot de passe: [défini lors de l'installation]

BASE DE DONNÉES
---------------
Database: $DB_NAME
User: $DB_USER
Password: $DB_PASSWORD

CLAUDE AI
---------
API Key: $CLAUDE_API_KEY

CHEMINS
-------
Application: $APP_DIR
Logs Gunicorn: /var/log/gunicorn/
Logs Application: /var/log/kb_basedoc/
Logs Nginx: /var/log/nginx/
Backups: $BACKUP_DIR

COMMANDES UTILES
----------------
# Redémarrer l'application
sudo systemctl restart kb_basedoc

# Voir les logs en temps réel
sudo journalctl -u kb_basedoc -f
sudo tail -f /var/log/gunicorn/error.log
sudo tail -f /var/log/kb_basedoc/app.log

# Status des services
sudo systemctl status kb_basedoc
sudo systemctl status nginx
sudo systemctl status postgresql

# Backup manuel
sudo /etc/cron.daily/kb_basedoc_backup

# Renouveler SSL
sudo certbot renew

# Accéder au shell Flask
cd $APP_DIR
source venv/bin/activate
flask shell

════════════════════════════════════════════════════════════════
INSTALLINFO

chmod 600 /root/kb_basedoc_install_info.txt

################################################################################
# POST-INSTALLATION
################################################################################
print_step "Vérification post-installation"

# Vérifier PostgreSQL
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    print_success "PostgreSQL: Base de données OK"
else
    print_error "PostgreSQL: Problème avec la base de données"
fi

# Vérifier Nginx
if systemctl is-active --quiet nginx; then
    print_success "Nginx: Service actif"
else
    print_error "Nginx: Service inactif"
fi

# Note: Gunicorn ne démarrera pas tant que l'application n'est pas complète
print_info "Gunicorn: Sera démarré après le développement de l'application"

################################################################################
# FIN INSTALLATION
################################################################################
echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✓ INSTALLATION DE BASE TERMINÉE AVEC SUCCÈS !${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${YELLOW}📋 Informations importantes :${NC}"
echo "────────────────────────────────────────────────────────────────"
echo "URL: https://$DOMAIN"
echo "Admin: $ADMIN_EMAIL"
echo ""
echo -e "${YELLOW}📁 Fichiers de configuration :${NC}"
echo "/root/kb_basedoc_install_info.txt - Informations complètes"
echo "$LOG_FILE - Log d'installation"
echo ""
echo -e "${YELLOW}⚠️  Prochaines étapes :${NC}"
echo "1. Développer l'application (Phase 1 - MVP)"
echo "2. Initialiser la base de données (flask db upgrade)"
echo "3. Créer l'utilisateur admin"
echo "4. Démarrer le service (systemctl start kb_basedoc)"
echo "5. Tester l'application"
echo ""
echo -e "${YELLOW}🔒 Sécurité :${NC}"
echo "- Pare-feu activé (UFW)"
echo "- Fail2Ban configuré"
echo "- SSL Let's Encrypt (si DNS configuré)"
echo "- Backup quotidien automatique"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

log "=== Installation terminée avec succès ==="
