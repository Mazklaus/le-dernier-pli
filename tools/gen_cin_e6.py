#!/usr/bin/env python3
"""Génère la cinématique e6_chute_fissure : dans la clairière, la terre se fend sous les pieds de
Tobie, il tombe ; dessous, il glisse et roule dans une coulée de terre et de racines jusqu'à la
pierre taillée de la cathédrale enterrée (e6_nef, première réplique).

L'écran de l'étape 6 est inversé (encre blanche sur nuit) : le vide est laissé en papier (la nuit
à l'écran), la lumière qui tombe de la fente est en hachures serrées (claire à l'écran).

  Plan A, la clairière, Tobie de près :
  cin_chute_01  le fond 1920 x 1080 : l'herbe de la clairière, les dernières croix au loin,
                Tobie debout (image 0) ;
  cin_chute_02  6 images de 600 x 560 en (660, 300), grille 3 x 2 :
                0 debout, une fêlure sous ses bottes ; 1 la fente s'ouvre, mottes qui sautent,
                bras écartés ; 2 la terre s'ouvre, il bascule, bras levés ; 3 il est à moitié
                dans le trou ; 4 seules ses mains dépassent ; 5 le trou, des mottes qui
                retombent. À 10 i/s, avec une tenue sur 0 (environ 0,6 s).
  Plan B, sous la terre :
  cin_chute_03  le fond 1920 x 1080 : la fente en haut à gauche et sa lumière, la coulée de
                terre et de racines en diagonale, la pierre taillée en bas à droite (un
                chapiteau couché, des feuilles sculptées) ;
  cin_chute_04  7 images de 240 x 240 sur fond transparent, en ligne : la chute lourde.
                0 il glisse sur le dos le long des racines ; 1 une seule culbute ; 2 l'impact,
                étalé sur le chapiteau ; 3 immobile, la terre retombe sur lui ; 4 immobile,
                couvert de terre ; 5 il se soulève lentement ; 6 à quatre pattes.
                À poser par son centre sur le chemin CHEMIN ci-dessous (instant, image, centre en
                px du plan) : glissade 1,6 s, culbute, impact à 2,0 s, immobilité totale de
                2,0 à 3,6 s (dont 0,7 s sans rien, puis la terre), relevé lent, tenue jusqu'à 4,8 s.

Aucun rouge (la silhouette de Tobie est trop petite pour le ruban, comme à l'étape 5). Aucune
cloche.

Usage : python3 tools/gen_cin_e6.py
"""
from __future__ import annotations

import math

from gen_cin_e1 import DST, H, W, bande, svg
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER, rnd

STP = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
ZONE_A = (660, 300, 600, 560)
SOL_A = 780                    # le sol de la clairière dans le plan A
PIEDS_A = 960
# Chemin de Tobie dans le plan B : (instant en s depuis le début du plan, image, centre x, y)
CHEMIN = [(0.0, 0, 330, 190), (0.2, 0, 450, 268), (0.4, 0, 570, 338), (0.6, 0, 690, 408),
          (0.8, 0, 810, 476), (1.0, 0, 930, 540), (1.2, 0, 1050, 604), (1.4, 0, 1160, 662),
          (1.6, 0, 1254, 708),
          (1.8, 1, 1350, 730),                       # une seule culbute
          (2.0, 2, 1452, 800),                       # l'impact sur le chapiteau
          (2.7, 3, 1452, 800),                       # immobile ; la terre retombe sur lui
          (3.1, 4, 1452, 800),                       # immobile, couvert de terre
          (3.6, 5, 1480, 790),                       # il se soulève lentement
          (4.2, 6, 1500, 780)]                       # à quatre pattes ; tenue jusqu'à 4,8 s


# ----------------------------------------------------------------------------- Tobie
def tobie_debout(x: float, pied: float, bras: str = "bas", s: float = 1.0) -> str:
    """Tobie debout, de trois quarts vers la gauche, 360 px de haut à s = 1 : la capuche de
    toile pointée vers l'avant, la capote, la lanterne à la hanche avant, la sacoche derrière,
    le pli à la poitrine. bras : bas, ecartes, leves."""
    o = []
    def p(d: str, fill: str, w: float = 2.6) -> None:
        o.append(f'<path d="{d}" fill="{fill}" {STP} stroke-width="{w}"/>')
    # bottes et jambes
    p("M-36 -20 L-38 0 L-6 0 L-8 -20 Z M8 -20 L8 0 L40 0 L36 -20 Z", ENCRE, 2)
    p("M-34 -92 L-36 -20 L-8 -20 L-2 -92 Z M2 -92 L8 -20 L36 -20 L32 -92 Z", "url(#h2)", 2.2)
    # la sacoche, derrière, à la hanche droite
    p("M34 -170 L66 -166 L64 -122 L36 -124 Z", "url(#h1)", 2.2)
    # la capote, du col aux genoux
    p("M-38 -258 Q0 -272 40 -258 Q54 -180 60 -92 L-60 -92 Q-52 -180 -38 -258 Z", "url(#h2)", 2.8)
    p("M0 -262 V-96", "none", 1.6)
    p("M-56 -150 Q0 -140 58 -150", "none", 2.4)
    # le pli à la poitrine, cire noire
    p("M-30 -230 L-4 -234 L-2 -204 L-28 -200 Z", PAPIER, 2.2)
    o.append(f'<circle cx="-15" cy="-217" r="6" fill="{ENCRE}"/>')
    # la lanterne à la hanche avant
    p("M-62 -148 H-40 V-112 H-62 Z", PAPIER, 2.2)
    p("M-62 -138 H-40 M-51 -148 V-112 M-58 -156 Q-51 -164 -44 -156", "none", 1.6)
    # les bras
    epg, epd = (-34, -248), (36, -248)
    poses = {"bas": ((-50, -190, -54, -136), (52, -190, 50, -140)),
             "ecartes": ((-90, -240, -138, -220), (92, -236, 136, -214)),
             "leves": ((-66, -300, -60, -360), (62, -304, 70, -362)),
             # perte d'équilibre : les deux bras battent l'air, de travers, haut et bas
             "battent": ((-100, -290, -150, -330), (96, -270, 150, -250))}
    for (ex, ey), (cx, cy, mx, my) in zip((epg, epd), poses[bras]):
        p(f"M{ex} {ey} Q{cx - 6} {cy} {mx} {my} L{mx + 14} {my + 4} Q{cx + 10} {cy + 4} {ex + 14} {ey + 6} Z", "url(#h2)", 2.4)
        o.append(f'<circle cx="{mx + 7}" cy="{my + 2}" r="10" fill="{PAPIER}" {STP} stroke-width="2"/>')
    # la tête dans la capuche de toile huilée, pointe vers l'avant
    p("M-30 -262 Q-62 -300 -74 -344 Q-30 -352 6 -338 Q34 -322 30 -262 Z", "url(#h1)", 2.6)
    o.append(f'<ellipse cx="-22" cy="-298" rx="20" ry="25" fill="{PAPIER}" {STP} stroke-width="2.2"/>')
    o.append(f'<path d="M-36 -302 L-28 -302 M-18 -302 L-10 -302 M-26 -296 L-30 -286 L-25 -285 M-32 -278 Q-25 -276 -18 -278" fill="none" {STP} stroke-width="1.8"/>')
    o.append(f'<path d="M-34 -314 Q-26 -318 -18 -313" fill="none" stroke="{LAVIS}" stroke-width="4" stroke-linecap="round"/>')
    return f'<g transform="translate({x:.1f} {pied:.1f}) scale({s})">{"".join(o)}</g>'


def tobie_glisse() -> str:
    """Sur le dos, les pieds devant, couché le long de la pente (centre de l'image en 0, 0)."""
    return (f'<g transform="rotate(32) scale(.42)">'
            f'<path d="M-150 -40 Q-160 0 -150 40 L120 50 Q140 0 120 -50 Z" fill="url(#h2)" {STP} stroke-width="5"/>'
            f'<path d="M120 -40 L210 -60 L216 -30 L124 -10 Z M120 20 L214 30 L210 60 L120 50 Z" fill="url(#h2)" {STP} stroke-width="4.4"/>'
            f'<path d="M206 -66 L240 -64 L238 -30 L212 -28 Z M208 24 L242 26 L240 60 L206 62 Z" fill="{ENCRE}" {STP} stroke-width="3"/>'
            f'<path d="M-150 -30 Q-210 -40 -236 -80 Q-200 -110 -150 -80 Z" fill="url(#h1)" {STP} stroke-width="5"/>'
            f'<ellipse cx="-180" cy="-40" rx="34" ry="28" fill="{PAPIER}" {STP} stroke-width="4"/>'
            f'<path d="M-60 -48 Q-90 -110 -130 -150 L-110 -164 Q-60 -120 -36 -52 Z" fill="url(#h2)" {STP} stroke-width="4.4"/>'
            f'<circle cx="-122" cy="-160" r="18" fill="{PAPIER}" {STP} stroke-width="4"/></g>')


def tobie_boule(angle: float) -> str:
    """Roulé en boule, la capuche et les bottes qui dépassent, tourné de angle degrés."""
    return (f'<g transform="rotate({angle:.0f}) scale(.42)">'
            f'<path d="M-150 10 Q-150 -130 -10 -140 Q140 -130 150 0 Q150 130 10 140 Q-130 140 -150 10 Z" fill="url(#h2)" {STP} stroke-width="5"/>'
            f'<path d="M-130 -60 Q-200 -110 -220 -170 Q-150 -170 -90 -120 Z" fill="url(#h1)" {STP} stroke-width="5"/>'
            f'<ellipse cx="-118" cy="-70" rx="34" ry="30" fill="{PAPIER}" {STP} stroke-width="4"/>'
            f'<path d="M80 100 L150 150 L130 176 L64 128 Z M110 60 L190 84 L182 116 L104 96 Z" fill="{ENCRE}" {STP} stroke-width="3"/>'
            f'<path d="M-60 -100 Q40 -60 60 60 M-110 40 Q-20 60 30 120" fill="none" {STP} stroke-width="3"/>'
            f'<path d="M-30 -136 Q60 -110 120 -40" fill="none" stroke="{LAVIS}" stroke-width="10"/></g>')


def tobie_etale() -> str:
    """Étalé à plat ventre au bas de la pente, bras en avant."""
    return (f'<g transform="rotate(8) scale(.42)">'
            f'<path d="M-130 -20 Q-140 30 -120 60 L150 60 Q160 20 150 -20 Z" fill="url(#h2)" {STP} stroke-width="5"/>'
            f'<path d="M150 -10 L240 0 L238 30 L150 40 Z" fill="url(#h2)" {STP} stroke-width="4.4"/>'
            f'<path d="M236 -6 L262 -4 L262 34 L236 34 Z" fill="{ENCRE}" {STP} stroke-width="3"/>'
            f'<path d="M-130 0 L-250 10 L-250 40 L-130 40 Z" fill="url(#h2)" {STP} stroke-width="4.4"/>'
            f'<circle cx="-262" cy="26" r="20" fill="{PAPIER}" {STP} stroke-width="4"/>'
            f'<path d="M-120 -24 Q-170 -80 -230 -70 Q-200 -10 -130 10 Z" fill="url(#h1)" {STP} stroke-width="5"/>'
            f'<ellipse cx="-170" cy="-20" rx="32" ry="26" fill="{PAPIER}" {STP} stroke-width="4"/></g>')


def tobie_quatre_pattes() -> str:
    """À quatre pattes, la tête basse, il reprend son souffle (les pieds sur la pierre en y +96)."""
    return (f'<g transform="scale(.42)">'
            f'<path d="M-110 -40 Q0 -90 120 -40 L120 30 Q0 10 -110 30 Z" fill="url(#h2)" {STP} stroke-width="5"/>'
            f'<path d="M70 0 L80 196 L120 200 L128 10 Z" fill="url(#h2)" {STP} stroke-width="4.4"/>'
            f'<path d="M84 170 L250 176 L250 206 L82 206 Z" fill="url(#h2)" {STP} stroke-width="4.4"/>'
            f'<path d="M248 170 L284 172 L284 208 L248 208 Z" fill="{ENCRE}" {STP} stroke-width="3"/>'
            f'<path d="M-90 0 L-120 200 L-86 204 L-56 10 Z M-40 10 L-60 204 L-26 206 L-4 16 Z" fill="url(#h2)" {STP} stroke-width="4.4"/>'
            f'<ellipse cx="-104" cy="206" rx="24" ry="12" fill="{PAPIER}" {STP} stroke-width="4"/><ellipse cx="-44" cy="208" rx="24" ry="12" fill="{PAPIER}" {STP} stroke-width="4"/>'
            f'<path d="M-100 -40 Q-170 -30 -200 30 Q-150 60 -96 20 Z" fill="url(#h1)" {STP} stroke-width="5"/>'
            f'<ellipse cx="-150" cy="40" rx="30" ry="26" fill="{PAPIER}" {STP} stroke-width="4"/></g>')


# ----------------------------------------------------------------------------- plan A
def clairiere() -> str:
    """L'herbe rase de la clairière, très près ; au loin les dernières croix, espacées ; le ciel
    ouvert du papier nu."""
    r = rnd(601)
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>',
         f'<path d="M0 {SOL_A - 150} Q700 {SOL_A - 166} {W} {SOL_A - 140}" fill="none" stroke="{MINE}" stroke-width="2"/>']
    for x in (160, 430, 1460, 1780):
        h = r.uniform(60, 90)
        y = SOL_A - 150 + r.uniform(-4, 6)
        o.append(f'<path d="M{x} {y:.0f} V{y - h:.0f} M{x - h * .24:.0f} {y - h * .74:.0f} H{x + h * .24:.0f}" stroke="{MINE}" stroke-width="3"/>')
    o.append(f'<path d="M0 {SOL_A - 150} Q700 {SOL_A - 166} {W} {SOL_A - 140} V{H} H0 Z" fill="url(#h1)" opacity=".35"/>')
    o.append(f'<rect y="{SOL_A}" width="{W}" height="{H - SOL_A}" fill="url(#h1)"/>')
    o.append(f'<path d="M0 {SOL_A} H{W}" {STP} stroke-width="3"/>')
    for _ in range(140):
        x, y = r.uniform(0, W), r.uniform(SOL_A - 120, SOL_A + 4)
        k = .5 + (y - SOL_A + 120) / 160
        o.append(f'<path d="M{x:.0f} {y:.0f} l{-4 * k:.1f} {-14 * k:.1f} M{x + 5:.0f} {y:.0f} l{1 * k:.1f} {-18 * k:.1f} M{x + 10:.0f} {y:.0f} l{5 * k:.1f} {-12 * k:.1f}" stroke="{ENCRE}" stroke-width="1.4"/>')
    return "".join(o)


def trou(k: int) -> str:
    """La fente sous les bottes, de la fêlure (0) au trou ouvert (2 à 5) : le dedans en papier nu
    (la nuit à l'écran), cerné de mottes."""
    x, y = PIEDS_A, SOL_A
    if k == 0:
        return f'<path d="M{x - 90} {y + 6} l20 -4 l14 6 l22 -6 l18 5 l26 -4 l20 5" fill="none" {STP} stroke-width="2.2"/>'
    larg = {1: 70, 2: 180, 3: 270, 4: 280, 5: 280}[k]
    prof = {1: 12, 2: 40, 3: 58, 4: 60, 5: 60}[k]
    r = rnd(610 + k)
    pts = []
    for i in range(14):
        a = math.pi * 2 * i / 14
        pts.append((x + math.cos(a) * larg / 2 * r.uniform(.85, 1.1), y + 8 + math.sin(a) * prof / 2 * r.uniform(.8, 1.15)))
    d = "M" + " L".join(f"{px:.0f} {py:.0f}" for px, py in pts) + " Z"
    o = [f'<path d="{d}" fill="{PAPIER}" {STP} stroke-width="3"/>']
    # la lèvre de terre, côté joueur : une bande hachurée sous le bord avant
    o.append(f'<path d="M{x - larg / 2:.0f} {y + 8} Q{x:.0f} {y + 8 + prof * .9:.0f} {x + larg / 2:.0f} {y + 8}" fill="none" {STP} stroke-width="2"/>')
    # les mottes qui sautent puis retombent
    for _ in range({1: 6, 2: 9, 3: 7, 4: 5, 5: 4}[k]):
        mx = x + r.uniform(-larg * .7, larg * .7)
        my = y - r.uniform(10, 120 if k < 4 else 50)
        o.append(f'<ellipse cx="{mx:.0f}" cy="{my:.0f}" rx="{r.uniform(5, 11):.0f}" ry="{r.uniform(4, 8):.0f}" fill="url(#h2)" {STP} stroke-width="1.6" transform="rotate({r.uniform(0, 90):.0f} {mx:.0f} {my:.0f})"/>')
    return "".join(o)


def tobie_a(k: int) -> str:
    """Tobie dans la fente, coupé par la lèvre avant du trou à mesure qu'il tombe."""
    bras = {0: "bas", 1: "ecartes", 2: "battent", 3: "battent", 4: "leves"}.get(k)
    if bras is None:
        return ""
    chute = {0: 0, 1: 6, 2: 60, 3: 200, 4: 330}[k]
    penche = {0: 0, 1: -4, 2: 16, 3: 12, 4: 0}[k]   # positif : le buste part en arrière
    corps = f'<g transform="rotate({penche} {PIEDS_A} {SOL_A})">{tobie_debout(PIEDS_A, SOL_A + chute, bras)}</g>'
    if chute < 20:
        return corps
    # tout ce qui passe sous le bord avant du trou disparaît
    return (f'<clipPath id="levre{k}"><path d="M0 0 H{W} V{SOL_A + 10} H{PIEDS_A + 140} '
            f'Q{PIEDS_A} {SOL_A + 44} {PIEDS_A - 140} {SOL_A + 10} H0 Z"/></clipPath>'
            f'<g clip-path="url(#levre{k})">{corps}</g>')


def plan_a(k: int) -> str:
    return clairiere() + trou(k) + tobie_a(k)


# ----------------------------------------------------------------------------- plan B
def coulee() -> str:
    """Sous la terre : la fente en haut à gauche, la lumière qui tombe en hachures serrées (claire
    à l'écran), la coulée de terre et de racines en diagonale, la pierre taillée en bas à droite."""
    r = rnd(620)
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>']
    # la voûte de terre au-dessus (le plafond de la cavité) et la fente qui s'y ouvre
    o.append(f'<path d="M0 0 H{W} V120 Q1500 180 1100 140 Q700 100 420 120 L360 60 L300 118 Q150 130 0 160 Z" fill="url(#h2)" {STP} stroke-width="3"/>')
    o.append(f'<path d="M300 118 L330 0 M360 60 L392 0" {STP} stroke-width="2.4"/>')
    # la lumière qui tombe de la fente : un faisceau de hachures sur la pente
    o.append(f'<path d="M300 118 L420 120 L760 520 L420 560 Z" fill="url(#v1)" opacity=".8"/>')
    # la coulée : la pente de terre, de la fente à la pierre
    pente = "M0 300 Q300 230 520 380 Q900 600 1300 800 Q1420 860 1500 860"
    o.append(f'<path d="{pente} L1500 {H} L0 {H} Z" fill="url(#h1)" {STP} stroke-width="3"/>')
    for _ in range(40):
        t = r.uniform(0, 1)
        x = t * 1450
        y = 300 + (x / 1500) ** 1.1 * 560 + r.uniform(20, 200)
        o.append(f'<path d="M{x:.0f} {y:.0f} q12 -4 24 0" fill="none" stroke="{ENCRE}" stroke-width="1.4"/>')
    # les racines, grosses comme des bras, qui traversent la coulée et pendent du plafond
    for d in ("M80 160 Q200 300 160 520 Q140 640 220 760", "M620 120 Q600 260 700 340 Q780 400 760 520",
              "M1180 150 Q1240 300 1180 420", "M1460 140 Q1420 260 1480 380 Q1520 460 1500 560",
              "M260 900 Q520 700 860 760 Q1000 790 1100 720"):
        o.append(f'<path d="{d}" fill="none" stroke="{ENCRE}" stroke-width="16" stroke-linecap="round"/>'
                 f'<path d="{d}" fill="none" stroke="{MINE}" stroke-width="4" stroke-linecap="round"/>')
    # la pierre taillée : un chapiteau couché, ses feuilles sculptées, des blocs d'appareil
    o.append(f'<path d="M1380 860 H1920 V{H} H1380 Z" fill="url(#h2)" {STP} stroke-width="3"/>')
    o.append(f'<path d="M1400 860 L1440 790 H1880 L1920 860 Z" fill="{PAPIER}" {STP} stroke-width="3"/>')
    for x in range(1460, 1880, 70):
        o.append(f'<path d="M{x} 860 Q{x + 10} 816 {x + 35} 800 Q{x + 60} 816 {x + 70} 860" fill="url(#h1)" {STP} stroke-width="2"/>'
                 f'<path d="M{x + 35} 806 V856" stroke="{ENCRE}" stroke-width="1.4"/>')
    o.append(f'<path d="M1440 790 H1880" {STP} stroke-width="5"/>')
    for x, y, w, h in ((1560, 640, 200, 110), (1760, 600, 160, 150), (1660, 520, 140, 110)):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PAPIER}" {STP} stroke-width="3"/>'
                 f'<path d="M{x + 12} {y + 18} l30 -4 M{x + w - 50} {y + h - 20} l26 3" stroke="{MINE}" stroke-width="1.6"/>')
    o.append(f'<path d="M1520 790 L1560 750 L1600 790 Z" fill="url(#h1)" {STP} stroke-width="2"/>')
    return "".join(o)


def terre(k: int) -> str:
    """La terre qui retombe sur lui pendant qu'il ne bouge plus : des mottes en l'air (3), puis
    posées sur son dos et autour (4, 5)."""
    r = rnd(630 + k)
    o = []
    if k == 3:
        for _ in range(9):
            x, y = r.uniform(-90, 90), r.uniform(-110, -10)
            o.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r.uniform(3, 7):.0f}" ry="{r.uniform(2, 5):.0f}" fill="url(#h2)" {STP} stroke-width="1.4"/>')
        o.append(f'<path d="M-40 -110 l4 30 M10 -116 l-2 40 M50 -104 l3 26" stroke="{MINE}" stroke-width="1.4" stroke-dasharray="4 5"/>')
    if k in (4, 5):
        o.append(f'<path d="M-70 4 Q-30 -10 10 -2 Q40 -12 70 2 L66 10 Q0 6 -66 12 Z" fill="url(#h2)" {STP} stroke-width="1.6"/>')
        for _ in range(6):
            x = r.uniform(-100, 100)
            o.append(f'<ellipse cx="{x:.0f}" cy="{r.uniform(22, 30):.0f}" rx="{r.uniform(3, 6):.0f}" ry="3" fill="url(#h2)" {STP} stroke-width="1.2"/>')
    return "".join(o)


def image_b(k: int) -> str:
    """Tobie seul, centré dans une image de 240 x 240 transparente."""
    corps = {0: tobie_glisse(), 1: tobie_boule(200), 2: tobie_etale(), 3: tobie_etale() + terre(3),
             4: tobie_etale() + terre(4),
             5: f'<g transform="translate(0 6) rotate(-6)">{tobie_quatre_pattes()}</g>' + terre(5),
             6: tobie_quatre_pattes()}[k]
    return f'<g transform="translate(120 120)">{corps}</g>'


def ligne_b() -> str:
    corps = "".join(f'<svg x="{k * 240}" y="0" width="240" height="240" viewBox="0 0 240 240">{image_b(k)}</svg>' for k in range(7))
    return svg(corps, (0, 0, 1680, 240))


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    (DST / "cin_chute_01.svg").write_text(svg(plan_a(0)), encoding="utf-8")
    (DST / "cin_chute_02.svg").write_text(bande([plan_a(k) for k in range(6)], ZONE_A, 3), encoding="utf-8")
    (DST / "cin_chute_03.svg").write_text(svg(coulee()), encoding="utf-8")
    (DST / "cin_chute_04.svg").write_text(ligne_b(), encoding="utf-8")
    print("cin_chute : 2 fonds et 2 bandes dans art/src/cin/")


if __name__ == "__main__":
    main()
