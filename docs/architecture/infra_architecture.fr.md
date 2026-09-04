🇫🇷 Version française | [🇬🇧 English version](infra_architecture.md)

---

# Architecture infra

Docker Compose + Traefik, même forme de routage en dev et en prod (voir
[docs/operations.fr.md](../operations.fr.md) pour le setup complet et les
tables de routage).

| Fichier | Responsabilité |
|---|---|
| `Dockerfile.backend` | Image backend — `python:3.13-slim`, dépendances installées via `uv sync --no-dev --frozen`, lance `uvicorn api.main:app` |
| `frontend/Dockerfile` | Image frontend — multi-stage : `node:22-alpine` build le bundle Vite, puis servi en fichiers statiques par `nginx:alpine` |
| `docker-compose.yml` | Stack dev — backend/frontend tournent depuis les sources avec hot-reload (`uvicorn --reload`, `npm run dev`), routés via des labels Traefik sur le réseau partagé `traefik-public` |
| `docker-compose.prod.yml` | Stack prod — les deux services tournent depuis leurs images buildées, entrypoint `websecure` (HTTPS), TLS via Let's Encrypt, domaine depuis `${DOMAIN}` |

## Découpage du routage

Les deux fichiers compose routent `/api/*` vers le backend avec le préfixe
retiré, et `/ws/*` vers le backend sans retrait (WebSocket), laissant tout
le reste au service frontend — voir les tables de routage dans
[docs/operations.fr.md](../operations.fr.md).

## Statut

Le déploiement local via Traefik est en place et utilisé quotidiennement en
développement. Le déploiement de démo distant/public (sur l'instance
Traefik de production existante de l'utilisateur) est configuré
(`docker-compose.prod.yml`) mais pas encore exécuté — prévu en Phase 7.
