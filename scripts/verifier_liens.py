"""
Vérifie tous les liens (champ `lien:`) de la BDD AIDES dans outil-aides-rse.html,
la syntaxe JS du script embarqué, et signale les aides dont la vérification date trop.

Usage : python scripts/verifier_liens.py
Pré-requis : pip install esprima (pour le check syntaxe)
"""
import re, ssl, urllib.request, urllib.error
from datetime import date
from pathlib import Path

SEUIL_JOURS_PEREMPTION = 180
try:
    import esprima
except ImportError:
    esprima = None

HTML = Path(__file__).parent.parent / "outil-aides-rse.html"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
TIMEOUT = 15
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def check(url: str) -> tuple[int | str, str]:
    """Tente HEAD puis GET. Renvoie (code|err, methode)."""
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA}, method=method)
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
                return r.status, method
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (400, 403, 405, 501):
                continue  # retry en GET
            return e.code, method
        except Exception as e:
            if method == "HEAD":
                continue
            return f"ERR {type(e).__name__}", method
    return "UNREACHABLE", "—"


def check_js_syntax(html: str) -> None:
    """Vérifie que le <script> du HTML est syntaxiquement valide."""
    if esprima is None:
        print("⚠ esprima non installé — check syntaxe JS sauté (pip install esprima)")
        return
    m = re.search(r"<script>(.*?)</script>", html, re.DOTALL)
    if not m:
        print("⚠ Aucun bloc <script> trouvé")
        return
    try:
        esprima.parseScript(m.group(1))
        print("✓ Syntaxe JS OK\n")
    except esprima.Error as e:
        print(f"✗ ERREUR JS : {e}\n")


def check_peremption(html: str) -> None:
    """Liste les aides dont derniere_verif dépasse SEUIL_JOURS_PEREMPTION, du plus ancien au plus récent."""
    pattern = re.compile(
        r'id:\s*"([^"]+)".*?nom:\s*"([^"]+)".*?derniere_verif:\s*"(\d{4}-\d{2}-\d{2})"',
        re.DOTALL,
    )
    today = date.today()
    perimees = []
    for aide_id, nom, verif_str in pattern.findall(html):
        verif_date = date.fromisoformat(verif_str)
        age = (today - verif_date).days
        if age > SEUIL_JOURS_PEREMPTION:
            perimees.append((age, aide_id, nom, verif_str))

    perimees.sort(reverse=True)
    print(f"=== PÉREMPTION (> {SEUIL_JOURS_PEREMPTION} jours) : {len(perimees)} aide(s) à revérifier ===")
    for age, aide_id, nom, verif_str in perimees:
        print(f"  [{age:>4} j] {verif_str} — {aide_id} — {nom}")
    print()


def main():
    html = HTML.read_text(encoding="utf-8")
    check_js_syntax(html)
    check_peremption(html)
    liens = sorted(set(re.findall(r'lien:\s*"(https?://[^"]+)"', html)))
    print(f"=== {len(liens)} liens uniques à vérifier ===\n")

    ok, ko = [], []
    for url in liens:
        code, methode = check(url)
        ligne = f"  [{code}] ({methode}) {url}"
        print(ligne)
        if isinstance(code, int) and 200 <= code < 400:
            ok.append(url)
        else:
            ko.append((url, code))

    print(f"\n=== RÉSUMÉ : {len(ok)} OK / {len(ko)} KO ===")
    for url, code in ko:
        print(f"  KO [{code}] {url}")


if __name__ == "__main__":
    main()
