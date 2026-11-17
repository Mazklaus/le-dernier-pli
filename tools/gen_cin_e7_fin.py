#!/usr/bin/env python3
"""Génère les deux cinématiques de fin de l'étape 7 (planche « Le Dernier Pli », validée GD) :
e7_moule_brise et e7_corde_tiree. Plein écran, en gros plan : la table de pierre des gravures
d'épilogue b et c (tools/gen_cin_epilogues.py) agrandie 1,5 fois (le cadre de la gravure, 720 px
de haut, remplit les 1080 de l'écran), même encre, mêmes motifs. Réemploi : moule, main, corde ; e7_corde_tiree reprend l'image 0 du moule (fermé : le pacte
tient encore).

  cin_moule_01   fond : la table, la main ouverte de Tobie, le ruban (tout ce qui ne bouge pas) ;
  cin_moule_02   6 images de ZONE_MOULE, grille 3 x 2, le moule seul sur fond transparent (posé sur
                 le fond du moule ou de la corde) : 0 le moule fermé, 1 la fente court sur
                 le fer, 2 les mâchoires s'écartent, 3 la cire noire sort, 4 elle coule,
                 5 elle est figée (= gravure b) ;
  cin_corde_01   fond de la corde : la table et le ruban, sans la main ouverte (l'autre main va
                 tenir la corde, son bras traverse l'image) ;
  cin_corde_02   la corde de la grande cloche, droite, sur fond transparent (le jeu la tourne) ;
  cin_corde_03   la main serrée et la manche, sur fond transparent, dans le repère de la corde.
Les planches de la corde servent aussi à l'épilogue « cloches » (la corde qui va et vient seule).

Usage : python3 tools/gen_cin_e7_fin.py
"""
from __future__ import annotations

import math

from gen_cin_e1 import DST, H, W, bande, svg
from gen_cin_epilogues import CY0, CY1, main_ouverte, main_serree, moule, ruban, table_pierre
from gen_decors_e1_surface import MINE, rnd
from gen_decors_e1_surface import ENCRE, LAVIS, PAPIER

# gros plan : le cadre de la gravure (y 50 à 770) agrandi à la hauteur de l'écran, centré en x
ECHELLE = 1.5
GROS_PLAN = f'translate({W / 2 - W / 2 * ECHELLE:.0f} {-CY0 * ECHELLE:.0f}) scale({ECHELLE})'
MOULE = (980, 470)
ZONE_MOULE = (560, 480, 860, 480)
# la corde, dans le repère de la gravure c : du haut du cadre au bas, la main aux 78 centièmes
C_X0, C_Y0, C_X1, C_Y1 = 1600, CY0 - 40, 470, CY1 + 40
PRISE_T = .78
LONGUEUR_CORDE = 2000
LARGEUR_CORDE = 34
ST = f'stroke="{ENCRE}" fill="none"'


def ecran(x: float, y: float) -> tuple[float, float]:
    """Un point du repère de la gravure, dans l'écran du gros plan."""
    return W / 2 - W / 2 * ECHELLE + x * ECHELLE, (y - CY0) * ECHELLE


def gros_plan(contenu: str) -> str:
    return f'<g transform="{GROS_PLAN}">{contenu}</g>'


def table() -> str:
    """La table de pierre des gravures b et c, mais le mur du fond en aplat de lavis gravé de
    quelques traits au lieu d'une hachure serrée plein écran (au gros plan, elle pesait 1,4 Mo)."""
    t = table_pierre()
    i = t.index('<path d="M260 330')
    r = rnd(711)
    traits = "".join(f'<path d="M{x} {y} l{r.randint(40, 120)} {r.randint(-3, 3)}" stroke="{ENCRE}" stroke-width="1.4" opacity=".5"/>'
                     for x, y in ((r.randint(0, W), r.randint(0, 330)) for _ in range(36)))
    return f'<rect width="{W}" height="{H}" fill="{PAPIER}"/><rect width="{W}" height="{H}" fill="{LAVIS}" opacity=".72"/>{traits}' + t[i:]


def ruban_pose() -> str:
    return ruban("M1270 600 C1330 560 1420 570 1440 620 C1456 664 1400 690 1350 668 C1310 650 1320 600 1380 590 "
                 "C1450 580 1520 620 1580 610", 11)


def fente(cx: float, cy: float) -> str:
    """La fente qui court sur le fer du moule fermé (avant qu'il cède), avec un éclat de papier."""
    return (f'<g transform="translate({cx} {cy}) rotate(-6)">'
            f'<path d="M6 -58 L-4 -30 L10 -10 L-2 14 L8 34 L0 54" fill="none" stroke="{ENCRE}" stroke-width="6" stroke-linejoin="round"/>'
            f'<path d="M6 -58 L-4 -30 L10 -10 L-2 14" fill="none" stroke="{PAPIER}" stroke-width="2"/></g>')


def moule_ecarte(cx: float, cy: float, ouverture: float) -> str:
    """Les deux mâchoires qui s'écartent : ouverture 0 (à peine) à 1 (la pose brisée de la gravure b),
    sans la cire. On interpole la pose brisée de gen_cin_epilogues.moule()."""
    gauche = (cx - 120 * ouverture - 18 * (1 - ouverture), cy, -16 * ouverture)
    droite = (cx + 130 * ouverture + 18 * (1 - ouverture), cy + 24 * ouverture, 22 * ouverture)
    entier = moule(cx, cy, brise=True)
    # la pose brisée est faite de deux groupes <g transform=...> après la coulée : on les reprend
    groupes = entier[entier.index('<g transform'):]
    g1, g2 = groupes.split('</g>', 1)[0] + '</g>', groupes.split('</g>', 1)[1]
    g1 = g1.split('>', 1)[1]
    g2 = g2.split('>', 1)[1]
    return (f'<g transform="translate({gauche[0]:.0f} {gauche[1]:.0f}) rotate({gauche[2]:.0f})">{g1}'
            f'<g transform="translate({droite[0]:.0f} {droite[1]:.0f}) rotate({droite[2]:.0f})">{g2}')


def cire_sortie(cx: float, cy: float, k: int) -> str:
    """La cire noire qui sort d'entre les mâchoires (k 3), coule (k 4) ; à k 5, c'est la pose figée
    de la gravure b (dessinée par moule(brise=True))."""
    if k == 3:
        return (f'<path d="M{cx - 40} {cy + 6} Q{cx - 10} {cy - 14} {cx + 30} {cy + 8} Q{cx + 44} {cy + 30} {cx + 20} {cy + 46} '
                f'Q{cx - 10} {cy + 50} {cx - 30} {cy + 34} Q{cx - 50} {cy + 20} {cx - 40} {cy + 6} Z" fill="{ENCRE}"/>')
    return (f'<path d="M{cx - 70} {cy + 10} Q{cx - 20} {cy - 20} {cx + 40} {cy + 10} Q{cx + 70} {cy + 40} {cx + 40} {cy + 70} '
            f'Q{cx + 22} {cy + 96} {cx + 36} {cy + 120} Q{cx + 40} {cy + 136} {cx + 26} {cy + 138} Q{cx + 10} {cy + 130} {cx + 14} {cy + 104} '
            f'Q{cx + 4} {cy + 90} {cx - 40} {cy + 70} Q{cx - 90} {cy + 40} {cx - 70} {cy + 10} Z" fill="{ENCRE}"/>'
            f'<path d="M{cx - 30} {cy + 6} Q{cx} {cy - 4} {cx + 24} {cy + 12}" stroke="{LAVIS}" stroke-width="3" fill="none"/>')


def image_moule(k: int) -> str:
    cx, cy = MOULE
    o = []
    if k == 0:
        o.append(moule(cx, cy, brise=False))
    elif k == 1:
        o.append(moule(cx, cy, brise=False) + fente(cx, cy))
    elif k == 2:
        o.append(moule_ecarte(cx, cy, .35))
    elif k in (3, 4):
        o.append(cire_sortie(cx, cy, k) + moule_ecarte(cx, cy, .8 if k == 3 else 1.0))
    else:
        o.append(moule(cx, cy, brise=True))
    return gros_plan("".join(o))


def fond_moule() -> str:
    """Tout sauf le moule : la zone animée le recouvre entièrement."""
    return gros_plan(table() + main_ouverte(560, 560) + ruban_pose())


def fond_corde() -> str:
    return gros_plan(table() + ruban_pose())


def corde() -> str:
    """La corde droite, verticale, centrée sur x 0 de son repère (le jeu la tourne et la pose à la
    prise) : torons en biais, à la même cadence que la gravure c."""
    w = LARGEUR_CORDE * ECHELLE
    lg = LONGUEUR_CORDE * ECHELLE
    pas = math.hypot(C_X1 - C_X0, C_Y1 - C_Y0) / 40 * ECHELLE
    torons = "".join(f'<path d="M{-12 * ECHELLE:.1f} {y - 8 * ECHELLE:.1f} L{10 * ECHELLE:.1f} {y + 10 * ECHELLE:.1f}" '
                     f'stroke="{ENCRE}" stroke-width="{3 * ECHELLE}"/>' for y in [k * pas for k in range(int(lg / pas) + 1)])
    larg = int(w + 8)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{larg}" height="{int(lg)}" viewBox="{-larg / 2} 0 {larg} {int(lg)}">'
            f'<rect x="{-w / 2}" y="0" width="{w}" height="{lg}" fill="{ENCRE}"/>'
            f'<rect x="{-w / 2 + 5 * ECHELLE}" y="0" width="{w - 10 * ECHELLE}" height="{lg}" fill="{PAPIER}"/>{torons}</svg>\n')


# la main, dans le repère de la corde (axe y le long de la corde, prise en 0, 0) : manche jusqu'à
# x -900, doigts jusqu'à x 44, de y -150 à 160
MAIN_BOITE = (-900, -160, 960, 330)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    (DST / "cin_moule_01.svg").write_text(svg(fond_moule()), encoding="utf-8")
    (DST / "cin_moule_02.svg").write_text(bande([image_moule(k) for k in range(6)], ZONE_MOULE, 3), encoding="utf-8")
    (DST / "cin_corde_01.svg").write_text(svg(fond_corde()), encoding="utf-8")
    (DST / "cin_corde_02.svg").write_text(corde(), encoding="utf-8")
    x, y, w, h = MAIN_BOITE
    s = ECHELLE
    (DST / "cin_corde_03.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(w * s)}" height="{int(h * s)}" viewBox="{x} {y} {w} {h}">'
        + svg("").split(">", 1)[1].rsplit("</svg>", 1)[0] + main_serree(0, 0, 0) + "</svg>\n", encoding="utf-8")
    px, py = ecran(C_X0 + (C_X1 - C_X0) * PRISE_T, C_Y0 + (C_Y1 - C_Y0) * PRISE_T)
    ang = math.degrees(math.atan2(C_Y1 - C_Y0, C_X1 - C_X0)) - 90
    print(f"e7 fin : 5 planches ; prise de la corde à l'écran ({px:.0f}, {py:.0f}), angle {ang:.2f}°")


if __name__ == "__main__":
    main()
