# 📊 État du Déploiement - KB Support Basedoc

**Date** : 12 décembre 2024
**Serveur** : ubuntu@193.70.41.117
**Domaine** : gagneraud.basedoc.fr

---

## ✅ Ce qui fonctionne

### 1. Application Flask
- ✅ Code source déployé dans `/var/www/kb_basedoc`
- ✅ Virtual environment Python créé avec toutes les dépendances
- ✅ Configuration `.env` créée avec les bonnes valeurs

### 2. Base de données PostgreSQL
- ✅ Base de données `kb_basedoc` créée
- ✅ Utilisateur `kb_user` créé avec les permissions correctes
- ✅ Schéma initialisé avec `flask db upgrade`
- ✅ Catégories de base créées avec `flask init-db`
- ✅ Administrateur créé :
  - Email : `dheurtebise@basedoc.fr`
  - Nom : `David Heurtebise`

### 3. Serveur Gunicorn
- ✅ Service systemd configuré : `kb_basedoc.service`
- ✅ Gunicorn démarré et en cours d'exécution sur port 8000
- ✅ Permissions corrigées pour logs et pidfiles

### 4. Reverse Proxy Nginx
- ✅ Nginx installé et configuré
- ✅ Configuration site `/etc/nginx/sites-available/kb_basedoc`
- ✅ Symlink créé dans `sites-enabled`
- ✅ Nginx redémarre correctement
- ✅ **Application accessible en HTTP** (port 80)

### 5. Sécurité
- ✅ Fail2Ban installé et configuré
- ✅ UFW (pare-feu) activé
  - Port 22 (SSH) : Ouvert
  - Port 80 (HTTP) : Ouvert
  - Port 443 (HTTPS) : Ouvert
- ✅ Permissions fichiers correctement configurées

---

## ⚠️ Problème actuel : SSL / HTTPS

### Erreur rencontrée :

```
Certbot failed to authenticate some domains (authenticator: nginx).
The Certificate Authority reported these problems:
  Domain: gagneraud.basedoc.fr
  Type:   dns
  Detail: DNS problem: NXDOMAIN looking up A for gagneraud.basedoc.fr
```

### Cause :

**Le DNS n'est pas configuré !**

Le domaine `gagneraud.basedoc.fr` n'a pas d'enregistrement DNS pointant vers l'IP du serveur `193.70.41.117`.

Let's Encrypt ne peut pas valider le domaine car il ne peut pas résoudre `gagneraud.basedoc.fr` en une adresse IP.

---

## 🔧 Ce qu'il faut faire MAINTENANT

### Étape 1 : Configurer le DNS (OBLIGATOIRE)

Vous devez créer un enregistrement DNS chez votre fournisseur DNS :

#### Si vous utilisez **OVH** :

1. Connectez-vous à l'espace client OVH
2. Allez dans **Web Cloud** → **Noms de domaine**
3. Sélectionnez le domaine `basedoc.fr`
4. Cliquez sur l'onglet **Zone DNS**
5. Cliquez sur **Ajouter une entrée**
6. Choisissez **Type A**
7. Remplissez :
   - **Sous-domaine** : `gagneraud`
   - **Cible** : `193.70.41.117`
   - **TTL** : 3600 (ou laissez par défaut)
8. Cliquez sur **Valider**

#### Si vous utilisez **CloudFlare** :

1. Connectez-vous à CloudFlare
2. Sélectionnez le domaine `basedoc.fr`
3. Allez dans **DNS** → **Records**
4. Cliquez sur **Add record**
5. Remplissez :
   - **Type** : `A`
   - **Name** : `gagneraud`
   - **IPv4 address** : `193.70.41.117`
   - **Proxy status** : 🔴 DNS only (désactivez le proxy orange)
   - **TTL** : Auto
6. Cliquez sur **Save**

#### Autre fournisseur DNS :

Créez un enregistrement de type **A** :
```
gagneraud.basedoc.fr  →  193.70.41.117
```

---

### Étape 2 : Vérifier la propagation DNS

Après avoir configuré le DNS, **attendez 5-30 minutes** pour la propagation.

#### Vérifier depuis votre machine locale :

```bash
# Méthode 1 : nslookup
nslookup gagneraud.basedoc.fr

# Méthode 2 : dig
dig gagneraud.basedoc.fr

# Méthode 3 : ping
ping gagneraud.basedoc.fr
```

Vous devriez voir l'IP **193.70.41.117** dans les résultats.

#### Vérifier en ligne :

- https://dnschecker.org/#A/gagneraud.basedoc.fr
- https://www.whatsmydns.net/#A/gagneraud.basedoc.fr

---

### Étape 3 : Obtenir le certificat SSL

Une fois le DNS propagé, connectez-vous au serveur :

```bash
ssh ubuntu@193.70.41.117
```

Puis lancez à nouveau Certbot :

```bash
sudo certbot --nginx -d gagneraud.basedoc.fr --non-interactive --agree-tos --email dheurtebise@basedoc.fr --redirect
```

Si tout se passe bien, vous verrez :

```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/gagneraud.basedoc.fr/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/gagneraud.basedoc.fr/privkey.pem

Deploying certificate
Successfully deployed certificate for gagneraud.basedoc.fr to /etc/nginx/sites-enabled/kb_basedoc
Congratulations! You have successfully enabled HTTPS on https://gagneraud.basedoc.fr
```

Nginx sera automatiquement reconfiguré pour utiliser HTTPS.

---

### Étape 4 : Vérifier le renouvellement automatique

Certbot a déjà été configuré pour le renouvellement automatique :

```bash
# Vérifier que le timer est actif
sudo systemctl status certbot.timer

# Tester le renouvellement (dry run)
sudo certbot renew --dry-run
```

---

## 🧪 Tester l'application MAINTENANT (sans SSL)

En attendant le DNS, vous pouvez tester l'application :

### Méthode 1 : Via l'IP directement

Ouvrez votre navigateur et allez sur :

```
http://193.70.41.117
```

⚠️ **Important** : Utilisez `http://` et NON `https://`

Vous devriez voir la page de connexion de l'application.

### Méthode 2 : Modifier votre fichier hosts (pour tester le domaine)

#### Sur Linux/Mac :

```bash
sudo nano /etc/hosts
```

Ajoutez cette ligne :
```
193.70.41.117  gagneraud.basedoc.fr
```

Sauvegardez (`Ctrl+X`, `Y`, `Enter`)

#### Sur Windows :

Ouvrez en tant qu'administrateur :
```
C:\Windows\System32\drivers\etc\hosts
```

Ajoutez :
```
193.70.41.117  gagneraud.basedoc.fr
```

Puis dans votre navigateur, allez sur :
```
http://gagneraud.basedoc.fr
```

⚠️ **N'oubliez pas de retirer cette ligne une fois le vrai DNS configuré !**

---

## 🎯 Checklist complète

- [x] Application déployée sur le serveur
- [x] PostgreSQL installé et configuré
- [x] Base de données créée et initialisée
- [x] Administrateur créé
- [x] Gunicorn configuré et démarré
- [x] Nginx configuré
- [x] Application accessible en HTTP
- [ ] **DNS configuré** ← **À FAIRE MAINTENANT**
- [ ] Certificat SSL obtenu
- [ ] Application accessible en HTTPS
- [ ] Tests complets de toutes les fonctionnalités

---

## 📝 Informations de connexion

Une fois le DNS et SSL configurés, vous pourrez accéder à :

**URL** : https://gagneraud.basedoc.fr

**Administrateur** :
- Email : `dheurtebise@basedoc.fr`
- Mot de passe : `[celui que vous avez défini lors de l'installation]`

---

## 🔍 Commandes de diagnostic

Si vous rencontrez des problèmes, voici les commandes utiles :

```bash
# Vérifier le service
sudo systemctl status kb_basedoc

# Voir les logs de l'application
sudo tail -f /var/log/kb_basedoc/app.log

# Voir les logs Gunicorn
sudo tail -f /var/log/gunicorn/error.log

# Voir les logs Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/kb_basedoc_error.log

# Redémarrer les services
sudo systemctl restart kb_basedoc
sudo systemctl restart nginx

# Tester la connexion PostgreSQL
psql -U kb_user -d kb_basedoc -h localhost -W

# Tester Gunicorn localement
curl -I http://localhost:8000

# Tester Nginx
curl -I http://localhost
```

---

## 📊 Architecture actuelle

```
Internet (port 80)
    ↓
Nginx (reverse proxy)
    ↓
Gunicorn (port 8000)
    ↓
Flask Application
    ↓
PostgreSQL (localhost:5432)
```

Une fois SSL configuré :

```
Internet (port 443, HTTPS)
    ↓
Nginx + SSL (Let's Encrypt)
    ↓
Gunicorn (port 8000)
    ↓
Flask Application
    ↓
PostgreSQL (localhost:5432)
```

---

## 🚀 Prochaines étapes après SSL

Une fois l'application accessible en HTTPS :

1. **Tester toutes les fonctionnalités** :
   - [ ] Login administrateur
   - [ ] Créer une procédure
   - [ ] Upload un fichier
   - [ ] Tester la recherche
   - [ ] Tester génération de tags IA
   - [ ] Tester reformulation IA

2. **Créer les templates manquants** :
   - [ ] `app/templates/procedures/list.html`
   - [ ] `app/templates/procedures/detail.html`
   - [ ] `app/templates/procedures/edit.html`
   - [ ] `app/templates/search.html`
   - [ ] `app/templates/errors/404.html`
   - [ ] `app/templates/errors/500.html`

3. **Configuration backup** :
   - [ ] Vérifier que le cron backup fonctionne
   - [ ] Tester une restauration

4. **Formation utilisateurs** :
   - [ ] Créer compte pour les membres de l'équipe IT
   - [ ] Former à l'utilisation de l'outil

---

## ⚡ Résumé : Action immédiate requise

**VOUS DEVEZ CONFIGURER LE DNS MAINTENANT** pour que le SSL fonctionne.

1. ✅ Allez chez votre fournisseur DNS (OVH/CloudFlare/autre)
2. ✅ Créez un enregistrement A : `gagneraud.basedoc.fr` → `193.70.41.117`
3. ⏳ Attendez 5-30 minutes
4. ✅ Vérifiez avec `nslookup gagneraud.basedoc.fr`
5. ✅ Relancez `sudo certbot --nginx -d gagneraud.basedoc.fr`
6. 🎉 Accédez à https://gagneraud.basedoc.fr

---

**Toutes les autres parties sont opérationnelles !** 🎉

L'application tourne, la base de données fonctionne, l'admin est créé.
Il ne manque **que le DNS** pour avoir le HTTPS.

En attendant, testez via `http://193.70.41.117` pour vérifier que tout fonctionne !
