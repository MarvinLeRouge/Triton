# ADR-0004: Interchangeable search strategies and a per-drone detection state machine

- Status: Accepted
- Date: 2026-08-11
- Source: PR #28, #29, #30 (`phase-4-drone-ai/feat/search-strategies`, `feat/strategy-assignment`, `feat/detection-state-machine`)

## Context

Drones needed two independent things: a way to decide where to move each
turn (a search strategy), and a way for each drone to escalate its own
confidence in a contact, separate from the fleet-wide streak that drives the
global win condition.

## Decision

- `SearchStrategy` as an abstract interface with a pool of interchangeable
  implementations (`GreedyMaxProbability`, `FrontierCoverage`), assigned per
  drone and periodically re-rolled at random via `StrategyAssignment`, with
  each drone independently rolling its own switch chance every turn.
- A per-drone `DetectionState` state machine (`SEARCHING → SIGNALING →
  CONFIRMING → TRACKING`), driven by each drone's own consecutive-detection
  streak, thresholds aligned by convention with the simulation's
  `lock_turns` parameter but tracked independently of it.

## Alternatives considered

- A single fixed strategy for the whole fleet — rejected in favor of a pool,
  to get variety and robustness in coverage rather than every drone
  behaving identically.
- A gradual decay of detection state on lost contact — rejected in favor of
  an immediate reset to `SEARCHING` on any missed detection, judged simpler
  and consistent with the existing fleet-wide streak's own behavior.

## Consequences / future evolution

Adding a new search strategy only requires implementing the interface and
adding it to the pool passed into `StrategyAssignment` — no other wiring
required (see the [developer guide](../guides/developer_guide.md)). The
state machine's thresholds being aligned with, but not derived from,
`lock_turns` is a convention that could drift if either is tuned in
isolation — not yet enforced by a shared constant.
