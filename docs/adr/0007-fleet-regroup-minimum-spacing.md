# ADR-0007: Fleet regroup on confirmed contact, with a minimum-spacing rule

- Status: Accepted
- Date: 2026-08-13
- Source: PR #40 (`phase-6-coordination/feat/fleet-regroup`)

## Context

Once a drone confirms or tracks Red, the rest of the fleet should converge
to help rather than continue independent search. Naively converging
straight on the same point risks the whole fleet lining up on one axis and
being flanked by Red all at once.

## Decision

As soon as any drone reaches `CONFIRMING`/`TRACKING`, every other drone
abandons its assigned `SearchStrategy` and moves toward that drone's own
computed destination for the turn (not its pre-move position) via
`regroup_target()` — a speed-clamped per-axis step mirroring
`red_baseline_target`'s movement math — while rejecting only a step that
would both close the distance to another Blue unit **and** end up under a
minimum spacing floor derived from `SonarModel.range_cells`.

## Alternatives considered

- Rejecting any position under `min_spacing` regardless of direction of
  travel — this was the initial design. Found during final review to freeze
  83% of regroup drone-turns in production, because drones' actual spawn
  distances (≤6 cells) are already below the sonar-derived `min_spacing`
  (8 cells by default) — a drone already "too close" could never move.
  Corrected to only reject *closing* moves, so an already-close drone keeps
  the ability to move as long as it doesn't reduce spacing further.
- Seeding the anchor's occupied-cell check with its pre-move position
  instead of its actual computed destination — tried and rejected, measured
  to cause ~26% of regroup turns to end with two drones stacked on the same
  cell, since the anchor always moves via its own strategy afterward.

## Consequences / future evolution

`min_spacing` floors at 1 to stay safe against a zero-range `SonarModel`
configuration used elsewhere in the test suite. General lesson recorded from
this branch: any parameter derived from another engine constant (here,
sonar range → regroup spacing) must be checked against real spawn/config
values, not just its own internal consistency, before being accepted.
