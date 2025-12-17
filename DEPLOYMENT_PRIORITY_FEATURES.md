# 🚀 Déploiement des Fonctionnalités Prioritaires

Ce document explique comment déployer les 5 fonctionnalités prioritaires sur le serveur de production.

## 📋 Fonctionnalités Implémentées

### 1. ✅ Système de Likes sur Procédures
- **Commit**: `4576cfe`
- Permet aux utilisateurs de voter "utile" sur une procédure
- Compteur affiché dans les métadonnées
- Protection contre les votes multiples (localStorage)
- Tracking dans l'audit log

### 2. ✅ Système d'Audit Log Complet
- **Commit**: `83e1eba`
- Historique de toutes les actions (create, update, delete, archive, restore, useful, comment, export)
- Dashboard admin avec filtres et pagination
- Tracking IP, user agent, timestamp, détails JSON
- Optimisé avec index composites

### 3. ✅ Système de Commentaires avec Réponses
- **Commit**: `52c6868`
- Commentaires et réponses imbriquées
- Édition/suppression (auteur ou admin uniquement)
- Badge "(modifié)" pour les éditions
- Interface moderne avec formulaires inline

### 4. ✅ Export PDF/DOCX pour Procédures
- **Commit**: `5deb4e6`
- Boutons d'export dans la page de détail
- Génération PDF avec WeasyPrint (formatage professionnel)
- Génération DOCX avec python-docx
- Tracking des exports dans l'audit log

### 5. ✅ Recherche PostgreSQL Full-Text Search
- **Commit**: `1c1dab8`
- Recherche avec ranking par pertinence
- Index GIN pour performance optimale
- Support de la langue française
- Poids : titre (A), description (B), contenu (C)

---

## 🔧 Déploiement Automatique

### Prérequis
- Accès SSH au serveur : `ubuntu@193.70.41.117`
- Droits sudo sur le serveur
- PostgreSQL en cours d'exécution

### Étapes

1. **Copier les fichiers sur le serveur**
   ```bash
   # Depuis votre machine locale
   scp -r * ubuntu@193.70.41.117:/tmp/kb-update/
   ```

2. **Se connecter au serveur**
   ```bash
   ssh ubuntu@193.70.41.117
   ```

3. **Exécuter le script de déploiement**
   ```bash
   cd /tmp/kb-update
   sudo ./deploy_priority_features.sh
   ```

Le script effectuera automatiquement :
- Installation des dépendances Python (WeasyPrint, beautifulsoup4)
- Exécution des 4 migrations SQL
- Installation des bibliothèques système nécessaires
- Redémarrage du service
- Vérification finale

---

## 📝 Déploiement Manuel (Alternative)

Si le script automatique échoue, suivez ces étapes manuelles :

### 1. Installation des Dépendances Python

```bash
cd /opt/kb-basedoc
source venv/bin/activate
pip install --upgrade pip
pip install WeasyPrint==60.2 beautifulsoup4==4.12.3
pip install -r requirements.txt
```

### 2. Installation des Bibliothèques Système (pour WeasyPrint)

```bash
sudo apt-get update
sudo apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info
```

### 3. Exécution des Migrations SQL

```bash
cd /opt/kb-basedoc

# Migration 1: Likes
sudo -u postgres psql -d kb_basedoc -f add_useful_count_to_procedures.sql

# Migration 2: Audit Log
sudo -u postgres psql -d kb_basedoc -f create_action_logs_table.sql

# Migration 3: Commentaires
sudo -u postgres psql -d kb_basedoc -f create_comments_table.sql

# Migration 4: Recherche Plein Texte
sudo -u postgres psql -d kb_basedoc -f add_fulltext_search_to_procedures.sql
```

### 4. Redémarrage du Service

```bash
sudo systemctl restart kb-basedoc
sudo systemctl status kb-basedoc
```

### 5. Vérification

```bash
# Vérifier les logs
sudo journalctl -u kb-basedoc -f

# Vérifier les tables
sudo -u postgres psql -d kb_basedoc -c "\dt"

# Vérifier la colonne search_vector
sudo -u postgres psql -d kb_basedoc -c "\d procedures"
```

---

## 🧪 Tests Post-Déploiement

### 1. Test du Système de Likes
1. Ouvrir une procédure
2. Cliquer sur "👍 Oui, c'est utile"
3. Vérifier que le compteur s'incrémente
4. Recharger la page → le bouton doit être désactivé

### 2. Test de l'Audit Log
1. Aller sur `/admin/audit-logs`
2. Vérifier que les actions récentes apparaissent
3. Tester les filtres (par type d'action, par utilisateur)

### 3. Test des Commentaires
1. Ouvrir une procédure
2. Ajouter un commentaire
3. Répondre à un commentaire
4. Modifier/supprimer un commentaire (si auteur)

### 4. Test de l'Export PDF/DOCX
1. Ouvrir une procédure
2. Cliquer sur [📕 Export PDF]
3. Vérifier que le PDF se télécharge avec un formatage correct
4. Cliquer sur [📘 Export DOCX]
5. Vérifier que le DOCX s'ouvre dans Word/LibreOffice

### 5. Test de la Recherche
1. Utiliser la barre de recherche
2. Taper des mots-clés
3. Vérifier que les résultats sont triés par pertinence
4. Tester l'autocomplétion

---

## 🐛 Dépannage

### Erreur: "Module WeasyPrint not found"
```bash
cd /opt/kb-basedoc
source venv/bin/activate
pip install WeasyPrint==60.2
sudo systemctl restart kb-basedoc
```

### Erreur: "Table action_logs does not exist"
```bash
cd /opt/kb-basedoc
sudo -u postgres psql -d kb_basedoc -f create_action_logs_table.sql
sudo systemctl restart kb-basedoc
```

### Erreur: "search_vector column does not exist"
```bash
cd /opt/kb-basedoc
sudo -u postgres psql -d kb_basedoc -f add_fulltext_search_to_procedures.sql
```

### Service ne démarre pas
```bash
# Vérifier les logs
sudo journalctl -u kb-basedoc -n 50

# Vérifier la syntaxe Python
cd /opt/kb-basedoc
source venv/bin/activate
python -m py_compile app/*.py
```

### Problème de permissions
```bash
sudo chown -R ubuntu:ubuntu /opt/kb-basedoc
sudo chmod +x /opt/kb-basedoc/venv/bin/*
```

---

## 📊 Statistiques du Déploiement

| Métrique | Valeur |
|----------|--------|
| Commits | 5 |
| Fichiers modifiés | 15+ |
| Nouvelles lignes | ~2000+ |
| Scripts SQL | 4 |
| Nouvelles dépendances | 2 (WeasyPrint, beautifulsoup4) |
| Nouveaux endpoints | 8 |
| Nouveaux modèles | 2 (ActionLog, Comment) |

---

## 📞 Support

En cas de problème :
1. Consulter les logs : `sudo journalctl -u kb-basedoc -f`
2. Vérifier la base de données : `sudo -u postgres psql -d kb_basedoc`
3. Vérifier les fichiers de migration sont présents
4. Redémarrer le service : `sudo systemctl restart kb-basedoc`

---

## 🎯 Accès

- **URL Application**: http://gagneraud.basedoc.fr
- **Dashboard Admin**: http://gagneraud.basedoc.fr/admin
- **Audit Logs**: http://gagneraud.basedoc.fr/admin/audit-logs
- **Serveur**: ubuntu@193.70.41.117

---

**Dernière mise à jour**: 17 décembre 2025
**Version**: 1.1.0 (avec 5 fonctionnalités prioritaires)
