#!/bin/bash

################################################################################
# Script de vérification installation KB Support Basedoc
# À exécuter après l'installation pour vérifier que tout fonctionne
################################################################################

set -euo pipefail

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCORE=0
TOTAL=0

check() {
    local name=$1
    local command=$2

    TOTAL=$((TOTAL + 1))

    echo -n "[$TOTAL] Vérification $name... "

    if eval "$command" &>/dev/null; then
        echo -e "${GREEN}✓${NC}"
        SCORE=$((SCORE + 1))
        return 0
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

check_output() {
    local name=$1
    local command=$2
    local expected=$3

    TOTAL=$((TOTAL + 1))

    echo -n "[$TOTAL] Vérification $name... "

    output=$(eval "$command" 2>/dev/null || echo "")

    if [[ "$output" == *"$expected"* ]]; then
        echo -e "${GREEN}✓${NC} ($output)"
        SCORE=$((SCORE + 1))
        return 0
    else
        echo -e "${RED}✗${NC} (attendu: $expected, obtenu: $output)"
        return 1
    fi
}

echo "════════════════════════════════════════════════════════════════"
echo "   🔍 Vérification installation KB Support Basedoc"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Vérifications système
echo "━━━ SYSTÈME ━━━"
check "OS Ubuntu" "lsb_release -d | grep -i ubuntu"
check "Python 3.12 installé" "python3.12 --version"
check "PostgreSQL installé" "pg_config --version"
check "Nginx installé" "nginx -v"
check "Certbot installé" "certbot --version"

echo ""

# Vérifications services
echo "━━━ SERVICES ━━━"
check "PostgreSQL actif" "systemctl is-active postgresql"
check "Nginx actif" "systemctl is-active nginx"
check "Fail2Ban actif" "systemctl is-active fail2ban"
check "Certbot timer actif" "systemctl is-active certbot.timer"

echo ""

# Vérifications base de données
echo "━━━ BASE DE DONNÉES ━━━"
check "Base kb_basedoc existe" "sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw kb_basedoc"
check "Utilisateur kb_user existe" "sudo -u postgres psql -c '\du' | grep -q kb_user"
check "Extension unaccent" "sudo -u postgres psql kb_basedoc -c 'SELECT * FROM pg_extension' | grep -q unaccent"
check "Extension pg_trgm" "sudo -u postgres psql kb_basedoc -c 'SELECT * FROM pg_extension' | grep -q pg_trgm"

echo ""

# Vérifications fichiers
echo "━━━ FICHIERS APPLICATION ━━━"
check "Répertoire /var/www/kb_basedoc" "[ -d /var/www/kb_basedoc ]"
check "Virtual environment" "[ -d /var/www/kb_basedoc/venv ]"
check "Fichier .env" "[ -f /var/www/kb_basedoc/.env ]"
check "Fichier config.py" "[ -f /var/www/kb_basedoc/config.py ]"
check "Fichier requirements.txt" "[ -f /var/www/kb_basedoc/requirements.txt ]"
check "Fichier run.py" "[ -f /var/www/kb_basedoc/run.py ]"
check "Fichier gunicorn_config.py" "[ -f /var/www/kb_basedoc/gunicorn_config.py ]"
check "Répertoire storage" "[ -d /var/www/kb_basedoc/storage ]"

echo ""

# Vérifications configuration
echo "━━━ CONFIGURATION ━━━"
check "Systemd service kb_basedoc" "[ -f /etc/systemd/system/kb_basedoc.service ]"
check "Nginx site kb_basedoc" "[ -f /etc/nginx/sites-available/kb_basedoc ]"
check "Nginx site enabled" "[ -L /etc/nginx/sites-enabled/kb_basedoc ]"
check "Configuration Nginx valide" "nginx -t"

echo ""

# Vérifications sécurité
echo "━━━ SÉCURITÉ ━━━"
check "Pare-feu UFW actif" "ufw status | grep -q 'Status: active'"
check "Port 22 (SSH) autorisé" "ufw status | grep -q '22.*ALLOW'"
check "Port 80 (HTTP) autorisé" "ufw status | grep -q '80.*ALLOW'"
check "Port 443 (HTTPS) autorisé" "ufw status | grep -q '443.*ALLOW'"
check "Fail2Ban jail SSH" "fail2ban-client status sshd"
check "Permissions .env (600)" "[ \$(stat -c %a /var/www/kb_basedoc/.env) = '600' ]"

echo ""

# Vérifications backup
echo "━━━ BACKUP ━━━"
check "Répertoire backup" "[ -d /var/backups/kb_basedoc ]"
check "Script backup quotidien" "[ -f /etc/cron.daily/kb_basedoc_backup ]"
check "Script backup exécutable" "[ -x /etc/cron.daily/kb_basedoc_backup ]"

echo ""

# Vérifications logs
echo "━━━ LOGS ━━━"
check "Répertoire logs Gunicorn" "[ -d /var/log/gunicorn ]"
check "Répertoire logs KB" "[ -d /var/log/kb_basedoc ]"
check "Logs Nginx access" "[ -f /var/log/nginx/kb_basedoc_access.log ]"
check "Logs Nginx error" "[ -f /var/log/nginx/kb_basedoc_error.log ]"

echo ""

# Vérifications réseau
echo "━━━ RÉSEAU ━━━"
check "DNS résolu" "dig +short gagneraud.basedoc.fr | grep -q ."
check_output "DNS pointe vers" "dig +short gagneraud.basedoc.fr | tail -n1" "193.70.41.117"
check "Port 80 ouvert" "nc -zv 127.0.0.1 80 2>&1 | grep -q succeeded || nc -zv 127.0.0.1 80 2>&1 | grep -q open"
check "Port 443 ouvert" "nc -zv 127.0.0.1 443 2>&1 | grep -q succeeded || nc -zv 127.0.0.1 443 2>&1 | grep -q open"

if [ -d /etc/letsencrypt/live/gagneraud.basedoc.fr ]; then
    check "Certificat SSL présent" "[ -f /etc/letsencrypt/live/gagneraud.basedoc.fr/fullchain.pem ]"
    check "Clé privée SSL présente" "[ -f /etc/letsencrypt/live/gagneraud.basedoc.fr/privkey.pem ]"
else
    echo "  ⚠️  SSL non configuré (normal si DNS pas encore propagé)"
fi

echo ""

# Vérifications Python packages
echo "━━━ PACKAGES PYTHON ━━━"
if [ -f /var/www/kb_basedoc/venv/bin/activate ]; then
    source /var/www/kb_basedoc/venv/bin/activate
    check "Flask installé" "python -c 'import flask'"
    check "SQLAlchemy installé" "python -c 'import flask_sqlalchemy'"
    check "Anthropic installé" "python -c 'import anthropic'"
    check "Gunicorn installé" "python -c 'import gunicorn'"
    deactivate
fi

echo ""

# Résumé
echo "════════════════════════════════════════════════════════════════"
PERCENT=$((SCORE * 100 / TOTAL))

if [ $PERCENT -ge 90 ]; then
    COLOR=$GREEN
    STATUS="EXCELLENT"
elif [ $PERCENT -ge 75 ]; then
    COLOR=$YELLOW
    STATUS="BON (quelques points à vérifier)"
elif [ $PERCENT -ge 50 ]; then
    COLOR=$YELLOW
    STATUS="MOYEN (plusieurs problèmes)"
else
    COLOR=$RED
    STATUS="PROBLÉMATIQUE"
fi

echo -e "${COLOR}Score: $SCORE/$TOTAL ($PERCENT%) - $STATUS${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""

if [ $PERCENT -lt 100 ]; then
    echo "⚠️  Vérifiez les points en échec ci-dessus"
    echo "📋 Consultez /var/log/kb_basedoc_install.log pour plus de détails"
else
    echo "✓ Installation complète et fonctionnelle !"
fi

echo ""
