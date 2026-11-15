#!/usr/bin/env python3
"""Génère les cinématiques de l'étape 7 (planches validées par le GD) : e7_descente et
e7_ouverture_sceau.

L'écran de l'étape 7 est clair, presque blanc, sans accent (papier_etapes.gd). Le seul rouge est
le ruban du pli (rouge exact, comme partout). Aucune cloche ne bouge ni ne sonne ; aucun battant
n'est montré (la forme sous la cloche reste au choix « Regarder la cloche qui bouge »).

e7_descente, 10 s, au début de e7_cloches : quatre plans.
  cin_descente_01  plan 1, 1920 x 1080 : en haut, la couronne de la plus grande cloche,
                   l'escalier qui tourne autour d'elle ; des cloches pendues à toutes les
                   hauteurs, la bouche bouchée de cire noire coulée en larmes.
  cin_descente_02  plan 2, 1920 x (1080 + PAN_2) : le flanc de la grande cloche et l'escalier,
                   plus près ; la caméra descend avec Tobie : le fond monte de PAN_2 px.
  cin_descente_03  plan 2, avant-plan transparent 1920 x (1080 + 2 x PAN_2) : deux cloches toutes
                   proches qui défilent deux fois plus vite.
  cin_descente_04  plan 3, 1920 x 1080 : gros plan immobile sur la lèvre d'une cloche, la cire
                   noire figée en larmes. Rien ne bouge (2 s).
  cin_descente_05  plan 4, 1920 x 1080 : en bas, la lèvre de la grande cloche ferme le ciel ;
                   l'escalier s'enfonce dans un blanc surexposé qui le mange presque.
  cin_descente_06  Tobie qui descend des marches, de profil vers la droite : 4 images de
                   120 x 200 transparentes, en ligne, pieds en (60, 196) ; à retourner (flip_h)
                   il descend toujours vers la droite (la moitié devant de la spirale) ; à mettre
                   à l'échelle par plan (ECHELLES), le long des clés CHEMINS (une marche et une
                   image toutes les 0,2 s ; caché quand l'escalier passe derrière la cloche).

e7_ouverture_sceau, 8 s, branche « Briser le sceau » de e7_sceau : un seul gros plan.
  cin_sceau_01     le fond 1920 x 1080 (l'image 0 entière).
  cin_sceau_02     10 images de la zone ZONE_SCEAU, grille 3 x 4 (hframes 3, vframes 4) :
                   0 le pli fermé dans les mains sales de Tobie, le pouce gauche bandé ; la
                     feuille épaisse pliée en trois, la cire noire à cheval sur le dernier pli,
                     le ruban rouge qui en fait le tour ;
                   1 le pouce droit appuie, la cire se fend ;
                   2 la cire éclate, le ruban se relâche ; 3 les éclats tombent, le ruban glisse ;
                   4 le ruban sort du cadre par le bas ; 5 plus de ruban, le pli sans cire ;
                   6 le premier tiers s'ouvre vers le haut ; 7 le dernier tiers retombe ;
                   8 la feuille penche vers la main gauche qui remonte ; 9 l'index gauche glisse
                     sous la première ligne. Durées : TEMPS_SCEAU.

Usage : python3 tools/gen_cin_e7.py
"""
from __future__ import annotations

import math
import random

from gen_cin_e1 import DST, H, W, bande, svg
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER

ROUGE = "#9B1C1C"
STP = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'

# Tobie dans chaque plan de e7_descente : échelle du sprite, et ses clés (instant depuis le début
# du plan, image, pieds x, y ; image -1 : caché derrière la grande cloche), calculées sur les
# marches dessinées et affichées par main(). Plan 2 : coordonnées dans le fond qui monte.
ECHELLES = {1: .55, 2: 1.0, 4: .35}
CHEMINS: dict[int, list] = {}
# Plan 2 : la caméra descend avec Tobie ; le fond monte de PAN_2 px (y 0 à -PAN_2) et
# l'avant-plan de 2 x PAN_2, linéairement de 0,1 s à 2,7 s, comme ses marches (calculé par plan_2()).
PAN_2 = 0
# e7_ouverture_sceau : durée de chaque image (s), total 8 s.
TEMPS_SCEAU = [1.5, 0.8, 0.3, 0.3, 0.3, 0.4, 0.8, 0.8, 0.3, 2.5]
ZONE_SCEAU = (300, 140, 1320, 940)


# ----------------------------------------------------------------------------- les cloches
def cloche(x: float, y: float, h: float, cire: bool = True, seed: int = 0, trait: float = 3.0,
           corde: bool = True, larmes: float = 1.0) -> str:
    """Une cloche pendue, (x, y) le haut de la couronne, h sa hauteur, immobile ; le bronze
    patiné (quelques taches de lavis pâle), deux moulures ; la bouche bouchée de cire noire qui a
    coulé et figé en larmes."""
    r = random.Random(seed)
    w = h * .9
    c = h * .1
    p = (f"M{x - w * .1:.0f} {y + c:.0f} Q{x - w * .3:.0f} {y + c:.0f} {x - w * .31:.0f} {y + h * .34:.0f} "
         f"Q{x - w * .33:.0f} {y + h * .74:.0f} {x - w * .5:.0f} {y + h:.0f} "
         f"Q{x:.0f} {y + h * 1.05:.0f} {x + w * .5:.0f} {y + h:.0f} "
         f"Q{x + w * .33:.0f} {y + h * .74:.0f} {x + w * .31:.0f} {y + h * .34:.0f} "
         f"Q{x + w * .3:.0f} {y + c:.0f} {x + w * .1:.0f} {y + c:.0f} Z")
    o = []
    if corde:
        o.append(f'<path d="M{x:.0f} {y - 3000:.0f} V{y + 4:.0f}" stroke="{ENCRE}" stroke-width="{max(1.2, trait * .5):.1f}"/>')
    # la tête plate de la cloche et sa couronne : trois anses serrées
    cw = w * .06
    o += [f'<path d="M{x - cw * 1.5:.0f} {y + c:.0f} V{y + c * .55:.0f} H{x + cw * 1.5:.0f} V{y + c:.0f}" fill="{PAPIER}" {STP} stroke-width="{trait:.1f}"/>']
    for k in (-1, 0, 1):
        ax = x + k * cw
        o.append(f'<path d="M{ax - cw * .45:.0f} {y + c * .55:.0f} Q{ax - cw * .5:.0f} {y:.0f} {ax:.0f} {y:.0f} Q{ax + cw * .5:.0f} {y:.0f} {ax + cw * .45:.0f} {y + c * .55:.0f}" '
                 f'fill="none" {STP} stroke-width="{trait * 1.2:.1f}"/>')
    o += [f'<path d="{p}" fill="{PAPIER}" {STP} stroke-width="{trait:.1f}"/>',
          f'<path d="M{x - w * .3:.0f} {y + h * .4:.0f} Q{x:.0f} {y + h * .44:.0f} {x + w * .3:.0f} {y + h * .4:.0f} '
          f'M{x - w * .36:.0f} {y + h * .79:.0f} Q{x:.0f} {y + h * .84:.0f} {x + w * .36:.0f} {y + h * .79:.0f}" fill="none" '
          f'stroke="{ENCRE}" stroke-width="{trait * .45:.1f}"/>']
    for _ in range(3):   # la patine : de petites taches, à la taille d'une main quelle que soit la cloche
        e = min(w * .05, 28)
        o.append(f'<ellipse cx="{x + r.uniform(-w * .22, w * .22):.0f}" cy="{y + h * r.uniform(.5, .75):.0f}" rx="{e * r.uniform(.6, 1.4):.0f}" '
                 f'ry="{e * r.uniform(.3, .6):.0f}" fill="{LAVIS}" opacity=".12"/>')
    if cire:
        o.append(f'<path d="M{x - w * .5:.0f} {y + h:.0f} Q{x:.0f} {y + h * 1.05:.0f} {x + w * .5:.0f} {y + h:.0f} '
                 f'Q{x:.0f} {y + h * 1.13:.0f} {x - w * .5:.0f} {y + h:.0f} Z" fill="{ENCRE}" {STP} stroke-width="{trait:.1f}"/>')
        for _ in range(r.randint(4, 7)):
            gx = x + r.uniform(-w * .42, w * .42)
            gl = min(h * r.uniform(.05, .2), r.uniform(40, 110)) * larmes
            e = min(max(3.0, h * .012), 9) * larmes
            y0 = y + h * 1.02
            o.append(f'<path d="M{gx - e:.0f} {y0:.0f} Q{gx - e * .4:.0f} {y0 + gl * .6:.0f} {gx - e * 1.3:.0f} {y0 + gl:.0f} '
                     f'Q{gx:.0f} {y0 + gl + e * 2.4:.0f} {gx + e * 1.3:.0f} {y0 + gl:.0f} Q{gx + e * .4:.0f} {y0 + gl * .6:.0f} {gx + e:.0f} {y0:.0f} Z" fill="{ENCRE}"/>')
    return "".join(o)


def escalier(cx: float, y0: float, y1: float, rx: float, pas: float = 60, couleur: str = ENCRE,
             trait: float = 1.0) -> tuple[str, list]:
    """L'escalier qui tourne autour du fût de la grande cloche, en élévation : marches, limon,
    main courante, quelques barreaux ; seule la moitié devant est dessinée. Rend le dessin et
    les marches (x, y, sens : +1 si l'on descend vers la droite)."""
    o, seg, marches = [], [], []
    t, y = 0.0, y0
    st = f'stroke="{couleur}" stroke-linejoin="round" stroke-linecap="round"'

    def fin() -> None:
        if len(seg) > 1:
            lim = " L".join(f"{a:.0f} {b + 14:.0f}" for a, b in seg)
            rail = " L".join(f"{a:.0f} {b - 72:.0f}" for a, b in seg)
            o.append(f'<path d="M{lim}" fill="none" {st} stroke-width="{4 * trait:.1f}"/>'
                     f'<path d="M{rail}" fill="none" {st} stroke-width="{2.4 * trait:.1f}"/>')
            for a, b in seg[::3]:
                o.append(f'<path d="M{a:.0f} {b:.0f} V{b - 72:.0f}" stroke="{couleur}" stroke-width="{1.4 * trait:.1f}"/>')
        seg.clear()
    while y < y1:
        x = cx + rx * math.sin(t)
        if math.cos(t) > 0:
            l = 70 * (0.6 + 0.4 * abs(math.cos(t)))
            o.append(f'<path d="M{x - l / 2:.0f} {y:.0f} h{l:.0f} v12 h{-l:.0f} Z" fill="{PAPIER}" {st} stroke-width="{2 * trait:.1f}"/>')
            seg.append((x, y))
            marches.append((x, y, 1 if math.cos(t + .22) * rx > 0 else -1))
        else:
            fin()
        t += .22
        y += pas * .22 / (2 * math.pi) * 6
    fin()
    return "".join(o), marches


def chemin_sur(marches: list, debut: int, n: int, t0: float = 0.0, dt: float = .2) -> list:
    """Tobie descend n marches à partir de la marche `debut`, toujours vers la droite sur la
    moitié devant : une clé par marche (instant, image du cycle, pieds x, y). Quand l'escalier
    passe derrière la grande cloche, une dernière clé (instant, -1, 0, 0) le cache jusqu'à la
    fin du plan."""
    ch = []
    prec = None
    for k in range(n):
        if debut + k >= len(marches):
            break
        x, y, _ = marches[debut + k]
        t = round(t0 + k * dt, 2)
        if prec is not None and abs(x - prec[0]) > 150:
            ch.append((t, -1, 0, 0))
            break
        ch.append((t, k % 4, round(x), round(y)))
        prec = (x, y)
    return ch


# ----------------------------------------------------------------------------- e7_descente
def descente_1() -> str:
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>']
    for k, (x, y, h) in enumerate([(220, 260, 150), (420, 120, 110), (610, 420, 190), (1500, 160, 120), (1700, 380, 170),
                                   (1820, 120, 90), (330, 640, 130), (1580, 700, 150), (120, 860, 100)]):
        o.append(cloche(x, y, h, seed=k, trait=2.4))
    o.append(cloche(980, 380, 1400, seed=9, trait=6))
    dessin, marches = escalier(980, 400, 1100, 480)
    o.append(dessin)
    CHEMINS[1] = chemin_sur(marches, 0, 12, 0.6)
    return svg("".join(o))


def debut_volee(marches: list, n: int = 1) -> int:
    """Indice de la première marche de la n-ième volée devant (après un saut derrière la cloche)."""
    sauts = [i for i in range(1, len(marches)) if abs(marches[i][0] - marches[i - 1][0]) > 150]
    return sauts[n - 1]


def plan_2() -> tuple[list, int, float]:
    """Les marches du plan 2, calées pour que Tobie commence sa volée à y 560 de l'écran ; la
    caméra le suit : le fond monte exactement de la hauteur qu'il descend (PAN_2)."""
    _, essai = escalier(960, 0, 4000, 660, pas=150)
    i = debut_volee(essai)
    dy = 560 - essai[i][1]
    _, marches = escalier(960, dy, 4000, 660, pas=150)
    fin = min(i + 13, len(marches) - 1)
    return marches, i, round(marches[fin][1] - marches[i][1])


def descente_2() -> str:
    marches, i, pan = plan_2()
    h = H + pan
    o = [f'<rect width="{W}" height="{h}" fill="{PAPIER}"/>', cloche(960, -900, 2700, seed=9, trait=7)]
    for k, (x, y, hc) in enumerate([(240, 900, 160), (1700, 1240, 140), (380, 1420, 110)]):
        if y < h + 40:
            o.append(cloche(x, y, hc, seed=50 + k, trait=2.4))
    dy = 560 - escalier(960, 0, 4000, 660, pas=150)[1][i][1]
    dessin, _ = escalier(960, dy, h + 120, 660, pas=150)
    o.append(dessin)
    CHEMINS[2] = chemin_sur(marches, i, 14, 0.1)
    return svg("".join(o), (0, 0, W, h))


def descente_3() -> str:
    """L'avant-plan du plan 2 : deux cloches toutes proches, sur fond transparent, deux fois
    plus haut que le pan du fond (elles défilent deux fois plus vite)."""
    h = H + 2 * PAN_2
    o = [cloche(150, 140, 520, seed=20, trait=8), cloche(1790, h - 760, 600, seed=21, trait=8)]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">'
            + svg("", (0, 0, 1, 1)).split("<defs>")[1].join(["<defs>", ""]).split("</svg>")[0] + "".join(o) + "</svg>\n")


def descente_4() -> str:
    return svg(f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>' + cloche(960, -760, 1560, seed=31, trait=9, larmes=2.2))


def descente_5() -> str:
    """En bas : la lèvre de la grande cloche ferme le ciel ; l'escalier s'enfonce dans le blanc,
    de plus en plus pâle, en traits de mine qui se perdent."""
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>',
         f'<path d="M-200 0 Q960 260 2120 0" fill="{PAPIER}" {STP} stroke-width="7"/>',
         f'<path d="M-200 0 Q960 300 2120 0 Q960 340 -200 0 Z" fill="{ENCRE}"/>']
    for k, (x, y, h) in enumerate([(260, 360, 110), (1660, 300, 90)]):
        o.append(f'<g opacity=".55">{cloche(x, y, h, seed=40 + k, trait=1.8)}</g>')
    dessin, marches = escalier(960, 400, 760, 300, pas=40, couleur=MINE, trait=.8)
    o.append(dessin)
    # plus bas, la lumière mange l'escalier : seuls des bouts de marches
    rr = random.Random(7)
    for x, y, _ in marches:
        pass
    _, bas = escalier(960, 760, 1080, 300, pas=40)
    for x, y, _ in bas:
        if rr.random() < .5 - (y - 760) / 900:
            o.append(f'<path d="M{x - 20:.0f} {y:.0f} h{rr.uniform(14, 34):.0f}" stroke="{MINE}" stroke-width="1.2"/>')
    # le blanc surexposé monte du bas et mange les marches : un voile de papier (le papier est
    # déjà le plus clair de l'écran, le shader écrête tout ce qui est plus blanc)
    o.append(f'<defs><radialGradient id="blanc" cx="50%" cy="100%" r="78%">'
             f'<stop offset="0" stop-color="{PAPIER}"/><stop offset=".5" stop-color="{PAPIER}" stop-opacity=".92"/>'
             f'<stop offset="1" stop-color="{PAPIER}" stop-opacity="0"/></radialGradient></defs>'
             f'<rect x="-200" y="300" width="{W + 400}" height="{H - 300}" fill="url(#blanc)"/>')
    tout = marches + bas
    volee = next(i for i in range(1, len(tout)) if abs(tout[i][0] - tout[i - 1][0]) > 150)
    CHEMINS[4] = chemin_sur(tout, volee, 12, 0.3, .2)
    return svg("".join(o))


def tobie_marche(k: int) -> str:
    """Tobie de profil vers la droite, qui descend une marche, pieds en (60, 196) : capuche de
    toile, capote, sacoche ; k : 0 et 2 jambes jointes, 1 et 3 un pied qui descend."""
    jambes = {0: ("M52 150 L50 196", "M62 150 L66 196"), 1: ("M52 150 L44 192", "M62 150 L78 172 L80 200"),
              2: ("M54 150 L54 196", "M60 150 L60 196"), 3: ("M52 150 L62 186 L66 202", "M62 150 L48 194")}[k]
    b = (0, -2, 0, -2)[k]
    return (f'<g transform="translate(0 {b})">'
            f'<path d="{jambes[0]}" fill="none" {STP} stroke-width="7"/><path d="{jambes[1]}" fill="none" {STP} stroke-width="7"/>'
            f'<path d="M40 70 Q58 62 76 72 L82 152 L36 152 Z" fill="url(#h2)" {STP} stroke-width="3"/>'
            f'<path d="M30 100 L44 98 L44 128 L30 128 Z" fill="url(#h1)" {STP} stroke-width="2.4"/>'
            f'<path d="M74 84 Q90 112 84 140" fill="none" {STP} stroke-width="7"/>'
            f'<circle cx="84" cy="142" r="6" fill="{PAPIER}" {STP} stroke-width="2"/>'
            f'<path d="M44 72 Q40 40 62 26 Q84 22 92 40 Q96 56 80 72 Z" fill="url(#h1)" {STP} stroke-width="3"/>'
            f'<path d="M72 42 Q82 40 86 48 L92 54 L86 58 Q86 66 76 68 Q70 58 72 42 Z" fill="{PAPIER}" {STP} stroke-width="2"/>'
            f'<path d="M80 50 l3 0" stroke="{ENCRE}" stroke-width="2.4"/>'
            f'<path d="M66 86 l6 14" stroke="{ROUGE}" stroke-width="3"/></g>')


def ligne_tobie() -> str:
    corps = "".join(f'<svg x="{k * 120}" y="0" width="120" height="200" viewBox="0 0 120 200">{tobie_marche(k)}</svg>' for k in range(4))
    return svg(corps, (0, 0, 480, 200)).replace(f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>', "")


# ----------------------------------------------------------------------------- e7_ouverture_sceau
def salete(x: float, y: float, rx: float, ry: float, seed: int) -> str:
    """Crasse et griffures sur une main : taches de lavis pâle, petites entailles."""
    r = random.Random(seed)
    o = []
    for _ in range(5):
        o.append(f'<ellipse cx="{x + r.uniform(-rx, rx) * .7:.0f}" cy="{y + r.uniform(-ry, ry) * .7:.0f}" rx="{r.uniform(10, 26):.0f}" '
                 f'ry="{r.uniform(6, 14):.0f}" fill="{LAVIS}" opacity=".28"/>')
    for _ in range(3):
        gx, gy = x + r.uniform(-rx, rx) * .6, y + r.uniform(-ry, ry) * .6
        o.append(f'<path d="M{gx:.0f} {gy:.0f} l{r.uniform(14, 26):.0f} {r.uniform(-8, 8):.0f}" stroke="{ENCRE}" stroke-width="2.4"/>')
    return "".join(o)


def doigt(x0: float, y0: float, x1: float, y1: float, ep: float = 60, bande_: bool = False) -> str:
    """Un pouce ou un index, de la base au bout, l'ongle noirci ; bande_ : le pouce entaillé à
    l'étape 5, enroulé d'un chiffon noué dont un bout pend."""
    a = math.atan2(y1 - y0, x1 - x0)
    l = math.hypot(x1 - x0, y1 - y0)
    o = [f'<g transform="translate({x0:.0f} {y0:.0f}) rotate({math.degrees(a):.1f})">',
         f'<rect x="0" y="{-ep / 2}" width="{l:.0f}" height="{ep}" rx="{ep / 2}" fill="{PAPIER}" {STP} stroke-width="5"/>',
         f'<path d="M{l - 44:.0f} {-ep / 2 + 12} Q{l - 14:.0f} {-ep / 2 + 10} {l - 12:.0f} 0 Q{l - 14:.0f} {ep / 2 - 10} {l - 44:.0f} {ep / 2 - 12} Z" '
         f'fill="{LAVIS}" opacity=".55" {STP} stroke-width="3"/>',
         f'<path d="M{l * .45:.0f} {-ep / 2 + 6} q6 {ep * .4:.0f} 0 {ep - 12:.0f}" fill="none" stroke="{ENCRE}" stroke-width="2"/>']
    if bande_:
        for k in range(4):
            bx = l * .18 + k * l * .13
            o.append(f'<path d="M{bx:.0f} {-ep / 2 - 6} L{bx + l * .16:.0f} {-ep / 2 - 4} L{bx + l * .12:.0f} {ep / 2 + 6} L{bx - l * .04:.0f} {ep / 2 + 4} Z" '
                     f'fill="url(#h1)" {STP} stroke-width="3.5"/>')
        o.append(f'<path d="M{l * .3:.0f} {ep / 2 + 4} q-10 40 18 70 q6 -26 -2 -66" fill="url(#h1)" {STP} stroke-width="3"/>')
    o.append('</g>')
    return "".join(o)


def main_bord(x: float, y: float, sens: int, haut: float = 150, seed: int = 0) -> str:
    """La paume et les doigts repliés derrière le bord de la feuille ; sale."""
    o = [f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="110" ry="{haut:.0f}" fill="{PAPIER}" {STP} stroke-width="5"/>']
    for k in range(3):
        o.append(f'<path d="M{x + sens * 40:.0f} {y + haut - 60 + k * 30:.0f} q{sens * 110} 0 {sens * 140} 24" fill="none" {STP} stroke-width="4"/>')
    o.append(salete(x, y, 90, haut * .8, seed))
    return "".join(o)


def manche(x: float, y: float, sens: int) -> str:
    """La manche de la capote, du coin bas de l'image au poignet. Le coude (ex, ey) et le point
    bas (bx2) sont fixes et dans ZONE_SCEAU : hors de la zone, la manche est la même dans toutes
    les images, sinon le fond (image 0) se raccorderait mal quand la main bouge."""
    def m(v: float) -> float:
        return v if sens > 0 else W - v
    return (f'<path d="M{m(-60):.0f} 1140 L{m(320):.0f} 900 L{x - sens * 60:.0f} {y + 40:.0f} '
            f'L{x + sens * 70:.0f} {y + 160:.0f} L{m(330):.0f} 1100 L{m(240):.0f} 1140 Z" '
            f'fill="url(#h2)" {STP} stroke-width="5"/>')


def feuille(x0: float, y0: float, x1: float, y1: float, plis=(), seed: int = 5) -> str:
    """La feuille épaisse dépliée, bords irréguliers, l'écriture serrée, illisible ; plis : les
    hauteurs des plis marqués."""
    rr = random.Random(seed)
    o = [f'<path d="M{x0} {y0} L{(x0 + x1) / 2:.0f} {y0 + 6} L{x1} {y0 - 6} L{x1 + 6} {y1} L{(x0 + x1) / 2:.0f} {y1 - 4} L{x0 - 6} {y1 + 4} Z" '
         f'fill="{PAPIER}" {STP} stroke-width="6"/>']
    for py in plis:
        o.append(f'<path d="M{x0 - 2} {py} L{x1 + 4} {py - 6}" stroke="{MINE}" stroke-width="4"/>')
    for yy in range(int(y0) + 60, int(y1) - 30, 56):
        if any(abs(yy - py) < 20 for py in plis):
            continue
        xx = x0 + 70
        d = f"M{xx} {yy}"
        while xx < x1 - 100:
            l = rr.uniform(30, 90)
            d += f" q{l / 3:.0f} -{rr.uniform(6, 14):.0f} {l / 2:.0f} 0 t{l / 2:.0f} 0 m{rr.uniform(12, 22):.0f} 0"
            xx += l + 18
        o.append(f'<path d="{d}" fill="none" stroke="{ENCRE}" stroke-width="3.2"/>')
    o.append(f'<ellipse cx="{x1 - 90}" cy="{y1 - 50}" rx="60" ry="22" fill="{LAVIS}" opacity=".22"/>')
    return "".join(o)


def pli_ferme(cire: int, ruban: int) -> str:
    """Le pli fermé : feuille épaisse pliée en trois (la tranche), le dernier rabat en travers ;
    cire 0 entière, 1 fendue, 2 éclats en l'air, 3 éclats plus bas, 4 plus rien ; ruban 0 noué,
    1 relâché, 2 qui glisse, 3 qui sort par le bas, 4 parti."""
    o = [f'<path d="M566 470 L1354 462 L1364 880 L560 890 Z" fill="{PAPIER}" {STP} stroke-width="6"/>',
         f'<path d="M560 890 L566 906 L1366 896 L1364 880" fill="{PAPIER}" {STP} stroke-width="4"/>',
         f'<path d="M562 640 Q960 650 1360 632" fill="none" {STP} stroke-width="4"/>',
         f'<ellipse cx="700" cy="820" rx="70" ry="26" fill="{LAVIS}" opacity=".22"/>',
         f'<ellipse cx="1240" cy="520" rx="50" ry="20" fill="{LAVIS}" opacity=".18"/>']
    if ruban == 0:
        o.append(f'<path d="M960 452 V900" stroke="{ROUGE}" stroke-width="24"/>'
                 f'<path d="M985 660 q70 70 50 210 M985 660 q120 30 150 160" fill="none" stroke="{ROUGE}" stroke-width="18" stroke-linecap="round"/>')
    elif ruban == 1:
        o.append(f'<path d="M972 452 Q990 660 962 900" fill="none" stroke="{ROUGE}" stroke-width="22"/>'
                 f'<path d="M985 680 q80 80 60 230 M985 680 q130 40 150 190" fill="none" stroke="{ROUGE}" stroke-width="18" stroke-linecap="round"/>')
    elif ruban == 2:
        o.append(f'<path d="M1010 640 q40 140 -10 260 t20 160" fill="none" stroke="{ROUGE}" stroke-width="20" stroke-linecap="round"/>')
    elif ruban == 3:
        o.append(f'<path d="M1060 900 q30 100 -10 200" fill="none" stroke="{ROUGE}" stroke-width="20" stroke-linecap="round"/>')
    if cire == 0 or cire == 1:
        o.append(f'<path d="M870 650 Q868 572 952 566 Q1050 566 1052 646 Q1056 730 966 738 Q872 738 870 650 Z" fill="{ENCRE}" {STP} stroke-width="5"/>'
                 f'<circle cx="962" cy="650" r="52" fill="none" stroke="{LAVIS}" stroke-width="5"/>')
        if cire == 1:
            o.append(f'<path d="M962 586 L946 636 L980 664 L952 724 M946 636 L900 646 M980 664 L1024 654" fill="none" stroke="{PAPIER}" stroke-width="7"/>')
    elif cire in (2, 3):
        dy = 0 if cire == 2 else 160
        for dx, ey, a in ((-120, 40, 20), (90, -60, -30), (140, 120, 50), (-60, 180, 10), (20, 10, 70)):
            o.append(f'<path d="M{960 + dx} {660 + ey + dy} l40 -30 l36 22 l-14 44 l-50 6 Z" fill="{ENCRE}" transform="rotate({a + dy / 4} {960 + dx} {660 + ey + dy})"/>')
        o.append(f'<path d="M900 600 Q960 580 1020 600 Q1050 650 1020 700" fill="none" stroke="{MINE}" stroke-width="3"/>')
    else:
        o.append(f'<path d="M900 600 Q960 580 1020 600 Q1050 650 1020 700 Q960 720 900 700 Q880 650 900 600 Z" fill="{LAVIS}" opacity=".3"/>')
    return "".join(o)


def image_sceau(k: int) -> str:
    """L'image k du gros plan (voir le docstring du module)."""
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>']
    if k <= 5:
        o.append(main_bord(520, 700, 1, seed=1) + main_bord(1400, 700, -1, seed=2))
        o.append(manche(520, 700, 1) + manche(1400, 700, -1))
        cire = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 4}[k]
        ruban = {0: 0, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4}[k]
        o.append(pli_ferme(cire, ruban))
        pouce_d = doigt(1400, 720, 1010, 668) if k == 1 else doigt(1400, 720, 1250, 640)
        o.append(doigt(520, 720, 680, 640, bande_=True) + pouce_d)
    elif k in (6, 7):
        o.append(main_bord(500, 700, 1, seed=1) + main_bord(1420, 700, -1, seed=2))
        o.append(manche(500, 700, 1) + manche(1420, 700, -1))
        o.append(feuille(546, 260, 1374, 890 if k == 6 else 1040, plis=(470,) if k == 6 else (470, 820)))
        if k == 6:   # le dernier tiers encore replié devant, sa tranche épaisse
            o.append(f'<path d="M560 640 L1364 632 L1366 896 L560 906 Z" fill="{PAPIER}" {STP} stroke-width="5"/>'
                     f'<path d="M560 906 L566 920 L1368 910 L1366 896" fill="{PAPIER}" {STP} stroke-width="3"/>'
                     f'<ellipse cx="700" cy="820" rx="70" ry="26" fill="{LAVIS}" opacity=".22"/>')
        o.append(doigt(500, 720, 640, 660, bande_=True) + doigt(1420, 720, 1280, 660))
    else:
        # la main gauche remonte au bord de la feuille, qui penche un peu de ce côté ; l'index
        # vient (8) puis glisse sous la première ligne (9)
        a = -2.0 if k == 8 else -3.0
        yg = 520 if k == 8 else 420
        f = (main_bord(500, yg, 1, 130, seed=1) + main_bord(1420, 760, -1, seed=2)
             + feuille(546, 220, 1374, 1020, plis=(480, 770)))
        index = doigt(520, yg - 80, 700, yg - 120, ep=54) if k == 8 else doigt(520, 336, 830, 316, ep=54)
        f += index + doigt(1420, 780, 1280, 720) + doigt(500, yg + 50, 600, yg + 100, bande_=True)
        o.append(manche(500, yg, 1) + manche(1420, 760, -1))
        o.append(f'<g transform="rotate({a} 1374 1020)">{f}</g>')
    return "".join(o)


# ----------------------------------------------------------------------------- sortie
def main() -> None:
    global PAN_2
    PAN_2 = plan_2()[2]
    DST.mkdir(parents=True, exist_ok=True)
    (DST / "cin_descente_01.svg").write_text(descente_1(), encoding="utf-8")
    (DST / "cin_descente_02.svg").write_text(descente_2(), encoding="utf-8")
    (DST / "cin_descente_03.svg").write_text(descente_3(), encoding="utf-8")
    (DST / "cin_descente_04.svg").write_text(descente_4(), encoding="utf-8")
    (DST / "cin_descente_05.svg").write_text(descente_5(), encoding="utf-8")
    (DST / "cin_descente_06.svg").write_text(ligne_tobie(), encoding="utf-8")
    (DST / "cin_sceau_01.svg").write_text(svg(image_sceau(0)), encoding="utf-8")
    (DST / "cin_sceau_02.svg").write_text(bande([image_sceau(k) for k in range(10)], ZONE_SCEAU, 3), encoding="utf-8")
    print("e7_descente : 6 planches ; e7_ouverture_sceau : 2 planches")
    for p, ch in CHEMINS.items():
        print(f"CHEMIN plan {p} (échelle {ECHELLES[p]}) :", ch)
    print("PAN_2 :", PAN_2)


if __name__ == "__main__":
    main()
