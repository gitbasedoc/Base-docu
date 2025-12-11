# 🚀 Guide de Déploiement Automatique

## Méthode 1 : Déploiement en une commande (RECOMMANDÉ)

### Sur le serveur VPS :

```bash
# Connectez-vous au serveur
ssh root@193.70.41.117

# Téléchargez et exécutez le script de déploiement
curl -sSL https://raw.githubusercontent.com/VOTRE-ORG/Base-docu/claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8/deploy.sh | bash
```

**Le script va vous demander** :
1. ✅ URL du repository Git
2. ✅ Branche (par défaut: `claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8`)
3. ✅ Clé API Claude (`sk-ant-...`)
4. ✅ Email admin
5. ✅ Nom admin
6. ✅ Mot de passe admin

**Ensuite il fait TOUT automatiquement** :
- Clone le repository
- Installe toutes les dépendances
- Configure PostgreSQL
- Configure Nginx + SSL
- Crée l'admin
- Démarre l'application

---

## Méthode 2 : Déploiement manuel

### Étape 1 : Transférer le script

Depuis votre machine locale :

```bash
# Aller dans le dossier du projet
cd /home/user/Base-docu

# Transférer le script sur le serveur
scp deploy.sh root@193.70.41.117:/root/

# Se connecter au serveur
ssh root@193.70.41.117
```

### Étape 2 : Exécuter le script

Sur le serveur :

```bash
# Rendre exécutable
chmod +x /root/deploy.sh

# Lancer le déploiement
/root/deploy.sh
```

---

## Méthode 3 : Avec Git directement sur le serveur

```bash
# Sur le serveur
ssh root@193.70.41.117

# Installer git
apt update
apt install -y git

# Cloner le repository
git clone https://github.com/VOTRE-ORG/Base-docu.git /root/kb_source
cd /root/kb_source

# Checkout de la branche
git checkout claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8

# Lancer le déploiement
chmod +x deploy.sh
./deploy.sh
```

---

## 📋 Ce dont vous avez besoin

Avant de commencer, préparez :

| Information | Exemple | Obligatoire |
|-------------|---------|-------------|
| **URL Repository Git** | `https://github.com/votre-org/Base-docu.git` | ✅ Oui |
| **Clé API Claude** | `sk-ant-api03-xxx...` | ✅ Oui |
| **Email Admin** | `dheurtebise@basedoc.fr` | ✅ Oui |
| **Nom Admin** | `David Heurtebise` | ✅ Oui |
| **Mot de passe Admin** | `********` (min 8 caractères) | ✅ Oui |
| **Branche Git** | `claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8` | Non (auto) |

---

## ⏱️ Durée du déploiement

- **Clone du repository** : ~30 secondes
- **Installation complète** : 10-15 minutes
- **Total** : ~15 minutes

---

## ✅ Après le déploiement

Une fois terminé, vous verrez :

```
════════════════════════════════════════════════════════════════
✓ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS !
════════════════════════════════════════════════════════════════

📋 Informations importantes :
────────────────────────────────────────────────────────────────
URL: https://gagneraud.basedoc.fr
Admin: dheurtebise@basedoc.fr

🚀 Prochaines étapes :
1. Accédez à https://gagneraud.basedoc.fr
2. Connectez-vous avec dheurtebise@basedoc.fr
3. Créez votre première procédure
```

### Vérifications :

```bash
# Vérifier que le service tourne
systemctl status kb_basedoc

# Voir les logs
journalctl -u kb_basedoc -f

# Tester l'accès
curl -I https://gagneraud.basedoc.fr
```

---

## 🔧 Résolution de problèmes

### Le script échoue au clonage Git

**Problème** : Authentification Git requise

**Solution** :
```bash
# Si repository privé, configurez les credentials
git config --global credential.helper store
```

### Le script s'arrête en demandant des informations

**Problème** : Mode interactif

**Solution** : Répondez aux questions avec les informations préparées

### Erreur de permissions

**Problème** : Script pas en root

**Solution** :
```bash
sudo /root/deploy.sh
```

---

## 📞 Support

Si vous rencontrez des problèmes :

1. **Consultez les logs** :
   ```bash
   cat /var/log/kb_basedoc_install.log
   ```

2. **Vérifiez l'installation** :
   ```bash
   /var/www/kb_basedoc/verify_installation.sh
   ```

3. **Informations sauvegardées** :
   ```bash
   cat /root/kb_deployment_info.txt
   ```

---

## 🎯 Commandes utiles post-déploiement

```bash
# Redémarrer l'application
systemctl restart kb_basedoc

# Voir les logs en temps réel
journalctl -u kb_basedoc -f

# Vérifier Nginx
systemctl status nginx

# Vérifier PostgreSQL
systemctl status postgresql

# Créer un nouvel utilisateur
cd /var/www/kb_basedoc
source venv/bin/activate
flask create-admin
```

---

## 🔄 Mise à jour de l'application

Pour mettre à jour après modifications :

```bash
# Sur le serveur
cd /var/www/kb_basedoc

# Pull les dernières modifications
git pull origin claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8

# Installer nouvelles dépendances si nécessaire
source venv/bin/activate
pip install -r requirements.txt

# Appliquer migrations si nécessaire
flask db upgrade

# Redémarrer
systemctl restart kb_basedoc
```

---

## 🎉 C'est tout !

Le script fait tout le travail pour vous. Lancez-le et attendez 15 minutes ! ☕
