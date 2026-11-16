#!/usr/bin/env python3
"""Génère la cinématique e5_autre_se_retourne : au bout du sentier, entre les croix, l'Autre
s'arrête quand Tobie l'appelle, sa tête tourne à moitié, jamais jusqu'au visage, puis il repart
du même pas boiteux (e5_autre, branche « L'appeler »).

Il est vu de dos, en silhouette à contre-jour dans le brouillard : un coureur comme Tobie, la
capuche, la sacoche à la hanche, la jambe gauche qui traîne. Quand il tourne la tête, seul le bord
de la capuche et un liseré de lumière sur la mâchoire changent : pas de nez, pas d'œil, pas de face.

  Tout est rendu au double (FINESSE) : la caméra pousse lentement vers l'Autre (jusqu'à x2),
  les planches sont posées à l'échelle 1/2 et restent nettes jusqu'au bout de la poussée.

  cin_autre_01  le fond 3840 x 2160 (1920 x 1080 à l'écran) : la forêt de croix dans le
                brouillard, le sentier qui s'enfonce, l'Autre arrêté (image 1) ;
  cin_autre_03  la brume qui dérive devant les croix : une bande transparente de 1920 x 210,
                posée à l'échelle 2 (3840 x 420 à l'écran), qui glisse lentement vers la gauche ;
  cin_autre_02  6 images de 400 x 340 (200 x 170 à l'écran) en (880, 500), grille 3 x 2 :
                0 il marche, 1 il s'arrête, 2 la tête tourne un peu, 3 un quart (le bord de la
                capuche, le liseré de la mâchoire), 4 la tête revient, 5 il repart (pied gauche
                qui traîne). À tenir sur l'image 3 (environ 0,8 s).

Usage : python3 tools/gen_cin_e5.py
"""
from __future__ import annotations

import math

from gen_cin_e1 import DST, H, W, bande, svg
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER, rnd

ZONE = (880, 500, 200, 170)
FINESSE = 2
BRUME_W, BRUME_H = 3840, 420
PIEDS = (960, 652)


def croix(x: float, y: float, h: float, couleur: str, ep: float) -> str:
    """Une croix de bois plantée, vue de loin : un trait vertical, une traverse, un peu penchée."""
    b = h * .34
    return (f'<path d="M{x:.0f} {y:.0f} V{y - h:.0f} M{x - b:.0f} {y - h * .72:.0f} H{x + b:.0f}" '
            f'stroke="{couleur}" stroke-width="{ep:.1f}" stroke-linecap="square"/>')


def foret() -> str:
    """Le brouillard (papier et lavis léger), les rangs de croix de plus en plus pâles vers le fond,
    le sentier qui monte au milieu vers l'horizon."""
    r = rnd(505)
    out = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>',
           '<defs><linearGradient id="brume" x1="0" y1="0" x2="0" y2="1">'
           f'<stop offset="0" stop-color="{PAPIER}"/><stop offset=".55" stop-color="{PAPIER}"/>'
           f'<stop offset="1" stop-color="{MINE}" stop-opacity=".5"/></linearGradient></defs>',
           f'<rect width="{W}" height="{H}" fill="url(#brume)"/>']
    # les rangs, du plus lointain (pâle, petit, près de l'horizon) au plus proche (encre, grand)
    horizon = 560
    for rang in range(9):
        t = rang / 8
        y = horizon + 12 + t * t * 460
        h = 30 + t * t * 330
        couleur = MINE if t < .45 else (LAVIS if t < .8 else ENCRE)
        ep = 1.2 + t * 7
        pas = 70 + t * 260
        x = r.uniform(-pas, 0)
        while x < W + pas:
            # le sentier reste dégagé : il se resserre vers l'horizon
            demi = 60 + t * t * 520
            if abs(x - 960) > demi:
                out.append(croix(x + r.uniform(-8, 8), y + r.uniform(-4, 4), h * r.uniform(.9, 1.1), couleur, ep))
            x += pas * r.uniform(.8, 1.2)
    # le sentier : deux ornières qui montent vers l'horizon
    out.append(f'<path d="M700 {H} Q880 760 952 {horizon + 10} M1220 {H} Q1040 760 968 {horizon + 10}" '
               f'fill="none" stroke="{MINE}" stroke-width="2.4"/>')
    for k in range(10):
        y = H - k * 46
        out.append(f'<path d="M{860 + k * 6} {y} q20 -4 40 0 M{1010 - k * 5} {y - 20} q16 -3 32 0" '
                   f'fill="none" stroke="{MINE}" stroke-width="1.4"/>')
    return "".join(out)


def autre(k: int) -> str:
    """L'Autre de dos, en silhouette, à la moitié de la taille de Tobie : maigre, voûté, la tête
    rentrée, la pointe de la capuche qui tombe dans le dos, la lanterne allumée à la main.
    k : 0 marche, 1 arrêt, 2 et 3 la tête tourne (la pointe de la capuche reste dans le dos et
    pivote vers l'arrière ; la joue et la mâchoire débordent, un liseré de brume les détache), 4 elle revient, 5 il repart. Dessiné à l'échelle 1 autour
    des pieds puis réduit de moitié."""
    x, y = PIEDS
    tour = (0, 0, 26, 55, 20, 0)[k]
    a = math.sin(math.radians(tour))
    out = []
    # le halo de la lanterne, tenue au bout du bras droit (à droite de l'image) : l'écran est
    # inversé, la lumière se dessine donc en sombre (lavis au cœur, mine autour), sans rouge
    lx, ly = x + 50, y - 96
    out.append('<defs><radialGradient id="halo_autre">'
               f'<stop offset="0" stop-color="{LAVIS}" stop-opacity=".95"/><stop offset=".22" stop-color="{LAVIS}" stop-opacity=".75"/>'
               f'<stop offset=".55" stop-color="{MINE}" stop-opacity=".45"/><stop offset=".8" stop-color="{MINE}" stop-opacity=".15"/>'
               f'<stop offset="1" stop-color="{MINE}" stop-opacity="0"/></radialGradient></defs>'
               f'<circle cx="{lx}" cy="{ly + 2}" r="150" fill="url(#halo_autre)"/>')
    # jambes maigres ; la gauche traîne quand il marche
    if k in (0, 5):
        g = (f'M{x - 14} {y - 112} L{x - 22} {y - 6} L{x - 8} {y - 2} L{x - 4} {y - 110} Z' if k == 0 else
             f'M{x - 14} {y - 112} L{x - 18} {y - 14} L{x - 4} {y - 10} L{x - 4} {y - 110} Z')
        d = f'M{x + 3} {y - 112} L{x + 12} {y - 2} H{x + 26} L{x + 15} {y - 112} Z'
    else:
        g = f'M{x - 14} {y - 112} L{x - 16} {y} H{x - 4} L{x - 3} {y - 112} Z'
        d = f'M{x + 3} {y - 112} L{x + 4} {y} H{x + 16} L{x + 15} {y - 112} Z'
    out.append(f'<path d="{g} {d}" fill="{ENCRE}"/>')
    # la capote étroite, les épaules hautes et rondes (voûté), l'ourlet effrangé
    out.append(f'<path d="M{x - 26} {y - 102} L{x - 32} {y - 180} Q{x - 34} {y - 204} {x - 14} {y - 210} H{x + 14} '
               f'Q{x + 34} {y - 204} {x + 32} {y - 180} L{x + 26} {y - 102} L{x + 18} {y - 96} L{x + 8} {y - 102} '
               f'L{x - 2} {y - 95} L{x - 12} {y - 102} L{x - 20} {y - 96} Z" fill="{ENCRE}"/>')
    # la sacoche sur la hanche droite, sa sangle (sans ruban) ; le bras gauche pendant
    out.append(f'<path d="M{x + 22} {y - 136} L{x + 42} {y - 140} L{x + 44} {y - 112} L{x + 24} {y - 108} Z" fill="{ENCRE}"/>'
               f'<path d="M{x - 26} {y - 196} L{x + 32} {y - 136}" stroke="{LAVIS}" stroke-width="2.4"/>'
               f'<path d="M{x - 30} {y - 196} Q{x - 40} {y - 160} {x - 36} {y - 120} L{x - 28} {y - 122} Q{x - 30} {y - 160} {x - 22} {y - 194} Z" fill="{ENCRE}"/>')
    # le bras droit tendu un peu à l'écart, la lanterne au bout
    out.append(f'<path d="M{x + 28} {y - 196} Q{x + 44} {y - 160} {x + 48} {y - 114} L{x + 40} {y - 114} Q{x + 36} {y - 160} {x + 22} {y - 192} Z" fill="{ENCRE}"/>'
               f'<path d="M{lx} {y - 114} V{ly - 10}" stroke="{ENCRE}" stroke-width="2"/>'
               f'<path d="M{lx - 7} {ly - 10} H{lx + 7} L{lx + 6} {ly + 12} H{lx - 6} Z" fill="{MINE}" stroke="{ENCRE}" stroke-width="1.6"/>'
               f'<path d="M{lx - 4} {ly - 6} H{lx + 4} V{ly + 8} H{lx - 4} Z" fill="{ENCRE}"/>')
    # la tête rentrée dans les épaules, sous la capuche ; la pointe tombe dans le dos (un fil de
    # brume la détache), elle pivote de profil quand il tourne la tête
    pointe = 30 * a
    out.append(f'<path d="M{x - 20 - 10 * a:.1f} {y - 214} Q{x - 22 - 10 * a:.1f} {y - 246} {x} {y - 250} Q{x + 22} {y - 246} {x + 20} {y - 214} '
               f'Q{x + 14} {y - 200} {x} {y - 198} Q{x - 14} {y - 200} {x - 20 - 10 * a:.1f} {y - 214} Z" fill="{ENCRE}"/>')
    if tour:
        # la pointe reste derrière la tête et retombe dans le dos, en pivotant vers l'arrière ;
        # pas de nez : seule la joue et la mâchoire débordent du bord de la capuche, à gauche
        out.append(f'<path d="M{x + 4 - 6 * a:.1f} {y - 232} Q{x + 14 - 4 * a:.1f} {y - 222} {x + 10 - 10 * a:.1f} {y - 192} '
                   f'L{x + 2 - 8 * a:.1f} {y - 206} Z" fill="{ENCRE}"/>'
                   f'<path d="M{x + 2 - 6 * a:.1f} {y - 214} Q{x + 6 - 8 * a:.1f} {y - 200} {x + 10 - 10 * a:.1f} {y - 192}" fill="none" stroke="{MINE}" stroke-width="1.6"/>'
                   f'<path d="M{x - 20 - 10 * a:.1f} {y - 222} Q{x - 25 - 12 * a:.1f} {y - 212} {x - 18 - 8 * a:.1f} {y - 203} '
                   f'Q{x - 10 - 4 * a:.1f} {y - 198} {x - 4} {y - 200} L{x - 10} {y - 214} Z" fill="{ENCRE}"/>'
                   f'<path d="M{x - 21 - 11 * a:.1f} {y - 220} Q{x - 25 - 12 * a:.1f} {y - 211} {x - 17 - 8 * a:.1f} {y - 202}" '
                   f'fill="none" stroke="{MINE}" stroke-width="{1.4 + tour / 20:.1f}" stroke-linecap="round"/>')
    else:
        out.append(f'<path d="M{x - 6} {y - 204} Q{x} {y - 170} {x + 2} {y - 158} Q{x + 6} {y - 172} {x + 8} {y - 204}" '
                   f'fill="none" stroke="{MINE}" stroke-width="1.6"/>')
    return f'<g transform="translate({x} {y}) scale(.5) translate({-x} {-y})">' + "".join(out) + '</g>'


def image(k: int) -> str:
    return foret() + autre(k)


def double(contenu_svg: str) -> str:
    """Le même SVG rendu FINESSE fois plus grand (la viewBox ne change pas)."""
    tete, reste = contenu_svg.split(">", 1)
    l, h = (int(v) for v in (tete.split('width="')[1].split('"')[0], tete.split('height="')[1].split('"')[0]))
    tete = tete.replace(f'width="{l}"', f'width="{l * FINESSE}"', 1).replace(f'height="{h}"', f'height="{h * FINESSE}"', 1)
    return tete + ">" + reste


def brume() -> str:
    """La nappe qui dérive : des bancs étirés, flous, en lavis léger (pâles à l'écran inversé),
    sur fond transparent ; les bords gauche et droit s'effacent."""
    r = rnd(506)
    # rendue à demi-résolution (elle est floue) : la planche fait 1920 x 210, posée à l'échelle 2
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{BRUME_W // 2}" height="{BRUME_H // 2}" viewBox="0 0 {BRUME_W} {BRUME_H}">',
           '<defs><filter id="flou" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="34"/></filter>'
           '<linearGradient id="bords" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
           '<stop offset=".08" stop-color="#fff"/><stop offset=".92" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
           f'<mask id="m-bords"><rect width="{BRUME_W}" height="{BRUME_H}" fill="url(#bords)"/></mask></defs>',
           '<g mask="url(#m-bords)"><g filter="url(#flou)">']
    x = -100.0
    while x < BRUME_W + 100:
        l = r.uniform(260, 620)
        out.append(f'<ellipse cx="{x + l / 2:.0f}" cy="{r.uniform(150, 300):.0f}" rx="{l / 2:.0f}" ry="{r.uniform(36, 80):.0f}" '
                   f'fill="{MINE}" opacity="{r.uniform(.25, .5):.2f}"/>')
        x += l * r.uniform(.5, .9)
    out.append('</g></g></svg>\n')
    return "".join(out)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    (DST / "cin_autre_01.svg").write_text(double(svg(image(1))), encoding="utf-8")
    (DST / "cin_autre_02.svg").write_text(double(bande([image(k) for k in range(6)], ZONE, 3)), encoding="utf-8")
    (DST / "cin_autre_03.svg").write_text(brume(), encoding="utf-8")
    print("cin_autre : 1 fond, 1 bande et la brume dans art/src/cin/")


if __name__ == "__main__":
    main()
