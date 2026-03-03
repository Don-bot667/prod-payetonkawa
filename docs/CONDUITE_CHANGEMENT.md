# Plan de Conduite du Changement — PayeTonKawa

## Contexte

L'entreprise PayeTonKawa, spécialisée dans la vente de café, a décidé de moderniser son système d'information. Ce projet représente un double changement :

1. **Changement technique** : passage d'une application monolithique à une architecture micro-services
2. **Changement organisationnel** : adoption de la méthodologie Agile (Scrum) en remplacement du cycle en V

Ce document décrit comment accompagner les équipes et les parties prenantes tout au long de cette transition pour maximiser les chances de succès et minimiser les résistances.

---

## 1. Analyse des changements

### Changements techniques

| Situation actuelle (Avant) | Nouvelle situation (Après) |
|---------------------------|---------------------------|
| Application monolithique unique | 3 micro-services indépendants (clients, produits, commandes) |
| Base de données unique partagée | 1 base de données dédiée par service |
| Communication directe entre modules | Communication asynchrone via RabbitMQ |
| Déploiement manuel (FTP, copie de fichiers) | CI/CD automatisé avec GitHub Actions |
| Pas de tests automatisés | 140 tests unitaires, couverture ~93% |
| Logs texte bruts | Logs JSON structurés avec identifiant de requête |
| Pas de monitoring | Endpoint `/health` sur chaque service |

### Changements organisationnels

| Situation actuelle (Avant) | Nouvelle situation (Après) |
|---------------------------|---------------------------|
| Cycle en V (cahier des charges figé) | Méthodologie Agile — Scrum |
| 1 seule équipe de développement | 3 équipes spécialisées (1 par service) |
| Développeurs sollicités directement | Demandes canalisées via le Product Owner |
| Réunions de suivi peu fréquentes | Daily stand-up (15 min/jour) + Sprint review bi-hebdo |
| Déploiements rares et risqués | Déploiements fréquents et automatisés |
| Peu de documentation formelle | Documentation technique complète et à jour |

### Cartographie des parties prenantes

| Partie prenante | Impact du changement | Implication attendue |
|-----------------|----------------------|----------------------|
| Direction générale | Faible (résultat visible) | Validation budget et orientation |
| Équipe de développement | Fort (nouvelles pratiques quotidiennes) | Acteur principal du changement |
| Équipe commerciale | Modéré (nouveaux outils de gestion) | Utilisateur des interfaces admin |
| Clients finaux | Faible (expérience améliorée) | Testeurs lors des phases UAT |
| Équipe infrastructure/Ops | Modéré (gestion Docker, CI/CD) | Partenaire technique |

---

## 2. Plan d'action — Les 4 axes

### Axe 1 — INFORMER

> Objectif : s'assurer que tout le monde comprend **pourquoi** ce changement a lieu

| Action | Cible | Timing | Responsable |
|--------|-------|--------|-------------|
| Présentation de la vision et des objectifs du projet | Toute l'entreprise | Semaine 1 (J-30) | Direction + Chef de projet |
| Distribution du document d'architecture | Équipe technique | Semaine 1 | Tech Lead |
| Affichage des bénéfices attendus (vitesse, fiabilité) | Tous | Continu | Communication interne |
| Mise à disposition de la FAQ sur l'intranet | Tous | Semaine 2 | Chef de projet |
| Newsletter mensuelle d'avancement | Toute l'entreprise | Mensuel | Chef de projet |

**Message clé à transmettre :**
> *"Ce changement n'est pas une remise en question du travail passé. L'ancien système a bien fonctionné. On évolue parce que l'entreprise grandit et que nos besoins ont changé."*

---

### Axe 2 — COMMUNIQUER

> Objectif : créer des canaux d'échange **bidirectionnels** — pas juste informer, mais aussi écouter

| Action | Participants | Fréquence | Format |
|--------|--------------|-----------|--------|
| Réunion de lancement (kick-off) | Direction + toutes les équipes | 1 fois | Présentiel, 2h |
| Daily stand-up | Équipes de développement | Quotidien | 15 min debout |
| Sprint review | Équipes dev + parties prenantes | Toutes les 2 semaines | Démo + retours |
| Rétrospective de sprint | Équipes de développement | Toutes les 2 semaines | 1h, format Start/Stop/Continue |
| Point de suivi direction | Direction + Chef de projet | Mensuel | 30 min |
| Canal dédié (ex: Slack #payetonkawa) | Toute l'équipe | Continu | Messagerie instantanée |

**Règle d'or :** les remontées de terrain doivent remonter jusqu'à la direction. Un développeur qui soulève un problème doit avoir un retour sous 48h maximum.

---

### Axe 3 — FORMER

> Objectif : donner aux équipes **les compétences nécessaires** pour réussir dans le nouvel environnement

#### Plan de formation

| Formation | Durée | Cible | Priorité |
|-----------|-------|-------|----------|
| Architecture micro-services (concepts, avantages, pièges) | 1 jour | Tous les développeurs | Haute |
| Docker et Docker Compose (conteneurs, images, volumes) | 1 jour | Développeurs + Ops | Haute |
| FastAPI et Python moderne (async, Pydantic, SQLAlchemy) | 1 jour | Développeurs backend | Haute |
| Méthodologie Agile Scrum (rôles, cérémonies, backlog) | 1 jour | Toute l'équipe | Haute |
| RabbitMQ — messagerie asynchrone (exchanges, queues, ack) | 0,5 jour | Développeurs | Moyenne |
| GitHub Actions — CI/CD (workflows, jobs, secrets) | 0,5 jour | Développeurs + Ops | Moyenne |
| Tests automatisés avec pytest (fixtures, mocks, couverture) | 0,5 jour | Développeurs | Moyenne |
| PostgreSQL avancé (indexation, backup, réplication) | 0,5 jour | Ops | Basse |

#### Modalités de formation

- **Ateliers pratiques** (hands-on) : les participants travaillent sur le vrai projet PayeTonKawa pendant la formation
- **Documentation interne** : les fichiers `docs/` sont utilisés comme support de cours
- **Pair programming** : les développeurs seniors accompagnent les juniors pendant les 2 premières semaines
- **Revues de code** : toute Pull Request doit être relue par au moins un autre développeur (knowledge sharing)

---

### Axe 4 — FAIRE PARTICIPER

> Objectif : donner aux équipes un **rôle actif** dans le changement — les gens résistent moins à ce qu'ils ont contribué à construire

| Action participative | Participants | Bénéfice |
|---------------------|--------------|----------|
| Choix des technologies (vote entre alternatives) | Développeurs seniors | Appropriation des décisions |
| Définition des standards de code (nommage, structure) | Toute l'équipe dev | Responsabilisation collective |
| Rédaction des règles GitFlow | Tech Lead + Développeurs | Processus accepté car co-construit |
| Tests utilisateurs des nouvelles interfaces | Équipe commerciale | Retours terrain intégrés tôt |
| Rétrospectives d'amélioration continue | Toute l'équipe | Amélioration pilotée par l'équipe elle-même |
| Désignation d'un "champion du changement" par équipe | Volontaires | Relais positif au quotidien |

---

## 3. Modèle de transition de Bridges

Le modèle de William Bridges distingue trois phases psychologiques que traversent les individus lors d'un changement. Comprendre ces phases permet d'adapter la communication et l'accompagnement.

```
TEMPS ──────────────────────────────────────────────────────────►

Phase 1 : FIN          Phase 2 : ZONE NEUTRE     Phase 3 : NOUVEAU DÉPART
━━━━━━━━━━━━━━━━━━     ━━━━━━━━━━━━━━━━━━━━━━━   ━━━━━━━━━━━━━━━━━━━━━━━━━

Deuil de l'ancien      Confusion, incertitude    Énergie nouvelle,
système                Apprentissage difficile   maîtrise, fierté
"Ça marchait bien"     "Je ne comprends rien"    "Je préfère le nouveau
                                                  système"

Semaines 1–2           Semaines 3–8              Semaine 9+

ACTION :               ACTION :                  ACTION :
Valoriser le passé     Accompagner, tolérer      Célébrer les succès,
Expliquer pourquoi     les erreurs, former       mesurer les progrès
on doit évoluer        intensivement
```

**Application pour PayeTonKawa :**

- **Phase 1 (Fin)** : Reconnaître que l'ancien système a bien servi l'entreprise. Ne pas le dénigrer. Expliquer clairement les limites qui justifient le changement (monolithe difficile à faire évoluer, déploiements risqués, pas de tests).

- **Phase 2 (Zone neutre)** : C'est la phase la plus délicate. Les développeurs apprennent Docker, GitHub Actions, les micro-services... tout en continuant à travailler. Tolérer les erreurs, doubler les revues de code, organiser des sessions de question/réponse hebdomadaires.

- **Phase 3 (Nouveau départ)** : Célébrer les premières PRs validées automatiquement par la CI, le premier déploiement Docker réussi, les 140 tests au vert. Ces petites victoires ancrent le nouveau mode de travail.

---

## 4. Résistances anticipées et réponses

| Résistance probable | Origine | Réponse adaptée |
|--------------------|---------|-----------------|
| *"Ça marchait bien avant, pourquoi changer ?"* | Peur du changement, attachement à l'existant | Montrer concrètement les limites de l'ancien système (temps de déploiement, bugs en cascade, pas de tests) |
| *"C'est trop compliqué, je ne comprends pas Docker"* | Manque de compétences, sentiment d'incompétence | Formation hands-on, pair programming, environnement de test sans risque |
| *"On n'a pas le temps de faire des tests en plus du code"* | Pression calendaire | Démontrer que les tests font gagner du temps à moyen terme (moins de régressions, moins de bugs en prod) |
| *"Pourquoi 3 APIs ? Un seul programme c'était plus simple"* | Incompréhension de l'architecture | Explication simple : si les produits plantent, les clients peuvent toujours se connecter. Isolation des pannes. |
| *"Qui va gérer tout ça en production ?"* | Inquiétude sur la charge de travail | Définir clairement les rôles et responsabilités. Montrer que l'automatisation (CI/CD, healthchecks) réduit la charge. |
| *"On ne peut pas tester avec le client en Agile, les besoins changent trop"* | Méconnaissance de Scrum | Expliquer que c'est justement l'avantage de l'Agile : s'adapter aux changements plutôt que de les subir |

---

## 5. Planning de transition

```
MOIS 1 — PRÉPARATION ET FORMATION
├── Semaine 1 : Kick-off, présentation vision, FAQ
├── Semaine 2 : Formation architecture micro-services + Docker
├── Semaine 3 : Formation FastAPI + RabbitMQ + tests
└── Semaine 4 : Formation Agile Scrum + mise en place des cérémonies

MOIS 2 — MISE EN PLACE ET PREMIERS SPRINTS
├── Semaine 1–2 : Sprint 1 (mise en place CI/CD, structure du projet)
├── Semaine 3–4 : Sprint 2 (développement api-clients + tests)
└── Sprint review + rétrospective

MOIS 3 — DÉVELOPPEMENT ET STABILISATION
├── Sprint 3 : api-produits (catalogue, images, stock)
├── Sprint 4 : api-commandes + RabbitMQ (consumer)
└── Sprint review + démo aux parties prenantes

MOIS 4 — FINALISATION ET DÉPLOIEMENT
├── Sprint 5 : Monitoring, documentation, Postman
├── Tests de charge + validation sécurité
├── Formation équipe commerciale (nouveaux outils admin)
└── Déploiement en production + support renforcé (2 semaines)

MOIS 5 — AUTONOMIE
├── Rétrospective globale du projet
├── Mesure des KPIs de succès
└── Passage en mode maintenance autonome
```

---

## 6. KPIs de succès

Les indicateurs ci-dessous permettent de mesurer objectivement si la transition est réussie.

### KPIs techniques

| Indicateur | Objectif | Méthode de mesure |
|------------|----------|------------------|
| Couverture de tests | ≥ 90% sur chaque API | `pytest --cov` dans la CI |
| Taux de succès de la CI | ≥ 95% des builds verts | GitHub Actions (taux de succès) |
| Temps de déploiement | < 10 minutes | Durée du pipeline GitHub Actions |
| Disponibilité des APIs | ≥ 99% | Endpoint `/health` + monitoring |
| Temps de réponse moyen | < 200 ms | Logs middleware (champ `duration_ms`) |

### KPIs organisationnels

| Indicateur | Objectif | Méthode de mesure |
|------------|----------|------------------|
| Satisfaction de l'équipe de dev | ≥ 7/10 | Sondage anonyme trimestriel |
| Vélocité des sprints | Stable ou croissante | Points livrés par sprint |
| Nombre de bugs en production | -50% vs avant | Tickets de bug ouverts |
| Délai de mise en production | -70% vs avant | Temps entre PR et déploiement |
| Participation aux cérémonies | ≥ 90% | Présence aux daily + reviews |

---

## 7. Facteurs clés de succès

1. **Soutien visible de la direction** : les équipes doivent voir que la direction croit dans ce projet et y consacre des ressources (temps, formation, budget)

2. **Communication transparente** : partager les difficultés rencontrées, pas seulement les succès. La confiance se construit sur l'honnêteté.

3. **Valoriser les petites victoires** : chaque PR fusionnée, chaque test qui passe, chaque déploiement réussi mérite d'être célébré.

4. **Tolérer les erreurs de transition** : en phase d'apprentissage, les erreurs sont normales. Les sanctionner crée de la peur et bloque l'adoption.

5. **Former avant de déployer** : ne pas mettre en production un outil que les équipes ne maîtrisent pas encore.

6. **Mesurer et ajuster** : suivre les KPIs régulièrement et adapter le plan en fonction de la réalité du terrain.
