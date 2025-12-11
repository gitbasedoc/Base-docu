# 🚀 Quick Start - KB Support Basedoc

Guide rapide pour démarrer l'application en 5 minutes.

## 📋 Prérequis

- [ ] Python 3.12+
- [ ] PostgreSQL 16+
- [ ] Git

## ⚡ Installation locale (développement)

```bash
# 1. Cloner le projet
git clone <votre-repo>
cd Base-docu

# 2. Créer virtual environment
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Installer dépendances
pip install -r requirements.txt

# 4. Créer base de données PostgreSQL
sudo -u postgres psql
CREATE DATABASE kb_basedoc;
CREATE USER kb_user WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE kb_basedoc TO kb_user;
\c kb_basedoc
GRANT ALL ON SCHEMA public TO kb_user;
\q

# 5. Configurer .env
cp .env.example .env
nano .env

# Éditer .env avec :
DATABASE_URL=postgresql://kb_user:dev_password@localhost/kb_basedoc
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
FLASK_ENV=development
CLAUDE_API_KEY=sk-ant-VOTRE_CLE_ICI

# 6. Initialiser la base de données
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
flask init-db

# 7. Créer un administrateur
flask create-admin
# Email: admin@example.com
# Nom: Admin
# Password: ******

# 8. Lancer l'application
flask run --debug

# 9. Accéder à l'application
# http://localhost:5000
```

## 🌐 Déploiement Production (VPS OVH)

```bash
# 1. Connexion au serveur
ssh root@193.70.41.117

# 2. Télécharger le script d'installation
# (transférer install_kb_basedoc_improved.sh sur le serveur)

# 3. Rendre exécutable
chmod +x install_kb_basedoc_improved.sh

# 4. Lancer l'installation
sudo ./install_kb_basedoc_improved.sh

# Suivre les instructions :
# - Clé API Claude : sk-ant-...
# - Email admin : dheurtebise@basedoc.fr
# - Nom admin : David Heurtebise
# - Mot de passe : ********

# 5. Vérifier l'installation
chmod +x verify_installation.sh
./verify_installation.sh

# 6. Accéder à l'application
# https://gagneraud.basedoc.fr
```

## 🔧 Commandes CLI utiles

```bash
# Base de données
flask init-db              # Initialiser avec catégories de base
flask db migrate -m "msg"  # Créer migration
flask db upgrade           # Appliquer migrations
flask db downgrade         # Annuler dernière migration

# Utilisateurs
flask create-admin         # Créer un administrateur
flask list-users           # Lister tous les utilisateurs

# Shell interactif
flask shell                # Accès aux modèles (User, Procedure, etc.)

# Développement
flask run --debug          # Mode debug
flask run --host=0.0.0.0   # Accessible depuis réseau

# Production
gunicorn --config gunicorn_config.py run:app
```

## 🐛 Résolution de problèmes

### Erreur : ModuleNotFoundError

```bash
pip install -r requirements.txt
```

### Erreur : Base de données

```bash
# Vérifier PostgreSQL
sudo systemctl status postgresql

# Tester connexion
psql -U kb_user -d kb_basedoc -h localhost

# Recréer si besoin
flask db init
flask db migrate
flask db upgrade
```

### Erreur : Permission denied

```bash
# Réparer permissions
sudo chown -R www-data:www-data /var/www/kb_basedoc
sudo chmod -R 755 /var/www/kb_basedoc
```

### Service ne démarre pas

```bash
# Voir les logs
sudo journalctl -u kb_basedoc -f
tail -f /var/log/gunicorn/error.log
```

## 📝 Premiers pas dans l'application

1. **Login** avec admin créé
2. **Créer catégories** (automatique avec `flask init-db`)
3. **Créer première procédure** :
   - Titre: "Test VPN"
   - Catégorie: Réseau
   - Contenu: Description du VPN...
   - Tags: Générer avec IA ou manuel
4. **Tester recherche**
5. **Tester upload fichier**

## 🎯 Prochaines étapes

Après installation réussie :

1. [ ] Créer 10 procédures de test
2. [ ] Tester toutes les fonctionnalités
3. [ ] Ajouter utilisateurs de l'équipe
4. [ ] Configurer backup automatique
5. [ ] Former l'équipe IT

## 📚 Documentation complète

- **README.md** - Vue d'ensemble
- **INSTALLATION.md** - Installation détaillée
- **SUMMARY.md** - Résumé du projet

## ✅ Checklist rapide

- [ ] PostgreSQL installé et configuré
- [ ] Python 3.12+ installé
- [ ] Virtual environment créé
- [ ] Dépendances installées
- [ ] Base de données créée
- [ ] .env configuré
- [ ] Migrations appliquées
- [ ] Catégories initialisées
- [ ] Admin créé
- [ ] Application démarre
- [ ] Login fonctionne

Bon démarrage ! 🚀
