#!/usr/bin/env python3
"""Génère l'Autre en jeu, à l'étape 5 : chr_autre_marche_01, 4 images de 200 x 320 (pieds en
(100, 316)), la silhouette de la cinématique e5_autre_se_retourne (tools/gen_cin_e5.autre) à
l'échelle 1, détourée, de dos, la lanterne à la main ; il marche sur place de son pas boiteux
(la jambe gauche traîne). Le jeu l'affiche à 0,6, un peu transparent, au bout du sentier.

Le halo de la lanterne est ramené dans le cadre (rayon 46 au lieu de 150) pour ne pas être
coupé au bord de l'image. Pas de visage, rien de rouge.

Usage : python3 tools/gen_chr_autre.py
"""
from __future__ import annotations

from gen_chr_pnj_e2 import DST
from gen_cin_e5 import PIEDS, autre

CADRE_L, CADRE_H = 200, 320
# pas : 0 et 2 la jambe gauche traîne (en arrière, puis ramenée), 1 et 3 les pieds joints ; le
# corps monte d'un cheveu sur les pieds joints
PAS = ((0, 0), (1, -2), (5, 0), (1, -2))


def image(i: int) -> str:
    k, dy = PAS[i]
    x, y = PIEDS
    dessin = autre(k).replace("scale(.5)", "scale(1)").replace('r="150"', 'r="46"')
    dessin = dessin.replace('id="halo_autre"', f'id="halo_autre_{i}"').replace("url(#halo_autre)", f"url(#halo_autre_{i})")
    return f'<g transform="translate({i * CADRE_L + 100 - x} {316 + dy - y})">{dessin}</g>'


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    n = len(PAS)
    (DST / "chr_autre_marche_01.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CADRE_L * n}" height="{CADRE_H}" viewBox="0 0 {CADRE_L * n} {CADRE_H}">'
        + "".join(image(i) for i in range(n)) + "</svg>\n", encoding="utf-8")
    print("chr_autre_marche_01 : 4 images dans art/src/chr")


if __name__ == "__main__":
    main()
