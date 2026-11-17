#!/usr/bin/env python3
"""Génère les images de l'épilogue animé « Le Quatorzième » (lettre d, ordre), d'après la planche
validée par le GD le 17/11, avec ses corrections (garde-fou « rien ne se compte ») :

  P1  cin_epi-d-rayon (1920 x 800) : un rayon profond qui s'enfonce dans le noir, les plis
      empilés de travers, poussiéreux, en tas qu'on ne peut pas compter ; cin_epi-d-ranger :
      une main pose le pli de Tobie sur le dessus, le seul au ruban rouge net, 3 images
      (ZONE_RANGER) : elle arrive, elle le pose, elle s'en va.
  P2  cin_epi-d-plaque (1920 x 800) : une plaque de bronze, vierge ; seulement l'usure et des
      rayures qu'on ne lit pas (aucun trait régulier). La poussière de cin_epi-c-poussiere.
  P3  cin_epi-d-remise (1920 x 800) : la manche à galons tend une sacoche, une cloche sans battant
      et le pli plié en trois (celui de e7_ouverture_sceau) ; cin_epi-d-mains : les mains d'un
      garçon qui viennent dessous et les prennent, 3 images (ZONE_MAINS).
  P4  réemploi : le décor de la tranchée de l'étape 1 et la marche de Tobie (le même pas).
Le rouge n'est que le ruban du pli. La cire est noire.

Usage : python3 tools/gen_cin_epilogue_quatorzieme.py
"""
from __future__ import annotations

import math
import random

from gen_cin_e1 import DST, W, bande, svg
from gen_cin_e7 import cloche, pli_ferme
from gen_cin_epilogues import main_ouverte
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER, ROUGE

ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
H_PLAN = 800
CLAIR = "#D3CFC2"

# --- P1 : le rayon -----------------------------------------------------------------------------
FUITE = (180, 300)                  # le point de fuite, dans le noir
TAS_TOBIE = (1400, 250)             # le dessus du tas le plus proche, où il pose le pli
ZONE_RANGER = (1180, 0, 740, 530)


def vers_fuite(x: float, y: float, t: float) -> tuple[float, float]:
    """Un point du premier plan ramené vers le point de fuite (t 0 : premier plan, 1 : fuite)."""
    return x + (FUITE[0] - x) * t, y + (FUITE[1] - y) * t


def pli_vieux(x: float, y: float, s: float, a: float, r: random.Random) -> str:
    """Un vieux pli couché, vu de biais : papier jauni (hachure), ruban passé, cachet noir."""
    w, h = 150 * s, 46 * s
    return (f'<g transform="translate({x:.0f} {y:.0f}) rotate({a:.1f})">'
            f'<path d="M{-w / 2:.0f} 0 L{w / 2:.0f} {-2 * s:.0f} L{w / 2 + 6 * s:.0f} {-h:.0f} L{-w / 2 + 4 * s:.0f} {-h + 3 * s:.0f} Z" fill="{CLAIR}" {ST} stroke-width="{max(1.2, 2.6 * s):.1f}"/>'
            f'<path d="M{-w / 2 + 2 * s:.0f} {-h * .45:.0f} L{w / 2 + 3 * s:.0f} {-h * .5:.0f}" stroke="{MINE}" stroke-width="{max(1, 5 * s):.1f}"/>'
            f'<ellipse cx="{r.uniform(-.2, .2) * w:.0f}" cy="{-h * .5:.0f}" rx="{10 * s:.1f}" ry="{6 * s:.1f}" fill="{ENCRE}"/></g>')


def rayon() -> str:
    r = random.Random(1501)
    o = [f'<rect width="{W}" height="{H_PLAN}" fill="{MINE}"/>']
    # trois planches du rayon qui filent vers le point de fuite
    for y0 in (180, 480, 790):
        x1, y1 = vers_fuite(W + 60, y0, 0)
        fx, fy = vers_fuite(W + 60, y0, .97)
        o.append(f'<path d="M{W + 60} {y0} L{fx:.0f} {fy:.0f} L{fx:.0f} {fy + 6:.0f} L{W + 60} {y0 + 34} Z" fill="url(#h2)" {ST} stroke-width="3"/>')
        # sur chaque planche, des tas de plis, du fond vers le premier plan (le fond d'abord)
        for k in range(70, -1, -1):
            t = (k / 70) ** .7 * .95
            s = 1.15 * (1 - t) + .06
            bx, by = vers_fuite(r.uniform(300, W + 40), y0, t)
            hauteur = r.randint(3, 9)
            yy = by
            for j in range(hauteur):
                yy -= 44 * s * r.uniform(.55, .9)
                if yy < by - 240 * s or yy < y0 - 290:
                    break
                o.append(pli_vieux(bx + r.uniform(-14, 14) * s, yy + 40 * s, s, r.uniform(-9, 9), r))
    # le tas le plus proche, sous la main : haut, de travers ; le pli de Tobie ira dessus
    x, y = TAS_TOBIE
    yy = 480
    for j in range(7):
        o.append(pli_vieux(x + r.uniform(-16, 16), yy, 1.1, r.uniform(-7, 7), r))
        yy -= (480 - y) / 7
    # le noir avale le fond, par crans nets (pas de dégradé)
    for x_cran, op in ((1100, .2), (800, .3), (560, .4), (380, .55)):
        o.append(f'<rect width="{x_cran}" height="{H_PLAN}" fill="{ENCRE}" opacity="{op}"/>')
    # la poussière sur le premier plan
    for _ in range(80):
        o.append(f'<circle cx="{r.uniform(900, W):.0f}" cy="{r.uniform(0, H_PLAN):.0f}" r="{r.uniform(1, 2.6):.1f}" fill="{CLAIR}" opacity=".7"/>')
    return "".join(o)


def pli_neuf(x: float, y: float, a: float = -4) -> str:
    """Le pli de Tobie, couché sur le tas : papier net, ruban rouge, cachet noir."""
    w, h = 170, 54
    return (f'<g transform="translate({x} {y}) rotate({a})">'
            f'<path d="M{-w / 2} 0 L{w / 2} -2 L{w / 2 + 6} {-h} L{-w / 2 + 4} {-h + 3} Z" fill="{PAPIER}" {ST} stroke-width="3.4"/>'
            f'<path d="M{-w / 2 + 2} {-h * .46:.0f} L{w / 2 + 3} {-h * .5:.0f}" stroke="{ENCRE}" stroke-width="10"/>'
            f'<path d="M{-w / 2 + 2} {-h * .46:.0f} L{w / 2 + 3} {-h * .5:.0f}" stroke="{ROUGE}" stroke-width="7"/>'
            f'<ellipse cx="0" cy="{-h * .48:.0f}" rx="13" ry="8" fill="{ENCRE}"/></g>')


def main_rangeuse(x: float, y: float, prise: bool) -> str:
    """Une main d'archiviste, dos vers nous, qui tient le pli par le bord (ou s'en va, ouverte) ;
    la manche sort du cadre en haut à droite."""
    o = [f'<path d="M{x + 40} {y - 40} L{x + 420} {y - 420} L{x + 560} {y - 330} L{x + 120} {y + 30} Z" fill="{LAVIS}" {ST} stroke-width="4"/>',
         f'<path d="M{x + 60} {y - 30} L{x + 120} {y + 30}" {ST} stroke-width="3"/>',
         f'<path d="M{x - 30} {y - 4} Q{x - 10} {y - 50} {x + 50} {y - 46} Q{x + 110} {y - 30} {x + 104} {y + 20} Q{x + 80} {y + 56} {x + 20} {y + 50} Z" fill="{PAPIER}" {ST} stroke-width="4"/>']
    if prise:
        o.append(f'<path d="M{x - 28} {y} Q{x - 60} {y + 10} {x - 66} {y + 34} Q{x - 56} {y + 44} {x - 34} {y + 30}" fill="{PAPIER}" {ST} stroke-width="3.4"/>')
    else:
        for dx in (-50, -30, -8):
            o.append(f'<path d="M{x + dx + 20} {y + 20} q-30 18 -40 46" fill="none" {ST} stroke-width="14"/>'
                     f'<path d="M{x + dx + 20} {y + 20} q-30 18 -40 46" fill="none" stroke="{PAPIER}" stroke-width="8"/>')
    return "".join(o)


def ranger(k: int) -> str:
    """0 la main arrive, le pli en l'air ; 1 elle le pose sur le dessus du tas ; 2 elle s'en va,
    le pli reste."""
    x, y = TAS_TOBIE
    o = [rayon()]
    if k == 0:
        o.append(pli_neuf(x + 40, y - 120, -12) + main_rangeuse(x + 120, y - 150, True))
    elif k == 1:
        o.append(pli_neuf(x, y, -4) + main_rangeuse(x + 80, y - 30, True))
    else:
        o.append(pli_neuf(x, y, -4) + main_rangeuse(x + 260, y - 240, False))
    return "".join(o)


def fond_rayon() -> str:
    return rayon()


# --- P2 : la plaque vierge -------------------------------------------------------------------------
def plaque() -> str:
    r = random.Random(1601)
    o = [f'<rect width="{W}" height="{H_PLAN}" fill="{CLAIR}"/>']
    # la pierre du mur, de grands blocs
    for y in (0, 260, 520):
        o.append(f'<path d="M0 {y} H{W}" {ST} stroke-width="3"/>')
        for x in range(r.randint(-200, 0), W, 520):
            o.append(f'<path d="M{x} {y} V{y + 260}" {ST} stroke-width="3"/>')
    # la plaque : bronze patiné, un double filet, vierge ; l'usure, des rayures sans ordre
    px, py, pw, ph = 560, 150, 800, 520
    o.append(f'<rect x="{px + 16}" y="{py + 16}" width="{pw}" height="{ph}" fill="{ENCRE}" opacity=".35"/>')
    o.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="{MINE}" {ST} stroke-width="6"/>')
    o.append(f'<rect x="{px + 26}" y="{py + 26}" width="{pw - 52}" height="{ph - 52}" fill="none" {ST} stroke-width="2.4"/>')
    for _ in range(14):
        cx, cy = r.uniform(px + 60, px + pw - 60), r.uniform(py + 60, py + ph - 60)
        o.append(f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{r.uniform(20, 70):.0f}" ry="{r.uniform(8, 26):.0f}" fill="{CLAIR}" opacity=".35"/>')
    for _ in range(9):
        cx, cy = r.uniform(px + 50, px + pw - 120), r.uniform(py + 50, py + ph - 50)
        a = r.uniform(0, math.pi)
        lg = r.uniform(30, 120)
        o.append(f'<path d="M{cx:.0f} {cy:.0f} q{lg * .4 * math.cos(a):.0f} {r.uniform(-12, 12):.0f} {lg * math.cos(a):.0f} {lg * math.sin(a) * .3:.0f}" fill="none" stroke="{PAPIER}" stroke-width="1.4" opacity=".7"/>')
    for x, y in ((px + 20, py + 20), (px + pw - 20, py + 20), (px + 20, py + ph - 20), (px + pw - 20, py + ph - 20)):
        o.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{LAVIS}" {ST} stroke-width="2"/>')
    return "".join(o)


# --- P3 : la remise ------------------------------------------------------------------------------
ZONE_MAINS = (0, 380, 1160, 420)


def remise(k: int = -1) -> str:
    """Sur la table de l'abri : la manche du sergent (galons) à droite tient la sacoche pliée ; dessus,
    la petite cloche sans battant et le pli en trois. k : les mains du garçon, 0 elles arrivent,
    1 elles sont dessous, 2 elles prennent (les pouces par-dessus) ; -1 : pas encore là."""
    o = [f'<rect width="{W}" height="{H_PLAN}" fill="{CLAIR}"/>']
    for y in range(40, H_PLAN, 90):
        o.append(f'<path d="M0 {y} H{W}" stroke="{MINE}" stroke-width="2"/>')
    # la manche et la main du sergent, à droite, galons sur l'avant-bras
    o.append(f'<path d="M{W + 40} 260 L1300 380 Q1280 470 1300 560 L{W + 40} 620 Z" fill="{MINE}" {ST} stroke-width="5"/>')
    o.append(f'<path d="M1540 330 L1580 400 L1620 318 M1560 352 L1600 422 L1640 340" fill="none" stroke="{PAPIER}" stroke-width="8"/>'
             f'<path d="M1540 330 L1580 400 L1620 318 M1560 352 L1600 422 L1640 340" fill="none" {ST} stroke-width="2.4"/>')
    # la sacoche pliée (cuir), sa sangle qui pend
    o.append(f'<path d="M640 470 L1300 450 L1310 620 L650 640 Z" fill="{LAVIS}" {ST} stroke-width="5"/>'
             f'<path d="M650 520 L1302 500" fill="none" stroke="{MINE}" stroke-width="3"/>'
             f'<path d="M940 520 V570 H1000 V518" fill="none" stroke="{MINE}" stroke-width="4"/>'
             f'<path d="M660 600 Q560 680 600 780" fill="none" {ST} stroke-width="14"/><path d="M660 600 Q560 680 600 780" fill="none" stroke="{LAVIS}" stroke-width="8"/>')
    # la main du sergent sous la sacoche
    o.append(f'<path d="M1300 560 Q1240 600 1180 600 Q1150 590 1170 570 Q1220 560 1300 520 Z" fill="{PAPIER}" {ST} stroke-width="4"/>')
    # la petite cloche sans battant, couchée ; le pli en trois, son ruban rouge, sa cire noire
    o.append(f'<g transform="translate(760 330) rotate(-78 60 70)">{cloche(60, 0, 140, cire=False, seed=1602, trait=3.4, corde=False, larmes=0)}</g>')
    o.append(f'<g transform="translate(920 222) scale(.42)">{pli_ferme(0, 0)}</g>')
    if k >= 0:
        dy = (90, 0, -6)[k]
        o.append(f'<g transform="translate(560 {610 + dy}) scale(1.1) rotate(-8)">{main_ouverte(0, 0).replace("url(#h2)", CLAIR).replace('fill="url(#v2)"', f'fill="{MINE}" opacity=".5"').replace('fill="url(#v1)"', f'fill="{MINE}" opacity=".3"')}</g>')
        if k == 2:
            o.append(f'<path d="M{690} {560 + dy} Q{720} {520 + dy} {770} {520 + dy} Q{790} {540 + dy} {760} {560 + dy}" fill="{PAPIER}" {ST} stroke-width="4"/>')
    return "".join(o)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    fichiers = {
        "cin_epi-d-rayon": svg(fond_rayon(), (0, 0, W, H_PLAN)),
        "cin_epi-d-ranger": bande([ranger(k) for k in range(3)], ZONE_RANGER, 3),
        "cin_epi-d-plaque": svg(plaque(), (0, 0, W, H_PLAN)),
        "cin_epi-d-remise": svg(remise(-1), (0, 0, W, H_PLAN)),
        "cin_epi-d-mains": bande([remise(k) for k in range(3)], ZONE_MAINS, 3),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"épilogue d : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
