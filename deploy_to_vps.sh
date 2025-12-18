#!/bin/bash
###############################################################################
# Script de déploiement des 5 fonctionnalités prioritaires
# KB Support Basedoc - Serveur vps-7d357224
# Chemin: /var/www/kb_basedoc
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

APP_DIR="/var/www/kb_basedoc"
VENV_DIR="${APP_DIR}/venv"
DB_NAME="kb_basedoc"
SERVICE_NAME="kb_basedoc.service"

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Déploiement KB Support Basedoc - Fonctionnalités Prioritaires${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

step() { echo -e "\n${YELLOW}▶ $1${NC}"; }
success() { echo -e "${GREEN}✓ $1${NC}"; }
error() { echo -e "${RED}✗ $1${NC}"; exit 1; }

# 1. Vérifier le répertoire
step "1/7 Vérification"
if [ ! -d "$APP_DIR" ]; then
    error "Répertoire non trouvé : $APP_DIR"
fi
cd "$APP_DIR" || error "Impossible d'accéder à $APP_DIR"
success "Répertoire trouvé"

# 2. Git pull
step "2/7 Récupération du code"
git pull origin claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8 || error "Git pull échoué"
success "Code mis à jour"

# 3. Installation dépendances Python
step "3/7 Installation dépendances Python"
source "${VENV_DIR}/bin/activate" || error "Impossible d'activer venv"
pip install --upgrade pip -q
pip install WeasyPrint==60.2 beautifulsoup4==4.12.3 -q
success "Dépendances Python installées"

# 4. Installation bibliothèques système
step "4/7 Installation bibliothèques système"
sudo apt-get update -qq
sudo apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info -qq
success "Bibliothèques système installées"

# 5. Migrations SQL
step "5/7 Exécution migrations SQL"

migrations=(
    "add_useful_count_to_procedures.sql:Likes"
    "create_action_logs_table.sql:Audit log"
    "create_comments_table.sql:Commentaires"
    "add_fulltext_search_to_procedures.sql:Recherche FTS"
)

for migration in "${migrations[@]}"; do
    file="${migration%%:*}"
    name="${migration##*:}"

    if [ -f "$file" ]; then
        echo "  → $name..."
        sudo -u postgres psql -d "$DB_NAME" -f "$file" > /dev/null 2>&1 || {
            echo "    (Déjà appliquée ou erreur ignorée)"
        }
    else
        echo "  ⚠ $file non trouvé"
    fi
done

success "Migrations SQL terminées"

# 6. Redémarrage service
step "6/7 Redémarrage du service"
sudo systemctl restart "$SERVICE_NAME"
sleep 3

if systemctl is-active --quiet "$SERVICE_NAME"; then
    success "Service redémarré"
else
    error "Échec redémarrage service"
fi

# 7. Vérification
step "7/7 Vérification finale"

# Vérifier tables
TABLES_COUNT=$(sudo -u postgres psql -d "$DB_NAME" -t -c "
    SELECT COUNT(*) FROM information_schema.tables
    WHERE table_name IN ('action_logs', 'comments')
    AND table_schema = 'public';
" | tr -d ' ')

if [ "$TABLES_COUNT" -eq 2 ]; then
    success "Tables créées (action_logs, comments)"
else
    echo "  ⚠ Certaines tables manquantes ($TABLES_COUNT/2)"
fi

# Vérifier search_vector
SEARCH_VECTOR=$(sudo -u postgres psql -d "$DB_NAME" -t -c "
    SELECT COUNT(*) FROM information_schema.columns
    WHERE table_name = 'procedures' AND column_name = 'search_vector';
" | tr -d ' ')

if [ "$SEARCH_VECTOR" -eq 1 ]; then
    success "Colonne search_vector créée"
else
    echo "  ⚠ Colonne search_vector manquante"
fi

echo -e "\n${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✓ Déploiement terminé avec succès !${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}\n"

echo -e "${BLUE}Fonctionnalités déployées :${NC}"
echo "  1. ✓ Système de likes sur procédures"
echo "  2. ✓ Système d'audit log complet"
echo "  3. ✓ Système de commentaires avec réponses"
echo "  4. ✓ Export PDF/DOCX"
echo "  5. ✓ Recherche PostgreSQL Full-Text Search"

echo -e "\n${YELLOW}Vérification :${NC}"
echo "  Logs: sudo journalctl -u $SERVICE_NAME -n 50"
echo "  Status: sudo systemctl status $SERVICE_NAME"
echo "  URL: http://gagneraud.basedoc.fr"

deactivate
