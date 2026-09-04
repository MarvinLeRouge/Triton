🇫🇷 Version française | [🇬🇧 English version](product-context.md)

---

# Contexte produit

## Ce qu'est Triton

Triton simule un problème classique de recherche et de suivi naval : une
flotte de drones sonar, guidée par une carte probabiliste, doit localiser et
suivre un navire ennemi évasif ("Red") avant qu'il n'atteigne son objectif.
C'est une simulation au tour par tour, déterministe par tour, pas un jeu
temps réel : à chaque tour, chaque entité se déplace et perçoit une fois, la
carte de probabilité se met à jour, et le résultat (victoire Blue, victoire
Red, ou timeout) est évalué.

## Pourquoi ce domaine

La simulation repose sur la théorie de la recherche bayésienne : plutôt que
de suivre la position exacte du navire ennemi, chaque drone Blue maintient
une distribution de probabilité sur sa position possible, mise à jour à
partir de relevés sonar imparfaits (un modèle de probabilité de détection en
cône, pas un capteur binaire "vu/pas vu"). Cela modélise une classe de
problème réelle (recherche et sauvetage, lutte anti-sous-marine, déni de
zone) où l'information parfaite n'est jamais disponible, et où les décisions
doivent se prendre à partir d'un état de croyance.

## Les deux factions

- **Blue** (la flotte jouée) : un `BlueMothership` stationnaire, plus un
  nombre configurable de `BlueDrone`. Les drones recherchent en coopération,
  franchissent les étapes d'une machine à états de détection (recherche →
  signalement → confirmation → suivi) au fur et à mesure que les preuves
  s'accumulent, et se regroupent autour du drone le plus proche d'un contact
  confirmé.
- **Red** (l'adversaire) : un unique navire avec un mouvement de base, un
  comportement d'évasion dès qu'il perçoit qu'il pourrait être suivi, et un
  objectif d'infiltration — il gagne en atteignant une zone définie derrière
  le point de spawn du mothership Blue sans être détecté, ou en ne se
  faisant jamais confirmer avant la limite de tours.

## Conditions de victoire

- **Victoire Blue** : Red est détecté et maintenu à portée d'engagement du
  `BlueMothership` pendant un nombre soutenu de tours consécutifs (pas un
  simple ping sonar isolé).
- **Victoire Red** : Red atteint la zone d'infiltration derrière le point de
  spawn du mothership, ou survit jusqu'à la limite de tours sans jamais être
  immobilisé assez longtemps pour permettre une victoire Blue.

## Public visé

Il s'agit avant tout d'un projet personnel/portfolio explorant les
algorithmes de recherche probabiliste, la coordination multi-agents au tour
par tour, et un pipeline complet engine → API → frontend, plutôt qu'un
produit en production avec des utilisateurs externes.
