#!/usr/bin/env python3
"""Génère les images NOUVELLES des épilogues animés « Le Dernier Pli » (planche validée par le GD
le 17/11) ; tout le reste est réemployé (gravures, cinés, décors). Plein écran 1920 x 1080 ou
calques transparents, 10 i/s.

Tribut (lettre b) :
  cin_epi-b-patere     calque : la patère vide de l'abri du sergent, la trace claire de la sacoche ;
  cin_epi-b-cendre     3 images de cendre qui tombe (calques transparents, rendus à demi-taille) ;
  cin_epi-b-nom        fond : une cloche de près, sous la terre, un nom gravé (illisible) au flanc.
Cloches (lettre c) :
  cin_epi-c-campanile  fond : les cloches pendues dans le noir de la descente, sans la grande ni
                       les trois qu'on libère ;
  cin_epi-c-grande     la grande cloche seule, transparente, pendue par sa corde (le jeu la balance) ;
  cin_epi-c-petites    les trois petites cloches libérées, 2 images chacune (bouchée, ouverte),
                       grille 2 x 3 ; cin_epi-c-bouchon : le bouchon de cire qui tombe ;
  cin_epi-c-poussiere  3 images de poussière qui tombe de la couronne (calques) ;
  cin_epi-c-ondes      2 images d'ondes (arcs gravés) par-dessus la grande cloche.
Garde-fous : aucun rouge (le ruban est déjà sur la table) ; la cire est noire ; rien de ce qui
pend dans la grande cloche n'est montré (sa bouche reste bouchée).

Usage : python3 tools/gen_cin_epilogues_anim.py
"""
from __future__ import annotations

import random

from gen_cin_e1 import DST, H, W, bande, svg
from gen_cin_e7 import cloche
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER

STP = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
# la grande cloche dans son calque : couronne en (G_X, G_Y), hauteur G_H
G_W, G_H, G_X, G_Y = 900, 880, 450, 140
# les petites cloches libérées, dans l'écran : (x, y du haut, hauteur)
PETITES = [(300, 300, 170), (1560, 220, 150), (1700, 520, 190)]
CASE_P = (240, 300)     # case d'une petite cloche dans sa planche
AUTRES = [(150, 120, 110), (520, 80, 90), (420, 640, 130), (1350, 120, 100), (1820, 120, 90), (120, 820, 100),
          (1480, 760, 140), (1820, 860, 110)]


def calque(w: int, h: int, contenu: str, vb: tuple[float, float, float, float] | None = None, rendu: float = 1.0) -> str:
    x, y, vw, vh = vb or (0, 0, w, h)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(w * rendu)}" height="{int(h * rendu)}" '
            f'viewBox="{x} {y} {vw} {vh}">{contenu}</svg>\n')


# --- b : la patère vide ---------------------------------------------------------------------
def patere() -> str:
    """Un crochet de fer planté dans la planche, et sous lui la trace plus claire qu'a laissée la
    sacoche pendue des années (la poussière de tranchée ne l'a pas encore recouverte)."""
    return calque(220, 300,
                  f'<path d="M40 70 Q40 230 110 250 Q180 230 180 70 Z" fill="{PAPIER}" opacity=".35"/>'
                  f'<path d="M40 70 Q40 230 110 250 Q180 230 180 70" fill="none" stroke="{MINE}" stroke-width="2" stroke-dasharray="6 8"/>'
                  f'<rect x="96" y="30" width="28" height="16" fill="{ENCRE}"/>'
                  f'<path d="M110 46 V74 Q110 92 128 92 Q142 92 142 80" fill="none" {STP} stroke-width="7"/>')


def cendre(k: int) -> str:
    """Des flocons de cendre gris, épars, rendus à demi-taille : 3 images qui bouclent (chaque flocon
    descend d'un cran ; les mêmes graines d'une image à l'autre)."""
    r = random.Random(41)
    out = []
    for _ in range(160):
        x, y = r.uniform(0, W), r.uniform(0, H)
        e = r.uniform(2, 6)
        y = (y + k * 26) % H
        x += [0, 6, 2][k] * (1 if r.random() < .5 else -1)
        out.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{e:.1f}" ry="{e * .6:.1f}" fill="{MINE}" opacity="{r.uniform(.5, .9):.2f}"/>')
    return "".join(out)


def nom_grave() -> str:
    """Le fond du dernier plan du tribut : une cloche de près, dans le noir sous la terre ; au
    flanc, un nom gravé à la pointe (des traits de lettres qu'on ne lit pas), la cire au bord."""
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>']
    for k, (x, y, h) in enumerate(AUTRES[:5]):
        o.append(f'<g opacity=".55">{cloche(x, y, h, seed=60 + k, trait=1.8)}</g>')
    o.append(cloche(960, -60, 1150, seed=66, trait=6))
    r = random.Random(67)
    # le nom : une ligne de lettres gravées, des jambages et des boucles, sans lettre lisible
    x, y = 760, 540
    traits = []
    while x < 1160:
        hl = r.uniform(26, 48)
        if r.random() < .35:
            traits.append(f'M{x:.0f} {y:.0f} q{r.uniform(6, 12):.0f} {-hl:.0f} {r.uniform(14, 22):.0f} 0')
            x += r.uniform(22, 30)
        else:
            traits.append(f'M{x:.0f} {y:.0f} l{r.uniform(-4, 6):.0f} {-hl:.0f}')
            x += r.uniform(10, 18)
    o.append(f'<path d="{" ".join(traits)}" fill="none" {STP} stroke-width="3.4"/>')
    o.append(f'<path d="{" ".join(traits)}" fill="none" stroke="{PAPIER}" stroke-width="1" transform="translate(1.6 1.6)"/>')
    o.append(f'<path d="M740 560 Q960 572 1180 560" fill="none" stroke="{ENCRE}" stroke-width="1.6"/>')
    return svg("".join(o))


# --- c : le campanile ------------------------------------------------------------------------
def campanile() -> str:
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>']
    for k, (x, y, h) in enumerate(AUTRES):
        o.append(f'<g opacity=".7">{cloche(x, y, h, seed=70 + k, trait=2.2)}</g>')
    # la corde de la grande cloche, qui monte dans le noir (la cloche, elle, est un calque)
    return svg("".join(o))


def grande() -> str:
    """La grande cloche, transparente ; l'origine du balancement est le haut de la corde visible
    (G_X, 0), où le jeu pose le pivot."""
    return calque(G_W, G_Y + G_H + 160, cloche(G_X, G_Y, G_H, seed=79, trait=6, corde=True))


def petites() -> str:
    """Trois petites cloches, deux images chacune : bouchée de cire (0), ouverte (1) avec le bord
    de cire fendu qui reste à la lèvre. Grille 2 colonnes (état) x 3 lignes (cloche)."""
    cw, ch = CASE_P
    out = []
    for i, (_, _, h) in enumerate(PETITES):
        for etat in (0, 1):
            x0, y0 = etat * cw, i * ch
            c = cloche(x0 + cw / 2, y0 + 30, h * .9 * min(1, 230 / h), cire=etat == 0, seed=90 + i, trait=2.4, corde=False)
            if etat == 1:
                hh = h * .9 * min(1, 230 / h)
                ww = hh * .9
                bx, by = x0 + cw / 2, y0 + 30 + hh
                c += (f'<path d="M{bx - ww * .5:.0f} {by:.0f} q{ww * .12:.0f} {hh * .06:.0f} {ww * .2:.0f} {hh * .02:.0f} '
                      f'M{bx + ww * .5:.0f} {by:.0f} q{-ww * .1:.0f} {hh * .07:.0f} {-ww * .22:.0f} {hh * .01:.0f}" fill="none" {STP} stroke-width="4"/>')
            out.append(f'<path d="M{x0 + cw / 2} {y0} V{y0 + 30}" stroke="{ENCRE}" stroke-width="1.6"/>' + c)
    return calque(cw * 2, ch * 3, "".join(out))


def bouchon() -> str:
    """Le bouchon de cire qui tombe : une galette noire fendue, vue de biais."""
    return calque(90, 40, f'<path d="M6 20 Q45 2 84 18 Q86 30 70 34 L52 26 L40 36 Q10 36 6 20 Z" fill="{ENCRE}"/>'
                          f'<path d="M30 14 Q46 10 62 16" stroke="{LAVIS}" stroke-width="2" fill="none"/>')


def poussiere(k: int) -> str:
    """La poussière qui tombe de la couronne, en filets de points sous la poutre (calque de 900 x 900,
    centré sur la couronne)."""
    r = random.Random(81)
    out = []
    for _ in range(70):
        x = 450 + r.gauss(0, 120)
        y = (r.uniform(0, 900) + k * 30) % 900
        e = r.uniform(1.4, 3.4)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{e:.1f}" fill="{PAPIER}" stroke="{ENCRE}" stroke-width=".9"/>')
    return "".join(out)


def ondes(k: int) -> str:
    """Le son : des arcs gravés, en tirets, qui partent de la lèvre (calque 1920 x 1080, la lèvre de
    la grande cloche en (960, 840) à l'écran) ; l'image 1 les décale d'un demi-pas vers l'extérieur."""
    out = []
    for i, rr in enumerate((260, 420, 600, 800, 1020)):
        rr += k * 70
        out.append(f'<path d="M{960 - rr} 840 A{rr} {rr * .55} 0 0 1 {960 + rr} 840" fill="none" stroke="{ENCRE}" '
                   f'stroke-width="{3.2 - i * .4:.1f}" stroke-dasharray="{22 + i * 8} {12 + i * 4}" opacity="{.9 - i * .14:.2f}"/>')
    return "".join(out)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    fichiers = {
        "cin_epi-b-patere": patere(),
        "cin_epi-b-cendre": bande([cendre(k) for k in range(3)], (0, 0, W, H), 1).replace(
            f'width="{W}" height="{H * 3}"', f'width="{W // 2}" height="{H * 3 // 2}"', 1),
        "cin_epi-b-nom": nom_grave(),
        "cin_epi-c-campanile": campanile(),
        "cin_epi-c-grande": grande(),
        "cin_epi-c-petites": petites(),
        "cin_epi-c-bouchon": bouchon(),
        "cin_epi-c-poussiere": bande([poussiere(k) for k in range(3)], (0, 0, 900, 900), 3),
        "cin_epi-c-ondes": bande([ondes(k) for k in range(2)], (0, 0, W, H), 1).replace(
            f'width="{W}" height="{H * 2}"', f'width="{W // 2}" height="{H}"', 1),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"épilogues animés : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
