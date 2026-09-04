🇫🇷 Version française | [🇬🇧 English version](developer_guide.md)

---

# Guide développeur

## Installation locale

Voir le [README](../../README.fr.md) racine pour les prérequis et
commandes, et [docs/operations.fr.md](../operations.fr.md) pour le setup
Docker + Traefik.

## Carte des modules

Voir [docs/architecture/](../architecture/) pour le détail par composant
(engine, API, frontend, infra).

## Référence API

- REST : documentation Swagger interactive générée par FastAPI, servie sur
  `/docs` (par ex. `http://localhost:8000/docs`, ou `.../api/docs` derrière
  Traefik).
- WebSocket (`/ws/game`, non couvert par Swagger) : le serveur envoie un
  payload JSON à la connexion puis après chaque tour, de la forme
  `Simulation.to_dict()` :

  ```json
  {
    "turn": 12,
    "result": "in_progress",
    "mothership": { "row": 10, "col": 4 },
    "drones": [
      {
        "row": 8, "col": 6, "heading": [1, 0],
        "detection_state": "searching",
        "strategy": "greedy_max_probability"
      }
    ],
    "vessel": { "row": 20, "col": 30 },
    "detection_events": [],
    "probability_map": [[0.001, 0.002, "..."], "..."]
  }
  ```

  `result` vaut `in_progress`, `blue_wins`, ou `red_wins`. La connexion est
  une `Simulation` par socket — il n'y a pas encore de requête que le client
  puisse renvoyer (contrôles de lecture prévus en Phase 7).

## Brancher un nouvel algorithme

Le moteur est conçu pour qu'une nouvelle logique de décision puisse être
ajoutée sans toucher à la boucle de tour de `Simulation`.

### Une nouvelle stratégie de recherche (comment les drones cherchent)

Implémenter `SearchStrategy` (`engine/search_strategy.py`) :

```python
class MyStrategy(SearchStrategy):
    @property
    def name(self) -> str:
        return "my_strategy"  # identifiant stable, exposé à l'API/frontend

    def next_target(
        self, position: tuple[int, int], speed: int,
        grid: Grid, probability_map: ProbabilityMap,
    ) -> tuple[int, int]:
        ...  # retourne la case (row, col) vers laquelle se déplacer ce tour
```

Ajouter une instance de cette stratégie au pool passé à
`StrategyAssignment` lors de la construction d'une `Simulation`. Chaque
drone tire indépendamment une chance de basculer vers une stratégie
choisie au hasard dans ce pool à chaque tour
(`StrategyAssignment.advance()`), donc une nouvelle stratégie n'a qu'à être
présente dans le pool pour commencer à être utilisée — aucun autre
câblage nécessaire.

### Un nouveau comportement Red (évasion, mouvement)

Le comportement de Red vit dans `engine/red_behavior.py` sous forme de
simples fonctions (`red_baseline_target`, `red_evasion_target`,
`blue_units_within_range`) plutôt qu'une interface de stratégie, Red ayant
un processus de décision unique et déterministe (pas un pool tournant).
Ajouter une nouvelle fonction suivant la même forme de signature (position
courante, positions Blue/info de menace, grille → prochaine cible) et
l'appeler depuis l'étape de mouvement Red de `Simulation`, à la place (ou en
complément, derrière une condition) de l'existante.

### Une nouvelle loi de détection sonar

`SonarModel` (`engine/sonar_model.py`) encapsule la géométrie du cône et la
loi de probabilité de détection dans une seule classe. Pour essayer une loi
différente (par ex. une fonction de décroissance différente, un demi-angle
de cône différent), soit modifier directement son intérieur, soit
introduire une deuxième implémentation avec la même surface publique
(`range_cells`, la méthode de probabilité de détection) et l'injecter
partout où `Simulation` est construite.

## Conventions de test

Miroir la structure des sources sous `tests/engine/`, `tests/api/`,
`frontend/src/**/__tests__/`. Le TDD (red-green-refactor) est le workflow
attendu pour les changements engine et API.
