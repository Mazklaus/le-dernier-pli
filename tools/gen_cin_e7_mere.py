#!/usr/bin/env python3
"""Génère les planches de la cinématique e7_mere_cloche (lot 1, planche validée par le GD le
17/11) : au début de e7_mere_cloche, la salle ronde sous la grande cloche (travelling avant),
la Mère-Cloche qui lève la tête, les yeux clos, puis le contrechamp : Tobie, petit, sous la
bouche noire de la cloche. Rien n'est montré dans la cloche.

  P1, 0 à 3 s : décor env_e7_plan3_mere-cloche_01 réemployé (pas de planche).
  P2, 3 à 7 s, de près (le dessin du PNJ, gen_chr_pnj_e7, comme dans l'épilogue a) :
  cin_e7-mere-gros    le fond 1920 x 1080 : la lèvre de bronze en arc au-dessus, le sol de
                      pierre et ses coulures de cire noire, la lampe ; elle, la tête baissée ;
  cin_e7-mere-tete    3 images de ZONE_TETE en ligne : 0 la tête baissée, 1 elle la lève,
                      2 levée vers lui ; les yeux toujours clos.
  P3, 7 à 10 s, contrechamp :
  cin_e7-mere-bouche  1920 x 1080 : la bouche de la grande cloche vue d'en bas, immense, un
                      aplat noir sans rien dedans ; le sol rond ; Tobie y est posé par la ciné
                      (planche de repos), pieds en PIEDS_TOBIE.

Aucun rouge dans ces planches (le ruban de Tobie est son calque _red, posé par la ciné), aucune
cloche qui bouge.

Usage : python3 tools/gen_cin_e7_mere.py
"""
from __future__ import annotations

import random
from pathlib import Path

from gen_chr_pnj_e7 import M_EPAULE_D, M_EPAULE_G, agrandie, bras_mere, corps_mere, main_lisante, tete_mere
from gen_cin_epilogues import DEFS_CIN
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER

DST = Path(__file__).resolve().parent.parent / "art" / "src" / "cin"
W, H = 1920, 1080
ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
K = 2.6
VISAGE = (960, 400)
OX, OY = VISAGE[0] - 125.6 * K, VISAGE[1] - 98.4 * K
ZONE_TETE = (700, 140, 520, 460)
SOL = 900
LAMPE = (500, 740)
PIEDS_TOBIE = (960, 960)
# la tête qui se lève : (décalage vertical, écrasement) dans le repère du PNJ
TETES = [(9.0, .84), (4.0, .92), (-2.0, 1.0)]


def svg(contenu: str, w: int = W, h: int = H) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{DEFS_CIN}{contenu}</svg>\n')


def bande(images: list[str], zone: tuple[int, int, int, int]) -> str:
    x, y, w, h = zone
    corps = "".join(f'<svg x="{i * w}" y="0" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}">{c}</svg>'
                    for i, c in enumerate(images))
    return svg(corps, w * len(images), h)


def coulures(r: random.Random, y: float, n: int) -> str:
    o = []
    for _ in range(n):
        cx = r.choice((r.uniform(60, 640), r.uniform(1280, 1860)))
        o.append(f'<path d="M{cx:.0f} {y + r.uniform(10, 120):.0f} q{r.uniform(10, 30):.0f} -6 {r.uniform(30, 80):.0f} 2 q-10 14 -30 10 Z" fill="{ENCRE}"/>')
    return "".join(o)


def lampe() -> str:
    """La petite lampe à huile sur sa pierre, éteinte, un fil de fumée (comme dans l'épilogue a)."""
    x, y = LAMPE
    return (f'<path d="M{x - 70} {y + 40} H{x + 80} L{x + 70} {y + 170} H{x - 60} Z" fill="{LAVIS}" {ST} stroke-width="3"/>'
            f'<path d="M{x - 34} {y + 30} Q{x} {y + 46} {x + 34} {y + 30} Q{x + 30} {y + 6} {x} {y + 4} Q{x - 30} {y + 6} {x - 34} {y + 30} Z" fill="url(#h2)" {ST} stroke-width="3"/>'
            f'<path d="M{x + 26} {y + 16} Q{x + 50} {y + 6} {x + 44} {y + 26}" fill="none" {ST} stroke-width="3"/>'
            f'<path d="M{x - 2} {y + 4} v-14" {ST} stroke-width="3"/>'
            f'<path d="M{x - 2} {y - 12} q-8 -20 2 -40 t-2 -44" fill="none" stroke="{MINE}" stroke-width="2"/>')


def dessous() -> str:
    r = random.Random(7071)
    return (f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>'
            f'<path d="M-40 330 Q960 -110 {W + 40} 330 L{W + 40} -10 L-40 -10 Z" fill="{LAVIS}" {ST} stroke-width="5"/>'
            f'<path d="M200 190 Q960 -40 1720 190 M500 90 Q960 0 1420 90" fill="none" stroke="{MINE}" stroke-width="2"/>'
            f'<path d="M-40 360 Q960 -80 {W + 40} 360" fill="none" {ST} stroke-width="2"/>'
            f'<path d="M0 {SOL} H{W}" {ST} stroke-width="3"/>'
            f'<rect y="{SOL}" width="{W}" height="{H - SOL}" fill="{LAVIS}" opacity=".6"/>'
            + coulures(r, SOL, 12) + lampe())


def mere(k: int) -> str:
    """La Mère-Cloche assise, ses mains sur l'éclat ; k : la tête (0 baissée à 2 levée)."""
    dy, sy = TETES[k]
    (gx, gy), (dx, dy_m) = (80, 293), (112, 291)
    bras = (f'<g {ST}>' + bras_mere(M_EPAULE_G, (94, 262), (gx, gy)) + main_lisante(gx, gy)
            + bras_mere(M_EPAULE_D, (148, 262), (dx, dy_m)) + main_lisante(dx, dy_m) + '</g>')
    cou = 206 + 18
    tete = (f'<g transform="translate(0 {dy}) translate(124 {cou}) scale(1 {sy}) translate(-124 {-cou})">'
            f'{tete_mere()}</g>')
    dessin = agrandie(corps_mere(0, grave=1.0) + bras + tete)
    return f'<g transform="translate({OX:.1f} {OY:.1f}) scale({K})">{dessin}</g>'


def bouche() -> str:
    """Le contrechamp : la bouche de la grande cloche, d'en bas, qui remplit le haut du cadre ;
    dedans, un aplat d'encre et rien d'autre. Le sol rond de pierre, la cire."""
    r = random.Random(7072)
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>',
         # le mur rond de la salle, au loin
         f'<path d="M-40 760 Q960 640 {W + 40} 760 V{H} H-40 Z" fill="{CLAIR_SOL}"/>',
         # la cloche : sa robe de bronze qui descend des deux côtés, la lèvre épaisse, le noir dedans
         f'<path d="M-200 -40 L-120 520 Q960 760 {W + 120} 520 L{W + 200} -40 Z" fill="{LAVIS}" {ST} stroke-width="6"/>',
         f'<path d="M-100 470 Q960 700 {W + 100} 470 Q960 610 -100 470 Z" fill="{ENCRE}"/>',
         f'<path d="M-120 520 Q960 760 {W + 120} 520" fill="none" {ST} stroke-width="10"/>',
         f'<path d="M-110 490 Q960 715 {W + 110} 490" fill="none" stroke="{MINE}" stroke-width="3"/>',
         f'<path d="M-160 200 Q960 380 {W + 160} 200 M-140 340 Q960 540 {W + 140} 340" fill="none" stroke="{MINE}" stroke-width="2.5" opacity=".7"/>',
         # le sol
         f'<path d="M0 {SOL + 40} Q960 {SOL - 20} {W} {SOL + 40}" fill="none" {ST} stroke-width="3"/>']
    for k in range(7):
        y = SOL + 70 + k * 26
        o.append(f'<path d="M0 {y} Q960 {y - 30 + k * 4} {W} {y}" fill="none" stroke="{MINE}" stroke-width="1.6"/>')
    o.append(coulures(r, SOL + 20, 14))
    # l'ombre portée de Tobie, sous ses pieds
    o.append(f'<ellipse cx="{PIEDS_TOBIE[0]}" cy="{PIEDS_TOBIE[1] - 4}" rx="70" ry="10" fill="{LAVIS}" opacity=".5"/>')
    return "".join(o)


CLAIR_SOL = "#D3CFC2"


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    fichiers = {
        "cin_e7-mere-gros": svg(dessous() + mere(0)),
        "cin_e7-mere-tete": bande([dessous() + mere(k) for k in range(3)], ZONE_TETE),
        "cin_e7-mere-bouche": svg(bouche()),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"e7_mere_cloche : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
