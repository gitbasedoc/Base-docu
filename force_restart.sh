#!/bin/bash
#
# Script pour forcer le redémarrage complet de l'application
#

echo "=========================================="
echo "  Force Restart - KB Support Basedoc"
echo "=========================================="
echo ""

set -e

echo "[1/6] Arrêt de l'application..."
sudo systemctl stop kb_basedoc
sleep 2

echo "[2/6] Suppression des fichiers .pyc et cache Python..."
find /var/www/kb_basedoc -type f -name '*.pyc' -delete
find /var/www/kb_basedoc -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

echo "[3/6] Vérification du template login.html..."
if ! grep -q "csrf_token()" /var/www/kb_basedoc/app/templates/login.html; then
    echo "  Ajout du token CSRF..."
    sed -i '/<form method="POST" class="login-form">/a\            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>' /var/www/kb_basedoc/app/templates/login.html
fi

echo "[4/6] Démarrage de l'application..."
sudo systemctl start kb_basedoc
sleep 3

echo "[5/6] Vérification du statut..."
sudo systemctl status kb_basedoc --no-pager

echo "[6/6] Redémarrage de Nginx..."
sudo systemctl reload nginx

echo ""
echo "=========================================="
echo "  Redémarrage terminé !"
echo "=========================================="
echo ""
echo "Testez maintenant : https://gagneraud.basedoc.fr"
echo ""
echo "Si le problème persiste, lancez le diagnostic :"
echo "  sudo bash diagnose_login.sh"
echo ""
