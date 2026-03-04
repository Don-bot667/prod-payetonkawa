# Documentation API PayeTonKawa

## Authentification

Toutes les routes (sauf `/`, `/health`, `/docs`) nécessitent le header `X-API-Key`.

```bash
X-API-Key: secret_key_123
```

| Code | Signification |
|------|---------------|
| 401 | Header `X-API-Key` absent |
| 403 | Clé incorrecte |
| 422 | Données invalides (validation Pydantic) |

La documentation Swagger interactive est disponible sur chaque API :
- http://localhost:8000/docs (clients)
- http://localhost:8001/docs (produits)
- http://localhost:8002/docs (commandes)

---

## API Clients — port 8000

### GET /
Retourne un message de bienvenue. Pas d'authentification requise.

```bash
curl http://localhost:8000/
# {"message": "Bienvenue sur l'API Clients de PayeTonKawa"}
```

---

### GET /health
Vérifie l'état de l'API et de la base de données. Pas d'authentification requise.

```bash
curl http://localhost:8000/health
```
```json
{
  "status": "healthy",
  "service": "api-clients",
  "database": "connected",
  "timestamp": "2026-03-02T10:00:00+00:00",
  "version": "1.0.0"
}
```

---

### POST /customers/
Crée un nouveau client.

**Body JSON :**
| Champ | Type | Requis | Contraintes |
|-------|------|--------|-------------|
| `nom` | string | Oui | 2–100 caractères |
| `prenom` | string | Oui | 2–100 caractères |
| `email` | string | Oui | Format email valide, unique |
| `mot_de_passe` | string | Oui | 4–100 caractères |
| `telephone` | string | Non | Format français `0XXXXXXXXX` |
| `adresse` | string | Non | Max 200 caractères |

```bash
curl -X POST http://localhost:8000/customers/ \
  -H "X-API-Key: secret_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Dupont",
    "prenom": "Jean",
    "email": "jean.dupont@example.com",
    "mot_de_passe": "monMdp123",
    "telephone": "0612345678",
    "adresse": "12 rue de la Paix, Paris 75001"
  }'
```
```json
{
  "id": 1,
  "nom": "Dupont",
  "prenom": "Jean",
  "email": "jean.dupont@example.com",
  "telephone": "0612345678",
  "adresse": "12 rue de la Paix, Paris 75001",
  "actif": true,
  "created_at": "2026-03-02T10:00:00"
}
```
> Le `mot_de_passe` n'est jamais renvoyé dans la réponse.

---

### POST /customers/login
Authentifie un client par email et mot de passe.

```bash
curl -X POST http://localhost:8000/customers/login \
  -H "X-API-Key: secret_key_123" \
  -H "Content-Type: application/json" \
  -d '{"email": "jean.dupont@example.com", "mot_de_passe": "monMdp123"}'
```
```json
{"id": 1, "nom": "Dupont", "prenom": "Jean", "email": "jean.dupont@example.com", ...}
```
Retourne **401** si email ou mot de passe incorrect.

---

### GET /customers/
Liste tous les clients. Supporte la pagination.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `skip` | int | 0 | Nombre de résultats à ignorer |
| `limit` | int | 100 | Nombre maximum de résultats |

```bash
curl "http://localhost:8000/customers/?skip=0&limit=20" \
  -H "X-API-Key: secret_key_123"
```

---

### GET /customers/{id}
Retourne un client par son identifiant.

```bash
curl http://localhost:8000/customers/1 \
  -H "X-API-Key: secret_key_123"
```
Retourne **404** si le client n'existe pas.

---

### PUT /customers/{id}
Modifie un client existant. Seuls les champs envoyés sont modifiés.

```bash
curl -X PUT http://localhost:8000/customers/1 \
  -H "X-API-Key: secret_key_123" \
  -H "Content-Type: application/json" \
  -d '{"adresse": "99 avenue des Champs, Lyon 69001"}'
```

---

### DELETE /customers/{id}
Supprime un client. Retourne **204** (pas de contenu) en cas de succès.

```bash
curl -X DELETE http://localhost:8000/customers/1 \
  -H "X-API-Key: secret_key_123"
```

---

## API Produits — port 8001

### GET /products/uploads/{filename}
Retourne l'image d'un produit. **Pas d'authentification requise.**

```bash
curl http://localhost:8001/products/uploads/produit_1.jpg
# Retourne le fichier image directement
```
Retourne **404** si l'image n'existe pas.

---

### GET /health
```bash
curl http://localhost:8001/health
# {"status": "healthy", "service": "api-produits", ...}
```

---

### POST /products/
Crée un nouveau produit.

| Champ | Type | Requis | Contraintes |
|-------|------|--------|-------------|
| `nom` | string | Oui | 2–200 caractères |
| `prix` | float | Oui | Strictement > 0 |
| `description` | string | Non | Max 500 caractères |
| `stock` | int | Non | >= 0 (défaut : 0) |
| `origine` | string | Non | Max 100 caractères |
| `poids_kg` | float | Non | > 0 (défaut : 1.0) |

```bash
curl -X POST http://localhost:8001/products/ \
  -H "X-API-Key: secret_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Café Burkina Faso",
    "description": "Café fruité aux notes de myrtille",
    "prix": 12.50,
    "stock": 100,
    "origine": "Burkina Faso",
    "poids_kg": 0.25
  }'
```
```json
{
  "id": 1,
  "nom": "Café Burkina Faso",
  "description": "Café fruité aux notes de myrtille",
  "prix": 12.5,
  "stock": 100,
  "origine": "Burkina Faso",
  "poids_kg": 0.25,
  "image_url": null,
  "actif": true,
  "date_creation": "2026-03-02T10:00:00",
  "date_modification": "2026-03-02T10:00:00"
}
```

---

### GET /products/
Liste tous les produits.

```bash
curl "http://localhost:8001/products/?skip=0&limit=50" \
  -H "X-API-Key: secret_key_123"
```

---

### GET /products/{id}
Retourne un produit par son identifiant.

```bash
curl http://localhost:8001/products/1 \
  -H "X-API-Key: secret_key_123"
```

---

### PUT /products/{id}
Modifie un produit existant (champs partiels acceptés).

```bash
# Mettre à jour le stock et le prix
curl -X PUT http://localhost:8001/products/1 \
  -H "X-API-Key: secret_key_123" \
  -H "Content-Type: application/json" \
  -d '{"stock": 80, "prix": 13.00}'
```
> Si le stock passe sous 10 unités, un événement `produit.stock_low` est automatiquement publié sur RabbitMQ.

---

### POST /products/{id}/image
Upload d'une image pour un produit.

**Formats acceptés :** jpg, jpeg, png, webp

```bash
curl -X POST http://localhost:8001/products/1/image \
  -H "X-API-Key: secret_key_123" \
  -F "file=@/chemin/vers/photo.jpg"
```
```json
{"id": 1, "nom": "Café Burkina Faso", ..., "image_url": "/uploads/produit_1.jpg"}
```

---

### DELETE /products/{id}
Supprime un produit. Retourne **204** en cas de succès.

```bash
curl -X DELETE http://localhost:8001/products/1 \
  -H "X-API-Key: secret_key_123"
```

---

## API Commandes — port 8002

### GET /health
```bash
curl http://localhost:8002/health
# {"status": "healthy", "service": "api-commandes", ...}
```

---

### POST /orders/
Crée une nouvelle commande avec ses lignes. Le total est calculé automatiquement.

| Champ | Type | Requis | Contraintes |
|-------|------|--------|-------------|
| `client_id` | int | Oui | > 0 |
| `lignes` | array | Oui | Au moins 1 ligne |
| `lignes[].produit_id` | int | Oui | > 0 |
| `lignes[].quantite` | int | Non | >= 1 (défaut : 1) |
| `lignes[].prix_unitaire` | float | Oui | > 0 |

```bash
curl -X POST http://localhost:8002/orders/ \
  -H "X-API-Key: secret_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "lignes": [
      {"produit_id": 1, "quantite": 2, "prix_unitaire": 12.50},
      {"produit_id": 3, "quantite": 1, "prix_unitaire": 8.00}
    ]
  }'
```
```json
{
  "id": 1,
  "client_id": 1,
  "statut": "en_attente",
  "total": 33.0,
  "date_commande": "2026-03-02T10:00:00",
  "date_modification": "2026-03-02T10:00:00",
  "lignes": [
    {"id": 1, "commande_id": 1, "produit_id": 1, "quantite": 2, "prix_unitaire": 12.5},
    {"id": 2, "commande_id": 1, "produit_id": 3, "quantite": 1, "prix_unitaire": 8.0}
  ]
}
```

---

### GET /orders/
Liste toutes les commandes.

```bash
curl "http://localhost:8002/orders/?skip=0&limit=50" \
  -H "X-API-Key: secret_key_123"
```

---

### GET /orders/{id}
Retourne une commande avec ses lignes.

```bash
curl http://localhost:8002/orders/1 \
  -H "X-API-Key: secret_key_123"
```

---

### GET /orders/client/{client_id}
Retourne toutes les commandes d'un client donné.

```bash
curl http://localhost:8002/orders/client/1 \
  -H "X-API-Key: secret_key_123"
```

---

### PUT /orders/{id}
Modifie le statut d'une commande.

**Statuts valides :** `en_attente` → `validee` → `expediee` → `livree`
(ou `client_supprime` si le client a été supprimé via RabbitMQ)

```bash
curl -X PUT http://localhost:8002/orders/1 \
  -H "X-API-Key: secret_key_123" \
  -H "Content-Type: application/json" \
  -d '{"statut": "validee"}'
```

---

### DELETE /orders/{id}
Supprime une commande et toutes ses lignes (CASCADE). Retourne **204**.

```bash
curl -X DELETE http://localhost:8002/orders/1 \
  -H "X-API-Key: secret_key_123"
```

---

## Codes de réponse HTTP

| Code | Signification |
|------|---------------|
| 200 | Succès (GET, PUT) |
| 201 | Créé avec succès (POST) |
| 204 | Supprimé avec succès (DELETE, pas de contenu) |
| 401 | Header `X-API-Key` absent |
| 403 | Clé API incorrecte |
| 404 | Ressource introuvable |
| 422 | Données invalides (détail des erreurs dans le body) |
| 500 | Erreur interne serveur |
