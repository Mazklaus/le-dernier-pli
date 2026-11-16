#!/usr/bin/env python3
"""Génère la cinématique e6_eboulement (retouche du GD : une vraie ciné, dessinée) : à l'entrée
du village, la voûte de la galerie d'où vient Tobie cède derrière lui.

Un seul plan, le village à l'échelle du jeu (repère du village décalé de X0) : le fond est le
décor du village (tools/gen_decors_e6.village), la galerie encore ouverte, Tobie debout.
L'écran de l'étape 6 est inversé : la poussière est en lavis (pâle à l'écran), les pierres ont
un trait d'encre (clair à l'écran) sur papier (la nuit).

  cin_eboulement_01  le fond 1920 x 1080 (l'image 0 entière) ;
  cin_eboulement_02  8 images de ZONE, grille 3 x 3, rendues à l'ÉCHELLE 0,75 (poussière floue :
                     le poids compte plus que le détail ; le jeu les remet à 1/ÉCHELLE) :
                     0 des graviers tombent de la voûte, Tobie debout ; 1 il lève la tête,
                     la poussière coule ; 2 la voûte se fend, l'étai plie, Tobie fait volte-face ;
                     3 la voûte cède : des blocs en l'air, l'étai casse, Tobie se jette en avant ;
                     4 les blocs touchent le sol, la poussière jaillit, Tobie à plat ventre ;
                     5 le nuage couvre tout le passage ; 6 il retombe lentement, l'éboulis
                     apparaît, Tobie à quatre pattes ; 7 l'éboulis (le même que le calque
                     fx_eboule-village), un reste de poussière au sol. Durées : TEMPS.

Aucun rouge (Tobie est vu en pied, le ruban n'est qu'un trait), aucune cloche.

Usage : python3 tools/gen_cin_e6_eboulement.py
"""
from __future__ import annotations

from gen_cin_e1 import DST, H, W, bande, svg
from gen_cin_e6 import tobie_boule, tobie_debout, tobie_etale, tobie_quatre_pattes
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER, rnd
from gen_decors_e3_surface import DEFS as DEFS_DECOR
from gen_decors_e6 import EBOULE_X, EBOULE_Y, fx_eboule, village

X0 = 300
ZONE = (360, 260, 1100, 820)
ECHELLE = 0.75
TEMPS = [0.6, 0.8, 0.3, 0.2, 0.3, 1.2, 1.2, 1.4]
# la poussière s'éteint avant les bords de la zone dessinée (sinon le nuage y est coupé net)
_x, _y, _w, _h = ZONE
MASQUE_ZONE = (f'<filter id="flou-bord" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="36"/></filter>'
               f'<mask id="m-zone" maskUnits="userSpaceOnUse" x="{_x}" y="{_y}" width="{_w}" height="{_h}">'
               f'<rect x="{_x + 110}" y="{_y + 110}" width="{_w - 220}" height="{_h}" fill="#fff" filter="url(#flou-bord)"/></mask>')
ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
# la galerie dans le repère de l'écran (village x 850 à 1000, voûte de 440 à 520)
GX0, GX1, VOUTE = 850 - X0, 1000 - X0, 470
TOBIE_X, PIED = 880, 900


def tobie_tete_haute(x: float, pied: float, s: float = .9) -> str:
    """Tobie debout qui lève la tête vers la voûte : sa tête et sa capuche pivotent vers l'arrière."""
    corps = tobie_debout(x, pied, "bas", s)
    i = corps.index('<path d="M-30 -262 Q-62 -300')
    fin = corps.rindex("</g>")
    return corps[:i] + '<g transform="rotate(28 0 -262)">' + corps[i:fin] + "</g></g>"


def miroir(contenu: str, x: float, y: float) -> str:
    """Un dessin de la chute (centré en (0, 0), à l'échelle du plan B de e6_chute_fissure) retourné
    (il regardait à gauche, il va vers la droite) et remis à la taille de Tobie dans le village."""
    return f'<g transform="translate({x} {y}) scale(-1.45 1.45)">{contenu}</g>'


def graviers(k: int, n: int, y0: float, y1: float, gros: float = 1.0) -> str:
    r = rnd(900 + k)
    out = []
    for _ in range(n):
        x = r.uniform(GX0 + 4, GX1 - 4)
        y = r.uniform(y0, y1)
        e = r.uniform(3, 7) * gros
        out.append(f'<path d="M{x:.0f} {y:.0f} l{e:.0f} {-e * .6:.0f} l{e * .8:.0f} {e * .7:.0f} l{-e * .4:.0f} {e:.0f} Z" fill="{MINE}" {ST} stroke-width="1.4"/>')
    return "".join(out)


def coulee(k: int, n: int) -> str:
    """La poussière qui coule de la voûte en filets."""
    r = rnd(950 + k)
    out = []
    for _ in range(n):
        x = r.uniform(GX0 + 10, GX1 - 10)
        out.append(f'<path d="M{x:.0f} {VOUTE + 40} q{r.uniform(-6, 6):.0f} {r.uniform(80, 200):.0f} {r.uniform(-10, 10):.0f} {r.uniform(160, 380):.0f}" '
                   f'fill="none" stroke="{LAVIS}" stroke-width="{r.uniform(2, 5):.1f}" opacity=".7"/>')
    return "".join(out)


def nuage(cx: float, cy: float, rx: float, ry: float, densite: float, seed: int) -> str:
    """Un nuage de poussière flou (en lavis : pâle à l'écran)."""
    r = rnd(seed)
    out = [f'<g mask="url(#m-zone)"><g filter="url(#flou-poussiere)" opacity="{densite:.2f}">']
    for _ in range(12):
        out.append(f'<ellipse cx="{cx + r.uniform(-rx, rx) * .7:.0f}" cy="{cy + r.uniform(-ry, ry) * .6:.0f}" rx="{rx * r.uniform(.35, .6):.0f}" '
                   f'ry="{ry * r.uniform(.35, .6):.0f}" fill="{LAVIS}"/>')
    out.append("</g></g>")
    return "".join(out)


def etai(k: int) -> str:
    """Les étais de la galerie : droits (0, 1), qui plient (2), cassés (3 et après, sous les blocs)."""
    if k <= 1:
        return ""
    if k == 2:
        return (f'<path d="M{GX0 + 16} {PIED} Q{GX0 + 30} {(PIED + 528) / 2} {GX0 + 18} 540 M{GX1 - 16} {PIED} Q{GX1 - 4} {(PIED + 528) / 2} {GX1 - 18} 544" '
                f'fill="none" {ST} stroke-width="7"/><path d="M{GX0 + 8} 540 L{GX1 - 8} 552" {ST} stroke-width="7"/>')
    if k == 3:   # l'étai casse : deux tronçons de travers, l'un tombe
        return (f'<path d="M{GX0 + 16} {PIED} L{GX0 + 24} 700 M{GX0 + 30} 690 L{GX0 + 70} 560" {ST} stroke-width="7"/>'
                f'<path d="M{GX0 + 70} 600 L{GX1 + 20} 660" {ST} stroke-width="7"/>')
    return ""


def blocs(k: int) -> str:
    """Les blocs de la voûte : fendus (2), en l'air (3), au sol (4, dans la poussière)."""
    r = rnd(970)
    out = []
    if k == 2:
        out.append(f'<path d="M{GX0 + 10} 520 L{GX0 + 40} 500 L{GX0 + 70} 530 L{GX0 + 100} 498 L{GX1 - 20} 526" fill="none" {ST} stroke-width="3"/>'
                   f'<path d="M{GX0 + 60} 470 L{GX0 + 66} 440 M{GX1 - 40} 480 L{GX1 - 30} 450" {ST} stroke-width="2.4"/>')
        out.append(graviers(2, 30, 540, PIED - 10, 1.6))
    elif k == 3:
        for _ in range(9):
            x = r.uniform(GX0 - 20, GX1 + 30)
            y = r.uniform(500, 820)
            e = r.uniform(18, 42)
            out.append(f'<path d="M{x:.0f} {y:.0f} l{e:.0f} {-e * .5:.0f} l{e * .7:.0f} {e * .8:.0f} l{-e * .5:.0f} {e * .9:.0f} l{-e:.0f} {-e * .2:.0f} Z" '
                       f'fill="{PAPIER}" {ST} stroke-width="3" transform="rotate({r.uniform(-30, 30):.0f} {x:.0f} {y:.0f})"/>')
        out.append(graviers(3, 50, 480, PIED - 10, 2.0))
    return "".join(out)


def eboulis(k: int) -> str:
    """L'éboulis du calque fx_eboule-village (repère du village), qui se forme (4) puis reste."""
    if k < 4:
        return ""
    calque = fx_eboule().replace(f'<g transform="translate({-EBOULE_X} {-EBOULE_Y})">', "<g>", 1)
    return f'<g transform="translate({-X0} 0)">{calque}</g>'


def image(k: int) -> str:
    """L'image k du plan (voir le docstring)."""
    o = [f'<g transform="translate({-X0} 0)">{village()}</g>']
    if k <= 1:
        o.append(graviers(k, 8 + k * 10, VOUTE + 60, PIED - 10))
        o.append(coulee(k, 2 + k * 4))
    o.append(eboulis(k))
    o.append(etai(k))
    o.append(blocs(k))
    if k == 0:
        o.append(tobie_debout(TOBIE_X, PIED, "bas", .9))
    elif k == 1:
        o.append(tobie_tete_haute(TOBIE_X, PIED))
    elif k == 2:
        o.append(tobie_debout(TOBIE_X + 30, PIED, "battent", .9))
    elif k == 3:
        o.append(miroir(tobie_boule(-30), TOBIE_X + 260, PIED - 170))
    elif k in (4, 5):
        o.append(miroir(tobie_etale(), TOBIE_X + 470, PIED - 30))
    else:
        o.append(miroir(tobie_quatre_pattes(), TOBIE_X + 470, PIED - 126))
    densites = {4: (.8, 1.0), 5: (.78, 1.3), 6: (.5, 1.2), 7: (.2, 1.1)}
    if k in densites:
        d, t = densites[k]
        o.append(nuage(GX0 + 200, 640, 260 * t, 300 * t, d, 990 + k))
        o.append(nuage(GX0 + 220, PIED - 30, 380 * t, 80 * t, min(1, d + .2), 995 + k))
    return (DEFS_DECOR + '<defs><filter id="flou-poussiere" x="-50%" y="-50%" width="200%" height="200%">'
            '<feGaussianBlur stdDeviation="26"/></filter>' + MASQUE_ZONE + '</defs>' + "".join(o))


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    (DST / "cin_eboulement_01.svg").write_text(svg(image(0)), encoding="utf-8")
    w, h = ZONE[2] * 3, ZONE[3] * 3
    planche = bande([image(k) for k in range(8)], ZONE, 3).replace(
        f'width="{w}" height="{h}"', f'width="{round(w * ECHELLE)}" height="{round(h * ECHELLE)}"', 1)
    (DST / "cin_eboulement_02.svg").write_text(planche, encoding="utf-8")
    print("e6_eboulement : 2 planches dans art/src/cin/")


if __name__ == "__main__":
    main()
