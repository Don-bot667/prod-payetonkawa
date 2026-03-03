# Sécurité PayeTonKawa

## Vue d'ensemble

La sécurité est appliquée à plusieurs niveaux : authentification des appels API, protection des mots de passe, validation des données entrantes, configuration CORS, et gestion des secrets.

---

## 1. Authentification par API Key

### Principe

Toutes les routes métier des 3 APIs sont protégées par une **clé API** transmise dans le header HTTP `X-API-Key`.

```bash
# Requête sans clé → 401 Unauthorized
curl http://localhost:8000/customers/

# Requête avec mauvaise clé → 403 Forbidden
curl -H "X-API-Key: mauvaise-cle" http://localhost:8000/customers/

# Requête avec bonne clé → 200 OK
curl -H "X-API-Key: secret_key_123" http://localhost:8000/customers/
```

### Implémentation

La vérification est centralisée dans `app/auth.py` de chaque API :

```python
async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key is None:
        raise HTTPException(status_code=401, detail="API Key manquante")
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="API Key invalide")
    return api_key
```

Elle est appliquée à **toutes les routes** du routeur via `dependencies=[Depends(verify_api_key)]`.

### Endpoints publics (sans authentification)

| Endpoint | Justification |
|----------|---------------|
| `GET /` | Message de bienvenue inoffensif |
| `GET /health` | Monitoring infra (utilisé par Docker healthcheck) |
| `GET /docs` | Documentation Swagger (à protéger en production) |

### La clé API en production

La clé est stockée dans une variable d'environnement, jamais en dur dans le code :

```yaml
# docker-compose.yml
environment:
  API_KEY: secret_key_123   # À remplacer par une vraie clé aléatoire en prod
```

En production, utiliser une clé longue et aléatoire :
```bash
# Générer une clé sécurisée
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 2. Protection des mots de passe

### Hachage avec bcrypt

Les mots de passe ne sont **jamais stockés en clair** en base de données. Ils sont hachés avec **bcrypt** avant insertion :

```python
import bcrypt

def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(
        plain_password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )
```

**Pourquoi bcrypt ?**
- Intègre un **sel aléatoire** (salt) automatique → deux fois le même mot de passe donnent deux hashes différents
- **Lent intentionnellement** → rend les attaques par force brute très coûteuses
- Algorithme éprouvé, utilisé depuis 1999, toujours recommandé

### Le mot de passe n'est jamais renvoyé

Le schéma de réponse `ClientResponse` ne contient pas le champ `mot_de_passe`. Même si quelqu'un intercepte la réponse de l'API, il ne verra jamais le hash.

---

## 3. Validation des données entrantes (Pydantic)

Toutes les données envoyées à l'API sont validées automatiquement via Pydantic avant d'atteindre la base de données.

### Exemples de règles appliquées

```python
class ClientCreate(BaseModel):
    nom: str = Field(..., min_length=2, max_length=100)
    email: EmailStr                                          # format email valide
    telephone: Optional[str] = Field(None, pattern=r'^0[1-9][0-9]{8}$')  # format FR
    mot_de_passe: str = Field(..., min_length=4, max_length=100)

class ProduitCreate(BaseModel):
    prix: float = Field(..., gt=0)    # prix strictement positif
    stock: int = Field(0, ge=0)      # stock >= 0
```

Si une règle est violée, FastAPI retourne automatiquement une **erreur 422** avec le détail du champ invalide. Aucun code non valide n'atteint jamais la base de données.

### Protection contre l'injection SQL

L'ORM SQLAlchemy utilise des **requêtes paramétrées** systématiquement. Le code n'écrit jamais de SQL manuellement avec des f-strings. L'injection SQL est donc impossible par construction.

```python
# Sécurisé : SQLAlchemy gère la mise en forme
db.query(Client).filter(Client.email == email).first()

# JAMAIS ça (vulnérable à l'injection) :
# db.execute(f"SELECT * FROM clients WHERE email = '{email}'")
```

---

## 4. CORS (Cross-Origin Resource Sharing)

Le CORS contrôle quels domaines peuvent appeler les APIs depuis un navigateur.

### Configuration actuelle

```python
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:4321"
).split(",")
```

Seuls les frontends déclarés peuvent appeler les APIs. Une requête depuis un domaine non autorisé sera bloquée par le navigateur.

### En production

Remplacer par les vrais domaines :
```
ALLOWED_ORIGINS=https://payetonkawa.fr,https://gestion.payetonkawa.fr
```

---

## 5. Gestion des secrets

### Règle absolue : aucun secret dans le code

Tous les secrets sont passés en **variables d'environnement** :

| Variable | Usage | Exemple |
|----------|-------|---------|
| `API_KEY` | Clé d'authentification des APIs | `secret_key_123` |
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql://user:pass@host/db` |
| `RABBITMQ_URL` | URL de connexion RabbitMQ | `amqp://guest:guest@rabbitmq:5672/` |

### Valeur par défaut sécurisée

Si la variable d'environnement n'est pas définie, une valeur par défaut explicitement marquée est utilisée :

```python
API_KEY = os.getenv("API_KEY", "dev-key-change-in-prod")
```

Le nom `dev-key-change-in-prod` est un signal clair que cette valeur ne doit pas aller en production.

### Ne jamais commiter

Ajouter au `.gitignore` :
```
.env
.env.local
.env.production
```

---

## 6. OWASP Top 10 — Mesures appliquées

| Risque OWASP | Mesure dans PayeTonKawa |
|--------------|------------------------|
| **A01 — Broken Access Control** | API Key obligatoire sur toutes les routes métier |
| **A02 — Cryptographic Failures** | Mots de passe hachés bcrypt, pas de données sensibles en clair |
| **A03 — Injection** | ORM SQLAlchemy (requêtes paramétrées), validation Pydantic |
| **A04 — Insecure Design** | Architecture micro-services, principe du moindre privilège |
| **A05 — Security Misconfiguration** | CORS restrictif, secrets en variables d'environnement |
| **A07 — Auth Failures** | Distinction 401 (clé absente) / 403 (clé invalide) |
| **A08 — Data Integrity Failures** | Validation stricte des types et formats en entrée |
| **A09 — Security Logging** | Logs JSON structurés avec `request_id`, niveau ERROR sur les échecs |

---

## 7. Logging de sécurité

Les événements importants sont tracés dans les logs :

```json
{"level": "ERROR", "message": "Healthcheck DB failed: ...", "service": "api-clients"}
{"level": "INFO",  "message": "Client supprime: id=42",     "request_id": "a1b2c3d4"}
{"level": "INFO",  "message": "Request completed",          "status_code": 403, "path": "/customers/"}
```

Chaque requête HTTP reçoit un identifiant unique (`X-Request-ID`) pour pouvoir la retrouver facilement dans les logs.

---

## 8. Recommandations pour la production

1. **HTTPS obligatoire** — utiliser un reverse proxy (Nginx) avec un certificat TLS (Let's Encrypt)
2. **Rotation des clés API** — changer régulièrement la valeur de `API_KEY`
3. **Rate limiting** — limiter le nombre de requêtes par IP pour éviter le brute force
4. **Protéger `/docs`** — désactiver ou restreindre l'accès à la documentation Swagger en prod
5. **Backup régulier** — sauvegarder les bases PostgreSQL quotidiennement
6. **Mise à jour des dépendances** — surveiller les CVE sur les librairies utilisées
