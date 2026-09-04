# ADR-0005: Red evasion and infiltration as plain functions, not a strategy pool

- Status: Accepted
- Date: 2026-08-11/12
- Source: PR #33, #34, #35 (`phase-5-red-behavior/feat/red-baseline-movement`, `feat/red-evasion`, `feat/red-detection-range`)

## Context

Red needed a non-trivial adversary behavior — advancing on a straight line
toward its objective would make the search trivial and uninteresting.

## Decision

Implement Red's behavior as plain functions rather than a `SearchStrategy`-
like interface: `red_baseline_target` moves toward the infiltration zone,
`red_evasion_target` moves directly away from the nearest detected threat,
and `blue_units_within_range` gives Red its own independent, omnidirectional
sensing range (Chebyshev distance), entirely separate from Blue's
directional sonar model.

## Alternatives considered

- Mirroring Blue's `SearchStrategy` abstraction for Red — rejected. Red has
  one deterministic decision process (evade if threatened, otherwise
  advance toward the objective), not a rotating pool of interchangeable
  behaviors, so a shared interface would add indirection without any reuse
  benefit.

## Consequences / future evolution

Adding a genuinely different Red behavior (e.g. a bypass maneuver, decoy
runs) means adding a new function with the same signature shape and wiring
it directly into `Simulation`'s Red movement step, rather than registering
it in a pool (see the [developer guide](../guides/developer_guide.md)). If
Red ever needs more than one interchangeable behavior mode, revisiting a
strategy-pool design at that point (matching ADR-0004's approach) would be
the natural next step.
