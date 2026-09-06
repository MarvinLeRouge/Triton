🇫🇷 Version française | [🇬🇧 English version](architecture.md)

---

# Architecture - Triton

> Référence technique publique. Voir les architectures [engine](architecture/engine_architecture.fr.md), [API](architecture/api_architecture.fr.md), [frontend](architecture/frontend_architecture.fr.md) et [infrastructure](architecture/infra_architecture.fr.md) pour les détails d'implémentation.

## Vue d'ensemble

Triton est une simulation de lutte anti-sous-marine (ASW) en temps réel, à quatre composants :

- **Engine** - Python pur + NumPy, aucune dépendance UI ou transport. Porte toute la logique de jeu : la grille, les entités, le modèle de détection sonar, les cartes de probabilité bayésiennes, les stratégies de recherche, et la boucle de tour (`Simulation`).
- **API** - FastAPI, couche de transport légère au-dessus de l'engine. Ouvre une `Simulation` par connexion WebSocket (`/ws/game`) et diffuse son état sérialisé à chaque tour.
- **Frontend** - Vue 3 + Vite + TypeScript, rendu via l'API Canvas. Un moteur de rendu passif entièrement piloté par les messages WebSocket, sans logique de jeu côté client.
- **Infrastructure** - Docker Compose + Traefik, même schéma de routage en dev et en prod.

## Structure du projet

```
triton/
├── engine/
│   ├── grid.py               # Grille discrétisée 2D
│   ├── entities.py            # Faction, DetectionState, drones/vaisseaux
│   ├── sonar_model.py          # Loi de probabilité de détection
│   ├── probability_map.py       # Carte de croyance bayésienne par drone
│   ├── map_fusion.py             # Consensus multi-drone
│   ├── search_strategy.py         # Stratégies de mouvement des drones
│   └── simulation.py               # Boucle de tour, évaluation des conditions de victoire
├── api/
│   └── main.py                # Application FastAPI : /health, /ws/game
├── frontend/
│   └── src/
│       ├── stores/game.ts      # Store Pinia, connexion WebSocket
│       └── components/          # GameCanvas.vue + helpers de dessin
├── docker-compose.yml            # Stack dev (routée par Traefik, hot-reload)
├── docker-compose.prod.yml        # Stack prod (images buildées, TLS)
└── docs/
    ├── architecture/    # architecture engine/api/frontend/infra
    ├── adr/             # architecture decision records
    └── guides/          # guides développeur/utilisateur
```

## Pour aller plus loin

- [Architecture engine](architecture/engine_architecture.fr.md)
- [Architecture API](architecture/api_architecture.fr.md)
- [Architecture frontend](architecture/frontend_architecture.fr.md)
- [Architecture infrastructure](architecture/infra_architecture.fr.md)
- [Registre des décisions d'architecture](adr/README.md)
- [Guide développeur](guides/developer_guide.fr.md)
- [Contexte produit](product-context.fr.md)
- [Opérations](operations.fr.md)
