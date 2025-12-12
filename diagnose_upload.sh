#!/bin/bash
#
# Script de diagnostic pour les fonctionnalités d'upload
#

echo "=========================================="
echo "  Diagnostic Upload/Import - KB Basedoc"
echo "=========================================="
echo ""

APP_DIR="/var/www/kb_basedoc"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}[CHECK 1]${NC} Vérification des répertoires de stockage..."
if [ -d "$APP_DIR/storage" ]; then
    echo -e "${GREEN}✓ storage/ existe${NC}"
    ls -la "$APP_DIR/storage/"
else
    echo -e "${RED}✗ storage/ n'existe pas${NC}"
    echo "Création..."
    mkdir -p "$APP_DIR/storage/images"
    mkdir -p "$APP_DIR/storage/temp"
fi

if [ -d "$APP_DIR/storage/images" ]; then
    echo -e "${GREEN}✓ storage/images/ existe${NC}"
else
    echo -e "${RED}✗ storage/images/ n'existe pas${NC}"
    mkdir -p "$APP_DIR/storage/images"
fi

if [ -d "$APP_DIR/storage/temp" ]; then
    echo -e "${GREEN}✓ storage/temp/ existe${NC}"
else
    echo -e "${RED}✗ storage/temp/ n'existe pas${NC}"
    mkdir -p "$APP_DIR/storage/temp"
fi

echo ""
echo -e "${BLUE}[CHECK 2]${NC} Vérification des permissions..."
stat -c "Permissions: %a Owner: %U:%G" "$APP_DIR/storage"
stat -c "Permissions: %a Owner: %U:%G" "$APP_DIR/storage/images" 2>/dev/null || echo "images/ n'existe pas"
stat -c "Permissions: %a Owner: %U:%G" "$APP_DIR/storage/temp" 2>/dev/null || echo "temp/ n'existe pas"

echo ""
echo -e "${BLUE}[CHECK 3]${NC} Vérification des dépendances Python..."
cd "$APP_DIR"
source venv/bin/activate

echo -n "PyMuPDF (fitz): "
python -c "import fitz; print('✓ Installé - version', fitz.version)" 2>/dev/null || echo "✗ NON INSTALLÉ"

echo -n "python-docx: "
python -c "from docx import Document; print('✓ Installé')" 2>/dev/null || echo "✗ NON INSTALLÉ"

echo -n "Pillow (PIL): "
python -c "from PIL import Image; print('✓ Installé')" 2>/dev/null || echo "✗ NON INSTALLÉ"

echo ""
echo -e "${BLUE}[CHECK 4]${NC} Vérification du blueprint files..."
python << 'PYEOF'
import sys
sys.path.insert(0, '/var/www/kb_basedoc')
try:
    from app import create_app
    app = create_app()

    print("\nRoutes /files disponibles:")
    with app.app_context():
        for rule in app.url_map.iter_rules():
            if '/files' in rule.rule or '/uploads' in rule.rule:
                methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
                print(f"  ✓ {rule.rule:40s} {methods:20s} {rule.endpoint}")

except Exception as e:
    print(f"✗ ERREUR: {e}")
    import traceback
    traceback.print_exc()
PYEOF

echo ""
echo -e "${BLUE}[CHECK 5]${NC} Test d'accès aux routes..."
echo "Test GET /uploads/test.txt"
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost/uploads/test.txt

echo ""
echo "Test POST /files/upload-image (sans fichier)"
curl -s -o /dev/null -w "Status: %{http_code}\n" -X POST http://localhost/files/upload-image

echo ""
echo -e "${BLUE}[CHECK 6]${NC} Dernières erreurs dans les logs..."
echo "--- Logs App (20 dernières lignes) ---"
tail -20 /var/log/kb_basedoc/app.log 2>/dev/null || echo "Pas de logs app"

echo ""
echo "--- Logs Gunicorn Error (20 dernières lignes) ---"
tail -20 /var/log/gunicorn/error.log 2>/dev/null || echo "Pas de logs gunicorn"

echo ""
echo -e "${BLUE}[CHECK 7]${NC} Test création de fichier dans storage..."
TEST_FILE="$APP_DIR/storage/images/test_write.txt"
echo "test" > "$TEST_FILE" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Écriture dans storage/images OK${NC}"
    rm "$TEST_FILE"
else
    echo -e "${RED}✗ Impossible d'écrire dans storage/images${NC}"
fi

echo ""
echo "=========================================="
echo "  Fin du diagnostic"
echo "=========================================="
