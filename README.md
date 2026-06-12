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

## 🗺️ Roadmap

### ✅ Planning

- [x] Project scoping & phase planning — architecture, naming conventions (Blue/Red factions), default simulation parameters, tooling (uv, ruff, mypy, ESLint, Prettier, Vitest, Codecov)

### 🔜 Planned

- [ ] **Phase 1 — Foundations**: grid, entities, initial placement, end-to-end pipeline (engine, API, frontend, Docker/Traefik)
- [ ] **Phase 2 — Sonar model**: cone-shaped POD, detection probability
- [ ] **Phase 3 — Bayesian map**: probability map, Bayesian update, temporal diffusion
- [ ] **Phase 4 — Drone intelligence**: search strategies, detection state machine
- [ ] **Phase 5 — Red behavior**: evasion, infiltration objective
- [ ] **Phase 6 — Multi-drone coordination**: map fusion, fleet regroup
- [ ] **Phase 7 — Polish & scenarios**: configuration, replayability, demo deployment
