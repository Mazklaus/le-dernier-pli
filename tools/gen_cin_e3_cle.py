#!/usr/bin/env python3
"""Génère les planches de la cinématique e3_cle_tourne (lot 2, planche validée par le GD le
17/11) : Tobie accepte le lit chez Ilde. Ilde rabat elle-même les volets, sort, la porte se
ferme sur nous, la clé tourne dehors, une fois, deux fois.

  P1, la fenêtre de la chambre :
  cin_e3-cle-fenetre   le fond 1920 x 1080 : le mur, la fenêtre ouverte sur le soir, le
                       village, la table de nuit ;
  cin_e3-cle-volets    3 images de ZONE_VOLETS, en ligne : Ilde, de dos, tend le bras vers le
                       volet gauche (0), l'a rabattu et prend le droit (1), les deux sont clos,
                       elle pousse l'espagnolette (2).
  P2, la porte, vue du lit :
  cin_e3-cle-porte     le fond : le mur sombre, l'encadrement ; le couloir éclairé par le
                       cierge d'Ilde ;
  cin_e3-cle-battant   2 images de ZONE_BATTANT : le battant entrouvert, Ilde en ombre dans
                       le couloir, son cierge levé (0) ; presque clos, un fil de lumière (1).
  P3, de près, vu de dedans :
  cin_e3-cle-serrure   le fond : les planches de la porte, le boîtier de fer, la gâche ;
  cin_e3-cle-pene      4 images de ZONE_PENE : le trou de serrure éclairé du couloir (0), la
                       clé l'obture (1), le pêne sort d'un cran (2), de deux (3).

Les clés d'Ilde pendent à sa ceinture, comme en jeu. Aucun rouge ; la flamme est en papier.

Usage : python3 tools/gen_cin_e3_cle.py
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
SOIR = "#B9B4A6"
FENETRE = (700, 1220, 200, 760)      # gauche, droite, haut, bas (le tableau de la fenêtre)
ZONE_VOLETS = (420, 100, 1080, 980)
PORTE = (780, 1140, 150, 1000)       # l'encadrement de la porte
ZONE_BATTANT = (560, 100, 800, 940)
ZONE_PENE = (700, 300, 760, 520)


def svg(contenu: str, w: int = W, h: int = H) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{DEFS_CIN}{contenu}</svg>\n')


def bande(images: list[str], zone: tuple[int, int, int, int]) -> str:
    x, y, w, h = zone
    corps = "".join(f'<svg x="{i * w}" y="0" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}">{c}</svg>'
                    for i, c in enumerate(images))
    return svg(corps, w * len(images), h)


def trait(*pts: tuple[float, float], ep: float, fond: str = PAPIER, bord: float = 5) -> str:
    d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    return (f'<path d="{d}" fill="none" stroke="{ENCRE}" stroke-width="{ep + 2 * bord}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{fond}" stroke-width="{ep}" stroke-linecap="round" stroke-linejoin="round"/>')


def planches(x0: float, y0: float, x1: float, y1: float, n: int, fond: str = MINE) -> str:
    """Un panneau de planches verticales (volet, porte)."""
    o = [f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{x1 - x0:.0f}" height="{y1 - y0:.0f}" fill="{fond}" {ST} stroke-width="6"/>']
    for i in range(1, n):
        x = x0 + (x1 - x0) * i / n
        o.append(f'<path d="M{x:.0f} {y0:.0f} V{y1:.0f}" stroke="{ENCRE}" stroke-width="3"/>')
    return "".join(o)


# --- P1 : la fenêtre, les volets ------------------------------------------------------------------
def fenetre_fond() -> str:
    r = random.Random(3101)
    g, d, h, b = FENETRE
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>',
         f'<rect y="{H - 150}" width="{W}" height="150" fill="{CLAIR}"/>',
         f'<path d="M0 {H - 150} H{W}" stroke="{ENCRE}" stroke-width="6"/>',
         f'<rect y="0" width="{W}" height="60" fill="{MINE}"/>']
    for x in range(0, W, 160):
        o.append(f'<path d="M{x} {H - 150} L{x - 60} {H}" stroke="{MINE}" stroke-width="3"/>')
    # le soir dans la fenêtre : le ciel, les toits, le clocher sans cloche
    o.append(f'<rect x="{g}" y="{h}" width="{d - g}" height="{b - h}" fill="{SOIR}"/>')
    for i, (dx, larg, haut) in enumerate(((0, 140, 120), (130, 160, 170), (300, 120, 100), (400, 140, 140))):
        x0 = g + dx
        o.append(f'<path d="M{x0} {b} V{b - haut} L{x0 + larg / 2:.0f} {b - haut - 60} L{x0 + larg} {b - haut} V{b} Z" fill="{MINE}"/>')
    cx = g + 270
    o.append(f'<path d="M{cx - 30} {b - 170} V{b - 330} L{cx} {b - 390} L{cx + 30} {b - 330} V{b - 170} Z" fill="{MINE}"/>')
    o.append(f'<rect x="{cx - 14}" y="{b - 316}" width="28" height="34" fill="{SOIR}"/>')
    # le cadre, les croisillons, l'appui
    o.append(f'<rect x="{g}" y="{h}" width="{d - g}" height="{b - h}" fill="none" {ST} stroke-width="16"/>')
    o.append(f'<path d="M{(g + d) / 2} {h} V{b} M{g} {(h + b) / 2} H{d}" {ST} stroke-width="12"/>')
    o.append(f'<rect x="{g - 40}" y="{b}" width="{d - g + 80}" height="30" fill="{CLAIR}" {ST} stroke-width="6"/>')
    # les murs, quelques fissures du plâtre
    for _ in range(6):
        x, y = r.uniform(0, W), r.uniform(100, H - 200)
        if g - 60 < x < d + 60:
            continue
        o.append(f'<path d="M{x:.0f} {y:.0f} l{r.uniform(-20, 20):.0f} {r.uniform(20, 50):.0f} l{r.uniform(-14, 14):.0f} {r.uniform(16, 40):.0f}" fill="none" stroke="{MINE}" stroke-width="2"/>')
    # la table de nuit, le bougeoir éteint
    o.append(f'<path d="M1420 {H - 150} V720 H1580 V{H - 150} M1420 720 H1580" fill="none" {ST} stroke-width="8"/>')
    o.append(f'<path d="M1490 720 v-60 M1476 660 h28" {ST} stroke-width="6"/>')
    return "".join(o)


def volet_ouvert(cote: int) -> str:
    """Un volet ouvert, plaqué en biais contre le mur dehors (on n'en voit que la tranche)."""
    g, d, h, b = FENETRE
    if cote < 0:
        return (f'<path d="M{g + 6} {h + 8} L{g + 70} {h + 40} L{g + 70} {b - 40} L{g + 6} {b - 8} Z" fill="{MINE}" {ST} stroke-width="5"/>'
                f'<path d="M{g + 38} {h + 26} V{b - 26}" stroke="{ENCRE}" stroke-width="3"/>')
    return (f'<path d="M{d - 6} {h + 8} L{d - 70} {h + 40} L{d - 70} {b - 40} L{d - 6} {b - 8} Z" fill="{MINE}" {ST} stroke-width="5"/>'
            f'<path d="M{d - 38} {h + 26} V{b - 26}" stroke="{ENCRE}" stroke-width="3"/>')


def volet_clos(cote: int) -> str:
    g, d, h, b = FENETRE
    m = (g + d) / 2
    x0, x1 = (g + 8, m) if cote < 0 else (m, d - 8)
    o = [planches(x0, h + 8, x1, b - 8, 4)]
    for y in (h + 90, b - 90):
        o.append(f'<path d="M{x0 + 10:.0f} {y} H{x1 - 10:.0f}" stroke="{ENCRE}" stroke-width="10"/>')
    o.append(f'<path d="M{x0 + 20:.0f} {h + 110} L{x1 - 20:.0f} {b - 110}" stroke="{ENCRE}" stroke-width="8"/>')
    return "".join(o)


def ilde_dos(k: int) -> str:
    """Ilde de dos devant la fenêtre : coiffe, châle, robe sombre, tablier noué, clés à la
    ceinture. Bras vers le volet gauche (0), vers le droit (1), sur l'espagnolette (2)."""
    g, d, h, b = FENETRE
    cx, sol = 960, H - 110
    epaule, taille = 520, 700
    o = []
    # les bras : derrière le corps si possible, tendus vers les volets
    bras = {
        0: [((cx - 100, epaule + 20), (cx - 200, epaule - 40), (g + 40, h + 300)), ((cx + 100, epaule + 20), (cx + 130, epaule + 140), (cx + 100, taille))],
        1: [((cx - 100, epaule + 20), (cx - 130, epaule + 140), (cx - 100, taille)), ((cx + 100, epaule + 20), (cx + 200, epaule - 40), (d - 40, h + 300))],
        2: [((cx - 100, epaule + 20), (cx - 60, epaule - 60), (cx - 14, h + 260)), ((cx + 100, epaule + 20), (cx + 60, epaule - 60), (cx + 14, h + 280))],
    }[k]
    # la robe, longue jusqu'au sol
    o.append(f'<path d="M{cx - 110} {epaule} Q{cx - 150} {taille} {cx - 190} {sol} H{cx + 190} Q{cx + 150} {taille} {cx + 110} {epaule} Z" '
             f'fill="{LAVIS}" {ST} stroke-width="7"/>')
    for i in range(5):
        x = cx - 120 + i * 60
        o.append(f'<path d="M{x} {taille + 40} Q{x + (i - 2) * 8} {taille + 200} {x + (i - 2) * 20} {sol - 10}" fill="none" stroke="{ENCRE}" stroke-width="3"/>')
    # le nœud du tablier, ses cordons
    o.append(f'<path d="M{cx - 130} {taille} H{cx + 130}" stroke="{PAPIER}" stroke-width="14"/>')
    o.append(f'<path d="M{cx - 130} {taille - 7} H{cx + 130} M{cx - 130} {taille + 7} H{cx + 130}" stroke="{ENCRE}" stroke-width="3"/>')
    o.append(f'<path d="M{cx} {taille} q-40 -24 -50 4 q10 24 50 -4 q40 -24 50 4 q-10 24 -50 -4 Z" fill="{PAPIER}" {ST} stroke-width="4"/>')
    o.append(f'<path d="M{cx - 6} {taille + 6} l-20 90 M{cx + 6} {taille + 6} l24 86" stroke="{PAPIER}" stroke-width="10" stroke-linecap="round"/>')
    o.append(f'<path d="M{cx - 6} {taille + 6} l-20 90 M{cx + 6} {taille + 6} l24 86" stroke="{ENCRE}" stroke-width="2"/>')
    # les clés, pendues au cordon sur la hanche
    kx, ky = cx + 140, taille + 10
    o.append(f'<circle cx="{kx}" cy="{ky + 30}" r="20" fill="none" {ST} stroke-width="6"/>')
    for i, a in enumerate((-14, 4, 20)):
        o.append(f'<g transform="rotate({a} {kx} {ky + 50})"><path d="M{kx} {ky + 50} v70 m0 -14 h14 m-14 -14 h10" fill="none" {ST} stroke-width="6"/></g>')
    # les bras
    for p in bras:
        o.append(trait(*p, ep=40, fond=LAVIS))
        o.append(f'<circle cx="{p[-1][0]}" cy="{p[-1][1]}" r="20" fill="{PAPIER}" {ST} stroke-width="5"/>')
    # le châle hachuré sur les épaules
    o.append(f'<path d="M{cx - 130} {epaule + 30} Q{cx} {epaule - 50} {cx + 130} {epaule + 30} L{cx + 40} {epaule + 170} L{cx} {epaule + 190} L{cx - 40} {epaule + 170} Z" '
             f'fill="{CLAIR}" {ST} stroke-width="6"/>')
    for i in range(6):
        x = cx - 100 + i * 40
        o.append(f'<path d="M{x} {epaule + 10} l30 {60 + (3 - abs(i - 2.5)) * 18:.0f}" stroke="{MINE}" stroke-width="3"/>')
    # la coiffe blanche, de dos
    o.append(f'<path d="M{cx - 64} {epaule - 10} Q{cx - 80} {epaule - 140} {cx} {epaule - 150} Q{cx + 80} {epaule - 140} {cx + 64} {epaule - 10} Q{cx} {epaule + 10} {cx - 64} {epaule - 10} Z" '
             f'fill="{PAPIER}" {ST} stroke-width="6"/>')
    o.append(f'<path d="M{cx - 50} {epaule - 90} Q{cx} {epaule - 110} {cx + 50} {epaule - 90}" fill="none" stroke="{MINE}" stroke-width="3"/>')
    return "".join(o)


def plan_volets(k: int) -> str:
    o = [fenetre_fond()]
    o.append(volet_clos(-1) if k >= 1 else volet_ouvert(-1))
    o.append(volet_clos(1) if k >= 2 else volet_ouvert(1))
    if k >= 2:
        g, d, h, b = FENETRE
        o.append(f'<path d="M{(g + d) / 2} {h + 10} V{b - 10}" {ST} stroke-width="14"/>')
    o.append(ilde_dos(k))
    return "".join(o)


# --- P2 : la porte se ferme ------------------------------------------------------------------------
def porte_fond() -> str:
    g, d, h, b = PORTE
    o = [f'<rect width="{W}" height="{H}" fill="{LAVIS}"/>',
         f'<rect y="{b}" width="{W}" height="{H - b}" fill="{ENCRE}"/>']
    for x in range(-200, W, 180):
        o.append(f'<path d="M{x} {b} L{x - 120} {H}" stroke="{LAVIS}" stroke-width="3"/>')
    # le couloir, éclairé par le cierge : un aplat de papier, le mur du fond, un carrelage
    o.append(f'<rect x="{g}" y="{h}" width="{d - g}" height="{b - h}" fill="{CLAIR}"/>')
    o.append(f'<path d="M{g} {b - 160} H{d}" stroke="{MINE}" stroke-width="4"/>')
    for x in range(g + 40, d, 70):
        o.append(f'<path d="M{x} {b - 160} L{x - 30} {b}" stroke="{MINE}" stroke-width="2"/>')
    # l'encadrement
    o.append(f'<path d="M{g - 40} {b} V{h - 40} H{d + 40} V{b}" fill="none" stroke="{MINE}" stroke-width="30"/>')
    o.append(f'<path d="M{g - 55} {b} V{h - 55} H{d + 55} V{b} M{g} {b} V{h} H{d} V{b}" fill="none" {ST} stroke-width="6"/>')
    # le pied du lit, au premier plan, d'où l'on regarde
    o.append(f'<path d="M-20 {H - 60} Q600 {H - 120} 1200 {H - 70} T{W + 20} {H - 90} V{H + 20} H-20 Z" fill="{MINE}" {ST} stroke-width="8"/>')
    o.append(f'<path d="M100 {H - 40} Q500 {H - 90} 900 {H - 50}" fill="none" stroke="{ENCRE}" stroke-width="3"/>')
    return "".join(o)


def ilde_cierge() -> str:
    """Ilde en ombre dans le couloir, le cierge levé, la flamme en papier."""
    g, d, h, b = PORTE
    cx, sol = 1030, b - 20
    return (f'<path d="M{cx - 70} {sol} Q{cx - 60} {sol - 300} {cx - 50} {sol - 420} Q{cx} {sol - 460} {cx + 50} {sol - 420} '
            f'Q{cx + 60} {sol - 300} {cx + 70} {sol} Z" fill="{ENCRE}"/>'
            f'<path d="M{cx - 40} {sol - 430} Q{cx - 50} {sol - 540} {cx} {sol - 548} Q{cx + 50} {sol - 540} {cx + 40} {sol - 430} Z" fill="{ENCRE}"/>'
            f'<path d="M{cx + 40} {sol - 380} L{cx + 70} {sol - 470}" stroke="{ENCRE}" stroke-width="26" stroke-linecap="round"/>'
            f'<rect x="{cx + 62}" y="{sol - 560}" width="18" height="90" fill="{PAPIER}" {ST} stroke-width="4"/>'
            f'<path d="M{cx + 71} {sol - 562} q-14 -24 0 -50 q14 26 0 50 Z" fill="{PAPIER}" {ST} stroke-width="4"/>')


def battant(k: int) -> str:
    """Le battant, gond à gauche, s'ouvre vers nous : entrouvert (0), presque clos (1)."""
    g, d, h, b = PORTE
    if k == 0:
        # vu en biais : le bord libre vient vers nous, plus haut et plus bas que l'encadrement
        bx = g + 160
        pts = [(g, h), (bx, h - 40), (bx, b + 50), (g, b)]
    else:
        bx = d - 30
        pts = [(g, h), (bx, h - 6), (bx, b + 6), (g, b)]
    dd = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts) + " Z"
    o = [f'<path d="{dd}" fill="{MINE}" {ST} stroke-width="6"/>']
    n = 4
    for i in range(1, n):
        u = i / n
        x = g + (bx - g) * u
        o.append(f'<path d="M{x:.0f} {h + (pts[1][1] - h) * u:.0f} L{x:.0f} {b + (pts[2][1] - b) * u:.0f}" stroke="{ENCRE}" stroke-width="3"/>')
    o.append(f'<path d="M{bx - 30} {(h + b) / 2 - 10} h-20" {ST} stroke-width="12"/>')
    return "".join(o)


def plan_battant(k: int) -> str:
    o = [porte_fond()]
    if k == 0:
        o.append(ilde_cierge())
    o.append(battant(k))
    return "".join(o)


# --- P3 : la serrure, la clé tourne ----------------------------------------------------------------
TROU = (960, 560)
GACHE_X = 1340


def serrure_fond() -> str:
    o = [planches(-20, -20, GACHE_X - 30, H + 20, 5)]
    # le montant de l'encadrement, à droite, et la gâche
    o.append(f'<rect x="{GACHE_X - 30}" y="-20" width="{W - GACHE_X + 50}" height="{H + 40}" fill="{LAVIS}" {ST} stroke-width="6"/>')
    o.append(f'<rect x="{GACHE_X + 10}" y="430" width="90" height="190" rx="8" fill="{ENCRE}"/>')
    o.append(f'<rect x="{GACHE_X + 30}" y="490" width="50" height="70" fill="{LAVIS}"/>')
    # le boîtier de fer, ses rivets
    o.append(f'<rect x="720" y="340" width="560" height="420" rx="10" fill="{ENCRE}"/>')
    o.append(f'<rect x="740" y="360" width="520" height="380" rx="6" fill="none" stroke="{LAVIS}" stroke-width="4"/>')
    for x, y in ((760, 380), (1240, 380), (760, 720), (1240, 720)):
        o.append(f'<circle cx="{x}" cy="{y}" r="12" fill="{LAVIS}"/>')
    o.append(f'<path d="M780 460 h120" stroke="{LAVIS}" stroke-width="6"/>')
    return "".join(o)


def pene(k: int) -> str:
    """Le trou de serrure et le pêne : lumière du couloir (0), clé engagée (1), un tour (2),
    deux tours (3)."""
    tx, ty = TROU
    o = [serrure_fond()]
    trou = (f'M{tx} {ty - 44} a28 28 0 1 1 0.1 0 Z M{tx - 12} {ty - 20} L{tx - 22} {ty + 50} H{tx + 22} L{tx + 12} {ty - 20} Z')
    o.append(f'<path d="{trou}" fill="{CLAIR if k == 0 else LAVIS}" fill-rule="nonzero"/>')
    if k >= 1:
        # le panneton de la clé, vu par le trou : il tourne d'un quart à chaque cran
        a = (0, 0, 90, 180)[k]
        o.append(f'<g transform="rotate({a} {tx} {ty - 30})"><rect x="{tx - 10}" y="{ty - 62}" width="20" height="64" fill="{MINE}" {ST} stroke-width="3"/></g>')
    # le pêne : rentré (0, 1), à mi-course (2), dans la gâche (3)
    sortie = (0, 0, 70, 150)[k]
    o.append(f'<rect x="{1200 + sortie}" y="500" width="100" height="50" fill="{CLAIR}" {ST} stroke-width="5"/>')
    o.append(f'<rect x="1260" y="340" width="20" height="420" fill="{ENCRE}"/>')
    return "".join(o)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    fichiers = {
        "cin_e3-cle-fenetre": svg(fenetre_fond()),
        "cin_e3-cle-volets": bande([plan_volets(k) for k in range(3)], ZONE_VOLETS),
        "cin_e3-cle-porte": svg(porte_fond()),
        "cin_e3-cle-battant": bande([plan_battant(k) for k in range(2)], ZONE_BATTANT),
        "cin_e3-cle-serrure": svg(serrure_fond()),
        "cin_e3-cle-pene": bande([pene(k) for k in range(4)], ZONE_PENE),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"e3_cle_tourne : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
