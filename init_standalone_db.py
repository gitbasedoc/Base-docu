#!/usr/bin/env python3
"""
Script d'initialisation de la base de données standalone
Crée une base SQLite propre avec les modèles simplifiés
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

# Charger les variables d'environnement standalone
from dotenv import load_dotenv
load_dotenv('.env.standalone')

# Configurer l'environnement
os.environ['FLASK_ENV'] = 'standalone'

# Imports
from app import create_app, db
from app.models_standalone import User, Tag, Procedure, Script, FAQ, Software, Attachment, Setting


def init_database():
    """Initialise la base de données standalone"""

    app = create_app('standalone')

    with app.app_context():
        # Supprimer l'ancienne base si elle existe
        db_path = Path(app.config['DATA_DIR']) / 'kb_basedoc.db'
        if db_path.exists():
            print(f"⚠️  Suppression de l'ancienne base de données...")
            db_path.unlink()

        print("🔨 Création de la nouvelle base de données...")

        # Créer toutes les tables
        db.create_all()

        print("✓ Tables créées avec succès!")

        # Créer l'utilisateur standalone
        print("\n👤 Création de l'utilisateur standalone...")
        user = User(
            email='standalone@local',
            full_name='Utilisateur',
            is_admin=True,
            is_active=True
        )
        user.set_password('standalone')
        db.session.add(user)

        # Créer quelques tags par défaut
        print("🏷️  Création des tags par défaut...")
        default_tags = [
            Tag(name='Windows', color='#0078D4'),
            Tag(name='Linux', color='#FCC624'),
            Tag(name='Réseau', color='#00A4EF'),
            Tag(name='Sécurité', color='#F25022'),
            Tag(name='PowerShell', color='#012456'),
            Tag(name='Active Directory', color='#7FBA00'),
            Tag(name='Office 365', color='#D83B01'),
        ]

        for tag in default_tags:
            db.session.add(tag)

        # Créer des paramètres par défaut
        print("⚙️  Création des paramètres par défaut...")
        settings = [
            Setting(key='app_name', value='KB Support Basedoc', description='Nom de l\'application'),
            Setting(key='company_name', value='Support IT', description='Nom de l\'entreprise'),
            Setting(key='version', value='2.0.0-standalone', description='Version de l\'application'),
        ]

        for setting in settings:
            db.session.add(setting)

        # Créer une procédure d'exemple
        print("📄 Création d'une procédure d'exemple...")
        example_procedure = Procedure(
            title='Bienvenue dans KB Support Basedoc !',
            description='Guide de démarrage rapide',
            content='''<h2>🎉 Bienvenue !</h2>

<p>Cette application vous permet de gérer votre base de connaissances IT personnelle.</p>

<h3>Fonctionnalités disponibles :</h3>

<ul>
    <li><strong>Procédures</strong> : Documentez vos procédures IT</li>
    <li><strong>Scripts</strong> : Bibliothèque de scripts PowerShell/Bash/Python avec coloration syntaxique</li>
    <li><strong>FAQ</strong> : Questions/Réponses fréquentes</li>
    <li><strong>Logiciels</strong> : Catalogue de vos logiciels avec licences</li>
    <li><strong>Recherche</strong> : Recherche globale dans tous vos contenus</li>
</ul>

<h3>Pour commencer :</h3>

<ol>
    <li>Créez votre première procédure</li>
    <li>Ajoutez des scripts utiles</li>
    <li>Organisez avec des tags</li>
    <li>Utilisez la recherche pour retrouver rapidement vos informations</li>
</ol>

<p><em>Vous pouvez supprimer cette procédure d'exemple à tout moment.</em></p>''',
            is_published=True,
            created_by=user.id
        )
        db.session.add(example_procedure)

        # Ajouter des tags à la procédure
        example_procedure.tags.append(default_tags[0])  # Windows

        # Créer un script d'exemple
        print("💻 Création d'un script d'exemple...")
        example_script = Script(
            title='Test de connectivité réseau',
            description='Script PowerShell pour tester la connectivité réseau',
            content='''# Script de test de connectivité réseau
# Auteur: KB Support Basedoc
# Version: 1.0

param(
    [Parameter(Mandatory=$true)]
    [string]$Target,

    [Parameter(Mandatory=$false)]
    [int]$Count = 4
)

Write-Host "Test de connectivité vers $Target..." -ForegroundColor Cyan

# Test Ping
Write-Host "`nTest Ping..." -ForegroundColor Yellow
Test-Connection -ComputerName $Target -Count $Count

# Test DNS
Write-Host "`nRésolution DNS..." -ForegroundColor Yellow
Resolve-DnsName $Target

Write-Host "`nTest terminé!" -ForegroundColor Green''',
            language='powershell',
            status='published',
            is_verified=True,
            author_id=user.id
        )
        db.session.add(example_script)
        example_script.tags.append(default_tags[2])  # Réseau
        example_script.tags.append(default_tags[4])  # PowerShell

        # Créer une FAQ d'exemple
        print("❓ Création d'une FAQ d'exemple...")
        example_faq = FAQ(
            question='Comment utiliser la recherche ?',
            answer='''<p>La barre de recherche en haut de la page vous permet de rechercher dans tous vos contenus :</p>

<ul>
    <li>Procédures</li>
    <li>Scripts</li>
    <li>FAQ</li>
    <li>Logiciels</li>
</ul>

<p>Il suffit de taper votre recherche et d'appuyer sur Entrée. Les résultats sont classés par pertinence.</p>

<p><strong>Astuce :</strong> Utilisez des mots-clés précis pour des résultats plus pertinents !</p>''',
            is_published=True,
            created_by=user.id
        )
        db.session.add(example_faq)

        # Commit de toutes les données
        print("\n💾 Enregistrement des données...")
        db.session.commit()

        print("\n✅ Base de données initialisée avec succès!")
        print(f"\n📂 Base de données : {db_path}")
        print(f"👤 Utilisateur : standalone@local")
        print(f"📊 {len(default_tags)} tags créés")
        print(f"📄 1 procédure d'exemple")
        print(f"💻 1 script d'exemple")
        print(f"❓ 1 FAQ d'exemple")

        print("\n🚀 Vous pouvez maintenant lancer l'application avec:")
        print("   python standalone.py\n")


if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"\n❌ Erreur : {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
