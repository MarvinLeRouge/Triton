🇫🇷 Version française | [🇬🇧 English version](README.md)

---

# Triton
## Introduction

Triton (Tracking & Reconnaissance In Tactical Operations Network) est une simulation au tour par tour d'une opération de recherche sonar autonome menée par une flotte multi-drones. Guidée par une carte de probabilité bayésienne, la flotte tente de localiser et de suivre un navire ennemi évasif sur une grille discrétisée.

## Concepts clés

- Modèle de détection probabiliste (sonar conique, POD)
- Mise à jour bayésienne de la carte à chaque balayage
- Coordination autonome des drones (optimisation de la couverture)
- Comportement ennemi adaptatif (évasion, contournement, fuite)

## Stack technique

- **Moteur** — Python (NumPy)
- **API** — FastAPI + WebSocket
- **Frontend** — Vue 3 + Vite + Canvas API
- **Infra** — Docker + Traefik

## Développement local

### Prérequis

- [uv](https://docs.astral.sh/uv/) — gestionnaire de paquets Python
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
- [Architecture](docs/architecture/)
- [Guide joueur](docs/guides/user_guide.fr.md)
- [Guide développeur](docs/guides/developer_guide.fr.md)
- [Registre des décisions d'architecture](docs/adr/)
- [Contribuer](CONTRIBUTING.fr.md)
