# Lancement Rapide de KB Support Basedoc

## 🚀 Pour lancer l'application immédiatement

### Sur Windows :
Double-cliquez sur le fichier : **`lancer_kb_basedoc.bat`**

### Sur Linux/Mac :
```bash
./lancer_kb_basedoc.sh
```

## ✨ Ce que fait le script automatiquement

Le script s'occupe de TOUT pour vous :

1. ✅ Vérifie que Python est installé
2. ✅ Crée l'environnement virtuel (si nécessaire)
3. ✅ Active l'environnement virtuel
4. ✅ Installe les dépendances (si nécessaire)
5. ✅ Initialise la base de données (si nécessaire)
6. ✅ Lance l'application

L'application s'ouvrira automatiquement dans votre navigateur sur : **http://localhost:5050**

## 🛑 Pour arrêter l'application

Appuyez sur `Ctrl+C` dans le terminal

## ⚙️ Options avancées

### Réinitialiser la base de données

**Windows :**
```cmd
venv\Scripts\activate
python standalone.py init-db --force
```

**Linux/Mac :**
```bash
source venv/bin/activate
python standalone.py init-db --force
```

### Créer un exécutable Windows (.exe)

```cmd
venv\Scripts\activate
pip install pyinstaller
pyinstaller standalone.spec
```

L'exécutable sera dans : `dist\KBBasedoc\KBBasedoc.exe`

## 📂 Fichiers importants

- **lancer_kb_basedoc.bat** - Script de lancement Windows
- **lancer_kb_basedoc.sh** - Script de lancement Linux/Mac
- **data/kb_basedoc.db** - Votre base de données (à sauvegarder !)
- **data/uploads/** - Vos fichiers téléchargés (à sauvegarder !)

## 🔧 Dépannage

### "Python n'est pas reconnu"
- Installez Python depuis : https://www.python.org/downloads/
- Cochez **"Add Python to PATH"** lors de l'installation

### "Permission denied" sur Linux
```bash
chmod +x lancer_kb_basedoc.sh
```

### L'application ne démarre pas
Regardez les logs dans : `data/logs/app.log`

## 📞 Besoin d'aide ?

Consultez la documentation complète : **INSTALLATION_STANDALONE.md**
