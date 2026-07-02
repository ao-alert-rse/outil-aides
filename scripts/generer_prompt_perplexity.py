"""Genere un prompt clef en main a coller dans Perplexity, listant les 44 aides
non chiffrees + format de reponse strict pour faciliter le reinjection."""
import csv

with open("aides_a_chiffrer.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f, delimiter=";"))

header = """ACTIVE LE MODE RECHERCHE APPROFONDIE (Deep Research / Pro).

Tu es un expert des aides financieres aux entreprises francaises (RSE, TEE, RH, Formation).

Pour chaque dispositif ci-dessous, tu dois TROUVER les chiffres officiels 2026 en cherchant LARGEMENT :

OU CHERCHER (par ordre de priorite) :
1. Le PDF "Regles de prise en charge 2026" de l'OPCO concerne (ex: "regles prise en charge AKTO 2026 PDF")
2. La fiche detaillee du dispositif sur le site officiel (PAS la page d'accueil)
3. Les brochures, communiques de presse, FAQ officielles
4. Les sites de partenaires officiels (DREETS, Service-Public, Bpifrance)
5. Articles recents (<6 mois) de cabinets specialises citant les chiffres

TU DOIS CHERCHER ACTIVEMENT, pas te contenter de la page fournie. Le lien fourni est un point d'entree, pas la source unique.

CE QUE TU CHERCHES POUR CHAQUE AIDE :
- Taux de prise en charge (ex: "100 % du cout pedagogique", "40 EUR/h", "50 % du cout HT")
- Plafond annuel ou par dossier (ex: "3 000 EUR/an", "200 000 EUR max")
- Eventuelle fourchette (montant minimum si publie)

REGLES :
- N'invente AUCUN chiffre. Mais cherche A FOND avant de dire N/A.
- Si tu trouves un chiffre dans un PDF officiel ou un article fiable, donne-le avec sa source.
- Si vraiment aucune source ne publie le chiffre (ex: reserve aux adherents), reponds "N/A — reserve adherents" ou "N/A — non publie".

FORMAT DE REPONSE OBLIGATOIRE (un bloc par aide, separateur "|") :

id | nouveau_taux | nouveau_plafond | montant_min | montant_max | source_url

- nouveau_taux : texte court (ex: "40 EUR/h" ou "100 % du cout pedagogique")
- nouveau_plafond : texte court (ex: "3 000 EUR/an" ou "200 000 EUR")
- montant_min : nombre seul en EUR (ex: 5000), vide si pas de fourchette
- montant_max : nombre seul en EUR (ex: 200000)
- source_url : URL exacte de la source

---

LISTE DES AIDES A TRAITER :

"""

lignes = []
for i, r in enumerate(rows, 1):
    lignes.append(
        f"{i}. id={r['id']}\n"
        f"   nom: {r['nom']}\n"
        f"   organisme: {r['origine']}\n"
        f"   lien officiel: {r['lien_officiel']}\n"
        f"   taux actuel en BDD: {r['taux_actuel']}\n"
        f"   plafond actuel en BDD: {r['plafond_actuel']}\n"
    )

footer = """
---

RAPPEL FORMAT REPONSE : une ligne par aide, separateur "|" :
id | nouveau_taux | nouveau_plafond | montant_min | montant_max | source_url

Commence directement par la premiere ligne, sans preambule.
"""

with open("prompt_perplexity.txt", "w", encoding="utf-8") as f:
    f.write(header + "\n".join(lignes) + footer)

print(f"OK : prompt_perplexity.txt ({len(rows)} aides)")
