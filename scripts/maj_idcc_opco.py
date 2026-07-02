"""
Régénère le bloc IDCC_OPCO + IDCC_LIBELLE dans outil-aides-rse.html
depuis le fichier XLSX officiel du Ministère du Travail.

Pré-requis : pip install openpyxl

Usage :
  1. Télécharger : https://bretagne.dreets.gouv.fr/sites/bretagne.dreets.gouv.fr/IMG/xlsx/table_idcc-opco-19072019-ministere_du_travail_.xlsx
     (ou la version la plus récente publiée par le Ministère)
  2. Placer le fichier dans data/table_idcc_opco.xlsx
  3. Lancer : python scripts/maj_idcc_opco.py
"""
import json, re
from pathlib import Path
import openpyxl

ROOT = Path(__file__).parent.parent
XLSX = ROOT / "data" / "table_idcc_opco.xlsx"
HTML = ROOT / "outil-aides-rse.html"
JSON_OUT = ROOT / "idcc_opco.json"

# Normalise les noms d'OPCO (cellule Excel) vers les slugs utilisés dans le HTML
NORM = {
    "OPCO ATLAS": "atlas",
    "OPCO 2i": "opco2i",
    "OPCO entreprises de proximité": "opcoep",
    "AFDAS": "afdas",
    "OPCO entreprises et salariés des services à forte intensité de main-d'œuvre": "akto",
    "OPCO Construction": "constructys",
    "OCAPIAT": "ocapiat",
    "OPCO Mobilité": "opco-mobilites",
    "OPCO Santé": "sante",
    "OPCO Cohésion sociale": "cohesion-sociale",
    "OPCO Commerce": "commerce",
}


def parse_xlsx(path: Path) -> tuple[dict, dict, set]:
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    mapping, libelles, unknown = {}, {}, set()
    for row in ws.iter_rows(min_row=4, values_only=True):
        idcc, opco, libelle, *_ = row
        if not idcc or not opco:
            continue
        opco = opco.strip()
        if opco not in NORM:
            unknown.add(opco)
            continue
        key = str(idcc)
        mapping[key] = NORM[opco]
        libelles[key] = libelle.strip() if libelle else ""
    return mapping, libelles, unknown


def inject_html(mapping: dict, libelles: dict) -> None:
    html = HTML.read_text(encoding="utf-8")
    map_json = json.dumps(mapping, ensure_ascii=False, separators=(",", ":"))
    lib_json = json.dumps(libelles, ensure_ascii=False, separators=(",", ":"))
    html = re.sub(
        r"const IDCC_OPCO = \{[^\n]+\};",
        f"const IDCC_OPCO = {map_json};",
        html, count=1,
    )
    html = re.sub(
        r"const IDCC_LIBELLE = \{[^\n]+\};",
        f"const IDCC_LIBELLE = {lib_json};",
        html, count=1,
    )
    HTML.write_text(html, encoding="utf-8")


def main():
    if not XLSX.exists():
        print(f"ERREUR : fichier introuvable -> {XLSX}")
        print("Télécharger depuis https://bretagne.dreets.gouv.fr/sites/bretagne.dreets.gouv.fr/IMG/xlsx/table_idcc-opco-19072019-ministere_du_travail_.xlsx")
        return
    mapping, libelles, unknown = parse_xlsx(XLSX)
    print(f"IDCC parsés : {len(mapping)}")
    if unknown:
        print(f"⚠ OPCO inconnus (ajouter au dict NORM) : {unknown}")
    JSON_OUT.write_text(
        json.dumps({"version": XLSX.stem, "mapping": mapping, "libelles": libelles},
                   ensure_ascii=False, indent=0),
        encoding="utf-8",
    )
    inject_html(mapping, libelles)
    print(f"OK. JSON écrit dans {JSON_OUT.name}, HTML mis à jour.")


if __name__ == "__main__":
    main()
