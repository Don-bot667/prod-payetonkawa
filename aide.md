Pour me Déployer après modification du code

## Sur ton PC (après modification)

```bash
git add .
git commit -m "description de ta modification"
git push origin main
```

---




## Sur le serveur


je n'oublie pas de me connecter a mon user deploy
le mdp : Ouzfa

```bash
ssh deploy@161.35.78.10
cd ~/prod-payetonkawa
git pull origin main
docker compose down
docker compose up -d --build
```

---















# 🔐 Accès PayeTonKawa

## 🌐 Sites Web

| Service | URL | Login |
|---------|-----|-------|
| **Site client** | https://payetonkawa.ouzfa.com | - |
| **Admin** | https://admin.payetonkawa.ouzfa.com | - |
| **API Docs** | https://api.payetonkawa.ouzfa.com/docs | - |

---

## 🛠️ Outils de gestion

| Service | URL | Email / User | Password |
|---------|-----|--------------|----------|
| **pgAdmin** | http://161.35.78.10:5050 | `faouz@gmail.com` | `faouz` |
| **RabbitMQ** | http://161.35.78.10:15672 | `guest` | `guest` |

---

## 🗄️ Bases de données PostgreSQL

| Base | Host | Port | User | Password | Database |
|------|------|------|------|----------|----------|
| Clients | 161.35.78.10 | 5436 | `faouz` | `faouz2020` | `clients_db` |
| Produits | 161.35.78.10 | 5437 | `faouz` | `faouz2020` | `produits_db` |
| Commandes | 161.35.78.10 | 5438 | `faouz` | `faouz2020` | `commandes_db` |

**Depuis pgAdmin, utilise :**
- Host : `db-clients` / `db-produits` / `db-commandes`
- Port : `5432`

---

## 🖥️ Serveur SSH

| Host | User | Password |
|------|------|----------|
| 161.35.78.10 | `root` | *(ton mot de passe Droplet)* |
| 161.35.78.10 | `deploy` | *(mot de passe créé lors de `adduser`)* |

```bash
ssh deploy@161.35.78.10
```

---

## 🔑 API Key

| Clé | Valeur |
|-----|--------|
| **X-API-Key** | `secret_key_123` |

---

## 📦 GitHub

| Repo | URL |
|------|-----|
| Production | https://github.com/Don-bot667/prod-payetonkawa |

---

⚠️ **Note sécurité** : En production réelle, change tous ces mots de passe par des valeurs plus sécurisées !