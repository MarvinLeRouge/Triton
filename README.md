[🇫🇷 Version française](README.fr.md) | 🇬🇧 English version

---

# Triton
## Introduction

Triton (Tracking & Reconnaissance In Tactical Operations Network) is a turn-based simulation of an autonomous multi-drone sonar search operation. A fleet of search drones, guided by a Bayesian probability map, attempts to locate and track an evasive enemy vessel across a discretized grid.

## Key concepts

- Probabilistic detection model (cone-shaped sonar, POD)
- Bayesian map update on each sensor sweep
- Autonomous drone coordination (coverage optimization)
- Adaptive enemy behavior (evasion, bypass, flight)

## Stack

- **Engine** — Python (NumPy)
- **API** — FastAPI + WebSocket
- **Frontend** — Vue 3 + Vite + Canvas API
- **Infra** — Docker + Traefik

## Local Development

### Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package manager
- Node.js ≥ 22
- Docker with Compose v2 (`docker compose`)

### Backend

```bash
uv sync
uv run pytest              # run tests
uv run ruff check .        # lint
uv run mypy engine api     # type-check
```

### Frontend

```bash
cd frontend
npm install
npm run dev                # dev server at http://localhost:5173
npm run test:unit          # unit tests
npm run lint               # ESLint + oxlint
npm run type-check         # TypeScript
```

### Full stack via Docker + Traefik (recommended)

Follow [docs/operations.md](docs/operations.md) for the one-time local Traefik setup, then:

```bash
# Add to /etc/hosts: 127.0.0.1 triton.marvinlerouge.local
docker compose up
# Open http://triton.marvinlerouge.local
```

For direct dev without Docker, the frontend needs to reach the backend.
Set `VITE_WS_URL=ws://localhost:8000/ws/game` in `frontend/.env`
and run the backend separately:

```bash
uv run uvicorn api.main:app --reload
```

---

## 🗺️ Roadmap

Phases 1 through 6 are complete (foundations, sonar model, Bayesian map, drone
intelligence, Red behavior, multi-drone coordination). Phase 7 (polish &
scenarios) is in progress. See [docs/roadmap.md](docs/roadmap.md) for the
full phase-by-phase breakdown.

## 📚 Documentation

- [Roadmap](docs/roadmap.md)
- [Product context](docs/product-context.md)
- [Operations / deployment](docs/operations.md)
- [Design system](docs/design-system.md)
- [Architecture](docs/architecture/)
- [Player guide](docs/guides/user_guide.md)
- [Developer guide](docs/guides/developer_guide.md)
- [Architecture Decision Records](docs/adr/)
- [Contributing](CONTRIBUTING.md)
