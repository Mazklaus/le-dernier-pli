#!/usr/bin/env python3
"""Génère les planches de repos des personnages de l'étape 1 (planche n° 2 de la DA).

Les dessins viennent de tools/donnees/pnj_e1.svgfrag (repère 240 x 420, sol à y 405), à la
même échelle que Tobie (0,845) : images de 200 x 320, sol à y 316, centre à x 100.
Chaque planche a 4 images de respiration à 10 i/s jouées en boucle lente (le code peut tenir
chaque image plus longtemps) : le haut du corps monte de 0 à 3 px, les pieds ne bougent pas.

  art/src/chr/chr_<nom>_repos_01.svg

Usage : python3 tools/gen_chr_pnj_e1.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DST = ROOT / "art" / "src" / "chr"
SOURCE = ROOT / "tools" / "donnees" / "pnj_e1.svgfrag"

ECHELLE = 0.845
CADRE_L, CADRE_H = 200, 320
SOL = 405
CENTRE_X = 120
SOUFFLE = (0.0, 0.004, 0.008, 0.004)     # étirement vertical depuis les pieds (3 px au plus)

PERSOS = {"lamarre": "p-lamarre", "cassien": "p-cassien", "jacquot": "p-jacquot",
          "ravaude": "p-ravaude", "guetteur": "p-guetteur"}


def main() -> None:
    src = SOURCE.read_text(encoding="utf-8")
    defs = re.search(r"<defs>.*?</defs>", src, re.S).group(0)
    DST.mkdir(parents=True, exist_ok=True)
    for nom, gid in PERSOS.items():
        groupe = re.search(rf'<g id="{gid}".*?\n    </g>', src, re.S).group(0)
        groupe = groupe.replace(f'id="{gid}"', f'id="{nom}"', 1)
        images = []
        for i, s in enumerate(SOUFFLE):
            tx = i * CADRE_L + 100 - CENTRE_X * ECHELLE
            ty = 316 - SOL * ECHELLE
            # étirement ancré au sol : translate(0, SOL) scale(1, 1+s) translate(0, -SOL)
            images.append(f'<g transform="translate({tx:.2f} {ty:.2f}) scale({ECHELLE}) '
                          f'translate(0 {SOL}) scale(1 {1 + s:.3f}) translate(0 {-SOL})">'
                          f'<use href="#{nom}"/></g>')
        n = len(SOUFFLE)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
               f'width="{CADRE_L * n}" height="{CADRE_H}" viewBox="0 0 {CADRE_L * n} {CADRE_H}">'
               f'{defs}<defs>{groupe}</defs>{"".join(images)}</svg>\n')
        (DST / f"chr_{nom}_repos_01.svg").write_text(svg, encoding="utf-8")
    print(f"{len(PERSOS)} planches dans {DST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
