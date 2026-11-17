#!/usr/bin/env python3
"""Génère les images de l'épilogue animé « La Remontée » (lettre e, recousu), d'après la planche
validée par le GD le 17/11 (direction-artistique/epilogues/planche_trois_fins.png). Consigne de
l'utilisateur : des images faites exprès pour la ciné ; seule la gravure e est réemployée.

  P1  cin_epi-e-galerie (1920 x 1300) : une galerie qui monte en biais vers une bouche de jour,
      étayée ; la caméra remonte avec eux. cin_epi-e-enfoui : un Enfoui qui grimpe, encapuchonné,
      la toile pâle, 4 images ; la seconde rangée est Tobie : sans ruban (sceau ouvert), on le
      reconnaît à sa sacoche vide et à la seule lanterne, éteinte (grille
      4 x 2, 240 x 360, les pieds en PIED).
  P2  cin_epi-e-mains (1920 x 800) : ses deux mains ouvertes, recousues (couture noire en travers
      des paumes) ; cin_epi-e-fermer : elles se ferment à demi puis se rouvrent, 2 images
      (ZONE_MAINS).
  P3  cin_epilogue-e (réemploi) + cin_epi-e-terre : la terre qui glisse de la butte, 3 images
      (ZONE_TERRE, fond transparent).
  P4  cin_epi-e-matin (1920 x 800) : le petit jour, un parapet de sacs, un soldat de face, il
      siffle ; cin_epi-e-epauler : il lève le fusil, l'épaule, vise, 6 images (grille 3 x 2 :
      image = pose x 2 + lèvres). Le noir tombe sur la dernière note : aucun coup n'est montré.
Aucun rouge : à sceau ouvert, le ruban est tombé (e7_ouverture_sceau). Rien ne se compte : la colonne sort du noir et y rentre.

Usage : python3 tools/gen_cin_epilogue_remontee.py
"""
from __future__ import annotations

import math
import random

from gen_cin_e1 import DST, W, bande, svg
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER

ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
H_PLAN = 800
CLAIR = "#D3CFC2"

# --- P1 : la galerie qui monte ----------------------------------------------------------------
H_GALERIE = 1300
PENTE = -0.5                         # la rampe : y = RAMPE0 + PENTE * x
RAMPE0 = 1180
HAUT_GALERIE = 520
ENFOUI = (240, 360)
PIED = (120, 340)


def rampe(x: float) -> float:
    return RAMPE0 + PENTE * x


def galerie() -> str:
    r = random.Random(1601)
    o = [f'<rect width="{W}" height="{H_GALERIE}" fill="{LAVIS}"/>']
    # le boyau : un aplat clair entre la rampe et le plafond, qui file vers le jour en haut à droite
    sol = " L".join(f"{x} {rampe(x) + r.uniform(-4, 4):.0f}" for x in range(-40, W + 81, 60))
    plafond = " L".join(f"{x} {rampe(x) - HAUT_GALERIE + r.uniform(-14, 14):.0f}" for x in range(W + 80, -41, -60))
    o.append(f'<path d="M{sol} L{plafond} Z" fill="{CLAIR}" {ST} stroke-width="5"/>')
    # la terre sous la rampe, un peu plus claire que la roche, des marches taillées
    o.append(f'<path d="M-40 {rampe(-40)} L{W + 80} {rampe(W + 80)} L{W + 80} {H_GALERIE} L-40 {H_GALERIE} Z" fill="{MINE}" {ST} stroke-width="5"/>')
    for x in range(-20, W + 60, 70):
        y = rampe(x)
        o.append(f'<path d="M{x} {y:.0f} v18 h70" fill="none" stroke="{ENCRE}" stroke-width="3"/>')
    # des cailloux et des racines dans la roche (au hasard, rien de régulier)
    for _ in range(90):
        x, y = r.uniform(0, W), r.uniform(0, H_GALERIE)
        if rampe(x) - HAUT_GALERIE - 20 < y < rampe(x) + 20:
            continue
        o.append(f'<path d="M{x:.0f} {y:.0f} q{r.uniform(-30, 30):.0f} {r.uniform(-8, 8):.0f} {r.uniform(-60, 60):.0f} {r.uniform(-4, 4):.0f}" '
                 f'stroke="{ENCRE}" stroke-width="2" fill="none" opacity=".6"/>')
    # les étais : deux montants et un chapeau, penchés comme la galerie
    for x in (240, 760, 1280, 1800):
        y0 = rampe(x)
        y1 = y0 - HAUT_GALERIE + 18
        for dx in (-70, 70):
            yb = rampe(x + dx)
            o.append(f'<path d="M{x + dx - 12} {yb + 4:.0f} L{x + dx - 12} {yb - HAUT_GALERIE + 30:.0f} L{x + dx + 12} {yb - HAUT_GALERIE + 30:.0f} L{x + dx + 12} {yb + 4:.0f} Z" fill="{LAVIS}" {ST} stroke-width="3.4"/>')
        o.append(f'<path d="M{x - 96} {rampe(x - 96) - HAUT_GALERIE + 44:.0f} L{x + 96} {rampe(x + 96) - HAUT_GALERIE + 44:.0f} '
                 f'L{x + 96} {rampe(x + 96) - HAUT_GALERIE + 20:.0f} L{x - 96} {rampe(x - 96) - HAUT_GALERIE + 20:.0f} Z" fill="{LAVIS}" {ST} stroke-width="3.4"/>')
        del y1
    # la bouche de jour, en haut à droite : le papier nu, des racines qui pendent
    o.append(f'<path d="M1560 {rampe(1560) - HAUT_GALERIE + 10:.0f} Q1700 -40 {W + 40} -40 L{W + 40} {rampe(W + 40) + 4:.0f} '
             f'Q1840 {rampe(1840) - 120:.0f} 1700 {rampe(1700) - 300:.0f} Z" fill="{PAPIER}" {ST} stroke-width="4"/>')
    for x in (1610, 1660, 1730, 1790):
        y = rampe(x) - HAUT_GALERIE + 14 if x < 1700 else 70
        o.append(f'<path d="M{x} {y:.0f} q{r.randint(-10, 10)} 40 {r.randint(-6, 6)} {r.randint(60, 110)}" stroke="{ENCRE}" stroke-width="2.4" fill="none"/>')
    # en bas à gauche, la galerie se perd dans le noir, par crans nets (la colonne en sort)
    for x_cran, op in ((520, .25), (330, .4), (160, .6)):
        o.append(f'<path d="M-40 0 L{x_cran} 0 L{x_cran} {H_GALERIE} L-40 {H_GALERIE} Z" fill="{ENCRE}" opacity="{op}"/>')
    return "".join(o)


def enfoui(k: int, tobie: bool) -> str:
    """Un Enfoui qui grimpe vers la droite, penché, le capuchon baissé, la toile pâle qui s'effrange
    sur les genoux ; k : le pas (4 images). Tobie : la sacoche vide et la lanterne éteinte, aucun ruban."""
    px, py = PIED
    ph = TAU * k / 4
    bob = -5 * abs(math.sin(ph))
    o = []
    # les jambes, bandées : la jambe d'avant puis la jambe d'arrière, posées sur la pente
    hanche = (px + 6, 236 + bob)
    for sgn, coul in ((-1, CLAIR), (1, PAPIER)):
        fx = px + sgn * 30 * math.cos(ph)
        fy = py + PENTE * (fx - px) - max(0.0, sgn * 14 * math.sin(ph))
        gx, gy = (hanche[0] + fx) / 2 + 14, (hanche[1] + fy) / 2 - 4
        d = f"M{hanche[0]:.0f} {hanche[1]:.0f} Q{gx:.0f} {gy:.0f} {fx:.0f} {fy:.0f}"
        o.append(f'<path d="{d}" fill="none" stroke="{ENCRE}" stroke-width="22" stroke-linecap="round"/>'
                 f'<path d="{d}" fill="none" stroke="{coul}" stroke-width="14" stroke-linecap="round"/>'
                 f'<path d="M{fx - 12:.0f} {fy:.0f} L{fx + 22:.0f} {fy - 6:.0f}" stroke="{ENCRE}" stroke-width="9" stroke-linecap="round"/>')
    # le bras d'arrière, ballant
    o.append(f'<path d="M126 {132 + bob:.0f} Q{104 - 8 * math.cos(ph):.0f} {190 + bob:.0f} {110 - 14 * math.cos(ph):.0f} {232 + bob:.0f}" fill="none" stroke="{ENCRE}" stroke-width="20" stroke-linecap="round"/>'
             f'<path d="M126 {132 + bob:.0f} Q{104 - 8 * math.cos(ph):.0f} {190 + bob:.0f} {110 - 14 * math.cos(ph):.0f} {232 + bob:.0f}" fill="none" stroke="{CLAIR}" stroke-width="13" stroke-linecap="round"/>')
    # la toile : des épaules aux genoux, penchée vers la pente, l'ourlet effrangé
    ourlet = " L".join(f"{x} {256 + bob + (8 if i % 2 else 0):.0f}" for i, x in enumerate(range(174, 79, -12)))
    o.append(f'<path d="M150 {98 + bob:.0f} Q186 {124 + bob:.0f} 178 {256 + bob:.0f} L{ourlet} Q86 {160 + bob:.0f} 120 {104 + bob:.0f} Z" fill="{PAPIER}" {ST} stroke-width="4"/>'
             f'<path d="M120 {110 + bob:.0f} Q96 {170 + bob:.0f} 90 {254 + bob:.0f} L112 {256 + bob:.0f} Q112 {180 + bob:.0f} 130 {116 + bob:.0f} Z" fill="{CLAIR}"/>'
             f'<path d="M150 {130 + bob:.0f} Q160 {190 + bob:.0f} 150 {250 + bob:.0f}" fill="none" stroke="{ENCRE}" stroke-width="2"/>')
    if tobie:
        # Tobie, sans ruban (il est tombé à l'ouverture du sceau) : la sacoche vide, plate, sur la
        # hanche, et le seul à porter une lanterne, éteinte, au bout du bras ballant
        o.append(f'<path d="M150 {104 + bob:.0f} L104 {214 + bob:.0f}" stroke="{ENCRE}" stroke-width="5"/>'
                 f'<path d="M86 {200 + bob:.0f} L124 {196 + bob:.0f} L126 {226 + bob:.0f} Q104 {232 + bob:.0f} 88 {228 + bob:.0f} Z" fill="{LAVIS}" {ST} stroke-width="3"/>')
        lx, ly = 110 - 14 * math.cos(ph), 240 + bob
        o.append(f'<path d="M{lx:.0f} {ly - 10:.0f} L{lx + 2:.0f} {ly + 6:.0f}" stroke="{ENCRE}" stroke-width="3"/>'
                 f'<path d="M{lx - 12:.0f} {ly + 6:.0f} h28 l-3 6 h-22 Z M{lx - 10:.0f} {ly + 12:.0f} h24 v30 h-24 Z" fill="{LAVIS}" {ST} stroke-width="3"/>'
                 f'<path d="M{lx - 4:.0f} {ly + 16:.0f} v22 M{lx + 8:.0f} {ly + 16:.0f} v22" stroke="{MINE}" stroke-width="2"/>'
                 f'<path d="M{lx - 12:.0f} {ly + 42:.0f} h28 l-3 6 h-22 Z" fill="{ENCRE}"/>')
    # le capuchon baissé vers la pente, le creux noir du visage tourné vers le sol
    hx, hy = 168, 78 + bob
    o.append(f'<path d="M{hx - 34} {hy + 22:.0f} Q{hx - 36} {hy - 30:.0f} {hx + 4} {hy - 34:.0f} Q{hx + 40} {hy - 30:.0f} {hx + 40} {hy + 8:.0f} '
             f'Q{hx + 30} {hy + 40:.0f} {hx - 4} {hy + 42:.0f} Z" fill="{PAPIER}" {ST} stroke-width="4"/>'
             f'<path d="M{hx + 8} {hy - 8:.0f} Q{hx + 34} {hy - 2:.0f} {hx + 32} {hy + 18:.0f} Q{hx + 20} {hy + 36:.0f} {hx + 2} {hy + 30:.0f} Q{hx - 6} {hy + 8:.0f} {hx + 8} {hy - 8:.0f} Z" fill="{ENCRE}"/>')
    # le bras d'avant, tendu vers la paroi au-dessus, la main qui cherche la prise
    mx, my = 214 + 8 * math.cos(ph), 150 + bob - 10 * math.cos(ph)
    o.append(f'<path d="M158 {126 + bob:.0f} Q190 {150 + bob:.0f} {mx:.0f} {my:.0f}" fill="none" stroke="{ENCRE}" stroke-width="20" stroke-linecap="round"/>'
             f'<path d="M158 {126 + bob:.0f} Q190 {150 + bob:.0f} {mx:.0f} {my:.0f}" fill="none" stroke="{PAPIER}" stroke-width="13" stroke-linecap="round"/>'
             f'<path d="M{mx:.0f} {my:.0f} l12 -6 M{mx:.0f} {my:.0f} l14 2 M{mx:.0f} {my:.0f} l10 9" stroke="{ENCRE}" stroke-width="4" stroke-linecap="round"/>')
    # un peu de terre sur les épaules
    r = random.Random(40 + k)
    for _ in range(9):
        o.append(f'<circle cx="{r.uniform(124, 176):.0f}" cy="{r.uniform(100, 140) + bob:.0f}" r="{r.uniform(1.6, 3.4):.1f}" fill="{LAVIS}"/>')
    return "".join(o)


TAU = 2 * math.pi


# --- P2 : les mains recousues -----------------------------------------------------------------------
MAIN_D = (1230, 470)
MAIN_G = (690, 470)
ECHELLE_MAIN = 1.9
ZONE_MAINS = (240, 0, 1440, 800)


def couture(x0: float, y0: float, x1: float, y1: float, pas: float = 14) -> str:
    """Une cicatrice cousue : le trait, et les points de fil noir en travers."""
    n = max(2, int(math.hypot(x1 - x0, y1 - y0) / pas))
    ang = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(ang) * 7, math.cos(ang) * 7
    o = [f'<path d="M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f}" stroke="{ENCRE}" stroke-width="2.2"/>']
    for i in range(1, n):
        cx, cy = x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n
        o.append(f'<path d="M{cx - nx:.1f} {cy - ny:.1f} L{cx + nx:.1f} {cy + ny:.1f}" stroke="{ENCRE}" stroke-width="2.6" stroke-linecap="round"/>')
    return "".join(o)


def main_recousue(x: float, y: float, miroir: bool, ferme: bool) -> str:
    """Une main ouverte, paume vers le ciel, les doigts vers le haut ; la manche de toile pâle sort
    du bas du cadre. La paume et le poignet cousus. ferme : les doigts repliés à demi."""
    doigts = []
    for bx, by, lg, ang, lw in ((96, 6, 96, -14, 22), (104, 30, 104, -2, 23), (98, 54, 94, 10, 21), (84, 76, 74, 22, 18)):
        if ferme:
            lg *= .5
            lw *= 1.08
        rad = math.radians(ang)
        ex, ey = bx + lg * math.cos(rad), by + lg * math.sin(rad)
        nx, ny = -math.sin(rad) * lw / 2, math.cos(rad) * lw / 2
        doigts.append(f'<path d="M{bx - nx:.1f} {by - ny:.1f} L{ex - nx:.1f} {ey - ny:.1f} '
                      f'Q{ex + lw * .7 * math.cos(rad):.1f} {ey + lw * .7 * math.sin(rad):.1f} {ex + nx:.1f} {ey + ny:.1f} '
                      f'L{bx + nx:.1f} {by + ny:.1f}" fill="{PAPIER}" {ST} stroke-width="3.4"/>')
        if ferme:  # le bout du doigt replié vers la paume : l'ongle, vu de face
            doigts.append(f'<path d="M{ex - nx * .6:.1f} {ey - ny * .6:.1f} Q{ex + 6 * math.cos(rad):.1f} {ey + 6 * math.sin(rad):.1f} {ex + nx * .6:.1f} {ey + ny * .6:.1f}" '
                          f'fill="none" stroke="{ENCRE}" stroke-width="2.4"/>')
        else:
            for t in (.42, .74):
                jx, jy = bx + lg * t * math.cos(rad), by + lg * t * math.sin(rad)
                doigts.append(f'<path d="M{jx - nx * .7:.1f} {jy - ny * .7:.1f} Q{jx + 3 * math.cos(rad):.1f} {jy + 3 * math.sin(rad):.1f} {jx + nx * .7:.1f} {jy + ny * .7:.1f}" '
                              f'fill="none" stroke="{ENCRE}" stroke-width="1.4"/>')
    pouce = ("M-10 -4 Q10 -30 34 -36 Q50 -38 54 -26 Q50 -14 34 -10 Q22 -6 20 -2" if ferme else
             "M-10 -4 Q16 -46 56 -60 Q82 -66 88 -48 Q84 -30 56 -22 Q36 -14 30 -2")
    sx = -ECHELLE_MAIN if miroir else ECHELLE_MAIN
    return (f'<g transform="translate({x} {y}) scale({sx} {ECHELLE_MAIN}) rotate(-96)">'
            # la manche de toile pâle, effrangée au poignet
            f'<path d="M-520 30 L-130 -6 L-140 22 L-124 44 L-138 70 L-120 104 L-520 150 Z" fill="{CLAIR}" {ST} stroke-width="3"/>'
            f'<path d="M-420 40 Q-300 60 -200 30 M-430 110 Q-320 100 -230 120" fill="none" stroke="{ENCRE}" stroke-width="1.4"/>'
            f'<path d="M-122 6 Q-60 -8 10 -6 Q70 -4 100 0 L106 88 Q60 108 -10 104 Q-80 102 -120 96 Z" fill="{PAPIER}" {ST} stroke-width="3.4"/>'
            + "".join(doigts) +
            f'<path d="{pouce}" fill="{PAPIER}" {ST} stroke-width="3"/>'
            f'<path d="M-20 14 Q30 34 96 26 M-40 44 Q20 62 98 54" fill="none" stroke="{ENCRE}" stroke-width="1.4"/>'
            # les coutures : en travers de la paume, et le tour du poignet
            + couture(-96, 86, 84, 10, 12) + couture(-112, 8, -108, 94, 11)
            + '</g>')


def fond_mains() -> str:
    """Dans la galerie, à la lumière d'en haut : la roche claire, quelques éclats ; rien d'autre."""
    r = random.Random(1602)
    o = [f'<rect width="{W}" height="{H_PLAN}" fill="{MINE}"/>']
    for _ in range(26):
        x, y = r.uniform(0, W), r.uniform(0, H_PLAN)
        o.append(f'<path d="M{x:.0f} {y:.0f} l{r.uniform(20, 70):.0f} {r.uniform(-6, 6):.0f}" stroke="{LAVIS}" stroke-width="2"/>')
    # le jour vient d'en haut : une large bande plus claire, à bord net
    o.append(f'<path d="M520 0 L1440 0 L1600 {H_PLAN} L360 {H_PLAN} Z" fill="{CLAIR}" opacity=".7"/>')
    return "".join(o)


def mains(ferme: bool) -> str:
    return main_recousue(*MAIN_G, False, ferme) + main_recousue(*MAIN_D, True, ferme)


# --- P3 : la terre qui glisse (sur la gravure e : silhouette en (1040, 426), parapet y 420) --------
SX, SY, PAR = 1040, 426, 420
ZONE_TERRE = (640, 240, 800, 340)


def butte_y(x: float) -> float:
    """Le haut de la butte de la gravure e (relevé sur l'image) : un plateau vers y 322 sous le
    torse, qui descend jusqu'au parapet (y 425) en x 710 et 1380."""
    d = (x - SX) / (330 if x < SX else 340)
    return 322 + 103 * min(1.0, d * d)


def terre(k: int) -> str:
    """Des mottes qui roulent sur la face de la butte, le long des fissures, et des filets de terre
    qui coulent ; 3 images en boucle, chacune décale tout d'un tiers de pas vers le bas."""
    r = random.Random(1603)
    o = []
    for _ in range(11):
        a = r.uniform(-250, 250)
        x0 = SX + a * .45
        y0 = butte_y(x0) + 10
        x1, y1 = SX + a * 1.2, 570
        rr = r.uniform(2.6, 5.6)
        decal = r.random()
        for j in range(2):
            u = ((j + k / 3 + decal) / 2) % 1.0 * .9
            o.append(f'<circle cx="{x0 + (x1 - x0) * u:.0f}" cy="{y0 + (y1 - y0) * u:.0f}" r="{rr:.1f}" fill="{LAVIS}" {ST} stroke-width="1.6"/>')
        if r.random() < .5:
            o.append(f'<path d="M{x0:.0f} {y0:.0f} L{x0 + (x1 - x0) * .5:.0f} {y0 + (y1 - y0) * .5:.0f}" stroke="{ENCRE}" stroke-width="2.2" '
                     f'stroke-dasharray="3 9" stroke-dashoffset="{-k * 4}" fill="none"/>')
    # quelques grains qui tombent des épaules
    for _ in range(8):
        x = SX + r.uniform(-110, 110)
        y = 250 + ((r.uniform(0, 60) + k * 20) % 60)
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(1.6, 3.2):.1f}" fill="{LAVIS}"/>')
    return "".join(o)


# --- P4 : le soldat au fusil, de face ------------------------------------------------------------------
TETE = (960, 250)
ZONE_EPAULER = (540, 40, 840, 760)
PARAPET = 560


def matin_fond() -> str:
    """Le petit jour vu depuis le no man's land, au ras du sol : le ciel pâle, un parapet de sacs,
    deux piquets de barbelés au premier plan, nets."""
    r = random.Random(1604)
    o = [f'<rect width="{W}" height="{H_PLAN}" fill="{PAPIER}"/>']
    for _ in range(12):
        y = r.randint(20, 380)
        o.append(f'<path d="M{r.randint(0, W)} {y} h{r.randint(140, 420)}" stroke="{MINE}" stroke-width="1.4"/>')
    return "".join(o)


def parapet() -> str:
    o = [f'<path d="M-20 {PARAPET} Q480 {PARAPET - 14} 960 {PARAPET - 6} T{W + 20} {PARAPET - 10} V{H_PLAN} H-20 Z" fill="{CLAIR}" {ST} stroke-width="4"/>']
    for j, y in enumerate(range(PARAPET + 50, H_PLAN + 60, 70)):
        for x in range(-70 + (j % 2) * 75, W + 80, 150):
            o.append(f'<path d="M{x} {y} Q{x + 75} {y - 50} {x + 150} {y}" fill="none" stroke="{ENCRE}" stroke-width="2.4"/>')
    # les piquets et le fil au premier plan (silhouettes d'encre, sans flou)
    for x in (230, 1720):
        o.append(f'<path d="M{x - 14} {H_PLAN} L{x - 6} {PARAPET + 10} L{x + 8} {PARAPET + 10} L{x + 16} {H_PLAN} Z" fill="{ENCRE}"/>')
    for y in (PARAPET + 50, PARAPET + 130):
        o.append(f'<path d="M-20 {y + 20} Q230 {y - 10} 980 {y + 30} T{W + 20} {y + 10}" fill="none" stroke="{ENCRE}" stroke-width="2.4"/>')
        for x in range(60, W, 170):
            yy = y + 18
            o.append(f'<path d="M{x - 8} {yy - 8} l16 16 M{x + 8} {yy - 8} l-16 16" stroke="{ENCRE}" stroke-width="2.4"/>')
    return "".join(o)


def bras(x0: float, y0: float, x1: float, y1: float) -> str:
    d = f"M{x0:.0f} {y0:.0f} L{x1:.0f} {y1:.0f}"
    return (f'<path d="{d}" stroke="{ENCRE}" stroke-width="58" stroke-linecap="round"/>'
            f'<path d="{d}" stroke="{LAVIS}" stroke-width="48" stroke-linecap="round"/>')


def poing(x: float, y: float) -> str:
    return (f'<path d="M{x - 26} {y - 18} Q{x - 30} {y + 20} {x} {y + 24} Q{x + 30} {y + 20} {x + 26} {y - 18} Q{x} {y - 30} {x - 26} {y - 18} Z" fill="{PAPIER}" {ST} stroke-width="3.4"/>'
            f'<path d="M{x - 18} {y - 2} h36 M{x - 18} {y + 10} h36" stroke="{ENCRE}" stroke-width="1.6"/>')


def fusil(x0: float, y0: float, x1: float, y1: float, crosse: float = 46) -> str:
    """Le fusil de x0 (la crosse) à x1 (la bouche) : le bois, le canon d'acier, la bouche noire."""
    ang = math.atan2(y1 - y0, x1 - x0)
    c, s = math.cos(ang), math.sin(ang)
    lg = math.hypot(x1 - x0, y1 - y0)
    return (f'<g transform="translate({x0:.0f} {y0:.0f}) rotate({math.degrees(ang):.1f})">'
            f'<path d="M0 {-crosse / 2:.0f} L{lg * .38:.0f} -12 L{lg * .7:.0f} -10 L{lg * .7:.0f} 10 L{lg * .38:.0f} 14 L0 {crosse / 2:.0f} Z" fill="{LAVIS}" {ST} stroke-width="3.4"/>'
            f'<path d="M{lg * .7:.0f} -6 L{lg:.0f} -5 L{lg:.0f} 5 L{lg * .7:.0f} 6 Z" fill="{MINE}" {ST} stroke-width="3"/>'
            f'<path d="M{lg * .3:.0f} -16 l30 0 l0 -10" fill="none" {ST} stroke-width="3"/>'
            f'</g>') if (c or s) else ""


def tete_soldat(pose: int, levres: int) -> str:
    """De face, le casque enfoncé, une moustache grise ; il siffle entre ses dents (levres 0 : la
    bouche en rond, 1 : plus serrée). pose 2 : la joue sur la crosse, l'œil gauche fermé."""
    x, y = TETE
    pench = (0, 6, 10)[pose]
    x += pench
    o = [f'<path d="M{x - 30} {y + 110} L{x - 34} {y + 170} L{x + 34} {y + 170} L{x + 30} {y + 110} Z" fill="{PAPIER}" {ST} stroke-width="4"/>',
         f'<path d="M{x - 84} {y - 20} Q{x - 92} {y + 70} {x - 60} {y + 112} Q{x - 30} {y + 140} {x} {y + 140} Q{x + 30} {y + 140} {x + 60} {y + 112} '
         f'Q{x + 92} {y + 70} {x + 84} {y - 20} Z" fill="{PAPIER}" {ST} stroke-width="4.4"/>',
         f'<path d="M{x - 86} {y + 24} Q{x - 108} {y + 26} {x - 104} {y + 54} Q{x - 100} {y + 74} {x - 82} {y + 70} '
         f'M{x + 86} {y + 24} Q{x + 108} {y + 26} {x + 104} {y + 54} Q{x + 100} {y + 74} {x + 82} {y + 70}" fill="{PAPIER}" {ST} stroke-width="3.4"/>']
    # les yeux : ouverts, droits sur nous ; en visant, le gauche (à l'écran) se ferme
    for dx in (-36, 36):
        if pose == 2 and dx > 0:
            o.append(f'<path d="M{x + dx - 18} {y + 26} Q{x + dx} {y + 32} {x + dx + 18} {y + 26}" fill="none" {ST} stroke-width="3.6"/>')
        else:
            o.append(f'<path d="M{x + dx - 18} {y + 26} Q{x + dx} {y + 14} {x + dx + 18} {y + 26} Q{x + dx} {y + 34} {x + dx - 18} {y + 26} Z" fill="{PAPIER}" {ST} stroke-width="3"/>'
                     f'<circle cx="{x + dx}" cy="{y + 25}" r="6" fill="{ENCRE}"/>')
        o.append(f'<path d="M{x + dx - 22} {y + 8} Q{x + dx} {y + (0 if pose < 2 else 6)} {x + dx + 22} {y + 6}" fill="none" {ST} stroke-width="4"/>')
    o.append(f'<path d="M{x - 4} {y + 30} L{x - 12} {y + 78} Q{x} {y + 86} {x + 12} {y + 78}" fill="none" {ST} stroke-width="3.4"/>')
    # la moustache, grise, et dessous la bouche qui siffle
    o.append(f'<path d="M{x - 52} {y + 104} Q{x - 30} {y + 84} {x} {y + 92} Q{x + 30} {y + 84} {x + 52} {y + 104} Q{x + 26} {y + 100} {x} {y + 102} Q{x - 26} {y + 100} {x - 52} {y + 104} Z" fill="{MINE}" {ST} stroke-width="3"/>')
    rb = (9, 6)[levres]
    o.append(f'<ellipse cx="{x}" cy="{y + 116}" rx="{rb}" ry="{rb * 1.15:.1f}" fill="{ENCRE}"/>'
             f'<path d="M{x - rb - 9} {y + 112} Q{x} {y + 104 - rb * .3:.0f} {x + rb + 9} {y + 112} M{x - rb - 7} {y + 122} Q{x} {y + 130 + rb * .3:.0f} {x + rb + 7} {y + 122}" fill="none" {ST} stroke-width="3"/>')
    # le casque de face : la bombe, le bord large qui fait de l'ombre sur le front
    o.append(f'<path d="M{x - 84} {y + 70} L{x - 92} {y + 6} M{x + 84} {y + 70} L{x + 92} {y + 6}" fill="none" {ST} stroke-width="3"/>'
             f'<path d="M{x - 96} {y - 14} Q{x - 90} {y - 86} {x} {y - 90} Q{x + 90} {y - 86} {x + 96} {y - 14} Z" fill="{LAVIS}" {ST} stroke-width="4.4"/>'
             f'<path d="M{x - 186} {y - 4} Q{x} {y - 40} {x + 186} {y - 4} L{x + 176} {y + 12} Q{x} {y - 18} {x - 176} {y + 12} Z" fill="{LAVIS}" {ST} stroke-width="4"/>'
             f'<path d="M{x - 64} {y - 52} Q{x} {y - 70} {x + 64} {y - 52}" fill="none" stroke="{MINE}" stroke-width="2.4"/>')
    return "".join(o)


def soldat(pose: int, levres: int) -> str:
    """Le soldat derrière le parapet, de face, vu des épaules ; pose 0 : le fusil en travers de la
    poitrine ; 1 : il l'épaule, la bouche vers le bas à gauche ; 2 : il vise, droit sur nous (la
    bouche du canon noire, en rond, devant lui)."""
    x, y = TETE
    o = [  # la capote, les épaules larges, le col
        f'<path d="M{x - 300} {PARAPET + 30} Q{x - 300} {y + 240} {x - 160} {y + 190} Q{x} {y + 160} {x + 160} {y + 190} '
        f'Q{x + 300} {y + 240} {x + 300} {PARAPET + 30} Z" fill="{LAVIS}" {ST} stroke-width="5"/>',
        f'<path d="M{x - 90} {y + 196} L{x - 40} {y + 150} L{x} {y + 210} L{x + 40} {y + 150} L{x + 90} {y + 196}" fill="none" {ST} stroke-width="4"/>',
        "".join(f'<circle cx="{x}" cy="{y + 250 + j * 70}" r="9" fill="{MINE}" {ST} stroke-width="3"/>' for j in range(3)),
    ]
    if pose == 0:
        o.append(fusil(x + 220, y + 330, x - 230, y + 30, 50))
        o.append(bras(x + 230, y + 200, x + 150, y + 290) + poing(x + 150, y + 290))
        o.append(bras(x - 230, y + 210, x - 120, y + 200) + poing(x - 110, y + 196))
        o.append(tete_soldat(0, levres))
    elif pose == 1:
        # la crosse monte à l'épaule droite (à gauche de l'écran : il nous fait face), le canon
        # descend vers nous en biais ; la main gauche sous le fût
        o.append(tete_soldat(1, levres))
        o.append(fusil(x - 130, y + 196, x + 300, y + 300, 46))
        o.append(bras(x + 250, y + 220, x + 170, y + 270) + poing(x + 170, y + 262))
        o.append(bras(x - 240, y + 220, x - 100, y + 230) + poing(x - 86, y + 222))
    else:
        o.append(tete_soldat(2, levres))
        # vu de face : la crosse contre sa joue droite (à gauche de l'écran), le fût en raccourci,
        # la bouche du canon sous l'œil qui vise ; la main gauche soutient le fût
        bx, by = x - 20, y + 214
        o.append(f'<path d="M{x - 64} {y + 118} L{x - 92} {y + 148} L{bx - 18} {by + 2} L{bx + 20} {by - 8} Z" fill="{LAVIS}" {ST} stroke-width="3.4"/>')
        o.append(bras(x - 250, y + 220, x - 110, y + 178) + poing(x - 96, y + 170))
        o.append(bras(x + 250, y + 230, bx + 40, by + 50) + poing(bx + 24, by + 44))
        o.append(f'<circle cx="{bx}" cy="{by}" r="40" fill="{MINE}" {ST} stroke-width="4"/>'
                 f'<circle cx="{bx}" cy="{by}" r="21" fill="{ENCRE}"/>'
                 f'<path d="M{bx - 5} {by - 40} l5 -18 l5 18" fill="{ENCRE}" {ST} stroke-width="2"/>')
    return "".join(o)


def matin(pose: int, levres: int) -> str:
    return matin_fond() + soldat(pose, levres) + parapet()


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    fichiers = {
        "cin_epi-e-galerie": svg(galerie(), (0, 0, W, H_GALERIE)),
        "cin_epi-e-enfoui": bande([enfoui(k, t) for t in (False, True) for k in range(4)], (0, 0) + ENFOUI, 4),
        "cin_epi-e-mains": svg(fond_mains() + mains(False), (0, 0, W, H_PLAN)),
        "cin_epi-e-fermer": bande([fond_mains() + mains(f) for f in (False, True)], ZONE_MAINS, 2),
        "cin_epi-e-terre": bande([terre(k) for k in range(3)], ZONE_TERRE, 3),
        "cin_epi-e-matin": svg(matin(0, 0), (0, 0, W, H_PLAN)),
        "cin_epi-e-epauler": bande([matin(p, l) for p in range(3) for l in range(2)], ZONE_EPAULER, 3),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"épilogue e : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
