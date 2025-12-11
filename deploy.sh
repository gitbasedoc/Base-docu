#!/bin/bash

################################################################################
# Script de déploiement automatique KB Support Basedoc
# Usage: curl -sSL <URL_DU_SCRIPT> | bash
# Ou: ./deploy.sh
################################################################################

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   KB SUPPORT BASEDOC - DÉPLOIEMENT AUTOMATIQUE               ║
║                                                               ║
║   Ce script va :                                             ║
║   1. Cloner le repository Git                                ║
║   2. Installer toutes les dépendances                        ║
║   3. Configurer la base de données                           ║
║   4. Configurer Nginx, Gunicorn, SSL                         ║
║   5. Démarrer l'application                                  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Vérifier root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}✗ Ce script doit être exécuté en tant que root${NC}"
    echo "  Utilisez: sudo ./deploy.sh"
    exit 1
fi

# Vérifier OS
if [ ! -f /etc/os-release ]; then
    echo -e "${RED}✗ Impossible de détecter l'OS${NC}"
    exit 1
fi

. /etc/os-release

if [ "$ID" != "ubuntu" ]; then
    echo -e "${RED}✗ Ce script est prévu pour Ubuntu (détecté: $ID)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ OS compatible: Ubuntu $VERSION_ID${NC}"
echo ""

################################################################################
# CONFIGURATION
################################################################################

echo -e "${YELLOW}━━━ CONFIGURATION ━━━${NC}"
echo ""

# URL du repository Git
read -p "URL du repository Git: " REPO_URL
if [ -z "$REPO_URL" ]; then
    echo -e "${RED}✗ URL du repository requise${NC}"
    exit 1
fi

# Branche
BRANCH="claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8"
read -p "Branche Git [$BRANCH]: " INPUT_BRANCH
if [ ! -z "$INPUT_BRANCH" ]; then
    BRANCH=$INPUT_BRANCH
fi

# Clé API Claude
while true; do
    read -p "Clé API Claude (sk-ant-...): " CLAUDE_API_KEY
    if [[ "$CLAUDE_API_KEY" =~ ^sk-ant- ]]; then
        break
    else
        echo -e "${RED}✗ Format de clé invalide${NC}"
    fi
done

# Email admin
read -p "Email administrateur [dheurtebise@basedoc.fr]: " ADMIN_EMAIL
ADMIN_EMAIL=${ADMIN_EMAIL:-dheurtebise@basedoc.fr}

# Nom admin
read -p "Nom complet administrateur [David Heurtebise]: " ADMIN_NAME
ADMIN_NAME=${ADMIN_NAME:-David Heurtebise}

# Mot de passe admin
while true; do
    read -sp "Mot de passe administrateur (min 8 caractères): " ADMIN_PASSWORD
    echo ""
    if [ ${#ADMIN_PASSWORD} -ge 8 ]; then
        read -sp "Confirmer le mot de passe: " ADMIN_PASSWORD_CONFIRM
        echo ""
        if [ "$ADMIN_PASSWORD" = "$ADMIN_PASSWORD_CONFIRM" ]; then
            break
        else
            echo -e "${RED}✗ Les mots de passe ne correspondent pas${NC}"
        fi
    else
        echo -e "${RED}✗ Minimum 8 caractères${NC}"
    fi
done

echo ""
echo -e "${GREEN}✓ Configuration collectée${NC}"
echo ""

################################################################################
# 1. INSTALLATION GIT
################################################################################

echo -e "${YELLOW}━━━ 1/7 Installation de Git ━━━${NC}"
apt update -qq
apt install -y git curl wget >/dev/null 2>&1
echo -e "${GREEN}✓ Git installé${NC}"
echo ""

################################################################################
# 2. CLONAGE DU REPOSITORY
################################################################################

echo -e "${YELLOW}━━━ 2/7 Clonage du repository ━━━${NC}"

# Supprimer l'ancien si existe
if [ -d "/var/www/kb_basedoc" ]; then
    echo "  Sauvegarde de l'installation existante..."
    mv /var/www/kb_basedoc /var/www/kb_basedoc.backup.$(date +%Y%m%d_%H%M%S)
fi

# Créer répertoire temporaire
TEMP_DIR="/tmp/kb_basedoc_deploy_$$"
mkdir -p $TEMP_DIR

# Cloner
echo "  Clonage depuis $REPO_URL..."
git clone -q "$REPO_URL" $TEMP_DIR

# Checkout de la branche
cd $TEMP_DIR
echo "  Checkout de la branche $BRANCH..."
git checkout -q $BRANCH

# Copier vers destination finale
echo "  Installation dans /var/www/kb_basedoc..."
mkdir -p /var/www/kb_basedoc
cp -r $TEMP_DIR/* /var/www/kb_basedoc/
cp -r $TEMP_DIR/.* /var/www/kb_basedoc/ 2>/dev/null || true

# Nettoyer
rm -rf $TEMP_DIR

cd /var/www/kb_basedoc

echo -e "${GREEN}✓ Repository cloné${NC}"
echo ""

################################################################################
# 3. VÉRIFICATION DES FICHIERS
################################################################################

echo -e "${YELLOW}━━━ 3/7 Vérification des fichiers ━━━${NC}"

REQUIRED_FILES=(
    "install_kb_basedoc_improved.sh"
    "requirements.txt"
    "run.py"
    "config.py"
    "app/__init__.py"
)

MISSING_FILES=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "  ${RED}✗ Fichier manquant: $file${NC}"
        MISSING_FILES=$((MISSING_FILES + 1))
    else
        echo -e "  ${GREEN}✓${NC} $file"
    fi
done

if [ $MISSING_FILES -gt 0 ]; then
    echo -e "${RED}✗ $MISSING_FILES fichier(s) manquant(s)${NC}"
    echo "  Vérifiez que vous avez cloné le bon repository et la bonne branche."
    exit 1
fi

echo -e "${GREEN}✓ Tous les fichiers requis sont présents${NC}"
echo ""

################################################################################
# 4. RENDRE LES SCRIPTS EXÉCUTABLES
################################################################################

echo -e "${YELLOW}━━━ 4/7 Configuration des permissions ━━━${NC}"

chmod +x install_kb_basedoc_improved.sh
chmod +x verify_installation.sh 2>/dev/null || true

echo -e "${GREEN}✓ Permissions configurées${NC}"
echo ""

################################################################################
# 5. CRÉATION DU FICHIER .ENV
################################################################################

echo -e "${YELLOW}━━━ 5/7 Configuration de l'environnement ━━━${NC}"

# Générer les secrets
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
SECRET_KEY=$(openssl rand -hex 32)

# Créer .env
cat > /var/www/kb_basedoc/.env << ENVFILE
# Database
DATABASE_URL=postgresql://kb_user:${DB_PASSWORD}@localhost/kb_basedoc

# Flask
SECRET_KEY=${SECRET_KEY}
FLASK_APP=run.py
FLASK_ENV=production

# Claude AI
CLAUDE_API_KEY=${CLAUDE_API_KEY}
CLAUDE_MODEL=claude-sonnet-4-5-20250929
CLAUDE_MAX_TOKENS=4096
CLAUDE_TIMEOUT=60

# Application
APP_NAME=KB Support Basedoc
COMPANY_NAME=Support IT - Gagneraud
UPLOAD_FOLDER=/var/www/kb_basedoc/storage

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/kb_basedoc/app.log
ENVFILE

chmod 600 /var/www/kb_basedoc/.env

echo -e "${GREEN}✓ Fichier .env créé${NC}"
echo ""

################################################################################
# 6. MODIFICATION DU SCRIPT D'INSTALLATION
################################################################################

echo -e "${YELLOW}━━━ 6/7 Préparation de l'installation automatique ━━━${NC}"

# Créer un fichier de réponses pour l'installation
cat > /tmp/kb_install_answers.txt << ANSWERS
${CLAUDE_API_KEY}
${ADMIN_EMAIL}
${ADMIN_NAME}
${ADMIN_PASSWORD}
${ADMIN_PASSWORD}
ANSWERS

echo -e "${GREEN}✓ Réponses préparées${NC}"
echo ""

################################################################################
# 7. LANCEMENT DE L'INSTALLATION
################################################################################

echo -e "${YELLOW}━━━ 7/7 Lancement de l'installation principale ━━━${NC}"
echo ""
echo -e "${BLUE}L'installation va maintenant démarrer...${NC}"
echo -e "${BLUE}Cela peut prendre 10-15 minutes.${NC}"
echo ""
sleep 3

# Modifier le script pour mode non-interactif si nécessaire
# Ou lancer avec les réponses pré-remplies

# Pour l'instant, on va créer un wrapper qui répond automatiquement
cat > /tmp/auto_install.sh << 'WRAPPER'
#!/bin/bash
cd /var/www/kb_basedoc

# Exporter les variables d'environnement pour que le script les utilise
export CLAUDE_API_KEY_AUTO="${CLAUDE_API_KEY}"
export ADMIN_EMAIL_AUTO="${ADMIN_EMAIL}"
export ADMIN_NAME_AUTO="${ADMIN_NAME}"
export ADMIN_PASSWORD_AUTO="${ADMIN_PASSWORD}"
export DB_PASSWORD_AUTO="${DB_PASSWORD}"

# Lancer l'installation
./install_kb_basedoc_improved.sh
WRAPPER

chmod +x /tmp/auto_install.sh

# Injecter les variables
sed -i "s|CLAUDE_API_KEY=\"\${CLAUDE_API_KEY}\"|CLAUDE_API_KEY=\"${CLAUDE_API_KEY}\"|g" /tmp/auto_install.sh
sed -i "s|ADMIN_EMAIL=\"\${ADMIN_EMAIL}\"|ADMIN_EMAIL=\"${ADMIN_EMAIL}\"|g" /tmp/auto_install.sh
sed -i "s|ADMIN_NAME=\"\${ADMIN_NAME}\"|ADMIN_NAME=\"${ADMIN_NAME}\"|g" /tmp/auto_install.sh
sed -i "s|ADMIN_PASSWORD=\"\${ADMIN_PASSWORD}\"|ADMIN_PASSWORD=\"${ADMIN_PASSWORD}\"|g" /tmp/auto_install.sh
sed -i "s|DB_PASSWORD=\"\${DB_PASSWORD}\"|DB_PASSWORD=\"${DB_PASSWORD}\"|g" /tmp/auto_install.sh

# Lancer le script d'installation principal
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Installation de KB Support Basedoc en cours...${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Lancer l'installation (mode automatique avec expect si disponible)
if command -v expect &> /dev/null; then
    # Avec expect (réponses automatiques)
    expect << EXPECTSCRIPT
spawn ./install_kb_basedoc_improved.sh
expect "Continuer l'installation?" { send "o\r" }
expect "Clé API Claude" { send "${CLAUDE_API_KEY}\r" }
expect "Email admin" { send "${ADMIN_EMAIL}\r" }
expect "Nom complet admin" { send "${ADMIN_NAME}\r" }
expect "Mot de passe admin" { send "${ADMIN_PASSWORD}\r" }
expect "Confirmer le mot de passe" { send "${ADMIN_PASSWORD}\r" }
expect eof
EXPECTSCRIPT
else
    # Sans expect, on lance normalement mais l'utilisateur devra répondre
    echo -e "${YELLOW}Note: Le script va vous demander quelques informations.${NC}"
    echo -e "${YELLOW}Utilisez les valeurs que vous avez configurées au début.${NC}"
    echo ""
    sleep 2
    ./install_kb_basedoc_improved.sh
fi

################################################################################
# 8. POST-INSTALLATION
################################################################################

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS !${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo ""

    echo -e "${BLUE}📋 Informations importantes :${NC}"
    echo "────────────────────────────────────────────────────────────────"
    echo "URL: https://gagneraud.basedoc.fr"
    echo "Admin: ${ADMIN_EMAIL}"
    echo ""
    echo "Base de données:"
    echo "  Password: ${DB_PASSWORD}"
    echo "  (Sauvegardé dans /root/kb_basedoc_install_info.txt)"
    echo ""

    echo -e "${BLUE}🔍 Vérification de l'installation :${NC}"
    if [ -f "./verify_installation.sh" ]; then
        chmod +x verify_installation.sh
        ./verify_installation.sh
    fi

    echo ""
    echo -e "${BLUE}🚀 Prochaines étapes :${NC}"
    echo "1. Accédez à https://gagneraud.basedoc.fr"
    echo "2. Connectez-vous avec ${ADMIN_EMAIL}"
    echo "3. Créez votre première procédure"
    echo ""

    # Sauvegarder les informations
    cat > /root/kb_deployment_info.txt << DEPLOYINFO
Déploiement KB Support Basedoc
Date: $(date)

URL: https://gagneraud.basedoc.fr
Admin Email: ${ADMIN_EMAIL}
Admin Name: ${ADMIN_NAME}

Database Password: ${DB_PASSWORD}
Secret Key: ${SECRET_KEY}
Claude API Key: ${CLAUDE_API_KEY}

Repository: ${REPO_URL}
Branch: ${BRANCH}
DEPLOYINFO

    chmod 600 /root/kb_deployment_info.txt

    echo -e "${GREEN}✓ Informations sauvegardées dans /root/kb_deployment_info.txt${NC}"
    echo ""

else
    echo ""
    echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}✗ ERREUR LORS DU DÉPLOIEMENT${NC}"
    echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Consultez les logs pour plus de détails:"
    echo "  /var/log/kb_basedoc_install.log"
    echo ""
    exit 1
fi
