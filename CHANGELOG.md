# Changelog

All notable changes to this project will be documented in this file.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2026-08-13

### Added

- Add Grid class with configurable size and (row, col) coordinates

- Add Faction enum and Entity hierarchy

- Add Simulation class with turn loop and win conditions

- Add FastAPI skeleton with health endpoint and WebSocket game route

- Add gameStore (Pinia) and update GameCanvas skeleton

- Add Docker and Traefik setup for dev and prod

- Fix Vite allowedHosts for Docker/Traefik and add dev landing page

- Add GameState serialization and entity properties to Simulation

- Stream simulation state over WebSocket

- Add GameState interface and simulation state tracking

- Add canvas-helpers with cell-to-pixel conversion

- Render grid and entities on GameCanvas

- Add SonarModel and BlueDrone heading tracking

- Integrate SonarModel into Simulation and stream detection events

- Render drone detection cones and flash on detection event

- Add ProbabilityMap class with informed prior initialization

- Implement Bayesian update on sonar sweep

- Implement temporal diffusion of the probability map

- Integrate ProbabilityMap into Simulation turn loop and expose it over WebSocket

- Render probability map as a heatmap overlay

- Add SearchStrategy interface with GreedyMaxProbability and FrontierCoverage implementations

- Implement per-drone independent strategy assignment and switching

- Add per-drone detection state machine

- Wire StrategyAssignment into Simulation via move_drones()

- Update per-drone detection state during advance()

- Move drones via their assigned search strategy

- Expose current search strategy name per drone

- Display current strategy and detection state per drone

- Implement Red baseline movement toward the infiltration target zone

- Implement Red evasion, bypass and flight behaviors on detection

- Implement Red's own detection range and Blue-unit awareness

- Add ProbabilityMap.replace_values() and fuse_maps()

- Give each drone its own ProbabilityMap instead of one shared map

- Implement periodic observation sync and map fusion via the mothership

- Add SonarModel.range_cells and regroup_target()

- Implement mothership-ordered fleet regroup on confirmed detection


### Fixed

- Migrate to dependency-groups, fix CI pytest guard and Node 22 lockfile

- Add pre-commit hooks and fix ruff formatting

- Refactor WsMock to module-level class to satisfy oxlint no-this-alias

- Reset vessel_moved signal after each advance() turn

- Avoid RedVessel spawning on an occupied cell

- Address final-review findings on drone de-confliction and detection-state coverage

- Harden map-fusion sync against aliasing and invalid config

- Prevent anchor collision and permanent drone freeze in fleet regroup


