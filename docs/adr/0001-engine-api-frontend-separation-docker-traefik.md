# ADR-0001: Engine/API/frontend separation with Docker + Traefik from Phase 1

- Status: Accepted
- Date: 2026-06-21
- Source: PR #9, #10 (`phase-1-foundations/feat/infra-docker-traefik`)

## Context

Triton needed a runnable end-to-end pipeline as early as possible (grid and
entities → API → Canvas rendering) to validate the architecture before any
game logic accumulated, plus local/production parity for the eventual demo
deployment.

## Decision

Split into three independently testable layers from the start: a pure
Python engine with zero UI or transport dependency, a FastAPI + WebSocket
transport layer, and a Vue 3 + Canvas renderer — orchestrated via Docker
Compose behind Traefik, using the same routing shape (`/api/*`, `/ws/*`,
catch-all to the frontend) in both dev and prod. Traefik was introduced in
Phase 1 rather than deferred to a later "productionization" phase.

## Alternatives considered

- A single monolithic process (e.g. server-rendered pages driving the
  simulation directly) — rejected, it would couple simulation turn timing to
  render timing and rule out a Canvas-based, continuously updating view.
- Deferring Docker/Traefik setup to a later phase, once the API surface
  stabilized — rejected, judged cheaper to get the routing shape right once,
  early, than to retrofit it after the API/WebSocket surface grew across
  later phases.

## Consequences / future evolution

Dev/prod parity exists from day one — the two `docker-compose*.yml` files
differ only in image build vs. source mount and TLS entrypoint, not in
routing logic (see [docs/operations.md](../operations.md)). Trade-off: any
routing change (new endpoint, new path prefix) must be made in both compose
files. Remote/public demo deployment against a real Traefik instance is
configured but not yet executed — planned for Phase 7.
