[🇫🇷 Version française](user_guide.fr.md) | 🇬🇧 English version

---

# Player Guide

## Running a simulation

Open the frontend (see the [README](../../README.md) for local setup). A
new simulation starts automatically as soon as the page connects over
WebSocket — there is no lobby or configuration screen yet (planned for
Phase 7's scenario configuration work).

## Reading the view

- **Grid**: the discretized battlefield, origin at the top-left corner.
- **Mothership**: the stationary Blue base.
- **Drones**: the searching Blue fleet. Each one shows its current heading
  and sonar cone.
- **Probability heatmap**: the fused belief map — brighter cells are where
  Red is more likely to be, based on everything the fleet has sensed so far.
- **Red vessel**: only rendered once detected; otherwise its position is
  unknown to you, exactly as it is to the Blue fleet.

## Detection states

Each drone's relationship to a contact escalates through four states as
evidence accumulates: **searching** (no contact) → **signaling** (a first,
unconfirmed ping) → **confirming** (repeated pings) → **tracking** (locked
on). Once a drone reaches confirming or tracking, the rest of the fleet
abandons independent search and regroups around it — watch for this
convergence as the clearest sign a hunt is underway.

## Outcome

A run ends when either side wins or the turn limit is reached:

- **Blue wins** if Red is tracked and held near the mothership for enough
  consecutive turns.
- **Red wins** if it reaches the infiltration zone behind the mothership's
  spawn undetected, or survives the full turn limit.

There are currently no playback controls (pause/step/replay) — a run plays
out continuously once connected; this is planned for Phase 7.
