#!/usr/bin/env python3
"""Génère les fonds de l'étape 6, la Cathédrale enterrée (maquette du Level Designer, #144).

Un fond fixe par lieu, sans parallaxe, découpé en tuiles de 2048 px au plus,
art/src/env/e6/env_e6_plan3_<lieu>_NN.svg, posé en (0, 0) dans le repère du lieu
(scenes/decors/decor_e6.gd). Sol à y 900 ; sous terre, le plafond de collision va de 330 à 450.

L'écran de l'étape 6 est inversé (encre blanche sur nuit, papier_etapes.gd) : le vide et la
nuit sont laissés en papier nu, la pierre est un trait, la terre une hachure, et une lumière
est un aplat foncé ou une hachure serrée (claire à l'écran). Le vert-de-gris reste réservé au
bocal d'Éloi et à l'uniforme de Mathurin : les décors n'en ont pas.

  fissure     1920  la clairière, au bord : l'herbe, une croix qui penche, la fente ouverte
                    dans la terre (passage Descendre, x 1200)
  nef         5760  l'église couchée dans la terre comme un navire : piliers penchés fendus par
                    les racines, vitraux plaqués de terre (x 1500), racines (x 2700), bancs
                    renversés, la voûte qui penche ; la descente (x 730) ; au-delà de
                    l'éboulement (x 4230), le passage vers le village (x 5500)
  village     4800  le village enfoui, chaud : maisons creusées dans la terre, poutres, bocaux
                    de vers luisants pendus (x 1920), la tablée au centre (x 2420) avec un
                    couvert de plus (x 2700) ; la voûte tombée derrière Tobie (x 928) ; la porte
                    de la niche (x 3720), le chemin du seuil (x 4600)
  niche       1920  la niche-maison du veilleur : lampe basse, paillasse, étagère, la boîte à
                    couture et ses boutons (x 800) ; Mathurin s'assoit sur son tabouret (x 1300)
  seuil       1920  la porte de la Mère-Cloche, très haute, scellée et rescellée de cire noire
                    (x 900) ; Éloi s'arrête là (x 1400)

Garde-fous : aucun rouge, aucune cloche (la Mère-Cloche n'est qu'une porte), aucun nombre,
rien derrière la porte.

Usage : python3 tools/gen_decors_e6.py
"""
from __future__ import annotations

import math

from gen_decors_e1_surface import rnd
from gen_decors_e3_surface import DEFS, ENCRE, H, LAVIS, MINE, PAPIER, ROOT, SOL, ST, TUILE

DST = ROOT / "art" / "src" / "env" / "e6"
PLAFOND = 450


# --------------------------------------------------------------------------- briques
def terre_haut(w: int, seed: int, bas: float = PLAFOND) -> str:
    """La terre au-dessus de tout : une masse hachurée au bord bosselé, des radicelles qui
    pendent."""
    r = rnd(seed)
    pts = [f"0 {bas - 20}"]
    x = 0
    while x < w:
        x += r.uniform(60, 160)
        pts.append(f"{x:.0f} {bas - r.uniform(0, 50):.0f}")
    out = [f'<path d="M0 0 H{w} V{bas - 20} L{" L".join(reversed(pts))} Z" fill="url(#h1)" {ST} stroke-width="2.6"/>']
    for _ in range(w // 70):
        x0 = r.uniform(0, w)
        y0 = bas - r.uniform(10, 40)
        out.append(f'<path d="M{x0:.0f} {y0:.0f} q{r.uniform(-8, 8):.0f} {r.uniform(20, 40):.0f} {r.uniform(-6, 6):.0f} {r.uniform(40, 90):.0f}" '
                   f'fill="none" stroke="{ENCRE}" stroke-width="1.2"/>')
    return "".join(out)


def sol_terre(w: int, seed: int) -> str:
    """Le sol de terre battue, quelques cailloux."""
    r = rnd(seed)
    out = [f'<rect y="{SOL}" width="{w}" height="{H - SOL}" fill="url(#h1)" opacity=".7"/>',
           f'<path d="M0 {SOL} H{w}" {ST} stroke-width="3"/>']
    for _ in range(w // 80):
        x, y = r.uniform(0, w), r.uniform(SOL + 16, H - 10)
        out.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r.uniform(4, 10):.0f}" ry="{r.uniform(3, 6):.0f}" fill="{PAPIER}" {ST} stroke-width="1.4"/>')
    return "".join(out)


def racine(d: str, ep: float = 16) -> str:
    """Une racine grosse comme un bras : claire à l'écran (lavis), cernée."""
    return (f'<path d="{d}" fill="none" stroke="{ENCRE}" stroke-width="{ep + 4:.0f}" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{LAVIS}" stroke-width="{ep:.0f}" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{ENCRE}" stroke-width="1.2" stroke-dasharray="14 22"/>')


def pilier(x: float, penche: float, haut: float = 120, larg: float = 70, fendu: bool = False, seed: int = 0) -> str:
    """Un pilier de la nef, penché (degrés, autour de son pied), fûts de pierre, chapiteau ;
    fendu : une fissure qui l'ouvre de haut en bas."""
    r = rnd(seed or int(x))
    out = [f'<g transform="rotate({penche:.1f} {x:.0f} {SOL})">',
           f'<rect x="{x - larg / 2:.0f}" y="{haut:.0f}" width="{larg:.0f}" height="{SOL - haut:.0f}" fill="{PAPIER}" {ST} stroke-width="3"/>',
           f'<path d="M{x - larg / 6:.0f} {haut + 30:.0f} V{SOL - 10} M{x + larg / 6:.0f} {haut + 30:.0f} V{SOL - 10}" stroke="{ENCRE}" stroke-width="1.4"/>',
           f'<path d="M{x - larg / 2 - 16:.0f} {haut:.0f} H{x + larg / 2 + 16:.0f} L{x + larg / 2:.0f} {haut + 30:.0f} H{x - larg / 2:.0f} Z" fill="url(#h1)" {ST} stroke-width="2.6"/>',
           f'<path d="M{x - larg / 2 - 10:.0f} {SOL} V{SOL - 26} H{x + larg / 2 + 10:.0f} V{SOL}" fill="none" {ST} stroke-width="2.6"/>']
    for k in range(int((SOL - haut) // 90)):
        y = haut + 60 + k * 90 + r.uniform(-6, 6)
        out.append(f'<path d="M{x - larg / 2:.0f} {y:.0f} H{x + larg / 2:.0f}" stroke="{ENCRE}" stroke-width="1.2"/>')
    if fendu:
        pts = [f"{x + r.uniform(-6, 6):.0f} {y:.0f}" for y in range(int(haut), SOL, 40)]
        out.append(f'<path d="M{" L".join(pts)}" fill="none" stroke="{ENCRE}" stroke-width="5"/>')
    out.append('</g>')
    return "".join(out)


def voute_couchee(w: int, penche: float) -> str:
    """Les ogives de la nef, vues d'en bas et de travers : arcs brisés qui penchent avec
    l'église, entre la terre et le plafond de collision."""
    out = []
    for x in range(-200, w + 400, 480):
        out.append(f'<g transform="rotate({penche:.1f} {x} {PLAFOND})">'
                   f'<path d="M{x - 240} {PLAFOND + 40} Q{x - 230} {PLAFOND - 260} {x} {PLAFOND - 330} '
                   f'Q{x + 230} {PLAFOND - 260} {x + 240} {PLAFOND + 40}" fill="none" {ST} stroke-width="5"/>'
                   f'<path d="M{x - 200} {PLAFOND + 40} Q{x - 190} {PLAFOND - 220} {x} {PLAFOND - 286} '
                   f'Q{x + 190} {PLAFOND - 220} {x + 200} {PLAFOND + 40}" fill="none" stroke="{ENCRE}" stroke-width="1.6"/></g>')
    return "".join(out)


def vitrail(x: float, y: float, w: float = 140, h: float = 300) -> str:
    """Un vitrail en lancette, les plombs dessinés, la terre plaquée derrière chaque verre."""
    out = [f'<path d="M{x} {y + h} V{y + 70} Q{x} {y} {x + w / 2} {y - 20} Q{x + w} {y} {x + w} {y + 70} V{y + h} Z" '
           f'fill="url(#h2)" {ST} stroke-width="4"/>']
    for k in range(1, 4):
        out.append(f'<path d="M{x + k * w / 4:.0f} {y + 20} V{y + h}" stroke="{ENCRE}" stroke-width="2.4"/>')
    for yy in range(int(y + 60), int(y + h), 50):
        out.append(f'<path d="M{x} {yy} H{x + w}" stroke="{ENCRE}" stroke-width="2.4"/>')
    out.append(f'<circle cx="{x + w / 2}" cy="{y + 40}" r="{w / 6:.0f}" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
    return "".join(out)


def banc(x: float, angle: float) -> str:
    """Un banc d'église renversé."""
    return (f'<g transform="rotate({angle:.0f} {x} {SOL})">'
            f'<rect x="{x - 90}" y="{SOL - 50}" width="180" height="14" fill="url(#h1)" {ST} stroke-width="2.4"/>'
            f'<rect x="{x - 90}" y="{SOL - 110}" width="12" height="110" fill="url(#h1)" {ST} stroke-width="2.4"/>'
            f'<path d="M{x - 70} {SOL - 36} V{SOL} M{x + 76} {SOL - 36} V{SOL}" {ST} stroke-width="4"/></g>')


def bocal_lumiere(x: float, y: float, s: float = 1.0) -> str:
    """Un bocal de vers luisants pendu à sa ficelle : la lumière est claire à l'écran (lavis
    et hachure serrée), sans vert-de-gris (réservé au bocal d'Éloi)."""
    return (f'<path d="M{x} {y - 60 * s:.0f} V{y - 22 * s:.0f}" stroke="{ENCRE}" stroke-width="1.4"/>'
            f'<circle cx="{x}" cy="{y:.0f}" r="{78 * s:.0f}" fill="url(#v1)" opacity=".55"/>'
            f'<circle cx="{x}" cy="{y:.0f}" r="{40 * s:.0f}" fill="url(#v1)"/>'
            f'<path d="M{x - 11 * s:.0f} {y + 14 * s:.0f} Q{x - 13 * s:.0f} {y - 4 * s:.0f} {x - 9 * s:.0f} {y - 16 * s:.0f} H{x + 9 * s:.0f} '
            f'Q{x + 13 * s:.0f} {y - 4 * s:.0f} {x + 11 * s:.0f} {y + 14 * s:.0f} Z" fill="{LAVIS}" {ST} stroke-width="2"/>'
            f'<path d="M{x - 9 * s:.0f} {y - 16 * s:.0f} H{x + 9 * s:.0f} V{y - 22 * s:.0f} H{x - 9 * s:.0f} Z" fill="{PAPIER}" {ST} stroke-width="1.4"/>')


def maison(x: float, larg: float, haut: float, seed: int, porte: bool = True) -> str:
    """Une maison creusée dans la paroi : façade de terre lissée, poutres, une fenêtre éclairée
    (claire à l'écran), une porte basse."""
    r = rnd(seed)
    y0 = SOL - haut
    out = [f'<path d="M{x} {SOL} V{y0 + 30} Q{x + larg / 2} {y0 - 30} {x + larg} {y0 + 30} V{SOL} Z" fill="{PAPIER}" {ST} stroke-width="3"/>',
           f'<path d="M{x - 10} {y0 + 34} H{x + larg + 10}" {ST} stroke-width="7"/>']
    fx = x + r.uniform(30, larg - 110)
    out.append(f'<rect x="{fx:.0f}" y="{y0 + 70}" width="70" height="56" fill="url(#h2)" {ST} stroke-width="2.6"/>'
               f'<path d="M{fx + 35:.0f} {y0 + 70} V{y0 + 126} M{fx:.0f} {y0 + 98} H{fx + 70:.0f}" stroke="{ENCRE}" stroke-width="2"/>')
    if porte:
        px = x + larg - 100 if fx < x + larg / 2 else x + 30
        out.append(f'<path d="M{px:.0f} {SOL} V{SOL - 150} Q{px + 35:.0f} {SOL - 176} {px + 70:.0f} {SOL - 150} V{SOL} Z" fill="url(#h1)" {ST} stroke-width="2.6"/>')
    return "".join(out)


# --------------------------------------------------------------------------- lieux
def fissure() -> str:
    """La fin de la clairière : l'herbe, une dernière croix qui penche, la fente ouverte."""
    w = 1920
    r = rnd(6001)
    out = [f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>',
           f'<path d="M0 640 Q900 620 {w} 660" fill="none" stroke="{MINE}" stroke-width="2"/>']
    for x in (240, 520, 1600):
        h = r.uniform(70, 110)
        out.append(f'<path d="M{x} 646 V{646 - h:.0f} M{x - h * .24:.0f} {646 - h * .74:.0f} H{x + h * .24:.0f}" stroke="{MINE}" stroke-width="3"/>')
    out.append(f'<g transform="rotate(-9 1500 {SOL})"><rect x="1490" y="{SOL - 260}" width="16" height="260" fill="url(#h1)" {ST} stroke-width="2.4"/>'
               f'<rect x="1440" y="{SOL - 200}" width="116" height="16" fill="url(#h1)" {ST} stroke-width="2.4"/></g>')
    out.append(f'<rect y="{SOL}" width="{w}" height="{H - SOL}" fill="url(#h1)"/>')
    out.append(f'<path d="M0 {SOL} H1080 M1320 {SOL} H{w}" {ST} stroke-width="3"/>')
    # la fente : une bouche noire (papier nu) aux lèvres arrachées, des racines coupées
    out.append(f'<path d="M1080 {SOL} L1110 {SOL + 30} L1150 {SOL + 50} L1200 {SOL + 60} L1250 {SOL + 46} L1290 {SOL + 26} L1320 {SOL} '
               f'L1300 {SOL + 90} L1220 {SOL + 180} L1110 {SOL + 110} Z" fill="{PAPIER}" {ST} stroke-width="3"/>')
    out.append(racine(f"M1100 {SOL + 20} q20 40 10 80", 8) + racine(f"M1290 {SOL + 14} q-10 30 4 70", 7))
    for _ in range(160):
        x, y = r.uniform(0, w), r.uniform(SOL - 30, SOL + 2)
        if 1060 < x < 1340:
            continue
        out.append(f'<path d="M{x:.0f} {y:.0f} l-4 -14 M{x + 5:.0f} {y:.0f} l1 -18 M{x + 10:.0f} {y:.0f} l5 -12" stroke="{ENCRE}" stroke-width="1.4"/>')
    return "".join(out)


def nef() -> str:
    """L'église couchée dans la terre, qui penche de plus en plus vers l'éboulement."""
    w = 5760
    out = [f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>', voute_couchee(w, 7), terre_haut(w, 6101, 300)]
    # piliers penchés, de plus en plus vers le fond
    for k, x in enumerate(range(260, w, 560)):
        if abs(x - 730) < 120 or 4100 < x < 4360:
            continue
        out.append(pilier(x, 3 + k * .9, 150 + (k % 2) * 30, 70, fendu=abs(x - 2700) < 300 or k % 3 == 2))
    # la descente (x 730) : des marches de pierre cassées
    for k in range(5):
        out.append(f'<path d="M{620 + k * 50} {SOL - 70 + k * 14} h56 v{70 - k * 14} h-56 Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
    # les vitraux plaqués de terre (x 1500)
    out.append(vitrail(1360, 470, 120, 300) + vitrail(1540, 450, 140, 330))
    # les racines qui ont fendu les piliers (x 2700) et d'autres qui tombent de la voûte
    out.append(racine("M2500 300 Q2560 520 2660 640 Q2740 740 2720 900", 22)
               + racine("M2880 300 Q2820 480 2760 600 Q2700 700 2700 800", 14)
               + racine("M900 300 Q920 420 880 520", 10) + racine("M3500 300 Q3540 460 3480 580", 12)
               + racine("M5000 300 Q5060 500 5000 700 Q4960 800 5020 900", 16))
    # bancs renversés
    for x, a in ((1900, -12), (2200, 8), (3300, -20), (3560, 14), (4700, -6), (5200, 18)):
        out.append(banc(x, a))
    # l'éboulement (x 4230) : il n'est pas peint ici, c'est un verrou ; autour, des pierres tombées
    for x in (4060, 4120, 4360, 4420):
        out.append(f'<path d="M{x - 30} {SOL} L{x - 20} {SOL - 36} L{x + 14} {SOL - 44} L{x + 34} {SOL} Z" fill="url(#h1)" {ST} stroke-width="2.4"/>')
    # le passage vers le village (x 5500) : une brèche dans le mur du chœur
    out.append(f'<path d="M5420 {SOL} V640 L5460 600 L5520 610 L5580 640 V{SOL} Z" fill="{PAPIER}" {ST} stroke-width="3"/>'
               f'<path d="M5400 {SOL} V620 M5600 {SOL} V630" stroke="{ENCRE}" stroke-width="2"/>')
    out.append(sol_terre(w, 6102))
    return "".join(out)


def village() -> str:
    """Le village enfoui : chaud, éclairé de bocaux, maisons creusées, la tablée au centre."""
    w = 4800
    r = rnd(6201)
    out = [f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>', terre_haut(w, 6202, 330)]
    # les poutres de soutènement, d'un bout à l'autre
    out.append(f'<path d="M0 360 H{w}" {ST} stroke-width="16"/><path d="M0 360 H{w}" stroke="{PAPIER}" stroke-width="10"/>')
    for x in range(160, w, 420):
        out.append(f'<rect x="{x - 12}" y="360" width="24" height="{SOL - 360}" fill="url(#h1)" {ST} stroke-width="2.6"/>'
                   f'<path d="M{x - 12} 420 L{x - 70} 362 M{x + 12} 420 L{x + 70} 362" {ST} stroke-width="5"/>')
    # la voûte tombée derrière Tobie (x 928) : un mur de terre et de pierres jusqu'au plafond
    out.append(f'<path d="M820 {SOL} L860 600 L840 420 L900 340 L1000 360 L1010 500 L990 {SOL} Z" fill="url(#h2)" {ST} stroke-width="3"/>')
    for _ in range(14):
        x, y = r.uniform(840, 990), r.uniform(420, 880)
        out.append(f'<path d="M{x:.0f} {y:.0f} l20 -10 l18 8 l-6 18 l-26 4 Z" fill="{PAPIER}" {ST} stroke-width="2"/>')
    # les maisons creusées
    for x, larg, haut, s in ((1060, 300, 300, 1), (1400, 260, 340, 2), (3000, 280, 320, 3), (3320, 240, 300, 4), (4000, 300, 330, 5)):
        out.append(maison(x, larg, haut, 6210 + s))
    # la porte de la niche du veilleur (x 3720) : basse, une lampe à côté
    out.append(f'<path d="M3640 {SOL} V700 Q3720 650 3800 700 V{SOL} Z" fill="{PAPIER}" {ST} stroke-width="3"/>'
               f'<path d="M3656 {SOL} V708 Q3720 668 3784 708 V{SOL}" fill="none" {ST} stroke-width="1.6"/>')
    # le chemin du seuil (x 4600) : un tunnel qui descend encore
    out.append(f'<path d="M4500 {SOL} V640 Q4600 560 4700 640 V{SOL} Z" fill="{PAPIER}" {ST} stroke-width="3"/>'
               f'<path d="M4520 {SOL} L4560 700 M4680 {SOL} L4640 700" stroke="{ENCRE}" stroke-width="1.4"/>')
    # la tablée au centre (x 2420) : une longue table, des bancs, les couverts ; un de plus (x 2700)
    out.append(f'<rect x="2080" y="{SOL - 120}" width="720" height="18" fill="url(#h1)" {ST} stroke-width="3"/>'
               f'<path d="M2110 {SOL - 102} V{SOL} M2770 {SOL - 102} V{SOL} M2440 {SOL - 102} V{SOL}" {ST} stroke-width="6"/>'
               f'<rect x="2060" y="{SOL - 60}" width="760" height="12" fill="url(#h1)" {ST} stroke-width="2.4"/>')
    for x in range(2120, 2800, 80):
        out.append(f'<ellipse cx="{x}" cy="{SOL - 124}" rx="22" ry="6" fill="{PAPIER}" {ST} stroke-width="2"/>'
                   f'<path d="M{x + 28} {SOL - 136} V{SOL - 122}" stroke="{ENCRE}" stroke-width="2"/>')
    out.append(f'<rect x="2686" y="{SOL - 150}" width="14" height="28" fill="{PAPIER}" {ST} stroke-width="2"/>')
    # les bocaux de vers luisants pendus aux poutres : la lumière du village
    for x in (1240, 1560, 1760, 1920, 2080, 2240, 2420, 2600, 2780, 3160, 3460, 3860, 4300):
        out.append(bocal_lumiere(x, 440 + (x * 7) % 60, 1.0 if abs(x - 1920) > 200 else 1.2))
        # la flaque de lumière qu'il pose sur la terre battue
        out.append(f'<ellipse cx="{x}" cy="{SOL + 14}" rx="120" ry="16" fill="url(#v1)" opacity=".6"/>')
    out.append(sol_terre(w, 6203))
    return "".join(out)


def niche() -> str:
    """La niche-maison du veilleur : basse, chaude, une lampe, une paillasse, une étagère, la
    boîte à couture et ses boutons sur une caisse (x 800)."""
    w = 1920
    out = [f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>', terre_haut(w, 6301, 420)]
    out.append(f'<path d="M0 470 Q960 420 {w} 470" fill="none" {ST} stroke-width="3"/>')
    # la lampe basse au-dessus de Mathurin (x 1300) : une lumière claire à l'écran
    out.append(f'<path d="M1300 420 V520" stroke="{ENCRE}" stroke-width="1.6"/>'
               f'<circle cx="1300" cy="540" r="120" fill="url(#v1)" opacity=".7"/>'
               f'<path d="M1280 520 H1320 L1312 556 H1288 Z" fill="{LAVIS}" {ST} stroke-width="2"/>')
    # la paillasse et sa couverture (au fond, à droite)
    out.append(f'<path d="M1520 {SOL} V{SOL - 50} Q1680 {SOL - 70} 1840 {SOL - 50} V{SOL} Z" fill="url(#h1)" {ST} stroke-width="2.6"/>'
               f'<path d="M1540 {SOL - 52} Q1620 {SOL - 90} 1710 {SOL - 60}" fill="none" {ST} stroke-width="2"/>')
    # l'étagère creusée : des pots, un pain
    out.append(f'<path d="M540 600 H760 M540 680 H760" {ST} stroke-width="5"/>')
    for x in (570, 620, 690):
        out.append(f'<path d="M{x} 600 V570 Q{x + 14} 560 {x + 28} 570 V600 Z" fill="{PAPIER}" {ST} stroke-width="2"/>')
    out.append(f'<ellipse cx="720" cy="666" rx="30" ry="14" fill="url(#h1)" {ST} stroke-width="2"/>')
    # la caisse et la boîte à couture (x 800) : fil, aiguille, boutons
    out.append(f'<rect x="740" y="{SOL - 90}" width="130" height="90" fill="url(#h1)" {ST} stroke-width="2.6"/>'
               f'<rect x="760" y="{SOL - 114}" width="80" height="24" fill="{PAPIER}" {ST} stroke-width="2"/>'
               f'<path d="M790 {SOL - 114} q10 -20 24 -8 M830 {SOL - 120} l18 -22" fill="none" stroke="{ENCRE}" stroke-width="1.4"/>')
    for x, y in ((774, -100), (790, -98), (806, -102), (822, -99)):
        out.append(f'<circle cx="{x}" cy="{SOL + y}" r="3.4" fill="{PAPIER}" {ST} stroke-width="1.2"/>')
    # la porte basse vers le village (à gauche, entrée x 360)
    out.append(f'<path d="M280 {SOL} V720 Q360 670 440 720 V{SOL} Z" fill="{PAPIER}" {ST} stroke-width="3"/>')
    out.append(sol_terre(w, 6302))
    return "".join(out)


def seuil() -> str:
    """La porte de la Mère-Cloche : très haute, dans une voûte qui monte, couverte de couches de
    cire noire qui ont coulé les unes sur les autres. Rien de ce qu'il y a derrière."""
    w = 1920
    r = rnd(6401)
    out = [f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>', terre_haut(w, 6402, 160)]
    # la voûte qui monte, en pierre
    out.append(f'<path d="M420 {SOL} V420 Q900 20 1380 420 V{SOL}" fill="none" {ST} stroke-width="6"/>'
               f'<path d="M460 {SOL} V430 Q900 70 1340 430 V{SOL}" fill="none" stroke="{ENCRE}" stroke-width="2"/>')
    # la porte : noire à l'écran (papier), cernée, couverte de coulures de cire en couches
    out.append(f'<path d="M560 {SOL} V420 Q900 120 1240 420 V{SOL} Z" fill="{PAPIER}" {ST} stroke-width="4"/>')
    for couche in range(5):
        y0 = 300 + couche * 110
        pts = [f"{560 + couche * 6} {y0 + 40}"]
        x = 560 + couche * 6
        while x < 1240 - couche * 6:
            x += r.uniform(30, 60)
            pts.append(f"{min(x, 1240 - couche * 6):.0f} {y0 + r.uniform(30, 120):.0f}")
        out.append(f'<path d="M{" L".join(pts)}" fill="none" stroke="{ENCRE}" stroke-width="2"/>')
        for _ in range(8):
            x = r.uniform(600, 1200)
            y = y0 + r.uniform(40, 100)
            out.append(f'<path d="M{x:.0f} {y:.0f} q-3 {r.uniform(20, 50):.0f} 2 {r.uniform(40, 90):.0f}" fill="none" stroke="{ENCRE}" stroke-width="1.6"/>'
                       f'<circle cx="{x + 2:.0f}" cy="{y + r.uniform(50, 90):.0f}" r="3" fill="none" stroke="{ENCRE}" stroke-width="1.4"/>')
    out.append(f'<path d="M900 300 V{SOL}" stroke="{ENCRE}" stroke-width="3"/>')
    # la cire au pied de la porte, en flaques figées
    out.append(f'<path d="M540 {SOL} Q620 {SOL - 24} 720 {SOL - 10} Q820 {SOL - 30} 920 {SOL - 12} Q1060 {SOL - 28} 1260 {SOL} Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
    out.append(sol_terre(w, 6403))
    return "".join(out)


def ecrire(nom: str, contenu: str, largeur: int) -> int:
    DST.mkdir(parents=True, exist_ok=True)
    n = math.ceil(largeur / TUILE)
    for i in range(n):
        x0 = i * TUILE
        w = min(TUILE, largeur - x0)
        (DST / f"env_e6_plan3_{nom}_{i + 1:02d}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="{x0} 0 {w} {H}">{DEFS}{contenu}</svg>\n',
            encoding="utf-8")
    return n


LIEUX = {"fissure": (fissure, 1920), "nef": (nef, 5760), "village": (village, 4800),
         "niche": (niche, 1920), "seuil": (seuil, 1920)}


def main() -> None:
    total = sum(ecrire(nom, fn(), w) for nom, (fn, w) in LIEUX.items())
    print(f"{total} tuiles de l'étape 6 dans art/src/env/e6")


if __name__ == "__main__":
    main()
