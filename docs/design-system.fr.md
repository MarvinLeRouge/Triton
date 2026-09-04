🇫🇷 Version française | [🇬🇧 English version](design-system.md)

---

# Système de design

**Statut** : préparatoire. Le frontend affiche actuellement une vue Canvas
fonctionnelle mais non stylée (grille, entités, cônes sonar, heatmap de
probabilité), sans passe de design visuel volontaire pour l'instant. Ce
document décrit les sections que ce fichier est censé contenir une fois la
passe de design `impeccable` de la Phase 7 réalisée, afin que le périmètre
prévu soit visible avant que le travail ne commence. Le contenu ci-dessous
sera remplacé par les décisions de design réelles et évaluées à ce moment-là
— à traiter comme un espace réservé, pas comme une spécification arrêtée.

## Sections attendues (à remplir en Phase 7)

- **Palette de couleurs** : une échelle cohérente pour la heatmap de
  probabilité (confiance faible → élevée), des couleurs distinctes pour les
  entités Blue/Red et les cônes sonar, lisibles en contexte clair comme
  sombre si un bascule de thème est ajouté.
- **Iconographie des entités** : comment `BlueMothership`, `BlueDrone` et
  `RedVessel` sont distingués visuellement sur le canvas, y compris des
  indicateurs d'état de détection (recherche / signalement / confirmation /
  suivi).
- **Hiérarchie visuelle** : ce qui attire l'œil en premier pendant une
  simulation en cours (détections actives, le mothership, la bannière de
  tour/résultat).
- **Accessibilité** : ratios de contraste pour la heatmap et les marqueurs
  d'entités, indices non dépendants de la couleur pour l'état de détection
  (forme, pas seulement teinte).
- **Comportement responsive** : comment le canvas et le panneau latéral
  s'adaptent à différentes tailles de viewport.

## Pourquoi c'est différé

Selon la décision de roadmap propre au projet, la passe de design
`impeccable` est volontairement programmée en Phase 7, une fois l'API, le
protocole WebSocket et les surfaces UI stabilisés — la faire plus tôt aurait
signifié refaire le travail au fil des évolutions du layout du canvas sur
les Phases 1 à 6 (cônes, heatmap, machine à états, etc.).
