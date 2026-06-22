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

Follow `docs/ai/dev-local-traefik.md` for the one-time local Traefik setup, then:

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

### ✅ Planning

- [x] Project scoping & phase planning — architecture, naming conventions (Blue/Red factions), default simulation parameters, tooling (uv, ruff, mypy, ESLint, Prettier, Vitest, Codecov)

### 🔜 Planned

- [x] **Phase 1 — Foundations**: grid, entities, initial placement, end-to-end pipeline (engine, API, frontend, Docker/Traefik)
- [ ] **Phase 2 — Sonar model**: cone-shaped POD, detection probability
- [ ] **Phase 3 — Bayesian map**: probability map, Bayesian update, temporal diffusion
- [ ] **Phase 4 — Drone intelligence**: search strategies, detection state machine
- [ ] **Phase 5 — Red behavior**: evasion, infiltration objective
- [ ] **Phase 6 — Multi-drone coordination**: map fusion, fleet regroup
- [ ] **Phase 7 — Polish & scenarios**: configuration, replayability, demo deployment
