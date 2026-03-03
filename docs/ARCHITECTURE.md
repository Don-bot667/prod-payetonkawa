# Architecture PayeTonKawa

## Vue d'ensemble

PayeTonKawa est une application e-commerce spécialisée dans la vente de café, construite sur une architecture **micro-services**. Au lieu d'une seule grosse application, le projet est découpé en 3 APIs indépendantes qui communiquent entre elles via un message broker (RabbitMQ).

---

## Schéma général

```
┌──────────────────────────────────────────────────────────────────┐
│                         NAVIGATEURS                              │
│   ┌─────────────────────┐        ┌─────────────────────┐        │
│   │   Site client        │        │   Site admin         │       │
│   │   (Astro - :4321)    │        │   (Astro - :4322)    │       │
│   └──────────┬──────────┘        └──────────┬──────────┘        │
└──────────────┼────────────────────────────────┼──────────────────┘
               │  requêtes HTTP                 │  requêtes HTTP
               ▼                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                    COUCHE APIS (FastAPI)                          │
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   api-clients   │  │  api-produits   │  │  api-commandes  │  │
│  │    port 8000    │  │   port 8001     │  │   port 8002     │  │
│  │                 │  │                 │  │                 │  │
│  │  POST /login    │  │  POST /image    │  │  GET /client/id │  │
│  │  CRUD clients   │  │  CRUD produits  │  │  CRUD commandes │  │
│  │  GET /health    │  │  GET /health    │  │  GET /health    │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
│           │                    │                     │           │
│  ┌────────▼────────┐  ┌────────▼────────┐  ┌────────▼────────┐  │
│  │  PostgreSQL     │  │  PostgreSQL     │  │  PostgreSQL     │  │
│  │  clients_db     │  │  produits_db    │  │  commandes_db   │  │
│  │  port 5436      │  │  port 5437      │  │  port 5438      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
               │  publish                        │  consume
               ▼                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                         RABBITMQ                                  │
│                      port 5672 (AMQP)                            │
│                      port 15672 (interface web)                  │
│                                                                   │
│   Exchange : payetonkawa (type topic)                            │
│                                                                   │
│   client.*  ──────────────────────────────────► api-commandes   │
│   produit.* ──────────────────────────────────► api-commandes   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Services

| Service | Port | Base de données | Rôle |
|---------|------|-----------------|------|
| api-clients | 8000 | clients_db (5436) | CRUD clients + authentification |
| api-produits | 8001 | produits_db (5437) | Catalogue + gestion stock + images |
| api-commandes | 8002 | commandes_db (5438) | Commandes + lignes de commande |
| site client | 4321 | — | Frontend e-commerce (Astro) |
| site admin | 4322 | — | Frontend gestion (Astro) |
| RabbitMQ | 5672 / 15672 | — | Messagerie asynchrone |

Chaque API a **sa propre base de données**. C'est le principe d'isolation des micro-services : aucune API ne lit directement dans la base d'une autre.

---

## Communication inter-services (RabbitMQ)

Les services ne s'appellent pas directement. Quand un événement se produit, l'API publie un **message** sur RabbitMQ. Les autres APIs abonnées reçoivent ce message et réagissent.

### Événements publiés

| Service émetteur | Routing key | Déclencheur |
|------------------|-------------|-------------|
| api-clients | `client.created` | Nouveau client créé |
| api-clients | `client.updated` | Client modifié |
| api-clients | `client.deleted` | Client supprimé |
| api-produits | `produit.created` | Nouveau produit créé |
| api-produits | `produit.updated` | Produit modifié |
| api-produits | `produit.deleted` | Produit supprimé |
| api-produits | `produit.stock_low` | Stock passe sous 10 unités |
| api-commandes | `commande.created` | Nouvelle commande |
| api-commandes | `commande.updated` | Statut de commande modifié |
| api-commandes | `commande.deleted` | Commande supprimée |

### Abonnements

| Service abonné | Écoute | Action déclenchée |
|----------------|--------|-------------------|
| api-commandes | `client.deleted` | Marque toutes ses commandes comme `client_supprime` |
| api-commandes | `produit.deleted` | Journalise la suppression du produit |

### Exemple de flux complet

```
Utilisateur supprime un client via le site admin
         │
         ▼
DELETE /customers/42  ──► api-clients
         │
         ▼  supprime en base + publie :
RabbitMQ ◄── routing_key="client.deleted", body={"client_id": 42}
         │
         ▼  api-commandes reçoit le message :
callback_client_deleted()
         │
         ▼  cherche toutes les commandes du client 42 et les marque :
commandes.statut = "client_supprime"
```

---

## Stack technique

### Backend : Python 3.12 + FastAPI

**Pourquoi FastAPI ?**
- C'est l'un des frameworks Python les plus rapides (basé sur Starlette et Uvicorn)
- Génère automatiquement une documentation interactive Swagger (`/docs`)
- La validation des données est automatique grâce à Pydantic (schemas)
- Support natif de l'asynchrone
- Syntaxe claire et concise

**Pourquoi Python ?**
- Langage maîtrisé par l'équipe
- Riche écosystème pour le web (FastAPI, SQLAlchemy, pika...)
- Lecture facile du code pour la maintenance

### Base de données : PostgreSQL 15

**Pourquoi PostgreSQL ?**
- **ACID** : les transactions sont sûres (pas de données corrompues)
- **Intégrité** : contraintes clé étrangère, unicité (ex : email unique)
- **Performance** : indexation, requêtes complexes optimisées
- **Scalabilité** : supporte les réplications, le partitioning
- **Standard** : très utilisé en production, large communauté

**Pourquoi une base par service ?**
Isolation complète : si la base des produits est en maintenance, les clients peuvent toujours se connecter. Chaque service peut aussi évoluer son schéma indépendamment.

### Message Broker : RabbitMQ

**Pourquoi RabbitMQ ?**
- **Asynchrone** : l'API n'attend pas que l'autre service réponde
- **Fiabilité** : les messages sont persistés (survivent à un redémarrage)
- **Acknowledgment** : si le traitement échoue, le message est remis en file
- **Routing flexible** : avec les exchanges de type `topic`, on peut choisir précisément qui reçoit quoi
- **Interface web** : monitoring visuel sur le port 15672

### Conteneurisation : Docker + Docker Compose

Chaque service tourne dans son propre conteneur Docker. Docker Compose orchestre le tout : un seul `docker compose up` lance les 7 services (3 APIs + 3 bases + RabbitMQ).

**Avantages :**
- Environnement identique en développement et production
- Isolation des processus
- Redémarrage automatique en cas de crash

### Frontend : Astro (TypeScript)

Deux frontends distincts :
- **site client** (`sitepayetonkawa/`) : navigation produits, panier, compte
- **site admin** (`gestionpayetonkawa/`) : gestion clients, produits, commandes

Astro génère des pages statiques avec des composants dynamiques, ce qui donne de bonnes performances de chargement.

---

## Sécurité

Toutes les routes des APIs (sauf `/`, `/health`, `/docs`) sont protégées par une **clé API** transmise dans le header `X-API-Key`.

```
Client ──── X-API-Key: secret_key_123 ────► API
                                            │
                                       verify_api_key()
                                            │
                              ┌─────────────┴─────────────┐
                              │                           │
                         clé correcte               clé manquante/fausse
                              │                           │
                         200 OK                    401 / 403 Forbidden
```

Pour les mots de passe clients, ils sont **hashés avec bcrypt** avant stockage. Le hash original n'est jamais récupérable.

---

## Tests

Chaque API possède sa suite de tests automatisés (dans `tests/`) :

| API | Tests | Couverture |
|-----|------:|----------:|
| api-clients | 45 | 93% |
| api-produits | 46 | 93% |
| api-commandes | 49 | 94% |

Les tests utilisent SQLite en mémoire (pas besoin de Docker) et des mocks pour RabbitMQ.

---

## Monitoring

Chaque API expose un endpoint `/health` qui vérifie la connexion à la base de données et retourne un JSON standardisé :

```json
{
  "status": "healthy",
  "service": "api-clients",
  "database": "connected",
  "timestamp": "2026-03-02T10:00:00+00:00",
  "version": "1.0.0"
}
```

Les logs sont en format JSON structuré avec horodatage, niveau, module, et un identifiant de requête unique (`request_id`) pour tracer chaque appel HTTP.
