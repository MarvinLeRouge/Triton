# Changelog

All notable changes to this project will be documented in this file.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.2.0] — 2026-06-22 — Phase 2: Sonar Model

### Added

**Engine**
- `SonarModel` — modèle de détection probabiliste : cône directionnel 120°/8 cases, loi POD exponentielle `exp(-λr) · noise(v) · attention(streak)`, tirage par tour
- `BlueDrone.heading` — cap du drone, mis à jour à chaque `move()`, défaut est (0,1)
- `Simulation.notify_vessel_moved()` — signal de vitesse de Red pour le prochain tour
- `Simulation._compute_detections()` — remplace le placeholder de partage de case par un tirage POD sonar
- `Simulation.to_dict()` — enrichi avec `drones[].heading` et `detection_events`

**API**
- `WebSocket /ws/game` — inclut désormais `detection_events` et `heading` par drone dans chaque frame

**Frontend**
- `DroneState` / `DetectionEvent` — types TypeScript pour le nouvel état de jeu
- `drawCone()` — helper canvas pur : secteur arc orienté selon le cap du drone
- `GameCanvas` — cônes sonar rendus derrière les entités, flash orange 1 tour sur détection

---

## [0.1.0] — 2026-06-21 — Phase 1: Foundations

### Added

**Engine**
- `Grid` — 50×50 discretized grid with bounds checking and clamping
- `Faction` enum — `BLUE` / `RED`
- `Entity` — abstract base class with absolute-coordinate movement and grid validation
- `BlueMothership`, `BlueDrone`, `RedVessel` — concrete entity subclasses
- `GameResult` — `IN_PROGRESS` / `BLUE_WINS` / `RED_WINS`
- `Simulation` — rule engine: detection streak, engagement streak, Chebyshev mothership range, turn limit; `to_dict()` serialization

**API**
- `GET /health` — health check endpoint
- `WebSocket /ws/game` — streams simulation state as JSON each turn (random-movement placeholder)

**Frontend**
- `useGameStore` (Pinia) — WebSocket lifecycle, `GameState` type, `gameState` reactive ref
- `GameCanvas` — 500×500 canvas rendering grid, BlueMothership (blue square), BlueDrone (blue circles), RedVessel (red triangle)
- `canvas-helpers` — `cellToPixelX` / `cellToPixelY` pure conversion functions

**Infrastructure**
- `Dockerfile.backend` — uv-based multi-layer Python image
- `frontend/Dockerfile` — multi-stage Node build → Nginx
- `docker-compose.yml` — local dev with Traefik (`triton.marvinlerouge.local`), Vite HMR, `internal` network
- `docker-compose.prod.yml` — production VPS, TLS via Let's Encrypt, `traefik-public` + `internal` networks

**Tooling & CI**
- uv + Python 3.13, ruff (lint + format), mypy strict, pytest-cov
- Vue 3 + Vite + TypeScript, oxlint + ESLint + Prettier, Vitest
- GitHub Actions CI (backend + frontend), Codecov OIDC (flags: `backend` / `frontend`)
- pre-commit hooks: ruff, mypy (backend); prettier, eslint, vue-tsc (frontend)
