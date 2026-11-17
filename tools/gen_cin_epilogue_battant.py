#!/usr/bin/env python3
"""Génère les images de l'épilogue animé « Le Battant » (lettre a, porteur), d'après la planche
validée par le GD le 17/11 (direction-artistique/epilogues/planche_trois_fins.png). Consigne de
l'utilisateur : des images faites exprès pour la ciné ; seule la gravure a est réemployée.

  P1  cin_epilogue-a (réemploi) + cin_epi-a-corde : la corde qui pend de la bouche noire de la
      grande cloche (rien n'est montré dedans), le jeu la balance à peine.
  P2  cin_epi-a-tranchee (2600 x 800) : la Longue Tranchée au calme, trois lignes de parapet qui
      filent vers l'horizon, quelques casques ; cin_epi-a-pelletee : une pelletée de terre jetée
      par-dessus le parapet, 3 images (240 x 260, le pied au bord du parapet en (120, 250)).
  P3  cin_epi-a-soldat (1920 x 800) : le soir, un jeune soldat en buste, de trois quarts ; il
      siffle ; cin_epi-a-siffle : sa tête, 3 images (lèvres, la note ; la larme qui descend).
  P4  cin_epi-a-mere (1920 x 800) : sous sa cloche, la Mère-Cloche en gros plan, les yeux clos,
      l'éclat de bronze sur les genoux ; cin_epi-a-lire : la tête et les mains, 6 images (grille
      3 x 2) : les doigts parcourent les noms et s'arrêtent sur le nom frais, les lèvres bougent ;
      cin_epi-a-lampe : la lampe éteinte qui se rallume, 3 images (120 x 200).
Garde-fous : rien dans la grande cloche, la cire noire, les yeux de la Mère-Cloche clos, aucun
rouge (le ruban de la gravure a est déjà là).

Usage : python3 tools/gen_cin_epilogue_battant.py
"""
from __future__ import annotations

import random

from gen_chr_pnj_e7 import M_EPAULE_D, M_EPAULE_G, agrandie, bras_mere, corps_mere, main_lisante, tete_mere
from gen_cin_e1 import DST, W, bande, svg
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER

ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
H_PLAN = 800      # les fonds s'arrêtent sous le bandeau du texte (y 790)
CLAIR = "#D3CFC2"  # un lavis clair, en aplat (le LAVIS du projet est sombre)

# --- P1 : la corde ----------------------------------------------------------------------------
CORDE = (40, 230)


def corde() -> str:
    w, h = CORDE
    torons = "".join(f'<path d="M12 {y} L28 {y + 10}" stroke="{ENCRE}" stroke-width="2.4"/>' for y in range(0, h - 30, 12))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<rect x="11" y="0" width="18" height="{h - 26}" fill="{PAPIER}" {ST} stroke-width="3"/>{torons}'
            f'<path d="M14 {h - 26} l-6 22 M20 {h - 26} l0 24 M26 {h - 26} l6 20" {ST} stroke-width="3" fill="none"/>'
            f'<path d="M10 {h - 30} H30" {ST} stroke-width="5"/></svg>\n')


# --- P2 : la Longue Tranchée ----------------------------------------------------------------------
TR_W = 2600
CASQUES = [(420, 556), (1180, 548), (1900, 560), (2380, 552)]


def ligne_parapet(y0: float, amp: float, pas: float, seed: int) -> list[tuple[float, float]]:
    r = random.Random(seed)
    pts, x, haut = [], -40.0, True
    while x < TR_W + 400:
        pts.append((x, y0 + (0 if haut else amp) + r.uniform(-3, 3)))
        x += pas * r.uniform(.7, 1.3)
        haut = not haut
    return pts


def tranchee() -> str:
    r = random.Random(1101)
    o = [f'<rect width="{TR_W}" height="{H_PLAN}" fill="{PAPIER}"/>']
    for _ in range(16):
        y = r.randint(40, 300)
        o.append(f'<path d="M{r.randint(0, TR_W)} {y} h{r.randint(120, 420)}" stroke="{MINE}" stroke-width="1.4"/>')
    # l'horizon, des collines basses, une ligne d'arbres morts
    o.append(f'<path d="M0 330 Q400 312 900 326 T1800 320 T{TR_W} 328 V{H_PLAN} H0 Z" fill="url(#h1)" {ST} stroke-width="2"/>')
    for x in range(60, TR_W, 230):
        hx = r.randint(20, 46)
        o.append(f'<path d="M{x} 326 v-{hx} M{x} {326 - hx * .6:.0f} l{r.choice((-1, 1)) * 9} -8" {ST} stroke-width="2" fill="none"/>')
    # trois lignes de parapet en zigzag : la lointaine, la moyenne, la proche (sacs)
    for y0, amp, pas, ep, fond, seed in ((356, 8, 90, 2, "url(#h2)", 3), (420, 16, 160, 3, "url(#h2)", 4)):
        pts = ligne_parapet(y0, amp, pas, seed)
        d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
        o.append(f'<path d="{d} L{TR_W + 80} {y0 + 30} L-40 {y0 + 30} Z" fill="{fond}" {ST} stroke-width="{ep}"/>')
        o.append(f'<path d="{d}" fill="none" stroke="{PAPIER}" stroke-width="1.4" transform="translate(0 -3)"/>')
    pts = ligne_parapet(560, 26, 300, 5)
    d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    o.append(f'<path d="{d} L{TR_W + 80} {H_PLAN} L-40 {H_PLAN} Z" fill="{CLAIR}" {ST} stroke-width="4"/>')
    for j, y in enumerate(range(640, H_PLAN + 40, 64)):
        for x in range(-60 + (j % 2) * 65, TR_W, 130):
            o.append(f'<path d="M{x} {y} Q{x + 65} {y - 40} {x + 130} {y}" fill="none" stroke="{ENCRE}" stroke-width="2.2"/>')
    o.append(f'<path d="{d}" fill="none" {ST} stroke-width="6"/>')
    # quelques casques au ras du parapet, immobiles : on creuse, on ne se bat plus
    for x, y in CASQUES:
        o.append(f'<path d="M{x - 30} {y} Q{x - 28} {y - 34} {x} {y - 36} Q{x + 28} {y - 34} {x + 30} {y} Z" fill="url(#h2)" {ST} stroke-width="3"/>'
                 f'<path d="M{x - 38} {y} H{x + 38}" {ST} stroke-width="5"/><path d="M{x} {y - 36} v-6" {ST} stroke-width="3"/>')
    return svg("".join(o), (0, 0, TR_W, H_PLAN))


PELLETEE = (240, 260)


def pelletee(k: int) -> str:
    """Une pelletée de terre jetée par-dessus le parapet : 0 le fer de la pelle paraît, chargé ;
    1 la terre part en gerbe ; 2 elle retombe, éparse, la pelle redescendue."""
    r = random.Random(77)
    o = []
    if k in (0, 1):
        y = 236 if k == 0 else 214
        a = -18 if k == 0 else -40
        o.append(f'<g transform="rotate({a} 110 {y + 30})"><path d="M110 {y + 60} V{y}" {ST} stroke-width="6"/>'
                 f'<path d="M96 {y} Q110 {y - 30} 124 {y} Z" fill="url(#h2)" {ST} stroke-width="3"/></g>')
    mottes = [(r.uniform(-1, 1), r.uniform(0, 1), r.uniform(5, 12)) for _ in range(16)]
    for dx, t, e in mottes:
        if k == 0:
            x, y = 112 + dx * 12, 222 - t * 8
        elif k == 1:
            x, y = 130 + dx * 30 + t * 50, 160 - t * 70
        else:
            x, y = 170 + dx * 50 + t * 40, 120 + t * 90
        o.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{e:.1f}" ry="{e * .7:.1f}" fill="{LAVIS}" {ST} stroke-width="1.6"/>')
    if k == 2:
        for _ in range(20):
            o.append(f'<circle cx="{r.uniform(120, 230):.0f}" cy="{r.uniform(80, 240):.0f}" r="{r.uniform(1.4, 3):.1f}" fill="{MINE}"/>')
    return "".join(o)


# --- P3 : le soldat qui siffle ----------------------------------------------------------------------
TETE = (960, 330)
ZONE_SIFFLE = (760, 160, 420, 400)


def soldat_tete(k: int) -> str:
    """La tête d'un jeune soldat, de trois quarts vers la gauche, le casque, le regard baissé ; il
    siffle (k 0 : les lèvres en rond, 1 : plus serrées, la note) ; une larme sort de l'œil (k 1)
    et descend sur la joue (k 2)."""
    x, y = TETE
    o = [  # la nuque, l'oreille, le visage
        f'<path d="M{x + 40} {y + 60} Q{x + 70} {y + 130} {x + 50} {y + 190} L{x - 30} {y + 200} Q{x - 40} {y + 150} {x - 30} {y + 120} Z" fill="{PAPIER}" {ST} stroke-width="4"/>',
        f'<path d="M{x - 92} {y - 10} Q{x - 100} {y + 60} {x - 76} {y + 104} Q{x - 50} {y + 140} {x - 6} {y + 142} Q{x + 50} {y + 136} {x + 76} {y + 70} '
        f'Q{x + 88} {y + 10} {x + 80} {y - 30} Z" fill="{PAPIER}" {ST} stroke-width="4.4"/>',
        f'<path d="M{x + 56} {y + 20} Q{x + 84} {y + 8} {x + 86} {y + 40} Q{x + 86} {y + 70} {x + 60} {y + 70}" fill="{PAPIER}" {ST} stroke-width="3.4"/>',
        # une barbe de quelques jours (points de mine), jeune
        "".join(f'<circle cx="{x + dx}" cy="{y + dy}" r="1.6" fill="{MINE}"/>' for dx, dy in
                ((-60, 100), (-48, 112), (-34, 120), (-20, 124), (6, 126), (22, 122), (36, 112), (48, 98), (-40, 104), (-12, 116), (14, 114), (30, 104))),
        # l'œil baissé, mi-clos, le sourcil qui tombe vers la tempe
        f'<path d="M{x - 62} {y + 20} Q{x - 46} {y + 28} {x - 28} {y + 20}" fill="none" {ST} stroke-width="3.4"/>',
        f'<path d="M{x - 58} {y + 22} Q{x - 46} {y + 30} {x - 32} {y + 22} Q{x - 46} {y + 26} {x - 58} {y + 22} Z" fill="{ENCRE}"/>',
        f'<path d="M{x - 70} {y + 2} Q{x - 50} {y - 6} {x - 22} {y + 6}" fill="none" {ST} stroke-width="3.6"/>',
        f'<path d="M{x + 2} {y + 18} Q{x + 18} {y + 26} {x + 30} {y + 20}" fill="none" {ST} stroke-width="3"/>',
        f'<path d="M{x - 2} {y + 2} Q{x + 18} {y - 4} {x + 38} {y + 6}" fill="none" {ST} stroke-width="3"/>',
        # le nez, la joue creusée
        f'<path d="M{x - 30} {y + 30} L{x - 52} {y + 76} Q{x - 40} {y + 84} {x - 26} {y + 78}" fill="none" {ST} stroke-width="3.4"/>',
        f'<path d="M{x + 18} {y + 70} Q{x + 26} {y + 96} {x + 16} {y + 116}" fill="none" stroke="{MINE}" stroke-width="2"/>',
    ]
    # la bouche qui siffle : un petit rond, plus serré sur la note
    r = (9, 6, 8)[k]
    o.append(f'<ellipse cx="{x - 36}" cy="{y + 108}" rx="{r}" ry="{r * 1.2:.1f}" fill="{ENCRE}"/>'
             f'<path d="M{x - 36 - r - 8} {y + 102} Q{x - 36} {y + 96 - r * .3:.0f} {x - 36 + r + 8} {y + 102} '
             f'M{x - 36 - r - 6} {y + 116} Q{x - 36} {y + 122 + r * .3:.0f} {x - 36 + r + 6} {y + 116}" fill="none" {ST} stroke-width="3"/>')
    # la larme : au coin de l'œil, puis sur la joue
    if k >= 1:
        lx, ly = (x - 36, y + 34) if k == 1 else (x - 22, y + 74)
        o.append(f'<path d="M{lx} {ly - 10} Q{lx + 7} {ly + 2} {lx} {ly + 8} Q{lx - 7} {ly + 2} {lx} {ly - 10} Z" fill="{PAPIER}" {ST} stroke-width="2.2"/>')
        if k == 2:
            o.append(f'<path d="M{x - 34} {y + 32} Q{x - 30} {y + 50} {x - 24} {y + 64}" fill="none" stroke="{MINE}" stroke-width="1.6"/>')
    # le casque, enfoncé, la bordure à l'ombre sur le front
    o.append(f'<path d="M{x - 120} {y - 6} Q{x - 110} {y - 140} {x} {y - 146} Q{x + 110} {y - 140} {x + 120} {y - 6} Z" fill="url(#h2)" {ST} stroke-width="4.4"/>'
             f'<path d="M{x - 150} {y} Q{x} {y - 30} {x + 150} {y - 2} L{x + 146} {y + 14} Q{x} {y - 14} {x - 148} {y + 16} Z" fill="{LAVIS}" {ST} stroke-width="4"/>'
             f'<path d="M{x - 40} {y - 144} Q{x} {y - 172} {x + 40} {y - 144}" fill="{LAVIS}" {ST} stroke-width="3.4"/>'
             f'<path d="M{x - 96} {y - 40} Q{x} {y - 64} {x + 96} {y - 40}" fill="none" stroke="{PAPIER}" stroke-width="2"/>')
    return "".join(o)


def soldat(k: int = 0) -> str:
    """Le soir dans la tranchée : la paroi de sacs dans l'ombre, une bande de ciel pâle au-dessus,
    le soldat en buste, la capote au col relevé, la bretelle du fusil."""
    r = random.Random(1301)
    o = [f'<rect width="{W}" height="{H_PLAN}" fill="{PAPIER}"/>']
    for _ in range(10):
        y = r.randint(20, 150)
        o.append(f'<path d="M{r.randint(0, W)} {y} h{r.randint(140, 400)}" stroke="{MINE}" stroke-width="1.4"/>')
    # la paroi de sacs dans l'ombre du soir : un aplat de mine, les sacs en quelques arcs
    o.append(f'<path d="M0 190 Q480 176 960 186 T{W} 182 V{H_PLAN} H0 Z" fill="{MINE}" {ST} stroke-width="4"/>')
    for j, y in enumerate(range(250, H_PLAN, 72)):
        for x in range(-60 + (j % 2) * 70, W, 140):
            o.append(f'<path d="M{x} {y} Q{x + 70} {y - 46} {x + 140} {y}" fill="none" stroke="{ENCRE}" stroke-width="2.2" opacity=".55"/>')
    # la capote : les épaules, le col relevé, des boutons, la bretelle en travers
    x, y = TETE
    o.append(f'<path d="M{x - 420} {H_PLAN} Q{x - 400} {y + 250} {x - 200} {y + 200} Q{x - 60} {y + 170} {x + 60} {y + 176} '
             f'Q{x + 300} {y + 190} {x + 400} {y + 280} Q{x + 460} {y + 360} {x + 470} {H_PLAN} Z" fill="{LAVIS}" {ST} stroke-width="5"/>')
    o.append(f'<path d="M{x - 300} {y + 300} Q{x - 320} {y + 400} {x - 300} {H_PLAN} M{x + 300} {y + 290} Q{x + 330} {y + 400} {x + 320} {H_PLAN} '
             f'M{x + 120} {y + 260} Q{x + 140} {y + 380} {x + 120} {H_PLAN}" fill="none" stroke="{MINE}" stroke-width="3"/>')
    o.append(f'<path d="M{x - 140} {y + 210} L{x - 90} {y + 130} L{x - 20} {y + 196} Z M{x + 30} {y + 196} L{x + 80} {y + 120} L{x + 140} {y + 200} Z" fill="{LAVIS}" {ST} stroke-width="4"/>')
    o.append(f'<path d="M{x - 60} {y + 220} L{x - 80} {H_PLAN}" fill="none" {ST} stroke-width="3"/>'
             + "".join(f'<circle cx="{x - 64 - j * 4}" cy="{y + 270 + j * 80}" r="9" fill="{PAPIER}" {ST} stroke-width="3"/>' for j in range(3)))
    o.append(f'<path d="M{x + 260} {y + 200} L{x - 220} {H_PLAN}" stroke="{ENCRE}" stroke-width="26"/>'
             f'<path d="M{x + 260} {y + 200} L{x - 220} {H_PLAN}" stroke="{LAVIS}" stroke-width="16"/>')
    o.append(soldat_tete(k))
    return "".join(o)


# --- P4 : la Mère-Cloche ---------------------------------------------------------------------------
# gros plan : le dessin du PNJ (gen_chr_pnj_e7, déjà agrandi 1,4 fois autour de ses pieds) mis à
# l'échelle K ; son visage à l'écran en (960, 250), l'éclat de bronze vers (916, 650)
K = 2.6
OX, OY = 960 - 125.6 * K, 250 - 98.4 * K
ZONE_LIRE = (700, 90, 440, 600)
# les mains, image par image (repère du PNJ) : (main gauche, main droite), les lèvres
MAINS = [((80, 293), (112, 291)), ((84, 295), (124, 293)), ((84, 297), (130, 305))]
LAMPE = (520, 520)
ZONE_LAMPE = (LAMPE[0] - 60, LAMPE[1] - 150, 120, 200)


def bouche_ouverte(tete: str) -> str:
    return tete.replace(f'<path d="M113 184 Q119 186 125 184" fill="none" stroke="{ENCRE}" stroke-width="1.4"/>',
                        f'<path d="M113 184 Q119 189 125 184 Q119 182 113 184 Z" fill="{ENCRE}" stroke="{ENCRE}" stroke-width="1.2"/>')


def mere(mains: int = 0, parle: bool = False) -> str:
    (gx, gy), (dx, dy) = MAINS[mains]
    bras = (f'<g {ST}>' + bras_mere(M_EPAULE_G, (94, 262), (gx, gy)) + main_lisante(gx, gy)
            + bras_mere(M_EPAULE_D, (148, 262), (dx, dy)) + main_lisante(dx, dy) + '</g>')
    tete = tete_mere()
    if parle:
        ouverte = bouche_ouverte(tete)
        assert ouverte != tete, "la bouche de la Mère-Cloche a changé de dessin"
        tete = ouverte
    dessin = agrandie(corps_mere(0, grave=1.0) + bras + tete)
    return f'<g transform="translate({OX:.1f} {OY:.1f}) scale({K})">{dessin}</g>'


def lampe(k: int) -> str:
    """Une petite lampe à huile posée sur une pierre : 0 éteinte, un fil de fumée ; 1 elle prend ;
    2 la flamme, droite."""
    x, y = LAMPE
    o = [f'<path d="M{x - 34} {y + 30} Q{x} {y + 46} {x + 34} {y + 30} Q{x + 30} {y + 6} {x} {y + 4} Q{x - 30} {y + 6} {x - 34} {y + 30} Z" fill="url(#h2)" {ST} stroke-width="3"/>',
         f'<path d="M{x + 26} {y + 16} Q{x + 50} {y + 6} {x + 44} {y + 26}" fill="none" {ST} stroke-width="3"/>',
         f'<path d="M{x - 2} {y + 4} v-14" {ST} stroke-width="3"/>']
    if k == 0:
        o.append(f'<path d="M{x - 2} {y - 12} q-8 -20 2 -40 t-2 -44" fill="none" stroke="{MINE}" stroke-width="2"/>')
    else:
        h = 26 if k == 1 else 46
        o.append(f'<path d="M{x - 2} {y - 8} Q{x - 14} {y - 8 - h * .45:.0f} {x - 2} {y - 8 - h} Q{x + 10} {y - 8 - h * .45:.0f} {x - 2} {y - 8} Z" fill="{PAPIER}" {ST} stroke-width="2.6"/>')
        if k == 2:
            o.append("".join(f'<path d="M{x - 2 + ax * 30:.0f} {y - 30 + ay * 30:.0f} l{ax * 14:.0f} {ay * 14:.0f}" {ST} stroke-width="2"/>'
                             for ax, ay in ((-1, -.3), (1, -.3), (-.7, -1), (.7, -1))))
    return "".join(o)


def dessous_cloche(k_lampe: int = 0) -> str:
    """Sous la grande cloche : la lèvre de bronze qui passe en arc au-dessus, le sol de pierre et
    les coulures de cire noire ; la lampe sur sa pierre, à gauche."""
    o = [f'<rect width="{W}" height="{H_PLAN}" fill="{PAPIER}"/>',
         f'<path d="M-40 260 Q960 -120 {W + 40} 260 L{W + 40} -10 L-40 -10 Z" fill="{LAVIS}" {ST} stroke-width="5"/>',
         f'<path d="M200 150 Q960 -60 1720 150 M500 70 Q960 -20 1420 70" fill="none" stroke="{MINE}" stroke-width="2"/>',
         f'<path d="M-40 290 Q960 -90 {W + 40} 290" fill="none" {ST} stroke-width="2"/>',
         f'<path d="M0 690 H{W}" {ST} stroke-width="3"/>',
         f'<rect y="690" width="{W}" height="{H_PLAN - 690}" fill="{LAVIS}" opacity=".6"/>']
    r = random.Random(1401)
    for _ in range(9):
        cx = r.choice((r.uniform(80, 600), r.uniform(1300, 1860)))
        o.append(f'<path d="M{cx:.0f} 700 q{r.uniform(10, 30):.0f} -6 {r.uniform(30, 70):.0f} 2 q-10 14 -30 10 Z" fill="{ENCRE}"/>')
    o.append(f'<path d="M{LAMPE[0] - 70} {LAMPE[1] + 40} H{LAMPE[0] + 80} L{LAMPE[0] + 70} {LAMPE[1] + 170} H{LAMPE[0] - 60} Z" fill="{LAVIS}" {ST} stroke-width="3"/>')
    o.append(lampe(k_lampe))
    return "".join(o)


def fond_mere() -> str:
    return dessous_cloche(0) + mere(0, False)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    fichiers = {
        "cin_epi-a-corde": corde(),
        "cin_epi-a-tranchee": tranchee(),
        "cin_epi-a-pelletee": bande([pelletee(k) for k in range(3)], (0, 0) + PELLETEE, 3),
        "cin_epi-a-soldat": svg(soldat(0), (0, 0, W, H_PLAN)),
        "cin_epi-a-siffle": bande([soldat(k) for k in range(3)], ZONE_SIFFLE, 3),
        "cin_epi-a-mere": svg(fond_mere(), (0, 0, W, H_PLAN)),
        "cin_epi-a-lire": bande([dessous_cloche(0) + mere(m, p) for m in range(3) for p in (False, True)], ZONE_LIRE, 3),
        "cin_epi-a-lampe": bande([dessous_cloche(k) for k in range(3)], ZONE_LAMPE, 3),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"épilogue a : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
