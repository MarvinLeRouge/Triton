[🇫🇷 Version française](infra_architecture.fr.md) | 🇬🇧 English version

---

# Infrastructure Architecture

Docker Compose + Traefik, same routing shape in dev and prod (see
[docs/operations.md](../operations.md) for the full setup and routing
tables).

| File | Responsibility |
|---|---|
| `Dockerfile.backend` | Backend image — `python:3.13-slim`, dependencies installed via `uv sync --no-dev --frozen`, runs `uvicorn api.main:app` |
| `frontend/Dockerfile` | Frontend image — multi-stage: `node:22-alpine` builds the Vite bundle, then served as static files by `nginx:alpine` |
| `docker-compose.yml` | Dev stack — backend/frontend run from source with hot-reload (`uvicorn --reload`, `npm run dev`), routed via Traefik labels on the shared `traefik-public` network |
| `docker-compose.prod.yml` | Prod stack — both services run from their built images, `websecure` (HTTPS) entrypoint, TLS via Let's Encrypt, domain from `${DOMAIN}` |

## Routing split

Both compose files route `/api/*` to the backend with the prefix stripped,
and `/ws/*` to the backend without stripping (WebSocket), leaving everything
else to the frontend service — see the routing tables in
[docs/operations.md](../operations.md).

## Status

Local deployment via Traefik is in place and used daily in development.
Remote/public demo deployment (against the user's existing production
Traefik instance) is configured (`docker-compose.prod.yml`) but not yet
executed — planned for Phase 7.
