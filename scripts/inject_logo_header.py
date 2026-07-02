"""Injecte le logo Nam & Kouji dans le <header> (réutilise le data URI déjà présent)."""
import re

with open("outil-aides-rse.html", "r", encoding="utf-8") as f:
    h = f.read()

m = re.search(r'src="(data:image/png;base64,[^"]+)"', h)
if not m:
    raise SystemExit("data URI logo introuvable")
data_uri = m.group(1)

ancien = '<div class="header-sigil">RSE<br>TEE<br>RH</div>'
nouveau = f'<img class="header-logo" src="{data_uri}" alt="Nam & Kouji">'

if ancien not in h:
    raise SystemExit("header-sigil introuvable")
h = h.replace(ancien, nouveau)

# CSS : remplace .header-sigil par .header-logo dans le style
if ".header-logo" not in h:
    css_add = """
  .header-logo {
    height: 52px;
    width: auto;
    flex-shrink: 0;
    background: #fff;
    border-radius: 4px;
    padding: 6px 10px;
  }
"""
    # Insertion juste après le bloc .header-sigil
    pat = re.compile(r"(\.header-sigil\s*\{[^}]+\})", re.DOTALL)
    h = pat.sub(r"\1" + css_add, h, count=1)

with open("outil-aides-rse.html", "w", encoding="utf-8") as f:
    f.write(h)

print(f"OK - taille HTML: {len(h):,}")
