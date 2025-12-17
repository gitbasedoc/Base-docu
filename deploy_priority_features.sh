#!/bin/bash
###############################################################################
# Script de déploiement des 5 fonctionnalités prioritaires
# KB Support Basedoc - Déploiement sur serveur de production
#
# Fonctionnalités :
# 1. Système de likes sur procédures
# 2. Système d'audit log complet
# 3. Système de commentaires avec réponses
# 4. Export PDF/DOCX pour procédures
# 5. Recherche PostgreSQL Full-Text Search avec ranking
#
# Usage: ./deploy_priority_features.sh
###############################################################################

set -e  # Arrêter en cas d'erreur

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/kb-basedoc"
VENV_DIR="${APP_DIR}/venv"
DB_NAME="kb_basedoc"
DB_USER="kb_user"
SERVICE_NAME="kb-basedoc"

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Déploiement des fonctionnalités prioritaires${NC}"
echo -e "${BLUE}  KB Support Basedoc${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

# Fonction pour afficher les étapes
step() {
    echo -e "\n${YELLOW}▶ $1${NC}"
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

# Vérifier si nous sommes root ou si nous avons sudo
if [ "$EUID" -ne 0 ]; then
    if ! command -v sudo &> /dev/null; then
        error "Ce script nécessite les droits root ou sudo"
    fi
    SUDO="sudo"
else
    SUDO=""
fi

# 1. Vérifier que l'application existe
step "1/6 Vérification de l'installation"
if [ ! -d "$APP_DIR" ]; then
    error "Répertoire de l'application non trouvé : $APP_DIR"
fi
success "Répertoire de l'application trouvé"

# 2. Activer l'environnement virtuel et installer les dépendances
step "2/6 Installation des dépendances Python"
if [ ! -d "$VENV_DIR" ]; then
    error "Environnement virtuel non trouvé : $VENV_DIR"
fi

cd "$APP_DIR"

# Activer venv et installer
$SUDO bash -c "
    source ${VENV_DIR}/bin/activate
    pip install --upgrade pip
    pip install WeasyPrint==60.2 beautifulsoup4==4.12.3
    pip install -r requirements.txt
"
success "Dépendances Python installées"

# 3. Exécuter les migrations SQL
step "3/6 Exécution des migrations SQL"

# Migration 1: Likes sur procédures
if [ -f "add_useful_count_to_procedures.sql" ]; then
    echo "  → Ajout du système de likes..."
    $SUDO -u postgres psql -d "$DB_NAME" -f add_useful_count_to_procedures.sql > /dev/null 2>&1 || {
        echo "    (Peut être déjà appliquée)"
    }
    success "  Migration likes appliquée"
else
    error "Fichier add_useful_count_to_procedures.sql non trouvé"
fi

# Migration 2: Audit log
if [ -f "create_action_logs_table.sql" ]; then
    echo "  → Création de la table d'audit..."
    $SUDO -u postgres psql -d "$DB_NAME" -f create_action_logs_table.sql > /dev/null 2>&1 || {
        echo "    (Peut être déjà appliquée)"
    }
    success "  Migration audit log appliquée"
else
    error "Fichier create_action_logs_table.sql non trouvé"
fi

# Migration 3: Commentaires
if [ -f "create_comments_table.sql" ]; then
    echo "  → Création de la table de commentaires..."
    $SUDO -u postgres psql -d "$DB_NAME" -f create_comments_table.sql > /dev/null 2>&1 || {
        echo "    (Peut être déjà appliquée)"
    }
    success "  Migration commentaires appliquée"
else
    error "Fichier create_comments_table.sql non trouvé"
fi

# Migration 4: Full-Text Search
if [ -f "add_fulltext_search_to_procedures.sql" ]; then
    echo "  → Configuration de la recherche plein texte..."
    $SUDO -u postgres psql -d "$DB_NAME" -f add_fulltext_search_to_procedures.sql > /dev/null 2>&1 || {
        echo "    (Peut être déjà appliquée)"
    }
    success "  Migration recherche plein texte appliquée"
else
    error "Fichier add_fulltext_search_to_procedures.sql non trouvé"
fi

success "Toutes les migrations SQL appliquées"

# 4. Vérifier les dépendances système pour WeasyPrint
step "4/6 Vérification des dépendances système"
echo "  → Vérification de WeasyPrint..."

# WeasyPrint nécessite certaines libs système
REQUIRED_LIBS="libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info"
MISSING_LIBS=""

for lib in $REQUIRED_LIBS; do
    if ! dpkg -l | grep -q "^ii  $lib"; then
        MISSING_LIBS="$MISSING_LIBS $lib"
    fi
done

if [ -n "$MISSING_LIBS" ]; then
    echo "  → Installation des bibliothèques manquantes..."
    $SUDO apt-get update -qq
    $SUDO apt-get install -y $MISSING_LIBS
    success "  Bibliothèques système installées"
else
    success "  Toutes les bibliothèques système présentes"
fi

# 5. Redémarrer le service
step "5/6 Redémarrage du service"
if systemctl list-units --type=service | grep -q "$SERVICE_NAME"; then
    $SUDO systemctl restart "$SERVICE_NAME"
    sleep 3

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        success "Service redémarré avec succès"
    else
        error "Échec du redémarrage du service"
    fi
else
    echo "  Service $SERVICE_NAME non trouvé, redémarrage manuel requis"
fi

# 6. Vérification finale
step "6/6 Vérification finale"

# Vérifier que les tables existent
echo "  → Vérification des tables en base..."
TABLES_CHECK=$($SUDO -u postgres psql -d "$DB_NAME" -t -c "
    SELECT COUNT(*) FROM information_schema.tables
    WHERE table_name IN ('action_logs', 'comments')
    AND table_schema = 'public';
")

if [ "$TABLES_CHECK" -eq 2 ]; then
    success "  Tables créées correctement"
else
    error "  Certaines tables sont manquantes"
fi

# Vérifier que le search_vector existe
SEARCH_VECTOR_CHECK=$($SUDO -u postgres psql -d "$DB_NAME" -t -c "
    SELECT COUNT(*) FROM information_schema.columns
    WHERE table_name = 'procedures'
    AND column_name = 'search_vector';
")

if [ "$SEARCH_VECTOR_CHECK" -eq 1 ]; then
    success "  Colonne search_vector créée"
else
    error "  Colonne search_vector manquante"
fi

echo -e "\n${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✓ Déploiement terminé avec succès !${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}\n"

echo -e "${BLUE}Fonctionnalités déployées :${NC}"
echo "  1. ✓ Système de likes sur procédures"
echo "  2. ✓ Système d'audit log complet"
echo "  3. ✓ Système de commentaires avec réponses"
echo "  4. ✓ Export PDF/DOCX pour procédures"
echo "  5. ✓ Recherche PostgreSQL Full-Text Search"

echo -e "\n${YELLOW}Prochaines étapes :${NC}"
echo "  1. Tester les fonctionnalités sur l'interface web"
echo "  2. Consulter les logs : journalctl -u $SERVICE_NAME -f"
echo "  3. Vérifier l'audit log : /admin/audit-logs"

echo -e "\n${BLUE}Accès :${NC}"
echo "  URL: http://gagneraud.basedoc.fr"
echo "  Admin: /admin"
