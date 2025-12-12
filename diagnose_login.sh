#!/bin/bash
#
# Script de diagnostic pour le problème de login
#

echo "=========================================="
echo "  Diagnostic KB Support Basedoc - Login"
echo "=========================================="
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

APP_DIR="/var/www/kb_basedoc"

echo -e "${BLUE}[CHECK 1]${NC} Vérification du template login.html..."
if grep -q "csrf_token()" "$APP_DIR/app/templates/login.html"; then
    echo -e "${GREEN}✓ Token CSRF présent dans le template${NC}"
else
    echo -e "${RED}✗ Token CSRF manquant dans le template${NC}"
fi
echo ""

echo -e "${BLUE}[CHECK 2]${NC} Vérification du service kb_basedoc..."
systemctl is-active --quiet kb_basedoc
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Service kb_basedoc actif${NC}"
else
    echo -e "${RED}✗ Service kb_basedoc inactif${NC}"
fi
echo ""

echo -e "${BLUE}[CHECK 3]${NC} Dernières lignes des logs d'erreur..."
echo -e "${YELLOW}--- Logs Gunicorn ---${NC}"
tail -20 /var/log/gunicorn/error.log 2>/dev/null || echo "Pas de logs Gunicorn"
echo ""
echo -e "${YELLOW}--- Logs Application ---${NC}"
tail -20 /var/log/kb_basedoc/app.log 2>/dev/null || echo "Pas de logs app"
echo ""

echo -e "${BLUE}[CHECK 4]${NC} Test de la route login..."
echo "Test GET /"
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost/
echo ""
echo "Test POST / (sans données)"
curl -s -o /dev/null -w "Status: %{http_code}\n" -X POST http://localhost/
echo ""

echo -e "${BLUE}[CHECK 5]${NC} Vérification configuration Flask..."
cd "$APP_DIR"
source venv/bin/activate
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/var/www/kb_basedoc')
try:
    from app import create_app
    app = create_app()

    print("\nRoutes enregistrées:")
    with app.app_context():
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
            print(f"  {rule.endpoint:30s} {methods:20s} {rule.rule}")

    print("\nBlueprints enregistrés:")
    for name, blueprint in app.blueprints.items():
        print(f"  - {name}")

except Exception as e:
    print(f"ERREUR: {e}")
    import traceback
    traceback.print_exc()
PYEOF
echo ""

echo -e "${BLUE}[CHECK 6]${NC} Processus Gunicorn..."
ps aux | grep gunicorn | grep -v grep
echo ""

echo -e "${BLUE}[CHECK 7]${NC} Configuration Nginx..."
nginx -t 2>&1
echo ""

echo "=========================================="
echo "  Fin du diagnostic"
echo "=========================================="
