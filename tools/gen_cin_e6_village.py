#!/usr/bin/env python3
"""Génère les planches de la cinématique e6_village_sous_terre (lot 1, planche validée par le GD
le 17/11) : au début de e6_tablee, le village dans l'argile et ses fumées, la longue table où
les cuillères font la musique, puis la chaise vide et son écuelle servie.

L'écran de l'étape 6 est inversé (l'écran gravure remappe encre et papier) : on dessine en
encre sur papier comme ailleurs ; la lumière des lanternes est un lavis sombre (claire à
l'écran), la nuit de la terre est le papier (noire à l'écran).

  P1, 0 à 4 s, le village (décor env_e6_plan3_village_01 réemployé, il glisse) :
  cin_e6-village-fumee    3 images de 320 x 300 en ligne, base à (160, 290) : une fumée qui
                          monte du toit et s'écrase sous le plafond de terre.
  P2, 4 à 8 s, la longue table (les gestes lever-cuillere réemployés, assis derrière) :
  cin_e6-village-table    le fond 2400 x 1080 : le mur d'argile, les poteaux, les lanternes ;
  cin_e6-village-plateau  2400 x 460, transparent, le dessus de table à la ligne 80 (posé en
                          y PLATEAU_Y - 80) : de la table
                          (écuelles, pain, cruches), son bord et la nappe qui cachent les jambes.
  P3, 8 à 12 s, la chaise vide :
  cin_e6-village-chaise   1920 x 1080 : la chaise au bout de la table, l'écuelle servie devant,
                          la cuillère posée ; des manches de voisins aux bords du cadre ;
  cin_e6-village-vapeur   3 images de 200 x 280 en ligne, base à (100, 270) : la vapeur de
                          l'écuelle.

Aucun rouge, aucune cloche, rien qui se compte (la table et ses convives débordent du cadre).

Usage : python3 tools/gen_cin_e6_village.py
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
TABLE_W = 2400
PLATEAU_Y = 700
BOL = (960, 760)       # l'écuelle servie, dans le plan de la chaise


def svg(contenu: str, w: int = W, h: int = H) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{DEFS_CIN}{contenu}</svg>\n')


def grille(images: list[str], w: int, h: int) -> str:
    corps = "".join(f'<g transform="translate({i * w} 0)">{c}</g>' for i, c in enumerate(images))
    return svg(corps, w * len(images), h)


def lueur(x: float, y: float, r: float, op: float = .12) -> str:
    """Le halo d'une lanterne : des cercles de lavis (clairs à l'écran)."""
    return "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r * f:.0f}" fill="{LAVIS}" opacity="{op}"/>' for f in (1, .7, .45))


def lanterne(x: float, y: float, s: float = 1.0) -> str:
    return (lueur(x, y + 30 * s, 150 * s) +
            f'<path d="M{x} {y - 40 * s} V{y}" {ST} stroke-width="{2 * s}"/>'
            f'<path d="M{x - 14 * s} {y} h{28 * s} l{4 * s} {40 * s} h{-36 * s} Z" fill="{LAVIS}" {ST} stroke-width="{3 * s}"/>')


def plafond(w: int, y: float, r: random.Random) -> str:
    """Le plafond de terre, et ses racines qui pendent."""
    d = f"M0 {y}"
    x = 0
    while x < w:
        x += r.uniform(80, 180)
        d += f" L{x:.0f} {y + r.uniform(-14, 14):.0f}"
    o = [f'<path d="{d} V0 H0 Z" fill="url(#terre)" {ST} stroke-width="3"/>']
    for _ in range(w // 60):
        xx = r.uniform(0, w)
        o.append(f'<path d="M{xx:.0f} {y - 4} q{r.uniform(-8, 8):.0f} {r.uniform(20, 40):.0f} {r.uniform(-4, 4):.0f} {r.uniform(30, 70):.0f}" '
                 f'fill="none" {ST} stroke-width="2"/>')
    return "".join(o)


# --- P1 : la fumée ------------------------------------------------------------------------------
def fumee(k: int) -> str:
    """Une colonne de fumée qui ondule (k : la phase), et s'étale sous le plafond (en haut)."""
    o = []
    for brin in range(3):
        d = f"M{150 + brin * 10} 290"
        for j in range(1, 8):
            y = 290 - j * 34
            x = 160 + math.sin(j * .9 + k * 2.1 + brin) * (6 + j * 3) + (brin - 1) * (4 + j * 2)
            d += f" T{x:.0f} {y}"
        o.append(f'<path d="{d}" fill="none" {ST} stroke-width="{3 - brin * .6:.1f}" opacity="{.9 - brin * .2:.1f}"/>')
    # la nappe qui s'étale sous le plafond
    dx = (0, 14, 28)[k]
    o.append(f'<path d="M{40 + dx} 40 Q160 {10 + dx / 4} {280 - dx / 2} 36 Q200 52 160 50 Q110 54 {40 + dx} 40 Z" fill="{LAVIS}" opacity=".3" {ST} stroke-width="2"/>')
    o.append(f'<ellipse cx="160" cy="{150 - k * 6}" rx="{36 + k * 4}" ry="70" fill="{LAVIS}" opacity=".18"/>')
    return "".join(o)


# --- P2 : la table ------------------------------------------------------------------------------
def table() -> str:
    r = random.Random(6061)
    w = TABLE_W
    o = [f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>', plafond(w, 170, r)]
    # le mur d'argile, des maisons basses dans la pénombre
    for x in range(120, w, 520):
        o.append(f'<path d="M{x} 640 V420 Q{x + 120} 380 {x + 240} 420 V640" fill="none" {ST} stroke-width="3" opacity=".6"/>'
                 f'<rect x="{x + 90}" y="470" width="60" height="50" fill="{LAVIS}" {ST} stroke-width="3" opacity=".7"/>')
    # les poteaux et leurs jambes de force
    for x in range(60, w, 400):
        o.append(f'<path d="M{x} 180 V700 M{x - 60} 186 L{x} 246 L{x + 60} 186" fill="none" {ST} stroke-width="8"/>')
    # les lanternes au-dessus de la table, leurs halos
    for x in range(260, w, 330):
        o.append(lanterne(x, 300 + (x % 3) * 18))
    # la grande lueur posée sur la table
    o.append(f'<ellipse cx="{w / 2}" cy="{PLATEAU_Y + 40}" rx="{w * .55:.0f}" ry="260" fill="{LAVIS}" opacity=".16"/>')
    return "".join(o)


def plateau() -> str:
    """Le dessus de la table, son bord, la nappe ; transparent au-dessus du plateau."""
    r = random.Random(6062)
    w = TABLE_W
    o = [f'<path d="M-20 40 H{w + 20} V60 H-20 Z" fill="{PAPIER}" {ST} stroke-width="4"/>',
         f'<path d="M-20 60 H{w + 20} V460 H-20 Z" fill="{PAPIER}" {ST} stroke-width="4"/>']
    for y in range(230, 460, 46):   # les planches du devant de la table
        o.append(f'<path d="M-20 {y} H{w + 20}" stroke="{MINE}" stroke-width="2"/>')
    # la nappe qui retombe en plis
    x = -20
    d = "M-20 60"
    while x < w + 20:
        x += r.uniform(60, 110)
        d += f" L{x:.0f} {r.uniform(150, 190):.0f}"
    o.append(f'<path d="{d} L{w + 20} 60 Z" fill="{PAPIER}" {ST} stroke-width="3"/>')
    # les écuelles, le pain, les cruches : sans ordre, rien qui se compte
    x = r.uniform(20, 80)
    while x < w:
        kind = r.random()
        if kind < .55:
            o.append(f'<path d="M{x - 34:.0f} 38 Q{x:.0f} 64 {x + 34:.0f} 38 Z" fill="{LAVIS}" {ST} stroke-width="3"/>'
                     f'<ellipse cx="{x:.0f}" cy="38" rx="34" ry="7" fill="{PAPIER}" {ST} stroke-width="2.5"/>')
        elif kind < .8:
            o.append(f'<path d="M{x - 40:.0f} 40 Q{x - 36:.0f} 10 {x:.0f} 8 Q{x + 36:.0f} 10 {x + 40:.0f} 40 Z" fill="{MINE}" {ST} stroke-width="3"/>'
                     f'<path d="M{x - 20:.0f} 20 l10 8 M{x:.0f} 14 l10 8 M{x + 18:.0f} 20 l8 8" {ST} stroke-width="2"/>')
        else:
            o.append(f'<path d="M{x - 18:.0f} 40 Q{x - 24:.0f} 0 {x - 10:.0f} -24 H{x + 10:.0f} Q{x + 24:.0f} 0 {x + 18:.0f} 40 Z" fill="{PAPIER}" {ST} stroke-width="3"/>'
                     f'<path d="M{x + 16:.0f} -10 q16 6 6 24" fill="none" {ST} stroke-width="3"/>')
        x += r.uniform(110, 190)
    return svg("".join(o), w, 460).replace('viewBox="0 0 2400 460"', 'viewBox="0 -40 2400 460"')


# --- P3 : la chaise vide ------------------------------------------------------------------------
def chaise() -> str:
    r = random.Random(6063)
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>', plafond(W, 90, r),
         lueur(960, 330, 520, .1), lanterne(560, 170, 1.1), lanterne(1400, 150, .9)]
    # la chaise, de face, au bout de la table : un dossier à barreaux, haute, vide
    cx = 960
    o.append(f'<path d="M{cx - 150} 720 V250 M{cx + 150} 720 V250" fill="none" {ST} stroke-width="12"/>')
    o.append(f'<path d="M{cx - 160} 250 H{cx + 160} M{cx - 150} 330 H{cx + 150}" fill="none" {ST} stroke-width="10"/>')
    for x in (-75, 0, 75):
        o.append(f'<path d="M{cx + x} 330 V560" {ST} stroke-width="6"/>')
    o.append(f'<path d="M{cx - 180} 560 H{cx + 180} L{cx + 160} 600 H{cx - 160} Z" fill="{PAPIER}" {ST} stroke-width="6"/>')
    # la table devant, en bas du cadre
    o.append(f'<path d="M-20 700 H{W + 20} V{H + 20} H-20 Z" fill="{PAPIER}" {ST} stroke-width="6"/>')
    o.append(f'<path d="M-20 720 H{W + 20}" {ST} stroke-width="3"/>')
    for k in range(9):
        y = 760 + k * 36
        o.append(f'<path d="M-20 {y} Q960 {y + r.uniform(-6, 6):.0f} {W + 20} {y}" fill="none" stroke="{MINE}" stroke-width="2"/>')
    # l'écuelle servie, pleine (la soupe est un lavis : claire à l'écran), la cuillère posée
    bx, by = BOL
    o.append(lueur(bx, by, 260, .08))
    o.append(f'<path d="M{bx - 170} {by - 20} Q{bx} {by + 150} {bx + 170} {by - 20} Z" fill="{PAPIER}" {ST} stroke-width="6"/>')
    o.append(f'<ellipse cx="{bx}" cy="{by - 20}" rx="170" ry="34" fill="{PAPIER}" {ST} stroke-width="5"/>')
    o.append(f'<ellipse cx="{bx}" cy="{by - 16}" rx="148" ry="24" fill="{LAVIS}" opacity=".75"/>')
    o.append(f'<path d="M{bx + 210} {by + 60} L{bx + 420} {by + 20}" {ST} stroke-width="10"/>'
             f'<ellipse cx="{bx + 196}" cy="{by + 64}" rx="30" ry="16" fill="{PAPIER}" {ST} stroke-width="5"/>')
    # le pain, à gauche
    o.append(f'<path d="M{bx - 480} {by + 60} Q{bx - 470} {by - 20} {bx - 360} {by - 24} Q{bx - 250} {by - 20} {bx - 240} {by + 60} Z" '
             f'fill="{MINE}" {ST} stroke-width="5"/>'
             f'<path d="M{bx - 430} {by} l20 16 M{bx - 370} {by - 10} l20 16 M{bx - 310} {by} l18 16" {ST} stroke-width="4"/>')
    # les manches des voisins aux bords : une main qui tient sa cuillère, une main posée
    o.append(f'<path d="M-40 560 L260 690 L230 780 L-40 700 Z" fill="{LAVIS}" {ST} stroke-width="6"/>'
             f'<path d="M250 690 q40 -10 60 20 q10 30 -20 50 q-30 10 -60 -10 Z" fill="{PAPIER}" {ST} stroke-width="5"/>'
             f'<path d="M300 700 L360 600" {ST} stroke-width="8"/><ellipse cx="366" cy="588" rx="18" ry="12" fill="{PAPIER}" {ST} stroke-width="4"/>')
    o.append(f'<path d="M{W + 40} 600 L{W - 280} 720 L{W - 250} 810 L{W + 40} 740 Z" fill="{LAVIS}" {ST} stroke-width="6"/>'
             f'<path d="M{W - 270} 720 q-50 0 -66 30 q-6 30 30 46 q40 6 60 -14 Z" fill="{PAPIER}" {ST} stroke-width="5"/>')
    return "".join(o)


def vapeur(k: int) -> str:
    o = []
    for brin in range(3):
        x0 = 60 + brin * 40
        d = f"M{x0} 270"
        for j in range(1, 7):
            y = 270 - j * 40
            x = x0 + math.sin(j * 1.1 + k * 2.1 + brin * 1.7) * (6 + j * 4)
            d += f" T{x:.0f} {y}"
        o.append(f'<path d="{d}" fill="none" {ST} stroke-width="3" opacity="{.85 - brin * .15:.2f}"/>')
    return "".join(o)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    fichiers = {
        "cin_e6-village-fumee": grille([fumee(k) for k in range(3)], 320, 300),
        "cin_e6-village-table": svg(table(), TABLE_W, H),
        "cin_e6-village-plateau": plateau(),
        "cin_e6-village-chaise": svg(chaise()),
        "cin_e6-village-vapeur": grille([vapeur(k) for k in range(3)], 200, 280),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"e6_village_sous_terre : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
