# 📝 Éditeur Avancé - Guide d'utilisation

## 🎉 Fonctionnalités implémentées

Votre application dispose maintenant d'un **éditeur de texte professionnel** avec toutes les fonctionnalités demandées dans le cahier des charges.

---

## ✨ Fonctionnalités principales

### 1. 📄 Import de documents PDF/Word

**Importez vos procédures existantes en un clic !**

- **Formats supportés** : PDF, DOC, DOCX
- **Conservation de la mise en forme** : titres, paragraphes, tableaux
- **Extraction automatique** : le contenu est converti en HTML

#### Comment utiliser :

1. Dans le formulaire de création/édition de procédure
2. Cliquez sur **[Importer PDF/Word]**
3. Sélectionnez votre fichier
4. Le contenu est automatiquement inséré dans l'éditeur
5. Modifiez si nécessaire et enregistrez

### 2. 🖼️ Upload d'images par Drag & Drop

**Ajoutez des images directement dans vos procédures !**

#### Méthodes d'ajout d'images :

**Méthode 1 : Drag & Drop**
- Glissez-déposez une image directement dans l'éditeur
- L'image est automatiquement uploadée et insérée

**Méthode 2 : Copier-Coller**
- Copiez une image (Ctrl+C)
- Collez-la dans l'éditeur (Ctrl+V)
- Upload automatique

**Méthode 3 : Bouton Image**
- Cliquez sur l'icône 🖼️ dans la barre d'outils
- Choisissez "Upload" puis sélectionnez votre image

**Formats supportés** : PNG, JPG, JPEG, GIF, WebP, SVG
**Taille maximale** : 10 MB par image

### 3. ✏️ Éditeur WYSIWYG Complet

**TinyMCE 6 intégré avec thème sombre**

#### Barre d'outils complète :

```
┌─────────────────────────────────────────────────────────────┐
│ Undo Redo | Blocks | B I U S | Align | Lists | Colors     │
│ Table | Link | Image | Media | Code | Fullscreen | Help    │
└─────────────────────────────────────────────────────────────┘
```

#### Fonctionnalités disponibles :

- **Mise en forme du texte** :
  - Gras, Italique, Souligné, Barré
  - Titres (H1 à H6)
  - Couleur du texte et fond

- **Alignement** :
  - Gauche, Centre, Droite, Justifié

- **Listes** :
  - Listes à puces
  - Listes numérotées
  - Indentation / Désindentation

- **Tableaux** :
  - Insertion de tableaux
  - Fusion de cellules
  - Formatage des bordures

- **Médias** :
  - Images (upload, URL, drag & drop)
  - Vidéos (embed YouTube, Vimeo)
  - Liens hypertextes

- **Code** :
  - Blocs de code
  - Mode code source HTML

- **Autres** :
  - Rechercher/Remplacer
  - Caractères spéciaux
  - Compteur de mots
  - Mode plein écran
  - Prévisualisation

---

## 🎨 Apparence

L'éditeur utilise un **thème sombre** qui correspond au design de l'application :

- Background : `#1a1a2e`
- Texte : `#e0e0e0`
- Titres : `#00ff88` (vert primaire)
- Code : `#2a2a3e`

---

## 🔧 Architecture technique

### Routes créées :

| Route | Méthode | Description |
|-------|---------|-------------|
| `/files/upload-image` | POST | Upload d'images avec validation |
| `/files/import-document` | POST | Import PDF/Word avec extraction |
| `/uploads/<path>` | GET | Servir les fichiers uploadés |

### Fichiers modifiés/créés :

1. **app/routes/files.py** (nouveau)
   - Gestion upload d'images
   - Extraction PDF via PyMuPDF (fitz)
   - Extraction Word via python-docx
   - Validation formats et tailles

2. **app/templates/procedures/edit.html** (modifié)
   - Intégration TinyMCE 6
   - Configuration upload images
   - Bouton import documents
   - Handlers JavaScript

3. **app/__init__.py** (modifié)
   - Enregistrement blueprint `files_bp`
   - Route `/uploads` pour servir fichiers

### Dépendances utilisées :

- **TinyMCE 6** : Éditeur WYSIWYG (via CDN)
- **PyMuPDF** : Extraction PDF (déjà installé)
- **python-docx** : Extraction Word (déjà installé)

---

## 📦 Déploiement

### Sur le serveur :

```bash
# Connectez-vous au serveur
ssh ubuntu@193.70.41.117

# Allez dans le répertoire
cd /var/www/kb_basedoc

# Récupérez les modifications
git pull origin claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8

# Créez les répertoires pour les uploads
mkdir -p storage/images
mkdir -p storage/temp
chmod 755 storage/images
chmod 755 storage/temp

# Redémarrez l'application
sudo systemctl restart kb_basedoc

# Vérifiez le statut
sudo systemctl status kb_basedoc
```

---

## 🧪 Tester l'éditeur

### Test 1 : Créer une procédure avec l'éditeur

1. Allez sur https://gagneraud.basedoc.fr
2. Cliquez sur **[+ Nouvelle procédure]**
3. Remplissez le titre et la catégorie
4. Dans l'éditeur :
   - Écrivez du texte
   - Formatez-le (gras, couleurs, etc.)
   - Ajoutez une image par drag & drop
   - Créez un tableau
5. Enregistrez

### Test 2 : Importer un PDF

1. Préparez un fichier PDF avec du texte
2. Cliquez sur **[+ Nouvelle procédure]**
3. Cliquez sur **[Importer PDF/Word]**
4. Sélectionnez votre PDF
5. Vérifiez que le contenu apparaît dans l'éditeur
6. Modifiez si nécessaire
7. Enregistrez

### Test 3 : Importer un Word

1. Préparez un fichier Word (.docx) avec :
   - Titres
   - Paragraphes
   - Tableaux
2. Importez-le comme pour le PDF
3. Vérifiez que :
   - Les titres sont en `<h3>`
   - Les tableaux sont conservés
   - La mise en forme est préservée

### Test 4 : Drag & Drop d'images

1. Ouvrez une image sur votre ordinateur
2. Glissez-déposez-la dans l'éditeur TinyMCE
3. L'image devrait :
   - S'uploader automatiquement
   - Apparaître dans l'éditeur
   - Être sauvegardée avec la procédure

---

## 🛡️ Sécurité

### Validations en place :

✅ **Images** :
- Extensions autorisées : png, jpg, jpeg, gif, webp, svg
- Taille max : 10 MB
- Nom de fichier sécurisé (UUID unique)
- Protection CSRF

✅ **Documents** :
- Extensions autorisées : pdf, doc, docx
- Validation du format
- Fichiers temporaires nettoyés après extraction
- Protection CSRF

✅ **Upload** :
- Stockage sécurisé dans `/storage`
- Noms de fichiers uniques (collision impossible)
- Permissions appropriées

---

## 📊 Exemples d'utilisation

### Exemple 1 : Procédure avec images

```
Titre : Réinitialiser un mot de passe Active Directory

Contenu :
┌─────────────────────────────────────┐
│ 1. Ouvrir "Utilisateurs et ordinateurs AD"   │
│ [Image: capture écran menu]         │
│                                     │
│ 2. Rechercher l'utilisateur         │
│ [Image: barre recherche]            │
│                                     │
│ 3. Clic droit > Réinitialiser       │
│ [Image: menu contextuel]            │
└─────────────────────────────────────┘
```

### Exemple 2 : Import d'une procédure existante

```
Vous avez : procedure_backup.pdf
Résultat après import :

Page 1
========
Procédure de sauvegarde mensuelle

1. Vérifier l'espace disque
2. Lancer le script backup.sh
3. Vérifier les logs
...
```

---

## 🎯 Avantages

✅ **Gain de temps** : Importez vos procédures existantes au lieu de les retaper

✅ **Richesse visuelle** : Ajoutez des captures d'écran pour guider vos collègues

✅ **Mise en forme professionnelle** : Tableaux, listes, couleurs

✅ **Facilité d'utilisation** : Interface WYSIWYG intuitive

✅ **Cohérence** : Thème sombre uniforme avec l'application

---

## 🆘 Dépannage

### Problème : L'éditeur ne s'affiche pas

**Solution** :
1. Vérifiez que TinyMCE est chargé : ouvrez la console (F12)
2. Vérifiez la connexion internet (TinyMCE via CDN)
3. Rechargez la page (Ctrl+F5)

### Problème : L'upload d'image échoue

**Solutions** :
1. Vérifiez la taille de l'image (< 10 MB)
2. Vérifiez le format (PNG, JPG, GIF, SVG, WebP)
3. Vérifiez les permissions sur `/storage/images`
4. Vérifiez les logs : `sudo tail -f /var/log/kb_basedoc/app.log`

### Problème : L'import PDF ne fonctionne pas

**Solutions** :
1. Vérifiez que PyMuPDF est installé :
   ```bash
   cd /var/www/kb_basedoc
   source venv/bin/activate
   python -c "import fitz; print('OK')"
   ```
2. Si erreur, réinstallez :
   ```bash
   pip install PyMuPDF
   ```

### Problème : L'import Word ne fonctionne pas

**Solutions** :
1. Vérifiez que python-docx est installé :
   ```bash
   cd /var/www/kb_basedoc
   source venv/bin/activate
   python -c "from docx import Document; print('OK')"
   ```
2. Si erreur, réinstallez :
   ```bash
   pip install python-docx
   ```

---

## 🚀 Prochaines améliorations possibles

Ideas pour le futur :

- [ ] Support des fichiers Excel (tableaux)
- [ ] Export de procédures en PDF
- [ ] Modèles de procédures pré-formatés
- [ ] Galerie d'images uploadées
- [ ] Édition collaborative en temps réel
- [ ] Historique des versions avec diff visuel
- [ ] Import depuis URL (Confluence, SharePoint, etc.)

---

**L'éditeur est maintenant prêt à l'emploi ! 🎉**

Testez-le et faites-moi savoir s'il y a des ajustements à faire.
