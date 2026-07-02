#!/usr/bin/env python3
"""V3c — Retrait idf_ara_apprenti, idf_prime_apprentissage, rse_label_lucie"""
import re, sys, os

HTML_FILE = os.path.join(os.path.dirname(__file__), "..", "outil-aides-rse.html")
IDS = {"idf_cheque_investiss_cyber"}


def supprimer_aides(content, ids):
    m = re.search(r"const AIDES\s*=\s*\[", content)
    if not m:
        sys.exit("const AIDES introuvable")
    debut = m.end()
    depth, pos = 1, debut
    while pos < len(content) and depth > 0:
        c = content[pos]
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
        pos += 1
    fin = pos - 1
    raw = content[debut:fin]

    blocs, i, n = [], 0, len(raw)
    while i < n:
        if raw[i] in (" ", "\n", "\r", "\t", ","):
            i += 1
            continue
        if raw[i] == "{":
            start, d, ins, sc, j = i, 0, False, None, i
            while j < n:
                ch = raw[j]
                if ins:
                    if ch == "\\":
                        j += 2
                        continue
                    if ch == sc:
                        ins = False
                elif ch in ('"', "'", "`"):
                    ins = True
                    sc = ch
                elif ch == "{":
                    d += 1
                elif ch == "}":
                    d -= 1
                    if d == 0:
                        blocs.append(raw[start : j + 1])
                        i = j + 1
                        break
                j += 1
            else:
                i = j
        else:
            i += 1

    sup, garde = [], []
    for b in blocs:
        mid = re.search(r'\bid\s*:\s*["\']([^"\']+)["\']', b)
        if mid and mid.group(1) in ids:
            sup.append(mid.group(1))
        else:
            garde.append(b)

    nouveau = "\n  " + ",\n  ".join(garde) + "\n"
    return content[:debut] + nouveau + content[fin:], sup


def main():
    with open(HTML_FILE, encoding="utf-8") as f:
        content = f.read()

    content, sup = supprimer_aides(content, IDS)
    print(f"Supprimes ({len(sup)}) : {', '.join(sorted(sup))}")
    non = IDS - set(sup)
    if non:
        print(f"Non trouves : {', '.join(sorted(non))}")

    ids_rest = re.findall(
        r'\bid\s*:\s*["\']([^"\']+)["\']',
        content[content.find("const AIDES") : content.find("function matcherAides")],
    )
    print(f"Aides restantes : {len(ids_rest)}")

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print("Fichier ecrit.")


if __name__ == "__main__":
    main()
