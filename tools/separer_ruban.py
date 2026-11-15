#!/usr/bin/env python3
"""Sépare le ruban rouge d'une icône SVG en calque _red (même cadrage), pour qu'il puisse battre.

Le ruban, ce sont les tracés à trait rouge (stroke="#9B1C1C"). Ils sont retirés du dessin de base
et posés seuls dans <nom>_red.svg, masqués par le reste du dessin : là où la cire passe devant
le ruban, le calque rouge est vide. Les aplats rouges (cire réchauffée, gouttes) restent dans la
base : c'est le sceau, pas le ruban.

Usage : python3 tools/separer_ruban.py art/src/ui/ui_sceau-intact.svg [...]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROUGE = "#9B1C1C"
RUBAN_RE = re.compile(rf'<path\b[^>]*\bstroke="{ROUGE}"[^>]*/>')


def separer(chemin: Path) -> None:
    svg = chemin.read_text(encoding="utf-8")
    entete = re.match(r"<svg\b[^>]*>", svg).group(0)
    defs = re.search(r"<defs>.*?</defs>", svg, re.S)
    defs = defs.group(0) if defs else ""
    corps = svg[len(entete):].replace(defs, "", 1).rsplit("</svg>", 1)[0]
    rubans = RUBAN_RE.findall(corps)
    if not rubans:
        print(f"{chemin.name} : aucun ruban, rien à faire")
        return
    base = RUBAN_RE.sub("", corps)
    # Pour le masque : tout le reste du dessin, en noir (fonds de motifs compris).
    reste = re.sub(r'(fill|stroke)="(?!none)[^"]*"', r'\1="#000"', base)
    vb = re.search(r'viewBox="([^"]+)"', entete).group(1).split()
    x, y, w, h = vb
    groupe = re.match(r"<g\b[^>]*>", base.strip())
    ouvre = groupe.group(0) if groupe else "<g>"
    rouge = (f'{entete}<defs><mask id="devant" maskUnits="userSpaceOnUse" x="{x}" y="{y}" width="{w}" height="{h}">'
             f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff"/>{reste}</mask></defs>'
             f'<g mask="url(#devant)">{ouvre}{"".join(rubans)}</g></g></svg>\n')
    chemin.write_text(f"{entete}{defs}{base}</svg>\n", encoding="utf-8")
    chemin.with_name(chemin.stem + "_red.svg").write_text(rouge, encoding="utf-8")
    print(f"{chemin.name} : {len(rubans)} tracé(s) de ruban -> {chemin.stem}_red.svg")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        separer(Path(arg))
