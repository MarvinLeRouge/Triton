🇫🇷 Version française | [🇬🇧 English version](operations.md)

---

# Opérations

## Développement local

### Sans Docker

Lancer le backend et le frontend séparément (voir le [README](../README.fr.md)
racine pour les commandes exactes). Le frontend a besoin de
`VITE_WS_URL=ws://localhost:8000/ws/game` dans `frontend/.env` pour atteindre
un backend lancé directement via `uvicorn`.

### Avec Docker + Traefik (recommandé)

Ceci reproduit localement le routage de production, en HTTP simple.

#### 1. Une seule fois : instance Traefik locale partagée

Ce setup est global à la machine (partagé entre tout projet local utilisant
le réseau `traefik-public`), pas spécifique à Triton, mais requis avant de
lancer Triton via Docker Compose.

```bash
docker network create traefik-public
mkdir -p ~/traefik-local
```

Créer `~/traefik-local/docker-compose.yml` :

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

#### 2. Ajouter l'entrée DNS locale

```bash
echo "127.0.0.1 triton.marvinlerouge.local" | sudo tee -a /etc/hosts
```

#### 3. Lancer Triton

```bash
docker compose up
```

Disponible sur `http://triton.marvinlerouge.local`.

### Table de routage (dev)

| URL | Cible |
|---|---|
| `http://triton.marvinlerouge.local/` | Serveur de dev Vite (HMR activé) |
| `http://triton.marvinlerouge.local/api/*` | FastAPI (préfixe `/api` retiré) |
| `http://triton.marvinlerouge.local/ws/*` | WebSocket FastAPI (pas de retrait de préfixe) |

Défini dans `docker-compose.yml` ; le conteneur frontend lance
`npm run dev` avec hot module reload, le conteneur backend lance
`uvicorn --reload`.

## Déploiement en production

Défini dans `docker-compose.prod.yml`, avec le même découpage de routage
`/api` et `/ws` qu'en dev, sur l'entrypoint `websecure` (HTTPS, port 443)
avec TLS via Let's Encrypt (`certresolver=letsencrypt`). Les deux services
buildent leur propre image (`Dockerfile.backend`, `frontend/Dockerfile`) au
lieu de tourner depuis les sources avec un serveur de dev.

Définir le domaine public dans `.env` (copié depuis `.env.example`) :

```bash
DOMAIN=triton.votredomaine.com
```

```bash
docker compose -f docker-compose.prod.yml up -d
```

**Statut** : cette configuration existe et reflète le setup dev, mais un
déploiement de démo public distant (sur l'instance Traefik de production
existante de l'utilisateur) n'a pas encore été exécuté — prévu en Phase 7
(voir [docs/roadmap.fr.md](roadmap.fr.md)).

## CI/CD

`.github/workflows/ci.yml` s'exécute sur push vers `main`, `develop`,
`phase-**`, et sur chaque pull request : lint backend (ruff check + format),
mypy strict, pytest avec couverture ; lint frontend (oxlint + ESLint),
vue-tsc, vitest avec couverture. Les deux jobs envoient leur couverture à
Codecov (OIDC, pas de token stocké) avec des flags `backend`/`frontend`
séparés. Aucune étape de déploiement — le déploiement est manuel (commandes
`docker compose` ci-dessus).
