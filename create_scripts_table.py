"""
Script pour créer la migration de la table scripts
"""

import os
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from flask_migrate import Migrate, init, migrate, upgrade

def create_migration():
    """Crée et applique la migration pour la table scripts"""

    app = create_app()

    with app.app_context():
        # Créer le répertoire migrations s'il n'existe pas
        if not os.path.exists('migrations'):
            print("📁 Initialisation de Flask-Migrate...")
            os.system('flask db init')

        # Créer la migration
        print("🔧 Création de la migration pour la table scripts...")
        os.system('flask db migrate -m "Add scripts table for collaborative script sharing"')

        print("✅ Migration créée avec succès!")
        print("\nPour appliquer la migration sur le serveur:")
        print("1. cd /var/www/kb_basedoc")
        print("2. source venv/bin/activate")
        print("3. flask db upgrade")

if __name__ == '__main__':
    create_migration()
