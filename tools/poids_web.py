#!/usr/bin/env python3
"""Répartition du poids téléchargé du build web, par famille d'assets et par cinématique.

Mesure ce que le joueur télécharge : les fichiers importés par Godot (.godot/imported, ceux
que le .pck embarque), compressés en gzip comme GitHub Pages et itch.io les servent. À lancer
après un import (godot --headless --import) ou un export, depuis la racine du projet.

Chaque cinématique (cin_<nom>_NN, calques _red compris) a son propre budget : une planche de
trop se voit dans la CI au lieu de faire sauter le budget global en silence.

Usage : python3 tools/poids_web.py [--budget-cine 1.0] [--budget-total 0] [--resume FICHIER]
  --budget-cine   Mo gzip par cinématique : avertissement CI au-delà (0 = pas de contrôle)
  --budget-total  Mo gzip pour l'ensemble des assets : avertissement CI au-delà (0 = pas de contrôle)
  --resume        ajoute le tableau en Markdown à ce fichier ($GITHUB_STEP_SUMMARY en CI)
Stdlib uniquement.
"""
from __future__ import annotations

import argparse
import gzip
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path.cwd()
CINE = re.compile(r"(cin_[a-z0-9-]+?)(?:_red)?(?:_\d{2})?$")
FAMILLES = [  # (préfixe du nom de la source, famille)
    ("amb_", "sons : ambiances"), ("mus_", "sons : musiques"),
    ("sfx_", "sons : bruitages"), ("vox_", "sons : timbres"),
    ("cin_", "cinématiques"), ("env_", "décors"), ("chr_", "personnages"),
    ("fx_", "effets"), ("ui_", "interface"),
]


def famille(source: Path) -> str:
    for prefixe, nom in FAMILLES:
        if source.name.startswith(prefixe):
            return nom
    if source.suffix.lower() in (".ttf", ".otf", ".woff", ".woff2"):
        return "polices"
    return "autres"


def importes(imp: Path) -> list[Path]:
    """Fichiers produits par un .import et embarqués dans l'export."""
    sortie = []
    for ligne in imp.read_text(encoding="utf-8", errors="replace").splitlines():
        if ligne.startswith(("path=", "path.")) and "=" in ligne:
            chemin = ligne.split("=", 1)[1].strip().strip('"')
            if chemin.startswith("res://"):
                p = ROOT / chemin[len("res://"):]
                if p.is_file():
                    sortie.append(p)
    return sortie


def poids_gzip(p: Path) -> int:
    return len(gzip.compress(p.read_bytes(), 6))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget-cine", type=float, default=1.0)
    ap.add_argument("--budget-total", type=float, default=0.0)
    ap.add_argument("--resume", type=Path)
    a = ap.parse_args()

    if not (ROOT / ".godot" / "imported").is_dir():
        print("::error::.godot/imported absent : lancer d'abord godot --headless --import")
        return 1

    par_famille: Counter[str] = Counter()
    par_cine: Counter[str] = Counter()
    for imp in sorted(ROOT.rglob("*.import")):
        if any(part.startswith(".") or part in ("build", "addons") for part in imp.relative_to(ROOT).parts[:-1]):
            continue
        source = imp.with_suffix("")
        octets = sum(poids_gzip(p) for p in importes(imp))
        if not octets:
            continue
        par_famille[famille(source)] += octets
        m = CINE.fullmatch(source.stem)
        if m:
            par_cine[m[1]] += octets

    mo = lambda o: o / 2**20  # noqa: E731
    total = sum(par_famille.values())
    lignes = ["| Famille | Mo (gzip) |", "| --- | ---: |"]
    lignes += [f"| {f} | {mo(o):.1f} |" for f, o in par_famille.most_common()]
    lignes += [f"| **assets (sans le moteur)** | **{mo(total):.1f}** |", ""]
    lignes += ["| Cinématique | Mo (gzip) |", "| --- | ---: |"]
    lignes += [f"| {c} | {mo(o):.2f} |" for c, o in par_cine.most_common()]
    texte = "\n".join(lignes)
    print(texte)
    if a.resume:
        with a.resume.open("a", encoding="utf-8") as f:
            f.write("\n### Poids des assets\n\n" + texte + "\n")

    if a.budget_cine > 0:
        for c, o in par_cine.most_common():
            if mo(o) > a.budget_cine:
                print(f"::warning::{c} : {mo(o):.2f} Mo, au-delà du budget de {a.budget_cine} Mo par cinématique")
    if a.budget_total > 0 and mo(total) > a.budget_total:
        print(f"::warning::Assets {mo(total):.1f} Mo, au-delà du budget de {a.budget_total} Mo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
