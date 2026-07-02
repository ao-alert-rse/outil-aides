#!/usr/bin/env python3
"""V3b — Retrait aides CCI/CMA + suppression section Appel a projets"""

import re, sys, os

HTML_FILE = os.path.join(os.path.dirname(__file__), "..", "outil-aides-rse.html")

IDS_A_RETIRER = {
    "mte_cedre_premier_pas",
    "mte_visite_energie_cci",
    "ademe_decarb_ind",
    "ademe_aap_ecei",
}


def supprimer_aides(content, ids):
    debut_pat = re.compile(r"const AIDES\s*=\s*\[")
    m = debut_pat.search(content)
    if not m:
        sys.exit("ERREUR : const AIDES introuvable")
    debut_array = m.end()
    depth = 1
    pos = debut_array
    while pos < len(content) and depth > 0:
        c = content[pos]
        if c == '[': depth += 1
        elif c == ']': depth -= 1
        pos += 1
    fin_array = pos - 1
    raw = content[debut_array:fin_array]

    blocs, i, n = [], 0, len(raw)
    while i < n:
        if raw[i] in (' ', '\n', '\r', '\t', ','):
            i += 1; continue
        if raw[i] == '{':
            start, depth_obj, in_str, str_char, j = i, 0, False, None, i
            while j < n:
                ch = raw[j]
                if in_str:
                    if ch == '\\': j += 2; continue
                    if ch == str_char: in_str = False
                elif ch in ('"', "'", '`'):
                    in_str = True; str_char = ch
                elif ch == '{': depth_obj += 1
                elif ch == '}':
                    depth_obj -= 1
                    if depth_obj == 0:
                        blocs.append(raw[start:j+1]); i = j+1; break
                j += 1
            else: i = j
        else: i += 1

    supprimes, gardes = [], []
    for bloc in blocs:
        mid = re.search(r'\bid\s*:\s*["\']([^"\']+)["\']', bloc)
        if mid and mid.group(1) in ids:
            supprimes.append(mid.group(1))
        else:
            gardes.append(bloc)

    nouveau = "\n  " + ",\n  ".join(gardes) + "\n"
    return content[:debut_array] + nouveau + content[fin_array:], supprimes


def supprimer_section_aap(content):
    # 1. NATURES_ORDER : retirer "Appel à projets"
    content = re.sub(
        r',\s*"Appel à projets"',
        '',
        content
    )
    # 2. SECTION_TITRES : retirer la ligne "Appel à projets": ...
    content = re.sub(
        r'\s*"Appel à projets"\s*:\s*"[^"]*",?\n?',
        '\n',
        content
    )
    # 3. inferNature : retirer la règle AAP
    content = re.sub(
        r'\s*// 6\. Appel à projets / AAP\n\s*if \(/appel à projets[^)]+\)[^;]+;\n',
        '\n',
        content
    )
    # 4. Badge CSS : retirer .badge-appel-a-projets
    content = re.sub(
        r'\s*\.badge-appel-a-projets[^}]+\}\n?',
        '\n',
        content
    )
    return content


def main():
    print(f"Lecture : {HTML_FILE}")
    with open(HTML_FILE, encoding="utf-8") as f:
        content = f.read()

    print(f"\n[1/2] Suppression de {len(IDS_A_RETIRER)} aides...")
    content, supprimes = supprimer_aides(content, IDS_A_RETIRER)
    non_trouves = IDS_A_RETIRER - set(supprimes)
    print(f"  Supprimes ({len(supprimes)}) : {', '.join(sorted(supprimes))}")
    if non_trouves:
        print(f"  Non trouves : {', '.join(sorted(non_trouves))}")

    print("\n[2/2] Suppression section Appel a projets...")
    content = supprimer_section_aap(content)

    ids_section = re.findall(r'\bid\s*:\s*["\']([^"\']+)["\']',
                             content[content.find("const AIDES"):content.find("function matcherAides")])
    print(f"  Aides restantes : {len(ids_section)}")

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\nFichier ecrit ({len(content):,} car.)")


if __name__ == "__main__":
    main()
