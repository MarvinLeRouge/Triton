🇫🇷 Version française | [🇬🇧 English version](README.md)

---

# Triton
## Introduction

Triton (Tracking & Reconnaissance In Tactical Operations Network) est une simulation au tour par tour d'une opération de recherche sonar autonome menée par une flotte multi-drones. Guidée par une carte de probabilité bayésienne, la flotte tente de localiser et de suivre un navire ennemi évasif sur une grille discrétisée.

## Concepts clés

- Modèle de détection probabiliste (sonar conique, POD)
- Mise à jour bayésienne de la carte à chaque balayage
- Coordination autonome des drones (optimisation de la couverture)
- Comportement ennemi adaptatif (évasion, contournement, fuite)

## Stack technique

- **Moteur** — Python (NumPy)
- **API** — FastAPI + WebSocket
- **Frontend** — Vue 3 + Vite + Canvas API
- **Infra** — Docker + Traefik

## 🗺️ Feuille de route

### ✅ Planification

- [x] Cadrage du projet & planification par phases — architecture, conventions de nommage (factions Blue/Red), paramètres par défaut de la simulation, outillage (uv, ruff, mypy, ESLint, Prettier, Vitest, Codecov)

### 🔜 Prévu

- [ ] **Phase 1 — Fondations** : grille, entités, placement initial, pipeline complet (engine, API, frontend, Docker/Traefik)
- [ ] **Phase 2 — Modèle sonar** : cône de détection (POD), probabilité de détection
- [ ] **Phase 3 — Carte bayésienne** : carte de probabilité, mise à jour bayésienne, diffusion temporelle
- [ ] **Phase 4 — Intelligence des drones** : stratégies de recherche, machine à états de détection
- [ ] **Phase 5 — Comportement Red** : évasion, objectif d'infiltration
- [ ] **Phase 6 — Coordination multi-drones** : fusion de cartes, regroupement de la flotte
- [ ] **Phase 7 — Finalisation & scénarios** : configuration, rejouabilité, déploiement de démo
