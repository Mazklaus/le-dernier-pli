#!/usr/bin/env python3
"""Génère les sources SVG des décors de surface de l'étape 1 (planche n° 4 de la DA).

Chaque plan est dessiné en coordonnées monde (1 px = 1 px à 1080p), puis découpé en
tuiles de 2048 px au plus : art/src/env/e1/env_e1_planN_<nom>_NN.svg. Les motifs de
hachure sont en userSpaceOnUse, donc continus d'une tuile à l'autre.
Positions reprises de scenes/etapes/etape_01/etape_01.tscn (surface de 10624 px).

Usage : python3 tools/gen_decors_e1_surface.py
Puis : python3 tools/export_svg.py
"""
from __future__ import annotations

import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DST = ROOT / "art" / "src" / "env" / "e1"
FX = ROOT / "art" / "src" / "fx"
H = 1080
TUILE = 2048
LARGEUR = 10624          # boyau (3840) + carrefour (5760 + mur) + pied de l'échelle (960)
VUE = 1920
VITESSES = {0: 0.05, 1: 0.2, 2: 0.5, 3: 1.0, 4: 1.4}
SOL = 900                # dessus du caillebotis
CRETE = 520              # haut du parados
SOMBRE_X = 6600          # cran de lumière après la chapelle

PAPIER, ENCRE, LAVIS, MINE, ROUGE = "#E8E5DA", "#15130F", "#4A463D", "#8C877A", "#9B1C1C"

DEFS = f"""<defs>
<pattern id="h1" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(38)"><rect width="5" height="5" fill="{PAPIER}"/><line x1="0" y1="0" x2="0" y2="5" stroke="{ENCRE}" stroke-width="1"/></pattern>
<pattern id="h2" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(38)"><rect width="4" height="4" fill="{PAPIER}"/><line x1="0" y1="0" x2="0" y2="4" stroke="{ENCRE}" stroke-width="1.1"/><line x1="0" y1="2" x2="4" y2="2" stroke="{ENCRE}" stroke-width=".8"/></pattern>
<pattern id="v1" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(38)"><line x1="0" y1="0" x2="0" y2="5" stroke="{ENCRE}" stroke-width="1"/></pattern>
<pattern id="terre" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(38)"><rect width="7" height="7" fill="{PAPIER}"/><line x1="0" y1="0" x2="0" y2="7" stroke="{ENCRE}" stroke-width="1.1"/><line x1="3.5" y1="0" x2="3.5" y2="7" stroke="{ENCRE}" stroke-width=".5"/></pattern>
<pattern id="sacs" width="68" height="32" patternUnits="userSpaceOnUse"><rect width="68" height="32" fill="{PAPIER}"/><path d="M2 30 Q2 4 34 4 Q66 4 66 30 Z" fill="url(#h1)" stroke="{ENCRE}" stroke-width="2.2"/><path d="M-32 14 Q-32 -12 0 -12 Q32 -12 32 14 M36 14 Q36 -12 68 -12" fill="none" stroke="{ENCRE}" stroke-width="1.5"/><path d="M24 16 L28 20 M40 12 L42 18" stroke="{ENCRE}" stroke-width="1.2"/></pattern>
<pattern id="planches" width="80" height="44" patternUnits="userSpaceOnUse"><rect width="80" height="44" fill="url(#h1)"/><path d="M0 0 H80 M0 22 H80 M28 0 V22 M60 22 V44" stroke="{ENCRE}" stroke-width="2"/><circle cx="10" cy="10" r="1.6" fill="{ENCRE}"/><circle cx="68" cy="32" r="1.6" fill="{ENCRE}"/></pattern>
<pattern id="caille" width="36" height="40" patternUnits="userSpaceOnUse"><rect width="36" height="40" fill="{PAPIER}"/><rect x="2" y="2" width="28" height="36" fill="url(#h1)" stroke="{ENCRE}" stroke-width="2"/></pattern>
</defs>"""


def rnd(seed: int) -> random.Random:
    return random.Random(seed)


def crete(x0: int, x1: int, y: float, amp: float, pas: int, seed: int) -> str:
    """Ligne de crête irrégulière (périodique sur rien : c'est du décor unique)."""
    r = rnd(seed)
    pts = []
    x = x0
    while x <= x1:
        pts.append(f"{x} {y + r.uniform(-amp, amp):.1f}")
        x += pas
    return " L".join(pts)


def plan3() -> str:
    out = []
    # parados : sacs en haut, coffrage de planches en bas, poteaux
    out.append(f'<path d="M0 {CRETE} L{crete(0, LARGEUR, CRETE, 6, 64, 3)} L{LARGEUR} 760 L0 760 Z" fill="url(#sacs)" stroke="{ENCRE}" stroke-width="3"/>')
    out.append(f'<rect x="0" y="760" width="{LARGEUR}" height="{SOL - 760}" fill="url(#planches)" stroke="{ENCRE}" stroke-width="3"/>')
    r = rnd(11)
    x = 120
    while x < LARGEUR:
        out.append(f'<path d="M{x} 744 L{x + r.uniform(-4, 4):.0f} {SOL}" stroke="{ENCRE}" stroke-width="12"/>')
        x += r.randint(260, 340)
    # mur entre carrefour et pied de l'échelle
    out.append(f'<rect x="9600" y="{CRETE - 20}" width="64" height="{SOL - CRETE + 20}" fill="url(#h2)" stroke="{ENCRE}" stroke-width="3"/>')

    def descente(cx: int, larg: int = 160, ruban: bool = False) -> None:
        x0 = cx - larg // 2
        out.append(f'<path d="M{x0} {SOL} L{x0} 640 Q{cx} 600 {x0 + larg} 640 L{x0 + larg} {SOL} Z" fill="{ENCRE}" stroke="{ENCRE}" stroke-width="3"/>')
        for i, y in enumerate(range(700, SOL, 40)):
            out.append(f'<path d="M{x0 + 16 + i * 4} {y} L{x0 + larg - 16 - i * 4} {y}" stroke="{PAPIER}" stroke-width="3"/>')
        out.append(f'<path d="M{x0 - 8} 640 L{x0 - 8} {SOL} M{x0 + larg + 8} 640 L{x0 + larg + 8} {SOL}" stroke="{ENCRE}" stroke-width="14"/>')
        if ruban:  # étais rubannés de la vieille sape
            for k in range(3):
                y = 680 + k * 60
                out.append(f'<path d="M{x0 - 14} {y} L{x0 + larg + 14} {y + 26}" stroke="{PAPIER}" stroke-width="10"/>')
                out.append(f'<path d="M{x0 - 14} {y} L{x0 + larg + 14} {y + 26}" stroke="{ENCRE}" stroke-width="2" fill="none" stroke-dasharray="14 10"/>')

    descente(200)                    # vers la couchette
    descente(3200)                   # vers l'abri du sergent
    descente(4300)                   # vers la cantine
    descente(8940, ruban=True)       # vieille sape
    descente(9340)                   # sape de sortie

    # écriteau de relève (détail, contour 2 px de plus)
    out.append(f'<rect x="2040" y="640" width="120" height="76" fill="{PAPIER}" stroke="{ENCRE}" stroke-width="4"/>')
    for k in range(5):
        y = 656 + k * 12
        out.append(f'<path d="M2054 {y} L{2140 - k * 6} {y}" stroke="{ENCRE}" stroke-width="1.6"/>')
        out.append(f'<path d="M2052 {y + 2} L{2146 - k * 6} {y - 3}" stroke="{ENCRE}" stroke-width="1"/>')
    out.append(f'<path d="M2100 716 L2100 {SOL}" stroke="{ENCRE}" stroke-width="8"/>')

    # croix de fortune aux noms grattés (carrefour 1400)
    out.append(f'<path d="M5240 {SOL} L5244 700 M5200 744 L5290 738" stroke="{ENCRE}" stroke-width="14"/>')
    out.append(f'<path d="M5212 740 L5224 746 M5256 736 L5272 742 M5236 770 L5250 778 M5238 800 L5250 806" stroke="{PAPIER}" stroke-width="2.4"/>')

    # niche de la chapelle (carrefour 2360)
    cx = 6200
    out.append(f'<path d="M{cx - 130} {SOL} L{cx - 130} 700 Q{cx} 600 {cx + 130} 700 L{cx + 130} {SOL} Z" fill="{ENCRE}"/>')
    out.append(f'<path d="M{cx - 100} {SOL} L{cx - 100} 712 Q{cx} 636 {cx + 100} 712 L{cx + 100} {SOL} Z" fill="url(#h2)" stroke="{PAPIER}" stroke-width="2"/>')
    for dx, hcierge in ((-30, 34), (0, 50), (30, 28)):
        top = 820 - hcierge
        out.append(f'<rect x="{cx + dx - 6}" y="{top}" width="12" height="{hcierge}" fill="{PAPIER}" stroke="{ENCRE}" stroke-width="2"/>')
        out.append(f'<path d="M{cx + dx} {top - 2} Q{cx + dx - 6} {top - 14} {cx + dx} {top - 26} Q{cx + dx + 6} {top - 14} {cx + dx} {top - 2} Z" fill="{PAPIER}" stroke="{ENCRE}" stroke-width="1.6"/>')
    out.append(f'<path d="M{cx - 70} 820 L{cx + 70} 820 L{cx + 80} {SOL} L{cx - 80} {SOL} Z" fill="url(#sacs)" stroke="{ENCRE}" stroke-width="3"/>')

    # étai aux bâtons gravés du compteur de cloches (carrefour 3200, la fausse note)
    out.append(f'<path d="M7040 744 L7040 {SOL}" stroke="{ENCRE}" stroke-width="22"/>')
    for k in range(12):
        x = 7032 + (k % 5) * 4
        y = 770 + (k // 5) * 30
        if k % 5 == 4:
            out.append(f'<path d="M7030 {y + 16} L7050 {y - 2}" stroke="{PAPIER}" stroke-width="2"/>')
        else:
            out.append(f'<path d="M{x} {y} L{x} {y + 18}" stroke="{PAPIER}" stroke-width="2"/>')

    # banquette de tir et périscope (carrefour 3940)
    out.append(f'<path d="M7640 {SOL} L7640 840 L7940 840 L7940 {SOL} Z" fill="url(#sacs)" stroke="{ENCRE}" stroke-width="3"/>')
    out.append(f'<rect x="7838" y="420" width="26" height="420" fill="url(#h2)" stroke="{ENCRE}" stroke-width="3"/>')
    out.append(f'<rect x="7830" y="402" width="42" height="22" fill="{ENCRE}"/>')
    out.append(f'<rect x="7814" y="640" width="26" height="22" fill="{ENCRE}"/>')

    # lanternes du chemin principal (papier nu, pas de halo peint)
    for lx in (900, 2600, 3900, 5600, 6900, 8400, 9900):
        out.append(f'<path d="M{lx} {CRETE + 14} L{lx} 580" stroke="{ENCRE}" stroke-width="2.4"/>')
        out.append(f'<path d="M{lx - 16} 580 L{lx + 16} 580 L{lx + 13} 628 L{lx - 13} 628 Z" fill="{PAPIER}" stroke="{ENCRE}" stroke-width="3"/>')
        out.append(f'<path d="M{lx} 592 Q{lx + 7} 604 {lx} 616 Q{lx - 7} 604 {lx} 592 Z" fill="{PAPIER}" stroke="{ENCRE}" stroke-width="1.6"/>')
        out.append(f'<rect x="{lx - 18}" y="574" width="36" height="7" fill="{ENCRE}"/>')

    # barbelés qui vibrent au pied de l'échelle (détail 740 → 10404)
    for k, y in enumerate((548, 572, 596)):
        out.append(f'<path d="M10260 {y} Q10330 {y + 14} 10400 {y} T10540 {y}" fill="none" stroke="{ENCRE}" stroke-width="2.6" stroke-dasharray="6 5"/>')
        out.append(f'<path d="M10262 {y + 3} Q10332 {y + 17} 10402 {y + 3} T10542 {y + 3}" fill="none" stroke="{ENCRE}" stroke-width="1.2"/>')
    out.append(f'<path d="M10250 {SOL} L10256 520 M10560 {SOL} L10552 520" stroke="{ENCRE}" stroke-width="10"/>')

    # caillebotis et terre
    out.append(f'<rect x="0" y="{SOL}" width="{LARGEUR}" height="40" fill="url(#caille)" stroke="{ENCRE}" stroke-width="3"/>')
    out.append(f'<rect x="0" y="{SOL + 40}" width="{LARGEUR}" height="{H - SOL - 40}" fill="url(#terre)" stroke="{ENCRE}" stroke-width="3"/>')

    # cran de lumière : voile de hachure net sur tout ce qui suit la chapelle
    out.append(f'<path d="M{SOMBRE_X} {CRETE} L{crete(SOMBRE_X, LARGEUR, CRETE, 6, 64, 3).split(" L", 0)[0]} L{LARGEUR} {CRETE} L{LARGEUR} {H} L{SOMBRE_X} {H} Z" fill="url(#v1)" opacity=".55"/>')
    return "".join(out)


def plan2(w: int) -> str:
    out = [f'<path d="M0 470 Q{w * .1:.0f} 430 {w * .2:.0f} 462 T{w * .4:.0f} 452 T{w * .6:.0f} 466 T{w * .8:.0f} 450 T{w} 460 L{w} {H} L0 {H} Z" fill="{LAVIS}"/>']
    r = rnd(21)
    x = 200
    while x < w:
        h = r.randint(50, 90)
        base = 470
        if r.random() < .55:
            out.append(f'<path d="M{x} {base} L{x} {base - h} M{x - 18} {base - h + 22} L{x + 18} {base - h + 22}" stroke="{LAVIS}" stroke-width="8"/>')
        else:
            out.append(f'<path d="M{x} {base} L{x + 4} {base - h}" stroke="{LAVIS}" stroke-width="7"/>')
        x += r.randint(500, 900)
    return "".join(out)


def plan1(w: int) -> str:
    out = [f'<path d="M0 {crete(0, w, 400, 14, 120, 31)} L{w} {H} L0 {H} Z" fill="{MINE}"/>']
    # clochers sans cloche : la baie est vide, en papier
    for cx in (900, 2700):
        out.append(f'<path d="M{cx - 26} 400 L{cx - 26} 270 L{cx} 230 L{cx + 26} 270 L{cx + 26} 400 Z" fill="{MINE}"/>')
        out.append(f'<rect x="{cx - 14}" y="282" width="28" height="30" fill="{PAPIER}"/>')
    for sx in (300, 1500, 2100, 3300):
        out.append(f'<path d="M{sx} 400 L{sx + 3} 350 L{sx - 10} 336 M{sx + 3} 366 L{sx + 18} 356" stroke="{MINE}" stroke-width="6" fill="none"/>')
    return "".join(out)


def plan0(w: int) -> str:
    out = [f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>']
    r = rnd(41)
    for _ in range(14):
        y = r.randint(60, 360)
        x = r.randint(-200, w)
        out.append(f'<path d="M{x} {y} H{x + r.randint(300, 900)}" stroke="{MINE}" stroke-width="1.4" opacity=".6"/>')
    out.append(f'<circle cx="{int(w * .7)}" cy="170" r="60" fill="none" stroke="{MINE}" stroke-width="2.6"/>')
    return "".join(out)


def plan4(w: int) -> str:
    out = []
    r = rnd(51)
    x = 300
    while x < w:
        larg = r.randint(160, 320)
        out.append(f'<path d="M{x} {H} Q{x + larg * .3:.0f} {H - r.randint(80, 140)} {x + larg * .6:.0f} {H - r.randint(60, 120)} T{x + larg} {H} Z" fill="{ENCRE}"/>')
        if r.random() < .5:
            px = x + larg // 2
            top = H - r.randint(220, 320)
            out.append(f'<path d="M{px} {H - 60} L{px + r.randint(-14, 14)} {top}" stroke="{ENCRE}" stroke-width="14"/>')
            out.append(f'<path d="M{px} {top + 30} Q{px + 120} {top + 70} {px + 260} {top + 34}" fill="none" stroke="{ENCRE}" stroke-width="3" stroke-dasharray="6 9"/>')
        x += larg + r.randint(900, 1700)
    return "".join(out)


def ecrire_tuiles(plan: int, nom: str, contenu: str, largeur: int, fond: bool) -> int:
    DST.mkdir(parents=True, exist_ok=True)
    n = math.ceil(largeur / TUILE)
    for i in range(n):
        x0 = i * TUILE
        w = min(TUILE, largeur - x0)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="{x0} 0 {w} {H}">'
               f'{DEFS}{contenu}</svg>\n')
        (DST / f"env_e1_plan{plan}_{nom}_{i + 1:02d}.svg").write_text(svg, encoding="utf-8")
    return n


def largeur_plan(v: float) -> int:
    return int(round(VUE + (LARGEUR - VUE) * v))


def fx() -> None:
    FX.mkdir(parents=True, exist_ok=True)
    r = rnd(61)
    flocons = "".join(f'<circle cx="{r.uniform(0, 1920):.0f}" cy="{r.uniform(0, 1080):.0f}" r="{r.uniform(1.4, 3):.1f}" fill="{MINE}"/>' for _ in range(180))
    (FX / "fx_cendre.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">{flocons}</svg>\n')
    def echelle(fill_montant: str, nom: str) -> None:
        barreaux = "".join(f'<path d="M14 {y} L66 {y}" stroke="{ENCRE}" stroke-width="7"/>' for y in range(40, 720, 64))
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="80" height="720" viewBox="0 0 80 720">{DEFS}'
               f'<rect x="4" y="0" width="14" height="720" fill="{fill_montant}" stroke="{ENCRE}" stroke-width="3"/>'
               f'<rect x="62" y="0" width="14" height="720" fill="{fill_montant}" stroke="{ENCRE}" stroke-width="3"/>{barreaux}</svg>\n')
        (FX / f"{nom}.svg").write_text(svg)
    echelle("url(#h2)", "fx_echelle-ombre")
    echelle(PAPIER, "fx_echelle-claire")
    (FX / "fx_tobie-cendre.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="32" height="16" viewBox="0 0 32 16"><path d="M4 11 Q14 2 28 8 Q22 12 14 12 Q8 13 4 11 Z" fill="{LAVIS}"/></svg>\n')
    (FX / "fx_chicane.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="260" viewBox="0 0 200 260">{DEFS}'
        f'<path d="M10 260 L18 60 Q100 30 182 60 L190 260 Z" fill="url(#sacs)" stroke="{ENCRE}" stroke-width="3"/></svg>\n')


def main() -> None:
    total = 0
    total += ecrire_tuiles(0, "ciel", plan0(largeur_plan(VITESSES[0])), largeur_plan(VITESSES[0]), True)
    total += ecrire_tuiles(1, "lointain", plan1(largeur_plan(VITESSES[1])), largeur_plan(VITESSES[1]), False)
    total += ecrire_tuiles(2, "milieu", plan2(largeur_plan(VITESSES[2])), largeur_plan(VITESSES[2]), False)
    total += ecrire_tuiles(3, "surface", plan3(), LARGEUR, False)
    total += ecrire_tuiles(4, "premier-plan", plan4(largeur_plan(VITESSES[4])), largeur_plan(VITESSES[4]), False)
    fx()
    print(f"{total} tuiles + 5 calques fx dans art/src/")


if __name__ == "__main__":
    main()
