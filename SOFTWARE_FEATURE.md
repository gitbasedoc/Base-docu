# 💻 Fonctionnalité Logiciels (Software)

## 🎯 Vue d'ensemble

La section Logiciels permet de créer, gérer et consulter une bibliothèque collaborative de logiciels utiles au service IT. Les utilisateurs peuvent ajouter des liens vers des logiciels, les décrire, et la communauté peut voter pour les logiciels les plus utiles.

## ✨ Fonctionnalités

### 1. Gestion Complète des Logiciels

#### Ajouter un Logiciel
- **Nom** : Nom du logiciel
- **Description** : Description détaillée de l'utilité
- **URL** : Lien vers le site officiel ou téléchargement
- **Catégorie** : Organisation par catégories existantes
- **Plateforme** : Windows, Linux, macOS, Web, Multi-plateforme, Mobile
- **Type** : Gratuit ou Payant

#### Modifier un Logiciel
- ✅ Permissions : Contributeur ou Admin uniquement
- ✅ Modification de toutes les informations
- ✅ Changement de catégorie et plateforme

#### Supprimer un Logiciel
- ✅ Permissions : Contributeur ou Admin uniquement
- ✅ Confirmation avant suppression
- ✅ Suppression complète de la base de données

### 2. Système de Navigation et Filtrage

#### Page Liste
- ✅ **Affichage par cartes** : Design moderne avec badges
- ✅ **Filtre par catégorie** : Sélection rapide par catégorie
- ✅ **Filtre par plateforme** : Windows, Linux, macOS, etc.
- ✅ **Filtre par type** : Gratuit ou Payant
- ✅ **Pagination** : 20 logiciels par page
- ✅ **Tri** : Par nombre de votes "utile" puis par date
- ✅ **Statistiques** : Nombre de votes "utile"

#### Badges et Indicateurs
- 🏷️ **Badge catégorie** : Avec code couleur personnalisé
- 💚 **Badge gratuit** : Fond vert pour logiciels gratuits
- 🟠 **Badge payant** : Fond orange pour logiciels payants
- 🖥️ **Badge plateforme** : Indique la plateforme supportée
- 👍 **Compteur "utile"** : Nombre de votes positifs

### 3. Page Détail Logiciel

#### Affichage Complet
- ✅ **Nom et description** : Informations complètes
- ✅ **URL cliquable** : Lien vers le site externe (nouvel onglet)
- ✅ **Métadonnées** : Contributeur, dates de création/modification
- ✅ **Catégorie** : Affichage avec code couleur
- ✅ **Navigation** : Breadcrumb et retour à la liste

#### Bouton "C'est utile ?"
- ✅ **Vote AJAX** : Sans rechargement de page
- ✅ **Compteur dynamique** : Mise à jour en temps réel
- ✅ **Protection** : Un seul vote par session
- ✅ **Animation** : Feedback visuel lors du clic

#### Actions Contributeur/Admin
- ✅ **Modifier** : Lien vers le formulaire d'édition
- ✅ **Supprimer** : Avec confirmation
- ✅ **Visible uniquement** : Pour contributeur ou admin

### 4. Accès Public

Tous les logiciels sont accessibles à tous les utilisateurs authentifiés :
- ✅ **Consultation** : Tous les utilisateurs connectés
- ✅ **Ajout** : Tous les utilisateurs connectés (collaboratif)
- ✅ **Modification** : Contributeur d'origine ou admin
- ✅ **Suppression** : Contributeur d'origine ou admin
- ✅ **Vote "utile"** : Tous les utilisateurs

---

## 🗂️ Structure de Données

### Modèle Software

```python
class Software(db.Model):
    id = Integer (PK)
    name = String(255) - Nom du logiciel
    description = Text - Description
    url = String(500) - URL vers le site
    category_id = Integer (FK vers Category)
    added_by = Integer (FK vers User)
    created_at = DateTime
    updated_at = DateTime
    is_free = Boolean - Gratuit ou payant
    platform = String(100) - Plateforme (Windows, Linux, etc.)
    useful_count = Integer - Nombre de votes "utile"
```

### Relations

- **Software.category** → Category : Catégorie du logiciel
- **Software.contributor** → User : Contributeur qui a ajouté le logiciel
- **User.software** → List[Software] : Logiciels ajoutés par l'utilisateur
- **Category.software** → List[Software] : Logiciels de cette catégorie

---

## 🛣️ Routes

| Route | Méthode | Description | Auth |
|-------|---------|-------------|------|
| `/software` | GET | Liste des logiciels | Oui |
| `/software/<id>` | GET | Détail d'un logiciel | Oui |
| `/software/new` | GET, POST | Ajouter un logiciel | Oui |
| `/software/<id>/edit` | GET, POST | Modifier un logiciel | Oui* |
| `/software/<id>/delete` | POST | Supprimer un logiciel | Oui* |
| `/software/<id>/useful` | POST | Marquer comme utile | Oui |

\* **Contributeur ou Admin** uniquement

---

## 🎨 Templates

### 1. `software/list.html`

Liste des logiciels avec :
- Cartes logiciels avec badges
- Filtres (catégorie, plateforme, type)
- Bouton "Visiter" (lien externe)
- Bouton "Détails"
- Statistiques (votes utiles)
- Pagination

**Design** :
- Grid responsive
- Badges de couleur (gratuit=vert, payant=orange)
- Hover effect avec bordure accentuée
- Code couleur par catégorie

### 2. `software/detail.html`

Page détaillée avec :
- Nom en grand titre avec icône 💻
- Badges (catégorie, type, plateforme)
- Métadonnées complètes
- Description détaillée
- URL cliquable avec icône externe
- Section "C'est utile ?" avec bouton vote
- Actions contributeur/admin (Modifier, Supprimer)
- Breadcrumb de navigation

**Interactivité** :
- Vote AJAX sans rechargement
- Animation au clic du bouton
- Protection contre votes multiples
- Mise à jour dynamique du compteur

### 3. `software/edit.html`

Formulaire d'édition avec :
- Champ Nom (input text)
- Champ URL (input url)
- Champ Description (textarea)
- Sélecteur de catégorie
- Sélecteur de plateforme (dropdown)
- Checkbox "Logiciel gratuit"
- Boutons Enregistrer / Annuler

**Validation** :
- Tous les champs requis sauf plateforme
- Validation URL côté navigateur
- CSRF protection

---

## 💡 Cas d'Usage

### 1. Partage d'Outil Utile

**Scénario** : Un technicien découvre un logiciel utile et veut le partager.

```
1. L'utilisateur clique sur "+ Ajouter un logiciel"
2. Remplit le formulaire :
   - Nom : "WinDirStat"
   - URL : "https://windirstat.net/"
   - Description : "Analyseur d'espace disque avec visualisation graphique"
   - Catégorie : "Système"
   - Plateforme : "Windows"
   - Gratuit : coché
3. Enregistre
4. Le logiciel apparaît dans la liste
```

### 2. Recherche d'Outil par Plateforme

**Scénario** : Un utilisateur cherche des outils Linux.

```
1. Va sur la page "Logiciels"
2. Sélectionne "Linux" dans le filtre Plateforme
3. Consulte la liste filtrée
4. Clique sur un logiciel pour voir les détails
5. Clique sur "Visiter" pour accéder au site officiel
6. Vote "Utile" si le logiciel répond au besoin
```

### 3. Maintenance par Admin

**Scénario** : Un admin veut organiser les logiciels.

```
1. Consulte la liste des logiciels
2. Filtre par catégorie "Non catégorisé"
3. Modifie chaque logiciel pour assigner la bonne catégorie
4. Supprime les doublons ou logiciels obsolètes
5. Vérifie que les URLs fonctionnent toujours
```

---

## 📊 Statistiques et Métriques

### Compteurs Disponibles

- **useful_count** : Incrémenté à chaque vote "utile"

### Affichage

- 👍 **Utile** : `{{ software.useful_count }} utile`

### Tri

Les logiciels sont triés par :
1. Nombre de votes "utile" (décroissant)
2. Date de création (décroissant)

Cela permet de mettre en avant les logiciels les plus appréciés.

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

# 5. Créer la table directement en SQL
sudo -u postgres psql kb_basedoc < create_software_table.sql

# OU avec la migration Flask
flask db migrate -m "Add software table"
flask db upgrade

# 6. Redémarrer le service
sudo systemctl restart kb_basedoc

# 7. Vérifier le statut
sudo systemctl status kb_basedoc
```

### Test Post-Déploiement

1. ✅ Aller sur https://gagneraud.basedoc.fr
2. ✅ Cliquer sur l'onglet **"Logiciels"** dans la navigation
3. ✅ Vérifier que la page se charge
4. ✅ Cliquer sur **"+ Ajouter un logiciel"**
5. ✅ Remplir le formulaire et enregistrer
6. ✅ Vérifier l'affichage dans la liste
7. ✅ Tester les filtres
8. ✅ Tester le vote "utile"
9. ✅ Vérifier les cartes de navigation sur la home page

---

## 🎨 Design et Style

### Palette de Couleurs

- **Cartes logiciels** : `#16213e` (fond sombre)
- **Bordure** : `#2a3f5f` (gris-bleu)
- **Bordure hover** : `#00ff88` (vert néon)
- **Badge gratuit** : `#4caf50` (vert)
- **Badge payant** : `#ff9800` (orange)
- **Bouton visiter** : `#00ff88` (vert néon)

### Icônes

- 💻 **Logiciels** : Ordinateur
- 👍 **Utile** : Pouce levé
- 🔗 **Visiter** : Lien
- 📅 **Date** : Calendrier
- 👤 **Contributeur** : Personnage
- ✏️ **Modifier** : Crayon
- 🗑️ **Supprimer** : Poubelle

### Typographie

- **Nom du logiciel** : 1.2rem, bold
- **Description** : 0.95rem, line-height 1.6
- **Métadonnées** : 0.9rem
- **Police** : Inter pour le texte, Fira Code pour le code

---

## 🔒 Permissions

### Matrice des Permissions

| Action | Non-connecté | Utilisateur | Contributeur | Admin |
|--------|--------------|-------------|--------------|-------|
| Voir logiciel | ❌ | ✅ | ✅ | ✅ |
| Ajouter logiciel | ❌ | ✅ | ✅ | ✅ |
| Modifier son logiciel | ❌ | ❌ | ✅ | ✅ |
| Modifier tout logiciel | ❌ | ❌ | ❌ | ✅ |
| Supprimer son logiciel | ❌ | ❌ | ✅ | ✅ |
| Supprimer tout logiciel | ❌ | ❌ | ❌ | ✅ |
| Voter "utile" | ❌ | ✅ | ✅ | ✅ |

---

## 📈 Améliorations Futures

### Court Terme
- [ ] Recherche full-text dans les logiciels
- [ ] Tags pour les logiciels
- [ ] Logiciels similaires (suggestions)
- [ ] Export CSV de la liste

### Moyen Terme
- [ ] Commentaires sur les logiciels
- [ ] Notes (1-5 étoiles)
- [ ] Captures d'écran
- [ ] Tutoriels d'installation

### Long Terme
- [ ] Versionning des logiciels
- [ ] Alertes de mise à jour
- [ ] Comparatif de logiciels
- [ ] Intégration avec API publiques (GitHub, etc.)

---

## 🐛 Dépannage

### Erreur "table software does not exist"

```bash
cd /var/www/kb_basedoc
source venv/bin/activate
sudo -u postgres psql kb_basedoc < create_software_table.sql
sudo systemctl restart kb_basedoc
```

### Vote "utile" ne fonctionne pas

1. Vérifier la console du navigateur (F12)
2. Vérifier que le CSRF token est présent
3. Vérifier les logs du serveur

---

## 📝 Notes Techniques

### Vote AJAX

```javascript
fetch('/software/<id>/useful', {
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
    "useful_count": 42
}
```

### Liens Externes

Tous les liens vers les logiciels s'ouvrent dans un nouvel onglet avec `target="_blank"` et `rel="noopener noreferrer"` pour la sécurité.

---

## 🎉 Résumé

La fonctionnalité Logiciels est maintenant complète et opérationnelle avec :

✅ Gestion complète CRUD
✅ Système de vote "utile"
✅ Filtrage multi-critères (catégorie, plateforme, type)
✅ Pagination
✅ Accès pour tous les utilisateurs connectés
✅ Contribution collaborative
✅ Permissions granulaires
✅ Design moderne et responsive
✅ Intégration avec les catégories existantes
✅ Navigation depuis la home page

**URL de test** : https://gagneraud.basedoc.fr/software
