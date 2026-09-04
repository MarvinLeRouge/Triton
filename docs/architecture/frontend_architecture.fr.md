🇫🇷 Version française | [🇬🇧 English version](frontend_architecture.md)

---

# Architecture du frontend

Vue 3 + Vite + TypeScript, rendu via l'API Canvas. Pas de routing (vue
unique), aucune logique métier — un afficheur passif piloté par les
messages WebSocket.

| Fichier | Responsabilité |
|---|---|
| `src/App.vue` | Composant racine |
| `src/stores/game.ts` | Store Pinia — porte la connexion WebSocket (`connect`/`disconnect`), le `ConnectionStatus`, et le dernier état de jeu reçu |
| `src/components/GameCanvas.vue` | Rend l'état de jeu courant sur un `<canvas>` |
| `src/components/canvas-helpers.ts` | Fonctions de dessin pures utilisées par `GameCanvas.vue` (grille, entités, cônes sonar, heatmap) |

## Client WebSocket

`game.ts` ouvre `ws(s)://<host>/ws/game` (protocole choisi selon
`window.location.protocol`), suit le statut de connexion via
`idle → connecting → connected → disconnected/error`, et stocke chaque
payload `Simulation.to_dict()` reçu tel quel pour que `GameCanvas.vue` le
rende. Il n'y a aucune logique de jeu côté client — chaque décision
(mouvement, détection, condition de victoire) est calculée côté serveur.

## Notes de conception

Le design visuel (palette, iconographie, accessibilité) n'est
volontairement pas traité ici pour l'instant — voir
[docs/design-system.fr.md](../design-system.fr.md) pour l'espace réservé
décrivant ce qui sera fait durant la passe `impeccable` de la Phase 7.
