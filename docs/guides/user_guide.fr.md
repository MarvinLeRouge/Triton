🇫🇷 Version française | [🇬🇧 English version](user_guide.md)

---

# Guide joueur

## Lancer une simulation

Ouvrir le frontend (voir le [README](../../README.fr.md) pour le setup
local). Une nouvelle simulation démarre automatiquement dès que la page se
connecte en WebSocket — il n'y a pas encore d'écran de lobby ou de
configuration (prévu par le travail de configuration de scénarios de la
Phase 7).

## Lire la vue

- **Grille** : le champ de bataille discrétisé, origine en haut à gauche.
- **Mothership** : la base Blue stationnaire.
- **Drones** : la flotte Blue en recherche. Chacun affiche son cap actuel et
  son cône sonar.
- **Heatmap de probabilité** : la carte de croyance fusionnée — les cases
  les plus claires sont celles où Red est le plus susceptible de se trouver,
  d'après tout ce que la flotte a perçu jusque-là.
- **Navire Red** : affiché uniquement une fois détecté ; sinon sa position
  vous est inconnue, exactement comme pour la flotte Blue.

## États de détection

La relation de chaque drone avec un contact évolue à travers quatre états au
fur et à mesure que les preuves s'accumulent : **recherche** (aucun contact)
→ **signalement** (un premier ping non confirmé) → **confirmation** (pings
répétés) → **suivi** (verrouillé). Dès qu'un drone atteint confirmation ou
suivi, le reste de la flotte abandonne sa recherche indépendante et se
regroupe autour de lui — cette convergence est le signe le plus clair qu'une
traque est en cours.

## Résultat

Une partie se termine quand un camp gagne ou que la limite de tours est
atteinte :

- **Victoire Blue** si Red est suivi et maintenu près du mothership pendant
  assez de tours consécutifs.
- **Victoire Red** s'il atteint la zone d'infiltration derrière le point de
  spawn du mothership sans être détecté, ou s'il survit jusqu'à la limite de
  tours.

Il n'y a actuellement aucun contrôle de lecture (pause/pas à pas/replay) —
une partie se déroule en continu une fois connectée ; c'est prévu pour la
Phase 7.
