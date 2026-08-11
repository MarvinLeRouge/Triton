# Changelog

All notable changes to this project will be documented in this file.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.3.0] — 2026-08-11 — Phase 3: Bayesian Map

### Added

**Engine**
- `ProbabilityMap` — 1:1 probability-of-presence grid, informed prior weighted toward RedVessel's north/east/south spawn bands, floor value to keep every cell reachable by future updates
- `ProbabilityMap.update()` — Bayesian update from a drone's sonar sweep outcome: a positive detection rules out cells outside that drone's cone, a negative sweep scales in-cone cells by `SonarModel.pod()`
- `ProbabilityMap.diffuse()` — temporal diffusion: each cell keeps a `stay_weight` share of its mass, the rest spreads across its 8 neighbors, modeling RedVessel's possible movement between sweeps
- `Simulation` — runs a Bayesian update per drone sweep and one `diffuse()` per turn, exposed via a `probability_map` property (injectable) and in `to_dict()`

**API**
- `WebSocket /ws/game` — now includes `probability_map` (grid-shaped array of floats) in each frame

**Frontend**
- `heatmapIntensity()` / `drawHeatmapCell()` — pure canvas helpers normalizing and rendering the probability map
- `GameCanvas` — probability map rendered as a translucent heatmap layer behind the grid and entities, updating live each turn

### Fixed

- `api/main.py::_new_game()` — `RedVessel` could spawn on the same cell as `BlueMothership` or a `BlueDrone`, crashing `Simulation.__init__`; extracted `_spawn_red_vessel()` now retries until the picked cell is free

---

## [0.2.0] — 2026-06-22 — Phase 2: Sonar Model

### Added

**Engine**
- `SonarModel` — probabilistic detection model: directional cone (120°, 8-cell range), exponential POD law `exp(-λr) · noise(v) · attention(streak)`, probabilistic draw each turn
- `BlueDrone.heading` — drone heading, updated on each `move()`, default `(0, 1)` (east)
- `Simulation.notify_vessel_moved()` — Red speed signal for the next turn
- `Simulation._compute_detections()` — replaces same-cell placeholder with a sonar POD draw
- `Simulation.to_dict()` — extended with `drones[].heading` and `detection_events`

**API**
- `WebSocket /ws/game` — now includes `detection_events` and per-drone `heading` in each frame

**Frontend**
- `DroneState` / `DetectionEvent` — TypeScript types for the updated game state
- `drawCone()` — pure canvas helper: arc sector oriented along the drone heading
- `GameCanvas` — sonar cones rendered behind entities, orange flash for 1 turn on detection

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
