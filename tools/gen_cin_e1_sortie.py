#!/usr/bin/env python3
"""Génère les plans dessinés de la cinématique e1_sortie_tranchee (retouche du GD) : après la
montée à l'échelle (jouée dans le décor, la caméra qui suit Tobie vers le haut), on le voit
franchir le parapet à contre-jour sur une aube pâle, puis un dernier temps bref sur Lamarre qui
baisse la tête.

  Plan B, le parapet, vu d'en bas, de la tranchée :
  cin_sortie_01  le fond 1920 x 1080 : l'aube pâle au-dessus du No Man's Land (piquets,
                 barbelés au loin), le parapet de sacs, le haut de l'échelle ; personne
                 (l'image 4 : il est passé) ;
  cin_sortie_02  4 images de ZONE_B, grille 2 x 2 : Tobie en silhouette noire à contre-jour,
                 0 la tête et les mains sur les sacs ; 1 un genou sur le parapet ; 2 accroupi
                 dessus, penché vers l'avant ; 3 il bascule de l'autre côté, on ne voit plus
                 que ses jambes. À 0,3 s l'image, puis le fond seul (tenue).
  Plan C, Lamarre au pied de l'échelle, de près :
  cin_sortie_03  le fond 1920 x 1080 : le sergent en buste devant les sacs, qui regarde en
                 haut (image 0) ;
  cin_sortie_04  2 images de ZONE_C, en ligne : 0 il regarde en haut ; 1 il baisse la tête,
                 le bord du casque lui cache les yeux.

Aucun rouge : Tobie est une silhouette à contre-jour (le ruban ne se voit pas).

Usage : python3 tools/gen_cin_e1_sortie.py
"""
from __future__ import annotations

import re

from gen_cin_e1 import DST, H, ROOT, W, bande, svg
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER, rnd

ZONE_B = (780, 360, 420, 560)
ZONE_C = (640, 60, 640, 560)
PARAPET = 640
ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
SOURCE_PNJ = ROOT / "tools" / "donnees" / "pnj_e1.svgfrag"


# ----------------------------------------------------------------------------- plan B
def aube() -> str:
    """Le ciel pâle (papier nu), une bande de brume claire à l'horizon, le No Man's Land au loin
    au-dessus du parapet : piquets tordus, fils de fer, un arbre cassé."""
    r = rnd(71)
    out = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>']
    for k, (y, op) in enumerate([(470, .10), (500, .14), (530, .2), (560, .26)]):
        out.append(f'<rect x="0" y="{y}" width="{W}" height="{40 + k * 6}" fill="{MINE}" opacity="{op}"/>')
    out.append(f'<path d="M0 {PARAPET - 40} Q480 {PARAPET - 70} 960 {PARAPET - 52} T1920 {PARAPET - 60} V{PARAPET + 20} H0 Z" fill="{LAVIS}" opacity=".35"/>')
    x = r.uniform(-40, 40)
    while x < W:
        h = r.uniform(30, 70)
        y = PARAPET - 50 + r.uniform(-6, 6)
        out.append(f'<path d="M{x:.0f} {y:.0f} l{r.uniform(-8, 8):.0f} {-h:.0f}" {ST} stroke-width="3" opacity=".6"/>')
        x += r.uniform(90, 200)
    for k in range(3):
        y0 = PARAPET - 80 + k * 12
        d = f"M0 {y0}"
        x = 0
        while x < W:
            x += r.uniform(60, 120)
            d += f" Q{x - 40:.0f} {y0 + r.uniform(8, 18):.0f} {x:.0f} {y0 + r.uniform(-4, 4):.0f}"
        out.append(f'<path d="{d}" fill="none" stroke="{ENCRE}" stroke-width="1.2" opacity=".5"/>')
    out.append(f'<path d="M1500 {PARAPET - 50} L1494 {PARAPET - 210} L1470 {PARAPET - 250} M1495 {PARAPET - 150} L1540 {PARAPET - 190}" '
               f'fill="none" {ST} stroke-width="6" opacity=".6"/>')
    return "".join(out)


def parapet() -> str:
    """Le parapet de sacs vu d'en bas, qui ferme le bas de l'image ; le haut de l'échelle."""
    r = rnd(72)
    out = []
    y = PARAPET
    rang = 0
    while y < H + 40:
        x = -r.uniform(0, 80) - (60 if rang % 2 else 0)
        while x < W:
            l = r.uniform(130, 170)
            out.append(f'<path d="M{x + 6:.0f} {y + 4:.0f} Q{x + l / 2:.0f} {y - 10:.0f} {x + l - 6:.0f} {y + 4:.0f} '
                       f'Q{x + l + 6:.0f} {y + 40:.0f} {x + l - 6:.0f} {y + 70:.0f} Q{x + l / 2:.0f} {y + 82:.0f} {x + 6:.0f} {y + 70:.0f} '
                       f'Q{x - 6:.0f} {y + 40:.0f} {x + 6:.0f} {y + 4:.0f} Z" fill="{PAPIER}" {ST} stroke-width="3"/>'
                       f'<path d="M{x + 14:.0f} {y + 56:.0f} Q{x + l / 2:.0f} {y + 70:.0f} {x + l - 14:.0f} {y + 56:.0f}" fill="none" stroke="{MINE}" stroke-width="2"/>')
            x += l
        y += 72
        rang += 1
    # le haut de l'échelle, appuyé au parapet
    out.append(f'<path d="M900 {H} L916 {PARAPET - 70} M1020 {H} L1004 {PARAPET - 70}" {ST} stroke-width="14"/>')
    for k in range(6):
        yy = PARAPET - 40 + k * 80
        out.append(f'<path d="M{912 - k * 2} {yy} H{1008 + k * 2}" {ST} stroke-width="9"/>')
    return "".join(out)


def membre(*pts: tuple[float, float], ep: float = 30) -> str:
    """Un bras ou une jambe : un trait épais aux bouts ronds, en noir."""
    d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    return f'<path d="{d}" fill="none" stroke="{ENCRE}" stroke-width="{ep:.0f}" stroke-linecap="round" stroke-linejoin="round"/>'


def tete(x: float, y: float, a: float = 0) -> str:
    """La tête sous la capuche, vue de dos, (x, y) le centre ; a : penchée (degrés)."""
    return (f'<g transform="rotate({a} {x} {y})"><path d="M{x - 36} {y + 30} Q{x - 44} {y - 30} {x} {y - 46} Q{x + 44} {y - 30} {x + 36} {y + 30} '
            f'Q{x} {y + 44} {x - 36} {y + 30} Z" fill="{ENCRE}"/><path d="M{x - 6} {y - 46} Q{x + 14} {y - 62} {x + 22} {y - 40}" fill="{ENCRE}"/></g>')


def buste(x0: float, y0: float, x1: float, y1: float, larg: float = 120) -> str:
    """Le dos de la capote, des épaules (x0, y0) aux hanches (x1, y1) ; la sacoche à la hanche."""
    return (f'<path d="M{x0 - larg / 2:.0f} {y0:.0f} Q{x0:.0f} {y0 - 22:.0f} {x0 + larg / 2:.0f} {y0:.0f} L{x1 + larg * .46:.0f} {y1:.0f} '
            f'L{x1 - larg * .46:.0f} {y1:.0f} Z" fill="{ENCRE}" stroke="{ENCRE}" stroke-width="10" stroke-linejoin="round"/>'
            f'<path d="M{x1 + larg * .3:.0f} {y1 - 70:.0f} h52 v60 h-52 Z" fill="{ENCRE}" stroke="{ENCRE}" stroke-width="6" stroke-linejoin="round"/>')


def tobie_ombre(k: int) -> str:
    """Tobie de dos, en silhouette noire à contre-jour, qui franchit le parapet (k 0 à 3)."""
    p = PARAPET
    if k == 0:   # en haut de l'échelle : la tête et le buste dépassent, les mains sur les sacs
        o = [membre((920, 900), (912, 800), (924, 720)), membre((1000, 860), (1006, 780), (994, 720)),
             buste(960, 520, 960, 730), tete(960, 470),
             membre((910, 530), (860, 600), (842, p - 6), ep=26), membre((1010, 530), (1062, 600), (1080, p - 6), ep=26)]
    elif k == 1:   # un genou sur le parapet, l'autre pied sur le dernier barreau, penché en avant
        o = [membre((930, 760), (920, 690), (950, 640)), membre((1004, 640), (1060, 610), (1110, p - 14)),
             buste(990, 470, 975, 650, 116), tete(1000, 420, 12),
             membre((945, 480), (900, 540), (880, p - 10), ep=26), membre((1040, 480), (1100, 520), (1150, p - 12), ep=26)]
    elif k == 2:   # accroupi sur les sacs, ramassé, prêt à basculer de l'autre côté
        o = [membre((900, p - 10), (930, 560), (980, 590)), membre((1050, p - 10), (1020, 560), (970, 590)),
             buste(980, 470, 975, 590, 130), tete(985, 440, 24),
             membre((930, 480), (900, 560), (910, p - 10), ep=24), membre((1040, 480), (1070, 560), (1060, p - 10), ep=24)]
    else:   # il a basculé : on ne voit plus que ses jambes, les semelles en l'air, qui glissent
        o = [membre((930, p + 6), (950, 570), (990, 540), ep=28), membre((1000, p + 6), (1020, 590), (1060, 570), ep=28),
             f'<path d="M972 520 l40 12 l-10 22 l-40 -12 Z" fill="{ENCRE}"/>',
             f'<path d="M1046 552 l38 14 l-10 22 l-38 -14 Z" fill="{ENCRE}"/>']
    return "".join(o)


def image_b(k: int) -> str:
    """Le parapet, Tobie à l'image k (0 à 3), personne à l'image 4 : il est sur l'échelle, entre
    nous et les sacs ; ce qui dépasse du parapet se découpe sur l'aube."""
    s = aube() + parapet()
    if k < 4:
        s += tobie_ombre(k)
    return s


# ----------------------------------------------------------------------------- plan C
def lamarre(k: int) -> str:
    """Le sergent Lamarre en buste (le dessin de sa planche, agrandi), devant les sacs de la
    tranchée ; k 0 il regarde en haut, 1 il baisse la tête sous le bord du casque."""
    src = SOURCE_PNJ.read_text(encoding="utf-8")
    defs = re.search(r"<defs>.*?</defs>", src, re.S).group(0)
    groupe = re.search(r'<g id="p-lamarre".*?\n    </g>', src, re.S).group(0)
    corps, tete = groupe.split("<!-- tête carrée -->")
    corps = corps.replace('id="p-lamarre"', 'id="lamarre-corps"', 1) + "</g>"
    tete = tete.replace("</g>", "").rstrip()
    if k == 1:
        # les sourcils et les yeux disparaissent sous le bord du casque, la moustache tombe
        tete = re.sub(r'<path d="M104 80 L116 82 M124 82 L136 80"[^>]*/>', "", tete)
        tete = re.sub(r'<path d="M108 87 L114 87 M126 87 L132 87"[^>]*/>', "", tete)
        tete = f'<g transform="translate(0 7) translate(120 108) scale(1 .9) translate(-120 -108)">{tete}</g>'
    else:
        # les yeux levés : les sourcils remontent, une pupille en haut de chaque œil
        tete = tete.replace('d="M104 80 L116 82 M124 82 L136 80"', 'd="M104 77 L116 78 M124 78 L136 77"')
        tete += (f'<circle cx="111" cy="85.5" r="1.6" fill="{ENCRE}"/><circle cx="129" cy="85.5" r="1.6" fill="{ENCRE}"/>')
    e = 4.2
    tx, ty = 960 - 120 * e, 120 - 38 * e
    fond = (f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>'
            f'<rect width="{W}" height="{H}" fill="url(#sacs)" opacity=".3"/>'
            f'<rect width="{W}" height="{H}" fill="{LAVIS}" opacity=".18"/>')
    gens = (f'{defs}<g transform="translate({tx:.0f} {ty:.0f}) scale({e})" stroke="{ENCRE}" stroke-linejoin="round" '
            f'stroke-linecap="round">{corps}{tete}</g>')
    return fond + gens


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    (DST / "cin_sortie_01.svg").write_text(svg(image_b(4)), encoding="utf-8")
    (DST / "cin_sortie_02.svg").write_text(bande([image_b(k) for k in range(4)], ZONE_B, 2), encoding="utf-8")
    (DST / "cin_sortie_03.svg").write_text(svg(lamarre(0)), encoding="utf-8")
    (DST / "cin_sortie_04.svg").write_text(bande([lamarre(k) for k in range(2)], ZONE_C, 2), encoding="utf-8")
    print("e1_sortie_tranchee : 4 planches dans art/src/cin/")


if __name__ == "__main__":
    main()
