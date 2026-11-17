#!/usr/bin/env python3
"""Génère les petits objets animés du relevé PNJ (playtest du 17/11), pour le nœud ObjetAnime du
Gameplay : une planche fx_<nom>_01 d'images de largeur fixe, en ligne, sur fond transparent.

  fx_buee-crypte_01    E4, la crypte : la buée sur la vitre d'une niche de saint (gen_decors_e4.niche :
                       vitre de 200 x 62 en (x + 10, 738)) ; 4 images de 220 x 80, à poser en
                       (x, 729) ; elle vient et s'en va « comme quelqu'un qui dort » :
                       0 presque rien, 1 elle monte, 2 pleine, 3 elle se retire. Boucle lente.
  fx_fumee-gamelle_01  E5, le campement : un filet de fumée sur la gamelle (gen_decors_e5,
                       gamelle en x 700, bord à SOL - 22) ; 3 images de 80 x 160, le pied du
                       filet en (40, 156) : à poser en (660, SOL - 178). Même trait que la fumée
                       du feu (mine, opacité ,7 : claire une fois l'écran inversé).
  fx_cloche-fremir_01  E7 : une seule cloche, pendue, cirée (gen_cin_e7.cloche), 150 de haut ;
                       2 images de 200 x 260, couronne en (100, 40) : 0 immobile, 1 elle frémit
                       (un demi-degré, la cire qui tremble, de courts traits au bord) ; jamais
                       de balancement, aucune onde : elle ne sonne pas.

Usage : python3 tools/gen_fx_objets_anim.py
"""
from __future__ import annotations

from pathlib import Path

from gen_cin_e7 import cloche
from gen_decors_e1_surface import ENCRE, MINE, PAPIER

DST = Path(__file__).resolve().parent.parent / "art" / "src" / "fx"


def planche(images: list[str], w: int, h: int) -> str:
    corps = "".join(f'<g transform="translate({i * w} 0)">{c}</g>' for i, c in enumerate(images))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w * len(images)}" height="{h}" '
            f'viewBox="0 0 {w * len(images)} {h}">{corps}</svg>\n')


def buee(k: int) -> str:
    """Des nappes de buée, papier pâle, plus ou moins denses ; les mêmes nappes d'une image à
    l'autre (elles grandissent depuis le bas de la vitre). Retour QA du 17/11 : à peine visible
    en 720p ; les nappes sont plus opaques et plus larges, les traits plus épais, et des
    gouttes perlent quand elle est pleine (même case, même ancrage)."""
    force = (.3, .7, .95, .6)[k]
    haut = (.3, .65, 1.0, .75)[k]
    nappes = ((60, 60, 50, 15), (124, 56, 60, 17), (176, 62, 38, 13), (90, 44, 46, 11), (154, 40, 34, 10), (40, 46, 26, 9))
    o = []
    for j, (x, y, rx, ry) in enumerate(nappes):
        if j >= 2 + 4 * haut:
            continue
        yy = 72 - (72 - y) * haut
        o.append(f'<ellipse cx="{x}" cy="{yy:.1f}" rx="{rx * (.7 + .3 * haut):.1f}" ry="{ry:.1f}" fill="{PAPIER}" opacity="{force * (1 - j * .06):.2f}"/>')
    # les traits de buée, comme ceux du décor, plus nombreux quand elle est pleine
    if k in (1, 2, 3):
        o.append(f'<path d="M24 {66 - 30 * haut:.0f} Q70 {62 - 30 * haut:.0f} 110 {68 - 30 * haut:.0f} M118 {64 - 28 * haut:.0f} Q160 {60 - 28 * haut:.0f} 200 {66 - 28 * haut:.0f}" '
                 f'fill="none" stroke="{PAPIER}" stroke-width="2.6" stroke-dasharray="8 5" opacity="{min(1.0, force + .1):.2f}"/>')
    if k == 2:
        for x, y in ((46, 52), (98, 58), (140, 50), (182, 56), (72, 64)):
            o.append(f'<circle cx="{x}" cy="{y}" r="2.6" fill="{PAPIER}"/>')
    return "".join(o)


def fumee(k: int) -> str:
    """Un filet de fumée qui ondule et monte : trois images, la vague décalée d'un tiers."""
    import math
    pts = []
    for j in range(15):
        y = 156 - j * 10
        x = 40 + (6 + j * 1.2) * math.sin(j * .7 - k * 2.1)
        pts.append((x, y))
    d = f"M{pts[0][0]:.1f} {pts[0][1]}" + "".join(f" L{x:.1f} {y}" for x, y in pts[1:])
    return (f'<path d="{d}" fill="none" stroke="{MINE}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" opacity=".7"/>'
            f'<path d="{d}" fill="none" stroke="{MINE}" stroke-width="6" stroke-linecap="round" opacity=".18" transform="translate({3 - k * 2} -4)"/>')


def cloche_fremir(k: int) -> str:
    c = cloche(100, 40, 150, seed=707, trait=2.2)
    if k == 0:
        return c
    traits = (f'<path d="M24 176 l-8 -2 M22 160 l-7 -4 M176 176 l8 -2 M178 160 l7 -4" stroke="{ENCRE}" stroke-width="1.6" stroke-linecap="round"/>')
    return f'<g transform="rotate(.6 100 0) translate(.8 0)">{c}</g>' + traits


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    fichiers = {
        "fx_buee-crypte_01": planche([buee(k) for k in range(4)], 220, 80),
        "fx_fumee-gamelle_01": planche([fumee(k) for k in range(3)], 80, 160),
        "fx_cloche-fremir_01": planche([cloche_fremir(k) for k in range(2)], 200, 260),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"objets animés : {len(fichiers)} planches dans art/src/fx/")


if __name__ == "__main__":
    main()
