# 🎫 TICKET : Corriger CORS pour la production

## 📋 Fichier à modifier

### `docker-compose.yml`

Cherche les 3 occurrences de `ALLOWED_ORIGINS` et remplace-les **toutes** par :

```yaml
ALLOWED_ORIGINS: "https://payetonkawa.ouzfa.com,https://admin.payetonkawa.ouzfa.com,http://localhost:3000,http://localhost:4321,http://localhost:4322"
```

---

## 📍 Les 3 endroits à modifier

### 1️⃣ Dans `api-clients` (ligne ~20)
```yaml
  api-clients:
    build: ./api-clients
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://faouz:faouz2020@db-clients:5432/clients_db
      API_KEY: secret_key_123
      ALLOWED_ORIGINS: "https://payetonkawa.ouzfa.com,https://admin.payetonkawa.ouzfa.com,http://localhost:3000,http://localhost:4321,http://localhost:4322"
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
```

### 2️⃣ Dans `api-produits` (ligne ~35)
```yaml
  api-produits:
    build: ./api-produits
    ports:
      - "8001:8000"
    environment:
      DATABASE_URL: postgresql://faouz:faouz2020@db-produits:5432/produits_db
      API_KEY: secret_key_123
      ALLOWED_ORIGINS: "https://payetonkawa.ouzfa.com,https://admin.payetonkawa.ouzfa.com,http://localhost:3000,http://localhost:4321,http://localhost:4322"
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
```

### 3️⃣ Dans `api-commandes` (ligne ~50)
```yaml
  api-commandes:
    build: ./api-commandes
    ports:
      - "8002:8000"
    environment:
      DATABASE_URL: postgresql://faouz:faouz2020@db-commandes:5432/commandes_db
      API_KEY: secret_key_123
      ALLOWED_ORIGINS: "https://payetonkawa.ouzfa.com,https://admin.payetonkawa.ouzfa.com,http://localhost:3000,http://localhost:4321,http://localhost:4322"
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
```

---

## ✅ Checklist

- [ ] Modifier `ALLOWED_ORIGINS` dans `api-clients`
- [ ] Modifier `ALLOWED_ORIGINS` dans `api-produits`
- [ ] Modifier `ALLOWED_ORIGINS` dans `api-commandes`
- [ ] `git add . && git commit -m "fix: CORS for production domains" && git push`

