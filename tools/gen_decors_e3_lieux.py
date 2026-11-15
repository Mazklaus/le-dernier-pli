#!/usr/bin/env python3
"""Génère les fonds des lieux de l'étape 3 (maison d'Ilde, clocher, chambre, chemins de nuit et d'aube).

Un seul plan fixe par lieu (pas de parallaxe : ce sont des pièces ou des chemins fermés),
découpé en tuiles de 2048 px au plus : art/src/env/e3/env_e3_plan3_<lieu>_NN.svg.
Repère local de chaque lieu (scenes/etapes/etape_03/lieux/*.tscn) : sol à y 900, plafond
de collision de 330 à 450, passages de 160 x 300 (y 600 à 900).

Même grammaire que la surface : murs chaulés en papier, peu de hachures. Les deux chemins
partagent le même dessin ; la nuit, les cierges plantés dans les champs brûlent (flammes en
papier nu), à l'aube ils sont éteints, la cire coulée jusqu'aux racines (détail champs_cierges).
La nuit elle-même vient de la teinte d'EtapeBase (lieux_nuit) : rien n'est assombri ici.

Usage : python3 tools/gen_decors_e3_lieux.py
"""
from __future__ import annotations

import math

from gen_decors_e1_surface import crete, rnd
from gen_decors_e3_surface import (DEFS, DST, ENCRE, H, LAVIS, MINE, PAPIER, SOL, ST, TUILE, fenetre,
                                   porte_bois)

PLAFOND = 330  # bas de la poutraison peinte : le plafond de collision commence là


def mur_interieur(w: int) -> str:
    """Pièce chaulée : mur en papier, poutres au plafond, plinthe salie, carreaux de terre cuite."""
    out = [f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>',
           # dessous du plancher de l'étage, dans l'ombre, et les solives
           f'<rect width="{w}" height="{PLAFOND + 120}" fill="{MINE}"/>',
           f'<rect y="{PLAFOND + 80}" width="{w}" height="40" fill="url(#h2)" {ST} stroke-width="3"/>']
    for y in range(40, PLAFOND, 70):
        out.append(f'<path d="M0 {y} H{w}" stroke="{LAVIS}" stroke-width="2"/>')
    for x in range(60, w, 240):
        out.append(f'<rect x="{x}" y="{PLAFOND - 20}" width="44" height="120" fill="url(#h2)" {ST} stroke-width="2.6"/>')
    out.append(f'<rect y="{SOL - 40}" width="{w}" height="40" fill="url(#v1)"/>')
    out.append(f'<path d="M0 {SOL - 40} H{w}" {ST} stroke-width="1.6"/>')
    # sol de tomettes, en perspective plate
    out.append(f'<rect y="{SOL}" width="{w}" height="{H - SOL}" fill="url(#h1)"/>')
    for y in range(SOL, H, 30):
        out.append(f'<path d="M0 {y} H{w}" {ST} stroke-width="1.6"/>')
    for x in range(0, w, 60):
        out.append(f'<path d="M{x} {SOL} L{x - 20} {H}" {ST} stroke-width="1.2"/>')
    out.append(f'<path d="M0 {SOL} H{w}" {ST} stroke-width="3"/>')
    return "".join(out)


def miche(px: float, py: float) -> str:
    return (f'<path d="M{px - 30:.0f} {py:.0f} Q{px - 30:.0f} {py - 34:.0f} {px:.0f} {py - 36:.0f} Q{px + 30:.0f} {py - 34:.0f} {px + 30:.0f} {py:.0f} Z" fill="{PAPIER}" {ST} stroke-width="2.2"/>'
            f'<path d="M{px - 14:.0f} {py - 26:.0f} L{px - 6:.0f} {py - 18:.0f} M{px + 2:.0f} {py - 30:.0f} L{px + 10:.0f} {py - 22:.0f}" {ST} stroke-width="1.6"/>')


def pain(x0: int, x1: int, y: int) -> str:
    """Une montagne de miches de pain blanc, en papier nu, qui déborde de la table et roule au sol :
    beaucoup trop pour une femme seule (ilde_pain)."""
    out = []
    larg = x1 - x0
    rangs = 7
    for rg in range(rangs):
        n = 7 - rg
        pas = larg / 7.4
        dx = x0 + 34 + rg * pas / 2
        for i in range(n):
            out.append(miche(dx + i * pas, y - rg * 30))
    # celles qui ont roulé : au bord, au sol, et une corbeille pleine sous la table
    out.append(miche(x1 + 16, y + 6))
    out.append(miche(x0 + 120, SOL))
    out.append(miche(x1 - 40, SOL))
    out.append(f'<path d="M{x0 + 170} {SOL} L{x0 + 160} {SOL - 70} H{x0 + 300} L{x0 + 290} {SOL} Z" fill="url(#h2)" {ST} stroke-width="2.4"/>')
    for i in range(3):
        out.append(miche(x0 + 190 + i * 40, SOL - 66))
    return "".join(out)


def table(x0: int, x1: int, haut: int = SOL - 130) -> str:
    return (f'<rect x="{x0}" y="{haut}" width="{x1 - x0}" height="18" fill="url(#h1)" {ST} stroke-width="2.6"/>'
            f'<path d="M{x0 + 16} {haut + 18} V{SOL} M{x1 - 16} {haut + 18} V{SOL}" {ST} stroke-width="10"/>')


def maison_ilde() -> str:
    w = 1920
    out = [mur_interieur(w)]
    out.append(porte_bois(120, 280))
    # fenêtre sur la rue, rideau de dentelle
    out.append(f'<rect x="380" y="520" width="160" height="200" fill="{ENCRE}" {ST} stroke-width="3"/>'
               f'<path d="M460 520 V720 M380 620 H540" stroke="{PAPIER}" stroke-width="3"/>'
               f'<rect x="372" y="720" width="176" height="10" fill="{PAPIER}" {ST} stroke-width="2"/>')
    # la table et le pain blanc
    out.append(table(560, 900))
    out.append(pain(560, 900, SOL - 130))
    # l'âtre : hotte de pierre, feu éteint, crémaillère
    out.append(f'<path d="M1180 {SOL} V620 L1140 560 H1440 L1400 620 V{SOL} Z" fill="url(#moellons)" {ST} stroke-width="3"/>')
    out.append(f'<path d="M1220 {SOL} V680 H1360 V{SOL} Z" fill="{ENCRE}"/>')
    out.append(f'<path d="M1290 680 V760 M1276 760 H1304" stroke="{MINE}" stroke-width="3"/>')
    out.append(f'<rect x="1150" y="548" width="280" height="14" fill="url(#h1)" {ST} stroke-width="2.2"/>')
    # sur le manteau : deux assiettes posées debout, une seule chaise devant le feu
    out.append(f'<ellipse cx="1220" cy="524" rx="22" ry="24" fill="{PAPIER}" {ST} stroke-width="2"/><ellipse cx="1360" cy="524" rx="22" ry="24" fill="{PAPIER}" {ST} stroke-width="2"/>')
    out.append(f'<path d="M1040 {SOL} V780 H1100 V{SOL} M1040 780 V680 M1040 700 H1060" fill="none" {ST} stroke-width="6"/>')
    # le lit clos (passage Lit, x 1520 à 1680) : une armoire à coucher, portes coulissantes ouvertes
    out.append(f'<rect x="1480" y="500" width="240" height="{SOL - 500}" fill="url(#h2)" {ST} stroke-width="3.4"/>')
    out.append(f'<path d="M1470 500 H1730 V480 H1470 Z" fill="url(#h1)" {ST} stroke-width="2.4"/>')
    out.append(f'<rect x="1520" y="600" width="160" height="{SOL - 650}" fill="{ENCRE}"/>')
    out.append(f'<path d="M1524 780 H1676 V820 H1524 Z" fill="{PAPIER}" {ST} stroke-width="2"/>')
    out.append(f'<path d="M1540 780 Q1560 750 1600 760" fill="none" stroke="{PAPIER}" stroke-width="3"/>')
    for cx in (1520, 1680):
        out.append(f'<circle cx="{cx - 16 if cx == 1520 else cx + 16}" cy="560" r="7" fill="none" {ST} stroke-width="2"/>')
    out.append(f'<path d="M1480 {SOL - 50} H1720" {ST} stroke-width="2"/>')
    # coffre au pied du lit
    out.append(f'<rect x="1740" y="{SOL - 90}" width="150" height="90" fill="url(#vantail)" {ST} stroke-width="2.6"/>')
    return "".join(out)


def clocher() -> str:
    """Bas de la tour : moellons nus, l'échelle vers le beffroi, les cordes coupées tombées au sol."""
    w = 1920
    out = [f'<rect width="{w}" height="{H}" fill="url(#moellons)"/>',
           f'<rect width="{w}" height="{PLAFOND + 120}" fill="{LAVIS}"/>',
           f'<rect y="{PLAFOND + 80}" width="{w}" height="40" fill="url(#h2)" {ST} stroke-width="3"/>']
    for x in range(100, w, 300):
        out.append(f'<rect x="{x}" y="0" width="50" height="{PLAFOND + 80}" fill="url(#h1)" {ST} stroke-width="2.6"/>')
    # trappe ouverte vers le beffroi : un carré de jour (papier nu) au plafond
    out.append(f'<rect x="740" y="{PLAFOND + 80}" width="140" height="40" fill="{PAPIER}" {ST} stroke-width="3"/>')
    # les cordes : deux bouts qui pendent de la trappe, coupés net bien au-dessus d'une main
    for x, bas in ((780, 600), (840, 560)):
        out.append(f'<path d="M{x} {PLAFOND + 120} V{bas}" {ST} stroke-width="9"/>')
        out.append(f'<path d="M{x - 6} {bas} H{x + 6}" {ST} stroke-width="3"/>')
    # ... et le reste, lové au sol (détail clocher_cordes, x 800)
    for i, r in enumerate((110, 86, 62, 40)):
        out.append(f'<ellipse cx="{800 + i * 6}" cy="{SOL - 12 - i * 10}" rx="{r}" ry="{r * .22:.0f}" fill="none" {ST} stroke-width="8"/>')
    out.append(f'<path d="M870 {SOL - 14} Q930 {SOL - 6} 960 {SOL - 24}" fill="none" {ST} stroke-width="6"/>')
    # l'échelle vers la trappe, contre le mur
    out.append(f'<path d="M900 {SOL} L860 {PLAFOND + 120} M980 {SOL} L940 {PLAFOND + 120}" {ST} stroke-width="8"/>')
    for t in range(1, 12):
        y = SOL - t * 40
        dx = (SOL - y) / (SOL - PLAFOND - 120) * 40
        out.append(f'<path d="M{900 - dx:.0f} {y} H{980 - dx:.0f}" {ST} stroke-width="5"/>')
    # porte de la rue (passage, x 120 à 280), meurtrière, banc du sonneur
    out.append(porte_bois(120, 280))
    out.append(f'<path d="M1560 520 V660 Q1560 676 1574 676 Q1588 676 1588 660 V520 Q1588 504 1574 504 Q1560 504 1560 520 Z" fill="{PAPIER}" {ST} stroke-width="3"/>')
    out.append(f'<rect x="1180" y="{SOL - 80}" width="360" height="16" fill="url(#h1)" {ST} stroke-width="2.4"/>'
               f'<path d="M1200 {SOL - 64} V{SOL} M1520 {SOL - 64} V{SOL}" {ST} stroke-width="8"/>')
    # la hache, posée contre le banc, propre
    out.append(f'<path d="M1560 {SOL} L1600 {SOL - 150}" {ST} stroke-width="7"/>'
               f'<path d="M1590 {SOL - 150} L1626 {SOL - 160} L1622 {SOL - 120} L1598 {SOL - 126} Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
    out.append(f'<rect y="{SOL}" width="{w}" height="{H - SOL}" fill="url(#terre)"/><path d="M0 {SOL} H{w}" {ST} stroke-width="3"/>')
    return "".join(out)


def chambre() -> str:
    w = 1440
    out = [mur_interieur(w)]
    # la fenêtre au volet cloué-décloué (détail chambre_volet, x 400) ; on voit passer la procession
    out.append(f'<rect x="300" y="520" width="200" height="220" fill="{ENCRE}" {ST} stroke-width="3"/>')
    out.append(f'<path d="M400 520 V740 M300 630 H500" stroke="{PAPIER}" stroke-width="3"/>')
    out.append(f'<rect x="292" y="740" width="216" height="10" fill="{PAPIER}" {ST} stroke-width="2"/>')
    out.append(f'<rect x="508" y="514" width="96" height="232" fill="url(#vantail)" {ST} stroke-width="2.6"/>')
    r = rnd(361)
    for _ in range(26):
        out.append(f'<circle cx="{r.uniform(516, 596):.0f}" cy="{r.choice((540, 628, 716)) + r.uniform(-6, 6):.0f}" r="2" fill="{ENCRE}"/>')
    # la porte de nuit (passage VersCheminNuit, x 920 à 1080)
    out.append(porte_bois(920, 1080))
    # le lit (passage VersCheminAube : on reste couché jusqu'à l'aube), x 1140 à 1420
    out.append(f'<path d="M1140 {SOL} V640 Q1140 610 1170 610 Q1200 610 1200 640 V760 H1380 V700 Q1380 670 1410 670 Q1430 680 1430 700 V{SOL}" fill="url(#h2)" {ST} stroke-width="3"/>')
    out.append(f'<path d="M1200 760 H1380 V800 H1200 Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
    out.append(f'<path d="M1210 760 Q1230 730 1270 740 Q1290 748 1280 760 Z" fill="{PAPIER}" {ST} stroke-width="2"/>')
    out.append(f'<path d="M1200 800 H1380 L1390 {SOL - 30} H1190 Z" fill="url(#h1)" {ST} stroke-width="2.4"/>')
    # chaise et bougeoir éteint
    out.append(f'<path d="M700 {SOL} V780 H760 V{SOL} M700 780 V680 M700 700 H720" fill="none" {ST} stroke-width="6"/>')
    out.append(f'<path d="M716 772 H748 M732 772 V748" {ST} stroke-width="3"/><rect x="726" y="728" width="12" height="20" fill="{PAPIER}" {ST} stroke-width="1.8"/>')
    # crucifix au mur, au-dessus du lit
    out.append(f'<path d="M1290 520 V600 M1270 544 H1310" {ST} stroke-width="5"/>')
    return "".join(out)


def chambre_large() -> str:
    """La chambre (1440) peinte sur 1920 : la caméra, centrée sur une pièce plus étroite que
    l'écran, montre 240 px de chaque côté. Ces marges sont les murs de la maison en coupe
    (lavis sous contre-hachure), comme une boîte : la pièce paraît close, ce qu'elle est.
    Le fond est posé à x -240 dans le repère du lieu (DecorE3)."""
    m = 240
    coupe = (f'<rect width="{m}" height="{H}" fill="{LAVIS}"/><rect width="{m}" height="{H}" fill="url(#v2)"/>'
             f'<path d="M{m - 3} 0 V{H}" {ST} stroke-width="5"/>')
    return (f'<g transform="translate({m} 0)">{chambre()}</g>'
            f'{coupe}<g transform="translate({1440 + 2 * m} 0) scale(-1 1)">{coupe}</g>')


def cierge(x: int, haut: int, allume: bool) -> str:
    """Cierge planté dans la terre, enfoncé profond ; allumé la nuit, éteint et coulé à l'aube."""
    s = [f'<rect x="{x - 8}" y="{SOL - haut}" width="16" height="{haut}" fill="{PAPIER}" {ST} stroke-width="1.8"/>',
         f'<path d="M{x - 9} {SOL} Q{x} {SOL - 8} {x + 9} {SOL}" fill="{PAPIER}" {ST} stroke-width="1.6"/>']
    if allume:
        s.append(f'<path d="M{x} {SOL - haut - 3} Q{x - 9} {SOL - haut - 18} {x} {SOL - haut - 38} Q{x + 9} {SOL - haut - 18} {x} {SOL - haut - 3} Z" fill="{PAPIER}" {ST} stroke-width="1.6"/>')
    else:
        s.append(f'<path d="M{x} {SOL - haut} V{SOL - haut - 8}" {ST} stroke-width="1.6"/>')
        s.append(f'<path d="M{x + 5} {SOL - haut + 6} Q{x + 9} {SOL - haut / 2:.0f} {x + 6} {SOL - 2}" fill="none" stroke="{MINE}" stroke-width="2.4"/>')
    return "".join(s)


def chemin(allume: bool) -> str:
    """Le chemin des champs derrière la maison d'Ilde : talus, champs plantés de cierges.
    La nuit est un vrai noir de gravure (contre-hachure dense) : les flammes des cierges, en
    réserve de papier, sont les seuls points clairs. L'aube reprend le papier."""
    if allume:
        return chemin_nuit()
    w = 3840
    out = [f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>']
    r = rnd(371)
    for _ in range(12):
        y = r.randint(40, 300)
        x = r.randint(-200, w)
        out.append(f'<path d="M{x} {y} H{x + r.randint(300, 800)}" stroke="{MINE}" stroke-width="1.4" opacity=".6"/>')
    out.append(f'<path d="M2640 520 A90 90 0 0 1 2820 520" fill="none" stroke="{MINE}" stroke-width="2.6"/>')
    # champs lointains, le clocher du village tout petit derrière (baie vide)
    out.append(f'<path d="M{crete(0, w, 520, 8, 160, 372)} L{w} {H} L0 {H} Z" fill="{MINE}"/>')
    out.append(f'<path d="M300 520 V420 L320 396 L340 420 V520 Z" fill="{MINE}"/><rect x="312" y="430" width="16" height="20" fill="{PAPIER}"/>')
    out.append(f'<path d="M{crete(0, w, 640, 10, 120, 373)} L{w} {H} L0 {H} Z" fill="{LAVIS}"/>')
    for y, pas, haut, ep in ((640, 70, 22, 4), (700, 90, 34, 6)):
        x = r.randint(20, 60)
        while x < w:
            out.append(f'<rect x="{x}" y="{y - haut}" width="{ep}" height="{haut}" fill="{PAPIER}"/>')
            x += pas + r.randint(-20, 20)
    out.append(f'<path d="M0 {SOL} V{SOL - 40} Q{w / 2:.0f} {SOL - 70} {w} {SOL - 40} V{SOL} Z" fill="url(#herbe)" {ST} stroke-width="2"/>')
    x = 140
    while x < w:
        if abs(x - 1800) > 60:
            out.append(cierge(x, r.randint(110, 170), False))
        x += r.randint(220, 380)
    out.append(cierge(1800, 190, False))
    out.append(f'<rect y="{SOL}" width="{w}" height="{H - SOL}" fill="url(#terre)"/><path d="M0 {SOL} H{w}" {ST} stroke-width="3"/>')
    out.append(f'<path d="M3440 {SOL} V{SOL - 70} Q3470 {SOL - 96} 3500 {SOL - 70} V{SOL} Z" fill="url(#moellons)" {ST} stroke-width="2.4"/>')
    return "".join(out)


def flamme(x: float, y: float, h: float, cerne: bool = True) -> str:
    """Flamme en papier nu, pointe en haut ; y est la mèche."""
    trait = f' {ST} stroke-width="1.6"' if cerne else ""
    return (f'<path d="M{x:.0f} {y:.0f} Q{x - h * .24:.0f} {y - h * .45:.0f} {x:.0f} {y - h:.0f} '
            f'Q{x + h * .24:.0f} {y - h * .45:.0f} {x:.0f} {y:.0f} Z" fill="{PAPIER}"{trait}/>')


def chemin_nuit() -> str:
    w = 3840
    r = rnd(371)
    # le ciel : lavis sous une contre-hachure d'encre serrée, un noir de gravure
    out = [f'<rect width="{w}" height="{H}" fill="{LAVIS}"/>',
           f'<rect width="{w}" height="{H}" fill="url(#v2)"/>']
    # lointain : lavis puis encre, le clocher du village en silhouette sans jour
    out.append(f'<path d="M{crete(0, w, 520, 8, 160, 372)} L{w} {H} L0 {H} Z" fill="{LAVIS}"/>')
    out.append(f'<path d="M300 520 V420 L320 396 L340 420 V520 Z" fill="{LAVIS}"/>')
    out.append(f'<path d="M{crete(0, w, 640, 10, 120, 373)} L{w} {H} L0 {H} Z" fill="{ENCRE}"/>')
    # cierges des champs : le corps se perd dans le noir, seules les flammes restent
    for y, pas, h in ((640, 70, 12), (700, 90, 18)):
        x = r.randint(20, 60)
        while x < w:
            out.append(f'<rect x="{x - 1}" y="{y - h * 1.6:.0f}" width="{2 + h // 8}" height="{h * 1.6:.0f}" fill="{LAVIS}"/>')
            out.append(flamme(x, y - h * 1.6, h, cerne=False))
            x += pas + r.randint(-20, 20)
    # talus en silhouette
    out.append(f'<path d="M0 {SOL} V{SOL - 40} Q{w / 2:.0f} {SOL - 70} {w} {SOL - 40} V{SOL} Z" fill="{ENCRE}"/>')
    # cierges du bord du chemin : une réserve de papier autour de chaque flamme, nette
    x = 140
    while x < w:
        haut = 190 if abs(x - 1800) <= 60 else r.randint(110, 170)
        if abs(x - 1800) <= 60:
            x = 1800
        out.append(f'<circle cx="{x}" cy="{SOL - haut - 16}" r="30" fill="{PAPIER}"/>')
        out.append(f'<rect x="{x - 8}" y="{SOL - haut}" width="16" height="{haut}" fill="{MINE}" {ST} stroke-width="1.8"/>')
        out.append(flamme(x, SOL - haut - 3, 36))
        out.append(f'<path d="M{x} {SOL - haut - 3} V{SOL - haut + 4}" {ST} stroke-width="1.6"/>')
        x += r.randint(220, 380)
    # le sol du chemin, sombre
    out.append(f'<rect y="{SOL}" width="{w}" height="{H - SOL}" fill="{LAVIS}"/>')
    out.append(f'<rect y="{SOL}" width="{w}" height="{H - SOL}" fill="url(#v1)"/>')
    out.append(f'<path d="M0 {SOL} H{w}" stroke="{ENCRE}" stroke-width="3"/>')
    out.append(f'<path d="M3440 {SOL} V{SOL - 70} Q3470 {SOL - 96} 3500 {SOL - 70} V{SOL} Z" fill="{ENCRE}"/>')
    return "".join(out)


def ecrire(nom: str, contenu: str, largeur: int) -> int:
    DST.mkdir(parents=True, exist_ok=True)
    n = math.ceil(largeur / TUILE)
    for i in range(n):
        x0 = i * TUILE
        w = min(TUILE, largeur - x0)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="{x0} 0 {w} {H}">'
               f'{DEFS}{contenu}</svg>\n')
        (DST / f"env_e3_plan3_{nom}_{i + 1:02d}.svg").write_text(svg, encoding="utf-8")
    return n


def main() -> None:
    total = ecrire("maison-ilde", maison_ilde(), 1920)
    total += ecrire("clocher", clocher(), 1920)
    total += ecrire("chambre", chambre_large(), 1920)
    total += ecrire("chemin-nuit", chemin(True), 3840)
    total += ecrire("chemin-aube", chemin(False), 3840)
    # La croisée de la fenêtre de la chambre, seule, sur fond transparent : posée par le code
    # au-dessus du cortège de la procession (vu par la fenêtre), en (300, 520) dans le lieu.
    fx = DST.parent.parent / "fx"
    fx.mkdir(parents=True, exist_ok=True)
    (fx / "fx_croisee-chambre.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="230" viewBox="300 520 200 230">{DEFS}'
        f'<rect x="300" y="520" width="200" height="220" fill="none" {ST} stroke-width="3"/>'
        f'<path d="M400 520 V740 M300 630 H500" stroke="{PAPIER}" stroke-width="3"/>'
        f'<rect x="292" y="740" width="216" height="10" fill="{PAPIER}" {ST} stroke-width="2"/></svg>\n', encoding="utf-8")
    print(f"{total} tuiles de lieux dans art/src/env/e3")


if __name__ == "__main__":
    main()
