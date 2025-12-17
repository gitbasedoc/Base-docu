# ❓ Fonctionnalité FAQ (Questions Fréquemment Posées)

## 🎯 Vue d'ensemble

La section FAQ permet de créer, gérer et consulter des questions fréquemment posées avec le même éditeur WYSIWYG avancé (TinyMCE) que les procédures. Les utilisateurs peuvent facilement trouver des réponses aux questions courantes et voter pour les réponses utiles.

## ✨ Fonctionnalités

### 1. Gestion Complète des FAQ

#### Créer une FAQ
- **Question** : Titre clair de la question
- **Réponse** : Contenu formaté avec l'éditeur TinyMCE
- **Catégorie** : Organisation par catégories existantes
- **Statut** : Publié ou Brouillon

#### Modifier une FAQ
- ✅ Permissions : Auteur ou Admin uniquement
- ✅ Même éditeur avancé que pour la création
- ✅ Modification du statut de publication

#### Supprimer une FAQ
- ✅ Permissions : Auteur ou Admin uniquement
- ✅ Confirmation avant suppression
- ✅ Suppression complète de la base de données

### 2. Éditeur Avancé TinyMCE

L'éditeur est identique à celui des procédures :

#### Fonctionnalités de l'Éditeur
- ✅ **Formatage riche** : Gras, italique, couleurs, alignement
- ✅ **Listes** : Puces et numérotées
- ✅ **Tableaux** : Création et édition de tableaux
- ✅ **Images** : Upload par drag & drop, copier-coller, ou bouton
- ✅ **Liens** : Insertion de liens hypertextes
- ✅ **Code** : Blocs de code avec formatage
- ✅ **Médias** : Insertion de vidéos et médias
- ✅ **Plein écran** : Mode plein écran pour la rédaction

#### Import de Documents
- ✅ **PDF** : Extraction et conversion du contenu
- ✅ **Word** : Import de fichiers .doc et .docx
- ✅ **Conservation** : Préservation de la structure et du formatage
- ✅ **Images** : Extraction des images intégrées

### 3. Système de Navigation et Filtrage

#### Page Liste
- ✅ **Affichage par cartes** : Design moderne avec aperçu
- ✅ **Filtre par catégorie** : Sélection rapide par catégorie
- ✅ **Affichage brouillons** : Option pour admins de voir les brouillons
- ✅ **Pagination** : 20 FAQ par page
- ✅ **Statistiques** : Nombre de vues et votes "utile"

#### Badges et Indicateurs
- 🏷️ **Badge catégorie** : Avec code couleur personnalisé
- 📝 **Badge brouillon** : Visible uniquement pour auteur/admin
- 👁️ **Compteur de vues** : Nombre de consultations
- 👍 **Compteur "utile"** : Nombre de votes positifs

### 4. Page Détail FAQ

#### Affichage de la Réponse
- ✅ **Formatage complet** : Rendu HTML de la réponse
- ✅ **Métadonnées** : Auteur, dates de création/modification, vues
- ✅ **Catégorie** : Affichage avec code couleur
- ✅ **Navigation** : Breadcrumb et retour à la liste

#### Bouton "C'était utile ?"
- ✅ **Vote AJAX** : Sans rechargement de page
- ✅ **Compteur dynamique** : Mise à jour en temps réel
- ✅ **Protection** : Un seul vote par session
- ✅ **Animation** : Feedback visuel lors du clic

#### Actions Admin
- ✅ **Modifier** : Lien vers l'éditeur
- ✅ **Supprimer** : Avec confirmation
- ✅ **Visible uniquement** : Pour auteur ou admin

### 5. Accès Public

Contrairement aux scripts qui nécessitent une connexion, les FAQ peuvent être consultées :

- ✅ **FAQ publiées** : Accessibles à tous (authentifiés ou non)
- ✅ **FAQ brouillons** : Visibles uniquement par auteur et admin
- ✅ **Compteur de vues** : Incrémenté à chaque consultation
- ✅ **Vote "utile"** : Disponible même sans connexion

---

## 🗂️ Structure de Données

### Modèle FAQ

```python
class FAQ(db.Model):
    id = Integer (PK)
    question = String(500) - La question
    answer = Text - La réponse (HTML formaté)
    category_id = Integer (FK vers Category)
    created_by = Integer (FK vers User)
    created_at = DateTime
    updated_at = DateTime
    is_published = Boolean - Publié ou brouillon
    view_count = Integer - Nombre de vues
    helpful_count = Integer - Nombre de votes "utile"
```

### Relations

- **FAQ.category** → Category : Catégorie de la FAQ
- **FAQ.author** → User : Auteur de la FAQ
- **User.faqs** → List[FAQ] : FAQs créées par l'utilisateur
- **Category.faqs** → List[FAQ] : FAQs de cette catégorie

---

## 🛣️ Routes

| Route | Méthode | Description | Auth |
|-------|---------|-------------|------|
| `/faq` | GET | Liste des FAQs | Non* |
| `/faq/<id>` | GET | Détail d'une FAQ | Non* |
| `/faq/new` | GET, POST | Créer une FAQ | Oui |
| `/faq/<id>/edit` | GET, POST | Modifier une FAQ | Oui** |
| `/faq/<id>/delete` | POST | Supprimer une FAQ | Oui** |
| `/faq/<id>/helpful` | POST | Marquer comme utile | Non |

\* **Non requis** pour les FAQ publiées, requis pour les brouillons
\*\* **Auteur ou Admin** uniquement

---

## 🎨 Templates

### 1. `faq/list.html`

Liste des FAQ avec :
- Cartes FAQ avec aperçu de la réponse
- Badges catégorie colorés
- Filtres (catégorie, afficher brouillons)
- Statistiques (vues, votes)
- Boutons d'action (Voir, Modifier)
- Pagination

**Design** :
- Cartes verticales empilées
- Hover effect avec bordure gauche accentuée
- Code couleur par catégorie
- Responsive design

### 2. `faq/detail.html`

Page détaillée avec :
- Question en grand titre avec icône ❓
- Badge catégorie
- Métadonnées complètes
- Réponse formatée en HTML
- Section "C'était utile ?" avec bouton vote
- Actions admin (Modifier, Supprimer)
- Breadcrumb de navigation

**Interactivité** :
- Vote AJAX sans rechargement
- Animation au clic du bouton
- Protection contre votes multiples
- Mise à jour dynamique du compteur

### 3. `faq/edit.html`

Formulaire d'édition avec :
- Champ Question (input text)
- Sélecteur de catégorie
- Import PDF/Word avec preview
- Éditeur TinyMCE pour la réponse
- Checkbox "Publier immédiatement"
- Boutons Enregistrer / Annuler

**Éditeur TinyMCE** :
- Configuration complète (mêmes plugins que procédures)
- Thème sombre adapté
- Upload d'images automatique
- Import de documents
- Mode plein écran

---

## 💡 Cas d'Usage

### 1. Support Utilisateur

**Scénario** : Un utilisateur cherche comment réinitialiser son mot de passe.

```
1. L'utilisateur clique sur "FAQ" dans la navigation
2. Filtre par catégorie "Comptes"
3. Trouve la FAQ "Comment réinitialiser mon mot de passe ?"
4. Lit la réponse détaillée avec captures d'écran
5. Clique sur "👍 Oui, c'est utile"
```

### 2. Création de FAQ par Technicien

**Scénario** : Un technicien veut documenter une solution courante.

```
1. Clic sur "+ Nouvelle FAQ"
2. Saisit la question : "Comment installer l'imprimante réseau ?"
3. Sélectionne catégorie "Matériel"
4. Importe un PDF existant avec la procédure
5. Enrichit avec des images (drag & drop)
6. Coche "Publier immédiatement"
7. Enregistre
```

### 3. Gestion par Admin

**Scénario** : Un admin veut organiser les FAQ.

```
1. Consulte la liste des FAQ
2. Coche "Afficher les brouillons"
3. Révise les brouillons soumis
4. Modifie et publie les FAQ validées
5. Supprime les FAQ obsolètes
```

---

## 📊 Statistiques et Métriques

### Compteurs Disponibles

- **view_count** : Incrémenté à chaque consultation
- **helpful_count** : Incrémenté à chaque vote "utile"

### Affichage

- 👁️ **Vues** : `{{ faq.view_count }} vues`
- 👍 **Utile** : `{{ faq.helpful_count }} utile`

### Utilisation

Ces métriques permettent de :
- Identifier les FAQ les plus consultées
- Mesurer l'utilité perçue
- Prioriser les mises à jour
- Analyser les besoins des utilisateurs

---

## 🔧 Déploiement

### Sur le Serveur de Production

```bash
# 1. Connexion au serveur
ssh ubuntu@193.70.41.117

# 2. Aller dans le répertoire
cd /var/www/kb_basedoc

# 3. Récupérer les derniers changements
git pull origin claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8

# 4. Activer l'environnement virtuel
source venv/bin/activate

# 5. Créer la migration
flask db migrate -m "Add FAQs table for frequently asked questions"

# 6. Appliquer la migration
flask db upgrade

# 7. Redémarrer le service
sudo systemctl restart kb_basedoc

# 8. Vérifier le statut
sudo systemctl status kb_basedoc
```

### Test Post-Déploiement

1. ✅ Aller sur https://gagneraud.basedoc.fr
2. ✅ Cliquer sur l'onglet **"FAQ"**
3. ✅ Créer une FAQ de test
4. ✅ Vérifier l'éditeur TinyMCE
5. ✅ Tester l'import PDF/Word
6. ✅ Tester le vote "utile"
7. ✅ Vérifier les filtres

---

## 🎨 Design et Style

### Palette de Couleurs

- **Cartes FAQ** : `#16213e` (fond sombre)
- **Bordure** : `#2a3f5f` (gris-bleu)
- **Bordure hover** : `#00ff88` (vert néon)
- **Badges** : Code couleur des catégories
- **Bouton "utile"** : `#00ff88` (vert néon)

### Icônes

- ❓ **FAQ** : Point d'interrogation
- 👁️ **Vues** : Œil
- 👍 **Utile** : Pouce levé
- 📅 **Date** : Calendrier
- 👤 **Auteur** : Personnage
- ✏️ **Modifier** : Crayon
- 🗑️ **Supprimer** : Poubelle

### Typographie

- **Question** : 1.3rem, bold
- **Réponse** : 1.05rem, line-height 1.8
- **Métadonnées** : 0.9rem
- **Police** : Inter pour le texte, Fira Code pour le code

---

## 🔒 Permissions

### Matrice des Permissions

| Action | Public | Utilisateur | Auteur | Admin |
|--------|--------|-------------|--------|-------|
| Voir FAQ publiée | ✅ | ✅ | ✅ | ✅ |
| Voir FAQ brouillon | ❌ | ❌ | ✅ | ✅ |
| Créer FAQ | ❌ | ✅ | ✅ | ✅ |
| Modifier sa FAQ | ❌ | ❌ | ✅ | ✅ |
| Modifier toute FAQ | ❌ | ❌ | ❌ | ✅ |
| Supprimer sa FAQ | ❌ | ❌ | ✅ | ✅ |
| Supprimer toute FAQ | ❌ | ❌ | ❌ | ✅ |
| Voter "utile" | ✅ | ✅ | ✅ | ✅ |

---

## 📈 Améliorations Futures

### Court Terme
- [ ] Recherche full-text dans les FAQ
- [ ] Tags pour les FAQ
- [ ] FAQ liées (suggestions)
- [ ] Export PDF d'une FAQ

### Moyen Terme
- [ ] Commentaires sur les FAQ
- [ ] Vote "pas utile" avec feedback
- [ ] Versionning des FAQ
- [ ] FAQ suggérées par l'IA

### Long Terme
- [ ] Chatbot FAQ avec IA
- [ ] Analytics avancés (taux de résolution)
- [ ] Multi-langues
- [ ] Intégration Slack/Teams

---

## 🐛 Dépannage

### Erreur "table faqs does not exist"

```bash
cd /var/www/kb_basedoc
source venv/bin/activate
flask db upgrade
sudo systemctl restart kb_basedoc
```

### Éditeur TinyMCE ne charge pas

1. Vérifier que `/static/js/tinymce/tinymce.min.js` existe
2. Vérifier la console du navigateur (F12)
3. Vérifier que `{% block head %}` est dans `base.html`

### Vote "utile" ne fonctionne pas

1. Vérifier la console du navigateur (F12)
2. Vérifier que le CSRF token est présent
3. Vérifier les logs du serveur

---

## 📝 Notes Techniques

### Import PDF/Word

Réutilise le même endpoint que les procédures :
- `/files/import-document` (POST)
- Extraction via PyMuPDF (PDF) et python-docx (Word)
- Conversion en HTML formaté

### Upload d'Images

Réutilise le même endpoint que les procédures :
- `/files/upload-image` (POST)
- Validation stricte du type MIME
- Nommage sécurisé avec UUID
- Stockage dans `/storage/images/`

### Vote AJAX

```javascript
fetch('/faq/<id>/helpful', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': '{{ csrf_token() }}'
    }
})
```

Retourne :
```json
{
    "success": true,
    "helpful_count": 42
}
```

---

## 🎉 Résumé

La fonctionnalité FAQ est maintenant complète et opérationnelle avec :

✅ Gestion complète CRUD
✅ Éditeur TinyMCE avancé
✅ Import PDF/Word
✅ Système de vote "utile"
✅ Filtrage et pagination
✅ Accès public pour FAQ publiées
✅ Permissions granulaires
✅ Design moderne et responsive
✅ Integration avec les catégories existantes

**URL de test** : https://gagneraud.basedoc.fr/faq
