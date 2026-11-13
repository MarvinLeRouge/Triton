[🇫🇷 Version française](roadmap.fr.md) | 🇬🇧 English version

---

# Roadmap

## ✅ Planning

- [x] Project scoping & phase planning — architecture, naming conventions (Blue/Red factions), default simulation parameters, tooling (uv, ruff, mypy, ESLint, Prettier, Vitest, Codecov)

## 🔜 Planned

- [x] **Phase 1 — Foundations**: grid, entities, initial placement, end-to-end pipeline (engine, API, frontend, Docker/Traefik)
- [x] **Phase 2 — Sonar model**: cone-shaped POD, detection probability
- [x] **Phase 3 — Bayesian map**: probability map, Bayesian update, temporal diffusion
- [x] **Phase 4 — Drone intelligence**: search strategies, detection state machine
- [x] **Phase 5 — Red behavior**: evasion, infiltration objective
- [x] **Phase 6 — Multi-drone coordination**: map fusion, fleet regroup
- [ ] **Phase 7 — Polish & scenarios**: configuration, replayability, OWASP security audit, design pass, local/remote demo deployment, design decisions doc

## Section 1 - Maintenance

- [x] FIX-001 - Fix the critical npm audit finding in the frontend (shell-quote)
- [x] CHORE-001 - Upgrade dependencies, move to Python 3.14, set up Dependabot
- [x] CHORE-002 - Align Node 26 across CI and dev, lockfile-only Dependabot updates for uv
- [x] FIX-002 - Fix the vitest dev advisories in the frontend (@vitest/mocker)
- [x] CHORE-003 - Migrate the frontend to vitest 5
- [x] CHORE-004 - Keep the Python base image on its current minor in Dependabot
