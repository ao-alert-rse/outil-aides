# Procédure de mise à jour mensuelle

Outil : `outil-aides-rse.html` — détecteur d'aides RSE/TEE/RH/Formation pour entreprises françaises.

Prévoir **~30 min/mois**, sans compétences techniques avancées. Pré-requis : Python 3 + un éditeur de texte (VS Code, Notepad++).

---

## Tableau récapitulatif des sources

| # | Quoi | Source | Fréquence MAJ source | Effort |
|---|---|---|---|---|
| 1 | Liens des aides | Vérification automatique | À chaque MAJ | 2 min |
| 2 | Table IDCC → OPCO | Ministère du Travail (XLSX) | Rare (arrêté 2019) | 5 min (si MAJ) |
| 3 | Plafonds OPCO Atlas | https://www.opco-atlas.fr/criteres-financement/ | ~annuelle | 5 min |
| 4 | Plafonds OPCO EP | https://www.opcoep.fr/criteres-de-financement | ~annuelle | 5 min |
| 5 | Plafonds OPCO 2i | https://www.opco2i.fr/formation-et-financement/les-regles-de-prise-en-charge/ | ~annuelle | 10 min (JS) |
| 6 | Plafonds 9 autres OPCO | voir liste plus bas | ~annuelle | À enrichir |
| 7 | Aides MTE/ADEME | https://mission-transition-ecologique.beta.gouv.fr | semestrielle | 5 min |
| 8 | Aides Bpifrance | https://www.bpifrance.fr/taxonomy/term/1076 | trimestrielle | 5 min |
| 9 | PCRH | https://travail-emploi.gouv.fr/la-prestation-de-conseil-en-ressources-humaines-pour-les-tpe-pme | annuelle | 2 min |
| 10 | Aides Région IdF | https://www.iledefrance.fr/aides-et-appels-a-projets | semestrielle | 5 min |
| 11 | Fraîcheur des aides | Vérification par portail source — voir section "Vérif fraîcheur" | semestrielle | 30 min |

---

## Routine mensuelle — 4 étapes

### Étape 1 — Vérifier que tous les liens marchent encore

```bash
python scripts/verifier_liens.py
```

Le script affiche pour chaque lien un code HTTP. Tout ce qui n'est pas `200` doit être investigué :
- Si le code est `404` → la page a déménagé. Chercher la nouvelle URL via Google et remplacer dans `outil-aides-rse.html`.
- Si le code est `400`, `403`, `503` → le serveur refuse les requêtes automatiques mais le lien marche probablement dans un navigateur. Ouvrir manuellement pour confirmer (ex. bpifrance.fr, ocapiat.fr bloquent systématiquement les requêtes automatiques — utiliser un navigateur réel, pas un fetch script).

Le script signale aussi automatiquement les aides dont `derniere_verif` dépasse 180 jours (section "PÉREMPTION" en haut de la sortie) — les traiter en priorité à l'étape 3.

### Étape 2 — Mettre à jour la table IDCC → OPCO (si nouvelle version)

Vérifier 1 fois/trimestre si le Ministère du Travail a publié une nouvelle version :
- Source canonique : https://travail-emploi.gouv.fr (chercher "table IDCC OPCO")
- Mirror DREETS Bretagne : https://bretagne.dreets.gouv.fr/sites/bretagne.dreets.gouv.fr/IMG/xlsx/table_idcc-opco-19072019-ministere_du_travail_.xlsx

Si nouveau fichier :
```bash
# 1. Télécharger le XLSX dans data/table_idcc_opco.xlsx
# 2. Lancer :
pip install openpyxl
python scripts/maj_idcc_opco.py
```

Le script régénère automatiquement le bloc `IDCC_OPCO` dans le HTML.

### Étape 3 — Vérifier les plafonds OPCO

Pour chaque OPCO couvert dans la BDD :
1. Ouvrir la page source officielle (cf. tableau ci-dessus)
2. Comparer chaque champ `taux` et `plafond` dans `outil-aides-rse.html` (section AIDES, lignes 464+)
3. Si différent : modifier la valeur directement dans le fichier HTML

**Règle d'or** : si le chiffre n'est pas explicitement publié sur la page officielle, mettre `"N/A — à vérifier sur opcoX.fr"`. **Jamais inventer un chiffre.**

Penser à mettre à jour le champ `derniere_verif: "YYYY-MM-DD"` pour chaque aide modifiée.

### Étape 4 — Ajouter ou retirer des aides

Pour ajouter une aide :
1. Copier-coller un bloc existant comme modèle dans la section `AIDES = [...]`
2. Adapter tous les champs obligatoires : `id`, `type` (OPCO/TEE/RH/RSE), `nom`, `opco` (tableau de slugs), `region` (optionnel — code INSEE région ex. `"11"` pour IdF, omettre si nationale), `description`, `taux`, `plafond`, `origine`, `effectif_min`, `effectif_max`, `lien`, `derniere_verif`
3. Champs optionnels (V4) :
   - `duree: "..."` — pour les aides de type accompagnement/diagnostic (ex. `"12 jours d'intervention sur 10 mois maximum"`), affiché dans la carte
   - `secteur_naf: [...]` / `secteur_naf_exclu: [...]` — restreint l'aide à certaines sections NAF (lettres A-U, cf. constante `SECTIONS_NAF`). N'utiliser que si l'éligibilité sectorielle est explicite et binaire sur la source officielle — ne pas inventer de règle
   - `plafond_variable: true` — si le montant est individualisé par nature (barème par branche/bassin/dossier) et ne sera JAMAIS un chiffre unique, plutôt que juste "N/A". Affiche un badge différent ("Montant individualisé" vs "Sur consultation") pour distinguer "génuinement variable" de "pas encore trouvé"
4. Vérifier avec la console navigateur (F12) qu'il n'y a pas d'erreur JS au chargement

Slugs OPCO valides : `atlas`, `opco2i`, `opcoep`, `afdas`, `akto`, `constructys`, `ocapiat`, `opco-mobilites`, `sante`, `cohesion-sociale`, `commerce`.

Codes région INSEE valides : voir constante `REGIONS_FR` dans le HTML.

## Vérif fraîcheur (semestrielle)

Pour respecter la règle d'or "aucune aide expirée", vérifier **par portail source** (pas aide par aide). Pour chaque portail, lister les aides BDD qui en dépendent puis vérifier sur le site que chaque dispositif est encore actif en 2026 :

| Portail | URL | Aides à recouper |
|---|---|---|
| ADEME Agir | https://agirpourlatransition.ademe.fr/entreprises/aides-financieres | toutes les `ademe_*` |
| Bpifrance | https://www.bpifrance.fr/taxonomy/term/1076 | toutes les `bpi_*` |
| Région IdF | https://www.iledefrance.fr/aides-et-appels-a-projets | toutes les `idf_*` |
| Mission Transition Écologique | https://mission-transition-ecologique.beta.gouv.fr/ | toutes les `mte_*` |
| OPCO Atlas | https://www.opco-atlas.fr/criteres-financement/ | aides `opco: ["atlas"]` |
| OPCO EP | https://www.opcoep.fr/criteres-de-financement | aides `opco: ["opcoep"]` |
| OPCO 2i | https://www.opco2i.fr/ | aides `opco2i_*` |
| AKTO | https://www.akto.fr/financer-une-formation/ | aides `akto_*` |
| AFDAS | https://www.afdas.com/ | aides `afdas_*` |
| Constructys | https://www.constructys.fr/ | aides `constructys_*` |
| OCAPIAT | https://www.ocapiat.fr/ | aides `ocapiat_*` |
| OPCO Commerce | https://www.lopcommerce.com/ | aides `opcommerce_*` |
| Uniformation | https://www.uniformation.fr/ | aides `uniformation_*` |

**Procédure pour chaque aide signalée hors-service :**
- Si dispositif clos définitivement → retirer l'entrée du HTML
- Si clôture connue à date précise → ajouter `date_fin: "YYYY-MM-DD"` (le moteur filtre automatiquement les aides périmées)
- Si statut ambigu → garder + ajouter `"à reconfirmer source officielle"` dans `taux`/`plafond` + mettre à jour `derniere_verif`

---

## Transmission à un successeur
</invoke>

Tous les fichiers nécessaires sont dans ce dossier. Cloner ou copier l'ensemble suffit :
- `outil-aides-rse.html` — l'outil
- `idcc_opco.json` — référence de la table IDCC→OPCO (régénérable)
- `scripts/` — scripts de maintenance
- `MAJ_MENSUELLE.md` — ce document

L'outil est un **fichier HTML unique autonome** : il s'ouvre dans n'importe quel navigateur, sans installation. Les seules dépendances externes sont :
- L'API `recherche-entreprises.api.gouv.fr` (DINUM, gratuit, sans clé)
- Les liens externes vers les sources des aides

Aucun serveur, aucune base de données, aucun compte à maintenir.

---

## Notes V4 (juillet 2026)

- 99 → **113 aides** : nouvelles aides (véhicules, CEC, Pacte Industrie/Entreprises, AAP Première Usine, 4 aides régionales hors IdF) + corrections FSE+/CEE/Tremplin ADEME/Prêt Nouvelle Industrie.
- 9 aides Bpifrance chiffrées par lecture directe en navigateur réel (bpifrance.fr bloque tout fetch automatique en 403 — impossible de les vérifier par script, seulement à la main ou via navigateur type Claude in Chrome).
- `bpi_fonds_spi2` : la fiche catalogue Bpifrance renvoie "offre non disponible" — à reconfirmer avant de la proposer à un client, peut-être à retirer.
- `akto_proprete_bilan_competences` : le taux historique (9,15 €/h) ne correspond à aucune section du PDF AKTO 2026 actuel — repassé en N/A, à reconfirmer auprès d'un conseiller AKTO.
- Nouveaux champs optionnels `duree`, `secteur_naf` / `secteur_naf_exclu`, `plafond_variable`, `nature` (override), `date_fin` (voir Étape 4 ci-dessus).
- `matcherAides` filtre désormais aussi par secteur NAF (`entreprise.naf_section`, déjà récupéré via l'API mais non exploité avant) — n'est posé que sur 3 aides Pacte Industrie/Entreprises pour l'instant, à étendre au cas par cas (attention : Diag PerfImmo notamment a une éligibilité tertiaire/mixte trop floue pour une règle fiable).
- `date_fin` désormais utilisé (`bpi_aap_premiere_usine`, clôture 06/04/2027) — ne l'utiliser que pour une vraie fermeture définitive, jamais une échéance annuelle récurrente (piège rencontré avec OPCO Santé SSSMS).
- `verifier_liens.py` signale automatiquement les aides à revérifier (`derniere_verif` > 180 jours).
- Filtres rapides par type (chips TEE/OPCO/RH/RSE/DEV) ajoutés au-dessus des résultats — 100% client-side.
- **Projet versionné avec git** (`git init` fait en juillet 2026, historique propre par commit thématique). Continuer à committer par petits lots avec des messages clairs.
- Plafond de minimis officiel confirmé (300 000 € d'aides publiques sur 3 exercices fiscaux) — trouvé sur la fiche expertAtlas. Utile si un jour on construit une alerte de dépassement dans le cumul.

### Reste à faire (priorité décroissante, notée pendant la session de juillet 2026)

1. **Régions hors IdF** : seules Auvergne-Rhône-Alpes, Hauts-de-France et Nouvelle-Aquitaine ont une aide spécifique en plus du portail générique. Il reste Bourgogne-Franche-Comté, Bretagne, Centre-Val de Loire, Corse, Grand Est, Normandie, Occitanie, Pays de la Loire, PACA (9 régions) — même méthode que juillet 2026 (1 agent de recherche par région, 1-2 aides phares), coût observé ~45k tokens/région. **Ne pas lancer sans validation explicite au préalable.**
2. ~~N/A restants à vérifier manuellement~~ — **fait le 2026-07-02** via Claude in Chrome : durée Diag Écoconception confirmée "18 jours d'intervention répartis sur 10 mois" (déjà en base) ; page Fonds SPI2 confirmée indisponible ("cette offre n'est plus disponible", warning déjà en base). Diag Impact Env./Adaptation/PerfImmo ont aussi leur durée renseignée en base (à revérifier seulement si un doute apparaît).
3. **Alerte plafond de minimis** dans le calculateur de cumul — le seuil (300 000 €/3 ans) est confirmé, reste à identifier aide par aide lesquelles y sont soumises avant de coder l'alerte.
4. ~~Petites améliorations UI restantes~~ — **fait le 2026-07-02** : badge "clôture proche" (⏳, seuil 60 jours) sur `date_fin`, légende expliquant les badges (⊘, "Sur consultation", "Montant individualisé"), compteur "X chiffrée(s) / Y à consulter" dans la barre de cumul.
5. Si Claude in Chrome est disponible en début de session, il permet de contourner le blocage 403 de bpifrance.fr/ocapiat.fr — vérifier la connexion avant de déclarer une donnée "impossible à vérifier".
- Champ `date_fin` du moteur de matching toujours inexploité (0 aide) — aucune échéance de clôture n'est renseignée à ce jour, alors que plusieurs sont connues (ex. AAP Bpifrance, dépôts OPCO Santé). À prioriser lors d'une prochaine session.
- Clientèle Nam & Kouji confirmée nationale (pas seulement IdF) — les aides régionales hors IdF restent sommaires (un seul lien portail par région) : à approfondir si le volume de dossiers hors IdF le justifie.

## Notes V3 (juin 2026)

- Nettoyage : passage de 131 à **99 aides**. Retraits : aides éditées par CCI (concurrence directe Felps), aides trésorerie/capital-risque hors RSE/RH/TEE, contrats secteur automobile, appels à projets ponctuels.
- Section "Appels à projets" retirée (`NATURES_ORDER`, `SECTION_TITRES`, `inferNature`).
- Nouveau champ optionnel `date_fin: "YYYY-MM-DD"` — le moteur `matcherAides` exclut automatiquement les aides dont la clôture est passée.
