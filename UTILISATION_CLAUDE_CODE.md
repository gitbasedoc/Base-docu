# 🚀 Utilisation de Claude Code pour le projet KB Support Basedoc

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir :

- ✅ **Git** installé sur Windows
- ✅ **Claude Code** installé (`npm install -g @anthropic-ai/claude-code`)
- ✅ **PowerShell** (inclus dans Windows)
- ✅ **Accès au repository GitHub** : https://github.com/gitbasedoc/Base-docu

---

## 🎯 Méthode 1 : Script automatique (RECOMMANDÉ)

### Installation du script

1. **Téléchargez le script** `start-claude-code.ps1` depuis le repository

2. **Placez-le** dans un endroit accessible, par exemple :
   ```
   C:\Scripts\start-claude-code.ps1
   ```

3. **Créez un raccourci** sur votre bureau :
   - Clic droit sur le bureau → Nouveau → Raccourci
   - Cible : `powershell.exe -ExecutionPolicy Bypass -File "C:\Scripts\start-claude-code.ps1"`
   - Nom : `Claude Code - KB Basedoc`

### Utilisation

Double-cliquez sur le raccourci ou exécutez :

```powershell
powershell -ExecutionPolicy Bypass -File C:\Scripts\start-claude-code.ps1
```

**Le script va automatiquement :**

1. ✅ Créer `F:\Claude_code\Base-de-connaissances` si nécessaire
2. ✅ Cloner le repository GitHub (première fois)
3. ✅ Basculer sur la bonne branche
4. ✅ Récupérer les dernières modifications
5. ✅ Lancer Claude Code dans le bon répertoire

---

## 🎯 Méthode 2 : Manuelle

### Première fois

```powershell
# Créer le répertoire
New-Item -ItemType Directory -Force -Path "F:\Claude_code\Base-de-connaissances"

# Aller dedans
cd F:\Claude_code\Base-de-connaissances

# Cloner le projet
git clone https://github.com/gitbasedoc/Base-docu.git .

# Basculer sur la bonne branche
git checkout claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8

# Lancer Claude Code
claude
```

### Les fois suivantes

```powershell
# Aller dans le répertoire
cd F:\Claude_code\Base-de-connaissances

# Récupérer les dernières modifications
git pull origin claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8

# Lancer Claude Code
claude
```

---

## 💬 Démarrer une conversation avec Claude Code

Une fois Claude Code lancé, vous pouvez dire :

### 1. Pour le contexte du projet

```
Lis les fichiers DEPLOYMENT_STATUS.md et EDITEUR_AVANCE.md
pour comprendre l'état actuel du projet KB Support Basedoc.
```

### 2. Pour faire des modifications

```
Je veux ajouter une nouvelle fonctionnalité pour [décrire la fonctionnalité].
Commence par analyser le code existant dans app/routes/
```

### 3. Pour corriger un bug

```
Il y a un bug dans l'éditeur TinyMCE : [décrire le bug].
Peux-tu diagnostiquer et corriger ?
```

---

## 🔄 Workflow complet

### 1. Lancer Claude Code

```powershell
# Via le script
.\start-claude-code.ps1

# OU manuellement
cd F:\Claude_code\Base-de-connaissances
git pull
claude
```

### 2. Travailler avec Claude Code

- Décrivez ce que vous voulez faire
- Claude Code modifie les fichiers
- Claude Code commit automatiquement

### 3. Pousser vers GitHub

```powershell
# Claude Code a déjà commit, il suffit de push
git push origin claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8
```

### 4. Déployer sur le serveur

```powershell
# Se connecter au serveur
ssh ubuntu@193.70.41.117

# Sur le serveur
cd /var/www/kb_basedoc
git pull origin claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8
sudo systemctl restart kb_basedoc
```

---

## 📚 Fichiers de documentation importants

Quand vous démarrez une session Claude Code, demandez-lui de lire :

| Fichier | Description |
|---------|-------------|
| `DEPLOYMENT_STATUS.md` | État du déploiement, ce qui fonctionne et ce qui reste à faire |
| `EDITEUR_AVANCE.md` | Documentation de l'éditeur WYSIWYG avec PDF/Word import |
| `DNS_CONFIGURATION.md` | Configuration DNS et SSL |
| `README.md` | Vue d'ensemble du projet |
| `SUMMARY.md` | Résumé complet du projet |

**Exemple de prompt initial :**

```
Salut ! Je travaille sur KB Support Basedoc, une base de connaissances IT en Flask.

Peux-tu lire ces fichiers pour avoir le contexte :
- DEPLOYMENT_STATUS.md
- EDITEUR_AVANCE.md
- README.md

Ensuite, je voudrais que tu m'aides à [décrire votre besoin].
```

---

## 🐛 Dépannage

### Erreur : "claude n'est pas reconnu"

**Solution :**

```powershell
# Installer Claude Code
npm install -g @anthropic-ai/claude-code

# OU utiliser npx
npx @anthropic-ai/claude-code
```

### Erreur : "Impossible d'exécuter des scripts"

**Solution :**

```powershell
# Autoriser l'exécution de scripts (en tant qu'admin)
Set-ExecutionPolicy RemoteSigned

# OU lancer avec bypass
powershell -ExecutionPolicy Bypass -File start-claude-code.ps1
```

### Le script ne trouve pas Git

**Solution :**

```powershell
# Vérifier que Git est installé
git --version

# Si non installé, téléchargez-le :
# https://git-scm.com/download/win
```

### Claude Code ne fait pas confiance au répertoire

**Solution :**

C'est normal la première fois. Répondez **"Yes"** quand il demande :

```
Do you trust the authors of the files in this folder?
```

---

## 🎓 Conseils d'utilisation

### ✅ Bonnes pratiques

1. **Toujours pull avant de commencer** :
   ```powershell
   git pull origin claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8
   ```

2. **Donner du contexte à Claude Code** :
   - Dites-lui de lire la documentation
   - Expliquez ce que vous voulez faire
   - Montrez des exemples si nécessaire

3. **Vérifier les modifications** :
   ```powershell
   git status
   git diff
   ```

4. **Tester avant de déployer** :
   - Vérifiez le code
   - Lisez les commits
   - Testez en local si possible

### ❌ À éviter

- ❌ Ne pas pull avant de commencer
- ❌ Ne pas donner de contexte à Claude Code
- ❌ Pousser sans vérifier les modifications
- ❌ Déployer sans tester

---

## 📞 Besoin d'aide ?

### Sur le projet

- Consultez `DEPLOYMENT_STATUS.md` pour l'état actuel
- Consultez `EDITEUR_AVANCE.md` pour l'éditeur
- Consultez les logs sur le serveur :
  ```bash
  sudo tail -f /var/log/kb_basedoc/app.log
  ```

### Sur Git

```powershell
# Voir l'historique
git log --oneline -10

# Voir les branches
git branch -a

# Annuler les modifications locales
git reset --hard HEAD
git clean -fd
```

### Sur Claude Code

- Documentation : https://github.com/anthropics/claude-code
- Commandes : Tapez `/help` dans Claude Code

---

## 🚀 Exemple de session complète

```powershell
# 1. Lancer le script
.\start-claude-code.ps1

# 2. Dans Claude Code
> Lis DEPLOYMENT_STATUS.md et EDITEUR_AVANCE.md.
> Je voudrais ajouter une fonction d'export PDF des procédures.
> Peux-tu analyser le code existant et proposer une implémentation ?

# 3. Claude Code travaille...
# 4. Vérifier les modifications
git status
git diff

# 5. Pousser vers GitHub
git push origin claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8

# 6. Déployer sur le serveur
ssh ubuntu@193.70.41.117
cd /var/www/kb_basedoc
git pull
sudo systemctl restart kb_basedoc

# 7. Tester
https://gagneraud.basedoc.fr
```

---

**Bon développement avec Claude Code ! 🎉**
