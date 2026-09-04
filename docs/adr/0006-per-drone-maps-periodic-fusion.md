# ADR-0006: Per-drone probability maps with periodic mean-fusion

- Status: Accepted (known limitation flagged, see Consequences)
- Date: 2026-08-13
- Source: PR #39 (`phase-6-coordination/feat/map-fusion`)

## Context

Since Phase 3 (ADR-0003), the fleet shared a single `ProbabilityMap`. As
multi-drone coordination became a goal, a single shared map made every
drone's search decisions dependent on one global picture that any drone
could affect without it reflecting that drone's own sensing.

## Decision

Give each `BlueDrone` its own independent `ProbabilityMap`, updated only
from its own sonar sweeps. Every `sync_interval` turns (default 10), fuse
all drones' maps via elementwise mean + renormalization (`fuse_maps()`) and
redistribute the consensus back to the whole fleet (`replace_values()`).
This was a deliberate breaking rename (`Simulation.probability_map` →
`probability_maps`), with no compatibility shim.

## Alternatives considered

- Keep a single shared map (status quo) — rejected, it defeats the purpose
  of giving drones independent search behavior.
- A mothership↔drone range constraint gating which drones participate in a
  given sync (only fusing/redistributing to drones within range) — explicitly
  considered and deferred, not implemented for this branch: all drones sync
  unconditionally regardless of distance to the mothership.

## Consequences / future evolution

Found during the branch's final review: elementwise mean dilutes a single
confident detection by roughly `1/N` at each sync (a map at `p=0.6` after one
detection drops to ~0.3 with 2 drones, ~0.15 with 4), since maps from drones
that saw nothing count as opposing votes. Not blocking for this branch (a
re-detecting drone recovers its own confidence at the next sweep), but
flagged to revisit before relying more heavily on multi-drone consensus: a
log-opinion-pool (normalized product) fusion would preserve a single
reliable observation better than a mean. Also still open: the
mothership↔drone range constraint deferred above, which could evolve into a
distance-proportional transmission delay rather than a binary in/out-of-range
cutoff.
