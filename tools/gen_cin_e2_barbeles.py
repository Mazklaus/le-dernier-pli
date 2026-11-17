#!/usr/bin/env python3
"""Génère les planches de la cinématique e2_barbeles_foncer (lot 1, planche validée par le GD
le 17/11) : dans le brouillard, de nuit, Tobie fonce dans les fils ; une pointe lui prend la
manche et un peu de peau ; il s'arrache et un lambeau de capote reste sur le fil.

  P1, 0 à 2,5 s, de profil :
  cin_e2-barbeles-brume    le fond 2400 x 1080 (le glissement de P1 ne montre aucun bord) :
                           le brouillard de nuit, la terre, la ceinture de barbelés à droite
                           (chevaux de frise, rouleaux, un fil tendu à y FIL_Y) ;
  cin_e2-barbeles-course   3 images de 320 x 440 en ligne, pieds à (160, 420) : Tobie en
                           silhouette noire qui court vers la droite.
  P2, 2,5 à 5 s, gros plan :
  cin_e2-barbeles-gros     le fond 1920 x 1080 : le fil en diagonale, ses pointes, la manche
                           accrochée (l'image 0 de la planche suivante, en entier) ;
  cin_e2-barbeles-manche   3 images de ZONE_MANCHE en ligne : 0 la pointe dans l'étoffe ; 1 une
                           goutte de sang perle sur la pointe d'en dessous, une griffure au
                           poignet ; 2 la goutte grossit, s'étire, l'étoffe tire plus fort.
  P3, 5 à 7 s, de profil (le fond de P1, en fin de glissement) :
  cin_e2-barbeles-lambeau  2 images de 200 x 220 en ligne, attache à (100, 20) : le lambeau
                           de capote pendu à une pointe du fil tendu, qui bat au vent.

Le seul rouge est le sang (goutte et griffure du gros plan). Tobie est une silhouette : le
ruban ne se voit pas.

Usage : python3 tools/gen_cin_e2_barbeles.py
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from gen_cin_epilogues import DEFS_CIN
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER, ROUGE

DST = Path(__file__).resolve().parent.parent / "art" / "src" / "cin"
W, H = 1920, 1080
ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
CLAIR = "#D3CFC2"
NUIT = "#2E2B25"
ETOFFE = "#5A554B"      # la capote : un ton au-dessus de la nuit, pour qu'elle se lise
SOL = 860
BRUME_W = 2400
FIL_Y = 640             # le fil tendu de la ceinture, dans le fond de P1
ATTACHE_LAMBEAU = (1640, FIL_Y)
ZONE_MANCHE = (480, 240, 1100, 700)
POINTE = (980, 501)     # la pointe qui prend la manche, dans le gros plan


def svg(contenu: str, w: int = W, h: int = H) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{DEFS_CIN}{contenu}</svg>\n')


def grille(images: list[str], w: int, h: int) -> str:
    corps = "".join(f'<g transform="translate({i * w} 0)">{c}</g>' for i, c in enumerate(images))
    return svg(corps, w * len(images), h)


def bande(images: list[str], zone: tuple[int, int, int, int]) -> str:
    x, y, w, h = zone
    corps = "".join(f'<svg x="{i * w}" y="0" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}">{c}</svg>'
                    for i, c in enumerate(images))
    return svg(corps, w * len(images), h)


# --- les fils ----------------------------------------------------------------------------------
def pointe(x: float, y: float, a: float, t: float = 14, ep: float = 3) -> str:
    """Une torsade de barbelé en (x, y) sur un fil d'angle a : quatre pointes en X."""
    o = []
    for d in (50, 130, 230, 310):
        r = math.radians(d) + a
        o.append(f"M{x:.1f} {y:.1f} l{t * math.cos(r):.1f} {t * math.sin(r):.1f}")
    return (f'<path d="{" ".join(o)}" {ST} stroke-width="{ep}" fill="none"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{ep * 1.3:.1f}" fill="{ENCRE}"/>')


def fil(x0: float, y0: float, x1: float, y1: float, pas: float, ep: float = 2.5, t: float = 12,
        mou: float = 0.0, op: float = 1.0) -> str:
    """Un fil (un peu de mou) et ses torsades tous les « pas »."""
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + mou
    o = [f'<path d="M{x0:.0f} {y0:.0f} Q{mx:.0f} {my:.0f} {x1:.0f} {y1:.0f}" fill="none" stroke="{ENCRE}" stroke-width="{ep}"/>']
    n = max(1, int(math.hypot(x1 - x0, y1 - y0) / pas))
    for k in range(1, n):
        u = k / n
        x = (1 - u) ** 2 * x0 + 2 * u * (1 - u) * mx + u * u * x1
        y = (1 - u) ** 2 * y0 + 2 * u * (1 - u) * my + u * u * y1
        o.append(pointe(x, y, math.atan2(y1 - y0, x1 - x0), t, ep))
    return f'<g opacity="{op}">{"".join(o)}</g>'


def brume_bandes(r: random.Random, w: int, y0: int, y1: int, n: int) -> str:
    o = []
    for _ in range(n):
        y = r.uniform(y0, y1)
        h = r.uniform(40, 120)
        x = r.uniform(-300, w - 200)
        o.append(f'<ellipse cx="{x + 400:.0f}" cy="{y:.0f}" rx="{r.uniform(400, 900):.0f}" ry="{h:.0f}" '
                 f'fill="{MINE}" opacity="{r.uniform(.06, .16):.2f}"/>')
    return "".join(o)


# --- P1 et P3 : la brume -----------------------------------------------------------------------
def cheval(x: float, y: float, h: float, ep: float = 9) -> str:
    """Un cheval de frise : deux croix de piquets et une barre."""
    return (f'<path d="M{x - h * .4:.0f} {y:.0f} L{x + h * .3:.0f} {y - h:.0f} M{x + h * .4:.0f} {y:.0f} L{x - h * .3:.0f} {y - h:.0f}" '
            f'{ST} stroke-width="{ep}" fill="none"/>')


def brume() -> str:
    r = random.Random(2202)
    w = BRUME_W
    o = [f'<rect width="{w}" height="{H}" fill="{NUIT}"/>',
         f'<rect width="{w}" height="{SOL - 80}" fill="{LAVIS}" opacity=".55"/>',
         brume_bandes(r, w, 150, 700, 18)]
    # la ceinture du fond, à peine lisible dans le brouillard
    x = 300
    while x < w:
        o.append(f'<g opacity=".22">{cheval(x, SOL - 140, 140, 6)}</g>')
        x += r.uniform(180, 260)
    o.append(fil(0, SOL - 230, w, SOL - 220, 90, 1.5, 8, 10, .22))
    # la terre
    o.append(f'<path d="M0 {SOL - 20} Q600 {SOL - 40} 1200 {SOL - 14} T{w} {SOL - 24} V{H} H0 Z" fill="{NUIT}"/>')
    for _ in range(60):
        xx, yy = r.uniform(0, w), r.uniform(SOL, H)
        o.append(f'<path d="M{xx:.0f} {yy:.0f} q{r.uniform(20, 50):.0f} {r.uniform(-6, 6):.0f} {r.uniform(50, 110):.0f} 0" '
                 f'fill="none" stroke="{LAVIS}" stroke-width="3" opacity=".7"/>')
    # la ceinture de devant : chevaux de frise, rouleaux, le fil tendu
    x = 1480
    while x < w + 100:
        o.append(cheval(x, SOL - 10, 320, 12))
        x += r.uniform(200, 250)
    for k in range(14):   # les rouleaux : des boucles de fil
        cx = 1460 + k * 70
        o.append(f'<ellipse cx="{cx}" cy="{SOL - 90}" rx="62" ry="80" fill="none" stroke="{ENCRE}" stroke-width="2.5"/>')
    o.append(fil(1460, SOL - 160, w, SOL - 150, 70, 2.5, 10, 14))
    o.append(fil(1440, FIL_Y, w, FIL_Y, 100, 3, 13))
    o.append(fil(1460, SOL - 260, w, SOL - 240, 85, 2.5, 11, 18))
    o.append(brume_bandes(r, w, 600, 900, 6))
    return "".join(o)


# --- Tobie qui court ----------------------------------------------------------------------------
def membre(*pts: tuple[float, float], ep: float = 22) -> str:
    d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    return f'<path d="{d}" fill="none" stroke="{ENCRE}" stroke-width="{ep}" stroke-linecap="round" stroke-linejoin="round"/>'


def botte(x: float, y: float, a: float = 0) -> str:
    return (f'<g transform="rotate({a} {x} {y})"><path d="M{x - 12} {y - 14} L{x + 26} {y - 8} Q{x + 32} {y + 2} {x + 22} {y + 4} '
            f'L{x - 14} {y + 4} Z" fill="{ENCRE}" stroke="{ENCRE}" stroke-width="4" stroke-linejoin="round"/></g>')


# (genou avant, pied avant, angle botte), (genou arrière, pied arrière, angle), (coude, main) x2
POSES = [
    (((205, 320), (238, 414), 0), ((118, 318), (64, 372), 40), ((150, 196), (124, 226)), ((228, 176), (256, 146))),
    (((180, 330), (160, 416), 0), ((150, 318), (112, 364), 60), ((168, 200), (176, 236)), ((196, 196), (214, 226))),
    (((212, 300), (218, 372), 30), ((124, 336), (92, 412), 10), ((226, 180), (254, 152)), ((150, 196), (122, 226))),
]


def tobie_course(k: int) -> str:
    """Tobie de profil, penché en avant, qui court vers la droite (k 0 à 2) ; pieds à y 420."""
    (ga, pa, aa), (gr, pr, ar), (c1, m1), (c2, m2) = POSES[k]
    rebond = (0, -8, 4)[k]
    hanche = (150, 252 + rebond)
    epaule = (186, 136 + rebond)
    o: list[str] = []
    # le bras de derrière, la jambe de derrière
    o.append(membre(epaule, c1, m1, ep=17))
    o.append(membre(hanche, gr, pr, ep=24))
    o.append(botte(*pr, ar))
    # la capote : épaules, pans qui battent derrière
    pan = (0, 14, -8)[k]
    o.append(f'<path d="M{epaule[0] - 26} {epaule[1] - 10} Q{epaule[0]} {epaule[1] - 26} {epaule[0] + 22} {epaule[1] - 4} '
             f'L{hanche[0] + 44} {hanche[1] + 24} Q{hanche[0]} {hanche[1] + 44} {hanche[0] - 56 - pan} {hanche[1] + 52 + pan / 2} '
             f'Q{hanche[0] - 36} {hanche[1] - 10} {epaule[0] - 26} {epaule[1] - 10} Z" fill="{ENCRE}" stroke="{ENCRE}" '
             f'stroke-width="6" stroke-linejoin="round"/>')
    # la sacoche qui saute à la hanche, sa sangle
    o.append(f'<path d="M{epaule[0] + 4} {epaule[1]} L{hanche[0] - 30} {hanche[1] - 4}" stroke="{MINE}" stroke-width="3" opacity=".7"/>')
    o.append(f'<rect x="{hanche[0] - 64}" y="{hanche[1] - 22 - rebond}" width="42" height="40" rx="4" fill="{ENCRE}" '
             f'transform="rotate({(-8, 6, -2)[k]} {hanche[0] - 43} {hanche[1] - 2})"/>')
    # la jambe de devant
    o.append(membre(hanche, ga, pa, ep=24))
    o.append(botte(*pa, aa))
    # la tête sous la capuche, tendue vers l'avant
    hx, hy = epaule[0] + 18, epaule[1] - 40
    o.append(f'<path d="M{hx - 30} {hy + 24} Q{hx - 38} {hy - 26} {hx} {hy - 34} Q{hx + 34} {hy - 30} {hx + 32} {hy + 4} '
             f'L{hx + 36} {hy + 18} L{hx + 26} {hy + 24} Q{hx} {hy + 40} {hx - 30} {hy + 24} Z" fill="{ENCRE}"/>')
    # le bras de devant
    o.append(membre(epaule, c2, m2, ep=17))
    return "".join(o)


# --- P2 : la manche accrochée --------------------------------------------------------------------
def gros(k: int) -> str:
    """Le gros plan : le fil en diagonale passe par POINTE ; la manche monte du bas à gauche,
    la pointe la prend par le haut ; le poignet et la main tirent vers le bas à droite."""
    r = random.Random(2203)
    px, py = POINTE
    tire = (0, 10, 22)[k]          # l'étoffe tirée vers le bas à droite
    o = [f'<rect width="{W}" height="{H}" fill="{NUIT}"/>',
         f'<rect width="{W}" height="{H}" fill="{LAVIS}" opacity=".45"/>',
         brume_bandes(r, W, 0, H, 10)]
    # des fils plus loin, flous dans le brouillard
    o.append(fil(-40, 120, W + 40, 300, 160, 4, 20, 30, .25))
    o.append(fil(-40, 860, W + 40, 1000, 180, 5, 24, 30, .2))
    # la manche : un gros tube d'étoffe, la couture, le revers
    cx, cy = 1130 + tire * .6, 640 + tire       # le centre du revers
    o.append(f'<path d="M300 {H + 40} L{px - 70} {py + 30} Q{px} {py - 26 - tire * .4} {px + 50} {py + 14} '
             f'L{cx + 30} {cy - 110} L{cx + 70} {cy + 90} L760 {H + 40} Z" fill="{ETOFFE}" {ST} stroke-width="6"/>')
    # les plis tirés vers la pointe
    for dx, dy in ((-150, 170), (-60, 210), (40, 200), (110, 160)):
        o.append(f'<path d="M{px + 4} {py + 16} Q{px + dx * .4:.0f} {py + dy * .5:.0f} {px + dx} {py + dy}" fill="none" '
                 f'stroke="{ENCRE}" stroke-width="3" opacity=".8"/>')
    o.append(f'<path d="M420 {H + 40} L{px - 20} {py + 120}" fill="none" stroke="{MINE}" stroke-width="3" stroke-dasharray="14 10"/>')
    # le revers de la manche
    o.append(f'<path d="M{cx + 30} {cy - 110} Q{cx + 80} {cy - 120} {cx + 110} {cy - 80} L{cx + 140} {cy + 70} '
             f'Q{cx + 110} {cy + 110} {cx + 70} {cy + 90} Z" fill="{LAVIS}" {ST} stroke-width="6"/>')
    # le poignet nu et la main serrée, qui tirent
    wx, wy = cx + 125, cy - 10
    o.append(f'<path d="M{wx} {wy - 70} L{wx + 90} {wy - 30} Q{wx + 110} {wy + 40} {wx + 60} {wy + 70} L{wx + 14} {wy + 70} Z" '
             f'fill="{CLAIR}" {ST} stroke-width="5"/>')
    hx, hy = wx + 96, wy + 10
    o.append(f'<path d="M{hx - 10} {hy - 50} Q{hx + 60} {hy - 64} {hx + 92} {hy - 10} Q{hx + 100} {hy + 50} {hx + 50} {hy + 74} '
             f'Q{hx} {hy + 84} {hx - 30} {hy + 56} Z" fill="{CLAIR}" {ST} stroke-width="5"/>')
    for f in range(4):   # les phalanges repliées
        o.append(f'<path d="M{hx + 30 + f * 4} {hy - 44 + f * 28} q34 4 40 22" fill="none" {ST} stroke-width="3"/>')
    # le fil principal et ses torsades ; la pointe qui prend l'étoffe
    a = math.atan2(665 - 330, 1720 - 200)
    o.append(f'<path d="M140 317 L1780 678" fill="none" stroke="{ENCRE}" stroke-width="7"/>')
    for x in (460, 720, 1240, 1500):
        o.append(pointe(x, 330 + (x - 200) * math.tan(a), a, 34, 6))
    o.append(pointe(px, py, a, 62, 8))
    # la pointe d'en dessous a griffé le poignet : la goutte qui perle (le seul rouge)
    tx, ty = px + 62 * math.cos(math.radians(130) + a), py + 62 * math.sin(math.radians(130) + a)
    if k >= 1:
        o.append(f'<path d="M{wx + 20} {wy - 40} q34 12 70 36" fill="none" stroke="{ROUGE}" stroke-width="5" stroke-linecap="round"/>')
        rg = (0, 13, 19)[k]
        long_ = (0, 0, 24)[k]
        o.append(f'<path d="M{tx:.0f} {ty - 2:.0f} Q{tx + rg:.0f} {ty + rg + long_:.0f} {tx:.0f} {ty + rg * 2 + long_:.0f} '
                 f'Q{tx - rg:.0f} {ty + rg + long_:.0f} {tx:.0f} {ty - 2:.0f} Z" fill="{ROUGE}"/>')
        o.append(f'<circle cx="{tx - rg * .3:.1f}" cy="{ty + rg * 1.1 + long_:.1f}" r="{rg * .25:.1f}" fill="{PAPIER}" opacity=".6"/>')
    return "".join(o)


# --- P3 : le lambeau ---------------------------------------------------------------------------
def lambeau(k: int) -> str:
    """Le lambeau de capote pendu à la pointe (attache à (100, 20)), qui bat au vent."""
    a = (8, -14)[k]
    return (f'<g transform="rotate({a} 100 20)">'
            f'<path d="M92 16 L112 18 L124 70 L140 92 L118 104 L128 150 L104 136 L92 176 L80 128 L58 140 L72 92 L62 60 Z" '
            f'fill="{MINE}" {ST} stroke-width="4"/>'
            f'<path d="M80 128 l-8 24 M104 136 l4 26 M118 104 l14 20 M92 176 l-2 18" {ST} stroke-width="2" fill="none"/>'
            f'<path d="M98 30 L94 120" fill="none" stroke="{MINE}" stroke-width="2.5" stroke-dasharray="8 7"/></g>'
            f'{pointe(100, 20, 0, 13, 3)}')


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    fichiers = {
        "cin_e2-barbeles-brume": svg(brume(), BRUME_W, H),
        "cin_e2-barbeles-course": grille([tobie_course(k) for k in range(3)], 320, 440),
        "cin_e2-barbeles-gros": svg(gros(0)),
        "cin_e2-barbeles-manche": bande([gros(k) for k in range(3)], ZONE_MANCHE),
        "cin_e2-barbeles-lambeau": grille([lambeau(k) for k in range(2)], 200, 220),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"e2_barbeles_foncer : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
