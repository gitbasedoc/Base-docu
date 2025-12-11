# 📚 KB Support Basedoc

Base de connaissances IT pour le service support de Gagneraud.

## 🎯 Description

Application web Flask de gestion de procédures IT avec :
- ✅ CRUD complet des procédures
- ✅ Système de catégorisation hiérarchique
- ✅ Tags automatiques via IA Claude
- ✅ Recherche full-text
- ✅ Upload de fichiers (PDF, scripts, images, vidéos)
- ✅ Versioning automatique
- ✅ Authentification sécurisée
- ✅ Dark theme technique/terminal

## 🚀 Installation rapide

### Prérequis

- Python 3.12+
- PostgreSQL 16+
- Ubuntu 24.04 LTS (recommandé)

### Installation automatique (VPS)

```bash
# Télécharger le script
chmod +x install_kb_basedoc_improved.sh

# Exécuter l'installation
sudo ./install_kb_basedoc_improved.sh
```

Consultez [INSTALLATION.md](INSTALLATION.md) pour les détails complets.

### Installation manuelle (développement)

```bash
# 1. Cloner le projet
git clone https://github.com/votre-org/kb-basedoc.git
cd kb-basedoc

# 2. Créer virtual environment
python3.12 -m venv venv
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
nano .env  # Éditer avec vos valeurs

# 5. Créer la base de données PostgreSQL
sudo -u postgres psql
CREATE DATABASE kb_basedoc;
CREATE USER kb_user WITH PASSWORD 'votre_password';
GRANT ALL PRIVILEGES ON DATABASE kb_basedoc TO kb_user;
\q

# 6. Initialiser les migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 7. Initialiser les données de base
flask init-db

# 8. Créer un administrateur
flask create-admin

# 9. Lancer l'application
flask run
# Ou pour production:
# gunicorn --config gunicorn_config.py run:app
```

## 📂 Structure du projet

```
kb-basedoc/
├── app/
│   ├── __init__.py           # Application factory
│   ├── models.py             # Modèles SQLAlchemy
│   ├── routes/               # Routes Flask
│   │   ├── auth.py           # Authentification
│   │   ├── procedures.py     # CRUD procédures
│   │   ├── search.py         # Recherche
│   │   └── api_ai.py         # API IA
│   ├── services/             # Services métier
│   │   ├── ai_service.py     # Service IA Claude
│   │   └── file_service.py   # Gestion fichiers
│   ├── templates/            # Templates Jinja2
│   └── static/               # Assets statiques
│       ├── css/
│       ├── js/
│       └── fonts/
├── migrations/               # Migrations Alembic
├── storage/                  # Fichiers uploadés
├── config.py                 # Configuration
├── run.py                    # Point d'entrée
├── requirements.txt          # Dépendances Python
├── gunicorn_config.py        # Configuration Gunicorn
└── .env                      # Variables d'environnement (non versionné)
```

## 🔧 Configuration

### Variables d'environnement (.env)

```bash
# Database
DATABASE_URL=postgresql://kb_user:password@localhost/kb_basedoc

# Flask
SECRET_KEY=votre_secret_key_aleatoire
FLASK_APP=run.py
FLASK_ENV=production  # ou development

# Claude AI
CLAUDE_API_KEY=sk-ant-votre_cle_api

# Application
APP_NAME=KB Support Basedoc
UPLOAD_FOLDER=/var/www/kb_basedoc/storage
```

Voir `.env.example` pour tous les paramètres disponibles.

## 🎨 Design System

### Palette de couleurs

```
Backgrounds:  #1f2937, #111827, #374151, #4b5563
Text:         #f9fafb, #9ca3af, #6b7280
Accents:
  - Cyan:     #06b6d4 (primaire)
  - Orange:   #f97316 (nouveau)
  - Green:    #10b981 (succès)
  - Yellow:   #fbbf24 (warning)
  - Red:      #ef4444 (danger)
  - Purple:   #8b5cf6 (info)
```

### Typographie

- Principale: `Fira Code`, `JetBrains Mono`, `Consolas` (monospace)
- Secondaire: `Inter`, `Segoe UI` (sans-serif)

## 🤖 Fonctionnalités IA

L'application utilise l'API Claude d'Anthropic pour :

### 1. Génération automatique de tags
```python
from app.services.ai_service import get_ai_service

ai = get_ai_service()
tags = ai.generate_tags(title="Mon titre", content="Mon contenu")
# Retourne: ['tag1', 'tag2', 'tag3', ...]
```

### 2. Reformulation de contenu
```python
reformulated = ai.reformulate_content(title="...", content="...")
```

### 3. Mise en page assistée
```python
layout = ai.layout_content(title="...", content="...", options={
    'use_emojis': True,
    'structure_sections': True,
    'number_steps': True
})
```

### 4. Recherche sémantique
```python
results = ai.semantic_search(query="Comment configurer VPN?", procedures=[...])
```

## 📡 API

### Endpoints IA

```bash
# Générer des tags
POST /api/ai/generate-tags
{
  "title": "Configuration VPN",
  "content": "Procédure complète...",
  "min_tags": 4,
  "max_tags": 8
}

# Reformuler
POST /api/ai/reformulate
{
  "title": "...",
  "content": "..."
}

# Mise en page
POST /api/ai/layout
{
  "title": "...",
  "content": "...",
  "options": {...}
}

# Recherche sémantique
POST /api/ai/semantic-search
{
  "query": "VPN problème connexion",
  "procedures": [...],
  "top_k": 10
}
```

### Endpoints recherche

```bash
# Recherche simple
GET /search?q=vpn

# Suggestions auto-complétion
GET /api/search/suggestions?q=vpn

# Rechercher tags
GET /api/search/tags?q=office
```

## 🛠️ Commandes CLI

```bash
# Initialiser la base de données
flask init-db

# Créer un administrateur
flask create-admin

# Lister les utilisateurs
flask list-users

# Shell interactif
flask shell

# Migrations
flask db migrate -m "Description"
flask db upgrade
flask db downgrade
```

## 🔐 Sécurité

- ✅ Hash bcrypt pour mots de passe
- ✅ Protection CSRF (Flask-WTF)
- ✅ Sessions sécurisées (HTTPOnly, Secure, SameSite)
- ✅ Validation MIME type (anti-spoofing)
- ✅ Sanitization markdown (Bleach)
- ✅ Rate limiting (Flask-Limiter)
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Path traversal protection (secure_filename)

## 📊 Performance

- ✅ Index PostgreSQL (full-text search, catégories)
- ✅ Pagination (20 items/page)
- ✅ Caching (Flask-Caching)
- ✅ Optimisation images automatique
- ✅ Connection pooling PostgreSQL

## 🧪 Tests

```bash
# Installer dépendances de test
pip install pytest pytest-cov

# Lancer les tests
pytest

# Avec coverage
pytest --cov=app tests/
```

## 📝 Développement

### Workflow

1. Créer une branche feature
```bash
git checkout -b feature/ma-fonctionnalite
```

2. Développer et tester
```bash
# Lancer en mode dev
export FLASK_ENV=development
flask run --debug
```

3. Créer une migration si modèle modifié
```bash
flask db migrate -m "Description des changements"
flask db upgrade
```

4. Commit et push
```bash
git add .
git commit -m "feat: Description"
git push origin feature/ma-fonctionnalite
```

### Conventions

- Code style: PEP 8
- Commits: Conventional Commits
- Branches: feature/, bugfix/, hotfix/

## 🚀 Déploiement

### Production (VPS OVH)

1. Utiliser le script d'installation automatique
```bash
sudo ./install_kb_basedoc_improved.sh
```

2. Vérifier l'installation
```bash
./verify_installation.sh
```

3. Accéder à l'application
```
https://gagneraud.basedoc.fr
```

### Mise à jour

```bash
# 1. Se connecter au serveur
ssh root@193.70.41.117

# 2. Aller dans le répertoire
cd /var/www/kb_basedoc

# 3. Pull les dernières modifications
git pull origin main

# 4. Activer le venv
source venv/bin/activate

# 5. Installer les dépendances
pip install -r requirements.txt

# 6. Migrations si nécessaire
flask db upgrade

# 7. Redémarrer le service
sudo systemctl restart kb_basedoc
```

## 📖 Documentation complète

- [INSTALLATION.md](INSTALLATION.md) - Guide d'installation complet
- [Cahier des charges](cahier_des_charges.md) - Spécifications détaillées
- `/docs` - Documentation API et développeurs (à venir)

## 🆘 Dépannage

### Problème de connexion DB

```bash
# Vérifier que PostgreSQL est actif
sudo systemctl status postgresql

# Tester la connexion
psql -U kb_user -d kb_basedoc -h localhost
```

### Service ne démarre pas

```bash
# Voir les logs
sudo journalctl -u kb_basedoc -f

# Tester manuellement
cd /var/www/kb_basedoc
source venv/bin/activate
gunicorn --config gunicorn_config.py run:app
```

### Erreur 500

```bash
# Logs application
tail -f /var/log/kb_basedoc/app.log

# Logs Gunicorn
tail -f /var/log/gunicorn/error.log

# Logs Nginx
tail -f /var/log/nginx/kb_basedoc_error.log
```

## 📧 Support

- Email: dheurtebise@basedoc.fr
- Documentation: https://gagneraud.basedoc.fr/docs

## 📄 Licence

© 2024 Gagneraud - Support IT
Usage interne uniquement

## 👥 Auteurs

- David Heurtebise - Admin & Lead Developer
- Équipe Support IT Gagneraud

## 🙏 Remerciements

- Anthropic pour l'API Claude
- Flask et l'écosystème Python
- La communauté open-source
