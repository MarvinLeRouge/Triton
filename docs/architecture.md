[🇫🇷 Version française](architecture.fr.md) | 🇬🇧 English version

---

# Architecture - Triton

> Public technical reference. See [engine](architecture/engine_architecture.md), [API](architecture/api_architecture.md), [frontend](architecture/frontend_architecture.md), and [infrastructure](architecture/infra_architecture.md) architecture for implementation details.

## Overview

Triton is a real-time ASW (anti-submarine warfare) simulation with four components:

- **Engine** - pure Python + NumPy, zero UI or transport dependency. Owns all game logic: the grid, entities, sonar detection model, Bayesian probability maps, search strategies, and the turn loop (`Simulation`).
- **API** - FastAPI, a thin transport layer over the engine. Opens one `Simulation` per WebSocket connection (`/ws/game`) and streams its serialized state every turn.
- **Frontend** - Vue 3 + Vite + TypeScript, Canvas API rendering. A passive renderer driven entirely by WebSocket messages, no client-side game logic.
- **Infrastructure** - Docker Compose + Traefik, same routing shape in dev and prod.

## Project structure

```
triton/
├── engine/
│   ├── grid.py               # Discretized 2-D grid
│   ├── entities.py            # Faction, DetectionState, drones/vessels
│   ├── sonar_model.py          # Probability-of-detection law
│   ├── probability_map.py       # Per-drone Bayesian belief map
│   ├── map_fusion.py             # Multi-drone map consensus
│   ├── search_strategy.py         # Drone movement strategies
│   └── simulation.py               # Turn loop, win-condition evaluation
├── api/
│   └── main.py                # FastAPI app: /health, /ws/game
├── frontend/
│   └── src/
│       ├── stores/game.ts      # Pinia store, WebSocket connection
│       └── components/          # GameCanvas.vue + drawing helpers
├── docker-compose.yml            # Dev stack (Traefik-routed, hot-reload)
├── docker-compose.prod.yml        # Prod stack (built images, TLS)
└── docs/
    ├── architecture/    # engine/api/frontend/infra architecture
    ├── adr/             # architecture decision records
    └── guides/          # developer/user guides
```

## Further reading

- [Engine architecture](architecture/engine_architecture.md)
- [API architecture](architecture/api_architecture.md)
- [Frontend architecture](architecture/frontend_architecture.md)
- [Infrastructure architecture](architecture/infra_architecture.md)
- [Architecture decision records](adr/README.md)
- [Developer guide](guides/developer_guide.md)
- [Product context](product-context.md)
- [Operations](operations.md)
