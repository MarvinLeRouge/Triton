# ADR-0003: Bayesian probability map with temporal diffusion

- Status: Accepted (superseded in part by [ADR-0006](0006-per-drone-maps-periodic-fusion.md))
- Date: 2026-08-11
- Source: PR #20, #21, #22, #23 (`phase-3-bayesian/feat/probability-map`, `feat/bayesian-update`, `feat/diffusion`)

## Context

The sonar model (ADR-0002) produces noisy, partial detection events. The
fleet needed a persistent belief state about where Red might be, rather than
reacting only to the current turn's raw detection outcome.

## Decision

Introduce a `ProbabilityMap` over the grid, updated via a Bayesian update on
each sonar sweep (reinforcing cells consistent with a detection or
non-detection) and periodically diffused — spreading confidence outward
toward neighboring cells over time, to model Red's ability to move between
sweeps. At this stage, the fleet shared a single map (`Simulation.probability_map`,
singular).

## Alternatives considered

- A decaying "last known position" heuristic instead of a full probability
  distribution — rejected, it cannot represent a multi-modal belief (e.g.
  after Red disappears from view, having possibly gone one of two ways).
- Per-drone independent maps from the start — not adopted at this stage; a
  single shared map made fleet-wide coordination implicit (every drone acts
  on the same picture), which was judged sufficient before individual drone
  autonomy became a design goal. This was revisited in Phase 6 (see
  ADR-0006).

## Consequences / future evolution

The diffusion rate is a tunable parameter that has not been stress-tested
against a highly evasive Red; flagged as an area to revisit if the map
proves too slow or too fast to track Red's actual movement. The single
shared map from this decision was superseded by per-drone maps with
periodic fusion in Phase 6 (ADR-0006), once independent per-drone search
became a goal.
