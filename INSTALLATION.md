# 🚀 Guide d'Installation KB Support Basedoc

## 📋 Prérequis

### Serveur
- **VPS OVH** avec Ubuntu 24.04 LTS
- **IP** : 193.70.41.117
- **RAM** : 8GB minimum
- **CPU** : 4 vCPU minimum
- **Disque** : 75GB SSD minimum
- **Accès** : SSH root ou sudo

### DNS
Configurer l'enregistrement DNS **avant** l'installation :
```
Type: A
Nom: gagneraud.basedoc.fr
Valeur: 193.70.41.117
TTL: 300
```

⏱️ **Attendre 15-30 minutes** pour la propagation DNS

### Vérifier la propagation DNS
```bash
dig +short gagneraud.basedoc.fr
# Doit retourner : 193.70.41.117
```

### Informations nécessaires
- ✅ Clé API Claude Anthropic (commence par `sk-ant-`)
- ✅ Email administrateur
- ✅ Nom complet administrateur
- ✅ Mot de passe administrateur (min 8 caractères)

---

## 🔧 Installation

### 1. Connexion au serveur

```bash
ssh root@193.70.41.117
```

### 2. Télécharger le script d'installation

```bash
# Créer répertoire de travail
mkdir -p /root/kb_install
cd /root/kb_install

# Télécharger le script (ajuster selon votre méthode)
# Option 1: Si vous avez le fichier en local
scp install_kb_basedoc_improved.sh root@193.70.41.117:/root/kb_install/

# Option 2: Copier/coller le contenu
nano install_kb_basedoc_improved.sh
# Copier le contenu du script
# Ctrl+X, Y, Enter pour sauvegarder
```

### 3. Rendre le script exécutable

```bash
chmod +x install_kb_basedoc_improved.sh
```

### 4. Exécuter l'installation

```bash
./install_kb_basedoc_improved.sh
```

### 5. Suivre les instructions

Le script va vous demander :

1. **Clé API Claude** :
   ```
   Clé API Claude (sk-ant-...): sk-ant-api03-VOTRE_CLE_ICI
   ```

2. **Email administrateur** (défaut: dheurtebise@basedoc.fr) :
   ```
   Email admin [dheurtebise@basedoc.fr]: [Entrée ou votre email]
   ```

3. **Nom administrateur** (défaut: David Heurtebise) :
   ```
   Nom complet admin [David Heurtebise]: [Entrée ou votre nom]
   ```

4. **Mot de passe** :
   ```
   Mot de passe admin (min 8 caractères): ********
   Confirmer le mot de passe: ********
   ```

### 6. Patienter

L'installation prend environ **10-15 minutes**.

Le script va :
- ✅ Mettre à jour le système
- ✅ Installer PostgreSQL, Nginx, Python 3.12
- ✅ Configurer la base de données
- ✅ Installer les dépendances Python
- ✅ Configurer le pare-feu (UFW)
- ✅ Configurer Fail2Ban
- ✅ Configurer SSL Let's Encrypt (si DNS OK)
- ✅ Configurer les backups automatiques

---

## ✅ Vérification de l'installation

### 1. Exécuter le script de vérification

```bash
# Rendre exécutable
chmod +x verify_installation.sh

# Exécuter
./verify_installation.sh
```

Le script vérifie :
- Services actifs (PostgreSQL, Nginx, Fail2Ban)
- Base de données créée
- Fichiers de configuration
- Sécurité (pare-feu, permissions)
- Réseau (DNS, SSL)
- Packages Python installés

**Score attendu** : 90-100%

### 2. Vérifications manuelles

#### Services actifs
```bash
systemctl status postgresql
systemctl status nginx
systemctl status fail2ban
```

#### Base de données
```bash
sudo -u postgres psql -c "\l" | grep kb_basedoc
```

#### Logs
```bash
# Installation
tail -50 /var/log/kb_basedoc_install.log

# Nginx
tail -20 /var/log/nginx/kb_basedoc_error.log
```

---

## 🔐 Informations sauvegardées

Toutes les informations d'installation sont sauvegardées dans :

```
/root/kb_basedoc_install_info.txt
```

**⚠️ IMPORTANT** : Ce fichier contient des informations sensibles (mots de passe DB, clé API).

```bash
# Afficher
cat /root/kb_basedoc_install_info.txt

# Sauvegarder localement (depuis votre machine)
scp root@193.70.41.117:/root/kb_basedoc_install_info.txt .
```

---

## 📂 Structure installée

```
/var/www/kb_basedoc/
├── app/                      # Code application (à développer)
│   ├── routes/
│   ├── services/
│   ├── templates/
│   └── static/
├── storage/                  # Fichiers uploadés
│   └── procedures/
├── venv/                     # Virtual environment Python
├── migrations/               # Migrations Alembic
├── .env                      # Variables d'environnement (SENSIBLE)
├── config.py                 # Configuration Flask
├── run.py                    # Point d'entrée
├── requirements.txt          # Dépendances Python
└── gunicorn_config.py        # Configuration Gunicorn

/var/log/
├── gunicorn/                 # Logs Gunicorn
├── kb_basedoc/              # Logs application
├── nginx/                    # Logs Nginx
└── kb_basedoc_install.log   # Log installation

/var/backups/kb_basedoc/     # Backups quotidiens

/etc/
├── nginx/sites-available/kb_basedoc
├── systemd/system/kb_basedoc.service
└── cron.daily/kb_basedoc_backup
```

---

## 🔄 Prochaines étapes

L'installation a créé l'infrastructure. Il reste à :

### 1. Développer l'application (Phase 1 - MVP)
- Modèles de données (User, Procedure, Category, Tag)
- Routes Flask (auth, procedures, search)
- Templates HTML
- Logique métier

### 2. Initialiser la base de données
```bash
cd /var/www/kb_basedoc
source venv/bin/activate
flask db upgrade
```

### 3. Créer l'utilisateur admin
```bash
python3 << 'EOF'
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    admin = User(
        email='dheurtebise@basedoc.fr',
        full_name='David Heurtebise',
        is_admin=True,
        is_active=True
    )
    admin.set_password('VOTRE_MOT_DE_PASSE')
    db.session.add(admin)
    db.session.commit()
    print("✓ Admin créé")
EOF
```

### 4. Démarrer l'application
```bash
systemctl start kb_basedoc
systemctl enable kb_basedoc
```

### 5. Tester
```bash
# Vérifier que le service tourne
systemctl status kb_basedoc

# Tester l'accès
curl -I https://gagneraud.basedoc.fr
```

---

## 🛠️ Commandes utiles

### Services

```bash
# Redémarrer l'application
sudo systemctl restart kb_basedoc

# Arrêter l'application
sudo systemctl stop kb_basedoc

# Démarrer l'application
sudo systemctl start kb_basedoc

# Status de l'application
sudo systemctl status kb_basedoc

# Redémarrer Nginx
sudo systemctl restart nginx

# Tester config Nginx
sudo nginx -t
```

### Logs

```bash
# Logs application en temps réel
sudo journalctl -u kb_basedoc -f

# Logs Gunicorn
sudo tail -f /var/log/gunicorn/error.log

# Logs application
sudo tail -f /var/log/kb_basedoc/app.log

# Logs Nginx
sudo tail -f /var/log/nginx/kb_basedoc_error.log
```

### Base de données

```bash
# Se connecter à PostgreSQL
sudo -u postgres psql kb_basedoc

# Backup manuel
sudo /etc/cron.daily/kb_basedoc_backup

# Restaurer un backup
gunzip < /var/backups/kb_basedoc/db_YYYYMMDD.sql.gz | sudo -u postgres psql kb_basedoc
```

### SSL

```bash
# Renouveler les certificats manuellement
sudo certbot renew

# Tester le renouvellement
sudo certbot renew --dry-run

# Status du timer de renouvellement automatique
systemctl status certbot.timer
```

### Flask

```bash
# Shell Flask
cd /var/www/kb_basedoc
source venv/bin/activate
flask shell

# Migrations
flask db migrate -m "Description"
flask db upgrade
flask db downgrade
```

---

## ❌ Problèmes courants

### 1. SSL non configuré

**Symptôme** : Message "DNS non résolu" ou "DNS pointe vers mauvaise IP"

**Solution** :
```bash
# Vérifier DNS
dig +short gagneraud.basedoc.fr

# Si OK, configurer SSL manuellement
sudo certbot --nginx -d gagneraud.basedoc.fr
```

### 2. Service kb_basedoc ne démarre pas

**Symptôme** : `systemctl status kb_basedoc` montre "failed"

**Solution** :
```bash
# Voir les logs détaillés
sudo journalctl -u kb_basedoc -n 50

# Vérifier que l'application est développée
ls -la /var/www/kb_basedoc/app/

# Tester manuellement
cd /var/www/kb_basedoc
source venv/bin/activate
gunicorn --config gunicorn_config.py run:app
```

### 3. Erreur de permissions

**Symptôme** : "Permission denied" dans les logs

**Solution** :
```bash
# Réparer les permissions
sudo chown -R www-data:www-data /var/www/kb_basedoc
sudo chmod -R 755 /var/www/kb_basedoc
sudo chmod -R 775 /var/www/kb_basedoc/storage
sudo chmod 600 /var/www/kb_basedoc/.env
```

### 4. Erreur de connexion PostgreSQL

**Symptôme** : "FATAL: password authentication failed"

**Solution** :
```bash
# Vérifier les credentials dans .env
cat /var/www/kb_basedoc/.env | grep DATABASE_URL

# Tester la connexion
sudo -u postgres psql kb_basedoc -c "SELECT version();"
```

### 5. Port 8000 déjà utilisé

**Symptôme** : "Address already in use"

**Solution** :
```bash
# Trouver le processus
sudo lsof -i :8000

# Tuer le processus
sudo kill -9 <PID>

# Ou changer le port dans gunicorn_config.py
```

---

## 🔒 Sécurité

### Pare-feu (UFW)

```bash
# Status
sudo ufw status verbose

# Autoriser un port
sudo ufw allow PORT

# Interdire un port
sudo ufw deny PORT
```

### Fail2Ban

```bash
# Status général
sudo fail2ban-client status

# Status jail spécifique
sudo fail2ban-client status sshd

# Débannir une IP
sudo fail2ban-client set sshd unbanip IP_ADDRESS
```

### Mises à jour de sécurité automatiques

Les mises à jour de sécurité sont automatiques via `unattended-upgrades`.

```bash
# Vérifier la configuration
cat /etc/apt/apt.conf.d/50unattended-upgrades
```

---

## 📊 Monitoring

### Ressources système

```bash
# CPU et RAM
htop

# Espace disque
df -h

# Utilisation par répertoire
du -sh /var/www/kb_basedoc/*
du -sh /var/backups/kb_basedoc/*
```

### Logs d'accès

```bash
# Derniers accès
sudo tail -20 /var/log/nginx/kb_basedoc_access.log

# Erreurs récentes
sudo tail -20 /var/log/nginx/kb_basedoc_error.log

# Statistiques
sudo cat /var/log/nginx/kb_basedoc_access.log | cut -d '"' -f3 | cut -d ' ' -f2 | sort | uniq -c | sort -rn
```

---

## 🆘 Support

### Fichiers de log importants

1. `/var/log/kb_basedoc_install.log` - Log d'installation
2. `/var/log/gunicorn/error.log` - Erreurs Gunicorn
3. `/var/log/kb_basedoc/app.log` - Logs application
4. `/var/log/nginx/kb_basedoc_error.log` - Erreurs Nginx
5. `sudo journalctl -u kb_basedoc` - Logs systemd

### Informations à fournir en cas de problème

```bash
# Collecter les informations
cat > /tmp/kb_debug.txt << 'EOF'
=== SYSTEM ===
uname -a
lsb_release -a

=== SERVICES ===
systemctl status kb_basedoc
systemctl status nginx
systemctl status postgresql

=== LOGS (last 50 lines) ===
tail -50 /var/log/kb_basedoc_install.log
tail -50 /var/log/gunicorn/error.log
journalctl -u kb_basedoc -n 50

=== DISK ===
df -h

=== NETWORK ===
dig +short gagneraud.basedoc.fr
curl -I https://gagneraud.basedoc.fr
EOF

bash /tmp/kb_debug.txt > /tmp/kb_debug_output.txt 2>&1
cat /tmp/kb_debug_output.txt
```

---

## 📝 Changelog

### Version 2.0 (2024-12-11)
- ✅ Ajout validation inputs
- ✅ Ajout vérifications OS
- ✅ Ajout rollback automatique
- ✅ Fix permissions PostgreSQL 15+
- ✅ Ajout pare-feu UFW
- ✅ Ajout Fail2Ban
- ✅ Ajout backup automatique
- ✅ Ajout logging complet
- ✅ Ajout .gitignore
- ✅ Amélioration sécurité Nginx
- ✅ Ajout rate limiting

### Version 1.0 (2024-12-10)
- Installation de base

---

## 📄 Licence

© 2024 Gagneraud - Support IT
Propriétaire : Gagneraud
Usage interne uniquement
