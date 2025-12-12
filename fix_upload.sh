#!/bin/bash
#
# Script de correction automatique des problèmes d'upload
#

echo "=========================================="
echo "  Fix Upload/Import - KB Basedoc"
echo "=========================================="
echo ""

set -e

APP_DIR="/var/www/kb_basedoc"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[1/7]${NC} Création des répertoires de stockage..."
mkdir -p "$APP_DIR/storage/images"
mkdir -p "$APP_DIR/storage/temp"
mkdir -p "$APP_DIR/storage/attachments"
echo -e "${GREEN}✓ Répertoires créés${NC}"

echo ""
echo -e "${YELLOW}[2/7]${NC} Configuration des permissions..."
chown -R ubuntu:ubuntu "$APP_DIR/storage"
chmod -R 755 "$APP_DIR/storage"
echo -e "${GREEN}✓ Permissions configurées${NC}"

echo ""
echo -e "${YELLOW}[3/7]${NC} Vérification et installation des dépendances Python..."
cd "$APP_DIR"
source venv/bin/activate

# PyMuPDF
python -c "import fitz" 2>/dev/null || {
    echo "  Installation de PyMuPDF..."
    pip install PyMuPDF
}

# python-docx
python -c "from docx import Document" 2>/dev/null || {
    echo "  Installation de python-docx..."
    pip install python-docx
}

# Pillow
python -c "from PIL import Image" 2>/dev/null || {
    echo "  Installation de Pillow..."
    pip install Pillow
}

echo -e "${GREEN}✓ Dépendances vérifiées${NC}"

echo ""
echo -e "${YELLOW}[4/7]${NC} Vérification de la configuration Nginx..."
# Vérifier la taille max d'upload dans Nginx
if ! grep -q "client_max_body_size" /etc/nginx/sites-available/kb_basedoc; then
    echo "  Ajout de client_max_body_size à la config Nginx..."
    sudo sed -i '/server_name/a\    client_max_body_size 50M;' /etc/nginx/sites-available/kb_basedoc
    sudo nginx -t && sudo systemctl reload nginx
    echo -e "${GREEN}✓ Nginx configuré${NC}"
else
    echo -e "${GREEN}✓ client_max_body_size déjà configuré${NC}"
fi

echo ""
echo -e "${YELLOW}[5/7]${NC} Vérification du fichier .env..."
if ! grep -q "UPLOAD_FOLDER" "$APP_DIR/.env"; then
    echo "  Ajout de UPLOAD_FOLDER dans .env..."
    echo "UPLOAD_FOLDER=/var/www/kb_basedoc/storage" >> "$APP_DIR/.env"
    echo -e "${GREEN}✓ .env mis à jour${NC}"
else
    echo -e "${GREEN}✓ UPLOAD_FOLDER déjà configuré${NC}"
fi

echo ""
echo -e "${YELLOW}[6/7]${NC} Nettoyage et redémarrage..."
# Nettoyer les fichiers temporaires
find "$APP_DIR/storage/temp" -type f -mtime +1 -delete 2>/dev/null || true

# Nettoyer le cache Python
find "$APP_DIR" -type f -name '*.pyc' -delete 2>/dev/null || true
find "$APP_DIR" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

# Redémarrer l'application
sudo systemctl restart kb_basedoc
sleep 3
echo -e "${GREEN}✓ Application redémarrée${NC}"

echo ""
echo -e "${YELLOW}[7/7]${NC} Vérification du statut..."
sudo systemctl status kb_basedoc --no-pager | head -15

echo ""
echo "=========================================="
echo -e "${GREEN}  Correction terminée !${NC}"
echo "=========================================="
echo ""
echo "Test des fonctionnalités :"
echo "  1. Allez sur https://gagneraud.basedoc.fr"
echo "  2. Créez une nouvelle procédure"
echo "  3. Testez l'upload d'image (drag & drop)"
echo "  4. Testez l'import PDF/Word"
echo ""
echo "Si le problème persiste, lancez le diagnostic :"
echo "  sudo bash diagnose_upload.sh"
echo ""
