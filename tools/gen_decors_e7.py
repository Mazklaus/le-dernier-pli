#!/usr/bin/env python3
"""Génère les fonds de l'étape 7, le Destinataire (maquette du Level Designer).

Un fond fixe par lieu, sans parallaxe, découpé en tuiles de 2048 px au plus,
art/src/env/e7/env_e7_plan3_<lieu>_NN.svg, posé en (0, 0) dans le repère du lieu
(scenes/decors/decor_e7.gd). Sol à y 900 ; dans les anneaux, le plafond de collision va de
330 à 450 : c'est le dessous de l'anneau du dessus.

L'écran de l'étape 7 est clair, presque blanc, sans accent (papier_etapes.gd). La descente
tourne autour de la plus grande cloche : derrière Tobie, le flanc de bronze, de plus en plus
large à chaque anneau ; devant et dessous, le vide, où pendent des cloches à toutes les
hauteurs, la bouche bouchée de cire noire coulée en larmes (les mêmes que dans e7_descente).

  galerie        1920  le haut du puits : la porte de la Mère-Cloche par où arrive Tobie (x 120),
                       une passerelle, et au bord (x 1500) la couronne de la grande cloche en
                       contrebas, où l'escalier commence
  anneau_cloches 2880  l'épaule de la grande cloche ; sur la rambarde, les battants décrochés,
                       posés pêle-mêle (x 900) ; e7_cloches (x 1440) ; l'escalier passe derrière
                       la cloche à droite (x 2650)
  anneau_lise    2880  le flanc, plus large ; le coin de Lise contre la rambarde (x 1440) : un
                       panier de laine, une lampe éteinte ; sa boîte à biscuits pleine de lettres
                       (x 1980) ; l'escalier passe derrière la cloche à gauche (x 230)
  anneau_porte   2880  la lèvre de la cloche, presque tout le fond ; la dernière porte, basse,
                       taillée dans le bronze (x 2560), et la cire : des sceaux noirs collés les
                       uns sur les autres qui débordent de la porte sur le bronze (x 1600 à 2700)
  mere_cloche    1920  sous la grande cloche : son intérieur fait le ciel ; la lèvre touche le
                       sol de chaque côté ; des coulures de cire noire au sol

Garde-fous : aucun rouge (le ruban du pli est le dernier rouge), aucune cloche ne bouge ni ne
sonne, aucun battant dans une cloche (les battants décrochés de la rambarde montrent l'absence),
la cire est noire, rien de ce qui pend dans la grande cloche n'est montré.

Usage : python3 tools/gen_decors_e7.py
"""
from __future__ import annotations

import math

from gen_cin_e7 import cloche
from gen_decors_e1_surface import rnd
from gen_decors_e3_surface import DEFS, ENCRE, H, LAVIS, MINE, PAPIER, ROOT, SOL, ST, TUILE

DST = ROOT / "art" / "src" / "env" / "e7"
PLAFOND = 450
LARGEUR_ANNEAU = 2880


# --------------------------------------------------------------------------- briques
def flanc(w: int, cx: float, r_haut: float, r_bas: float, seed: int, moulures=(560, 760)) -> str:
    """Le flanc de la grande cloche derrière l'anneau, de y 0 à SOL : un bronze clair aux bords
    qui tournent (hachures), quelques moulures, une patine pâle. r_haut, r_bas : demi-largeurs."""
    r = rnd(seed)
    g0, d0, g1, d1 = cx - r_haut, cx + r_haut, cx - r_bas, cx + r_bas
    out = [f'<path d="M{g0:.0f} -10 Q{g0 - (r_bas - r_haut) * .2:.0f} {SOL * .6:.0f} {g1:.0f} {SOL + 20} '
           f'H{d1:.0f} Q{d0 + (r_bas - r_haut) * .2:.0f} {SOL * .6:.0f} {d0:.0f} -10 Z" fill="{PAPIER}" {ST} stroke-width="7"/>']
    # l'arrondi : une bande hachurée le long de chaque bord
    for sens, x0, x1 in ((1, g0, g1), (-1, d0, d1)):
        e = 110 * sens
        out.append(f'<path d="M{x0:.0f} -10 Q{x0 - (x1 - x0) * -.2:.0f} {SOL * .6:.0f} {x1:.0f} {SOL + 20} '
                   f'L{x1 + e:.0f} {SOL + 20} Q{x0 + e * .9:.0f} {SOL * .6:.0f} {x0 + e:.0f} -10 Z" fill="url(#h1)" opacity=".55"/>')
    for y in moulures:
        t = y / SOL
        xg, xd = g0 + (g1 - g0) * t, d0 + (d1 - d0) * t
        out.append(f'<path d="M{xg:.0f} {y} Q{cx:.0f} {y + 26} {xd:.0f} {y}" fill="none" stroke="{ENCRE}" stroke-width="3"/>'
                   f'<path d="M{xg:.0f} {y + 16} Q{cx:.0f} {y + 42} {xd:.0f} {y + 16}" fill="none" stroke="{MINE}" stroke-width="2"/>')
    for _ in range(int(w / 260)):
        x = r.uniform(g1 + 160, d1 - 160)
        y = r.uniform(470, 860)
        out.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r.uniform(14, 34):.0f}" ry="{r.uniform(6, 14):.0f}" fill="{LAVIS}" opacity=".12"/>')
    return "".join(out)


def cloches_vide(w: int, seed: int, zones: list[tuple[float, float]], n: int = 6) -> str:
    """Des cloches pendues dans le vide, hors du flanc (zones : intervalles x libres), petites
    et pâles au loin, à toutes les hauteurs ; rien de régulier."""
    r = rnd(seed)
    out = []
    for k in range(n):
        a, b = zones[k % len(zones)]
        if b - a < 80:
            continue
        h = r.uniform(70, 170)
        x = r.uniform(a + h * .5, b - h * .5)
        y = r.uniform(-40, SOL - h * 1.3)
        out.append(f'<g opacity="{r.uniform(.45, .8):.2f}">{cloche(x, y, h, seed=seed * 10 + k, trait=1.8)}</g>')
    return "".join(out)


def dessous_anneau(w: int, seed: int) -> str:
    """Le dessous de l'anneau du dessus (le plafond de collision, 330 à 450) : le limon, les
    marches vues par en dessous, quelques barreaux de sa rambarde au-dessus."""
    r = rnd(seed)
    out = [f'<path d="M-10 352 H{w + 10} V444 H-10 Z" fill="{PAPIER}" {ST} stroke-width="4"/>',
           f'<path d="M-10 432 H{w + 10}" stroke="{ENCRE}" stroke-width="7"/>']
    x = r.uniform(0, 60)
    while x < w:
        out.append(f'<path d="M{x:.0f} 352 L{x + 26:.0f} 432" stroke="{MINE}" stroke-width="2"/>')
        x += r.uniform(58, 74)
    out.append(f'<path d="M-10 352 H{w + 10} V372 H-10 Z" fill="url(#h1)" opacity=".5"/>')
    x = r.uniform(0, 30)
    while x < w:
        out.append(f'<path d="M{x:.0f} 352 V250" stroke="{ENCRE}" stroke-width="2.4"/>')
        x += r.uniform(40, 56)
    out.append(f'<path d="M-10 250 H{w + 10}" stroke="{ENCRE}" stroke-width="5"/>')
    return "".join(out)


def passerelle(w: int, seed: int, x0: float = -10, x1: float | None = None) -> str:
    """La marche de l'escalier, en long : le chant des dalles sous les pieds (SOL à SOL + 40),
    le limon, et le vide dessous où pendent d'autres cloches."""
    r = rnd(seed)
    x1 = w + 10 if x1 is None else x1
    out = [f'<path d="M{x0:.0f} {SOL} H{x1:.0f} V{SOL + 40} H{x0:.0f} Z" fill="{PAPIER}" {ST} stroke-width="5"/>',
           f'<path d="M{x0:.0f} {SOL + 40} H{x1:.0f} V{SOL + 64} H{x0:.0f} Z" fill="url(#h1)" {ST} stroke-width="3"/>']
    x = x0 + r.uniform(30, 80)
    while x < x1:
        out.append(f'<path d="M{x:.0f} {SOL + 2} V{SOL + 40}" stroke="{ENCRE}" stroke-width="2.2"/>')
        x += r.uniform(80, 130)
    for _ in range(int((x1 - x0) / 140)):   # l'usure des dalles
        xx = r.uniform(x0, x1)
        out.append(f'<path d="M{xx:.0f} {SOL + r.uniform(12, 30):.0f} h{r.uniform(10, 30):.0f}" stroke="{MINE}" stroke-width="1.6"/>')
    return "".join(out)


def rambarde(x0: float, x1: float, seed: int, haut: float = 120) -> str:
    """La rambarde côté cloche : main courante, poteaux, barreaux fins."""
    r = rnd(seed)
    y = SOL - haut
    out = [f'<path d="M{x0:.0f} {y:.0f} H{x1:.0f}" stroke="{ENCRE}" stroke-width="7"/>',
           f'<path d="M{x0:.0f} {y + 10:.0f} H{x1:.0f}" stroke="{MINE}" stroke-width="2"/>']
    x = x0 + r.uniform(10, 40)
    while x < x1:
        out.append(f'<path d="M{x:.0f} {y:.0f} V{SOL}" stroke="{ENCRE}" stroke-width="2"/>')
        x += r.uniform(38, 52)
    x = x0 + 60
    while x < x1:
        out.append(f'<path d="M{x - 8:.0f} {y - 6:.0f} H{x + 8:.0f} V{SOL} H{x - 8:.0f} Z" fill="{PAPIER}" {ST} stroke-width="3"/>')
        x += r.uniform(380, 520)
    return "".join(out)


def tournant(x: float, sens: int) -> str:
    """Le bout de l'anneau, où l'escalier passe derrière la grande cloche : une ouverture sombre
    entre le bronze et les marches, où les marches descendent et se perdent (sens +1 : à droite)."""
    a, b = x - 150, x + 150
    out = [f'<path d="M{a:.0f} {SOL} V{SOL - 230} Q{x:.0f} {SOL - 330} {b:.0f} {SOL - 230} V{SOL} Z" fill="url(#h2)" {ST} stroke-width="5"/>']
    for k in range(5):
        xx = x - sens * 120 + sens * k * 50
        yy = SOL - 150 + k * 30
        out.append(f'<path d="M{xx:.0f} {yy:.0f} h{sens * 44:.0f} v9 h{-sens * 44:.0f} Z" fill="{PAPIER}" {ST} stroke-width="2" opacity="{1 - k * .18:.2f}"/>')
    return "".join(out)


def battants(x: float, seed: int) -> str:
    """Les battants décrochés, posés sur la main courante et contre les barreaux, pêle-mêle :
    des poires de bronze au bout d'une tige, cirées, luisantes."""
    r = rnd(seed)
    out = []
    for dx, a, l in [(-190, 72, 190), (-120, 84, 210), (-20, 66, 170), (40, 80, 230), (150, 70, 180), (230, 88, 150)]:
        bx = x + dx + r.uniform(-8, 8)
        rad = math.radians(a)
        tx, ty = bx + math.cos(rad) * l, SOL - 40 - math.sin(rad) * l
        out.append(f'<path d="M{bx:.0f} {SOL - 40} L{tx:.0f} {ty:.0f}" {ST} stroke-width="9"/>'
                   f'<circle cx="{tx + math.cos(rad) * 10:.0f}" cy="{ty - math.sin(rad) * 10:.0f}" r="10" fill="none" {ST} stroke-width="4"/>'
                   f'<path d="M{bx - 24:.0f} {SOL - 30} Q{bx - 26:.0f} {SOL - 70} {bx:.0f} {SOL - 74} Q{bx + 26:.0f} {SOL - 70} {bx + 24:.0f} {SOL - 30} '
                   f'Q{bx + 20:.0f} {SOL - 2} {bx:.0f} {SOL - 2} Q{bx - 20:.0f} {SOL - 2} {bx - 24:.0f} {SOL - 30} Z" fill="url(#h1)" {ST} stroke-width="3"/>'
                   f'<path d="M{bx - 10:.0f} {SOL - 58} q-4 14 0 30" fill="none" stroke="{PAPIER}" stroke-width="4"/>')
    return "".join(out)


def coin_lise(x: float) -> str:
    """Le coin de Lise contre la rambarde : une lampe éteinte au sol, un panier de laine."""
    return (f'<path d="M{x + 150} {SOL} v-46 q20 -26 40 0 v46 Z" fill="{PAPIER}" {ST} stroke-width="3"/>'
            f'<path d="M{x + 160} {SOL - 46} h20 M{x + 170} {SOL - 70} v-14" stroke="{ENCRE}" stroke-width="2.4"/>'
            f'<path d="M{x - 330} {SOL} q-6 -40 10 -50 h86 q16 10 10 50 Z" fill="url(#v1)" {ST} stroke-width="3"/>'
            f'<circle cx="{x - 296}" cy="{SOL - 54}" r="16" fill="url(#h1)" {ST} stroke-width="2.4"/>'
            f'<path d="M{x - 280} {SOL - 60} q30 -40 50 -20" fill="none" stroke="{ENCRE}" stroke-width="1.6"/>')


def boite_lettres(x: float) -> str:
    """La boîte à biscuits en fer, ouverte, pleine de lettres serrées debout, toutes pareilles."""
    out = [f'<path d="M{x - 70} {SOL} V{SOL - 60} H{x + 70} V{SOL} Z" fill="{PAPIER}" {ST} stroke-width="4"/>',
           f'<path d="M{x - 70} {SOL - 60} L{x - 96} {SOL - 120} H{x + 50} L{x + 70} {SOL - 60}" fill="{PAPIER}" {ST} stroke-width="3"/>',
           f'<ellipse cx="{x}" cy="{SOL - 30}" rx="30" ry="14" fill="none" stroke="{MINE}" stroke-width="2"/>']
    r = rnd(int(x))
    xx = x - 62
    while xx < x + 58:
        h = r.uniform(14, 24)
        out.append(f'<path d="M{xx:.0f} {SOL - 60} v{-h:.0f} h{r.uniform(9, 13):.0f} v{h:.0f}" fill="{PAPIER}" {ST} stroke-width="1.6"/>')
        xx += r.uniform(6, 10)
    return "".join(out)


def larme_cire(x: float, y: float, e: float, gl: float) -> str:
    """Une coulure de cire figée qui part de (x, y), large de 2e, longue de gl."""
    return (f'<path d="M{x - e:.0f} {y:.0f} Q{x - e * .5:.0f} {y + gl * .6:.0f} {x - e * 1.2:.0f} {y + gl:.0f} '
            f'Q{x:.0f} {y + gl + e * 2.4:.0f} {x + e * 1.2:.0f} {y + gl:.0f} Q{x + e * .5:.0f} {y + gl * .6:.0f} {x + e:.0f} {y:.0f} Z" fill="{ENCRE}"/>')


def sceau(x: float, y: float, e: float, r) -> str:
    """Un sceau de cire noire : un disque au bord écrasé, irrégulier, cerné d'un fil de mine qui
    le détache de ceux qu'il recouvre ; un bourrelet le long du bord ; au centre, l'empreinte du
    même cachet que le pli de Tobie (un anneau et son point)."""
    pts = []
    for k in range(9):
        a = k / 9 * 2 * math.pi + r.uniform(-.2, .2)
        d = e * r.uniform(.88, 1.12)
        pts.append((x + math.cos(a) * d, y + math.sin(a) * d * .92))
    d = "M" + " ".join(f"{(pts[k][0] + pts[k - 1][0]) / 2:.0f} {(pts[k][1] + pts[k - 1][1]) / 2:.0f} Q{pts[k][0]:.0f} {pts[k][1]:.0f}" for k in range(9))
    d = d.replace("M", "M", 1)
    debut = d.split(" Q")[0]
    d += " " + debut[1:] + " Z"
    return (f'<path d="{d}" fill="{ENCRE}" stroke="{MINE}" stroke-width="2"/>'
            f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{e * .78:.0f}" ry="{e * .72:.0f}" fill="none" stroke="{LAVIS}" stroke-width="2"/>'
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{e * .42:.0f}" fill="none" stroke="{MINE}" stroke-width="{max(1.6, e * .09):.1f}"/>'
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{e * .1:.0f}" fill="{MINE}"/>')


def sceaux(x0: float, x1: float, y0: float, y1: float, seed: int, n: int) -> str:
    """Des sceaux de cire noire collés les uns sur les autres, en couches : plus on approche de
    x1 (la porte), plus ils sont serrés, fondus dans une nappe de cire qui a coulé ; jamais
    alignés, jamais comptables. Les plus anciens d'abord, les plus récents dessus."""
    r = rnd(seed)
    out = []
    # la nappe : la cire des couches anciennes, fondue, en grosses galettes sans empreinte qui
    # se chevauchent, de plus en plus serrées vers la porte ; quelques coulures dessous
    for _ in range(n // 2):
        t = r.random() ** .35
        x = x0 + (x1 - x0) * (.3 + .7 * t)
        marge = (y1 - y0) * (.45 - .4 * t) * .6
        y = r.uniform(y0 + marge, y1 - marge)
        e = r.uniform(26, 50)
        pts = []
        for k in range(8):
            a = k / 8 * 2 * math.pi + r.uniform(-.25, .25)
            pts.append((x + math.cos(a) * e * r.uniform(.8, 1.2), y + math.sin(a) * e * r.uniform(.6, 1.0)))
        d = " ".join(f"Q{pts[k][0]:.0f} {pts[k][1]:.0f} {(pts[k][0] + pts[(k + 1) % 8][0]) / 2:.0f} {(pts[k][1] + pts[(k + 1) % 8][1]) / 2:.0f}" for k in range(8))
        out.append(f'<path d="M{(pts[7][0] + pts[0][0]) / 2:.0f} {(pts[7][1] + pts[0][1]) / 2:.0f} {d} Z" fill="{ENCRE}"/>')
        if r.random() < .3:
            out.append(larme_cire(x + r.uniform(-e * .5, e * .5), y + e * .7, r.uniform(4, 7), r.uniform(20, 70)))
    # les sceaux, sur plusieurs couches
    for _ in range(n):
        t = r.random() ** .5
        x = x0 + (x1 - x0) * t
        marge = (y1 - y0) * (.45 - .4 * t) * .5
        y = r.uniform(y0 + marge, y1 - marge)
        e = r.uniform(13, 24) * (1.1 - .2 * t)
        out.append(sceau(x, y, e, r))
        if r.random() < .15:
            out.append(larme_cire(x + r.uniform(-e * .4, e * .4), y + e * .85, e * .2, r.uniform(16, 50)))
    return "".join(out)


# --------------------------------------------------------------------------- lieux
def galerie() -> str:
    w = 1920
    out = [f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>',
           # la poutre du haut du puits, d'où pendent les cloches
           f'<path d="M-10 60 H{w + 10} V108 H-10 Z" fill="url(#planches)" {ST} stroke-width="4"/>']
    out.append(cloches_vide(w, 71, [(700, 1100), (1150, 1900), (300, 700)], 7))
    # en contrebas, la couronne de la grande cloche et le début de l'escalier
    out.append(cloche(1790, 720, 1700, seed=9, trait=6, cire=False))
    # la passerelle et la rambarde jusqu'au bord ; au bout, l'escalier qui plonge devant la cloche
    out.append(passerelle(w, 72))
    out.append(rambarde(-10, 1380, 73, 110))
    for k in range(4):
        xx = 1500 + k * 70
        out.append(f'<path d="M{xx} {SOL + 70 + k * 26} h62 v10 h-62 Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
    # la porte de la Mère-Cloche, vue de ce côté : très haute, la cire rompue à hauteur de main
    out.append(f'<path d="M30 {SOL} V240 Q130 140 230 240 V{SOL} Z" fill="url(#vantail)" {ST} stroke-width="6"/>'
               f'<path d="M12 {SOL} V226 Q130 104 248 226 V{SOL}" fill="none" {ST} stroke-width="5"/>')
    out.append(sceaux(50, 210, 560, 680, 74, 12))
    return "".join(out)


def anneau_cloches() -> str:
    w = LARGEUR_ANNEAU
    out = [f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>',
           cloches_vide(w, 81, [(0, 330), (2550, w)], 5),
           flanc(w, 1440, 1020, 1160, 82),
           dessous_anneau(w, 83), rambarde(-10, w + 10, 84),
           battants(900, 85), tournant(2650, 1), passerelle(w, 86),
           cloches_vide(w, 87, [(100, 900), (1000, 2000), (2100, 2800)], 4)]
    return "".join(out)


def anneau_lise() -> str:
    w = LARGEUR_ANNEAU
    out = [f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>',
           cloches_vide(w, 91, [(0, 180), (2700, w)], 3),
           flanc(w, 1440, 1220, 1340, 92, moulures=(600,)),
           dessous_anneau(w, 93), rambarde(-10, w + 10, 94),
           coin_lise(1440), boite_lettres(1980), tournant(230, -1), passerelle(w, 96)]
    return "".join(out)


def anneau_porte() -> str:
    w = LARGEUR_ANNEAU
    out = [f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>',
           flanc(w, 1440, 1420, 1560, 101, moulures=(520, 700, 730)),
           dessous_anneau(w, 102), rambarde(-10, 1500, 103)]
    # la dernière porte, basse, taillée dans le bronze de la lèvre
    out.append(f'<path d="M2440 {SOL} V600 Q2560 520 2680 600 V{SOL} Z" fill="url(#vantail)" {ST} stroke-width="6"/>'
               f'<path d="M2420 {SOL} V590 Q2560 494 2700 590 V{SOL}" fill="none" {ST} stroke-width="4"/>')
    out.append(sceaux(1580, 2420, 540, 860, 104, 52))
    out.append(sceaux(2460, 2660, 600, 870, 105, 34))
    out.append(passerelle(w, 106))
    return "".join(out)


def mere_cloche() -> str:
    w = 1920
    out = [f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>',
           # l'intérieur de la grande cloche fait le ciel : tout le haut est du bronze dans
           # l'ombre ; des anneaux plus clairs donnent la profondeur ; la lèvre retombe jusqu'au
           # sol de chaque côté
           # (un aplat de lavis : une hachure sur tout l'écran pèserait 2,8 Mo)
           f'<rect width="{w}" height="{SOL}" fill="{MINE}"/>']
    # une gravure en anneaux qui suivent la voûte, serrés en haut, de plus en plus lâches
    by, pas = 40.0, 9.0
    while by < 470:
        bx = -260 + by * .9
        out.append(f'<path d="M{bx:.0f} {SOL} Q{bx + 80:.0f} {by + 260:.0f} {bx + 420:.0f} {by + 80:.0f} Q960 {by - 80:.0f} {w - bx - 420:.0f} {by + 80:.0f} '
                   f'Q{w - bx - 80:.0f} {by + 260:.0f} {w - bx:.0f} {SOL}" fill="none" stroke="{ENCRE}" stroke-width="2"/>')
        by += pas
        pas *= 1.16
    for k, (bx, by) in enumerate([(-60, 120), (120, 260), (300, 390)]):
        out.append(f'<path d="M{bx} {SOL} Q{bx + 80} {by + 260} {bx + 420} {by + 80} Q960 {by - 80} {w - bx - 420} {by + 80} '
                   f'Q{w - bx - 80} {by + 260} {w - bx} {SOL}" fill="none" stroke="{PAPIER}" stroke-width="{6 - k * 2}"/>')
    out.append(f'<path d="M0 0 H{w} V90 Q960 10 0 90 Z" fill="{ENCRE}"/>')
    out += [f'<path d="M-20 {SOL} L80 {SOL} Q40 640 -20 380 Z" fill="{PAPIER}" {ST} stroke-width="8"/>',
            f'<path d="M{w + 20} {SOL} L{w - 80} {SOL} Q{w - 40} 640 {w + 20} 380 Z" fill="{PAPIER}" {ST} stroke-width="8"/>',
            # au plus haut, une corde qui monte dans le noir et se perd
            f'<path d="M960 -20 V140" stroke="{ENCRE}" stroke-width="4"/>',
            f'<path d="M-10 {SOL} H{w + 10} V{H} H-10 Z" fill="{PAPIER}" {ST} stroke-width="5"/>']
    r = rnd(110)
    for y in (SOL + 50, SOL + 115):   # quelques joints de dalles, irréguliers
        x = r.uniform(-40, 80)
        out.append(f'<path d="M-10 {y} H{w + 10}" stroke="{MINE}" stroke-width="2"/>')
        while x < w:
            out.append(f'<path d="M{x:.0f} {y - (50 if y < SOL + 100 else 65)} V{y}" stroke="{MINE}" stroke-width="2"/>')
            x += r.uniform(160, 300)
    r = rnd(111)
    for _ in range(12):   # la cire tombée au sol, en flaques figées
        x = r.uniform(120, 1800)
        e = r.uniform(16, 50)
        out.append(f'<ellipse cx="{x:.0f}" cy="{SOL + r.uniform(30, 160):.0f}" rx="{e:.0f}" ry="{e * .3:.0f}" fill="{ENCRE}"/>')
    return "".join(out)


def ecrire(nom: str, contenu: str, largeur: int) -> int:
    DST.mkdir(parents=True, exist_ok=True)
    n = math.ceil(largeur / TUILE)
    for i in range(n):
        x0 = i * TUILE
        w = min(TUILE, largeur - x0)
        (DST / f"env_e7_plan3_{nom}_{i + 1:02d}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="{x0} 0 {w} {H}">{DEFS}{contenu}</svg>\n',
            encoding="utf-8")
    return n


LIEUX = {"galerie": (galerie, 1920), "anneau-cloches": (anneau_cloches, LARGEUR_ANNEAU),
         "anneau-lise": (anneau_lise, LARGEUR_ANNEAU), "anneau-porte": (anneau_porte, LARGEUR_ANNEAU),
         "mere-cloche": (mere_cloche, 1920)}


def main() -> None:
    total = sum(ecrire(nom, fn(), w) for nom, (fn, w) in LIEUX.items())
    print(f"{total} tuiles de l'étape 7 dans art/src/env/e7")


if __name__ == "__main__":
    main()
