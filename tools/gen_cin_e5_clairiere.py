#!/usr/bin/env python3
"""Génère les planches de la cinématique e5_clairiere_ciel (lot 2, planche validée par le GD le
17/11) : au début de e5_clairiere, Tobie sort des dernières croix, le regard monte vers le ciel
qui s'ouvre, immense, puis plonge : en contrebas, un toit d'église à moitié enterré.

Le plan 1 réemploie le décor (env_e5_plan3_cimetiere_02 et clairiere_01). Planches nouvelles :
  cin_e5-clairiere-ciel     1920 x 2160 : le tilt. En bas, les deux dernières croix de près,
                            la brume au ras du sol ; en haut, le ciel ouvert, du papier nu.
  cin_e5-clairiere-nuages   1920 x 900 (transparent) : de longs nuages hauts qui dérivent.
  cin_e5-clairiere-eglise   1920 x 1080 : la plongée. Le creux de terre, le toit de la nef à
                            moitié enterré, le moignon du clocher muré ; la crête d'herbe devant.
  cin_e5-clairiere-herbe    2 images (transparent) : les herbes de la crête sous le vent,
                            posées en ZONE_HERBE.

L'écran de l'étape 5 inverse l'image : dessiné à l'endroit. Aucun rouge, aucune cloche, rien ne
se compte (les ardoises et les herbes sont des hachures, pas des séries).

Usage : python3 tools/gen_cin_e5_clairiere.py
"""
from __future__ import annotations

import random
from pathlib import Path

from gen_cin_epilogues import DEFS_CIN
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER

DST = Path(__file__).resolve().parent.parent / "art" / "src" / "cin"
W, H = 1920, 1080
ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
CLAIR = "#D3CFC2"
SOL_CIEL = 2060                 # le sol au bas de la planche du tilt
ZONE_NUAGES = (0, 80, 1920, 900)
ZONE_HERBE = (0, 900, 1920, 180)


def svg(contenu: str, w: int = W, h: int = H) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{DEFS_CIN}{contenu}</svg>\n')


def bande(images: list[str], zone: tuple[int, int, int, int]) -> str:
    """Les images côte à côte, chacune recadrée sur la zone (fond transparent)."""
    x, y, w, h = zone
    corps = "".join(f'<svg x="{i * w}" y="0" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}">{im}</svg>'
                    for i, im in enumerate(images))
    return svg(corps, w * len(images), h)


def grande_croix(x: float, pied: float, h: float, larg: float, a: float, r: random.Random) -> str:
    """Une croix de bois de tout près : poteau, traverse, veines, une fente."""
    b = h * .26
    ty = pied - h * .78
    o = [f'<g transform="rotate({a:.1f} {x:.0f} {pied:.0f})">',
         f'<rect x="{x - larg / 2:.0f}" y="{pied - h:.0f}" width="{larg:.0f}" height="{h + 40:.0f}" fill="{CLAIR}" {ST} stroke-width="6"/>',
         f'<rect x="{x - b:.0f}" y="{ty - larg / 2:.0f}" width="{2 * b:.0f}" height="{larg:.0f}" fill="{CLAIR}" {ST} stroke-width="6"/>']
    for i in range(4):
        vx = x - larg / 2 + 10 + i * (larg - 20) / 3
        o.append(f'<path d="M{vx:.0f} {pied - h + 10:.0f} Q{vx + r.uniform(-5, 5):.0f} {pied - h / 2:.0f} {vx:.0f} {pied + 30:.0f}" '
                 f'fill="none" stroke="{MINE}" stroke-width="2"/>')
    o.append(f'<path d="M{x - b + 16:.0f} {ty - 4:.0f} H{x + b - 20:.0f}" stroke="{MINE}" stroke-width="2"/>')
    o.append('</g>')
    return "".join(o)


def ciel() -> str:
    r = random.Random(5501)
    o = [f'<rect width="{W}" height="{2 * H}" fill="{PAPIER}"/>',
         '<defs><linearGradient id="brumeC" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{MINE}" stop-opacity="0"/><stop offset=".55" stop-color="{MINE}" stop-opacity=".18"/>'
         f'<stop offset="1" stop-color="{MINE}" stop-opacity=".45"/></linearGradient></defs>',
         f'<rect y="1250" width="{W}" height="{SOL_CIEL - 1250}" fill="url(#brumeC)"/>']
    # le bord déchiré du brouillard : il s'arrête, le ciel commence
    for k in range(5):
        y = 1180 + k * 60
        pts = " ".join(f"{x:.0f},{y + r.uniform(-18, 18):.0f}" for x in range(-40, W + 80, 120))
        o.append(f'<polyline points="{pts}" fill="none" stroke="{LAVIS}" stroke-width="{2.5 - k * .3:.1f}" opacity="{.25 + k * .1:.2f}"/>')
    # au loin, les croix qui s'espacent, de plus en plus pâles, puis plus rien au milieu
    for _ in range(26):
        x = r.choice((r.uniform(0, 640), r.uniform(1300, W)))
        h = r.uniform(60, 150)
        pied = r.uniform(1820, 1900)
        o.append(f'<path d="M{x:.0f} {pied:.0f} V{pied - h:.0f} M{x - h * .22:.0f} {pied - h * .74:.0f} H{x + h * .22:.0f}" '
                 f'stroke="{MINE}" stroke-width="{h / 30:.1f}" opacity="{r.uniform(.35, .7):.2f}"/>')
    o.append(f'<path d="M0 1890 Q960 1872 {W} 1896" fill="none" stroke="{MINE}" stroke-width="2"/>')
    # le sol, l'herbe rase
    o.append(f'<rect y="{SOL_CIEL}" width="{W}" height="{2 * H - SOL_CIEL}" fill="url(#h1)" opacity=".5"/>')
    o.append(f'<path d="M0 {SOL_CIEL} H{W}" {ST} stroke-width="4"/>')
    # les deux dernières croix de chaque côté, de tout près : elles sortent du cadre par le bas
    for x, h, larg, a in ((150, 900, 54, -2.0), (390, 740, 40, 1.5), (1560, 800, 44, -1.2), (1800, 920, 58, 2.2)):
        o.append(grande_croix(x, SOL_CIEL + 10, h, larg, a, r))
    return "".join(o)


def nuages() -> str:
    """Les nuages hauts, longs et fins (dessinés dans le repère de la planche du ciel)."""
    r = random.Random(5502)
    o = []
    for y, x0, x1, ep in ((180, -200, 900, 3), (260, 500, 1700, 2.4), (420, -100, 1100, 2.6), (520, 1100, 2100, 3),
                          (700, 200, 1500, 2), (880, -150, 700, 2.2), (900, 1300, 2100, 2)):
        m = (x0 + x1) / 2
        o.append(f'<path d="M{x0} {y} Q{m:.0f} {y - r.uniform(20, 40):.0f} {x1} {y + r.uniform(-10, 10):.0f}" '
                 f'fill="none" stroke="{MINE}" stroke-width="{ep}" stroke-linecap="round" opacity=".7"/>')
        o.append(f'<path d="M{x0 + 120} {y + 16} Q{m:.0f} {y - 6:.0f} {x1 - 160} {y + 18}" fill="none" stroke="{LAVIS}" '
                 f'stroke-width="{ep * .6:.1f}" stroke-linecap="round" opacity=".35"/>')
    return "".join(o)


def eglise() -> str:
    r = random.Random(5503)
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>']
    # l'autre versant du creux, qui remonte vers une mince bande de ciel
    o.append(f'<path d="M0 150 Q600 120 1100 160 T{W} 140" fill="none" {ST} stroke-width="3"/>')
    o.append(f'<path d="M0 150 Q600 120 1100 160 T{W} 140 V560 Q960 640 0 560 Z" fill="{MINE}" opacity=".16"/>')
    for k in range(9):
        y = 200 + k * 46
        o.append(f'<path d="M{r.uniform(-60, 200):.0f} {y + k * 4} Q960 {y + 40 + k * 6} {W + r.uniform(-200, 60):.0f} {y + k * 4}" '
                 f'fill="none" stroke="{MINE}" stroke-width="1.6" opacity=".6"/>')
    # le fond du creux : la terre tassée autour du toit
    o.append(f'<ellipse cx="960" cy="700" rx="760" ry="170" fill="{MINE}" opacity=".22"/>')
    # le toit de la nef, à moitié enterré, vu d'en haut et de biais : le pan du fond, étroit,
    # et le pan vers nous, que la terre mange par le bas
    r1, r2 = (560, 540), (1320, 500)
    fond = (r1, r2, (1350, 440), (600, 478))
    devant = (r1, r2, (1290, 720), (500, 770))
    def poly(pts):
        return "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts) + " Z"
    o.append(f'<path d="{poly(fond)}" fill="{CLAIR}" {ST} stroke-width="6"/>')
    o.append(f'<path d="{poly(devant)}" fill="url(#h1)" {ST} stroke-width="6"/>')
    # les rangs d'ardoises : des traits parallèles au faîte, irréguliers, sans compte possible
    for k in range(1, 9):
        t = k / 9
        xa, ya = r1[0] + (devant[3][0] - r1[0]) * t, r1[1] + (devant[3][1] - r1[1]) * t
        xb, yb = r2[0] + (devant[2][0] - r2[0]) * t, r2[1] + (devant[2][1] - r2[1]) * t
        o.append(f'<path d="M{xa + r.uniform(4, 30):.0f} {ya:.0f} L{xb - r.uniform(4, 30):.0f} {yb:.0f}" '
                 f'stroke="{ENCRE}" stroke-width="2.2" stroke-dasharray="{r.randint(30, 70)} {r.randint(6, 14)}"/>')
    o.append(f'<path d="M{r1[0]} {r1[1]} L{r2[0]} {r2[1]}" {ST} stroke-width="9"/>')
    # des ardoises tombées, un trou noir dans le pan
    o.append(f'<path d="M860 600 l80 -8 l18 46 l-76 20 Z" fill="{ENCRE}"/>')
    # le moignon du clocher, au bout du faîte : muré, la flèche brisée
    o.append(f'<path d="M1290 520 V370 L1320 340 L1355 375 L1380 360 V540 Z" fill="{CLAIR}" {ST} stroke-width="6"/>')
    o.append(f'<path d="M1310 450 Q1335 410 1360 450 V500 H1310 Z" fill="url(#pierre)" {ST} stroke-width="4"/>')
    o.append(f'<path d="M1320 340 L1312 310 M1355 375 l12 -26" {ST} stroke-width="5"/>')
    # la terre qui recouvre la moitié basse : un bourrelet irrégulier, mangeant les pans
    pts = [(300, 760)]
    for x in range(380, 1660, 80):
        pts.append((x, 660 + 120 * ((x - 960) / 700) ** 2 + r.uniform(-14, 14)))
    pts += [(1680, 760), (1700, 1080), (220, 1080)]
    terre = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts) + " Z"
    o.append(f'<path d="{terre}" fill="{PAPIER}"/>')
    o.append(f'<path d="{terre}" fill="{MINE}" opacity=".2"/>')
    o.append('<path d="M' + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts[:-3]) + f'" fill="none" {ST} stroke-width="5"/>')
    # la pente qui descend vers nous, jusqu'à la crête
    o.append(f'<path d="M0 560 Q300 760 220 1080 M{W} 540 Q1640 760 1700 1080" fill="none" {ST} stroke-width="3"/>')
    for _ in range(40):
        x, y = r.uniform(60, 1860), r.uniform(780, 960)
        o.append(f'<path d="M{x:.0f} {y:.0f} q14 -4 28 0" fill="none" stroke="{MINE}" stroke-width="1.6"/>')
    # la crête au premier plan : la terre, sans les brins (ils sont dans la vignette)
    o.append(f'<path d="M0 1010 Q480 990 960 1006 T{W} 1000 V{H} H0 Z" fill="{CLAIR}" {ST} stroke-width="4"/>')
    return "".join(o)


def herbe(image: int) -> str:
    """Les brins de la crête ; l'image 1 les couche sous le vent."""
    r = random.Random(5504)
    o = []
    x = -10.0
    while x < W + 10:
        base = 1004 + r.uniform(-6, 10)
        h = r.uniform(50, 130)
        pli = r.uniform(4, 16) + (28 if image else 0) * h / 130
        o.append(f'<path d="M{x:.0f} {base:.0f} q{pli * .3:.0f} {-h * .55:.0f} {pli:.0f} {-h:.0f}" fill="none" stroke="{ENCRE}" '
                 f'stroke-width="{r.uniform(2.5, 4.5):.1f}" stroke-linecap="round"/>')
        x += r.uniform(9, 22)
    return "".join(o)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    x, y, w, h = ZONE_NUAGES
    fichiers = {
        "cin_e5-clairiere-ciel": svg(ciel(), W, 2 * H),
        "cin_e5-clairiere-nuages": svg(f'<svg width="{w}" height="{h}" viewBox="{x} {y} {w} {h}">{nuages()}</svg>', w, h),
        "cin_e5-clairiere-eglise": svg(eglise()),
        "cin_e5-clairiere-herbe": bande([herbe(0), herbe(1)], ZONE_HERBE),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"e5_clairiere_ciel : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
