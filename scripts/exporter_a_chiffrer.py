"""Exporte un CSV des aides non chiffrees (montant_min=null ET montant_max=null)
pour facilitation collecte manuelle via Perplexity / sites officiels."""
import re, csv

with open("outil-aides-rse.html", encoding="utf-8") as f:
    h = f.read()

# Localise la zone AIDES
m = re.search(r"const AIDES\s*=\s*\[", h)
debut = m.end()
depth, pos = 1, debut
while pos < len(h) and depth > 0:
    c = h[pos]
    if c == "[": depth += 1
    elif c == "]": depth -= 1
    pos += 1
fin = pos - 1
raw = h[debut:fin]

# Decoupe en blocs {}
blocs, i, n = [], 0, len(raw)
while i < n:
    if raw[i] in (" ", "\n", "\r", "\t", ","): i += 1; continue
    if raw[i] == "{":
        start, d, ins, sc, j = i, 0, False, None, i
        while j < n:
            ch = raw[j]
            if ins:
                if ch == "\\": j += 2; continue
                if ch == sc: ins = False
            elif ch in ('"', "'", "`"): ins = True; sc = ch
            elif ch == "{": d += 1
            elif ch == "}":
                d -= 1
                if d == 0: blocs.append(raw[start:j+1]); i = j+1; break
            j += 1
        else: i = j
    else: i += 1

def get(bloc, field):
    m = re.search(rf'\b{field}\s*:\s*"([^"]*)"', bloc)
    return m.group(1) if m else ""

def get_num(bloc, field):
    m = re.search(rf"\b{field}\s*:\s*(\d+|null)", bloc)
    if m:
        v = m.group(1)
        return "" if v == "null" else v
    return ""

rows = []
for b in blocs:
    aid = get(b, "id")
    if aid.startswith("region_portail_"):
        continue  # portails ignores (montants non applicables)
    mn = get_num(b, "montant_min")
    mx = get_num(b, "montant_max")
    if mn == "" and mx == "":
        rows.append({
            "id": aid,
            "nom": get(b, "nom"),
            "origine": get(b, "origine"),
            "lien_officiel": get(b, "lien"),
            "taux_actuel": get(b, "taux"),
            "plafond_actuel": get(b, "plafond"),
            "nouveau_taux": "",
            "nouveau_plafond": "",
            "montant_min": "",
            "montant_max": "",
            "source_url_perplexity": "",
            "notes": "",
        })

with open("aides_a_chiffrer.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter=";")
    w.writeheader()
    w.writerows(rows)

print(f"OK : {len(rows)} aides exportees -> aides_a_chiffrer.csv")
