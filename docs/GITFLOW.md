# Stratégie de branches — GitFlow

## Branches principales

| Branche | Rôle |
|---------|------|
| `main` | Code stable, prêt pour la production. Le CI build les images Docker à chaque push. |
| `develop` | Intégration continue. Les features sont mergées ici avant d'aller en production. |

## Branches de travail

| Branche | Utilisation | Exemple |
|---------|-------------|---------|
| `feature/xxx` | Nouvelle fonctionnalité | `feature/ajout-motdepasse` |
| `bugfix/xxx` | Correction d'un bug | `bugfix/login-erreur-401` |
| `hotfix/xxx` | Correction urgente directement sur main | `hotfix/crash-api-produits` |

## Workflow standard

```
1. Se placer sur develop et mettre à jour
   git checkout develop
   git pull origin develop

2. Créer une branche de travail
   git checkout -b feature/ma-fonctionnalite

3. Développer, commiter régulièrement
   git add .
   git commit -m "feat: ajout du champ mot de passe"

4. Pousser la branche
   git push origin feature/ma-fonctionnalite

5. Créer une Pull Request vers develop sur GitHub

6. Les tests CI s'exécutent automatiquement
   → Si tout est vert : merge possible
   → Si un test échoue : corriger avant de merger

7. Mise en production : merge develop → main
   → Le CI build et valide les images Docker
```

## Convention de commits

| Préfixe | Usage |
|---------|-------|
| `feat:` | Nouvelle fonctionnalité |
| `fix:` | Correction de bug |
| `docs:` | Documentation uniquement |
| `test:` | Ajout ou modification de tests |
| `refactor:` | Refactoring sans changement de comportement |
| `chore:` | Tâches de maintenance (deps, config...) |

Exemples :
```
feat: ajout endpoint POST /customers/login
fix: correction hashage bcrypt incompatible passlib
docs: ajout mdp-part.md
test: ajout tests pour TestLoginCustomer
```

## Règles

- On ne pousse jamais directement sur `main`
- Toute PR doit avoir les tests CI verts avant d'être mergée
- Un commit = une modification logique (ne pas mélanger feature et bugfix dans le même commit)
