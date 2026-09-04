[🇫🇷 Version française](product-context.fr.md) | 🇬🇧 English version

---

# Product Context

## What Triton is

Triton simulates a classic naval search-and-track problem: a fleet of sonar
drones, guided by a probabilistic map, must locate and track an evasive
enemy vessel ("Red") before it reaches its objective. It is a turn-based,
deterministic-per-turn simulation, not a real-time game: each turn, every
entity moves and senses once, the probability map updates, and the outcome
(Blue win, Red win, or timeout) is evaluated.

## Why this domain

The simulation is built around Bayesian search theory: rather than tracking
the enemy vessel's exact position, each Blue drone maintains a probability
distribution over where it could be, updated from imperfect sonar readings
(a cone-shaped probability-of-detection model, not a binary "seen/not seen"
sensor). This models a real class of problem (search and rescue, ASW, area
denial) where perfect information is never available, and decisions have to
be made from a belief state instead.

## The two factions

- **Blue** (the fleet being played): one stationary `BlueMothership` plus a
  configurable number of `BlueDrone`s. Drones search cooperatively, escalate
  through a detection state machine (searching → signaling → confirming →
  tracking) as evidence accumulates, and regroup around whichever drone is
  closest to a confirmed contact.
- **Red** (the adversary): a single vessel with baseline movement, evasion
  behavior once it senses it may be tracked, and an infiltration objective —
  it wins by reaching a defined zone behind the Blue mothership's spawn
  point undetected, or by never being confirmed within the turn limit.

## Win conditions

- **Blue wins**: Red is detected and held within engagement range of the
  `BlueMothership` for a sustained number of consecutive turns (not a single
  lucky sonar ping).
- **Red wins**: Red reaches the infiltration zone behind the mothership's
  spawn point, or survives to the turn limit without ever being pinned down
  long enough for a Blue win.

## Intended audience

This is primarily a personal/portfolio project exploring probabilistic
search algorithms, turn-based multi-agent coordination, and a full engine →
API → frontend pipeline, rather than a production product with external
users.
