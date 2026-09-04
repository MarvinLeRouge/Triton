[🇫🇷 Version française](frontend_architecture.fr.md) | 🇬🇧 English version

---

# Frontend Architecture

Vue 3 + Vite + TypeScript, rendering via the Canvas API. No routing (single
view), no backend logic — a passive renderer driven by WebSocket messages.

| File | Responsibility |
|---|---|
| `src/App.vue` | Root component |
| `src/stores/game.ts` | Pinia store — owns the WebSocket connection (`connect`/`disconnect`), `ConnectionStatus`, and the latest received game state |
| `src/components/GameCanvas.vue` | Renders the current game state onto a `<canvas>` |
| `src/components/canvas-helpers.ts` | Pure drawing helper functions used by `GameCanvas.vue` (grid, entities, sonar cones, heatmap) |

## WebSocket client

`game.ts` opens `ws(s)://<host>/ws/game` (protocol chosen from
`window.location.protocol`), tracks connection status through
`idle → connecting → connected → disconnected/error`, and stores each
incoming `Simulation.to_dict()` payload as-is for `GameCanvas.vue` to render.
There is no client-side game logic — every decision (movement, detection,
win condition) is computed server-side.

## Design notes

Visual design (palette, iconography, accessibility) is intentionally not
addressed here yet — see [docs/design-system.md](../design-system.md) for
the placeholder describing what will land during the Phase 7 `impeccable`
pass.
