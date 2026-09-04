🇫🇷 Version française | [🇬🇧 English version](api_architecture.md)

---

# Architecture de l'API

Application FastAPI (`api/main.py`), fine couche de transport au-dessus du
moteur : elle ne porte aucune logique de jeu, se contente de créer/faire
avancer une `Simulation` et d'en sérialiser l'état.

| Endpoint | Rôle |
|---|---|
| `GET /health` | Vérification de disponibilité |
| `WS /ws/game` | Ouvre une nouvelle `Simulation` par connexion, envoie son état sérialisé (`Simulation.to_dict()`) à la connexion puis après chaque tour, jusqu'à la déconnexion du socket ou la fin de partie |

## Référence API live

La documentation OpenAPI interactive (Swagger UI) est générée par FastAPI à
l'exécution : lancer le backend et ouvrir `/docs` (par ex.
`http://localhost:8000/docs`, ou `http://triton.marvinlerouge.local/api/docs`
derrière Traefik). Elle couvre la route `GET /health` ; le protocole
WebSocket (forme du message envoyé sur `/ws/game`) n'est pas couvert par
OpenAPI et est documenté à la place dans le
[guide développeur](../guides/developer_guide.fr.md).

## Notes de conception

- Une instance `Simulation` par connexion WebSocket — aucun état partagé
  entre parties concurrentes, aucune persistance.
- La boucle de tour tourne côté serveur à intervalle fixe (`STEP_INTERVAL`) ;
  le frontend n'est qu'un afficheur passif de l'état qu'il reçoit.
