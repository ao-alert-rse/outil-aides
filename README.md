# Détecteur d'aides — Nam & Kouji

Outil interne Nam & Kouji pour identifier, à partir du SIRET (ou du nom) d'une entreprise, les aides publiques françaises mobilisables en RSE, transition écologique (TEE), ressources humaines (RH) et formation professionnelle. Pensé pour des conseillers accompagnant des TPE/PME.

**Site en ligne :** https://ao-alert-rse.github.io/outil-aides/ (accès réservé, voir [Authentification](#authentification))
## Reprendre ce projet avec Claude Code

Ce projet a été conçu pour pouvoir être repris facilement, même par quelqu'un qui ne l'a pas développé à l'origine. L'application est volontairement simple : un site statique (HTML/CSS/JS) hébergé sur GitHub Pages, avec une base de données Supabase.

Si vous reprenez le projet, le plus simple est de vous appuyer sur **Claude Code**, qui peut vous aider à comprendre l'architecture, diagnostiquer un problème ou implémenter une évolution sans avoir à repartir de zéro.

### Option A — Claude Code Desktop (recommandé)

C'est la solution la plus simple si vous n'êtes pas à l'aise avec la ligne de commande.

#### 1. Télécharger le projet

Aller sur le dépôt GitHub :

```text
https://github.com/ao-alert-rse/outil-aides
```

Puis :

1. Cliquer sur le bouton vert **Code**.
2. Cliquer sur **Download ZIP**.
3. Décompresser le dossier où vous le souhaitez.

Aucun compte GitHub n'est nécessaire pour cette étape.

#### 2. Installer Claude Code Desktop

Télécharger Claude Code Desktop :

```text
https://claude.com/claude-code
```

Puis :

1. Installer l'application.
2. Se connecter avec un compte Anthropic.

#### 3. Ouvrir le projet dans Claude

Depuis l'écran d'accueil de Claude Code :

**Open project** → sélectionner le dossier décompressé à l'étape précédente.

Claude peut maintenant lire l'ensemble du projet.

#### 4. Donner le bon contexte à Claude

Au début de la toute première session, demandez-lui explicitement :

> Lis entièrement `README.md` avant de faire quoi que ce soit.

Si le dépôt contient également un fichier `CLAUDE.md`, demandez aussi :

> Lis également `CLAUDE.md`, il contient les règles de travail du projet.

Cette étape est importante : Claude ne connaît pas automatiquement l'architecture ni les choix de conception du projet.

#### 5. Lancer le projet localement

Aucune dépendance n'est nécessaire, aucun build, aucun `npm install`.

Lancer simplement :

```bash
python -m http.server 8080
```

Puis ouvrir :

```text
http://localhost:8080/index.html
```

---

### Option B — Claude Code en terminal

Si vous êtes à l'aise avec Git :

```bash
git clone https://github.com/ao-alert-rse/outil-aides.git
cd outil-aides
claude
```

Claude utilise automatiquement le dossier courant comme projet.

Pour lancer l'application :

```bash
python -m http.server 8080
```

Puis ouvrir :

```text
http://localhost:8080/index.html
```

---

### Ce qu'il faut récupérer pour pouvoir maintenir le projet

Le code seul ne suffit pas. Demandez également à la personne qui vous transmet le projet :

- un accès au projet Supabase ;
- l'URL du projet (`SUPABASE_URL`) ;
- la clé publique (`SUPABASE_ANON_KEY`) ;
- un compte utilisateur de l'application ;
- éventuellement la clé `SERVICE_ROLE` si vous devez recréer ou administrer la base.

Sans ces accès :

- vous pourrez lire et modifier le code ;
- mais vous ne pourrez pas tester complètement l'application.

---

### Exemples de demandes utiles à faire à Claude

Comprendre le projet :

> Explique-moi l'architecture de ce projet comme si je le reprenais aujourd'hui.

Comprendre un fichier :

> Explique-moi le rôle de `index.html` et ses interactions avec Supabase.

Ajouter une fonctionnalité :

> Je veux ajouter une nouvelle fonctionnalité. Propose une implémentation simple et cohérente avec l'architecture existante.

Corriger un bug :

> Voici le problème observé. Analyse-le et propose un correctif minimal.

Faire un audit :

> Fais un audit du projet et indique les points fragiles ou les améliorations possibles.

---

### Une bonne habitude à prendre

Claude ne garde pas automatiquement la mémoire de vos sessions précédentes.

Au début de chaque nouvelle session importante, redonnez toujours le contexte :

- ce que vous voulez faire ;
- le fichier concerné ;
- les contraintes éventuelles.

Par exemple :

> Lis le README puis aide-moi à ajouter une fonctionnalité sans introduire de framework ni de build.

---

### Principes du projet

L'application a volontairement été conçue pour rester extrêmement simple :

- site statique HTML/CSS/JS ;
- aucun framework ;
- aucune étape de build ;
- aucun serveur ;
- GitHub Pages pour l'hébergement ;
- Supabase pour la base de données et l'authentification.

En cas de doute, privilégier toujours la solution la plus simple possible.
## Sommaire

- [À propos](#à-propos)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Démarrage rapide (dev local)](#démarrage-rapide-dev-local)
- [Base de données](#base-de-données)
- [Authentification](#authentification)
- [Mettre à jour la base d'aides](#mettre-à-jour-la-base-daides)
- [Automatisation](#automatisation)
- [Déploiement](#déploiement)
- [Sécurité](#sécurité)
- [Limites connues](#limites-connues)
- [Feuille de route](#feuille-de-route)

## À propos

Un conseiller saisit le SIRET (ou le nom) d'une entreprise cliente. L'outil récupère ses données publiques (effectif, code NAF, région, convention collective), en déduit automatiquement son OPCO, puis affiche la liste des aides publiques pour lesquelles elle est potentiellement éligible — avec, pour chaque aide, le taux de prise en charge, le plafond, le lien officiel et la date de dernière vérification.

Le conseiller peut ensuite sélectionner les aides pertinentes pour estimer un cumul indicatif et exporter une synthèse en PDF à remettre au client.

Toutes les aides restent **à valider auprès de l'organisme concerné** avant d'être proposées à un client — l'outil sert à débroussailler, pas à se substituer à une vérification finale.

## Fonctionnalités

- **Recherche par SIRET ou par nom d'entreprise** (API publique [recherche-entreprises.api.gouv.fr](https://recherche-entreprises.api.gouv.fr/docs/), gratuite, sans clé). La recherche par nom affiche une liste de résultats cliquables (nom, SIRET, adresse) pour lever l'ambiguïté.
- **Détection automatique de l'OPCO** à partir des codes IDCC (convention collective) de l'entreprise, via la table de correspondance du Ministère du Travail (332 IDCC → 11 OPCO). Sélection manuelle possible en secours si l'auto-détection échoue ou est ambiguë.
- **Moteur de matching** filtrant les aides par : OPCO, branche (IDCC), région, secteur d'activité (NAF), effectif, date de clôture.
- **Regroupement par nature** (Formation, Prêt, Subvention, Accompagnement, Étude & diagnostic, Investissement, Portails régionaux) avec filtres rapides par thématique (Transition écologique, Formation/OPCO, RH, RSE, Développement économique).
- **Badges informatifs** : clôture proche (⏳, sous 60 jours), montant non communiqué ("Sur consultation"), montant individualisé au cas par cas.
- **Calculateur de cumul** : sélection d'aides à la carte, estimation d'une fourchette basse/haute, export PDF de la synthèse.
- **Effectif affinable manuellement** si la tranche INSEE ne suffit pas.

## Architecture

Application statique (HTML/CSS/JS vanilla, aucun framework, aucune étape de build) hébergée sur GitHub Pages, avec un backend léger sur [Supabase](https://supabase.com/) (base de données Postgres + authentification).

```
┌─────────────────────────┐        ┌──────────────────────────────┐
│   index.html (statique)  │        │  recherche-entreprises.api    │
│   GitHub Pages            │──────▶│  .gouv.fr (données entreprise)│
└──────────┬───────────────┘        └──────────────────────────────┘
           │
           │  Supabase JS SDK (clé publique "anon", protégée par RLS)
           ▼
┌─────────────────────────┐
│  Supabase                │
│  - Auth (email/mdp)      │
│  - Table `aides` (RLS)   │
└───────────────────────────┘
```

- **Pas de serveur applicatif** : le navigateur du conseiller communique directement avec Supabase et avec l'API entreprises, via des clés publiques protégées par des règles d'accès (RLS) côté Supabase.
- **Authentification** : Supabase Auth, comptes créés par invitation uniquement (pas d'auto-inscription publique).
- **Automatisation** : une GitHub Action hebdomadaire vérifie que les liens officiels de la base ne sont pas cassés (voir [Automatisation](#automatisation)).

## Démarrage rapide (dev local)

Aucune dépendance à installer, aucun build : c'est un fichier HTML statique.

```bash
git clone https://github.com/ao-alert-rse/outil-aides.git
cd outil-aides
python -m http.server 8080
# puis ouvrir http://localhost:8080/index.html
```

Il faut un compte conseiller valide (créé par invitation, voir [Authentification](#authentification)) pour se connecter et charger la base d'aides.

## Base de données

Une seule table, `aides`, dont la structure est documentée dans [`schema.sql`](./schema.sql) (à exécuter dans l'éditeur SQL Supabase pour initialiser une nouvelle instance).

| Colonne | Type | Description |
|---|---|---|
| `id` | text (PK) | Identifiant unique, slug lisible (ex. `bpi_diag_ecoconception`) |
| `type` | text | Thématique : `TEE`, `OPCO`, `RH`, `RSE`, `DEV` |
| `nom` | text | Nom du dispositif |
| `description` | text | Résumé du dispositif |
| `taux` | text | Taux de prise en charge (texte libre, souvent variable) |
| `plafond` | text | Plafond en euros ou en nature (texte libre) |
| `origine` | text | Organisme(s) financeur(s) |
| `effectif_min` / `effectif_max` | integer | Bornes d'effectif éligibles |
| `region` | text | Code région INSEE si l'aide est régionale |
| `secteur_naf` / `secteur_naf_exclu` | text[] | Sections NAF incluses/exclues |
| `opco` | text[] | Liste des OPCO concernés (aides formation) |
| `idcc` | text[] | Codes IDCC concernés si l'aide cible une branche précise |
| `lien` | text | URL de la fiche officielle |
| `derniere_verif` | date | Date de dernière vérification manuelle |
| `montant_min` / `montant_max` | numeric | Bornes chiffrées pour le calculateur de cumul |
| `duree` | text | Durée du dispositif si pertinente |
| `date_fin` | date | Date de clôture connue (utilisée par le badge "clôture proche" et pour exclure les aides expirées) |
| `plafond_variable` | boolean | `true` si le plafond est calculé au cas par cas (affiche "Montant individualisé" plutôt que "Sur consultation") |
| `nature` | text | Override manuel de la classification automatique par nature (sinon déduite par mots-clés à partir du nom/de la description) |

**Row Level Security (RLS)** : la table n'est lisible que par les utilisateurs authentifiés (policy `aides_select_authenticated`). Un visiteur non connecté obtient une liste vide, pas une erreur — c'est le comportement normal de Postgres RLS.

## Authentification

Comptes créés **exclusivement par invitation**, pas d'auto-inscription publique (le site étant hébergé sur un dépôt public, ouvrir l'inscription exposerait la base d'aides à n'importe quel visiteur).

Pour ajouter un conseiller : dashboard Supabase → **Authentication → Users → Invite user**. Le conseiller reçoit un email pour définir son mot de passe.

## Mettre à jour la base d'aides

Directement dans Supabase, sans toucher au code ni redéployer :

- **Table Editor** → table `aides`, pour éditer/ajouter des lignes à la main.
- **SQL Editor**, pour des mises à jour en masse.

Le fichier [`schema.sql`](./schema.sql) du dépôt documente uniquement la **structure** de la table (pas les données — la base compilée est une donnée propriétaire, volontairement absente de ce dépôt public).

## Automatisation

Une GitHub Action ([`.github/workflows/check-links.yml`](./.github/workflows/check-links.yml)) exécute chaque lundi le script [`scripts/check-links.js`](./scripts/check-links.js) : il interroge Supabase pour lister tous les liens uniques de la base, vérifie leur code HTTP, et **échoue volontairement** si un lien est cassé — ce qui déclenche une notification automatique de GitHub (aucun service d'email tiers à configurer).

Secrets requis (Settings → Secrets and variables → Actions) :
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY` (clé admin, contourne le RLS — à ne jamais utiliser côté client, uniquement dans ce contexte CI)

Déclenchement manuel possible depuis l'onglet **Actions** du dépôt (bouton "Run workflow").

## Déploiement

GitHub Pages, branche `main`, racine du dépôt. Toute modification poussée sur `main` est servie directement (pas de pipeline de build à attendre).

## Sécurité

- La clé Supabase intégrée dans `index.html` est la clé **publique "anon"**, conçue pour être exposée côté client — elle ne donne accès qu'à ce que les policies RLS autorisent explicitement.
- La clé **`service_role`** (admin, contourne tout le RLS) n'existe que comme secret GitHub Action, jamais dans le code du dépôt.
- Le dépôt étant public, aucune donnée métier propriétaire (base d'aides compilée, notes internes) n'y est stockée — uniquement le code de l'application et la structure (vide) de la base.

## Limites connues

- **Effectif** : dérivé de la tranche d'effectif INSEE (borne haute de la fourchette), donc approximatif pour des seuils d'effectif qui ne correspondent pas exactement aux bornes réelles. Un champ de saisie manuelle permet d'affiner si besoin.
- **Code NAF** : celui du siège social de l'entreprise. Pour un grand groupe multi-établissements, ce peut être un code générique ("holding") peu représentatif de l'activité réelle de l'établissement recherché.
- **Pas de suivi du plafond de minimis dans le temps** : une fonctionnalité de calcul de plafond de minimis a été testée puis retirée (voir historique Git) car elle ne portait que sur la sélection en cours, sans connaître l'historique réel du client — jugée plus trompeuse qu'utile en l'état. À refaire proprement une fois un dossier client persistant en place (voir feuille de route).

## Feuille de route

- Dossiers clients persistants, avec historique des aides obtenues dans le temps (pour un vrai suivi du plafond de minimis sur 3 exercices glissants)
- Élargissement de l'automatisation au-delà de la vérification des liens (dispositifs suspendus, dates de clôture dépassées)
- Nom de domaine personnalisé
