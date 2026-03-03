**J'ai trouvé le problème !** 🔍

Dans `sitepayetonkawa/src/lib/api.ts`, les URLs sont en **localhost** :

```ts
const API_CLIENTS = "http://localhost:8000";
const API_PRODUITS = "http://localhost:8001";
const API_COMMANDES = "http://localhost:8002";
```

En production, le navigateur de l'utilisateur essaie d'accéder à `localhost` sur **sa propre machine**, pas sur ton serveur !

---

## 🎫 TICKET : Corriger les URLs des APIs pour la production

### Fichiers à modifier (2 fichiers)

---

### 1️⃣ `sitepayetonkawa/src/lib/api.ts`

**Remplacer les 3 premières lignes :**

```ts
// Configuration des APIs
const API_CLIENTS = "https://api.payetonkawa.ouzfa.com";
const API_PRODUITS = "https://api.payetonkawa.ouzfa.com";
const API_COMMANDES = "https://api.payetonkawa.ouzfa.com";
```

---

### 2️⃣ `gestionpayetonkawa/src/lib/api.ts`

**Même chose** — remplacer les URLs localhost par :

```ts
const API_CLIENTS = "https://api.payetonkawa.ouzfa.com";
const API_PRODUITS = "https://api.payetonkawa.ouzfa.com";
const API_COMMANDES = "https://api.payetonkawa.ouzfa.com";
```

---

### 3️⃣ Mettre à jour Nginx pour router toutes les routes API

Actuellement Nginx route `/clients`, `/products`, `/orders` mais le code appelle `/customers/`, `/products/`, `/orders/`.

```bash
sudo nano /etc/nginx/sites-available/payetonkawa
```

Dans le bloc `api.payetonkawa.ouzfa.com`, **remplace** par :

```nginx
server {
    server_name api.payetonkawa.ouzfa.com;

    location /customers {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /products {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /orders {
        proxy_pass http://localhost:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://localhost:8000/openapi.json;
        proxy_set_header Host $host;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/payetonkawa.ouzfa.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/payetonkawa.ouzfa.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}
```
