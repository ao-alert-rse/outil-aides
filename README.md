# Détecteur d'aides — Nam & Kouji

Outil interne pour identifier les aides publiques (RSE / transition écologique / RH / formation) applicables à une entreprise à partir de son SIRET.

## Fonctionnement

- Recherche par SIRET (API publique recherche-entreprises.api.gouv.fr), détection automatique de l'OPCO via IDCC.
- Base d'aides hébergée sur Supabase (table `aides`), chargée au démarrage après connexion.
- Accès réservé aux conseillers Nam & Kouji (compte créé par invitation, pas d'auto-inscription).

## Ajouter un conseiller

Dashboard Supabase → Authentication → Users → Invite user.

## Mettre à jour la base d'aides

Directement dans le dashboard Supabase (Table Editor → `aides`), ou via l'éditeur SQL. Le fichier [`schema.sql`](./schema.sql) documente la structure de la table et sert de base pour une ré-initialisation si besoin.

## Toutes les aides restent à valider auprès de l'organisme concerné avant d'être proposées à un client.
