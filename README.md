# Détecteur d'aides RSE / TEE / RH — Nam & Kouji

Outil interne pour détecter les aides de financement RSE, transition écologique et énergétique
(TEE), RH et formation, mobilisables par une entreprise française à partir de son SIRET.

Cabinet : Nam & Kouji, conseil RSE, Île-de-France (clientèle nationale).

---

## Démarrage rapide

Aucune installation, aucun build. Le tout tient dans **un seul fichier HTML autonome**.

- **Usage direct** : double-cliquer sur `outil-aides-rse.html`, il s'ouvre dans le navigateur par défaut.
- **En développement** (recommandé pour l'API SIRET, certains navigateurs bloquent `fetch()` sur `file://`) :
  ```bash
  python -m http.server 8080
  # puis ouvrir http://localhost:8080/outil-aides-rse.html
  ```
- Tester avec le SIRET de Nam & Kouji : `95373180900018` (TPE, 4 salariés, OPCO Atlas, IDCC 1486).

Aucun compte, aucune base de données externe, aucune clé API à gérer.

---

## Comment ça marche

1. L'utilisateur saisit un SIRET.
2. L'app interroge l'API publique `recherche-entreprises.api.gouv.fr` (DINUM, gratuite, sans clé) pour récupérer : nom, effectif, région, code NAF, liste des IDCC (conventions collectives) de l'entreprise.
3. L'OPCO est déduit automatiquement de l'IDCC via la table `IDCC_OPCO` (332 IDCC, arrêté du Ministère du Travail du 19/07/2019).
4. Le moteur `matcherAides()` filtre les 109 aides de la base selon : OPCO, IDCC de branche, région, secteur NAF, date de clôture (`date_fin`), tranche d'effectif.
5. L'utilisateur coche les aides pertinentes ; une barre sticky recalcule le cumul en temps réel (les prêts/investissements remboursables sont marqués `⊘` et exclus du cumul).
6. Export PDF via `window.print()` + CSS `@media print` dédiée (fiche récap avec logo, fiche entreprise, cumul, aides cochées).

---

## Structure du fichier `outil-aides-rse.html`

Fichier unique (~450 Ko), dans l'ordre :

1. `<style>` — CSS (charte graphique : `#085440` vert primaire, `#edaf0e` doré, `#f0e3b1` sable ; logo Nam & Kouji en base64)
2. `<body>` — structure HTML de la page
3. `<script>` — logique JS, dans cet ordre :
   - `const AIDES = [...]` — **la base de données**, 109 objets (voir schéma ci-dessous)
   - `const IDCC_OPCO`, `IDCC_LIBELLE` — table de correspondance IDCC → OPCO
   - `const REGIONS_FR`, `SECTIONS_NAF`, `SECTIONS_INDUSTRIE` — référentiels INSEE
   - `fetchEntreprise()` — appel API SIRET
   - `matcherAides()` — moteur de filtrage (le cœur de l'app)
   - `rendreCarte()`, `afficherChiffre()`, `estimationLabel()`, `inferNature()` — rendu d'une aide
   - `calculerCumul()` — somme des montants sélectionnés
   - `exporterPDF()` — export

### Schéma d'une aide (objet dans `AIDES`)

```js
{
  id: "identifiant_unique",           // requis — slug stable, sert de clé (ne jamais changer)
  type: "TEE",                        // requis — OPCO | TEE | RH | RSE | DEV (catégorie affichée)
  nom: "Nom affiché de l'aide",       // requis
  opco: ["atlas"],                    // requis — [] si aucun filtre OPCO, sinon slugs (voir liste plus bas)
  idcc: ["1486"],                     // optionnel — restreint à des IDCC précis au sein de l'OPCO
  region: "11",                       // optionnel — code région INSEE (ex. "11" = Île-de-France), absent = national
  secteur_naf: ["B","C","D","E"],     // optionnel — liste blanche de sections NAF (lettres A-U)
  secteur_naf_exclu: ["B","C","D","E"], // optionnel — liste noire (mutuellement exclusif avec secteur_naf en pratique)
  date_fin: "2027-04-06",             // optionnel — date de clôture DÉFINITIVE (pas une échéance annuelle récurrente !)
  description: "...",
  taux: "80 % pour les <250 salariés",
  plafond: "5 000 € à 200 000 €",     // ou "N/A — voir [lien]" si non chiffré
  plafond_variable: true,             // optionnel — si le montant est individualisé par nature (jamais un chiffre unique), affiche un badge différent de "N/A"
  origine: "ADEME",
  effectif_min: 1,
  effectif_max: 249,                  // null = pas de plafond
  nature: "Investissement",           // optionnel — force la classification (Prêt/Investissement/Formation/...) si l'inférence automatique se tromperait
  lien: "https://...",                // toujours la fiche produit officielle la plus précise possible, jamais une page d'accueil générique
  derniere_verif: "2026-07-02",       // date de la dernière vérification humaine ou automatisée
  montant_min: null,
  montant_max: null,                  // valeur de l'aide elle-même (subvention), PAS le reste à charge de l'entreprise
  duree: "12 jours sur 10 mois"       // optionnel — pour les aides de type accompagnement/diagnostic
}
```

**Règle d'or, non négociable** : aucun chiffre ne doit être inventé ou approximé. Si un montant/taux/plafond
n'est pas explicitement publié sur une source officielle consultée directement, la valeur est `null` (montants)
ou `"N/A — à vérifier sur [url]"` (texte). Un chiffre trouvé uniquement via un extrait de résultat de recherche
(sans avoir pu lire la page officielle elle-même) n'est **pas** considéré comme confirmé — voir la section
"Difficultés connues" plus bas.

Slugs OPCO valides : `atlas`, `opco2i`, `opcoep`, `afdas`, `akto`, `constructys`, `ocapiat`, `opco-mobilites`,
`sante`, `cohesion-sociale`, `commerce`.

---

## Mise à jour de la base

**Toute la procédure récurrente est documentée dans [`MAJ_MENSUELLE.md`](MAJ_MENSUELLE.md).** Ne pas la dupliquer
ici — s'y référer pour : fréquence de vérification par source, étapes, règles d'ajout d'une aide, notes de version.

En résumé, 3 scripts actifs à connaître :

| Script | Rôle | Fréquence |
|---|---|---|
| `scripts/verifier_liens.py` | Vérifie les ~50 liens (codes HTTP) + syntaxe JS + signale les aides dont `derniere_verif` dépasse 180 jours | À chaque passage |
| `scripts/maj_idcc_opco.py` | Régénère le bloc `IDCC_OPCO` depuis le XLSX officiel du Ministère du Travail | Si nouvel arrêté (rare) |
| `scripts/generer_sources_xlsx.py` | Régénère `SOURCES.xlsx` (tableau consolidé de toutes les sources) depuis le HTML | Après toute modif de la BDD |

Les autres scripts dans `scripts/` (`nettoyer_v3*.py`, `injecter_montants.py`, `inject_logo*.py`,
`exporter_a_chiffrer.py`, `generer_prompt_perplexity.py`) sont des **scripts historiques ponctuels**,
déjà exécutés lors de la migration V3 — conservés pour traçabilité, à ne pas relancer sans comprendre
ce qu'ils font (plusieurs suppriment ou réécrivent des blocs entiers de la BDD).

### Valider une modification

```bash
# Syntaxe JS + liens + péremption
python scripts/verifier_liens.py

# Vérification manuelle rapide de la syntaxe seule (sans requêtes réseau)
python -c "import re, esprima; html=open('outil-aides-rse.html',encoding='utf-8').read(); esprima.parseScript(re.search(r'<script>(.*?)</script>', html, re.DOTALL).group(1)); print('JS OK')"
```

Puis tester dans le navigateur avec le SIRET Nam & Kouji (voir Démarrage rapide) et vérifier la console (F12)
pour l'absence d'erreurs.

---

## Difficultés connues

- **bpifrance.fr et certains PDF ocapiat.fr bloquent tout accès automatisé** (403 systématique en `fetch`/script,
  même avec un User-Agent de navigateur). Ces sources ne peuvent être vérifiées qu'à la main ou via un vrai
  navigateur (ex. extension Claude in Chrome). Ne jamais faire confiance à un chiffre Bpifrance obtenu uniquement
  via un extrait de moteur de recherche — vérifier la page officielle directement avant d'intégrer.
- **Couverture régionale inégale** : l'Île-de-France a des aides détaillées ; les autres régions n'ont pour
  la plupart qu'un lien portail générique. La clientèle de Nam & Kouji étant nationale, c'est un axe
  d'approfondissement identifié mais pas encore traité.
- **Champ `date_fin` très peu utilisé** (1 aide sur 109 actuellement) : la plupart des échéances rencontrées
  dans les sources sont des dates limites *annuelles récurrentes* (ex. dépôt de dossier avant le 31/08 chaque
  année), pas des fermetures définitives de dispositif — ne pas les confondre. `date_fin` ne doit recevoir
  qu'une vraie date de clôture, sinon l'aide disparaîtra à tort de l'outil après cette date.
- **`bpi_fonds_spi2`** : la fiche catalogue Bpifrance renvoie "offre non disponible" (juillet 2026) — à
  reconfirmer avant de la proposer à un client.
- `aides_a_chiffrer.csv` et `prompt_perplexity.txt` (racine) sont des artefacts de travail de la migration V3
  (workflow d'aide au chiffrage via Perplexity) — probablement obsolètes, ne pas les considérer comme source de vérité.
- Le dossier `data/` contient des captures HTML/PDF des pages sources consultées lors de la V3 (archivage,
  pas rechargé automatiquement).

---

## Fichiers du projet

```
outil-aides-rse.html   → l'outil (fichier unique, tout est dedans)
CLAUDE.md               → règles de travail token-strict pour les sessions IA sur ce projet
MAJ_MENSUELLE.md        → procédure de mise à jour récurrente + notes de version
README.md               → ce fichier
SOURCES.xlsx            → export consolidé de toutes les sources (régénéré par script)
idcc_opco.json          → référence de la table IDCC→OPCO (régénérable)
scripts/                → scripts de maintenance (voir tableau ci-dessus)
data/                   → archives des pages sources consultées (HTML/PDF), logo
```

---

## Contexte pour un successeur

Ce projet a été développé et maintenu par itérations successives (V1 à V4, voir notes de version dans
`MAJ_MENSUELLE.md`) avec l'assistance de Claude Code. Aucune connaissance technique avancée n'est requise
pour le maintenir : Python 3 + un éditeur de texte suffisent. La contrainte non négociable est la **règle d'or**
(aucun chiffre inventé) — toute modification de données doit être traçable jusqu'à une source officielle
explicitement consultée.
