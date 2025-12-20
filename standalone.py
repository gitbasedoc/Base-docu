#!/usr/bin/env python3
"""
Script de lancement standalone pour KB Support Basedoc
Version mono-utilisateur sans authentification
"""

import os
import sys
import webbrowser
import time
import threading
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement standalone
load_dotenv('.env.standalone')

# Configurer l'environnement
os.environ['FLASK_ENV'] = 'standalone'

# Imports Flask
from app import create_app, db
from flask_migrate import upgrade
from app.models import User


def ensure_directories():
    """Créer les répertoires nécessaires"""
    base_dir = Path(__file__).parent
    data_dir = base_dir / 'data'

    # Créer les dossiers
    (data_dir / 'uploads').mkdir(parents=True, exist_ok=True)
    (data_dir / 'logs').mkdir(parents=True, exist_ok=True)

    print("✓ Dossiers créés/vérifiés")


def init_database(force=False):
    """Initialiser la base de données"""
    import subprocess

    if force:
        print("⚠️  Mode force activé - la base sera réinitialisée")

    print("Lancement du script d'initialisation...")
    result = subprocess.run([sys.executable, 'init_standalone_db.py'], capture_output=False)

    if result.returncode != 0:
        print("❌ Erreur lors de l'initialisation")
        sys.exit(1)


def open_browser(port=5050):
    """Ouvrir le navigateur après un court délai"""
    time.sleep(1.5)  # Attendre que le serveur démarre
    url = f'http://localhost:{port}'
    print(f"\n🌐 Ouverture du navigateur : {url}\n")
    webbrowser.open(url)


def run_app():
    """Lancer l'application"""
    # Créer les dossiers nécessaires
    ensure_directories()

    # Créer l'application
    app = create_app('standalone')

    # Vérifier que la base de données existe
    db_path = Path(app.config['DATA_DIR']) / 'kb_basedoc.db'
    if not db_path.exists():
        print("\n⚠️ Base de données non trouvée. Initialisation...")
        init_database()

    # Port
    port = int(os.environ.get('PORT', 5050))

    print("\n" + "="*60)
    print("  KB Support Basedoc - Mode Standalone")
    print("="*60)
    print(f"\n📂 Base de données : {db_path}")
    print(f"📂 Uploads : {app.config['UPLOAD_FOLDER']}")
    print(f"📂 Logs : {app.config['LOG_FILE']}")
    print(f"\n🚀 Serveur démarré sur http://localhost:{port}")
    print("\n💡 Appuyez sur Ctrl+C pour arrêter\n")
    print("="*60 + "\n")

    # Ouvrir le navigateur dans un thread séparé
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # Lancer l'application
    app.run(
        host='127.0.0.1',
        port=port,
        debug=False,
        use_reloader=False  # Évite le double démarrage
    )


def main():
    """Point d'entrée principal"""
    import argparse

    parser = argparse.ArgumentParser(description='KB Support Basedoc - Standalone')
    parser.add_argument('command', nargs='?', default='run',
                        choices=['run', 'init-db'],
                        help='Commande à exécuter (run ou init-db)')
    parser.add_argument('--force', action='store_true',
                        help='Force la réinitialisation de la base de données')

    args = parser.parse_args()

    if args.command == 'init-db':
        ensure_directories()
        init_database(force=args.force)
        print("\n✓ Initialisation terminée!")
        print("\nVous pouvez maintenant lancer l'application avec:")
        print("  python standalone.py\n")
    else:
        run_app()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt de l'application...\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur : {e}\n")
        sys.exit(1)
