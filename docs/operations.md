[🇫🇷 Version française](operations.fr.md) | 🇬🇧 English version

---

# Operations

## Local development

### Without Docker

Run the backend and frontend separately (see the root [README](../README.md)
for the exact commands). The frontend needs `VITE_WS_URL=ws://localhost:8000/ws/game`
in `frontend/.env` to reach a backend started with `uvicorn` directly.

### With Docker + Traefik (recommended)

This mirrors the production routing locally, over plain HTTP.

#### 1. One-time: shared local Traefik instance

This setup is machine-wide (shared across any local project using the
`traefik-public` network), not specific to Triton, but is required before
running Triton via Docker Compose.

```bash
docker network create traefik-public
mkdir -p ~/traefik-local
```

Create `~/traefik-local/docker-compose.yml`:

```yaml
services:
  traefik:
    image: traefik:v3
    container_name: traefik-local
    restart: unless-stopped
    command:
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--providers.docker.network=traefik-public"
      - "--entrypoints.web.address=:80"
      - "--log.level=INFO"
    ports:
      - "80:80"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
    networks:
      - traefik-public

networks:
  traefik-public:
    external: true
```

```bash
cd ~/traefik-local && docker compose up -d
```

#### 2. Add the local DNS entry

```bash
echo "127.0.0.1 triton.marvinlerouge.local" | sudo tee -a /etc/hosts
```

#### 3. Start Triton

```bash
docker compose up
```

Available at `http://triton.marvinlerouge.local`.

### Dev routing summary

| URL | Target |
|---|---|
| `http://triton.marvinlerouge.local/` | Vite dev server (HMR enabled) |
| `http://triton.marvinlerouge.local/api/*` | FastAPI (`/api` prefix stripped) |
| `http://triton.marvinlerouge.local/ws/*` | FastAPI WebSocket (no prefix strip) |

Defined in `docker-compose.yml`; the frontend container runs `npm run dev`
with hot module reload, the backend container runs `uvicorn --reload`.

## Production deployment

Defined in `docker-compose.prod.yml`, using the same `/api` and `/ws` routing
split as dev, over the `websecure` (HTTPS, port 443) entrypoint with TLS via
Let's Encrypt (`certresolver=letsencrypt`). Both services build their own
image (`Dockerfile.backend`, `frontend/Dockerfile`) rather than running from
source with a dev server.

Set the public domain in `.env` (copy from `.env.example`):

```bash
DOMAIN=triton.yourdomain.com
```

```bash
docker compose -f docker-compose.prod.yml up -d
```

**Status**: this configuration exists and mirrors the dev setup, but a
public remote demo deployment (against the user's existing production
Traefik instance) has not been executed yet — planned for Phase 7 (see
[docs/roadmap.md](roadmap.md)).

## CI/CD

`.github/workflows/ci.yml` runs on push to `main`, `develop`, `phase-**`
branches, and on every pull request: backend lint (ruff check + format),
mypy strict, pytest with coverage; frontend lint (oxlint + ESLint), vue-tsc,
vitest with coverage. Both jobs upload coverage to Codecov (OIDC, no stored
token) with separate `backend`/`frontend` flags. There is no deploy step —
deployment is manual (`docker compose` commands above).
