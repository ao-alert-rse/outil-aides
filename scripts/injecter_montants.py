#!/usr/bin/env python3
"""
V3d — Injecte montant_min / montant_max dans chaque aide
en parsant taux et plafond. Quand aucun chiffre n'est trouvable -> null.
"""
import re, sys, os

HTML_FILE = os.path.join(os.path.dirname(__file__), "..", "outil-aides-rse.html")

# Nettoie une valeur "5 000 € HT / an" -> 5000
def to_int(s):
    s = s.replace(" ", " ").replace(" ", "").replace(".", "")
    try:
        return int(s)
    except ValueError:
        return None


def extraire_montants(taux: str, plafond: str):
    """Retourne (min, max) ou (None, None) si non parsable."""
    # Cas "Gratuit"
    txt_combine = (taux + " " + plafond).lower()
    if "gratuit" in txt_combine and "n/a" not in txt_combine:
        return 0, 0

    # Cas N/A explicite -> null
    if taux.lower().startswith("n/a") and plafond.lower().startswith("n/a"):
        return None, None

    valeurs = []
    fourchette = None

    # On parse plafond en priorite, puis taux si plafond est vide ou "—"
    for src in (plafond, taux):
        if not src or src in ("—", "-"):
            continue

        # Fourchette explicite : "5 000 € à 200 000 €" ou "250 € ... ou 500 €"
        m_fourchette = re.search(
            r"(\d[\d\s \.]*)\s*€?\s*(?:à|a|-|–|ou)\s*(\d[\d\s \.]*)\s*€",
            src,
        )
        if m_fourchette:
            lo = to_int(m_fourchette.group(1))
            hi = to_int(m_fourchette.group(2))
            if lo is not None and hi is not None and hi > lo:
                fourchette = (lo, hi)
                break

        # "Maximum X €" / "jusqu'a X €" / "plafonne a X €"
        m_max = re.search(
            r"(?:maximum|plafonn[ée]\s*(?:à|a)|jusqu[''](?:à|a))\s*(\d[\d\s \.]*)\s*€",
            src,
            re.IGNORECASE,
        )
        if m_max:
            v = to_int(m_max.group(1))
            if v is not None:
                valeurs.append(v)
                continue

        # Tous les "X €" dans la chaine
        for m in re.finditer(r"(\d[\d\s \.]*)\s*€", src):
            v = to_int(m.group(1))
            if v is not None:
                # On exclut les petits chiffres < 50 € (probablement €/h ou %)
                if v >= 50:
                    valeurs.append(v)

    if fourchette:
        return fourchette

    if valeurs:
        # Si plusieurs valeurs : min/max de l'ensemble
        if len(valeurs) > 1:
            return min(valeurs), max(valeurs)
        # Une seule valeur : c'est un plafond -> montant_max
        return None, valeurs[0]

    return None, None


def extraire_blocs(content):
    m = re.search(r"const AIDES\s*=\s*\[", content)
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
    return content[:debut], blocs, content[fin:]


def injecter_dans_bloc(bloc: str, mn, mx) -> str:
    """Ajoute montant_min / montant_max apres la ligne derniere_verif."""
    # Supprime d'eventuels champs deja presents (idempotence)
    bloc = re.sub(r",?\s*montant_min:\s*(?:null|\d+)", "", bloc)
    bloc = re.sub(r",?\s*montant_max:\s*(?:null|\d+)", "", bloc)

    def fmt(v):
        return "null" if v is None else str(v)

    nouveau = f',\n    montant_min: {fmt(mn)},\n    montant_max: {fmt(mx)}'
    # Insertion juste avant la fermeture du bloc
    return re.sub(r"(\s*)\}$", nouveau + r"\1}", bloc)


def main():
    with open(HTML_FILE, encoding="utf-8") as f:
        content = f.read()

    avant, blocs, apres = extraire_blocs(content)

    stats = {"avec_min_max": 0, "avec_max_seul": 0, "null": 0, "gratuit": 0}
    nouveaux_blocs = []
    parse_log = []

    for bloc in blocs:
        m_id = re.search(r'\bid\s*:\s*["\']([^"\']+)["\']', bloc)
        m_taux = re.search(r'taux\s*:\s*"([^"]*)"', bloc)
        m_plaf = re.search(r'plafond\s*:\s*"([^"]*)"', bloc)
        aide_id = m_id.group(1) if m_id else "?"
        taux = m_taux.group(1) if m_taux else ""
        plafond = m_plaf.group(1) if m_plaf else ""

        # Skip les portails regionaux et annuaires (montants non applicables)
        if aide_id.startswith("region_portail_"):
            mn, mx = None, None
        else:
            mn, mx = extraire_montants(taux, plafond)

        if mn == 0 and mx == 0:
            stats["gratuit"] += 1
        elif mn is not None and mx is not None:
            stats["avec_min_max"] += 1
        elif mx is not None:
            stats["avec_max_seul"] += 1
        else:
            stats["null"] += 1

        parse_log.append((aide_id, mn, mx, taux[:40], plafond[:40]))
        nouveaux_blocs.append(injecter_dans_bloc(bloc, mn, mx))

    nouveau = "\n  " + ",\n  ".join(nouveaux_blocs) + "\n"
    out = avant + nouveau + apres

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(out)

    print(f"Aides traitees : {len(blocs)}")
    print(f"  avec fourchette min-max : {stats['avec_min_max']}")
    print(f"  avec plafond seul (max) : {stats['avec_max_seul']}")
    print(f"  gratuit (0-0)           : {stats['gratuit']}")
    print(f"  non chiffrable (null)   : {stats['null']}")

    # Echantillon de log pour validation
    print("\n--- Echantillon (10 premieres) ---")
    for aid, mn, mx, t, p in parse_log[:10]:
        print(f"{aid:35s}  min={mn}  max={mx}  | t='{t}' p='{p}'")
    print("\n--- 10 non parsees ---")
    nuls = [r for r in parse_log if r[1] is None and r[2] is None]
    for aid, mn, mx, t, p in nuls[:10]:
        print(f"{aid:35s}  | t='{t}' p='{p}'")


if __name__ == "__main__":
    main()
