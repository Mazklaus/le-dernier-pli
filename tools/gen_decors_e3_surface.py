#!/usr/bin/env python3
"""Génère les sources SVG des décors de surface de l'étape 3, le Village aux cloches muettes.

Même méthode que les étapes 1 et 2 : chaque plan est dessiné en coordonnées monde, puis
découpé en tuiles de 2048 px au plus dans art/src/env/e3/env_e3_planN_<nom>_NN.svg.
Positions reprises de scenes/etapes/etape_03/etape_03.tscn : lisière (0 à 2880) puis rue et
place (2880 à 7680), sol plat à y 900.

Parti pris : après le No Man's Land, un village trop intact. Murs chaulés laissés en papier,
peu de hachures, rien de cassé. L'étrangeté tient en deux fausses notes : les lampions de la
noce pendus à l'envers (flamme vers le bas) et la baie vide du clocher, où l'on voit le ciel.
La nuit vient de la teinte d'EtapeBase : aucun changement de lumière n'est peint ici.
Le papier chaud de l'étape vient du shader : tout reste dessiné sur #E8E5DA.

Usage : python3 tools/gen_decors_e3_surface.py
"""
from __future__ import annotations

import math
from pathlib import Path

from gen_decors_e1_surface import DEFS as DEFS_E1, ENCRE, LAVIS, MINE, PAPIER, crete, rnd

ROOT = Path(__file__).resolve().parent.parent
DST = ROOT / "art" / "src" / "env" / "e3"
H = 1080
TUILE = 2048
VUE = 1920
LARGEUR = 7680
VITESSES = {0: 0.05, 1: 0.2, 2: 0.5, 3: 1.0, 4: 1.4}
SOL = 900
ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'

# Repères de la maquette (coordonnées monde)
FUSILS_X = 900            # détail lisiere_fusils
LISIERE_X = 1500          # rencontre e3_lisiere
VILLAGE_X = 2400          # premiers pavés
PORTE_ILDE = (3920, 4080)  # passage VersMaisonIlde (centre 4000, zone 3920 à 4080)
LAMPIONS_X = 4800         # détail place_lampions
NOCE_X = 5300             # rencontre e3_noce
PORTE_CLOCHER = (6520, 6680)  # passage VersClocher (centre 6600)

DEFS = DEFS_E1.replace("</defs>", f"""
<pattern id="paves" width="46" height="26" patternUnits="userSpaceOnUse"><rect width="46" height="26" fill="{PAPIER}"/><path d="M3 12 Q3 3 12 3 L34 3 Q43 3 43 12 Q43 22 34 22 L12 22 Q3 22 3 12 Z M-20 25 Q-20 16 -11 16 M26 25 Q26 16 35 16" fill="none" stroke="{ENCRE}" stroke-width="1.6"/></pattern>
<pattern id="tuiles" width="30" height="22" patternUnits="userSpaceOnUse"><rect width="30" height="22" fill="url(#h1)"/><path d="M0 0 Q7.5 14 15 0 Q22.5 14 30 0 M-15 11 Q-7.5 25 0 11 Q7.5 25 15 11 Q22.5 25 30 11 Q37.5 25 45 11" fill="none" stroke="{ENCRE}" stroke-width="1.8"/></pattern>
<pattern id="moellons" width="72" height="36" patternUnits="userSpaceOnUse"><rect width="72" height="36" fill="{PAPIER}"/><path d="M0 0 H72 M0 18 H72 M24 0 V18 M60 0 V18 M10 18 V36 M46 18 V36" stroke="{ENCRE}" stroke-width="1.7"/><path d="M30 6 L36 10 M52 26 L58 24" stroke="{ENCRE}" stroke-width="1"/></pattern>
<pattern id="vantail" width="26" height="40" patternUnits="userSpaceOnUse"><rect width="26" height="40" fill="url(#h1)"/><path d="M0 0 V40" stroke="{ENCRE}" stroke-width="2"/><circle cx="13" cy="8" r="1.4" fill="{ENCRE}"/></pattern>
<pattern id="herbe" width="24" height="16" patternUnits="userSpaceOnUse"><rect width="24" height="16" fill="{PAPIER}"/><path d="M3 16 L5 6 M8 16 L7 9 M15 16 L18 4 M20 16 L21 10" stroke="{ENCRE}" stroke-width="1.2"/></pattern>
</defs>""")


# ---------------------------------------------------------------- plan 3 : la surface

def maison(x0: int, x1: int, mur: int, faite: int, fenetres: list[int], porte: tuple[int, int] | None = None,
           etage: bool = True, volets: bool = True) -> str:
    """Maison chaulée vue de face : mur en papier, toit de tuiles, pied du mur sali."""
    cx = (x0 + x1) / 2
    out = [
        # toit en bâtière, débord des deux côtés
        f'<path d="M{x0 - 22} {mur} L{cx:.0f} {faite} L{x1 + 22} {mur} Z" fill="url(#tuiles)" {ST} stroke-width="3"/>',
        f'<rect x="{x0}" y="{mur}" width="{x1 - x0}" height="{SOL - mur}" fill="{PAPIER}" {ST} stroke-width="3"/>',
        f'<rect x="{x0}" y="{SOL - 46}" width="{x1 - x0}" height="46" fill="url(#v1)"/>',
        f'<path d="M{x0} {mur + 10} H{x1}" {ST} stroke-width="1.4"/>',
    ]
    # cheminée
    chx = int(cx + (x1 - x0) * .22)
    pente = (mur - faite) / ((x1 - x0) / 2 + 22)
    chy = faite + (chx - cx) * pente
    out.append(f'<path d="M{chx} {chy + 12:.0f} L{chx} {faite - 30} L{chx + 34} {faite - 30} L{chx + 34} {chy + 38:.0f} Z" fill="url(#moellons)" {ST} stroke-width="2.4"/>')
    rangs = [mur + 50] + ([mur + 50 + 190] if etage and SOL - mur > 420 else [])
    if etage and SOL - mur > 420:
        rangs = [mur + 50, mur + 250]
    for fy in rangs:
        for fx in fenetres:
            if porte and porte[0] - 40 < fx + 60 and fx < porte[1] + 40 and fy + 110 > 582:
                continue
            out.append(fenetre(fx, fy, volets))
    if porte:
        out.append(porte_bois(*porte))
    return "".join(out)


def fenetre(x: int, y: int, volets: bool = True) -> str:
    """Fenêtre à petits bois, vitres noires ; volets ouverts en planches hachurées."""
    w, h = 64, 96
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{ENCRE}"/>',
         f'<path d="M{x + w / 2} {y} V{y + h} M{x} {y + h / 2} H{x + w}" stroke="{PAPIER}" stroke-width="3"/>',
         f'<rect x="{x - 6}" y="{y + h}" width="{w + 12}" height="8" fill="{PAPIER}" {ST} stroke-width="2"/>']
    if volets:
        for vx in (x - 34, x + w + 4):
            s.append(f'<rect x="{vx}" y="{y - 2}" width="30" height="{h + 4}" fill="url(#h1)" {ST} stroke-width="2"/>')
            s.append(f'<path d="M{vx} {y + 24} H{vx + 30} M{vx} {y + h - 22} H{vx + 30}" {ST} stroke-width="1.6"/>')
    return "".join(s)


def porte_bois(x0: int, x1: int, haut: int = 600) -> str:
    """Porte de bois à linteau de pierre (la taille du passage de la maquette : 160 x 300)."""
    return (f'<path d="M{x0 - 16} {haut - 18} H{x1 + 16} V{haut} H{x0 - 16} Z" fill="url(#moellons)" {ST} stroke-width="2.4"/>'
            f'<rect x="{x0}" y="{haut}" width="{x1 - x0}" height="{SOL - haut}" fill="url(#vantail)" {ST} stroke-width="3"/>'
            f'<path d="M{(x0 + x1) / 2:.0f} {haut} V{SOL}" {ST} stroke-width="2"/>'
            f'<circle cx="{x1 - 22}" cy="{haut + 160}" r="5" fill="{ENCRE}"/>'
            f'<path d="M{x0 - 10} {SOL} H{x1 + 10} V{SOL - 10} H{x0 - 10} Z" fill="{PAPIER}" {ST} stroke-width="2"/>')


def arbre(x: int, haut: int, larg: int, seed: int) -> str:
    """Grand arbre de lisière : tronc hachuré, houppier gravé (contre-hachure), feuillu."""
    r = rnd(seed)
    pts = []
    n = 14
    for i in range(n):
        a = math.pi * (1.05 + i / (n - 1) * -1.1)
        rr = larg * r.uniform(.8, 1.05)
        pts.append(f"{x + math.cos(a) * rr:.0f} {haut + 160 - math.sin(a) * rr * .8:.0f}")
    houppier = "M" + " Q".join(f"{p} {q}" for p, q in zip(pts[::2], pts[1::2])) + " Z"
    return (f'<path d="M{x - 18} {SOL} Q{x - 8} {haut + 300} {x - 14} {haut + 140} L{x + 14} {haut + 140} Q{x + 10} {haut + 300} {x + 22} {SOL} Z" fill="url(#h2)" {ST} stroke-width="3"/>'
            f'<path d="{houppier}" fill="url(#h2)" {ST} stroke-width="3"/>'
            f'<path d="M{x} {haut + 190} L{x - larg * .4:.0f} {haut + 120} M{x} {haut + 220} L{x + larg * .45:.0f} {haut + 150}" fill="none" {ST} stroke-width="5"/>')


def fusils_de_bois(x0: int) -> str:
    """Six fusils taillés dans le bois, alignés contre le mur, sans gâchette (détail lisiere_fusils)."""
    out = []
    for i in range(6):
        x = x0 + i * 30
        # crosse au sol, canon contre le mur, légère inclinaison
        out.append(f'<path d="M{x} {SOL} L{x + 18} {SOL} L{x + 30} {SOL - 70} L{x + 36} {SOL - 210} L{x + 30} {SOL - 212} L{x + 20} {SOL - 76} Z" fill="url(#h1)" {ST} stroke-width="2.2"/>')
        out.append(f'<path d="M{x + 4} {SOL - 8} L{x + 22} {SOL - 44}" {ST} stroke-width="1.2"/>')
    return "".join(out)


def calvaire(x: int) -> str:
    """Croix de chemin à petit toit, en bois, au bout de la lisière."""
    return (f'<path d="M{x - 30} {SOL} L{x + 30} {SOL} L{x + 22} {SOL - 30} L{x - 22} {SOL - 30} Z" fill="url(#moellons)" {ST} stroke-width="2.4"/>'
            f'<rect x="{x - 9}" y="{SOL - 330}" width="18" height="300" fill="url(#h1)" {ST} stroke-width="2.6"/>'
            f'<rect x="{x - 70}" y="{SOL - 270}" width="140" height="16" fill="url(#h1)" {ST} stroke-width="2.6"/>'
            f'<path d="M{x - 48} {SOL - 316} L{x} {SOL - 352} L{x + 48} {SOL - 316}" fill="none" {ST} stroke-width="5"/>')


def barriere(x0: int, x1: int, y: int = SOL) -> str:
    out = [f'<path d="M{x0} {y - 70} H{x1} M{x0} {y - 34} H{x1}" {ST} stroke-width="5"/>']
    for x in range(x0, x1 + 1, 90):
        out.append(f'<path d="M{x} {y} L{x} {y - 94} L{x + 6} {y - 102} L{x + 12} {y - 94} L{x + 12} {y} Z" fill="url(#h1)" {ST} stroke-width="2"/>')
    return "".join(out)


def lampion(x: float, y: float, i: int) -> str:
    """Lampion de papier plissé pendu À L'ENVERS : la bouche et la flamme tournées vers le sol."""
    h = 40 + (i % 3) * 6
    w = 32 + (i % 2) * 6
    haut, bas = y + 10, y + 10 + h
    plis = "".join(f'M{x - w / 2 + 2:.0f} {haut + h * t:.0f} Q{x:.0f} {haut + h * t + 5:.0f} {x + w / 2 - 2:.0f} {haut + h * t:.0f} '
                   for t in (.28, .5, .72))
    return (f'<path d="M{x:.0f} {y:.0f} L{x:.0f} {haut:.0f}" {ST} stroke-width="1.6"/>'
            # le corps plissé, ovale, entre deux bagues
            f'<path d="M{x - w * .3:.0f} {haut:.0f} Q{x - w / 2 - 6:.0f} {haut + h / 2:.0f} {x - w * .3:.0f} {bas:.0f} L{x + w * .3:.0f} {bas:.0f} Q{x + w / 2 + 6:.0f} {haut + h / 2:.0f} {x + w * .3:.0f} {haut:.0f} Z" fill="{PAPIER}" {ST} stroke-width="2.2"/>'
            f'<path d="{plis}" fill="none" stroke="{MINE}" stroke-width="1.4"/>'
            f'<rect x="{x - w * .3 - 2:.0f}" y="{haut - 3:.0f}" width="{w * .6 + 4:.0f}" height="5" fill="{ENCRE}"/>'
            # la bouche, en bas, plus large : c'est elle qui devrait être en haut
            f'<rect x="{x - w * .34 - 2:.0f}" y="{bas - 2:.0f}" width="{w * .68 + 4:.0f}" height="7" fill="{ENCRE}"/>'
            # la flamme pend vers le bas, nette, en papier cerné
            f'<path d="M{x:.0f} {bas + 5:.0f} Q{x - 6:.0f} {bas + 15:.0f} {x:.0f} {bas + 29:.0f} Q{x + 6:.0f} {bas + 15:.0f} {x:.0f} {bas + 5:.0f} Z" fill="{PAPIER}" {ST} stroke-width="1.6"/>')


def guirlande(x0: int, y0: int, x1: int, y1: int, fleche: int, n: int, seed: int) -> str:
    """Fil tendu entre deux façades, lampions pendus à l'envers."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + fleche
    out = [f'<path d="M{x0} {y0} Q{cx:.0f} {cy:.0f} {x1} {y1}" fill="none" {ST} stroke-width="2"/>']
    for i in range(1, n + 1):
        t = i / (n + 1)
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        out.append(lampion(x, y, i + seed))
    return "".join(out)


def table_de_noce(x0: int, x1: int) -> str:
    """Longue table nappée de blanc, bancs, pichets : la noce attend ses convives (e3_noce)."""
    out = [f'<path d="M{x0} {SOL - 112} H{x1} L{x1 + 10} {SOL - 70} H{x0 - 10} Z" fill="{PAPIER}" {ST} stroke-width="2.6"/>',
           f'<path d="M{x0 - 10} {SOL - 70} Q{x0 + 60} {SOL - 58} {x0 + 120} {SOL - 70} T{x0 + 240} {SOL - 70} T{x0 + 360} {SOL - 70} T{x0 + 480} {SOL - 70} T{x1 + 10} {SOL - 70}" fill="none" {ST} stroke-width="2"/>']
    for lx in (x0 + 20, x1 - 30):
        out.append(f'<rect x="{lx}" y="{SOL - 66}" width="12" height="66" fill="url(#h1)" {ST} stroke-width="2"/>')
    out.append(f'<rect x="{x0 - 30}" y="{SOL - 52}" width="{x1 - x0 + 60}" height="12" fill="url(#h1)" {ST} stroke-width="2"/>')
    for px in range(x0 + 60, x1 - 40, 130):
        out.append(f'<path d="M{px} {SOL - 112} L{px - 2} {SOL - 140} Q{px + 10} {SOL - 152} {px + 22} {SOL - 140} L{px + 20} {SOL - 112} Z" fill="url(#h1)" {ST} stroke-width="1.8"/>')
        out.append(f'<ellipse cx="{px + 64}" cy="{SOL - 114}" rx="20" ry="5" fill="{PAPIER}" {ST} stroke-width="1.6"/>')
    return "".join(out)


def puits(x: int) -> str:
    return (f'<path d="M{x - 70} {SOL} V{SOL - 90} H{x + 70} V{SOL} Z" fill="url(#moellons)" {ST} stroke-width="2.6"/>'
            f'<path d="M{x - 60} {SOL - 90} V{SOL - 250} M{x + 60} {SOL - 90} V{SOL - 250} M{x - 76} {SOL - 250} L{x} {SOL - 300} L{x + 76} {SOL - 250}" fill="none" {ST} stroke-width="6"/>'
            f'<path d="M{x - 60} {SOL - 210} H{x + 60} M{x} {SOL - 210} V{SOL - 150}" {ST} stroke-width="3"/>'
            f'<path d="M{x - 14} {SOL - 150} H{x + 14} L{x + 10} {SOL - 124} H{x - 10} Z" fill="url(#h1)" {ST} stroke-width="2"/>')


def eglise() -> str:
    """Nef basse puis clocher à baie vide : on voit le ciel là où devraient pendre les cloches."""
    nx0, nx1 = 6060, 6440
    tx0, tx1 = 6440, 6760
    out = [
        # nef : mur de moellons, toit d'ardoise sombre
        f'<path d="M{nx0 - 20} 560 L{nx0 + 80} 430 L{nx1} 430 L{nx1} 560 Z" fill="{LAVIS}" {ST} stroke-width="3"/>',
        f'<rect x="{nx0}" y="560" width="{nx1 - nx0}" height="{SOL - 560}" fill="url(#moellons)" {ST} stroke-width="3"/>',
        f'<path d="M6180 820 V700 Q6180 650 6230 650 Q6280 650 6280 700 V820 Z" fill="{ENCRE}"/>',
        f'<path d="M6230 650 V820 M6180 735 H6280" stroke="{PAPIER}" stroke-width="2.6"/>',
        # tour : jusqu'au haut de l'écran, contreforts
        f'<rect x="{tx0}" y="-20" width="{tx1 - tx0}" height="{SOL + 20}" fill="url(#moellons)" {ST} stroke-width="3.4"/>',
        f'<path d="M{tx0 - 24} {SOL} L{tx0} {SOL - 260} M{tx1 + 24} {SOL} L{tx1} {SOL - 260}" {ST} stroke-width="3"/>',
        f'<path d="M{tx0 - 24} {SOL} L{tx0} {SOL - 260} L{tx0} {SOL} Z M{tx1 + 24} {SOL} L{tx1} {SOL - 260} L{tx1} {SOL} Z" fill="url(#h2)" {ST} stroke-width="2.4"/>',
        # bandeau et baie : deux arcs ouverts sur le ciel (papier nu), rien ne pend
        f'<path d="M{tx0 - 10} 330 H{tx1 + 10} V346 H{tx0 - 10} Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>',
    ]
    for bx in (6490, 6620):
        out.append(f'<path d="M{bx} 310 V170 Q{bx} 110 {bx + 50} 110 Q{bx + 100} 110 {bx + 100} 170 V310 Z" fill="{PAPIER}" {ST} stroke-width="3"/>')
        out.append(f'<path d="M{bx + 6} 310 V176 Q{bx + 6} 120 {bx + 50} 118" fill="none" stroke="{MINE}" stroke-width="2"/>')
    # la poutre du beffroi, vide, et un bout de corde coupé net
    out.append(f'<rect x="{tx0 + 10}" y="150" width="{tx1 - tx0 - 20}" height="14" fill="url(#h1)" {ST} stroke-width="2.2"/>')
    out.append(f'<path d="M6672 164 V196" {ST} stroke-width="2.2"/><path d="M6666 196 H6678" {ST} stroke-width="1.6"/>')
    # cadran d'horloge sans aiguilles
    out.append(f'<circle cx="6600" cy="460" r="52" fill="{PAPIER}" {ST} stroke-width="3"/>')
    out.extend(f'<path d="M{6600 + math.cos(a) * 42:.0f} {460 + math.sin(a) * 42:.0f} L{6600 + math.cos(a) * 50:.0f} {460 + math.sin(a) * 50:.0f}" {ST} stroke-width="2.4"/>'
               for a in [i * math.pi / 6 for i in range(12)])
    # porte du clocher (passage VersClocher), en arc
    x0, x1 = PORTE_CLOCHER
    out.append(f'<path d="M{x0 - 16} {SOL} V640 Q{x0 - 16} 584 {(x0 + x1) / 2:.0f} 584 Q{x1 + 16} 584 {x1 + 16} 640 V{SOL} Z" fill="url(#moellons)" {ST} stroke-width="2.6"/>')
    out.append(f'<path d="M{x0} {SOL} V644 Q{x0} 600 {(x0 + x1) / 2:.0f} 600 Q{x1} 600 {x1} 644 V{SOL} Z" fill="url(#vantail)" {ST} stroke-width="3"/>')
    out.append(f'<path d="M{(x0 + x1) / 2:.0f} 600 V{SOL}" {ST} stroke-width="2"/><circle cx="{x1 - 20}" cy="770" r="6" fill="{ENCRE}"/>')
    return "".join(out)


def sol() -> str:
    """Herbe à la lisière, pavés au village ; terre gravée sous le niveau du jeu."""
    bord = crete(0, VILLAGE_X, SOL - 4, 4, 40, 301)
    return (f'<rect x="0" y="{SOL}" width="{LARGEUR}" height="{H - SOL}" fill="url(#terre)"/>'
            f'<path d="M{bord} L{VILLAGE_X} {SOL + 40} L0 {SOL + 40} Z" fill="url(#herbe)" {ST} stroke-width="2.2"/>'
            f'<rect x="{VILLAGE_X}" y="{SOL}" width="{LARGEUR - VILLAGE_X}" height="56" fill="url(#paves)" {ST} stroke-width="2.4"/>'
            f'<path d="M{VILLAGE_X - 30} {SOL + 4} Q{VILLAGE_X - 10} {SOL - 6} {VILLAGE_X + 10} {SOL}" fill="none" {ST} stroke-width="2"/>')


def plan3() -> str:
    out = []
    # lisière : grands arbres feuillus, intacts (ce qui frappe après le No Man's Land)
    for x, haut, larg, s in ((140, 40, 210, 1), (470, 110, 170, 2), (1290, 20, 230, 3), (1980, 90, 190, 4)):
        out.append(arbre(x, haut, larg, s))
    # mur de jardin et les fusils de bois
    out.append(f'<rect x="650" y="700" width="520" height="{SOL - 700}" fill="url(#moellons)" {ST} stroke-width="3"/>')
    out.append(f'<path d="M640 700 H1180 L1170 684 H650 Z" fill="url(#h1)" {ST} stroke-width="2.4"/>')
    out.append(fusils_de_bois(FUSILS_X - 90))
    out.append(calvaire(LISIERE_X + 180))
    out.append(barriere(2050, 2400))
    # la rue : maisons chaulées serrées
    out.append(maison(2420, 2980, 470, 300, [2490, 2640, 2810]))
    out.append(maison(3000, 3520, 520, 380, [3070, 3260, 3410], porte=(3200, 3330)))
    # maison d'Ilde : la porte du passage, un pot de fleurs à la fenêtre
    out.append(maison(3560, 4200, 450, 260, [3620, 3780], porte=PORTE_ILDE))
    out.append(f'<path d="M3770 640 H3854 L3846 664 H3778 Z" fill="url(#h1)" {ST} stroke-width="2"/>'
               f'<path d="M3790 640 Q3786 616 3800 606 M3812 640 Q3814 612 3828 604 M3834 640 Q3840 622 3848 618" fill="none" {ST} stroke-width="2"/>')
    # portail fermé derrière la maison d'Ilde : le chemin des champs, clos le jour
    out.append(f'<rect x="4200" y="660" width="120" height="{SOL - 660}" fill="url(#moellons)" {ST} stroke-width="2.6"/>')
    out.append(f'<rect x="4214" y="680" width="92" height="{SOL - 680}" fill="url(#vantail)" {ST} stroke-width="2.6"/>')
    out.append(f'<path d="M4214 700 L4306 880 M4210 790 H4310" {ST} stroke-width="4"/>')
    # la place : façades du fond plus basses, puits, guirlandes de lampions à l'envers, la noce
    out.append(maison(4320, 4760, 560, 420, [4390, 4560], etage=False))
    out.append(puits(4560))
    out.append(maison(5700, 6040, 540, 400, [5760, 5920], etage=False))
    out.append(guirlande(4180, 470, 5000, 450, 120, 9, 0))
    out.append(guirlande(5000, 450, 5760, 560, 110, 8, 1))
    out.append(f'<path d="M5000 900 L5004 430" {ST} stroke-width="10"/>')
    out.append(f'<path d="M4986 430 H5022" {ST} stroke-width="5"/>')
    out.append(table_de_noce(NOCE_X - 260, NOCE_X + 300))
    out.append(eglise())
    # dernière maison et la ruelle sans issue (mur de droite)
    out.append(maison(6820, 7420, 480, 320, [6880, 7060, 7260], porte=(7110, 7230)))
    out.append(f'<rect x="7420" y="560" width="260" height="{SOL - 560}" fill="url(#moellons)" {ST} stroke-width="3"/>')
    out.append(f'<path d="M7470 900 V700 H7630 V900 Z" fill="{ENCRE}"/>')
    out.append(sol())
    return "".join(out)


# ---------------------------------------------------------------- plans lointains

def plan2(w: int) -> str:
    """Toits du village en lavis derrière la rue ; vergers du côté de la lisière."""
    out = [f'<path d="M{crete(0, w, 640, 6, 160, 321)} L{w} {H} L0 {H} Z" fill="{LAVIS}"/>']
    r = rnd(322)
    x = 40
    while x < 1500:
        rr = r.randint(60, 90)
        out.append(f'<circle cx="{x}" cy="{620 - rr * .4:.0f}" r="{rr}" fill="{LAVIS}"/>')
        out.append(f'<rect x="{x - 8}" y="600" width="16" height="60" fill="{LAVIS}"/>')
        x += r.randint(140, 220)
    x = 1600
    while x < w:
        lg = r.randint(220, 380)
        haut = r.randint(470, 540)
        out.append(f'<path d="M{x} 660 V{haut + 40} L{x + lg / 2:.0f} {haut - 70} L{x + lg} {haut + 40} V660 Z" fill="{LAVIS}"/>')
        if r.random() < .7:
            cx = x + int(lg * r.uniform(.2, .7))
            out.append(f'<rect x="{cx}" y="{haut - 60}" width="26" height="70" fill="{LAVIS}"/>')
        if r.random() < .6:
            out.append(f'<rect x="{x + lg * .3:.0f}" y="{haut + 80}" width="30" height="40" fill="{MINE}"/>')
        x += lg + r.randint(-30, 60)
    return "".join(out)


def plan1(w: int) -> str:
    """Champs en pente douce, rangée de peupliers, chemin blanc qui monte."""
    out = [f'<path d="M{crete(0, w, 520, 10, 140, 331)} L{w} {H} L0 {H} Z" fill="{MINE}"/>',
           f'<path d="M{w * .35:.0f} {H} Q{w * .45:.0f} 640 {w * .62:.0f} 540" fill="none" stroke="{PAPIER}" stroke-width="10"/>']
    for y in (600, 680, 780):
        out.append(f'<path d="M0 {y} Q{w / 2:.0f} {y - 30} {w} {y + 10}" fill="none" stroke="{LAVIS}" stroke-width="1.6" opacity=".7"/>')
    r = rnd(332)
    for x in range(120, w, 150):
        if r.random() < .25:
            continue
        hh = r.randint(110, 160)
        out.append(f'<path d="M{x} 520 Q{x - 16} {520 - hh * .6:.0f} {x} {520 - hh} Q{x + 16} {520 - hh * .6:.0f} {x} 520 Z" fill="{MINE}"/>')
    return "".join(out)


def plan0(w: int) -> str:
    out = [f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>']
    r = rnd(341)
    for _ in range(10):
        y = r.randint(60, 380)
        x = r.randint(-200, w)
        out.append(f'<path d="M{x} {y} H{x + r.randint(300, 800)}" stroke="{MINE}" stroke-width="1.4" opacity=".6"/>')
    out.append(f'<circle cx="{int(w * .3)}" cy="150" r="56" fill="none" stroke="{MINE}" stroke-width="2.6"/>')
    return "".join(out)


def plan4(w: int) -> str:
    """Premier plan : touffes d'herbe à la lisière, bornes et une roue de charrette au village."""
    out = []
    r = rnd(351)
    x = 260
    lisiere = int(VILLAGE_X * 1.4 - 0.4 * 960)
    while x < w:
        if x < lisiere:
            larg = r.randint(140, 260)
            out.append(f'<path d="M{x} {H} Q{x + larg * .2:.0f} {H - r.randint(70, 120)} {x + larg * .35:.0f} {H - 30} Q{x + larg * .5:.0f} {H - r.randint(90, 140)} {x + larg * .65:.0f} {H - 30} Q{x + larg * .8:.0f} {H - r.randint(60, 110)} {x + larg} {H} Z" fill="{ENCRE}"/>')
            x += larg + r.randint(700, 1300)
        else:
            if r.random() < .5:
                out.append(f'<path d="M{x} {H} V{H - 90} Q{x + 40} {H - 120} {x + 80} {H - 90} V{H} Z" fill="{ENCRE}"/>')
            else:
                cy = H + 40
                out.append(f'<circle cx="{x + 120}" cy="{cy}" r="150" fill="none" stroke="{ENCRE}" stroke-width="16"/>')
                out.extend(f'<path d="M{x + 120} {cy} L{x + 120 + math.cos(a) * 150:.0f} {cy + math.sin(a) * 150:.0f}" stroke="{ENCRE}" stroke-width="9"/>'
                           for a in [-math.pi * (i + .5) / 6 for i in range(6)])
                out.append(f'<circle cx="{x + 120}" cy="{cy}" r="26" fill="{ENCRE}"/>')
            x += r.randint(1300, 2000)
    return "".join(out)


def ecrire_tuiles(plan: int, nom: str, contenu: str, largeur: int) -> int:
    DST.mkdir(parents=True, exist_ok=True)
    n = math.ceil(largeur / TUILE)
    for i in range(n):
        x0 = i * TUILE
        w = min(TUILE, largeur - x0)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="{x0} 0 {w} {H}">'
               f'{DEFS}{contenu}</svg>\n')
        (DST / f"env_e3_plan{plan}_{nom}_{i + 1:02d}.svg").write_text(svg, encoding="utf-8")
    return n


def largeur_plan(v: float) -> int:
    return int(round(VUE + (LARGEUR - VUE) * v))


def main() -> None:
    total = 0
    for p, nom, f in ((0, "ciel", plan0), (1, "lointain", plan1), (2, "milieu", plan2), (4, "premier-plan", plan4)):
        w = largeur_plan(VITESSES[p])
        total += ecrire_tuiles(p, nom, f(w), w)
    total += ecrire_tuiles(3, "surface", plan3(), LARGEUR)
    print(f"{total} tuiles dans art/src/env/e3")


if __name__ == "__main__":
    main()
