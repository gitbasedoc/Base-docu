#!/usr/bin/env python3
"""
Point d'entrée pour KB Support Basedoc
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

from app import create_app, db
from app.models import User, Category, Procedure, Tag, Attachment, ProcedureVersion, Setting

# Créer l'application
app = create_app()


@app.shell_context_processor
def make_shell_context():
    """
    Context processor pour le shell Flask
    Permet d'avoir accès aux modèles directement dans le shell
    """
    return {
        'db': db,
        'User': User,
        'Category': Category,
        'Procedure': Procedure,
        'Tag': Tag,
        'Attachment': Attachment,
        'ProcedureVersion': ProcedureVersion,
        'Setting': Setting
    }


@app.cli.command()
def init_db():
    """
    Initialise la base de données avec les données de base
    Usage: flask init-db
    """
    print("Initialisation de la base de données...")

    # Créer les catégories principales
    categories_data = [
        ('Office 365', 'o365', None, 0, '#06b6d4'),
        ('Matériel', 'hard', None, 1, '#f97316'),
        ('Réseau', 'net', None, 2, '#10b981'),
        ('Comptes et accès', 'acct', None, 3, '#fbbf24'),
        ('Logiciels', 'soft', None, 4, '#8b5cf6'),
        ('Système', 'sys', None, 5, '#ef4444'),
    ]

    for name, short_name, parent_id, display_order, color_code in categories_data:
        category = Category.query.filter_by(short_name=short_name).first()
        if not category:
            category = Category(
                name=name,
                short_name=short_name,
                parent_id=parent_id,
                display_order=display_order,
                color_code=color_code
            )
            db.session.add(category)
            print(f"✓ Catégorie créée: {name}")
        else:
            print(f"- Catégorie existe: {name}")

    # Créer sous-catégories Office 365
    o365 = Category.query.filter_by(short_name='o365').first()
    if o365:
        subcategories_o365 = [
            ('Outlook', 'out', o365.id, 0),
            ('Teams', 'team', o365.id, 1),
            ('OneDrive', 'one', o365.id, 2),
            ('SharePoint', 'share', o365.id, 3),
            ('Exchange', 'exch', o365.id, 4),
        ]

        for name, short_name, parent_id, display_order in subcategories_o365:
            category = Category.query.filter_by(short_name=short_name).first()
            if not category:
                category = Category(
                    name=name,
                    short_name=short_name,
                    parent_id=parent_id,
                    display_order=display_order,
                    color_code=o365.color_code
                )
                db.session.add(category)
                print(f"✓ Sous-catégorie créée: {name}")

    db.session.commit()
    print("\n✓ Initialisation terminée")


@app.cli.command()
def create_admin():
    """
    Crée un utilisateur administrateur
    Usage: flask create-admin
    """
    import getpass

    print("Création d'un administrateur\n")

    email = input("Email: ").strip()
    if not email:
        print("✗ Email requis")
        return

    # Vérifier si l'utilisateur existe
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        print(f"✗ L'utilisateur {email} existe déjà")
        return

    full_name = input("Nom complet: ").strip()
    if not full_name:
        print("✗ Nom complet requis")
        return

    password = getpass.getpass("Mot de passe: ")
    password_confirm = getpass.getpass("Confirmer le mot de passe: ")

    if password != password_confirm:
        print("✗ Les mots de passe ne correspondent pas")
        return

    if len(password) < 8:
        print("✗ Le mot de passe doit contenir au moins 8 caractères")
        return

    # Créer l'administrateur
    admin = User(
        email=email,
        full_name=full_name,
        is_admin=True,
        is_active=True
    )
    admin.set_password(password)

    db.session.add(admin)
    db.session.commit()

    print(f"\n✓ Administrateur créé: {email}")


@app.cli.command()
def list_users():
    """
    Liste tous les utilisateurs
    Usage: flask list-users
    """
    users = User.query.order_by(User.created_at.desc()).all()

    print(f"\nUtilisateurs ({len(users)}):")
    print("-" * 80)

    for user in users:
        admin_badge = "[ADMIN]" if user.is_admin else ""
        active_badge = "" if user.is_active else "[INACTIF]"

        print(f"{user.id:3d} | {user.email:40s} | {user.full_name:30s} {admin_badge} {active_badge}")

    print("-" * 80)


if __name__ == '__main__':
    # Vérifier les variables d'environnement critiques
    required_env_vars = ['SECRET_KEY', 'DATABASE_URL']
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"✗ Variables d'environnement manquantes: {', '.join(missing_vars)}")
        print("  Assurez-vous que le fichier .env est présent et correctement configuré")
        exit(1)

    # Lancer l'application
    app.run(host='0.0.0.0', port=8000, debug=False)
