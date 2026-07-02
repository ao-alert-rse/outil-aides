#!/usr/bin/env python3
"""
V3 — Nettoyage aides hors scope + injection filtre date_fin
Usage : python scripts/nettoyer_v3.py
"""

import re
import sys
import os

HTML_FILE = os.path.join(os.path.dirname(__file__), "..", "outil-aides-rse.html")

IDS_A_RETIRER = {
    # a) CCI
    "rse_cci_flash_diag",
    "rse_cci_diag_conseil",
    "idf_programme_croissance_cci",
    "idf_cheque_diag_cyber",
    "les_aides_fr_annuaire",
    # b) Trésorerie / capital-risque hors RSE/RH/TEE
    "idf_backup_prevention",
    "idf_backup_reprise",
    "idf_pmup_jeunes_pousses",
    "idf_innovup",
    "opco2i_mobilite_internationale_apprenti",
    # c) Secteur automobile
    "opcomob_auto_pdc_moins11",
    "opcomob_auto_pdc_11_19",
    "opcomob_auto_pdc_20_29",
    "opcomob_auto_pdc_30_39",
    "opcomob_auto_pdc_40_49",
    "opcomob_auto_parcours_multi_modaux",
    "opcomob_auto_poei",
    "opcomob_auto_apprentissage",
    "opcomob_auto_pro_reconversion",
    # d) AAP fermés / ponctuels
    "ademe_aap_bciat",
    "bpi_premiere_usine",
    "bpi_fnvi",
    "idf_btp_circulaire",
    "ue_innovation_fund",
}

DATE_FIN_FILTER = """\
    // filtre date_fin : exclure les aides dont la clôture est passée
    if (aide.date_fin) {
      const today = new Date().toISOString().slice(0, 10);
      if (aide.date_fin < today) return false;
    }
"""


def supprimer_aides(content: str, ids_a_retirer: set) -> tuple[str, list]:
    """
    Supprime les blocs d'aides dont l'id est dans ids_a_retirer.
    Stratégie : découpage de la section AIDES[] en entrées individuelles,
    reconstruction sans les entrées ciblées.
    Retourne (nouveau_contenu, ids_effectivement_retires).
    """

    # Localise le tableau const AIDES = [ ... ];
    debut_pat = re.compile(r"const AIDES\s*=\s*\[")
    m = debut_pat.search(content)
    if not m:
        sys.exit("ERREUR : impossible de localiser 'const AIDES = ['")

    debut_array = m.end()  # position juste après le '['

    # Trouve la fermeture du tableau (']' au niveau 0 par rapport à '[')
    depth = 1
    pos = debut_array
    while pos < len(content) and depth > 0:
        c = content[pos]
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
        pos += 1
    fin_array = pos - 1  # position du ']' fermant

    raw_array = content[debut_array:fin_array]

    # Découpe en blocs d'objets { ... }
    # On parcourt caractère par caractère en tenant compte des strings
    blocs = []
    i = 0
    n = len(raw_array)
    while i < n:
        # Saute espaces/virgules entre blocs
        if raw_array[i] in (' ', '\n', '\r', '\t', ','):
            i += 1
            continue
        if raw_array[i] == '{':
            # Commence un bloc : trouve la fermeture en tenant compte de strings
            start = i
            depth_obj = 0
            in_str = False
            str_char = None
            j = i
            while j < n:
                ch = raw_array[j]
                if in_str:
                    if ch == '\\':
                        j += 2
                        continue
                    if ch == str_char:
                        in_str = False
                elif ch in ('"', "'", '`'):
                    in_str = True
                    str_char = ch
                elif ch == '{':
                    depth_obj += 1
                elif ch == '}':
                    depth_obj -= 1
                    if depth_obj == 0:
                        blocs.append(raw_array[start:j+1])
                        i = j + 1
                        break
                j += 1
            else:
                i = j
        else:
            i += 1

    # Filtre les blocs
    supprimes = []
    gardes = []
    for bloc in blocs:
        m_id = re.search(r'\bid\s*:\s*["\']([^"\']+)["\']', bloc)
        if m_id and m_id.group(1) in ids_a_retirer:
            supprimes.append(m_id.group(1))
        else:
            gardes.append(bloc)

    # Reconstruit la section
    nouveau_array = "\n  " + ",\n  ".join(gardes) + "\n"
    nouveau_content = (
        content[:debut_array]
        + nouveau_array
        + content[fin_array:]
    )
    return nouveau_content, supprimes


def injecter_filtre_date_fin(content: str) -> str:
    """
    Ajoute le filtre date_fin dans matcherAides, juste avant le filtre effectif.
    Ne touche pas au reste de la fonction.
    """
    cible = "    // si effectif inconnu, on affiche toutes les aides sans filtrer"
    if DATE_FIN_FILTER.strip() in content:
        print("  → Filtre date_fin déjà présent, pas de modification.")
        return content
    if cible not in content:
        sys.exit("ERREUR : ancre 'si effectif inconnu' introuvable dans matcherAides")
    return content.replace(cible, DATE_FIN_FILTER + cible)


def main():
    print(f"Lecture : {HTML_FILE}")
    with open(HTML_FILE, encoding="utf-8") as f:
        content = f.read()

    lignes_avant = content.count("\n")

    # 1. Suppression des aides
    print(f"\n[1/2] Suppression de {len(IDS_A_RETIRER)} aides…")
    content, supprimes = supprimer_aides(content, IDS_A_RETIRER)

    non_trouves = IDS_A_RETIRER - set(supprimes)
    print(f"  Supprimés ({len(supprimes)}) : {', '.join(sorted(supprimes))}")
    if non_trouves:
        print(f"  ⚠ Non trouvés ({len(non_trouves)}) : {', '.join(sorted(non_trouves))}")

    # 2. Injection filtre date_fin
    print("\n[2/2] Injection filtre date_fin dans matcherAides…")
    content = injecter_filtre_date_fin(content)

    # 3. Vérification rapide : compter les aides restantes
    ids_restants = re.findall(r'\bid\s*:\s*["\']([^"\']+)["\']', content)
    # On filtre pour ne garder que ceux dans la section AIDES (avant matcherAides)
    debut_m = content.find("function matcherAides")
    debut_aides = content.find("const AIDES")
    aides_section = content[debut_aides:debut_m] if debut_m > debut_aides else content[debut_aides:]
    ids_section = re.findall(r'\bid\s*:\s*["\']([^"\']+)["\']', aides_section)
    print(f"  Aides restantes : {len(ids_section)}")

    # 4. Écriture
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n✓ Fichier écrit ({len(content):,} caractères, {content.count(chr(10))} lignes)")
    print("  Vérifiez la syntaxe JS avec : node --input-type=module < outil-aides-rse.html (ou esprima)")


if __name__ == "__main__":
    main()
