# PayeTonKawa

![CI](https://github.com/Don-bot667/payetonkawa/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/Don-bot667/payetonkawa/branch/main/graph/badge.svg)](https://codecov.io/gh/Don-bot667/payetonkawa)

Application e-commerce de vente de café en architecture micro-services. Projet MSPR — EISI 2026.

---

## Présentation

PayeTonKawa permet de gérer la vente de café en ligne avec :
- La gestion des comptes clients (inscription, connexion)
- Un catalogue de produits avec gestion des stocks et images
- La gestion des commandes
- Une synchronisation temps réel entre les services via RabbitMQ
- Un site client et un site d'administration

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   api-clients   │     │  api-produits   │     │  api-commandes  │
│    :8000        │     │    :8001        │     │    :8002        │
│  PostgreSQL     │     │  PostgreSQL     │     │  PostgreSQL     │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                        │
         └───────────────────────┼────────────────────────┘
                                 │
                          ┌──────▼──────┐
                          │  RabbitMQ   │
                          │  :5672      │
                          └─────────────┘
```

| Service | Port | Description |
|---------|------|-------------|
| api-clients | 8000 | CRUD clients + authentification |
| api-produits | 8001 | Catalogue + stock + images |
| api-commandes | 8002 | Commandes + lignes |
| Site client (Astro) | 4321 | Frontend e-commerce |
| Site admin (Astro) | 4322 | Interface de gestion |
| RabbitMQ | 5672 / 15672 | Message broker |

---

## Lancer le projet

### Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Git

### Démarrage

```bash
git clone https://github.com/Don-bot667/payetonkawa.git
cd payetonkawa
docker compose up --build
```

### Vérifier l'état des services

```bash
docker compose ps
```

### Accès

| Interface | URL |
|-----------|-----|
| API Clients (Swagger) | http://localhost:8000/docs |
| API Produits (Swagger) | http://localhost:8001/docs |
| API Commandes (Swagger) | http://localhost:8002/docs |
| RabbitMQ Management | http://localhost:15672 (guest / guest) |

### Arrêt

```bash
# Arrêter les services
docker compose down

# Arrêter et supprimer les bases de données
docker compose down -v
```

---

## Utilisation de l'API

Toutes les routes sont protégées par le header `X-API-Key` :

```bash
# Créer un client
curl -X POST http://localhost:8000/customers/ \
  -H "X-API-Key: secret_key_123" \
  -H "Content-Type: application/json" \
  -d '{"nom": "Dupont", "prenom": "Jean", "email": "jean@example.com", "mot_de_passe": "monMdp"}'

# Lister les produits
curl http://localhost:8001/products/ \
  -H "X-API-Key: secret_key_123"

# Créer une commande
curl -X POST http://localhost:8002/orders/ \
  -H "X-API-Key: secret_key_123" \
  -H "Content-Type: application/json" \
  -d '{"client_id": 1, "lignes": [{"produit_id": 1, "quantite": 2, "prix_unitaire": 12.50}]}'
```

---

## Tests

Les tests ne nécessitent **pas** Docker (SQLite en mémoire + mocks RabbitMQ).

```bash
# api-clients (45 tests)
cd api-clients
venv/bin/pip install bcrypt==5.0.0   # première fois seulement
venv/bin/pytest tests/ --cov=app

# api-produits (46 tests)
cd api-produits
venv/bin/pytest tests/ --cov=app

# api-commandes (49 tests)
cd api-commandes
venv/bin/pytest tests/ --cov=app
```

| API | Tests | Couverture |
|-----|------:|----------:|
| api-clients | 45 | 93% |
| api-produits | 46 | 93% |
| api-commandes | 49 | 94% |

---

## Stack technique

| Technologie | Usage |
|-------------|-------|
| Python 3.12 + FastAPI | Backend APIs |
| PostgreSQL 15 | Bases de données |
| SQLAlchemy | ORM Python |
| Pydantic v2 | Validation des données |
| RabbitMQ 3 + pika | Messagerie asynchrone |
| bcrypt | Hashage des mots de passe |
| Docker + Docker Compose | Conteneurisation |
| Astro (TypeScript) | Frontends |
| pytest + pytest-cov | Tests automatisés |
| GitHub Actions | CI/CD |

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | Schéma, services, choix techniques |
| [Sécurité](docs/SECURITE.md) | API Key, bcrypt, OWASP, CORS |
| [Hébergement](docs/HEBERGEMENT.md) | VPS, Kubernetes, scaling, backup |
| [API](docs/API.md) | Tous les endpoints avec exemples curl |
| [GitFlow](docs/GITFLOW.md) | Branches, conventions de commits |
| [Conduite du changement](docs/CONDUITE_CHANGEMENT.md) | Plan de transition |

---

## Structure du projet

```
payetonkawa/
├── api-clients/          # API gestion des clients
│   ├── app/              # Code source FastAPI
│   ├── tests/            # Tests automatisés
│   └── Dockerfile
├── api-produits/         # API gestion des produits
│   ├── app/
│   ├── tests/
│   └── Dockerfile
├── api-commandes/        # API gestion des commandes
│   ├── app/
│   ├── tests/
│   └── Dockerfile
├── sitepayetonkawa/      # Frontend client (Astro)
├── gestionpayetonkawa/   # Frontend admin (Astro)
├── docs/                 # Documentation technique
├── postman/              # Collection Postman
├── .github/workflows/    # CI/CD GitHub Actions
└── docker-compose.yml    # Orchestration des services
```

---

## Auteur

**Don** — david.djinadou@advercity.fr
Projet réalisé dans le cadre du MSPR TPRE814 — EISI 2026
