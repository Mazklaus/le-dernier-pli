#!/usr/bin/env python3
"""Génère les sources SVG des décors de surface de l'étape 2, le No Man's Land (planche n° 5 de la DA).

Même méthode que l'étape 1 : chaque plan est dessiné en coordonnées monde, puis
découpé en tuiles de 2048 px au plus dans art/src/env/e2/env_e2_planN_<nom>_NN.svg.
Positions reprises de scenes/etapes/etape_02/etape_02.tscn (surface de 16320 px,
sol à trois hauteurs : 900, crête du poste à 780, fond des trous à 1060).
Les tuiles font 1300 px de haut, pour couvrir le fond des trous et le sol dessous.

Le papier gris de gaz de l'étape vient du shader (scripts/rendu/papier_etapes.gd) :
les assets restent dessinés sur le papier de référence #E8E5DA.

Usage : python3 tools/gen_decors_e2_surface.py
Puis : python3 tools/export_svg.py (ou un rendu Chromium), et godot --headless --import.
"""
from __future__ import annotations

import math
from pathlib import Path

from gen_decors_e1_surface import DEFS, ENCRE, LAVIS, MINE, PAPIER, crete, rnd

ROOT = Path(__file__).resolve().parent.parent
DST = ROOT / "art" / "src" / "env" / "e2"
FX = ROOT / "art" / "src" / "fx"
H = 1300
TUILE = 2048
VUE = 1920
LARGEUR = 16320
VITESSES = {0: 0.05, 1: 0.2, 2: 0.5, 3: 1.0, 4: 1.4}

# Profil du sol, identique à la CollisionPolygon2D de la maquette grise.
SOL = [(0, 900), (1600, 900), (1808, 780), (3400, 780), (3608, 900), (12000, 900),
       (12277, 1060), (13600, 1060), (13877, 900), (LARGEUR, 900)]

BROUILLARD = (4800, 10100)
CEINTURES = (5230, 10030)
SOUCHE_X = 14800          # sous le détail souche_entailles (les initiales sont gravées dedans)


def sol_y(x: float) -> float:
    for (x0, y0), (x1, y1) in zip(SOL, SOL[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return 900


def largeur_plan(v: float) -> int:
    return int(round(VUE + (LARGEUR - VUE) * v))


def seuil(x_monde: int, v: float) -> int:
    return int(round((x_monde - VUE / 2) * v + VUE / 2))


# --- motifs propres à l'étape 2 --------------------------------------------------
DEFS2 = DEFS.replace("</defs>", f"""<pattern id="boue" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(-38)"><rect width="9" height="9" fill="{PAPIER}"/><line x1="0" y1="0" x2="0" y2="9" stroke="{ENCRE}" stroke-width="1"/></pattern>
</defs>""")


def fil(x0: float, x1: float, y: float, seed: int, epais: float = 2.2) -> str:
    """Un brin de barbelé : ligne qui pend entre deux piquets, avec des nœuds nets."""
    r = rnd(seed)
    mx = (x0 + x1) / 2
    out = [f'<path d="M{x0:.0f} {y:.0f} Q{mx:.0f} {y + r.uniform(10, 26):.0f} {x1:.0f} {y + r.uniform(-4, 4):.0f}" fill="none" stroke="{ENCRE}" stroke-width="{epais}"/>']
    n = int((x1 - x0) / 18)
    for k in range(1, n):
        t = k / n
        bx = x0 + (x1 - x0) * t
        by = y + 4 * t * (1 - t) * 18
        out.append(f'<path d="M{bx - 4:.0f} {by - 4:.0f} L{bx + 4:.0f} {by + 4:.0f} M{bx + 4:.0f} {by - 4:.0f} L{bx - 4:.0f} {by + 4:.0f}" stroke="{ENCRE}" stroke-width="1.4"/>')
    return "".join(out)


def ceinture(xc: int, seed: int, largeur: int = 420, chicane: int = 110) -> str:
    """Une ceinture de barbelés : piquets en X, trois brins, une chicane ouverte au milieu."""
    r = rnd(seed)
    out = []
    xs = list(range(xc - largeur // 2, xc + largeur // 2 + 1, 70))
    for x in xs:
        if abs(x - xc) < chicane / 2:
            continue
        y = sol_y(x)
        h = r.randint(150, 200)
        out.append(f'<path d="M{x - 22} {y} L{x + 18} {y - h} M{x + 22} {y} L{x - 18} {y - h}" stroke="{ENCRE}" stroke-width="7"/>')
    gauche = [x for x in xs if x < xc - chicane / 2]
    droite = [x for x in xs if x > xc + chicane / 2]
    for groupe in (gauche, droite):
        for a, b in zip(groupe, groupe[1:]):
            for k, dy in enumerate((60, 110, 155)):
                out.append(fil(a, b, sol_y(a) - dy, seed * 31 + a + k))
    # fil arraché qui pend dans la chicane
    x0 = xc - chicane / 2 - 10
    out.append(f'<path d="M{x0:.0f} {sol_y(x0) - 110:.0f} Q{xc - 20} {sol_y(xc) - 40} {xc - 6} {sol_y(xc) - 8}" fill="none" stroke="{ENCRE}" stroke-width="1.6" stroke-dasharray="7 6"/>')
    return "".join(out)


def cratere(xc: int, larg: int, seed: int) -> str:
    """Trou d'obus décoratif : lèvres de terre et creux en contre-hachure, sans hauteur de jeu."""
    y = sol_y(xc)
    r = rnd(seed)
    l2 = larg // 2
    out = [f'<path d="M{xc - l2} {y} Q{xc - l2 + 30} {y - r.randint(26, 40)} {xc - l2 + 70} {y - 6} Q{xc} {y + 22} {xc + l2 - 70} {y - 6} Q{xc + l2 - 30} {y - r.randint(26, 40)} {xc + l2} {y} Z" fill="url(#terre)" stroke="{ENCRE}" stroke-width="3"/>',
           f'<path d="M{xc - l2 + 80} {y - 2} Q{xc} {y + 16} {xc + l2 - 80} {y - 2}" fill="none" stroke="{ENCRE}" stroke-width="1.5"/>']
    return "".join(out)


def plan3() -> str:
    out = []
    pts = " L".join(f"{x} {y}" for x, y in SOL)
    sol = f"M{pts} L{LARGEUR} {H} L0 {H} Z"
    out.append(f'<path d="{sol}" fill="url(#terre)"/>')
    # liseré de surface : boue retournée, plus sombre, sur 40 px
    out.append(f'<path d="M{pts}" fill="none" stroke="{ENCRE}" stroke-width="3"/>')
    bande = " L".join(f"{x} {y + 40}" for x, y in reversed(SOL))
    out.append(f'<path d="M{pts} L{bande} Z" fill="url(#boue)"/>')
    out.append(f'<path d="M{" L".join(f"{x} {y + 40}" for x, y in SOL)}" fill="none" stroke="{ENCRE}" stroke-width="1.5"/>')

    # 1. Le parapet : talus de sacs au départ, le dernier sac (détail parapet_sac à 600)
    out.append(f'<path d="M0 900 L0 760 L120 744 L260 790 L360 900 Z" fill="url(#sacs)" stroke="{ENCRE}" stroke-width="3"/>')
    out.append(f'<path d="M560 900 Q560 860 600 858 Q640 860 640 900 Z" fill="url(#h1)" stroke="{ENCRE}" stroke-width="3"/>')
    out.append(f'<rect x="586" y="872" width="28" height="14" fill="{PAPIER}" stroke="{ENCRE}" stroke-width="1.5"/>')
    out.append(f'<path d="M592 876 L592 882 M598 876 L604 876 L598 882 L604 882 M608 876 L608 882" stroke="{ENCRE}" stroke-width="1.2"/>')

    # 2. Le poste avancé, sur la crête (780) : îlot de sacs, registre, bougie, boyau effondré
    out.append(f'<path d="M1830 780 L1850 690 L2120 682 L2140 780 Z" fill="url(#sacs)" stroke="{ENCRE}" stroke-width="3"/>')
    out.append(f'<path d="M2760 780 L2770 700 L3080 694 L3100 780 Z" fill="url(#sacs)" stroke="{ENCRE}" stroke-width="3"/>')
    # caisse et registre (détail poste_registre à 2000)
    out.append(f'<rect x="1950" y="730" width="100" height="50" fill="url(#planches)" stroke="{ENCRE}" stroke-width="3"/>')
    out.append(f'<path d="M1966 730 L1974 718 L2032 718 L2040 730 Z" fill="{PAPIER}" stroke="{ENCRE}" stroke-width="2"/>')
    out.append(f'<path d="M2003 718 L2003 730" stroke="{ENCRE}" stroke-width="1.5"/>')
    # bougie dans une boîte de conserve (détail poste_bougie à 2400), flamme en papier nu
    out.append(f'<rect x="2378" y="736" width="44" height="44" fill="url(#h2)" stroke="{ENCRE}" stroke-width="3"/>')
    out.append(f'<path d="M2378 736 L2370 718 M2422 736 L2430 720" stroke="{ENCRE}" stroke-width="2"/>')
    out.append(f'<rect x="2394" y="748" width="12" height="22" fill="{PAPIER}" stroke="{ENCRE}" stroke-width="1.6"/>')
    out.append(f'<path d="M2400 746 Q2394 736 2400 724 Q2406 736 2400 746 Z" fill="{PAPIER}" stroke="{ENCRE}" stroke-width="1.6"/>')
    # boyau effondré qui plonge sous le poste (VersBoyau à 2650) : bouche noire, planches cassées
    out.append(f'<path d="M2580 780 Q2590 690 2650 684 Q2712 690 2720 780 Z" fill="{ENCRE}"/>')
    out.append(f'<path d="M2570 700 L2732 716 M2600 684 L2640 746" stroke="{ENCRE}" stroke-width="12"/>')
    out.append(f'<path d="M2572 700 L2730 716" stroke="{PAPIER}" stroke-width="2" stroke-dasharray="10 14"/>')
    # nos barbelés : la chicane de Brisse (3230) se ferme par fx_cheval-frise
    out.append(ceinture(3260, 7, largeur=560, chicane=140))

    # 3. Le brouillard : deux ceintures, le piquet au chiffon, le casque
    for i, xc in enumerate(CEINTURES):
        out.append(ceinture(xc, 11 + i))
    # piquet et chiffon noué (détail brouillard_piquet à 6200) : chiffon en lavis, jamais rouge
    out.append(f'<path d="M6200 900 L6206 700" stroke="{ENCRE}" stroke-width="8"/>')
    out.append(f'<path d="M6204 716 L6240 712 L6252 736 L6232 742 L6246 770 L6222 748 L6204 740 Z" fill="{LAVIS}" stroke="{ENCRE}" stroke-width="2"/>')
    out.append(fil(6206, 6330, 760, 91, 1.6))
    # casque posé à l'endroit (détail brouillard_casque à 7400)
    out.append(f'<path d="M7364 900 Q7366 856 7400 852 Q7434 856 7436 900 Z" fill="url(#h2)" stroke="{ENCRE}" stroke-width="3"/>')
    out.append(f'<path d="M7352 900 L7448 900" stroke="{ENCRE}" stroke-width="5"/>')
    # reste de fil où le mort est figé (e2_mort à 8256)
    out.append(f'<path d="M8150 900 L8160 760 M8380 900 L8370 770" stroke="{ENCRE}" stroke-width="7"/>')
    out.append(fil(8160, 8370, 790, 93))
    for xc, l, s in ((5900, 260, 1), (7000, 320, 2), (7900, 220, 3), (9100, 300, 4), (9600, 200, 5)):
        out.append(cratere(xc, l, s))

    # 4. Les trous d'obus : lèvres de plus en plus nombreuses, puis le grand trou (sacoche à 12900)
    for xc, l, s in ((10500, 280, 6), (10900, 240, 7), (11300, 360, 8), (11700, 300, 9)):
        out.append(cratere(xc, l, s))
    out.append(f'<path d="M12000 900 Q11960 880 11930 900 M13877 900 Q13920 878 13960 900" fill="none" stroke="{ENCRE}" stroke-width="3"/>')
    out.append(f'<path d="M12277 1060 L13600 1060 L13600 {H} L12277 {H} Z" fill="url(#h2)"/>')
    out.append(f'<path d="M12000 900 L12277 1060 L13600 1060 L13877 900" fill="none" stroke="{ENCRE}" stroke-width="3"/>')
    # flaque nette au fond du trou : papier nu, contour
    out.append(f'<path d="M12500 1062 Q12700 1074 12880 1062 Z" fill="{PAPIER}" stroke="{ENCRE}" stroke-width="1.5"/>')

    # 5. La souche du cantique : seul vertical, aplat d'encre, contour 3 px ; initiales en papier
    sx = SOUCHE_X
    out.append(f'<path d="M{sx - 70} 900 Q{sx - 54} 860 {sx - 48} 700 L{sx - 40} 520 L{sx - 18} 470 L{sx - 4} 498 L{sx + 10} 452 L{sx + 30} 506 L{sx + 44} 640 Q{sx + 52} 860 {sx + 78} 900 Z" fill="{ENCRE}" stroke="{ENCRE}" stroke-width="3"/>')
    out.append(f'<path d="M{sx - 40} 520 L{sx - 90} 470 M{sx + 36} 580 L{sx + 92} 540 L{sx + 110} 548" stroke="{ENCRE}" stroke-width="9" fill="none"/>')
    out.append(f'<path d="M{sx - 20} 690 L{sx - 20} 718 M{sx - 26} 690 L{sx - 14} 690 M{sx - 6} 718 L{sx} 690 L{sx + 6} 718 M{sx - 3} 706 L{sx + 3} 706 M{sx + 14} 704 L{sx + 18} 708 M{sx + 16} 700 L{sx + 16} 712" stroke="{PAPIER}" stroke-width="2"/>')
    out.append(f'<path d="M{sx - 30} 682 Q{sx} 674 {sx + 28} 682 L{sx + 28} 726 Q{sx} 734 {sx - 30} 726 Z" fill="none" stroke="{PAPIER}" stroke-width="1"/>')
    return "".join(out)


def plan2(w: int) -> str:
    """Champ retourné en lavis, lèvres de trous et piquets lointains."""
    forme = f"M{crete(0, w, 640, 10, 160, 22)} L{w} {H} L0 {H} Z"
    out = [f'<path d="{forme}" fill="{LAVIS}"/>']
    r = rnd(23)
    x = 160
    while x < w:
        if r.random() < .5:
            out.append(f'<path d="M{x - 60} 642 Q{x} {642 - r.randint(14, 26)} {x + 60} 642" fill="{LAVIS}" stroke="{LAVIS}" stroke-width="4"/>')
        else:
            h = r.randint(40, 80)
            out.append(f'<path d="M{x} 646 L{x + r.randint(-6, 6)} {646 - h}" stroke="{LAVIS}" stroke-width="6"/>')
            out.append(f'<path d="M{x} {646 - h + 14} L{x + 90} {646 - h + 26}" stroke="{LAVIS}" stroke-width="2"/>')
        x += r.randint(260, 620)
    return "".join(out)


def plan1(w: int) -> str:
    """Horizon de mine très bas ; le village aux cloches muettes se lève seulement à la fin."""
    forme = f"M{crete(0, w, 560, 6, 200, 32)} L{w} {H} L0 {H} Z"
    out = [f'<path d="{forme}" fill="{MINE}"/>']
    for sx in (500, 1300, 2300, 2900):
        out.append(f'<path d="M{sx} 562 L{sx + 2} 520 L{sx - 8} 508 M{sx + 2} 532 L{sx + 14} 524" stroke="{MINE}" stroke-width="5" fill="none"/>')
    # village : vu quand Tobie est à la souche (x monde 15700 au milieu de l'écran)
    vx = seuil(15700, VITESSES[1])
    toits = [(-260, 60, 40), (-190, 80, 54), (-110, 60, 36), (60, 70, 46), (140, 90, 60), (240, 60, 34)]
    for dx, larg, haut in toits:
        x0 = vx + dx
        out.append(f'<path d="M{x0} 562 L{x0} {562 - haut} L{x0 + larg / 2:.0f} {562 - haut - 26} L{x0 + larg} {562 - haut} L{x0 + larg} 562 Z" fill="{MINE}"/>')
    # clocher sans cloche, même motif qu'à l'étape 1 : la baie vide en papier
    out.append(f'<path d="M{vx - 24} 562 L{vx - 24} 400 L{vx} 352 L{vx + 24} 400 L{vx + 24} 562 Z" fill="{MINE}"/>')
    out.append(f'<rect x="{vx - 12}" y="410" width="24" height="28" fill="{PAPIER}"/>')
    return "".join(out)


def plan0(w: int) -> str:
    """Ciel de gaz : quelques traînées de mine, pas de soleil."""
    out = [f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>']
    r = rnd(42)
    for _ in range(18):
        y = r.randint(80, 420)
        x = r.randint(-300, w)
        out.append(f'<path d="M{x} {y} H{x + r.randint(400, 1100)}" stroke="{MINE}" stroke-width="{r.choice((1.2, 1.6, 2.4))}" opacity=".7"/>')
    return "".join(out)


def plan4(w: int) -> str:
    """Premier plan clairsemé : mottes et piquets en aplat d'encre, de plus en plus rares."""
    out = []
    r = rnd(52)
    x = 500
    pas = 1200
    while x < w:
        larg = r.randint(140, 300)
        out.append(f'<path d="M{x} {H} Q{x + larg * .3:.0f} {H - r.randint(150, 230)} {x + larg * .6:.0f} {H - r.randint(120, 200)} T{x + larg} {H} Z" fill="{ENCRE}"/>')
        if r.random() < .45:
            px = x + larg // 2
            top = H - r.randint(360, 480)
            out.append(f'<path d="M{px} {H - 120} L{px + r.randint(-20, 20)} {top}" stroke="{ENCRE}" stroke-width="14"/>')
        x += larg + pas + r.randint(0, 900)
        pas += 90          # chaque écran plus vide que le précédent
    return "".join(out)


def ecrire_tuiles(plan: int, nom: str, contenu: str, largeur: int) -> int:
    DST.mkdir(parents=True, exist_ok=True)
    n = math.ceil(largeur / TUILE)
    for i in range(n):
        x0 = i * TUILE
        w = min(TUILE, largeur - x0)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="{x0} 0 {w} {H}">'
               f'{DEFS2}{contenu}</svg>\n')
        (DST / f"env_e2_plan{plan}_{nom}_{i + 1:02d}.svg").write_text(svg, encoding="utf-8")
    return n


def fx() -> None:
    """Calques séparés que le code montre, cache ou déplace."""
    FX.mkdir(parents=True, exist_ok=True)
    # trois bandes de brouillard en aplat de mine, bord haut découpé net, raccord en boucle sur x
    for i, (haut, amp, seed) in enumerate(((420, 14, 71), (620, 10, 72), (850, 6, 73))):
        r = rnd(seed)
        pts = [(0, haut)]
        x = 0
        while x < 1920 - 160:
            x += r.randint(220, 460)
            pts.append((x, haut + r.uniform(-amp, amp)))
        pts.append((1920, haut))
        d = "M" + " L".join(f"{px:.0f} {py:.0f}" for px, py in pts) + f" L1920 {H} L0 {H} Z"
        (FX / f"fx_brouillard_{i + 1:02d}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="{H}" viewBox="0 0 1920 {H}"><path d="{d}" fill="{MINE}"/></svg>\n')
    # cheval de frise qui ferme la chicane de Brisse (retiré quand le verrou s'ouvre)
    (FX / "fx_cheval-frise.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="220" viewBox="0 0 200 220">{DEFS2}'
        f'<path d="M20 214 L90 20 M110 20 L180 214 M30 120 L170 120" stroke="{ENCRE}" stroke-width="8"/>'
        f'<path d="M20 214 L180 214" stroke="{ENCRE}" stroke-width="5"/>'
        + fil(30, 170, 70, 81) + fil(26, 174, 160, 82) + '</svg>\n')
    # fil qui retombe derrière Tobie à la sortie du brouillard (verrou de retour)
    (FX / "fx_fil-retombe.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="240" height="200" viewBox="0 0 240 200">{DEFS2}'
        f'<path d="M14 196 L26 30" stroke="{ENCRE}" stroke-width="7"/>'
        + fil(26, 230, 60, 83) + fil(26, 220, 120, 84) + fil(26, 236, 170, 85) + '</svg>\n')
    # la sacoche de Matthieu, seule, sans corps ; plaque de coureur en papier, sans chiffre lisible
    (FX / "fx_sacoche-matthieu.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="120" height="90" viewBox="0 0 120 90">{DEFS2}'
        f'<path d="M10 86 L16 30 Q60 18 104 30 L110 86 Z" fill="url(#h1)" stroke="{ENCRE}" stroke-width="3"/>'
        f'<path d="M16 30 Q60 52 104 30" fill="none" stroke="{ENCRE}" stroke-width="3"/>'
        f'<path d="M30 30 Q24 4 60 6 Q96 4 90 30" fill="none" stroke="{ENCRE}" stroke-width="4"/>'
        f'<rect x="46" y="54" width="28" height="18" fill="{PAPIER}" stroke="{ENCRE}" stroke-width="1.5"/>'
        f'<path d="M52 63 L68 63" stroke="{MINE}" stroke-width="2"/></svg>\n')


def main() -> None:
    total = 0
    total += ecrire_tuiles(0, "ciel", plan0(largeur_plan(VITESSES[0])), largeur_plan(VITESSES[0]))
    total += ecrire_tuiles(1, "lointain", plan1(largeur_plan(VITESSES[1])), largeur_plan(VITESSES[1]))
    total += ecrire_tuiles(2, "milieu", plan2(largeur_plan(VITESSES[2])), largeur_plan(VITESSES[2]))
    total += ecrire_tuiles(3, "surface", plan3(), LARGEUR)
    total += ecrire_tuiles(4, "premier-plan", plan4(largeur_plan(VITESSES[4])), largeur_plan(VITESSES[4]))
    fx()
    print(f"{total} tuiles + 6 calques fx dans art/src/")


if __name__ == "__main__":
    main()
