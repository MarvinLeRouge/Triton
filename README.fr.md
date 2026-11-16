🇫🇷 Version française | [🇬🇧 English version](README.md)

---

# Triton

> *Simulation au tour par tour d'une recherche sonar autonome par une flotte de drones : carte de probabilité bayésienne, modèle de détection probabiliste, couverture coordonnée des drones et cible évasive. Moteur Python (NumPy), FastAPI et WebSocket, frontend Vue.js.*

[![CI](https://github.com/MarvinLeRouge/Triton/actions/workflows/ci.yml/badge.svg)](https://github.com/MarvinLeRouge/Triton/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.14+-3776AB?logo=python&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D?logo=vuedotjs&logoColor=white)
[![Backend coverage](https://img.shields.io/codecov/c/github/MarvinLeRouge/Triton?flag=backend&label=backend&logo=codecov)](https://app.codecov.io/gh/MarvinLeRouge/Triton)
[![Frontend coverage](https://img.shields.io/codecov/c/github/MarvinLeRouge/Triton?flag=frontend&label=frontend&logo=codecov)](https://app.codecov.io/gh/MarvinLeRouge/Triton)
[![License](https://img.shields.io/github/license/MarvinLeRouge/Triton?cacheSeconds=3600)](LICENSE)

## Introduction

Triton (Tracking & Reconnaissance In Tactical Operations Network) est une simulation au tour par tour d'une opération de recherche sonar autonome menée par une flotte multi-drones. Guidée par une carte de probabilité bayésienne, la flotte tente de localiser et de suivre un navire ennemi évasif sur une grille discrétisée.

## Concepts clés

- **Probabilité de détection (POD)** : chaque drone porte un sonar conique dont la POD décroît exponentiellement avec la distance ([ADR-0002](docs/adr/0002-cone-shaped-sonar-pod-exponential-decay.md))
- **Carte de recherche bayésienne** : après chaque balayage, la carte de probabilité est mise à jour par la règle de Bayes, puis diffusée entre deux balayages pour modéliser le déplacement de la cible ([ADR-0003](docs/adr/0003-bayesian-probability-map-temporal-diffusion.md))
- **Fusion des cartes** : chaque drone tient sa propre carte, fusionnée périodiquement en un consensus de flotte ([ADR-0006](docs/adr/0006-per-drone-maps-periodic-fusion.md))
- **Machine à états de détection** : chaque drone passe par les états searching, signaling, confirming et tracking ([ADR-0004](docs/adr/0004-search-strategies-detection-state-machine.md)) ; sur un contact confirmé, la flotte se regroupe autour de lui ([ADR-0007](docs/adr/0007-fleet-regroup-minimum-spacing.md))
- **Comportement ennemi adaptatif** : évasion, contournement, fuite ([ADR-0005](docs/adr/0005-red-evasion-infiltration-behavior.md))

## Stack technique

- **Moteur** : Python (NumPy)
- **API** : FastAPI + WebSocket
- **Frontend** : Vue 3 + Vite + Canvas API
- **Infra** : Docker + Traefik

## Développement local

### Prérequis

- [uv](https://docs.astral.sh/uv/) : gestionnaire de paquets Python
- Node.js ≥ 22
- Docker avec Compose v2 (`docker compose`)

### Backend

```bash
uv sync
uv run pytest              # tests
uv run ruff check .        # lint
uv run mypy engine api     # vérification de types
```

### Frontend

```bash
cd frontend
npm install
npm run dev                # serveur de dev sur http://localhost:5173
npm run test:unit          # tests unitaires
npm run lint               # ESLint + oxlint
npm run type-check         # TypeScript
```

### Stack complète via Docker + Traefik (recommandé)

Suivre [docs/operations.fr.md](docs/operations.fr.md) pour le setup Traefik local (one-time), puis :

```bash
# Ajouter dans /etc/hosts : 127.0.0.1 triton.marvinlerouge.local
docker compose up
# Ouvrir http://triton.marvinlerouge.local
```

Pour développer sans Docker, le frontend doit atteindre le backend.
Définir `VITE_WS_URL=ws://localhost:8000/ws/game` dans `frontend/.env`
et lancer le backend séparément :

```bash
uv run uvicorn api.main:app --reload
```

---

## 🗺️ Feuille de route

Les phases 1 à 6 sont terminées (fondations, modèle sonar, carte bayésienne,
intelligence des drones, comportement Red, coordination multi-drones). La
Phase 7 (finalisation & scénarios) est en cours. Voir
[docs/roadmap.fr.md](docs/roadmap.fr.md) pour le détail phase par phase.

## 📚 Documentation

- [Feuille de route](docs/roadmap.fr.md)
- [Contexte produit](docs/product-context.fr.md)
- [Opérations / déploiement](docs/operations.fr.md)
- [Système de design](docs/design-system.fr.md)
- [Architecture](docs/architecture.fr.md)
- [Guide joueur](docs/guides/user_guide.fr.md)
- [Guide développeur](docs/guides/developer_guide.fr.md)
- [Registre des décisions d'architecture](docs/adr/)
- [Contribuer](docs/i18n/fr/CONTRIBUTING.fr.md)
