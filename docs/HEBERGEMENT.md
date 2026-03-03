# Hébergement & Scaling PayeTonKawa

## Déploiement local (développement)

### Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (inclut Docker Compose)
- Git

### Lancement en une commande

```bash
git clone https://github.com/Don-bot667/payetonkawa.git
cd payetonkawa
docker compose up --build
```

Docker télécharge les images, construit les conteneurs, et démarre les 7 services automatiquement.

### Vérifier que tout tourne

```bash
docker compose ps
```

```
NAME                   STATUS          PORTS
payetonkawa-api-clients    Up (healthy)    0.0.0.0:8000->8000/tcp
payetonkawa-api-produits   Up (healthy)    0.0.0.0:8001->8000/tcp
payetonkawa-api-commandes  Up (healthy)    0.0.0.0:8002->8000/tcp
payetonkawa-rabbitmq       Up              0.0.0.0:5672->5672/tcp
```

### URLs locales

| Service | URL |
|---------|-----|
| API Clients (Swagger) | http://localhost:8000/docs |
| API Produits (Swagger) | http://localhost:8001/docs |
| API Commandes (Swagger) | http://localhost:8002/docs |
| RabbitMQ (interface web) | http://localhost:15672 (guest/guest) |
| Site client | http://localhost:4321 |
| Site admin | http://localhost:4322 |

### Arrêter et remettre à zéro

```bash
# Arrêter sans supprimer les données
docker compose down

# Arrêter ET supprimer les bases de données (reset complet)
docker compose down -v
```

---

## Options d'hébergement en production

### Option 1 — VPS (recommandé pour démarrer)

Un **VPS** (Virtual Private Server) est un serveur virtuel loué chez un hébergeur.

| Hébergeur | Config recommandée | Prix indicatif |
|-----------|-------------------|----------------|
| OVH | 4 vCPU, 8 Go RAM, 80 Go SSD | ~20€/mois |
| Scaleway | 4 vCPU, 8 Go RAM, 80 Go SSD | ~25€/mois |
| DigitalOcean | 4 vCPU, 8 Go RAM, 160 Go SSD | ~48€/mois |

**Avantages :** contrôle total, prix fixe, simple à comprendre
**Inconvénients :** maintenance manuelle, pas d'auto-scaling

**Déploiement sur VPS :**
```bash
# Sur le serveur distant
git clone https://github.com/Don-bot667/payetonkawa.git
cd payetonkawa

# Créer un fichier .env avec les vrais secrets
API_KEY=votre-cle-secrete-longue
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=motdepasse-fort

docker compose -f docker-compose.prod.yml up -d
```

---

### Option 2 — Kubernetes (scalabilité avancée)

Kubernetes (K8s) est un orchestrateur de conteneurs. Il permet de gérer automatiquement l'auto-scaling, la haute disponibilité et les redémarrages.

| Hébergeur | Service | Prix indicatif |
|-----------|---------|----------------|
| AWS | EKS (Elastic Kubernetes Service) | ~70€/mois + usage |
| Google Cloud | GKE (Google Kubernetes Engine) | ~60€/mois + usage |
| Microsoft Azure | AKS (Azure Kubernetes Service) | ~65€/mois + usage |

**Avantages :** auto-scaling, haute disponibilité, déploiements sans interruption
**Inconvénients :** complexité plus élevée, coût variable selon la charge

---

### Option 3 — PaaS (Platform as a Service)

Des plateformes qui gèrent l'infrastructure pour vous. On déploie juste le code.

| Plateforme | Avantages | Prix indicatif |
|------------|-----------|----------------|
| Railway | Très simple, supporte Docker Compose | ~5-20€/mois |
| Render | Déploiement Git automatique | ~7-25€/mois |
| Fly.io | Proche des serveurs clients, bon support Docker | ~10-30€/mois |

**Avantages :** déploiement simplifié, pas de gestion serveur
**Inconvénients :** moins de contrôle, prix peut monter avec le trafic

---

## Scaling horizontal

Le **scaling horizontal** consiste à multiplier les instances d'un service pour absorber plus de trafic.

### Exemple avec Docker Compose

```yaml
# docker-compose.prod.yml
services:
  api-produits:
    image: payetonkawa/api-produits:latest
    deploy:
      replicas: 3          # 3 instances en parallèle
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
```

### Avec un Load Balancer (Nginx)

Un **reverse proxy** distribue les requêtes entre les instances :

```
Internet
    │
    ▼
┌───────────────────┐
│   Nginx           │  ← reçoit toutes les requêtes
│   (load balancer) │
└──────┬────────────┘
       │  distribue aléatoirement
   ┌───┴────────────────────────┐
   ▼           ▼               ▼
api-produits  api-produits  api-produits
instance 1    instance 2    instance 3
```

Configuration Nginx :
```nginx
upstream api_produits {
    server api-produits-1:8000;
    server api-produits-2:8000;
    server api-produits-3:8000;
}

server {
    listen 80;
    location /products/ {
        proxy_pass http://api_produits;
    }
}
```

### Quelle API scaler en priorité ?

| API | Charge attendue | Priorité scaling |
|-----|----------------|-----------------|
| api-produits | Forte (catalogue, images) | Haute |
| api-clients | Moyenne (connexions) | Moyenne |
| api-commandes | Faible (achats) | Faible |

---

## Base de données en production

### Scaling vertical

La façon la plus simple : augmenter les ressources du serveur PostgreSQL (plus de RAM, plus de CPU, SSD NVMe).

### Scaling horizontal

Pour les très forts volumes :

- **Read replicas** : une base principale en écriture, plusieurs copies en lecture seule
- **PgBouncer** : un pool de connexions évite d'ouvrir trop de connexions simultanées à PostgreSQL
- **Partitionnement** : diviser les grandes tables (ex : commandes par année)

### Sauvegardes automatiques

```bash
# Sauvegarde quotidienne automatique (cron job)
0 2 * * * pg_dump -U faouz clients_db > /backups/clients_$(date +%Y%m%d).sql

# Restauration
psql -U faouz clients_db < /backups/clients_20260302.sql
```

---

## Monitoring en production

### Outils recommandés

| Outil | Rôle |
|-------|------|
| **Prometheus** | Collecte de métriques (CPU, mémoire, requêtes/s) |
| **Grafana** | Tableaux de bord visuels à partir des métriques |
| **Loki** | Centralisation des logs de tous les services |
| **AlertManager** | Alertes email/Slack quand une métrique dépasse un seuil |

### Les endpoints `/health` déjà en place

Les 3 APIs exposent déjà un endpoint `/health` utilisable par les outils de monitoring :

```bash
curl http://localhost:8000/health
# {"status": "healthy", "service": "api-clients", "database": "connected", ...}
```

Docker Compose utilise déjà ces endpoints pour vérifier automatiquement que les services fonctionnent (healthcheck toutes les 30 secondes).

---

## Variables d'environnement à configurer en production

| Variable | Description | Exemple prod |
|----------|-------------|--------------|
| `API_KEY` | Clé d'authentification | Clé aléatoire de 64 caractères |
| `DATABASE_URL` | Connexion PostgreSQL | `postgresql://user:pass@db-host/clients_db` |
| `RABBITMQ_URL` | Connexion RabbitMQ | `amqp://admin:pass@rabbitmq-host:5672/` |
| `ALLOWED_ORIGINS` | Domaines CORS autorisés | `https://payetonkawa.fr` |

Stocker ces variables dans un **gestionnaire de secrets** (HashiCorp Vault, AWS Secrets Manager, ou un simple fichier `.env` non commité).
