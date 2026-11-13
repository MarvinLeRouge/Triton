🇫🇷 Version française | [🇬🇧 English version](roadmap.md)

---

# Feuille de route

## ✅ Planification

- [x] Cadrage du projet & planification par phases — architecture, conventions de nommage (factions Blue/Red), paramètres par défaut de la simulation, outillage (uv, ruff, mypy, ESLint, Prettier, Vitest, Codecov)

## 🔜 Prévu

- [x] **Phase 1 — Fondations** : grille, entités, placement initial, pipeline complet (engine, API, frontend, Docker/Traefik)
- [x] **Phase 2 — Modèle sonar** : cône de détection (POD), probabilité de détection
- [x] **Phase 3 — Carte bayésienne** : carte de probabilité, mise à jour bayésienne, diffusion temporelle
- [x] **Phase 4 — Intelligence des drones** : stratégies de recherche, machine à états de détection
- [x] **Phase 5 — Comportement Red** : évasion, objectif d'infiltration
- [x] **Phase 6 — Coordination multi-drones** : fusion de cartes, regroupement de la flotte
- [ ] **Phase 7 — Finalisation & scénarios** : configuration, rejouabilité, audit sécurité OWASP, passe design, déploiement de démo local/distant, documentation des choix de conception

## Section 1 - Maintenance

- [x] FIX-001 - Corriger la vulnérabilité critique npm audit du frontend (shell-quote)
- [x] CHORE-001 - Mise à jour des dépendances, passage à Python 3.14, mise en place de Dependabot
- [x] CHORE-002 - Aligner Node 26 sur la CI et le dev, mises à jour Dependabot uv limitées au lockfile
- [x] FIX-002 - Corriger les vulnérabilités vitest du frontend (@vitest/mocker)
- [x] CHORE-003 - Migrer le frontend vers vitest 5
- [x] CHORE-004 - Bloquer les montées de version mineure de l'image Python dans Dependabot
- [x] CI-001 - Lancer la CI sur la PR du bot changelog pour que son auto-merge aboutisse
