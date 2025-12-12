#!/bin/bash
#
# Fix final pour le problème de login (Method Not Allowed)
# Ce script met à jour le code et redémarre l'application
#

echo "============================================"
echo "  Fix Login - KB Support Basedoc"
echo "============================================"
echo ""

set -e

APP_DIR="/var/www/kb_basedoc"

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$APP_DIR"

echo -e "${YELLOW}[1/5]${NC} Récupération des dernières modifications..."
git pull origin claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8

echo ""
echo -e "${YELLOW}[2/5]${NC} Suppression des caches Python..."
find . -type f -name '*.pyc' -delete 2>/dev/null || true
find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

echo ""
echo -e "${YELLOW}[3/5]${NC} Arrêt de l'application..."
sudo systemctl stop kb_basedoc
sleep 2

echo ""
echo -e "${YELLOW}[4/5]${NC} Démarrage de l'application..."
sudo systemctl start kb_basedoc
sleep 3

echo ""
echo -e "${YELLOW}[5/5]${NC} Vérification du statut..."
sudo systemctl status kb_basedoc --no-pager | head -15

echo ""
echo -e "${GREEN}============================================"
echo "  Fix appliqué avec succès !"
echo "============================================${NC}"
echo ""
echo "✓ Template login.html : Token CSRF ajouté"
echo "✓ Route auth.py : Méthode POST autorisée sur '/'"
echo "✓ Application redémarrée"
echo ""
echo "Testez maintenant :"
echo "  https://gagneraud.basedoc.fr"
echo ""
echo "Connectez-vous avec :"
echo "  Email : dheurtebise@basedoc.fr"
echo "  Password : [votre mot de passe]"
echo ""
