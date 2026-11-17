#!/usr/bin/env python3
"""Génère les images de la cinématique e3_danse_rose (lot 1, planche validée par le GD le 17/11) :
Rose entraîne Tobie pour un seul tour maladroit ; elle rit, les rubans de papier tournent.

  cin_e3-danse-rubans    les rubans de papier de la noce qui pendent du bouquet et tournent avec
                         elle : 4 images de 160 x 220, l'attache en (80, 20).
  cin_e3-danse-rire      le gros plan (1920 x 1080) : Rose rit, un vrai visage (retouche du GD :
                         « le seul moment de joie du jeu ») : les yeux plissés par le rire, la
                         bouche ouverte, une mèche qui s'échappe de la coiffe, la couronne de
                         fleurs des champs, le voile ; derrière, les lampions de la noce.
  cin_e3-danse-rires     sa tête, 2 images (ZONE_RIRE) : le rire éclate, puis la tête part en
                         arrière et la mèche suit.
Le jour, la place du village : beaucoup de papier. Aucun rouge (rubans de papier, comme la noce).

Usage : python3 tools/gen_cin_e3_danse.py
"""
from __future__ import annotations

import math
from pathlib import Path

from gen_cin_e1 import bande
from gen_cin_epilogues import DEFS_CIN
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER

DST = Path(__file__).resolve().parent.parent / "art" / "src" / "cin"
W, H = 1920, 1080
ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
CLAIR = "#D3CFC2"
VISAGE = (960, 500)
ZONE_RIRE = (560, 80, 800, 760)


def svg(contenu: str, w: int = W, h: int = H) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{DEFS_CIN}{contenu}</svg>\n')


# --- les rubans ---------------------------------------------------------------------------------------
def rubans(k: int) -> str:
    """Trois rubans de papier qui partent du bouquet ; ils s'envolent du côté où elle tourne et
    reviennent (k 0 à 3 : un tour)."""
    o = []
    for j, (lg, ph) in enumerate(((170, 0.0), (150, 1.1), (190, 2.2))):
        a = math.sin(TAU * k / 4 + ph)
        pts = []
        for i in range(9):
            t = i / 8
            pts.append((80 + a * 60 * t + math.sin(t * 5 + k + j) * 10 * t, 20 + lg * t * (1 - .25 * abs(a))))
        d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
        o.append(f'<path d="{d}" fill="none" stroke="{ENCRE}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
                 f'<path d="{d}" fill="none" stroke="{PAPIER}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    return "".join(o)


TAU = 2 * math.pi


# --- le gros plan --------------------------------------------------------------------------------------
def fond_rire() -> str:
    """La place, le jour : le papier, la guirlande de lampions qui passe derrière elle, hors de net
    (un contour doublé, jamais de flou)."""
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>']
    for dy, op in ((-6, .35), (6, .35), (0, 1)):
        o.append(f'<path d="M-40 {170 + dy} Q960 {330 + dy} {W + 40} {150 + dy}" fill="none" stroke="{MINE if op < 1 else ENCRE}" stroke-width="2.4" opacity="{op}"/>')
    for x in range(40, W, 170):
        t = x / W
        y = (1 - t) ** 2 * 170 + 2 * (1 - t) * t * 330 + t * t * 150
        o.append(f'<path d="M{x - 24} {y + 10:.0f} Q{x} {y - 4:.0f} {x + 24} {y + 10:.0f} L{x + 20} {y + 64:.0f} Q{x} {y + 74:.0f} {x - 20} {y + 64:.0f} Z" '
                 f'fill="{CLAIR}" stroke="{MINE}" stroke-width="2.4"/>'
                 f'<path d="M{x - 26} {y + 37:.0f} Q{x} {y + 46:.0f} {x + 26} {y + 37:.0f}" fill="none" stroke="{MINE}" stroke-width="1.6"/>')
    return "".join(o)


def rose_tete(k: int) -> str:
    """Rose, en buste, de face, qui rit. k 0 : le rire éclate (la bouche grande ouverte, les yeux
    plissés) ; k 1 : la tête part un peu en arrière et de côté, la mèche suit, les épaules montent."""
    x, y = VISAGE
    rot = (0, -5)[k]
    eleve = (0, -10)[k]
    o = []
    # le voile, derrière, qui tombe des deux côtés jusqu'au bas du cadre
    o.append(f'<path d="M{x - 190} {y - 170} Q{x - 330} {y + 120} {x - 360} {H} L{x + 360} {H} Q{x + 330} {y + 120} {x + 190} {y - 170} Z" '
             f'fill="{PAPIER}" {ST} stroke-width="3"/>'
             f'<path d="M{x - 250} {y + 20} Q{x - 290} {y + 300} {x - 300} {H} M{x + 250} {y + 20} Q{x + 290} {y + 300} {x + 300} {H}" fill="none" stroke="{MINE}" stroke-width="2"/>')
    # les épaules, le corsage blanc, le col, le cou
    o.append(f'<path d="M{x - 330} {H} Q{x - 320} {y + 300 + eleve} {x - 120} {y + 250 + eleve} L{x + 120} {y + 250 + eleve} Q{x + 320} {y + 300 + eleve} {x + 330} {H} Z" fill="{PAPIER}" {ST} stroke-width="4"/>'
             f'<path d="M{x - 120} {y + 250 + eleve} Q{x} {y + 330 + eleve} {x + 120} {y + 250 + eleve}" fill="none" {ST} stroke-width="3"/>'
             f'<path d="M{x - 200} {y + 360} Q{x - 210} {y + 450} {x - 196} {H} M{x + 200} {y + 360} Q{x + 210} {y + 450} {x + 196} {H}" fill="none" stroke="{MINE}" stroke-width="2"/>'
             f'<path d="M{x - 60} {y + 160} L{x - 66} {y + 262 + eleve} Q{x} {y + 300 + eleve} {x + 66} {y + 262 + eleve} L{x + 60} {y + 160} Z" fill="{PAPIER}" {ST} stroke-width="3.6"/>'
             f'<path d="M{x - 40} {y + 230} Q{x} {y + 250} {x + 40} {y + 230}" fill="none" stroke="{MINE}" stroke-width="2"/>')
    t = []   # la tête, qui tourne autour du cou
    # les cheveux relevés, derrière le visage (un chignon)
    t.append(f'<path d="M{x - 176} {y - 30} Q{x - 196} {y - 230} {x} {y - 250} Q{x + 196} {y - 230} {x + 176} {y - 30} Q{x + 150} {y - 150} {x} {y - 160} Q{x - 150} {y - 150} {x - 176} {y - 30} Z" '
             f'fill="{LAVIS}" {ST} stroke-width="3.6"/>')
    # les oreilles
    for sg in (-1, 1):
        t.append(f'<path d="M{x + sg * 158} {y - 20} Q{x + sg * 196} {y - 30} {x + sg * 194} {y + 20} Q{x + sg * 190} {y + 60} {x + sg * 156} {y + 52}" fill="{PAPIER}" {ST} stroke-width="3.4"/>'
                 f'<path d="M{x + sg * 170} {y - 6} Q{x + sg * 182} {y + 14} {x + sg * 168} {y + 34}" fill="none" stroke="{ENCRE}" stroke-width="2"/>')
    # le visage : un ovale plein, le menton un peu pointu, les pommettes hautes (le rire les monte)
    t.append(f'<path d="M{x - 160} {y - 70} Q{x - 168} {y + 70} {x - 110} {y + 150} Q{x - 60} {y + 206} {x} {y + 210} Q{x + 60} {y + 206} {x + 110} {y + 150} '
             f'Q{x + 168} {y + 70} {x + 160} {y - 70} Q{x + 120} {y - 170} {x} {y - 176} Q{x - 120} {y - 170} {x - 160} {y - 70} Z" fill="{PAPIER}" {ST} stroke-width="4.4"/>')
    # les cheveux sur le front, partagés par la raie, gonflés aux tempes
    t.append(f'<path d="M{x - 162} {y - 60} Q{x - 150} {y - 150} {x - 8} {y - 168} Q{x - 70} {y - 110} {x - 150} {y - 30} Z" fill="{LAVIS}" {ST} stroke-width="3"/>'
             f'<path d="M{x + 162} {y - 60} Q{x + 150} {y - 150} {x + 8} {y - 168} Q{x + 70} {y - 110} {x + 150} {y - 30} Z" fill="{LAVIS}" {ST} stroke-width="3"/>'
             f'<path d="M{x - 30} {y - 150} Q{x - 90} {y - 120} {x - 140} {y - 60} M{x + 30} {y - 150} Q{x + 90} {y - 120} {x + 140} {y - 60}" fill="none" stroke="{MINE}" stroke-width="1.8"/>')
    # la mèche qui s'échappe de la coiffe et tombe sur la joue (elle suit la tête en k 1)
    mx = (0, 18)[k]
    t.append(f'<path d="M{x + 60} {y - 140} Q{x + 120 + mx} {y - 70} {x + 104 + mx} {y + 10} Q{x + 96 + mx} {y + 50} {x + 118 + mx * 1.4} {y + 80}" '
             f'fill="none" stroke="{ENCRE}" stroke-width="9" stroke-linecap="round"/>'
             f'<path d="M{x + 60} {y - 140} Q{x + 120 + mx} {y - 70} {x + 104 + mx} {y + 10} Q{x + 96 + mx} {y + 50} {x + 118 + mx * 1.4} {y + 80}" '
             f'fill="none" stroke="{LAVIS}" stroke-width="4" stroke-linecap="round"/>')
    # les sourcils levés, arqués par le rire
    for sg in (-1, 1):
        t.append(f'<path d="M{x + sg * 30} {y - 70} Q{x + sg * 74} {y - 104} {x + sg * 120} {y - 80}" fill="none" {ST} stroke-width="5"/>')
    # les yeux plissés : deux arcs vers le haut, les cils, les pattes d'oie du rire
    for sg in (-1, 1):
        ex = x + sg * 72
        t.append(f'<path d="M{ex - 38} {y - 24} Q{ex} {y - 54} {ex + 38} {y - 24}" fill="none" {ST} stroke-width="5"/>'
                 f'<path d="M{ex - 30} {y - 22} Q{ex} {y - 38} {ex + 30} {y - 22}" fill="none" stroke="{ENCRE}" stroke-width="2"/>'
                 + "".join(f'<path d="M{ex + dx} {y - 44 + abs(dx) * .4:.0f} l{dx * .12:.1f} 10" stroke="{ENCRE}" stroke-width="2.2" stroke-linecap="round"/>' for dx in (-24, -10, 6, 20))
                 + f'<path d="M{ex + sg * 46} {y - 30} l{sg * 18} -8 M{ex + sg * 48} {y - 20} l{sg * 20} 2 M{ex + sg * 46} {y - 10} l{sg * 16} 10" stroke="{ENCRE}" stroke-width="2" stroke-linecap="round"/>')
    # le nez, retroussé, et les joues hautes (quelques traits de mine, des taches de son)
    t.append(f'<path d="M{x - 6} {y - 20} Q{x - 14} {y + 30} {x - 24} {y + 46} Q{x - 6} {y + 60} {x + 18} {y + 50}" fill="none" {ST} stroke-width="3.4"/>'
             f'<path d="M{x - 30} {y + 52} q-6 -6 -2 -12 M{x + 24} {y + 48} q6 -6 2 -12" fill="none" stroke="{ENCRE}" stroke-width="2"/>')
    for sg in (-1, 1):
        t.append(f'<path d="M{x + sg * 80} {y + 34} Q{x + sg * 110} {y + 30} {x + sg * 124} {y + 50}" fill="none" stroke="{MINE}" stroke-width="2.4"/>'
                 + "".join(f'<circle cx="{x + sg * dx}" cy="{y + dy}" r="2.4" fill="{MINE}"/>' for dx, dy in ((70, 10), (90, 18), (104, 6), (84, 30), (60, 26))))
    # la bouche ouverte du rire : les lèvres, les dents du haut, la langue, les fossettes
    ouv = (64, 50)[k]
    t.append(f'<path d="M{x - 78} {y + 96} Q{x} {y + 84} {x + 78} {y + 96} Q{x + 60} {y + 96 + ouv * 1.4} {x} {y + 100 + ouv * 1.5} Q{x - 60} {y + 96 + ouv * 1.4} {x - 78} {y + 96} Z" '
             f'fill="{ENCRE}" {ST} stroke-width="4"/>'
             f'<path d="M{x - 62} {y + 98} Q{x} {y + 90} {x + 62} {y + 98} L{x + 56} {y + 116} Q{x} {y + 110} {x - 56} {y + 116} Z" fill="{PAPIER}" {ST} stroke-width="2"/>'
             f'<path d="M{x - 36} {y + 92 + ouv * 1.25} Q{x} {y + 70 + ouv * 1.1} {x + 36} {y + 92 + ouv * 1.25} Q{x} {y + 98 + ouv * 1.4} {x - 36} {y + 92 + ouv * 1.25} Z" fill="{LAVIS}"/>'
             f'<path d="M{x - 84} {y + 92} q-12 6 -10 18 M{x + 84} {y + 92} q12 6 10 18" fill="none" stroke="{ENCRE}" stroke-width="2.6"/>')
    # la couronne de fleurs des champs sur les cheveux : des marguerites, des épis de lavande
    for i in range(11):
        a = math.pi * (1.08 - i * .1)
        fx, fy = x + math.cos(a) * 175, y - 150 - math.sin(a) * 78
        if i % 3 == 1:
            t.append(f'<path d="M{fx:.0f} {fy + 14:.0f} L{fx + 4:.0f} {fy - 30:.0f}" stroke="{ENCRE}" stroke-width="2"/>'
                     + "".join(f'<ellipse cx="{fx + 1 + j:.0f}" cy="{fy - 6 - j * 7:.0f}" rx="4" ry="5" fill="{LAVIS}"/>' for j in range(4)))
        else:
            t.append("".join(f'<ellipse cx="{fx + 15 * math.cos(b):.0f}" cy="{fy + 15 * math.sin(b):.0f}" rx="9" ry="6" transform="rotate({math.degrees(b):.0f} {fx + 15 * math.cos(b):.0f} {fy + 15 * math.sin(b):.0f})" '
                             f'fill="{PAPIER}" {ST} stroke-width="1.8"/>' for b in [m * TAU / 7 for m in range(7)])
                     + f'<circle cx="{fx:.0f}" cy="{fy:.0f}" r="7" fill="{MINE}" {ST} stroke-width="1.8"/>')
    o.append(f'<g transform="translate(0 {eleve}) rotate({rot} {x} {y + 200})">{"".join(t)}</g>')
    return "".join(o)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    fichiers = {
        "cin_e3-danse-rubans": bande([rubans(k) for k in range(4)], (0, 0, 160, 220), 4),
        "cin_e3-danse-rire": svg(fond_rire() + rose_tete(0)),
        "cin_e3-danse-rires": bande([fond_rire() + rose_tete(k) for k in range(2)], ZONE_RIRE, 2),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"e3_danse_rose : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
