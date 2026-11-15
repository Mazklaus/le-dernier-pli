#!/usr/bin/env python3
"""Génère les fonds des pièces souterraines de l'étape 1 (couchette, abri du sergent, cantine,
chapelle de sacs, vieille sape, sape de sortie) et deux calques : le rideau de la sape de sortie
(VerrouCendre) et rien d'autre.

Un seul plan fixe par lieu, découpé en tuiles de 2048 px au plus :
art/src/env/e1/env_e1_plan3_<lieu>_NN.svg. Repère local de chaque lieu
(scenes/etapes/etape_01/lieux/*.tscn) : sol à y 900, plafond de collision de 330 à 450,
passages de 160 x 300 (y 600 à 900).

Grammaire de la planche n° 4 : sous terre, la lumière est faite d'anneaux de hachure nets autour
des sources (bougie, braise, jour en haut d'un escalier), jamais de dégradé. Hors des anneaux :
hachure + contre-hachure ; dans l'anneau : hachure seule ; au cœur : le papier.
La vieille sape (zone sombre) a deux versions : « noir » (tout sous la contre-hachure, seule
une lueur au battant de cloche) et « lumiere » (lanterne : toute la galerie sous une simple hachure, sans anneau fixe,
la niche à la ration et le mot gravé « ...RELE »). Le code choisit selon le choix fait à e1_sape. Le voile gris de la maquette
(ZoneSombre/Visuel) est masqué par le code : l'obscurité est peinte ici.

Usage : python3 tools/gen_decors_e1_lieux.py
"""
from __future__ import annotations

import math

from gen_decors_e1_surface import DEFS, DST, ENCRE, FX, H, LAVIS, MINE, PAPIER, SOL, TUILE, rnd

ST = f'stroke="{ENCRE}" fill="none"'
# Coffrage des pièces : planches horizontales sur papier, joints décalés (pas de hachure de fond :
# l'ombre vient des anneaux de lumière).
DEFS = DEFS.replace("</defs>", (
    f'<pattern id="coffrage" width="300" height="40" patternUnits="userSpaceOnUse"><rect width="300" height="40" fill="{PAPIER}"/>'
    f'<path d="M0 0.5 H300 M0 20.5 H300 M110 0 V20 M240 20 V40" stroke="{ENCRE}" stroke-width="2"/>'
    f'<path d="M14 9 H80 M140 12 H210 M30 31 H120 M170 29 H220 M256 7 H290" stroke="{MINE}" stroke-width="1.3"/>'
    f'<circle cx="116" cy="10" r="1.8" fill="{ENCRE}"/><circle cx="246" cy="30" r="1.8" fill="{ENCRE}"/></pattern>'
    "</defs>"))
PLAFOND = 330   # haut du plafond de collision : le coffrage peint va de 330 à 450
BAS_PLAFOND = 450


# --- Pièce ----------------------------------------------------------------------------------

def piece(w: int, mur: str = "coffrage", seed: int = 1) -> str:
    """Terre au-dessus, plafond de rondins, mur coffré, étais, caillebotis."""
    r = rnd(seed)
    out = [f'<rect width="{w}" height="{H}" fill="url(#terre)"/>',
           f'<rect width="{w}" height="{PLAFOND}" fill="{LAVIS}"/>']
    # racines et cailloux dans la terre au-dessus du coffrage
    for _ in range(w // 160):
        x = r.randint(0, w)
        y = r.randint(40, PLAFOND - 40)
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="{r.randint(10, 26)}" ry="{r.randint(6, 14)}" fill="{MINE}" {ST} stroke-width="2"/>')
    for _ in range(w // 300):
        x = r.randint(0, w)
        out.append(f'<path d="M{x} {PLAFOND} Q{x + r.randint(-30, 30)} {PLAFOND - 80} {x + r.randint(-60, 60)} {PLAFOND - 170}" {ST} stroke-width="2.4"/>')
    # mur
    out.append(f'<rect y="{BAS_PLAFOND}" width="{w}" height="{SOL - BAS_PLAFOND}" fill="url(#{mur})" {ST} stroke-width="3"/>')
    # plafond : rondins vus de côté (deux rangs), puis la poutre maîtresse
    out.append(f'<rect y="{PLAFOND}" width="{w}" height="{BAS_PLAFOND - PLAFOND}" fill="url(#h2)" {ST} stroke-width="3"/>')
    for y in (PLAFOND + 6, PLAFOND + 44):
        out.append(f'<rect y="{y}" width="{w}" height="32" fill="url(#h1)" {ST} stroke-width="2.4"/>')
        x = r.randint(0, 120)
        while x < w:
            out.append(f'<path d="M{x} {y} V{y + 32}" {ST} stroke-width="2"/>')
            x += r.randint(140, 320)
    out.append(f'<rect y="{BAS_PLAFOND - 36}" width="{w}" height="36" fill="{PAPIER}" {ST} stroke-width="3"/>')
    out.append(f'<path d="M0 {BAS_PLAFOND - 22} H{w}" {ST} stroke-width="1.2" stroke-dasharray="30 18"/>')
    # étais
    x = 90
    while x < w:
        out.append(etai(x, r))
        x += r.randint(300, 380)
    # caillebotis et terre battue
    out.append(f'<rect y="{SOL}" width="{w}" height="40" fill="url(#caille)" {ST} stroke-width="3"/>')
    out.append(f'<rect y="{SOL + 40}" width="{w}" height="{H - SOL - 40}" fill="url(#terre)" {ST} stroke-width="3"/>')
    return "".join(out)


def etai(x: int, r, penche: float = 0.0) -> str:
    dx = penche * (SOL - BAS_PLAFOND)
    return (f'<path d="M{x - 11} {BAS_PLAFOND} L{x + 11} {BAS_PLAFOND} L{x + 11 + dx:.0f} {SOL} L{x - 11 + dx:.0f} {SOL} Z" fill="url(#h2)" {ST} stroke-width="2.6"/>'
            f'<path d="M{x - 40} {BAS_PLAFOND + 2} L{x} {BAS_PLAFOND + 40} L{x + 40} {BAS_PLAFOND + 2}" {ST} stroke-width="6"/>')


def lumiere(nom: str, w: int, sources: list[tuple[int, int, int]]) -> str:
    """Anneaux nets : (x, y, rayon du cœur). L'anneau va jusqu'à 1,8 fois le cœur."""
    trous_coeur = "".join(f'<circle cx="{x}" cy="{y}" r="{r0}" fill="#000"/>' for x, y, r0 in sources)
    trous_anneau = "".join(f'<circle cx="{x}" cy="{y}" r="{r0 * 1.8:.0f}" fill="#000"/>' for x, y, r0 in sources)
    cadre = f'maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{H}"'
    pleins = "".join(f'<circle cx="{x}" cy="{y}" r="{r0 * 1.8:.0f}" fill="#fff"/>' for x, y, r0 in sources)
    return (f'<mask id="i-{nom}" {cadre}>{pleins}</mask>'
            f'<mask id="c-{nom}" {cadre}><rect width="{w}" height="{H}" fill="#fff"/>{trous_coeur}</mask>'
            f'<mask id="a-{nom}" {cadre}><rect width="{w}" height="{H}" fill="#fff"/>{trous_anneau}</mask>'
            f'<g mask="url(#c-{nom})"><rect width="{w}" height="{H}" fill="url(#v1)" mask="url(#i-{nom})"/></g>'
            f'<rect width="{w}" height="{H}" fill="url(#v2)" mask="url(#a-{nom})"/>')


def escalier(cx: int, vers_droite: bool) -> str:
    """Escalier de rondins qui monte vers la tranchée (passage de 160 x 300, y 600 à 900)."""
    x0, x1 = cx - 80, cx + 80
    out = [f'<path d="M{x0} {SOL} L{x0} 640 Q{cx} 596 {x1} 640 L{x1} {SOL} Z" fill="{ENCRE}"/>']
    # le jour en haut, vu par l'ouverture
    hx = x1 - 50 if vers_droite else x0 + 50
    out.append(f'<path d="M{hx - 34} 652 Q{hx} 628 {hx + 34} 652 L{hx + 30} 700 L{hx - 30} 700 Z" fill="{PAPIER}"/>')
    for i, y in enumerate(range(SOL - 30, 700, -34)):
        d = i * 9
        a, b = (x0 + 10 + d, x1 - 10) if vers_droite else (x0 + 10, x1 - 10 - d)
        out.append(f'<path d="M{a} {y} L{b} {y}" stroke="{PAPIER}" stroke-width="5"/>')
        out.append(f'<path d="M{a} {y + 6} L{b} {y + 6}" stroke="{MINE}" stroke-width="2"/>')
    out.append(f'<path d="M{x0 - 10} 630 L{x0 - 10} {SOL} M{x1 + 10} 630 L{x1 + 10} {SOL}" {ST} stroke-width="16"/>')
    out.append(f'<path d="M{x0 - 24} 626 L{x1 + 24} 626" {ST} stroke-width="14"/>')
    return "".join(out)


def bougie(x: int, y: int, h: int = 30) -> str:
    """Bougie posée en y (pied), flamme en papier nu."""
    top = y - h
    return (f'<rect x="{x - 6}" y="{top}" width="12" height="{h}" fill="{PAPIER}" {ST} stroke-width="2"/>'
            f'<path d="M{x - 9} {top + 4} Q{x - 9} {top} {x - 4} {top + 2}" {ST} stroke-width="1.6"/>'
            f'<path d="M{x} {top - 2} Q{x - 6} {top - 14} {x} {top - 28} Q{x + 6} {top - 14} {x} {top - 2} Z" fill="{PAPIER}" {ST} stroke-width="1.6"/>')


def caisse(x0: int, x1: int, haut: int, mot: str = "") -> str:
    out = [f'<rect x="{x0}" y="{SOL - haut}" width="{x1 - x0}" height="{haut}" fill="url(#h1)" {ST} stroke-width="3"/>',
           f'<path d="M{x0} {SOL - haut} L{x1} {SOL} M{x0} {SOL - haut // 2} H{x1}" {ST} stroke-width="2"/>']
    if mot:
        out.append(f'<rect x="{(x0 + x1) // 2 - 34}" y="{SOL - haut + 10}" width="68" height="20" fill="{PAPIER}" {ST} stroke-width="1.6"/>')
    return "".join(out)


def table(x0: int, x1: int, haut: int = SOL - 120) -> str:
    return (f'<rect x="{x0}" y="{haut}" width="{x1 - x0}" height="16" fill="url(#h2)" {ST} stroke-width="3"/>'
            f'<path d="M{x0 + 14} {haut + 16} L{x0 + 20} {SOL} M{x1 - 14} {haut + 16} L{x1 - 20} {SOL} '
            f'M{x0 + 20} {SOL - 40} L{x1 - 20} {SOL - 40}" {ST} stroke-width="8"/>')


def clou_et_papier(x: int, y: int, w: int = 60, h: int = 80, lignes: int = 5) -> str:
    out = [f'<rect x="{x - w // 2}" y="{y}" width="{w}" height="{h}" fill="{PAPIER}" {ST} stroke-width="3.4"/>',
           f'<circle cx="{x}" cy="{y + 6}" r="3" fill="{ENCRE}"/>']
    for k in range(lignes):
        yy = y + 18 + k * (h - 26) // max(lignes, 1)
        out.append(f'<path d="M{x - w // 2 + 8} {yy} L{x + w // 2 - 8 - (k % 2) * 12} {yy}" {ST} stroke-width="1.4"/>')
    return "".join(out)


# --- Lieux ----------------------------------------------------------------------------------

def couchette() -> str:
    w = 1920
    out = [piece(w, seed=11)]
    # deux rangs de couchettes en bois et grillage, de 280 à 1420
    for x0 in (280, 680, 1080):
        x1 = x0 + 340
        for y in (560, 760):
            out.append(f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="70" fill="url(#h2)" {ST} stroke-width="2"/>')
            out.append(f'<path d="M{x0} {y + 70} H{x1}" {ST} stroke-width="10"/>')
            # paillasse et couverture roulée en papier
            out.append(f'<path d="M{x0 + 14} {y + 64} Q{x0 + 60} {y + 30} {x0 + 140} {y + 44} Q{x1 - 80} {y + 52} {x1 - 14} {y + 64} Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
            out.append(f'<ellipse cx="{x1 - 50}" cy="{y + 50}" rx="30" ry="16" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
        out.append(f'<path d="M{x0} {BAS_PLAFOND} V{SOL} M{x1} {BAS_PLAFOND} V{SOL}" {ST} stroke-width="14"/>')
    # la lettre (détail couchette_lettre, x 900) épinglée au montant
    out.append(clou_et_papier(900, 640, 54, 70, 4))
    # l'abécédaire (x 1250) gravé dans la planche : lettres grattées en papier
    out.append(f'<rect x="1160" y="660" width="180" height="70" fill="url(#h2)" {ST} stroke-width="3.4"/>')
    lettres = ["M1172 676 l8 22 l8 -22", "M1196 698 l6 -22 l6 22 M1199 690 h6", "M1218 676 v22 h10",
               "M1236 676 l10 22 M1246 676 l-10 22", "M1172 712 h12 M1178 712 v14", "M1196 712 v14 h10",
               "M1218 712 l6 14 l6 -14", "M1238 712 h10 l-10 14 h10"]
    for d in lettres:
        out.append(f'<path d="{d}" stroke="{PAPIER}" stroke-width="2.6" fill="none"/>')
    # gamelle et bougie sur une planchette clouée (la seule lumière de la pièce)
    out.append(f'<path d="M940 520 H1040" {ST} stroke-width="8"/>')
    out.append(bougie(990, 516, 26))
    # escalier de sortie vers le boyau (x 1700)
    out.append(escalier(1700, vers_droite=True))
    out.append(lumiere("couchette", w, [(990, 470, 150), (1700, 640, 130)]))
    return "".join(out)


def abri_sergent() -> str:
    w = 2880
    out = [piece(w, seed=12)]
    out.append(escalier(200, vers_droite=False))
    # la carte d'état-major (x 1000), traits de crayon, quatre punaises
    out.append(f'<rect x="900" y="560" width="200" height="140" fill="{PAPIER}" {ST} stroke-width="3.4"/>')
    out.append(f'<path d="M912 640 Q960 600 1010 630 T1088 610 M930 690 Q980 660 1040 676 T1090 660" {ST} stroke-width="2"/>')
    out.append(f'<path d="M940 580 L960 600 M960 580 L940 600 M1050 650 l14 14 M1064 650 l-14 14" {ST} stroke-width="2.4"/>')
    for px, py in ((906, 566), (1094, 566), (906, 694), (1094, 694)):
        out.append(f'<circle cx="{px}" cy="{py}" r="4" fill="{ENCRE}"/>')
    # lampe tempête pendue au plafond devant la carte
    out.append(f'<path d="M1000 {BAS_PLAFOND} V506" {ST} stroke-width="2.4"/>')
    out.append(f'<path d="M984 506 L1016 506 L1012 548 L988 548 Z" fill="{PAPIER}" {ST} stroke-width="3"/>')
    out.append(f'<path d="M1000 516 Q1006 527 1000 538 Q994 527 1000 516 Z" fill="{PAPIER}" {ST} stroke-width="1.4"/>')
    # la gamelle (x 1700) sur une caisse de munitions
    out.append(caisse(1630, 1770, 90, "mot"))
    out.append(f'<path d="M1668 810 Q1668 786 1700 786 Q1732 786 1732 810 Z" fill="{PAPIER}" {ST} stroke-width="2.6"/>')
    out.append(f'<path d="M1690 786 Q1700 770 1712 786" {ST} stroke-width="2"/>')
    # capote pendue à une patère
    out.append(f'<path d="M2080 560 l14 0 M2088 560 L2060 600 L2054 760 L2120 760 L2112 600 Z" fill="url(#h1)" {ST} stroke-width="2.6"/>')
    # au fond : la table de Lamarre, la bougie, le pli, la lampe, une ration (e1_ordre, x 2450)
    out.append(table(2330, 2650))
    out.append(f'<path d="M2290 {SOL} L2290 760 M2290 800 H2340 L2340 {SOL}" {ST} stroke-width="7"/>')
    out.append(bougie(2520, 780, 34))
    out.append(f'<rect x="2400" y="762" width="56" height="18" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
    out.append(f'<path d="M2400 762 L2428 774 L2456 762" {ST} stroke-width="1.6"/>')
    out.append(f'<path d="M2580 780 L2580 750 L2610 750 L2610 780 Z M2584 750 Q2595 736 2606 750" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
    out.append(f'<rect x="2350" y="768" width="40" height="12" fill="url(#h1)" {ST} stroke-width="2"/>')
    # étagère : bouteilles et boîtes
    out.append(f'<path d="M2380 600 H2640" {ST} stroke-width="8"/>')
    for bx in (2400, 2440, 2560):
        out.append(f'<path d="M{bx - 8} 596 V560 Q{bx} 548 {bx} 536 Q{bx} 548 {bx + 8} 560 V596 Z" fill="url(#h1)" {ST} stroke-width="2"/>')
    out.append(f'<rect x="2480" y="566" width="50" height="30" fill="{PAPIER}" {ST} stroke-width="2"/>')
    out.append(lumiere("abri", w, [(200, 640, 120), (1000, 560, 170), (2520, 720, 200)]))
    return "".join(out)


def cantine() -> str:
    w = 1920
    out = [piece(w, seed=13)]
    out.append(escalier(200, vers_droite=False))
    # le tableau des rations (x 700) : semaines barrées une à une
    out.append(f'<rect x="590" y="560" width="220" height="150" fill="url(#h2)" {ST} stroke-width="4"/>')
    out.append(f'<rect x="600" y="570" width="200" height="130" fill="{ENCRE}"/>')
    for rang in range(4):
        y = 586 + rang * 30
        for k in range(5):
            x = 612 + k * 9
            out.append(f'<path d="M{x} {y} v18" stroke="{PAPIER}" stroke-width="2"/>')
        out.append(f'<path d="M608 {y + 16} L656 {y + 2}" stroke="{PAPIER}" stroke-width="2"/>')
        out.append(f'<path d="M680 {y + 9} H{780 - rang * 18}" stroke="{PAPIER}" stroke-width="2"/>')
        if rang < 3:  # la semaine est barrée
            out.append(f'<path d="M602 {y + 9} H798" stroke="{PAPIER}" stroke-width="3"/>')
    # comptoir de planches, la marmite sur son brasero (e1_cantine, x 1300 : Mère Ravaude derrière)
    out.append(f'<rect x="1020" y="780" width="560" height="120" fill="url(#coffrage)" {ST} stroke-width="3"/>')
    out.append(f'<path d="M1010 780 H1590" {ST} stroke-width="10"/>')
    out.append(f'<path d="M1150 780 L1156 700 L1244 700 L1250 780 Z" fill="url(#h1)" {ST} stroke-width="3"/>')
    out.append(f'<path d="M1136 704 H1264 M1146 704 Q1146 690 1160 690 M1254 704 Q1254 690 1240 690" {ST} stroke-width="4"/>')
    # tuyau du fourneau qui perce le plafond
    out.append(f'<path d="M1180 690 V{PLAFOND} M1210 690 V{PLAFOND}" {ST} stroke-width="3"/>')
    out.append(f'<rect x="1180" y="{PLAFOND}" width="30" height="360" fill="url(#h1)"/>')
    # louche et gamelles empilées
    out.append(f'<path d="M1236 700 L1270 650 M1270 650 l10 -6" {ST} stroke-width="3"/>')
    for k in range(4):
        out.append(f'<ellipse cx="1460" cy="{772 - k * 10}" rx="34" ry="7" fill="{PAPIER}" {ST} stroke-width="2"/>')
    # banc et table des hommes
    out.append(table(380, 560, SOL - 100))
    out.append(lumiere("cantine", w, [(200, 640, 120), (1200, 720, 190), (700, 520, 110)]))
    return "".join(out)


def chapelle() -> str:
    w = 1920
    out = [piece(w, mur="sacs", seed=14)]
    out.append(escalier(200, vers_droite=False))
    # le mur des ex-voto (x 800) : plaques, cœurs de fer-blanc, lettres, une plaque de coureur
    r = rnd(141)
    for k in range(14):
        x = 680 + (k % 5) * 56 + r.randint(-8, 8)
        y = 560 + (k // 5) * 70 + r.randint(-8, 8)
        forme = k % 3
        if forme == 0:
            out.append(f'<rect x="{x - 16}" y="{y}" width="32" height="24" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
            out.append(f'<path d="M{x - 10} {y + 9} H{x + 10} M{x - 10} {y + 16} H{x + 6}" {ST} stroke-width="1.2"/>')
        elif forme == 1:
            out.append(f'<path d="M{x} {y + 26} L{x - 15} {y + 9} Q{x - 15} {y - 2} {x - 7} {y} Q{x} {y + 2} {x} {y + 8} Q{x} {y + 2} {x + 7} {y} Q{x + 15} {y - 2} {x + 15} {y + 9} Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
        else:
            out.append(f'<path d="M{x - 12} {y} H{x + 12} V{y + 30} L{x} {y + 22} L{x - 12} {y + 30} Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
        out.append(f'<circle cx="{x}" cy="{y - 4}" r="2.4" fill="{ENCRE}"/>')
    # cierges votifs au pied du mur
    for k, x in enumerate(range(700, 920, 36)):
        out.append(bougie(x, SOL, 22 + (k * 7) % 18))
    # l'autel de sacs (e1_cendre, x 1400) : nappe, bol de cendre, la cloche sans battant pendue
    out.append(f'<path d="M1440 {SOL} L1450 760 L1730 760 L1740 {SOL} Z" fill="url(#sacs)" {ST} stroke-width="3"/>')
    out.append(f'<path d="M1440 752 H1740 V790 L1700 780 L1660 794 L1620 780 L1580 794 L1540 780 L1500 794 L1460 780 L1440 790 Z" fill="{PAPIER}" {ST} stroke-width="2.6"/>')
    out.append(f'<path d="M1560 752 Q1560 728 1590 728 Q1620 728 1620 752 Z" fill="url(#h2)" {ST} stroke-width="2.6"/>')
    out.append(f'<path d="M1566 732 Q1590 718 1614 732" fill="{LAVIS}" {ST} stroke-width="1.6"/>')
    for x, h in ((1470, 40), (1500, 56), (1680, 50), (1712, 36)):
        out.append(bougie(x, 752, h))
    out.append(f'<path d="M1590 {BAS_PLAFOND} V560" {ST} stroke-width="2.4"/>')
    out.append(f'<path d="M1566 616 Q1568 566 1590 562 Q1612 566 1614 616 Z" fill="url(#h1)" {ST} stroke-width="3"/>')
    out.append(f'<ellipse cx="1590" cy="616" rx="24" ry="6" fill="{PAPIER}" {ST} stroke-width="2"/>')
    out.append(lumiere("chapelle", w, [(200, 640, 120), (800, 800, 150), (1590, 700, 210)]))
    return "".join(out)


def vieille_sape(allumee: bool) -> str:
    """Galerie abandonnée : étais penchés, poutre tombée, éboulis, racines.
    La zone sombre commence à x 560 (ZoneSombre du LD)."""
    w = 2880
    r = rnd(15)
    out = [f'<rect width="{w}" height="{H}" fill="url(#terre)"/>',
           f'<rect width="{w}" height="{PLAFOND}" fill="{LAVIS}"/>',
           f'<rect y="{BAS_PLAFOND}" width="{w}" height="{SOL - BAS_PLAFOND}" fill="url(#terre)" {ST} stroke-width="3"/>']
    # plafond affaissé, coffrage arraché par endroits
    bord = " L".join(f"{x} {BAS_PLAFOND - 30 + r.randint(-6, 18) + (24 if 1200 < x < 1700 else 0)}" for x in range(w, -1, -80))
    out.append(f'<path d="M0 {PLAFOND} H{w} V{BAS_PLAFOND - 20} L{bord} Z" fill="url(#h2)" {ST} stroke-width="3"/>')
    for x in range(40, w, 230):
        if r.random() < .7:
            out.append(f'<path d="M{x} {PLAFOND + 20} L{x + r.randint(-60, 60)} {BAS_PLAFOND + r.randint(0, 60)}" {ST} stroke-width="{r.choice((6, 9))}"/>')
    # planches du mur, les unes tenues, les autres tombées
    x = 0
    while x < w:
        lg = r.randint(120, 260)
        if r.random() < .55:
            y = r.randint(500, 760)
            ang = r.uniform(-8, 8)
            out.append(f'<rect x="{x}" y="{y}" width="{lg}" height="30" fill="url(#h1)" {ST} stroke-width="2.4" transform="rotate({ang:.1f} {x + lg // 2} {y + 15})"/>')
        x += lg + r.randint(20, 120)
    # étais rubanés de l'entrée (comme en surface), puis étais penchés
    for xe, pen in ((120, 0), (330, 0), (760, .06), (1100, -.08), (1460, .1), (1980, -.05), (2380, .07), (2760, -.04)):
        out.append(etai(xe, r, pen))
    for k in range(3):
        y = 560 + k * 70
        out.append(f'<path d="M100 {y} L350 {y + 30}" stroke="{PAPIER}" stroke-width="10"/>')
        out.append(f'<path d="M100 {y} L350 {y + 30}" {ST} stroke-width="2" stroke-dasharray="14 10"/>')
    out.append(escalier(200, vers_droite=False))
    # poutre maîtresse tombée en travers et éboulis
    out.append(f'<path d="M1240 520 L1290 500 L1700 820 L1660 846 Z" fill="url(#h2)" {ST} stroke-width="3"/>')
    out.append(f'<path d="M1180 {SOL} Q1300 760 1420 800 Q1520 720 1640 {SOL} Z" fill="url(#terre)" {ST} stroke-width="3"/>')
    for _ in range(18):
        ex, ey = r.randint(1200, 1640), r.randint(820, 896)
        out.append(f'<ellipse cx="{ex}" cy="{ey}" rx="{r.randint(8, 18)}" ry="{r.randint(5, 10)}" fill="{MINE}" {ST} stroke-width="2"/>')
    # racines qui pendent du plafond
    for xr in range(500, w, 170):
        if r.random() < .6:
            l = r.randint(60, 180)
            out.append(f'<path d="M{xr} {BAS_PLAFOND - 10} q{r.randint(-20, 20)} {l // 2} {r.randint(-30, 30)} {l}" {ST} stroke-width="2.2"/>')
    # la niche à la ration (x 1800) et le mot gravé dans la poutre (« ...RELE »)
    out.append(f'<path d="M1730 {SOL - 70} V720 Q1800 690 1870 720 V{SOL - 70} Z" fill="{ENCRE}" {ST} stroke-width="3"/>')
    if allumee:
        out.append(f'<rect x="1772" y="{SOL - 104}" width="56" height="34" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
        out.append(f'<path d="M1772 {SOL - 88} H1828 M1800 {SOL - 104} V{SOL - 70}" {ST} stroke-width="1.6"/>')
        out.append(f'<rect x="1660" y="590" width="280" height="64" fill="url(#h2)" {ST} stroke-width="3"/>')
        # « ...RELE » gratté au couteau, le début rongé
        mot = ("M1712 616 h3 M1722 616 h3 M1732 616 h3 "
               "M1748 632 v-20 h10 q6 0 6 6 q0 6 -6 6 h-10 m10 0 l8 8 "
               "M1778 612 h-12 v20 h12 m-12 -10 h9 "
               "M1786 612 v20 h12 "
               "M1818 612 h-12 v20 h12 m-12 -10 h9")
        out.append(f'<path d="{mot}" stroke="{PAPIER}" stroke-width="2.4" fill="none" transform="translate(1800 622) scale(1.7) translate(-1765 -622)"/>')
    # le petit battant de cloche, tombé au sol (x 2500) : seulement dans le noir (contenu exclusif)
    if not allumee:
        out.append(f'<path d="M2486 {SOL - 6} L2516 {SOL - 14}" {ST} stroke-width="4"/>')
        out.append(f'<circle cx="2522" cy="{SOL - 15}" r="7" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
    # sol défoncé
    out.append(f'<rect y="{SOL}" width="{w}" height="{H - SOL}" fill="url(#terre)" {ST} stroke-width="3"/>')
    for xc in range(0, w, 36):
        if xc < 1100 or r.random() < .4:
            out.append(f'<path d="M{xc + 4} {SOL + 2} V{SOL + 34}" {ST} stroke-width="2"/>')
    out.append(f'<path d="M0 {SOL + 36} H1100" {ST} stroke-width="2.4"/>')
    # l'obscurité, peinte (la ZoneSombre commence à x 560)
    cadre = f'maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{H}"'
    if allumee:
        # la lanterne : Tobie la porte avec lui, donc pas d'anneau fixe (ce serait un projecteur sur
        # la niche) ; toute la galerie sous une simple hachure, la niche et le mot en papier s'y lisent.
        out.append(f'<rect x="560" width="{w - 560}" height="{H}" fill="url(#v1)"/>')
    else:
        # le noir : tout sous la contre-hachure, puis l'encre ; seule lueur, le battant
        out.append(f'<mask id="vs-n" {cadre}><rect x="560" width="{w - 560}" height="{H}" fill="#fff"/>'
                   f'<circle cx="2516" cy="{SOL - 14}" r="60" fill="#000"/></mask>')
        out.append(f'<rect width="{w}" height="{H}" fill="url(#v2)" mask="url(#vs-n)"/>')
        out.append(f'<mask id="vs-n2" {cadre}><rect x="900" width="{w - 900}" height="{H}" fill="#fff"/>'
                   f'<circle cx="2516" cy="{SOL - 14}" r="130" fill="#000"/></mask>')
        out.append(f'<rect width="{w}" height="{H}" fill="{ENCRE}" opacity=".82" mask="url(#vs-n2)"/>')
    return "".join(out)


def sape_sortie() -> str:
    w = 2880
    out = [piece(w, seed=16)]
    out.append(escalier(200, vers_droite=False))
    # le sifflet (x 900) pendu par sa ficelle à un clou de l'étai
    out.append(f'<circle cx="900" cy="600" r="4" fill="{ENCRE}"/>')
    out.append(f'<path d="M900 600 Q890 640 900 680 Q912 700 904 716" {ST} stroke-width="1.6"/>')
    out.append(f'<path d="M892 716 h28 a8 8 0 0 1 0 16 h-28 Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
    # paquetage de Jacquot posé contre le mur, sa bougie (e1_adieu, x 1400)
    out.append(f'<path d="M1180 {SOL} Q1176 820 1210 812 L1268 812 Q1290 820 1286 {SOL} Z" fill="url(#h1)" {ST} stroke-width="2.6"/>')
    out.append(f'<path d="M1196 830 H1270" {ST} stroke-width="3"/>')
    out.append(caisse(1440, 1520, 60))
    out.append(bougie(1480, SOL - 60, 28))
    # au bout, la sortie vers l'échelle (x 2700) : le jour qui tombe par le haut
    out.append(escalier(2700, vers_droite=True))
    out.append(lumiere("sortie", w, [(200, 640, 120), (1480, 760, 170), (2700, 600, 190)]))
    return "".join(out)


def rideau() -> str:
    """VerrouCendre (40 x 450, centré) : une couverture mouillée tendue en travers de la sape,
    clouée à une traverse, pour le gaz. Elle tombe avec le verrou (après e1_adieu)."""
    w, h = 140, 460
    plis = " ".join(f"M{x} 22 Q{x + 6} 240 {x - 4} {h - 6}" for x in range(24, w - 10, 22))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{DEFS}'
            f'<path d="M8 18 L132 18 L136 {h - 4} Q100 {h - 18} 70 {h - 6} Q40 {h - 18} 4 {h - 4} Z" fill="url(#h1)" {ST} stroke-width="3"/>'
            f'<path d="{plis}" {ST} stroke-width="1.6"/>'
            f'<rect x="0" y="4" width="{w}" height="18" fill="url(#h2)" {ST} stroke-width="3"/>'
            f'<path d="M14 {h - 60} H126" {ST} stroke-width="2" stroke-dasharray="10 8"/></svg>\n')


def ecrire(nom: str, contenu: str, largeur: int) -> int:
    DST.mkdir(parents=True, exist_ok=True)
    n = math.ceil(largeur / TUILE)
    for i in range(n):
        x0 = i * TUILE
        w = min(TUILE, largeur - x0)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="{x0} 0 {w} {H}">'
               f'{DEFS}{contenu}</svg>\n')
        (DST / f"env_e1_plan3_{nom}_{i + 1:02d}.svg").write_text(svg, encoding="utf-8")
    return n


def main() -> None:
    total = ecrire("couchette", couchette(), 1920)
    total += ecrire("abri-sergent", abri_sergent(), 2880)
    total += ecrire("cantine", cantine(), 1920)
    total += ecrire("chapelle", chapelle(), 1920)
    total += ecrire("vieille-sape-noir", vieille_sape(False), 2880)
    total += ecrire("vieille-sape-lumiere", vieille_sape(True), 2880)
    total += ecrire("sape-sortie", sape_sortie(), 2880)
    FX.mkdir(parents=True, exist_ok=True)
    (FX / "fx_rideau-sape.svg").write_text(rideau(), encoding="utf-8")
    print(f"{total} tuiles + fx_rideau-sape dans art/src/")


if __name__ == "__main__":
    main()
