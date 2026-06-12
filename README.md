# Triton
## Introduction

Triton (Tracking & Reconnaissance In Tactical Operations Network) is a turn-based simulation of an autonomous multi-drone sonar search operation. A fleet of search drones, guided by a Bayesian probability map, attempts to locate and track an evasive enemy vessel across a discretized grid.

## Key concepts

- Probabilistic detection model (cone-shaped sonar, POD)
- Bayesian map update on each sensor sweep
- Autonomous drone coordination (coverage optimization)
- Adaptive enemy behavior (evasion, bypass, flight)

## Stack

- **Engine** — Python (NumPy)
- **API** — FastAPI + WebSocket
- **Frontend** — Vue 3 + Vite + Canvas API
- **Infra** — Docker + Traefik

## Status

🚧 Early development
