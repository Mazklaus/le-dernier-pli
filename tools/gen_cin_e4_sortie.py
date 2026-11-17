#!/usr/bin/env python3
"""Génère les planches de la cinématique e4_sortie_hopital (lot 2, planche validée par le GD le
17/11, retouche comprise) : à la fin de e4_benediction, la porte de l'hôpital se referme
derrière Tobie ; dehors, la lumière est blanche ; au loin, la forêt de croix.

  P1 et P2, la porte de la rue latérale, de près :
  cin_e4-sortie-porte    le fond 1920 x 1080 : le mur de briques, l'encadrement de pierre, la
                         lucarne noire, la marche ;
  cin_e4-sortie-battant  3 images de ZONE_BATTANT, en ligne : le battant ouvert vers
                         l'intérieur, le noir de l'hôpital (0), à demi (1), clos (2).
  P3, plan large :
  cin_e4-sortie-foret    la route qui monte, et au loin la forêt de croix, en plusieurs plans
                         de profondeur : croix de travers, tailles inégales, la brume qui mange
                         le fond (comme la Forêt de Croix validée, mais à l'endroit : l'étape 4
                         n'est pas inversée).

Tobie (chr_tobie_repos_01 et son ruban) est posé par la ciné. Aucun rouge.

Usage : python3 tools/gen_cin_e4_sortie.py
"""
from __future__ import annotations

import random
from pathlib import Path

from gen_cin_epilogues import DEFS_CIN
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER

DST = Path(__file__).resolve().parent.parent / "art" / "src" / "cin"
W, H = 1920, 1080
ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
CLAIR = "#D3CFC2"
PORTE = (520, 860, 300, 900)         # gauche, droite, haut, bas de la baie
SEUIL = 960                          # le dessus de la marche
ZONE_BATTANT = (480, 260, 420, 680)
HORIZON = 560


def svg(contenu: str, w: int = W, h: int = H) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{DEFS_CIN}{contenu}</svg>\n')


def bande(images: list[str], zone: tuple[int, int, int, int]) -> str:
    x, y, w, h = zone
    corps = "".join(f'<svg x="{i * w}" y="0" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}">{c}</svg>'
                    for i, c in enumerate(images))
    return svg(corps, w * len(images), h)


# --- P1 et P2 : la porte ------------------------------------------------------------------------
def porte_fond() -> str:
    g, d, h, b = PORTE
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>']
    # le mur de briques, en aplat, joints tracés
    mur_d = 1500
    o.append(f'<rect x="-10" y="-10" width="{mur_d + 10}" height="{SEUIL + 10}" fill="{CLAIR}"/>')
    for i, y in enumerate(range(0, SEUIL, 44)):
        o.append(f'<path d="M0 {y} H{mur_d}" stroke="{MINE}" stroke-width="2"/>')
        dx = 0 if i % 2 == 0 else 60
        for x in range(dx, mur_d, 120):
            o.append(f'<path d="M{x} {y} v44" stroke="{MINE}" stroke-width="2"/>')
    o.append(f'<path d="M{mur_d} -10 V{SEUIL}" {ST} stroke-width="6"/>')
    # la ruelle qui file à droite, le ciel blanc
    o.append(f'<path d="M{mur_d} {SEUIL - 300} Q1700 {SEUIL - 320} {W} {SEUIL - 310}" fill="none" stroke="{MINE}" stroke-width="3"/>')
    o.append(f'<path d="M1760 {SEUIL} V{SEUIL - 380} M1730 {SEUIL - 340} h60" stroke="{ENCRE}" stroke-width="7" stroke-linecap="square"/>')
    # la baie : le noir de l'hôpital
    o.append(f'<rect x="{g}" y="{h}" width="{d - g}" height="{b - h}" fill="{ENCRE}"/>')
    # l'encadrement de pierre, le linteau, la lucarne au-dessus
    o.append(f'<path d="M{g - 50} {b} V{h - 50} H{d + 50} V{b} H{d} V{h} H{g} V{b} Z" fill="{PAPIER}" {ST} stroke-width="6"/>')
    o.append(f'<rect x="{g - 70}" y="{h - 90}" width="{d - g + 140}" height="44" fill="{PAPIER}" {ST} stroke-width="6"/>')
    lx = (g + d) / 2
    o.append(f'<path d="M{lx - 36} {h - 140} V{h - 220} Q{lx} {h - 270} {lx + 36} {h - 220} V{h - 140} Z" fill="{ENCRE}"/>')
    o.append(f'<path d="M{lx - 60} {h - 110} Q{lx} {h - 140} {lx + 60} {h - 110}" fill="none" {ST} stroke-width="5"/>')
    # la marche, le pavé
    o.append(f'<rect x="{g - 90}" y="{b}" width="{d - g + 180}" height="{SEUIL - b}" fill="{PAPIER}" {ST} stroke-width="6"/>')
    o.append(f'<rect x="-10" y="{SEUIL}" width="{W + 20}" height="{H - SEUIL + 10}" fill="{CLAIR}" {ST} stroke-width="6"/>')
    r = random.Random(4101)
    for y in range(SEUIL + 24, H, 40):
        x = r.uniform(-40, 0)
        while x < W:
            lg = r.uniform(60, 90)
            o.append(f'<path d="M{x:.0f} {y} q{lg / 2:.0f} -12 {lg:.0f} 0" fill="none" stroke="{MINE}" stroke-width="2.5"/>')
            x += lg + 10
    return "".join(o)


def battant(k: int) -> str:
    """Le battant, gond à gauche, s'ouvre vers l'intérieur : ouvert (0), à demi (1), clos (2)."""
    g, d, h, b = PORTE
    if k == 2:
        bx, haut, bas = d, h, b
    else:
        # vu par la baie, il fuit vers le fond : plus court, plus étroit
        bx = g + (110, 230)[k]
        rentre = (40, 18)[k]
        haut, bas = h + rentre, b - rentre
    dd = f"M{g} {h} L{bx} {haut} L{bx} {bas} L{g} {b} Z"
    o = [f'<path d="{dd}" fill="{MINE}" {ST} stroke-width="6"/>']
    for i in range(1, 4):
        u = i / 4
        x = g + (bx - g) * u
        o.append(f'<path d="M{x:.0f} {h + (haut - h) * u:.0f} L{x:.0f} {b + (bas - b) * u:.0f}" stroke="{ENCRE}" stroke-width="3"/>')
    if k == 2:
        o.append(f'<path d="M{g + 20} {h + 120} H{d - 20} M{g + 20} {b - 120} H{d - 20}" stroke="{ENCRE}" stroke-width="10"/>')
        o.append(f'<circle cx="{d - 50}" cy="{(h + b) / 2 + 20}" r="12" fill="{ENCRE}"/>')
    return "".join(o)


def plan_battant(k: int) -> str:
    return porte_fond() + battant(k)


# --- P3 : la forêt de croix -----------------------------------------------------------------------
def croix(x: float, pied: float, h: float, ep: float, couleur: str, penche: float) -> str:
    b = h * .26
    return (f'<g transform="rotate({penche:.1f} {x:.0f} {pied:.0f})"><path d="M{x:.0f} {pied:.0f} V{pied - h:.0f} '
            f'M{x - b:.0f} {pied - h * .74:.0f} H{x + b:.0f}" stroke="{couleur}" stroke-width="{ep:.1f}" stroke-linecap="square"/></g>')


def croix_bois(x: float, pied: float, h: float, larg: float, penche: float) -> str:
    """Une croix proche, en planches : aplats cernés, une veine, de travers."""
    b = h * .28
    ty = pied - h * .74
    return (f'<g transform="rotate({penche:.1f} {x:.0f} {pied:.0f})">'
            f'<rect x="{x - larg / 2:.0f}" y="{pied - h:.0f}" width="{larg:.0f}" height="{h:.0f}" fill="{MINE}" {ST} stroke-width="3"/>'
            f'<rect x="{x - b:.0f}" y="{ty - larg / 2:.0f}" width="{2 * b:.0f}" height="{larg:.0f}" fill="{MINE}" {ST} stroke-width="3"/>'
            f'<path d="M{x - 2:.0f} {pied - h + 16:.0f} V{pied - 20:.0f}" stroke="{LAVIS}" stroke-width="1.5"/></g>')


def foret() -> str:
    r = random.Random(4102)
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>',
         f'<path d="M0 {HORIZON} Q600 {HORIZON - 8} 1200 {HORIZON + 4} T{W} {HORIZON} V{H} H0 Z" fill="{CLAIR}"/>']
    # les rangs, du plus lointain (pâle, petit, serré) au plus proche ; la brume entre chaque
    # plan mange le fond (aplats de papier translucides, sans dégradé)
    rangs = 8
    for rang in range(rangs):
        t = rang / (rangs - 1)
        pied = HORIZON + 10 + t * 150
        h = 26 + t * 150
        ep = 1.2 + t * 4
        couleur = MINE if t < .6 else LAVIS
        pas = 34 + t * 120
        x = r.uniform(-pas, 0) + 700 * (1 - t) * .2
        while x < W + pas:
            if t < .5 or x > 700:
                o.append(croix(x, pied + r.uniform(-5, 5), h * r.uniform(.7, 1.3), ep, couleur, r.uniform(-7, 7)))
            x += pas * r.uniform(.6, 1.4)
        if rang < rangs - 1:
            o.append(f'<rect x="0" y="{HORIZON - 200}" width="{W}" height="{pied - HORIZON + 214:.0f}" fill="{PAPIER}" opacity=".32"/>')
    # la lisière proche, à droite : quelques grandes croix de bois, de travers
    for x, h, a in ((1380, 330, -4), (1530, 260, 6), (1660, 400, -2), (1800, 300, 8), (1900, 360, -6)):
        o.append(croix_bois(x, HORIZON + 230 + (x - 1380) * .1, h, 18, a))
    # la route qui monte de la gauche vers la forêt, ses ornières
    o.append(f'<path d="M-20 {H + 10} Q500 860 980 {HORIZON + 160} L1080 {HORIZON + 156} Q760 900 520 {H + 10} Z" fill="{PAPIER}" {ST} stroke-width="4"/>')
    o.append(f'<path d="M150 {H} Q560 870 1010 {HORIZON + 162} M360 {H} Q700 890 1050 {HORIZON + 160}" fill="none" stroke="{MINE}" stroke-width="3"/>')
    # la terre labourée du premier plan
    for _ in range(40):
        x, y = r.uniform(0, W), r.uniform(HORIZON + 240, H)
        o.append(f'<path d="M{x:.0f} {y:.0f} q{r.uniform(20, 50):.0f} -8 {r.uniform(60, 140):.0f} 0" fill="none" stroke="{MINE}" stroke-width="3"/>')
    return "".join(o)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    fichiers = {
        "cin_e4-sortie-porte": svg(porte_fond()),
        "cin_e4-sortie-battant": bande([plan_battant(k) for k in range(3)], ZONE_BATTANT),
        "cin_e4-sortie-foret": svg(foret()),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"e4_sortie_hopital : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
