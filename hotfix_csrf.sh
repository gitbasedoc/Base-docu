#!/bin/bash
#
# Script de hotfix pour ajouter le token CSRF au template login
#

echo "==================================="
echo "  Hotfix CSRF - KB Support Basedoc"
echo "==================================="
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Chemin de l'application
APP_DIR="/var/www/kb_basedoc"
TEMPLATE_FILE="$APP_DIR/app/templates/login.html"

echo -e "${YELLOW}[1/3]${NC} Vérification du fichier template..."

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}✗ Erreur : Fichier $TEMPLATE_FILE non trouvé${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Fichier trouvé${NC}"
echo ""

echo -e "${YELLOW}[2/3]${NC} Application du correctif..."

# Vérifier si le correctif est déjà appliqué
if grep -q "csrf_token()" "$TEMPLATE_FILE"; then
    echo -e "${GREEN}✓ Le token CSRF est déjà présent${NC}"
else
    # Faire une sauvegarde
    cp "$TEMPLATE_FILE" "$TEMPLATE_FILE.bak"
    echo "  Sauvegarde créée : $TEMPLATE_FILE.bak"

    # Appliquer le correctif
    sed -i '/<form method="POST" class="login-form">/a\            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>' "$TEMPLATE_FILE"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Correctif appliqué avec succès${NC}"
    else
        echo -e "${RED}✗ Erreur lors de l'application du correctif${NC}"
        # Restaurer la sauvegarde
        mv "$TEMPLATE_FILE.bak" "$TEMPLATE_FILE"
        exit 1
    fi
fi
echo ""

echo -e "${YELLOW}[3/3]${NC} Redémarrage de l'application..."

sudo systemctl restart kb_basedoc

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Application redémarrée${NC}"
else
    echo -e "${RED}✗ Erreur lors du redémarrage${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  Hotfix appliqué avec succès !${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Vous pouvez maintenant vous reconnecter à l'application."
echo ""
echo "Pour vérifier les logs :"
echo "  sudo tail -f /var/log/kb_basedoc/app.log"
echo ""
