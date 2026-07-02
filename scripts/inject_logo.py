"""Injecte le logo Nam & Kouji en base64 dans le print-header du HTML."""
import base64, re

with open("data/image-1782476121980.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
data_uri = f"data:image/png;base64,{b64}"

with open("outil-aides-rse.html", "r", encoding="utf-8") as f:
    html = f.read()

ancien = '''<div class="print-header">
  <div class="brand">Nam &amp; Kouji</div>
  <div class="subtitle">Détecteur d'aides RSE / TEE / RH / Formation — synthèse personnalisée</div>
</div>'''

nouveau = f'''<div class="print-header">
  <img class="brand-logo" src="{data_uri}" alt="Nam & Kouji — Stratégie RSE">
  <div class="subtitle">Détecteur d'aides RSE / TEE / RH / Formation — synthèse personnalisée</div>
</div>'''

if ancien not in html:
    raise SystemExit("Ancien bloc print-header introuvable")

html = html.replace(ancien, nouveau)

# Ajouter le style .brand-logo dans le CSS @media print si pas déjà present
if ".brand-logo" not in html:
    css_add = """
    .brand-logo {
      max-height: 70px;
      width: auto;
      display: block;
      margin-bottom: 6px;
    }"""
    # Insertion après .print-header .subtitle declaration
    pattern = re.compile(
        r"(\.print-header\s*\.subtitle\s*\{[^}]+\})"
    )
    m = pattern.search(html)
    if m:
        html = html[:m.end()] + css_add + html[m.end():]
    else:
        raise SystemExit("Selector .print-header .subtitle introuvable pour insertion CSS")

with open("outil-aides-rse.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"OK - logo inline ({len(b64):,} chars base64)")
print(f"Taille HTML: {len(html):,} chars")
