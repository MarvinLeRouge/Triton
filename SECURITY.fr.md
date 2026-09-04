🇫🇷 Version française | [🇬🇧 English version](SECURITY.md)

---

# Politique de sécurité

## Périmètre

Triton est une simulation au tour par tour sans compte utilisateur, sans
authentification, et sans donnée personnelle persistée : chaque session est
une connexion WebSocket éphémère qui exécute une simulation autonome. La
surface d'attaque principale est l'API FastAPI/WebSocket et le déploiement de
démo derrière Traefik.

## Versions supportées

Seul le dernier commit sur `main` est supporté. Il n'y a pas de branche de
release maintenue.

## Signaler une vulnérabilité

Signaler une vulnérabilité en contactant directement le mainteneur du projet
(voir le profil GitHub lié à ce dépôt) plutôt qu'en ouvrant une issue
publique. Merci d'inclure assez de détails pour reproduire le problème. Les
signalements seront pris en compte et traités au mieux, s'agissant d'un
projet personnel.

## État actuel

Aucun audit de sécurité formel n'a encore été réalisé. Un audit dédié basé
sur l'OWASP (surface API/WebSocket, gestion des entrées, configuration
CORS/Traefik, dépendances) est prévu en Phase 7 de la roadmap, une fois les
surfaces API et frontend stabilisées — voir
[docs/roadmap.fr.md](docs/roadmap.fr.md).
