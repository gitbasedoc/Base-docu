#!/bin/bash
# Script pour trouver l'emplacement de l'application KB Basedoc

echo "🔍 Recherche de l'application KB Basedoc..."
echo ""

# Méthode 1: Chercher via le processus gunicorn
echo "1. Recherche via processus gunicorn..."
GUNICORN_PID=$(pgrep -f "gunicorn.*run:app" | head -1)
if [ -n "$GUNICORN_PID" ]; then
    GUNICORN_CWD=$(pwdx "$GUNICORN_PID" 2>/dev/null | awk '{print $2}')
    if [ -n "$GUNICORN_CWD" ]; then
        echo "   ✓ Trouvé via gunicorn: $GUNICORN_CWD"
    fi
fi

# Méthode 2: Chercher le fichier run.py
echo ""
echo "2. Recherche du fichier run.py..."
RUNPY_LOCATIONS=$(find /home /opt -name "run.py" -type f 2>/dev/null | grep -E "(basedoc|kb-)" | head -3)
if [ -n "$RUNPY_LOCATIONS" ]; then
    echo "$RUNPY_LOCATIONS" | while read location; do
        echo "   ✓ Trouvé: $(dirname "$location")"
    done
fi

# Méthode 3: Chercher via le service systemd
echo ""
echo "3. Recherche via service systemd..."
SERVICES=$(systemctl list-units --type=service --all | grep -E "(basedoc|kb-)" | awk '{print $1}')
if [ -n "$SERVICES" ]; then
    echo "$SERVICES" | while read service; do
        echo "   Service: $service"
        systemctl cat "$service" 2>/dev/null | grep -E "WorkingDirectory|ExecStart" | head -2
    done
fi

# Méthode 4: Chercher le répertoire app
echo ""
echo "4. Recherche du répertoire app/..."
APP_DIRS=$(find /home /opt -type d -name "app" 2>/dev/null | while read dir; do
    if [ -f "$dir/models.py" ] && [ -f "$dir/routes/procedures.py" ] 2>/dev/null; then
        echo "$(dirname "$dir")"
    fi
done | head -3)
if [ -n "$APP_DIRS" ]; then
    echo "$APP_DIRS" | while read location; do
        echo "   ✓ Trouvé: $location"
    done
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
