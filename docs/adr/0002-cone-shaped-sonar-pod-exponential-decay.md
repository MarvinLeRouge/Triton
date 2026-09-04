# ADR-0002: Cone-shaped sonar with exponential probability-of-detection

- Status: Accepted
- Date: 2026-06-22
- Source: PR #14 (`phase-2-sonar/feat/pod-model`)

## Context

The Phase 1 placeholder detection ("same cell = seen") was too crude to make
search meaningful — it gave no partial information and no directional
constraint.

## Decision

Each drone senses through a directional cone (dot-product/angle test against
its heading, Euclidean range check), and detection within the cone is
probabilistic rather than binary: an exponentially decaying
probability-of-detection with distance, modulated by two factors — a noise
factor (Red moving vs. holding still makes it easier or harder to hear) and
an attention factor that ramps up with the drone's own consecutive-detection
streak (a drone already onto something gets better at confirming it).

## Alternatives considered

- Binary range-only detection with no cone — rejected, irrelevant to a
  directional sonar sensor and too easy to trivially evade by staying just
  outside a small angle.
- A flat or step-function probability-of-detection instead of a smooth
  exponential decay — rejected, the exponential law is tunable via a single
  decay parameter without redesigning the geometry, and produces a
  gradually more forgiving detection chance at close range rather than a
  hard cutoff.

## Consequences / future evolution

Default POD parameters (decay rate, attention ramp, noise factor) were
calibrated empirically against expected qualitative behavior, not derived
from a real sonar model — flagged in the project's own planning notes as an
area to recalibrate later if playtesting shows unrealistic detection rates,
without needing to touch the underlying cone geometry or the law's shape.
