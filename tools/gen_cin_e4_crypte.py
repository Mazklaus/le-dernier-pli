#!/usr/bin/env python3
"""Génère les planches de la cinématique e4_descente_crypte (lot 1, planche validée par le GD
le 17/11) : avant la lanterne, Tobie descend la vis de la crypte ; la lumière d'en haut
rétrécit jusqu'au noir complet. On ne voit pas encore les saints.

  P1, 0 à 4 s, plongée dans la vis :
  cin_e4-crypte-vis      dessinée sur 2240, rendue en 1400 x 1400 (affichée à 1,6), centre au milieu : la cage de l'escalier vue d'en haut,
                         une suite de paliers qui rapetissent de RAPPORT en RAPPORT (marches en
                         rayons, mur de pierre), de plus en plus sombres, le fond noir. Tournée
                         et agrandie d'un palier en 4 s, la vis « descend » sans couture ;
  cin_e4-crypte-dessus   2 images de 160 x 160, centre (80, 80) : Tobie vu d'en haut (capuche,
                         épaules, sacoche), tourné vers le haut de l'image, une foulée chacune.
  P2, 4 à 8 s, dans la cage, de côté :
  cin_e4-crypte-cage     1920 x 1080 : le mur de pierre, les marches qui descendent de la porte
                         (en haut à gauche) vers le bas à droite ;
  cin_e4-crypte-lumiere  4 images de ZONE_LUMIERE, grille 2 x 2, transparentes : la porte d'en
                         haut et son cône de lumière qui rétrécit (0 large, 1 étroit, 2 un trait,
                         3 un point), posées sur le noir qui monte.
  P3, 8 à 10 s : noir complet (pas de planche).

Aucun rouge, aucune figure de saint.

Usage : python3 tools/gen_cin_e4_crypte.py
"""
from __future__ import annotations

import math
from pathlib import Path

from gen_cin_epilogues import DEFS_CIN
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER

DST = Path(__file__).resolve().parent.parent / "art" / "src" / "cin"
W, H = 1920, 1080
ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
VIS = 2240
R = VIS / 2
RENDU = 1400            # la vis est dessinée sur VIS et rendue à RENDU px (affichée à VIS / RENDU)
RAPPORT = 0.6           # chaque palier plus bas est vu RAPPORT fois plus petit
MARCHES = 16            # marches par tour
DECALAGE = 67.5         # le palier d'en dessous est tourné d'autant (degrés)
ZONE_LUMIERE = (0, 0, 1400, 1080)
PORTE = (250, 240)      # le haut de la porte, d'où vient la lumière (P2)


def svg(contenu: str, w: int = W, h: int = H) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{DEFS_CIN}{contenu}</svg>\n')


def grille(images: list[str], w: int, h: int, colonnes: int) -> str:
    lignes = math.ceil(len(images) / colonnes)
    corps = "".join(f'<g transform="translate({(i % colonnes) * w} {(i // colonnes) * h})">{c}</g>' for i, c in enumerate(images))
    return svg(corps, w * colonnes, h * lignes)


def bande(images: list[str], zone: tuple[int, int, int, int], colonnes: int) -> str:
    x, y, w, h = zone
    lignes = math.ceil(len(images) / colonnes)
    corps = "".join(f'<svg x="{(i % colonnes) * w}" y="{(i // colonnes) * h}" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}">{c}</svg>'
                    for i, c in enumerate(images))
    return svg(corps, w * colonnes, h * lignes)


# --- P1 : la vis en plongée ---------------------------------------------------------------------
def palier(r: float, a0: float, k: int) -> str:
    """Un palier vu d'en haut, de rayon extérieur r : le mur (r à 0,86 r), les marches en rayons
    (0,86 r à RAPPORT r), tourné de a0 ; assombri selon sa profondeur k."""
    c = R
    rm, ri = r * .86, r * RAPPORT
    o = [f'<circle cx="{c}" cy="{c}" r="{r:.1f}" fill="{MINE}"/>',
         f'<circle cx="{c}" cy="{c}" r="{r:.1f}" fill="none" {ST} stroke-width="{max(2, 6 * r / R):.1f}"/>',
         f'<circle cx="{c}" cy="{c}" r="{rm:.1f}" fill="{PAPIER}" {ST} stroke-width="{max(1.5, 5 * r / R):.1f}"/>']
    ep = max(1.2, 4 * r / R)
    # les assises du mur : un joint au milieu, des joints montants décalés d'une assise à l'autre
    rj = (r + rm) / 2
    o.append(f'<circle cx="{c}" cy="{c}" r="{rj:.1f}" fill="none" stroke="{ENCRE}" stroke-width="{ep * .5:.1f}" opacity=".6"/>')
    for j in range(36):
        a = math.radians(j * 10 + (5 if j % 2 else 0))
        for r0, r1 in ((rm, rj), (rj, r)):
            a1 = a + (math.radians(5) if r0 == rj else 0)
            o.append(f'<path d="M{c + r0 * math.cos(a1):.1f} {c + r0 * math.sin(a1):.1f} L{c + r1 * math.cos(a1):.1f} {c + r1 * math.sin(a1):.1f}" '
                     f'stroke="{ENCRE}" stroke-width="{ep * .5:.1f}" opacity=".6"/>')
    for m in range(MARCHES):
        a = math.radians(a0 + m * 360 / MARCHES)
        # le nez de marche : un rayon un peu courbe, l'ombre de la contremarche à côté
        x0, y0 = c + ri * math.cos(a), c + ri * math.sin(a)
        x1, y1 = c + rm * math.cos(a), c + rm * math.sin(a)
        a2 = a + math.radians(360 / MARCHES * .28)
        x2, y2 = c + rm * math.cos(a2), c + rm * math.sin(a2)
        x3, y3 = c + ri * math.cos(a2), c + ri * math.sin(a2)
        o.append(f'<path d="M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f} L{x3:.1f} {y3:.1f} Z" fill="{LAVIS}" opacity=".55"/>')
        o.append(f'<path d="M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f}" {ST} stroke-width="{ep:.1f}"/>')
    o.append(f'<circle cx="{c}" cy="{c}" r="{ri:.1f}" fill="none" {ST} stroke-width="{ep:.1f}"/>')
    # la profondeur : chaque palier plus bas est plus sombre (la lumière vient d'en haut, de nous)
    o.append(f'<circle cx="{c}" cy="{c}" r="{r:.1f}" fill="{ENCRE}" opacity="{min(.9, .17 * k):.2f}"/>')
    return "".join(o)


def vis() -> str:
    o: list[str] = []
    # le premier palier déborde du cadre (r > R) : aucun coin ne se voit en tournant
    r = R * 1.42
    k = 0
    while r > 14:
        o.append(palier(r, k * DECALAGE, k))
        r *= RAPPORT
        k += 1
    o.append(f'<circle cx="{R}" cy="{R}" r="{r + 2:.1f}" fill="{ENCRE}"/>')
    return "".join(o)


def dessus(k: int) -> str:
    """Tobie vu d'en haut, tourné vers le haut de l'image (k : la foulée)."""
    p = (-1, 1)[k]
    return (f'<g {ST}>'
            # les pieds qui dépassent, en alternance
            f'<ellipse cx="{80 - 14}" cy="{62 - 10 * p}" rx="7" ry="11" fill="{ENCRE}"/>'
            f'<ellipse cx="{80 + 14}" cy="{62 + 10 * p}" rx="7" ry="11" fill="{ENCRE}"/>'
            # les épaules de la capote, les pans
            f'<path d="M34 84 Q36 64 80 62 Q124 64 126 84 Q128 112 80 118 Q32 112 34 84 Z" fill="{LAVIS}" stroke-width="4"/>'
            # les bras qui balancent
            f'<ellipse cx="{36}" cy="{86 + 10 * p}" rx="11" ry="20" fill="{LAVIS}" stroke-width="4"/>'
            f'<ellipse cx="{124}" cy="{86 - 10 * p}" rx="11" ry="20" fill="{LAVIS}" stroke-width="4"/>'
            # la sacoche sur la hanche droite, sa sangle en travers
            f'<path d="M50 70 L112 104" stroke="{ENCRE}" stroke-width="3" fill="none"/>'
            f'<rect x="108" y="98" width="24" height="20" rx="3" fill="{ENCRE}"/>'
            # la capuche
            f'<ellipse cx="80" cy="82" rx="22" ry="25" fill="{ENCRE}"/>'
            f'<path d="M66 70 Q80 60 94 70" stroke="{MINE}" stroke-width="2" fill="none"/>'
            f'</g>')


# --- P2 : la cage de l'escalier, de côté ----------------------------------------------------------
def marche_xy(m: int) -> tuple[float, float]:
    """Le nez de la marche m (0 sous la porte)."""
    return 200 + 118 * m, 420 + 54 * m


def cage() -> str:
    o = [f'<rect width="{W}" height="{H}" fill="url(#pierre)"/>',
         f'<rect width="{W}" height="{H}" fill="{LAVIS}" opacity=".18"/>']
    # le mur s'arrondit : des bandes d'ombre verticales vers les bords
    for x, op in ((0, .25), (140, .12), (1700, .14), (1820, .28)):
        o.append(f'<rect x="{x}" y="0" width="140" height="{H}" fill="{ENCRE}" opacity="{op}"/>')
    # la porte d'en haut (fermée par le noir du couloir : la lumière viendra de la planche suivante)
    px, py = PORTE
    o.append(f'<path d="M{px - 90} 420 V{py + 60} Q{px} {py - 60} {px + 90} {py + 60} V420 Z" fill="{LAVIS}" {ST} stroke-width="6"/>')
    o.append(f'<path d="M{px - 110} 420 V{py + 54} Q{px} {py - 84} {px + 110} {py + 54} V420" fill="none" {ST} stroke-width="4"/>')
    # les marches : un palier sous la porte, puis les marches qui descendent ; le dessous en lavis
    pts = [f"{px - 140} 420"]
    for m in range(16):
        x, y = marche_xy(m)
        pts += [f"{x + 118} {y}", f"{x + 118} {y + 54}"]
    o.append(f'<path d="M{" L".join(pts)} L{W + 40} {H + 40} L{px - 140} {H + 40} Z" fill="{PAPIER}" {ST} stroke-width="5"/>')
    for m in range(16):
        x, y = marche_xy(m)
        o.append(f'<path d="M{x + 118} {y + 4} V{y + 50}" stroke="{LAVIS}" stroke-width="10" opacity=".6"/>')
        o.append(f'<path d="M{x + 30} {y + 18} h70" stroke="{MINE}" stroke-width="2"/>')
    o.append(f'<path d="M{px - 140} 470 L{W + 40} {470 + (W + 180 - px) * 54 / 118:.0f} L{W + 40} {H + 40} L{px - 140} {H + 40} Z" '
             f'fill="{LAVIS}" opacity=".45"/>')
    # la main courante : une corde passée dans des anneaux du mur
    o.append(f'<path d="M{px + 120} 300 Q{px + 600} 520 {W + 20} 900" fill="none" {ST} stroke-width="5"/>')
    for t in (.2, .45, .7):
        x = px + 120 + (W + 20 - px - 120) * t
        y = 300 + 600 * t * t + 100 * t
        o.append(f'<circle cx="{x:.0f}" cy="{y - 10:.0f}" r="9" fill="none" {ST} stroke-width="4"/>')
    return "".join(o)


def lumiere(k: int) -> str:
    """La porte d'en haut et son cône de lumière sur les marches, qui rétrécit (k 0 à 3)."""
    px, py = PORTE
    larg = (90, 46, 14, 5)[k]           # demi-largeur de l'ouverture éclairée
    portee = (1300, 900, 520, 0)[k]     # jusqu'où le cône descend
    o = []
    if k < 3:
        o.append(f'<path d="M{px - larg} {py + 40} L{px + larg} {py + 40} L{px + larg + portee * .9:.0f} {420 + portee * .46:.0f} '
                 f'L{px - larg + portee * .45:.0f} {420 + portee * .5:.0f} Z" fill="{PAPIER}" opacity=".22"/>')
        o.append(f'<path d="M{px - larg} {py + 40} L{px + larg} {py + 40} L{px + larg + portee * .6:.0f} {420 + portee * .3:.0f} '
                 f'L{px - larg + portee * .3:.0f} {420 + portee * .33:.0f} Z" fill="{PAPIER}" opacity=".25"/>')
        o.append(f'<path d="M{px - larg} 420 V{py + 60} Q{px} {py - 60 + (90 - larg)} {px + larg} {py + 60} V420 Z" fill="{PAPIER}"/>')
    else:
        o.append(f'<circle cx="{px}" cy="{py + 30}" r="5" fill="{PAPIER}"/>')
    return "".join(o)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    fichiers = {
        "cin_e4-crypte-vis": svg(vis(), VIS, VIS).replace(f'width="{VIS}" height="{VIS}"', f'width="{RENDU}" height="{RENDU}"', 1),
        "cin_e4-crypte-dessus": grille([dessus(k) for k in range(2)], 160, 160, 2),
        "cin_e4-crypte-cage": svg(cage()),
        "cin_e4-crypte-lumiere": bande([lumiere(k) for k in range(4)], ZONE_LUMIERE, 2),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"e4_descente_crypte : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
