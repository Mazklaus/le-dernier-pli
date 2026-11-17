#!/usr/bin/env python3
"""Génère les planches de la cinématique e2_rites_matthieu (lot 2, planche validée par le GD le
17/11, retouches comprises) : option « Lui rendre ses rites » de e2_sacoche. Tobie pose son pain
dans la sacoche vide de Matthieu, s'agenouille au bord du trou et dit la prière des morts.

  P1, gros plan sur la sacoche ouverte au fond du trou :
  cin_e2-rites-sacoche  le fond 1920 x 1080 : la boue, la sacoche ouverte, la tache de cire
                        noire au fond, la sangle (le prénom brodé n'est pas écrit) ;
  cin_e2-rites-mains    3 images de ZONE_MAINS, en ligne : deux vraies mains sales tiennent le
                        quignon au-dessus (0), le descendent dans la sacoche (1), le lâchent et
                        se retirent (2).
  P2, au bord du trou, de dos :
  cin_e2-rites-trou     le fond : le ciel blanc, l'horizon des piquets, le trou d'obus et la
                        sacoche refermée tout au fond ;
  cin_e2-rites-dos      2 images de ZONE_DOS : Tobie debout (0), agenouillé (1). De dos, le pli
                        et son ruban (à la poitrine) ne se voient pas.
  P3, de près, de trois quarts :
  cin_e2-rites-visage   le fond : le bas du visage sous la capuche, paupières baissées, sans
                        sourire, une trace de boue sur la joue ;
  cin_e2-rites-levres   2 images de ZONE_LEVRES : les lèvres closes (0), entrouvertes (1).

Aucun rouge. Aplats seulement (pas de motifs : les PNG restent légers).

Usage : python3 tools/gen_cin_e2_rites.py
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from gen_cin_epilogues import DEFS_CIN
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER

DST = Path(__file__).resolve().parent.parent / "art" / "src" / "cin"
W, H = 1920, 1080
ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
CLAIR = "#D3CFC2"
BOUE = "#6B665A"
ZONE_MAINS = (460, 0, 1000, 1080)
ZONE_DOS = (180, 180, 760, 900)
ZONE_LEVRES = (1020, 620, 340, 220)


def svg(contenu: str, w: int = W, h: int = H) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{DEFS_CIN}{contenu}</svg>\n')


def bande(images: list[str], zone: tuple[int, int, int, int]) -> str:
    x, y, w, h = zone
    corps = "".join(f'<svg x="{i * w}" y="0" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}">{c}</svg>'
                    for i, c in enumerate(images))
    return svg(corps, w * len(images), h)


def trait(*pts: tuple[float, float], ep: float, fond: str = PAPIER, bord: float = 6) -> str:
    """Un doigt, un membre : un trait épais cerné d'encre."""
    d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    return (f'<path d="{d}" fill="none" stroke="{ENCRE}" stroke-width="{ep + 2 * bord}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{fond}" stroke-width="{ep}" stroke-linecap="round" stroke-linejoin="round"/>')


# --- P1 : la sacoche, les mains, le pain -----------------------------------------------------------
SAC = (700, 1220, 430, 900)       # gauche, droite, haut (bord de l'ouverture), bas


def sacoche_fond() -> str:
    r = random.Random(2201)
    g, d, h, b = SAC
    o = [f'<rect width="{W}" height="{H}" fill="{BOUE}"/>']
    # mottes et flaques de la boue
    for _ in range(46):
        x, y = r.uniform(-40, W + 40), r.uniform(-40, H + 40)
        rx, ry = r.uniform(40, 130), r.uniform(14, 40)
        c = r.choice((LAVIS, MINE, LAVIS))
        o.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="{c}"/>')
    for _ in range(30):
        x, y = r.uniform(0, W), r.uniform(0, H)
        o.append(f'<path d="M{x:.0f} {y:.0f} q{r.uniform(20, 60):.0f} {r.uniform(-12, 12):.0f} {r.uniform(60, 120):.0f} 0" fill="none" stroke="{ENCRE}" stroke-width="3"/>')
    # le rabat renversé vers le haut, la sangle qui en part
    o.append(f'<path d="M{g + 20} {h} L{g + 60} {h - 250} Q{(g + d) / 2} {h - 290} {d - 60} {h - 250} L{d - 20} {h} Z" '
             f'fill="{MINE}" {ST} stroke-width="7"/>')
    o.append(f'<path d="M{g + 70} {h - 30} L{g + 96} {h - 220} Q{(g + d) / 2} {h - 252} {d - 96} {h - 220} L{d - 70} {h - 30}" '
             f'fill="none" stroke="{ENCRE}" stroke-width="3" stroke-dasharray="12 10"/>')
    o.append(f'<path d="M{(g + d) / 2 - 40} {h - 270} L{(g + d) / 2 - 90} -20 M{(g + d) / 2 + 40} {h - 272} L{(g + d) / 2 - 10} -20" '
             f'{ST} stroke-width="7" fill="none"/>')
    o.append(f'<path d="M{(g + d) / 2 - 60} {h - 270} L{(g + d) / 2 - 110} -20 L{(g + d) / 2 - 30} -20 L{(g + d) / 2 + 20} {h - 272} Z" fill="{LAVIS}"/>')
    o.append(f'<path d="M{(g + d) / 2 - 52} {h - 300} L{(g + d) / 2 - 92} 0" stroke="{PAPIER}" stroke-width="3" stroke-dasharray="10 12"/>')
    # le corps de la sacoche, l'intérieur sombre, la cire au fond
    o.append(f'<path d="M{g} {h} Q{(g + d) / 2} {h - 30} {d} {h} L{d + 20} {b - 30} Q{(g + d) / 2} {b + 20} {g - 20} {b - 30} Z" '
             f'fill="{MINE}" {ST} stroke-width="8"/>')
    o.append(f'<path d="M{g + 26} {h + 10} Q{(g + d) / 2} {h - 14} {d - 26} {h + 10} L{d - 40} {h + 220} Q{(g + d) / 2} {h + 250} {g + 40} {h + 220} Z" '
             f'fill="{LAVIS}" {ST} stroke-width="5"/>')
    o.append(f'<path d="M{g + 300} {h + 170} q30 -24 70 -10 q40 -6 56 20 q-4 30 -50 32 q-20 18 -50 4 q-34 -10 -26 -46 Z" fill="{ENCRE}"/>')
    return "".join(o)


def bord_avant() -> str:
    """La lèvre avant de l'ouverture et la face de la sacoche, redessinées par-dessus le pain."""
    g, d, h, b = SAC
    return (f'<path d="M{g + 40} {h + 220} Q{(g + d) / 2} {h + 250} {d - 40} {h + 220} L{d + 20} {b - 30} '
            f'Q{(g + d) / 2} {b + 20} {g - 20} {b - 30} Z" fill="{MINE}" {ST} stroke-width="8"/>'
            f'<path d="M{g + 40} {h + 260} Q{(g + d) / 2} {h + 290} {d - 40} {h + 260}" fill="none" stroke="{ENCRE}" stroke-width="3" stroke-dasharray="12 10"/>'
            f'<rect x="{(g + d) / 2 - 36}" y="{h + 280}" width="72" height="54" rx="8" fill="{LAVIS}" {ST} stroke-width="5"/>')


def pain(cx: float, cy: float, a: float = 0) -> str:
    """Le quignon : la croûte bombée, la mie entamée, des miettes."""
    r = random.Random(2202)
    o = [f'<g transform="rotate({a} {cx} {cy})">',
         f'<path d="M{cx - 150} {cy + 40} Q{cx - 160} {cy - 70} {cx - 30} {cy - 90} Q{cx + 120} {cy - 100} {cx + 150} {cy + 10} '
         f'Q{cx + 150} {cy + 60} {cx + 100} {cy + 70} L{cx - 120} {cy + 74} Q{cx - 150} {cy + 70} {cx - 150} {cy + 40} Z" '
         f'fill="{CLAIR}" {ST} stroke-width="7"/>',
         f'<path d="M{cx - 120} {cy + 74} Q{cx - 150} {cy + 20} {cx - 100} {cy - 20} Q{cx - 70} {cy + 30} {cx - 80} {cy + 74} Z" '
         f'fill="{PAPIER}" {ST} stroke-width="4"/>']
    for i in range(3):
        x = cx - 40 + i * 60
        o.append(f'<path d="M{x} {cy - 70 + i * 4} q30 30 20 70" fill="none" stroke="{ENCRE}" stroke-width="4"/>')
    for _ in range(9):
        x, y = cx - 120 + r.uniform(0, 30), cy + r.uniform(0, 60)
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="3" fill="{MINE}"/>')
    o.append('</g>')
    return "".join(o)


def salete(cx: float, cy: float, graine: int, n: int = 7, rayon: float = 50) -> str:
    """La crasse : des taches de boue sur la peau."""
    r = random.Random(graine)
    o = []
    for _ in range(n):
        x, y = cx + r.uniform(-rayon, rayon), cy + r.uniform(-rayon, rayon)
        o.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r.uniform(6, 18):.0f}" ry="{r.uniform(4, 10):.0f}" '
                 f'fill="{MINE}" transform="rotate({r.uniform(0, 180):.0f} {x:.0f} {y:.0f})"/>')
    return "".join(o)


def main_tenant(cx: float, cy: float, cote: int, graine: int) -> str:
    """Une main qui tient le pain par le côté : le pouce dessus, les doigts repliés dessous.
    cote : le sens vers le pain (+1 pour la main gauche, à gauche du pain ; −1 pour la droite)."""
    s = cote
    o = []
    # la manche de la capote, qui vient du bas de l'écran
    o.append(f'<path d="M{cx - s * 40} {cy + 70} L{cx - s * 180} {H + 40} L{cx + s * 20} {H + 40} L{cx + s * 80} {cy + 100} Z" '
             f'fill="{CLAIR}" {ST} stroke-width="7"/>')
    o.append(f'<path d="M{cx - s * 36} {cy + 110} Q{cx + s * 20} {cy + 140} {cx + s * 92} {cy + 120}" fill="none" {ST} stroke-width="6"/>')
    # la paume, vue de côté
    o.append(f'<path d="M{cx - s * 40} {cy + 110} Q{cx - s * 70} {cy + 10} {cx - s * 10} {cy - 40} Q{cx + s * 50} {cy - 50} {cx + s * 70} {cy - 10} '
             f'Q{cx + s * 90} {cy + 60} {cx + s * 80} {cy + 110} Z" fill="{PAPIER}" {ST} stroke-width="6"/>')
    # les doigts repliés sous le pain (on en voit les phalanges)
    for i in range(4):
        y = cy + 20 + i * 24
        o.append(trait((cx + s * 50, y - 10), (cx + s * 110, y + 4), (cx + s * 120, y + 22), ep=20))
        o.append(f'<ellipse cx="{cx + s * 120:.0f}" cy="{y + 24:.0f}" rx="7" ry="5" fill="{LAVIS}"/>')
    # le pouce, posé sur la croûte
    o.append(trait((cx - s * 5, cy - 30), (cx + s * 60, cy - 70), (cx + s * 112, cy - 74), ep=26))
    o.append(f'<path d="M{cx + s * 104} {cy - 84} q{s * 12} 2 {s * 14} 10" fill="none" stroke="{LAVIS}" stroke-width="6" stroke-linecap="round"/>')
    o.append(salete(cx + s * 20, cy + 30, graine))
    # les jointures, des plis sales
    for i in range(3):
        o.append(f'<path d="M{cx + s * (0 + i * 14)} {cy + 60 + i * 8} q{s * 10} -6 {s * 20} 0" fill="none" stroke="{ENCRE}" stroke-width="3"/>')
    return "".join(o)


def main_ouverte(cx: float, cy: float, cote: int, graine: int) -> str:
    """Une main qui vient de lâcher le pain : la paume vers le bas, les doigts ouverts, tournés vers
    la sacoche (cote : +1 pour la main gauche, −1 pour la droite)."""
    s = cote
    o = [f'<path d="M{cx - s * 40} {cy + 60} L{cx - s * 200} {H + 40} L{cx + s * 70} {H + 40} L{cx + s * 80} {cy + 90} Z" '
         f'fill="{CLAIR}" {ST} stroke-width="7"/>',
         f'<path d="M{cx - s * 46} {cy + 100} Q{cx + s * 10} {cy + 130} {cx + s * 82} {cy + 110}" fill="none" {ST} stroke-width="6"/>',
         f'<path d="M{cx - s * 50} {cy + 90} Q{cx - s * 60} {cy} {cx} {cy - 30} Q{cx + s * 70} {cy - 30} {cx + s * 76} {cy + 30} '
         f'Q{cx + s * 70} {cy + 90} {cx + s * 60} {cy + 100} Z" fill="{PAPIER}" {ST} stroke-width="6"/>']
    for i, (dx, lg, a) in enumerate(((-30, 84, 26), (-6, 106, 36), (20, 102, 46), (44, 80, 56))):
        x0, y0 = cx + s * dx, cy - 22
        x1 = x0 + s * lg * math.sin(math.radians(a))
        y1 = y0 - lg * math.cos(math.radians(a))
        o.append(trait((x0, y0), (x1, y1), ep=22))
        o.append(f'<ellipse cx="{x1:.0f}" cy="{y1 + 4:.0f}" rx="7" ry="5" fill="{LAVIS}"/>')
    o.append(trait((cx - s * 40, cy + 30), (cx - s * 90, cy - 10), (cx - s * 104, cy - 50), ep=24))
    o.append(salete(cx + s * 10, cy + 20, graine))
    return "".join(o)


def plan_mains(k: int) -> str:
    o = [sacoche_fond()]
    g, d, h, _ = SAC
    mx = (g + d) / 2
    if k == 0:
        o.append(pain(mx, 250, -4))
        o.append(main_tenant(mx - 190, 260, 1, 11) + main_tenant(mx + 190, 250, -1, 12))
    elif k == 1:
        o.append(pain(mx, h + 140, 2))
        o.append(bord_avant())
        o.append(main_tenant(mx - 190, h + 150, 1, 11) + main_tenant(mx + 190, h + 146, -1, 12))
    else:
        o.append(pain(mx + 10, h + 190, 6))
        o.append(bord_avant())
        o.append(main_ouverte(mx - 330, 840, 1, 11) + main_ouverte(mx + 330, 850, -1, 12))
    return "".join(o)


# --- P2 : au bord du trou, de dos ------------------------------------------------------------------
TROU = (1180, 780, 640, 200)       # centre, demi-axes
HORIZON = 440


def trou_fond() -> str:
    r = random.Random(2204)
    cx, cy, rx, ry = TROU
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>',
         f'<path d="M0 {HORIZON} Q480 {HORIZON - 14} 960 {HORIZON + 4} T{W} {HORIZON - 6} V{H} H0 Z" fill="{CLAIR}"/>']
    # les piquets et le fil, très loin, avalés par la brume
    for x in range(60, W, 210):
        hx = x + r.uniform(-40, 40)
        o.append(f'<path d="M{hx:.0f} {HORIZON + 4} l{r.uniform(-8, 8):.0f} -{r.uniform(50, 90):.0f}" stroke="{MINE}" stroke-width="6" stroke-linecap="round"/>')
    o.append(f'<path d="M0 {HORIZON - 40} Q300 {HORIZON - 20} 600 {HORIZON - 44} T1200 {HORIZON - 36} T{W} {HORIZON - 42}" fill="none" stroke="{MINE}" stroke-width="2"/>')
    # la terre retournée, ses sillons
    for _ in range(24):
        x, y = r.uniform(0, W), r.uniform(HORIZON + 30, H)
        o.append(f'<path d="M{x:.0f} {y:.0f} q{r.uniform(30, 80):.0f} {r.uniform(-14, 4):.0f} {r.uniform(90, 200):.0f} {r.uniform(-6, 6):.0f}" fill="none" stroke="{MINE}" stroke-width="3"/>')
    # le trou : la lèvre de terre, l'intérieur, l'eau au fond
    o.append(f'<ellipse cx="{cx}" cy="{cy - 10}" rx="{rx + 70}" ry="{ry + 50}" fill="{MINE}"/>')
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{LAVIS}" {ST} stroke-width="7"/>')
    o.append(f'<ellipse cx="{cx + 30}" cy="{cy + 60}" rx="{rx * .5:.0f}" ry="{ry * .36:.0f}" fill="{BOUE}"/>')
    for i in range(7):
        a = math.pi * (0.1 + i * 0.12)
        x0, y0 = cx + rx * math.cos(a + math.pi), cy + ry * math.sin(a + math.pi)
        o.append(f'<path d="M{x0:.0f} {y0:.0f} L{x0 + (cx - x0) * .3:.0f} {y0 + (cy + 40 - y0) * .5:.0f}" stroke="{ENCRE}" stroke-width="3"/>')
    # la sacoche refermée, toute petite au fond
    sx, sy = cx + 40, cy + 60
    o.append(f'<path d="M{sx - 44} {sy - 26} L{sx + 44} {sy - 26} L{sx + 50} {sy + 24} L{sx - 50} {sy + 24} Z" fill="{MINE}" {ST} stroke-width="5"/>')
    o.append(f'<path d="M{sx - 44} {sy - 26} L{sx - 40} {sy} L{sx + 40} {sy} L{sx + 44} {sy - 26}" fill="{LAVIS}" {ST} stroke-width="4"/>')
    # la brume, en bandes plates
    for y, op in ((HORIZON - 70, .55), (HORIZON - 10, .45), (HORIZON + 50, .3)):
        o.append(f'<rect x="0" y="{y}" width="{W}" height="56" fill="{PAPIER}" opacity="{op}"/>')
    return "".join(o)


def tobie_dos(k: int) -> str:
    """Tobie de dos, au bord du trou : debout (0), agenouillé (1). Pieds (ou genoux) à y 1040."""
    cx = 560
    o = []
    if k == 0:
        sol, hanche, epaule, tete = 1040, 760, 470, 360
        # les jambes, les bottes
        o.append(trait((cx - 40, hanche), (cx - 52, sol - 30), ep=46, fond=MINE))
        o.append(trait((cx + 40, hanche), (cx + 54, sol - 30), ep=46, fond=MINE))
        o.append(f'<path d="M{cx - 90} {sol - 40} h76 v46 h-76 Z M{cx + 16} {sol - 40} h76 v46 h-76 Z" fill="{ENCRE}" {ST} stroke-width="6"/>')
        bas = hanche + 110
        bras = [((cx - 130, epaule + 40), (cx - 150, hanche - 40), (cx - 140, hanche + 40)),
                ((cx + 130, epaule + 40), (cx + 150, hanche - 40), (cx + 140, hanche + 40))]
    else:
        sol, hanche, epaule, tete = 1040, 880, 600, 500
        # agenouillé : les jambes repliées vers nous, les semelles des bottes
        o.append(trait((cx - 60, hanche + 40), (cx - 90, sol - 20), ep=50, fond=MINE))
        o.append(trait((cx + 60, hanche + 40), (cx + 90, sol - 20), ep=50, fond=MINE))
        o.append(f'<path d="M{cx - 150} {sol - 50} q30 -14 66 0 l8 70 q-40 12 -78 0 Z M{cx + 84} {sol - 50} q36 -14 66 0 l4 70 q-40 12 -76 0 Z" '
                 f'fill="{ENCRE}" {ST} stroke-width="6"/>')
        bas = sol - 40
        bras = [((cx - 130, epaule + 40), (cx - 120, hanche - 70), (cx - 70, hanche - 20)),
                ((cx + 130, epaule + 40), (cx + 120, hanche - 70), (cx + 70, hanche - 20))]
    # les bras (les mains jointes devant, cachées par le dos quand il est agenouillé)
    for b in bras:
        o.append(trait(*b, ep=44, fond=CLAIR))
    # la capote : le dos, la couture, la ceinture, les pans
    o.append(f'<path d="M{cx - 140} {epaule + 20} Q{cx} {epaule - 30} {cx + 140} {epaule + 20} L{cx + 170} {bas} '
             f'Q{cx} {bas + 30} {cx - 170} {bas} Z" fill="{PAPIER}" {ST} stroke-width="8"/>')
    o.append(f'<path d="M{cx} {epaule} L{cx} {bas + 14}" stroke="{ENCRE}" stroke-width="4"/>')
    o.append(f'<path d="M{cx - 156} {hanche - 40} Q{cx} {hanche - 20} {cx + 156} {hanche - 40}" fill="none" stroke="{ENCRE}" stroke-width="18"/>')
    o.append(f'<path d="M{cx - 90} {epaule + 30} L{cx - 110} {hanche - 50} M{cx + 90} {epaule + 30} L{cx + 110} {hanche - 50}" stroke="{MINE}" stroke-width="3"/>')
    # la sacoche à la hanche (vide de son pain), la lanterne de l'autre côté
    o.append(f'<path d="M{cx - 196} {hanche - 30} h96 l6 100 h-108 Z" fill="{MINE}" {ST} stroke-width="6"/>')
    o.append(f'<path d="M{cx - 196} {hanche - 30} h96 l2 34 h-100 Z" fill="{LAVIS}" {ST} stroke-width="4"/>')
    o.append(f'<path d="M{cx + 120} {epaule + 30} L{cx - 150} {hanche - 30}" stroke="{ENCRE}" stroke-width="7"/>')
    o.append(f'<rect x="{cx + 168}" y="{hanche - 10}" width="40" height="58" rx="5" fill="{CLAIR}" {ST} stroke-width="5"/>')
    o.append(f'<path d="M{cx + 176} {hanche - 10} q12 -24 24 0" fill="none" {ST} stroke-width="4"/>')
    # la capuche, de dos, la tête un peu penchée quand il est à genoux
    pench = 0 if k == 0 else 26
    o.append(f'<path d="M{cx - 110} {epaule + 30} Q{cx - 130} {tete - 60 + pench} {cx - 30} {tete - 110 + pench} '
             f'Q{cx + 20} {tete - 150 + pench} {cx + 60} {tete - 110 + pench} Q{cx + 140} {tete - 40 + pench} {cx + 110} {epaule + 30} '
             f'Q{cx} {epaule + 60} {cx - 110} {epaule + 30} Z" fill="{MINE}" {ST} stroke-width="8"/>')
    for i in range(5):
        x = cx - 70 + i * 34
        o.append(f'<path d="M{x} {tete - 100 + pench + abs(i - 2) * 10} L{x - 10} {epaule + 30}" stroke="{LAVIS}" stroke-width="4"/>')
    return "".join(o)


def plan_dos(k: int) -> str:
    return trou_fond() + tobie_dos(k)


# --- P3 : le bas du visage, de trois quarts ---------------------------------------------------------
def visage_fond() -> str:
    o = [f'<rect width="{W}" height="{H}" fill="{MINE}"/>']
    # le creux sombre de la capuche
    o.append(f'<path d="M440 -20 Q420 600 700 1100 L1640 1100 Q1600 500 1560 -20 Z" fill="{LAVIS}"/>')
    # le cou, le col de la capote
    o.append(f'<path d="M800 840 L760 1100 L1200 1100 L1180 880 Z" fill="{PAPIER}" {ST} stroke-width="7"/>')
    o.append(f'<path d="M600 1100 L700 930 Q960 1010 1260 920 L1420 1100 Z" fill="{CLAIR}" {ST} stroke-width="8"/>')
    o.append(f'<path d="M960 990 L960 1100" stroke="{ENCRE}" stroke-width="5"/>')
    # le visage : joue proche à gauche, profil du nez et du menton à droite
    o.append('<path d="M620 -20 Q590 380 640 560 Q700 800 900 900 Q1060 960 1250 880 Q1300 860 1292 830 '
             'L1268 806 Q1300 790 1300 762 Q1296 744 1308 732 Q1300 712 1314 690 Q1300 660 1296 622 '
             'Q1350 610 1388 576 Q1394 556 1376 540 Q1310 440 1260 352 Q1250 320 1270 280 L1290 -20 Z" '
             f'fill="{PAPIER}" {ST} stroke-width="8"/>')
    # l'aile du nez, la narine
    o.append(f'<path d="M1270 560 Q1240 590 1270 616 Q1300 624 1330 604" fill="none" {ST} stroke-width="6"/>')
    o.append(f'<path d="M1300 600 q14 -8 26 0" fill="none" {ST} stroke-width="5"/>')
    # les paupières baissées : l'œil proche, l'œil lointain, leurs cils
    o.append(f'<path d="M790 370 Q860 344 936 364" fill="none" {ST} stroke-width="5"/>')
    o.append(f'<path d="M786 392 Q860 424 940 390" fill="none" {ST} stroke-width="8"/>')
    for i in range(6):
        x = 800 + i * 24
        o.append(f'<path d="M{x} {402 + abs(i - 2.5) * -3:.0f} l-4 14" {ST} stroke-width="3"/>')
    o.append(f'<path d="M1160 368 Q1196 352 1232 366" fill="none" {ST} stroke-width="4"/>')
    o.append(f'<path d="M1156 388 Q1196 410 1236 386" fill="none" {ST} stroke-width="7"/>')
    for i in range(3):
        o.append(f'<path d="M{1172 + i * 22} 400 l-3 12" {ST} stroke-width="3"/>')
    # les sourcils, sous le bord de la capuche
    o.append(f'<path d="M770 300 Q850 276 950 296" fill="none" stroke="{ENCRE}" stroke-width="12" stroke-linecap="round"/>')
    o.append(f'<path d="M1150 296 Q1200 284 1250 300" fill="none" stroke="{ENCRE}" stroke-width="10" stroke-linecap="round"/>')
    # la joue creusée, la mâchoire, le pli du menton
    o.append(f'<path d="M700 600 Q760 700 830 740" fill="none" stroke="{MINE}" stroke-width="5"/>')
    o.append(f'<path d="M1150 830 Q1200 846 1250 830" fill="none" stroke="{MINE}" stroke-width="5"/>')
    # la boue sur la joue, la cendre qu'on ne voit pas (sous la capuche)
    o.append(salete(760, 520, 2205, n=9, rayon=60))
    o.append(f'<path d="M700 470 l70 10 M712 490 l60 8" stroke="{MINE}" stroke-width="4"/>')
    # le bord de la capuche, qui mange le front en biais
    o.append(f'<path d="M380 -20 L380 250 Q700 180 1000 220 Q1300 250 1600 190 L1600 -20 Z" fill="{MINE}" {ST} stroke-width="10"/>')
    for i in range(9):
        x = 460 + i * 130
        o.append(f'<path d="M{x} -20 L{x + 30} {200 + (i % 3) * 14}" stroke="{LAVIS}" stroke-width="5"/>')
    o.append(f'<path d="M380 250 Q420 700 620 1100" fill="none" {ST} stroke-width="10"/>')
    o.append(f'<path d="M1600 190 Q1560 600 1620 1100" fill="none" {ST} stroke-width="10"/>')
    return "".join(o)


def levres(k: int) -> str:
    """La bouche de trois quarts, coins droits (pas de sourire) : close (0), entrouverte (1)."""
    if k == 0:
        return (f'<path d="M1090 728 Q1150 716 1200 722 Q1250 714 1300 724" fill="none" {ST} stroke-width="9"/>'
                f'<path d="M1120 690 Q1200 676 1290 692" fill="none" stroke="{MINE}" stroke-width="4"/>'
                f'<path d="M1130 770 Q1200 782 1286 764" fill="none" {ST} stroke-width="5"/>')
    return (f'<path d="M1092 726 Q1150 712 1200 718 Q1252 710 1302 722 Q1250 748 1200 750 Q1140 748 1092 726 Z" '
            f'fill="{ENCRE}" {ST} stroke-width="6"/>'
            f'<path d="M1120 690 Q1200 676 1290 692" fill="none" stroke="{MINE}" stroke-width="4"/>'
            f'<path d="M1130 784 Q1200 796 1286 778" fill="none" {ST} stroke-width="5"/>')


def plan_visage(k: int) -> str:
    return visage_fond() + levres(k)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    fichiers = {
        "cin_e2-rites-sacoche": svg(sacoche_fond()),
        "cin_e2-rites-mains": bande([plan_mains(k) for k in range(3)], ZONE_MAINS),
        "cin_e2-rites-trou": svg(trou_fond()),
        "cin_e2-rites-dos": bande([plan_dos(k) for k in range(2)], ZONE_DOS),
        "cin_e2-rites-visage": svg(plan_visage(0)),
        "cin_e2-rites-levres": bande([plan_visage(k) for k in range(2)], ZONE_LEVRES),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"e2_rites_matthieu : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
