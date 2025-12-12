# 🌐 Configuration DNS - Guide Rapide

## ⚡ Action Urgente Requise

**Le déploiement est à 95% terminé !**

Il ne manque **QUE la configuration DNS** pour activer HTTPS.

---

## 🎯 Ce qu'il faut faire (5 minutes)

### Enregistrement DNS requis :

```
Type : A
Nom : gagneraud
Domaine : basedoc.fr
Valeur/Cible : 193.70.41.117
TTL : 3600 (ou Auto)
```

Résultat final : `gagneraud.basedoc.fr` → `193.70.41.117`

---

## 📋 Instructions par fournisseur DNS

### 🔵 OVH (Recommandé)

1. **Connexion** :
   - Allez sur https://www.ovh.com/manager/
   - Connectez-vous avec vos identifiants

2. **Accéder à la zone DNS** :
   - Cliquez sur **Web Cloud** (menu gauche)
   - Cliquez sur **Noms de domaine**
   - Sélectionnez `basedoc.fr`
   - Cliquez sur l'onglet **Zone DNS**

3. **Ajouter l'enregistrement** :
   - Cliquez sur **Ajouter une entrée**
   - Sélectionnez **A**
   - Remplissez :
     ```
     Sous-domaine : gagneraud
     TTL : 3600
     Cible : 193.70.41.117
     ```
   - Cliquez sur **Suivant** puis **Valider**

4. **Résultat** :
   ```
   gagneraud.basedoc.fr    IN    A    193.70.41.117
   ```

⏱️ **Délai de propagation** : 5-30 minutes

---

### 🟠 CloudFlare

1. **Connexion** :
   - Allez sur https://dash.cloudflare.com/
   - Connectez-vous

2. **Sélectionner le domaine** :
   - Cliquez sur `basedoc.fr` dans la liste

3. **Ajouter l'enregistrement** :
   - Allez dans **DNS** → **Records**
   - Cliquez sur **Add record**
   - Remplissez :
     ```
     Type : A
     Name : gagneraud
     IPv4 address : 193.70.41.117
     Proxy status : DNS only (🔴 gris, PAS orange)
     TTL : Auto
     ```
   - Cliquez sur **Save**

⚠️ **Important** : Désactivez le proxy CloudFlare (icône nuage grise) pour Let's Encrypt.

⏱️ **Délai de propagation** : 2-5 minutes (CloudFlare est rapide)

---

### 🟢 Autre fournisseur DNS (Generic)

Si vous utilisez un autre fournisseur (Gandi, Namecheap, Google Domains, etc.) :

1. Connectez-vous à votre panneau de contrôle DNS
2. Trouvez la section "Zone DNS" ou "DNS Management"
3. Ajoutez un enregistrement **A** :
   - **Host/Name** : `gagneraud`
   - **Type** : `A`
   - **Value/Target** : `193.70.41.117`
   - **TTL** : `3600` ou `1 Hour`
4. Sauvegardez

⏱️ **Délai de propagation** : 15-60 minutes

---

## ✅ Vérifier que le DNS fonctionne

### Méthode 1 : Command line (Linux/Mac)

```bash
# nslookup
nslookup gagneraud.basedoc.fr

# Résultat attendu :
# Name:    gagneraud.basedoc.fr
# Address: 193.70.41.117
```

```bash
# dig
dig gagneraud.basedoc.fr +short

# Résultat attendu :
# 193.70.41.117
```

```bash
# ping
ping gagneraud.basedoc.fr

# Résultat attendu :
# PING gagneraud.basedoc.fr (193.70.41.117): 56 data bytes
```

### Méthode 2 : Command line (Windows)

```cmd
nslookup gagneraud.basedoc.fr

REM Résultat attendu :
REM Nom :    gagneraud.basedoc.fr
REM Address: 193.70.41.117
```

### Méthode 3 : Sites web

Vérifiez la propagation DNS mondiale :

- **DNS Checker** : https://dnschecker.org/#A/gagneraud.basedoc.fr
- **What's My DNS** : https://www.whatsmydns.net/#A/gagneraud.basedoc.fr
- **DNS Propagation** : https://www.dnspropagation.net/

Vous devriez voir des ✅ verts avec l'IP `193.70.41.117` dans plusieurs pays.

---

## 🔄 Après la propagation DNS

Une fois que le DNS pointe correctement (vérification ci-dessus), faites ceci :

### 1. Connectez-vous au serveur

```bash
ssh ubuntu@193.70.41.117
```

### 2. Obtenez le certificat SSL

```bash
sudo certbot --nginx -d gagneraud.basedoc.fr --non-interactive --agree-tos --email dheurtebise@basedoc.fr --redirect
```

### 3. Vérifiez le résultat

Si le certificat est obtenu avec succès, vous verrez :

```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/gagneraud.basedoc.fr/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/gagneraud.basedoc.fr/privkey.pem

Deploying certificate
Successfully deployed certificate for gagneraud.basedoc.fr to /etc/nginx/sites-enabled/kb_basedoc
Congratulations! You have successfully enabled HTTPS on https://gagneraud.basedoc.fr
```

### 4. Testez HTTPS

Ouvrez votre navigateur :

```
https://gagneraud.basedoc.fr
```

Vous devriez voir :
- 🔒 Cadenas vert dans la barre d'adresse
- Page de connexion de l'application

---

## ⏱️ Combien de temps ça prend ?

| Fournisseur DNS | Temps de propagation typique |
|-----------------|------------------------------|
| CloudFlare      | 2-5 minutes                  |
| OVH             | 5-30 minutes                 |
| Gandi           | 15-60 minutes                |
| Namecheap       | 30-60 minutes                |
| Google Domains  | 5-15 minutes                 |

💡 **Astuce** : Utilisez les sites de vérification DNS pour savoir quand c'est propagé, plutôt que d'attendre un temps fixe.

---

## 🐛 Problèmes courants

### Problème 1 : "Le DNS ne se propage pas"

**Causes possibles** :
- Vous n'avez pas sauvegardé la modification dans le panneau DNS
- Le domaine `basedoc.fr` n'utilise pas les bons serveurs DNS
- TTL trop élevé (ancien enregistrement en cache)

**Solutions** :
1. Vérifiez que la modification est bien visible dans le panneau DNS
2. Vérifiez les nameservers du domaine :
   ```bash
   dig basedoc.fr NS
   ```
3. Attendez le TTL de l'ancien enregistrement (si existant)

### Problème 2 : "Certbot échoue toujours"

**Vérifiez que le DNS fonctionne VRAIMENT** :

```bash
# Depuis votre machine locale
nslookup gagneraud.basedoc.fr

# Depuis le serveur
ssh ubuntu@193.70.41.117
nslookup gagneraud.basedoc.fr
```

Les deux doivent retourner `193.70.41.117`.

### Problème 3 : "Le site est accessible mais pas avec HTTPS"

Si le HTTP fonctionne (`http://gagneraud.basedoc.fr`) mais pas HTTPS :

1. Vérifiez que certbot a bien été exécuté
2. Vérifiez les logs :
   ```bash
   sudo tail -f /var/log/letsencrypt/letsencrypt.log
   ```
3. Vérifiez la configuration Nginx :
   ```bash
   sudo nginx -t
   ```

---

## 📞 Aide supplémentaire

### Vérifier les serveurs DNS du domaine

```bash
dig basedoc.fr NS

# Vous devriez voir les nameservers (ex: pour OVH)
# dns200.anycast.me.
# ns200.anycast.me.
```

### Forcer le refresh du cache DNS local

**Linux** :
```bash
sudo systemd-resolve --flush-caches
```

**Mac** :
```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

**Windows** :
```cmd
ipconfig /flushdns
```

---

## 🎯 Checklist DNS

- [ ] Me connecter au panneau DNS de mon fournisseur
- [ ] Ajouter l'enregistrement A pour `gagneraud.basedoc.fr` → `193.70.41.117`
- [ ] Sauvegarder la modification
- [ ] Attendre 5-30 minutes
- [ ] Vérifier avec `nslookup gagneraud.basedoc.fr`
- [ ] Vérifier sur https://dnschecker.org/
- [ ] Se connecter au serveur avec SSH
- [ ] Lancer `sudo certbot --nginx -d gagneraud.basedoc.fr`
- [ ] Tester https://gagneraud.basedoc.fr
- [ ] Se connecter avec dheurtebise@basedoc.fr
- [ ] 🎉 C'est terminé !

---

## 📸 Captures d'écran

### OVH - Ajout d'un enregistrement A

```
╔══════════════════════════════════════════════════╗
║  Ajouter une entrée DNS                          ║
╠══════════════════════════════════════════════════╣
║  Type d'enregistrement : [A ▼]                   ║
║                                                  ║
║  Sous-domaine : [gagneraud                    ]  ║
║  TTL          : [3600                         ]  ║
║  Cible        : [193.70.41.117                ]  ║
║                                                  ║
║          [Annuler]        [Valider]              ║
╚══════════════════════════════════════════════════╝
```

### CloudFlare - Ajout d'un enregistrement A

```
╔══════════════════════════════════════════════════╗
║  Add record                                      ║
╠══════════════════════════════════════════════════╣
║  Type     : [A ▼]                                ║
║  Name     : [gagneraud                        ]  ║
║  IPv4     : [193.70.41.117                    ]  ║
║  Proxy    : [🔴 DNS only] (gris, pas orange)    ║
║  TTL      : [Auto ▼]                             ║
║                                                  ║
║                              [Save]              ║
╚══════════════════════════════════════════════════╝
```

---

## 🚀 Résumé : 3 étapes seulement !

1. **Ajouter le DNS** (5 min)
   ```
   gagneraud.basedoc.fr → 193.70.41.117
   ```

2. **Attendre propagation** (5-30 min)
   ```bash
   nslookup gagneraud.basedoc.fr
   ```

3. **Obtenir SSL** (2 min)
   ```bash
   ssh ubuntu@193.70.41.117
   sudo certbot --nginx -d gagneraud.basedoc.fr
   ```

**C'est tout !** 🎉

---

**L'application est déjà en ligne, il ne manque que cette petite config DNS !** ✨
