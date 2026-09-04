🇫🇷 Version française | [🇬🇧 English version](CONTRIBUTING.md)

---

# Contribuer à Triton

Il s'agit avant tout d'un projet personnel. Les contributions externes
(signalements de bugs, corrections, petites améliorations) sont les
bienvenues mais restent limitées en portée.

## Prérequis

- [uv](https://docs.astral.sh/uv/) — gestionnaire de paquets Python
- Node.js ≥ 22
- Docker avec Compose v2 (`docker compose`), pour la stack complète via Traefik

## Installation locale

```bash
git clone https://github.com/MarvinLeRouge/Triton.git
cd Triton
uv sync
cd frontend && npm install
```

## Lancer les tests

```bash
uv run pytest              # backend
cd frontend && npm run test:unit   # frontend
```

## Déroulement

1. Forker le dépôt et créer une branche à partir de `develop` (pas `main`, qui
   est protégée et ne reçoit des merges qu'à la fin d'une phase complète).
2. Faire la modification, avec des tests qui la couvrent.
3. Commiter en suivant la convention ci-dessous.
4. Pousser et ouvrir une pull request vers `develop`.
5. La CI doit passer avant la revue.

## Nommage des branches

| Type | Préfixe |
|---|---|
| Fonctionnalité de phase (roadmap) | `phase-{n}-{nom-phase}/feat/{nom-feature}` |
| Fonctionnalité (hors phase roadmap) | `feat/description-courte` |
| Correction | `fix/description-courte` |
| Maintenance | `chore/description-courte` |
| Documentation | `docs/description-courte` |
| Refactoring | `refactor/description-courte` |
| Tests | `test/description-courte` |

Minuscules, kebab-case, sans caractères spéciaux.

## Convention de commit

Suivre [Conventional Commits](https://www.conventionalcommits.org/), impératif,
minuscules, sans point final, avec une section `Modified files:` obligatoire :

```
type(scope/module): résumé court

Modified files:
- chemin/vers/fichier-a.ext - ce qui a été modifié
- chemin/vers/fichier-b.ext - ce qui a été modifié
```

Le scope doit toujours préciser `backend/<module>`, `frontend/<module>`,
`infra`, ou `root` — jamais un simple `type: ...`.

Types : `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, `perf`, `ci`.

Exemples :

```
feat(backend/engine): add grid initialization
fix(frontend/canvas): correct heatmap color scale
docs(root): add CONTRIBUTING.md
```

## Style de code

Backend (Python) :

```bash
uv run ruff check .        # lint
uv run ruff format --check .
uv run mypy engine api     # vérification de types stricte
```

Frontend (TypeScript/Vue) :

```bash
cd frontend
npm run lint               # ESLint + oxlint
npm run type-check         # vue-tsc
```

La CI rejettera toute pull request qui ne passe pas ces vérifications.

## Releases et changelog

La section `[Unreleased]` de `CHANGELOG.md` est maintenue automatiquement :
un workflow CI (`.github/workflows/changelog.yml`, config dans `cliff.toml`)
exécute [git-cliff](https://git-cliff.org/) à chaque push sur `main` et
ouvre ou met à jour une pull request avec la section régénérée. Ne jamais
modifier à la main la section `[Unreleased]` de `CHANGELOG.md` ni ce qui
est au-dessus ; les entrées antérieures à `v0.6.0` sont un historique
rédigé à la main, figé.

Pour sortir une vraie release, une fois que `main` reflète l'état à
publier :

1. Créer un tag annoté : `git tag -a vX.Y.Z -m "Phase N: Titre"`.
2. Le pousser : `git push origin vX.Y.Z`.
3. Régénérer localement le changelog avec le titre de version :
   `npx git-cliff --config cliff.toml --tag vX.Y.Z --prepend CHANGELOG.md`
   (après avoir retiré tout bloc `[Unreleased]` obsolète), puis commiter
   le résultat.

## Code de conduite

Ce projet suit un [Code de conduite](CODE_OF_CONDUCT.fr.md). En participant,
vous vous engagez à le respecter.

## Licence

En contribuant, vous acceptez que vos contributions soient distribuées sous la
licence du projet (voir [LICENSE](LICENSE)).
