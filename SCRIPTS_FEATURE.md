# 📜 Fonctionnalité Scripts Collaboratifs

## 🎯 Vue d'ensemble

Remplacement de l'onglet "Procédures" par un espace collaboratif de partage de scripts. Les utilisateurs peuvent publier, partager et réviser des scripts utiles avec l'IA.

## ✨ Fonctionnalités

### 1. Gestion des Scripts

- **Créer un script** : Formulaire avec titre, description, code, langage
- **Modifier un script** : Seul l'auteur ou un admin peut modifier
- **Supprimer un script** : Seul l'auteur ou un admin peut supprimer
- **Lister les scripts** : Pagination, filtres par langage et statut
- **Voir un script** : Affichage détaillé avec coloration syntaxique

### 2. Révision IA du Code 🤖

Fonctionnalité phare : bouton "Réviser avec l'IA" qui analyse le code et fournit :

- **Sécurité** : Vulnérabilités, injection, credentials, permissions
- **Performance** : Optimisations, boucles inefficaces, IO
- **Bonnes pratiques** : Style, nommage, documentation, gestion d'erreurs
- **Bugs potentiels** : Erreurs logiques, edge cases, variables non initialisées
- **Score global** : Note sur 100
- **Résumé** : Appréciation générale

#### Exemple de révision

```json
{
  "security": [
    {
      "issue": "Path traversal vulnérabilité",
      "severity": "critical",
      "suggestion": "Utiliser secure_filename() et valider le chemin"
    }
  ],
  "performance": [
    {
      "issue": "Boucle inefficace ligne 42",
      "impact": "medium",
      "suggestion": "Utiliser une compréhension de liste"
    }
  ],
  "best_practices": [
    {
      "practice": "Ajout de commentaires",
      "priority": "medium",
      "suggestion": "Documenter la fonction principale"
    }
  ],
  "bugs": [],
  "overall_score": 75,
  "summary": "Le code est globalement correct mais présente des vulnérabilités de sécurité à corriger."
}
```

### 3. Système de Vérification

- **Badge "Vérifié"** : Visible pour les scripts vérifiés par un admin
- **Notes de vérification** : Les admins peuvent ajouter des notes
- **Statuts** : Draft, Published, Archived

### 4. Filtrage et Recherche

- **Par langage** : PowerShell, Bash, Python, JavaScript, SQL, Batch, VBScript
- **Par statut** : Publiés, Brouillons, Archivés
- **Pagination** : 20 scripts par page

### 5. Interface Moderne

- **Cards avec badges** : Langage, vérifié, statut
- **Coloration par langage** : Chaque langage a sa couleur distinctive
- **Éditeur de code** : Support Tab, compteur de lignes/caractères
- **Responsive** : Design adaptatif mobile

## 🗂️ Structure de Données

### Modèle Script

```python
class Script(db.Model):
    id = Integer (PK)
    title = String(500)
    description = Text
    content = Text (le code)
    language = String(50) - PowerShell, Bash, Python, etc.
    author_id = Integer (FK vers User)
    created_at = DateTime
    updated_at = DateTime
    is_verified = Boolean
    verification_notes = Text
    ai_suggestions = Text (JSON)
    status = String(20) - draft, published, archived
```

### Relations

- **Script.author** → User : Auteur du script
- **User.scripts** → List[Script] : Scripts créés par l'utilisateur

## 🛣️ Routes

| Route | Méthode | Description |
|-------|---------|-------------|
| `/scripts` | GET | Liste des scripts |
| `/scripts/<id>` | GET | Détail d'un script |
| `/scripts/new` | GET, POST | Créer un script |
| `/scripts/<id>/edit` | GET, POST | Modifier un script |
| `/scripts/<id>/delete` | POST | Supprimer un script |
| `/scripts/<id>/review` | POST | Réviser le code avec l'IA |
| `/scripts/<id>/verify` | POST | Marquer comme vérifié (admin) |

## 🎨 Templates

### 1. `scripts/list.html`

Affichage en grille des scripts avec :
- Cards colorées par langage
- Filtres langage/statut
- Badge vérifié
- Actions rapides (Voir, Modifier)

### 2. `scripts/detail.html`

Affichage détaillé avec :
- Métadonnées (auteur, dates)
- Code avec coloration syntaxique
- Bouton "Réviser avec l'IA"
- Bouton "Copier le code"
- Section révision IA (affichage dynamique)
- Actions admin (vérifier)
- Zone danger (supprimer)

### 3. `scripts/edit.html`

Formulaire d'édition avec :
- Éditeur de code monospace
- Support Tab (insertion 4 espaces)
- Compteur lignes/caractères
- Sélecteur de langage
- Sélecteur de statut

## 🤖 Service IA

### Fonction `review_code()`

```python
AIService.review_code(
    code: str,
    language: str,
    title: str
) -> Dict
```

**Prompt spécialisé** : Analyse détaillée en 6 catégories (sécurité, performance, bonnes pratiques, bugs, score, résumé)

**Retry automatique** : 3 tentatives avec exponential backoff

**Stockage** : Les suggestions sont sauvegardées dans `Script.ai_suggestions` (JSON)

## 📊 Migration de Base de Données

### Création de la table scripts

```bash
# Sur le serveur
cd /var/www/kb_basedoc
source venv/bin/activate
python create_scripts_table.py  # Génère la migration
flask db upgrade  # Applique la migration
```

## 🚀 Déploiement

### Étapes de déploiement

1. **Commit local** :
```bash
git add .
git commit -m "feat: Add collaborative scripts feature with AI code review"
git push origin claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8
```

2. **Sur le serveur** :
```bash
ssh ubuntu@193.70.41.117
cd /var/www/kb_basedoc
git pull origin claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8
source venv/bin/activate
flask db upgrade
sudo systemctl restart kb_basedoc
```

3. **Vérification** :
```bash
sudo systemctl status kb_basedoc
curl -I http://localhost:8000
```

## 🔒 Permissions

- **Tous les utilisateurs** : Créer, voir, lister des scripts
- **Auteur** : Modifier, supprimer ses propres scripts
- **Admin** : Modifier, supprimer n'importe quel script, vérifier les scripts

## 🎯 Cas d'Usage

### 1. Partage de scripts PowerShell

Un administrateur système publie un script PowerShell de sauvegarde automatique. Les autres admins peuvent le consulter, le copier et bénéficier de la révision IA.

### 2. Validation de code

Un développeur junior écrit un script Bash et utilise la révision IA pour identifier les failles de sécurité avant de le publier.

### 3. Bibliothèque d'équipe

L'équipe construit progressivement une bibliothèque de scripts vérifiés et documentés.

## 📈 Améliorations Futures

- [ ] Export de scripts (fichier .ps1, .sh, etc.)
- [ ] Commentaires sur les scripts
- [ ] Système de votes/likes
- [ ] Historique des versions
- [ ] Recherche full-text dans le code
- [ ] Snippets (morceaux de code réutilisables)
- [ ] API REST pour l'intégration externe

## 🐛 Dépannage

### Erreur "table scripts does not exist"

```bash
cd /var/www/kb_basedoc
source venv/bin/activate
flask db upgrade
```

### Erreur module 'scripts' not found

Vérifier que `scripts_bp` est bien enregistré dans `app/__init__.py` :
```python
from app.routes.scripts import scripts_bp
app.register_blueprint(scripts_bp)
```

### Bouton révision IA ne fonctionne pas

1. Vérifier que `CLAUDE_API_KEY` est définie dans `.env`
2. Vérifier les logs : `tail -f /var/log/kb_basedoc/app.log`
3. Vérifier la console du navigateur (F12)

## 📝 Notes

- Les révisions IA sont stockées dans la base de données (champ `ai_suggestions`)
- La dernière révision est affichée automatiquement lors de la visualisation
- Le coût estimé d'une révision : ~$0.02 (dépend de la taille du code)
- Le modèle utilisé : Claude Sonnet 4.5
