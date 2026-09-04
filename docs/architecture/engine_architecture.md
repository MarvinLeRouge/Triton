[🇫🇷 Version française](engine_architecture.fr.md) | 🇬🇧 English version

---

# Engine Architecture

Pure Python + NumPy, zero UI or transport dependency. All game logic lives
here; the API layer only drives it and serializes its state.

| Module | Responsibility |
|---|---|
| `grid.py` | Discretized 2-D grid (`Grid`), origin at the NW corner, `(row, col)` coordinates |
| `entities.py` | `Faction`, `DetectionState` state machine, `Entity` base class, `BlueMothership`, `BlueDrone`, `RedVessel` |
| `sonar_model.py` | `SonarModel` — cone-shaped probability-of-detection law with exponential distance decay |
| `probability_map.py` | `ProbabilityMap` — per-drone Bayesian belief map over the grid, with diffusion and Bayesian update |
| `map_fusion.py` | `fuse_maps()` — pure elementwise-mean consensus of multiple drones' maps |
| `search_strategy.py` | `SearchStrategy` (abstract) and its implementations (`GreedyMaxProbability`, `FrontierCoverage`) driving drone movement |
| `strategy_assignment.py` | `StrategyAssignment` — assigns and periodically re-rolls each drone's active search strategy |
| `red_behavior.py` | Red's baseline movement, evasion, infiltration zone/objective |
| `fleet_regroup.py` | `regroup_target()` — pure movement step used when drones converge on a confirmed contact |
| `simulation.py` | `Simulation` — the turn loop: movement, sonar sweeps, map updates/fusion, fleet regroup, win-condition evaluation (`GameResult`) |

## Extension points

See [the developer guide](../guides/developer_guide.md) for how to plug in a
new `SearchStrategy`, a new Red behavior, or a different sonar detection law
without touching `Simulation`'s turn loop.

## Deeper design rationale

Per-decision rationale (alternatives considered, trade-offs, possible future
evolutions) lives in [docs/adr/](../adr/) for decisions already made, and
will be expanded by the dedicated Phase 7 documentation task for the engine's
core algorithmic choices (POD law, Bayesian update, diffusion, detection
state machine) — see [docs/roadmap.md](../roadmap.md).
