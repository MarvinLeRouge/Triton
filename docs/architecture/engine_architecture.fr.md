🇫🇷 Version française | [🇬🇧 English version](engine_architecture.md)

---

# Architecture du moteur

Python pur + NumPy, aucune dépendance UI ou transport. Toute la logique de
jeu vit ici ; la couche API se contente de le piloter et de sérialiser son
état.

| Module | Responsabilité |
|---|---|
| `grid.py` | Grille discrétisée en 2D (`Grid`), origine au coin NO, coordonnées `(ligne, colonne)` |
| `entities.py` | `Faction`, machine à états `DetectionState`, classe de base `Entity`, `BlueMothership`, `BlueDrone`, `RedVessel` |
| `sonar_model.py` | `SonarModel` — loi de probabilité de détection en cône avec décroissance exponentielle selon la distance |
| `probability_map.py` | `ProbabilityMap` — carte de croyance bayésienne par drone sur la grille, avec diffusion et mise à jour bayésienne |
| `map_fusion.py` | `fuse_maps()` — fusion consensuelle pure par moyenne élément par élément des cartes de plusieurs drones |
| `search_strategy.py` | `SearchStrategy` (abstraite) et ses implémentations (`GreedyMaxProbability`, `FrontierCoverage`) pilotant le déplacement des drones |
| `strategy_assignment.py` | `StrategyAssignment` — assigne et retire périodiquement la stratégie de recherche active de chaque drone |
| `red_behavior.py` | Mouvement de base de Red, évasion, zone/objectif d'infiltration |
| `fleet_regroup.py` | `regroup_target()` — pas de mouvement pur utilisé quand les drones convergent vers un contact confirmé |
| `simulation.py` | `Simulation` — la boucle de tour : mouvement, balayages sonar, mise à jour/fusion des cartes, regroupement de flotte, évaluation des conditions de victoire (`GameResult`) |

## Points d'extension

Voir [le guide développeur](../guides/developer_guide.fr.md) pour savoir
comment brancher une nouvelle `SearchStrategy`, un nouveau comportement Red,
ou une loi de détection sonar différente sans toucher à la boucle de tour de
`Simulation`.

## Justification approfondie des choix

La justification détaillée par décision (alternatives envisagées,
compromis, évolutions futures possibles) vit dans [docs/adr/](../adr/) pour
les décisions déjà prises, et sera enrichie par la tâche de documentation
dédiée de la Phase 7 pour les choix algorithmiques structurants du moteur
(loi POD, mise à jour bayésienne, diffusion, machine à états de détection) —
voir [docs/roadmap.fr.md](../roadmap.fr.md).
