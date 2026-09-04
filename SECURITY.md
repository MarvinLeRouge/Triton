[🇫🇷 Version française](SECURITY.fr.md) | 🇬🇧 English version

---

# Security Policy

## Scope

Triton is a turn-based simulation with no user accounts, no authentication,
and no persisted personal data — each session is an ephemeral WebSocket
connection running a self-contained simulation. The main attack surface is
the FastAPI/WebSocket API and the Traefik-fronted demo deployment.

## Supported versions

Only the latest commit on `main` is supported. There are no maintained
release branches.

## Reporting a vulnerability

Report a vulnerability by contacting the project maintainer directly (see the
GitHub profile linked from this repository) rather than opening a public
issue. Include enough detail to reproduce the issue. Reports will be
acknowledged and addressed on a best-effort basis, given this is a personal
project.

## Current status

No formal security audit has been performed yet. A dedicated OWASP-based
audit (API/WebSocket surface, input handling, CORS/Traefik configuration,
dependencies) is planned for Phase 7 of the roadmap, once the API and
frontend surfaces are stable — see [docs/roadmap.md](docs/roadmap.md).
