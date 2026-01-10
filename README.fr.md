# Automatisation du Rapport de Guerre Clash Royale

Ce projet récupère automatiquement les statistiques de guerre pour le clan CCPOM via l'API officielle de Clash Royale et publie un rapport du top 5 sur Discord chaque lundi.

## Structure du Projet

*   `analyze_war.py`: script principal pour les appels API et l'analyse des données
*   `.github/workflows/main.yml`: workflow GitHub Actions pour l'exécution automatique
*   `requirements.txt`: dépendances Python

## Configuration Initiale

### 1. API Clash Royale

Créez un jeton sur le portail des développeurs de Clash Royale.
Étant donné que les GitHub Actions utilisent des adresses IP sortantes dynamiques, vous devrez peut-être utiliser un proxy ou mettre à jour le jeton si la connexion est refusée.

### 2. Webhook Discord

Dans les paramètres de votre serveur Discord, créez un Webhook pour le canal souhaité et copiez l'URL.

### 3. Secrets GitHub

Ajoutez les variables suivantes dans `Settings > Secrets and variables > Actions` de votre dépôt :

*   `CLASH_API_TOKEN`: votre jeton d'API Supercell
*   `DISCORD_WEBHOOK_URL`: l'URL complète du Webhook Discord

## Logique du Script

Le script interroge le point de terminaison `riverracelog` pour récupérer l'historique des guerres.
Il calcule :

*   Les 5 meilleurs scores (renommée) de la guerre terminée la plus récente
*   Les 5 meilleurs joueurs sur la base d'une moyenne mobile des 4 dernières semaines

## Exécution

### Automatique

Le script s'exécute automatiquement chaque lundi à 08h00 UTC via GitHub Actions.

### Manuelle

Vous pouvez déclencher le script manuellement via l'onglet `Actions` sur GitHub en sélectionnant `Clash Royale War Report` et en cliquant sur `Run workflow`.
