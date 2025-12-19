# Installation de KB Support Basedoc en mode Standalone

Ce guide vous permet d'installer et d'utiliser KB Support Basedoc comme application autonome sur votre PC Windows.

## Prérequis

### 1. Python 3.10 ou supérieur

Téléchargez et installez Python depuis [python.org](https://www.python.org/downloads/)

**Important :** Cochez "Add Python to PATH" lors de l'installation

Vérifiez l'installation :
```bash
python --version
```

### 2. Git (pour cloner le projet)

Téléchargez et installez Git depuis [git-scm.com](https://git-scm.com/)

Vérifiez l'installation :
```bash
git --version
```

## Installation du projet

### 1. Cloner le repository

```bash
# Créer un dossier pour vos projets (par exemple)
mkdir C:\Projects
cd C:\Projects

# Cloner le projet
git clone <URL_DU_REPO> Base-docu
cd Base-docu
```

### 2. Créer un environnement virtuel Python

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows
venv\Scripts\activate

# Vous devriez voir (venv) apparaître dans votre terminal
```

### 3. Installer les dépendances

```bash
# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt

# Installer PyInstaller pour générer le .exe
pip install pyinstaller
```

## Configuration de l'application

### 1. Créer le fichier de configuration locale

Le fichier `.env.standalone` est déjà créé et configuré pour vous.

### 2. Initialiser la base de données

```bash
# L'environnement virtuel doit être activé
python standalone.py init-db
```

Cette commande va :
- Créer la base de données SQLite locale dans `data/kb_basedoc.db`
- Créer les tables nécessaires
- Créer le dossier `data/uploads` pour les fichiers

## Lancement de l'application

### Mode développement (avec console)

```bash
# Activer l'environnement virtuel si ce n'est pas déjà fait
venv\Scripts\activate

# Lancer l'application
python standalone.py
```

L'application sera accessible à : **http://localhost:5050**

Pour arrêter : `Ctrl+C`

### Générer le fichier .exe

Pour créer une version exécutable qui ne nécessite pas Python :

```bash
# Activer l'environnement virtuel
venv\Scripts\activate

# Générer le .exe
pyinstaller standalone.spec

# Le .exe sera généré dans : dist\KBBasedoc\KBBasedoc.exe
```

**Utilisation du .exe :**
1. Copiez tout le dossier `dist\KBBasedoc` où vous voulez
2. Double-cliquez sur `KBBasedoc.exe`
3. L'application s'ouvre dans votre navigateur par défaut

**Important :** Le dossier `data` contenant votre base de données doit être au même niveau que le .exe

## Structure des dossiers

```
Base-docu/
├── app/                    # Code de l'application
├── data/                   # Données de l'application (créé automatiquement)
│   ├── kb_basedoc.db      # Base de données SQLite
│   ├── uploads/           # Fichiers uploadés
│   └── logs/              # Logs de l'application
├── dist/                   # Fichier .exe généré (après packaging)
├── venv/                   # Environnement virtuel Python
├── standalone.py           # Script de lancement standalone
├── standalone.spec         # Configuration PyInstaller
└── requirements.txt        # Dépendances Python
```

## Utilisation quotidienne

### Option 1 : Mode développement
1. Ouvrir un terminal dans le dossier `Base-docu`
2. Activer l'environnement : `venv\Scripts\activate`
3. Lancer : `python standalone.py`
4. Ouvrir le navigateur : http://localhost:5050

### Option 2 : Fichier .exe
1. Double-cliquer sur `dist\KBBasedoc\KBBasedoc.exe`
2. L'application s'ouvre automatiquement dans le navigateur

## Mise à jour de l'application

```bash
# Dans le dossier Base-docu
git pull origin claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8

# Mettre à jour les dépendances
pip install -r requirements.txt

# Régénérer le .exe si besoin
pyinstaller standalone.spec
```

## Sauvegarde de vos données

**Important :** Vos données sont stockées dans `data/kb_basedoc.db`

Pour sauvegarder :
1. Copiez le fichier `data/kb_basedoc.db`
2. Copiez le dossier `data/uploads/`

Pour restaurer :
1. Remplacez `data/kb_basedoc.db` par votre sauvegarde
2. Remplacez `data/uploads/` par votre sauvegarde

## Dépannage

### L'application ne démarre pas
- Vérifiez que Python est bien installé : `python --version`
- Vérifiez que l'environnement virtuel est activé (vous voyez `(venv)`)
- Vérifiez les logs dans `data/logs/app.log`

### Erreur de base de données
```bash
# Réinitialiser la base de données (ATTENTION : efface toutes les données)
python standalone.py init-db --force
```

### Le .exe ne fonctionne pas
- Assurez-vous que le dossier `data` existe au même niveau que le .exe
- Vérifiez l'antivirus (peut bloquer le .exe)
- Lancez le .exe en mode administrateur

## Support

Pour toute question ou problème, consultez les logs dans `data/logs/app.log`
