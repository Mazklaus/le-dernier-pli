#!/usr/bin/env python3
"""Génère les planches de la cinématique e6_fuite_noir (lot 2, planche validée par le GD le
17/11) : option « Fuir » de e6_eloi. Tobie court dans le noir, tombe, les mains à plat sur la
pierre ; longtemps après, la petite lumière verte est là, au loin, immobile.

  cin_e6-fuite-noir     1920 x 1080 : la nef dans le noir, des piliers et des racines à peine
                        devinés (le papier devient le noir de l'écran inversé)
  cin_e6-fuite-course   3 images de 360 x 600 (transparent) : sa silhouette qui court, à peine
                        plus claire que le noir
  cin_e6-fuite-dalles   1920 x 1080 : de tout près, les dalles de la nef
  cin_e6-fuite-mains    2 images (transparent, ZONE_MAINS) : les mains qui arrivent, puis à plat,
                        doigts écartés, la poussière soulevée
  cin_e6-fuite-loin     1920 x 1080 : le noir, un sol à peine dessiné
  cin_e6-fuite-lueur    (transparent, ZONE_LUEUR) : la lumière verte du bocal, au loin

L'écran de l'étape 6 inverse l'image : dessiné à l'endroit. Le vert-de-gris (ACCENT) est posé
plein, sans transparence, pour que l'écran le garde exact. Aucun rouge.

Usage : python3 tools/gen_cin_e6_fuite.py
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
PEAU = "#5E5A52"        # la peau des PNJ de l'étape 6 : pâle une fois l'écran inversé
ACCENT = "#5F7F72"      # vert-de-gris exact de l'étape 6 (papier_etapes.gd)
OMBRE = "#C4C0B3"       # la silhouette : à peine plus claire que le noir de l'écran inversé
COURSE = (360, 600)
ZONE_MAINS = (360, 280, 1200, 800)
ZONE_LUEUR = (1240, 560, 160, 160)


def svg(contenu: str, w: int = W, h: int = H) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{DEFS_CIN}{contenu}</svg>\n')


def bande(images: list[str], zone: tuple[int, int, int, int]) -> str:
    x, y, w, h = zone
    corps = "".join(f'<svg x="{i * w}" y="0" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}">{im}</svg>'
                    for i, im in enumerate(images))
    return svg(corps, w * len(images), h)


# --------------------------------------------------------------------------- P1, la course
def noir() -> str:
    r = random.Random(6601)
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>']
    # des piliers penchés, à peine des bords
    for x, a in ((240, -3), (760, 2), (1260, -4), (1720, 3)):
        o.append(f'<g transform="rotate({a} {x} 900)" opacity=".5"><path d="M{x - 60} -40 V900 M{x + 60} -40 V900" '
                 f'stroke="{MINE}" stroke-width="3" fill="none"/></g>')
    # des racines qui pendent
    for _ in range(9):
        x = r.uniform(0, W)
        o.append(f'<path d="M{x:.0f} -10 q{r.uniform(-40, 40):.0f} {r.uniform(80, 160):.0f} {r.uniform(-20, 20):.0f} {r.uniform(200, 320):.0f}" '
                 f'fill="none" stroke="{MINE}" stroke-width="{r.uniform(2, 4):.1f}" opacity=".45"/>')
    o.append(f'<path d="M0 905 Q500 890 960 902 T{W} 896" fill="none" stroke="{MINE}" stroke-width="3" opacity=".6"/>')
    return "".join(o)


def coureur(i: int) -> str:
    """La silhouette qui court, de profil vers la droite, penchée en avant ; 3 phases."""
    w, h = COURSE
    cx = w / 2
    # (genou avant, pied avant, genou arrière, pied arrière, bras avant, bras arrière), relatifs à la hanche
    phases = (
        ((70, 70), (40, 175), (-40, 80), (-120, 130), (60, -60), (-70, -110)),
        ((30, 90), (10, 190), (-10, 90), (-30, 190), (10, -40), (-10, -80)),
        ((-40, 80), (-120, 130), (70, 70), (40, 175), (-70, -110), (60, -60)),
    )[i]
    hx, hy = cx, 350 - (8 if i == 1 else 0)
    ep = (cx + 30, 210 + hy - 350)
    o = []
    for (gx, gy), (px, py) in ((phases[0], phases[1]), (phases[2], phases[3])):
        o.append(f'<path d="M{hx:.0f} {hy:.0f} L{hx + gx:.0f} {hy + gy:.0f} L{hx + px:.0f} {hy + py:.0f}" fill="none" '
                 f'stroke="{OMBRE}" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"/>')
    for bx, by in (phases[4], phases[5]):
        o.append(f'<path d="M{ep[0]:.0f} {ep[1]:.0f} L{ep[0] + bx * .6:.0f} {ep[1] + 70:.0f} L{ep[0] + bx:.0f} {ep[1] + 70 + by * .4:.0f}" '
                 f'fill="none" stroke="{OMBRE}" stroke-width="22" stroke-linecap="round" stroke-linejoin="round"/>')
    # le manteau, le buste penché, la capuche
    o.append(f'<path d="M{hx - 50:.0f} {hy + 20:.0f} L{ep[0] - 40:.0f} {ep[1] - 10:.0f} Q{ep[0] + 10:.0f} {ep[1] - 40:.0f} {ep[0] + 50:.0f} {ep[1]:.0f} '
             f'L{hx + 46:.0f} {hy + 30:.0f} Q{hx:.0f} {hy + 50:.0f} {hx - 50:.0f} {hy + 20:.0f} Z" fill="{OMBRE}"/>')
    o.append(f'<ellipse cx="{ep[0] + 30:.0f}" cy="{ep[1] - 60:.0f}" rx="42" ry="48" fill="{OMBRE}"/>')
    # un liseré à peine plus clair sur le dos : la seule chose qu'on voie
    o.append(f'<path d="M{hx - 50:.0f} {hy + 20:.0f} L{ep[0] - 40:.0f} {ep[1] - 10:.0f} Q{ep[0] - 10:.0f} {ep[1] - 90:.0f} {ep[0] + 30:.0f} {ep[1] - 108:.0f}" '
             f'fill="none" stroke="{MINE}" stroke-width="3" stroke-linecap="round" opacity=".8"/>')
    return f'<svg x="{i * w}" y="0" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{"".join(o)}</svg>'


# --------------------------------------------------------------------------- P2, la chute
def dalles() -> str:
    r = random.Random(6602)
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>',
         f'<rect y="120" width="{W}" height="{H - 120}" fill="url(#pierre)"/>']
    fuite = (960, -900)
    for k in range(-6, 7):
        x = 960 + k * 360
        o.append(f'<path d="M{fuite[0] + (x - fuite[0]) * .55:.0f} 120 L{x:.0f} {H}" stroke="{MINE}" stroke-width="5"/>')
    for y in (120, 260, 450, 720, 1040):
        o.append(f'<path d="M0 {y + r.uniform(-6, 6):.0f} L{W} {y + r.uniform(-6, 6):.0f}" stroke="{MINE}" stroke-width="5"/>')
    o.append(f'<path d="M680 520 l60 40 l-20 70 M1300 830 l40 -30 l50 20" fill="none" stroke="{MINE}" stroke-width="3"/>')
    o.append(f'<rect width="{W}" height="120" fill="{PAPIER}"/>')
    return "".join(o)


def doigt(x0: float, y0: float, x1: float, y1: float, ep: float) -> str:
    return (f'<path d="M{x0:.0f} {y0:.0f} L{x1:.0f} {y1:.0f}" stroke="{ENCRE}" stroke-width="{ep + 10:.0f}" stroke-linecap="round"/>'
            f'<path d="M{x0:.0f} {y0:.0f} L{x1:.0f} {y1:.0f}" stroke="{PEAU}" stroke-width="{ep:.0f}" stroke-linecap="round"/>')


def main_plate(cx: float, cy: float, sens: int, s: float, ecart: float) -> str:
    """Une main à plat, vue de dessus, doigts vers le haut ; sens -1 gauche, 1 droite."""
    o = []
    doigts = ((-1.0, 150, -12), (-.35, 185, -4), (.3, 175, 4), (.9, 145, 12))
    for dx, lg, a in doigts:
        bx, by = cx + dx * 58 * s * sens, cy - 70 * s
        ang = (a * ecart) * sens

        ex = bx + math.sin(math.radians(ang)) * lg * s
        ey = by - math.cos(math.radians(ang)) * lg * s
        o.append(doigt(bx, by, ex, ey, 46 * s))
    # le pouce, vers l'autre main
    o.append(doigt(cx - 80 * s * sens, cy + 10 * s, cx - (150 + 30 * ecart) * s * sens, cy - 70 * s, 50 * s))
    o.append(f'<path d="M{cx - 95 * s:.0f} {cy - 80 * s:.0f} Q{cx:.0f} {cy - 110 * s:.0f} {cx + 95 * s:.0f} {cy - 80 * s:.0f} '
             f'L{cx + 90 * s:.0f} {cy + 80 * s:.0f} Q{cx:.0f} {cy + 120 * s:.0f} {cx - 90 * s:.0f} {cy + 80 * s:.0f} Z" fill="{PEAU}" {ST} stroke-width="6"/>')
    # la manche, qui sort du cadre par le bas
    o.append(f'<path d="M{cx - 110 * s:.0f} {cy + 70 * s:.0f} L{cx + 110 * s:.0f} {cy + 70 * s:.0f} L{cx + 150 * s:.0f} {cy + 400 * s:.0f} '
             f'L{cx - 150 * s:.0f} {cy + 400 * s:.0f} Z" fill="url(#h1)" {ST} stroke-width="6"/>')
    # la terre sur les doigts
    r = random.Random(int(cx))
    for _ in range(6):
        o.append(f'<circle cx="{cx + r.uniform(-70, 70) * s:.0f}" cy="{cy + r.uniform(-120, 40) * s:.0f}" r="{r.uniform(5, 10) * s:.0f}" fill="{LAVIS}"/>')
    return "".join(o)


def mains(image: int) -> str:
    if image == 0:      # elles arrivent : plus haut, plus grandes (plus près de nous), doigts serrés
        return main_plate(700, 640, -1, 1.12, .3) + main_plate(1220, 620, 1, 1.12, .3)
    o = [main_plate(720, 700, -1, 1.0, 1.0), main_plate(1200, 690, 1, 1.0, 1.0)]
    r = random.Random(6603)
    for cx in (720, 1200):      # la poussière soulevée
        for _ in range(5):
            x, y = cx + r.uniform(-260, 260), 760 + r.uniform(-40, 120)
            o.append(f'<path d="M{x:.0f} {y:.0f} q20 -16 40 0" fill="none" stroke="{MINE}" stroke-width="4" stroke-linecap="round"/>')
    return "".join(o)


# --------------------------------------------------------------------------- P3, la lumière
def loin() -> str:
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>',
         f'<path d="M0 820 Q700 790 1320 702 T{W} 690" fill="none" stroke="{MINE}" stroke-width="3" opacity=".5"/>',
         f'<path d="M1100 300 L1160 700 M1480 280 L1450 700" stroke="{MINE}" stroke-width="2" opacity=".35"/>']
    return "".join(o)


def lueur() -> str:
    x, y, w, h = ZONE_LUEUR
    cx, cy = x + w / 2, y + h / 2
    o = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{ACCENT}" stroke-width="{e}"/>' for r, e in ((70, 2), (52, 3))]
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="18" ry="24" fill="{ACCENT}"/>')
    o.append(f'<path d="M{cx - 7} {cy - 8} q3 -2 6 0 M{cx + 2} {cy + 4} q3 -2 6 0" fill="none" stroke="{ENCRE}" stroke-width="2"/>')
    return f'<svg width="{w}" height="{h}" viewBox="{x} {y} {w} {h}">{"".join(o)}</svg>'


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    w, h = COURSE
    fichiers = {
        "cin_e6-fuite-noir": svg(noir()),
        "cin_e6-fuite-course": svg("".join(coureur(i) for i in range(3)), w * 3, h),
        "cin_e6-fuite-dalles": svg(dalles()),
        "cin_e6-fuite-mains": bande([mains(0), mains(1)], ZONE_MAINS),
        "cin_e6-fuite-loin": svg(loin()),
        "cin_e6-fuite-lueur": svg(lueur(), ZONE_LUEUR[2], ZONE_LUEUR[3]),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"e6_fuite_noir : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
