#!/usr/bin/env python3
"""Génère les gestes de l'étape 2 (directive animation, balises de la Narrative #138).

Même format que tools/gen_gestes_e1.py : chr_<perso>_<geste>_01, images de 200 x 320, pieds à
(100, 316), jouées une fois à 10 i/s puis retour au repos (ou à l'image figée du mort).

  Brisse : lever-main (« Halte »), tendre (la main ouverte : « Montre ton pli »), donner (un
           biscuit de guerre), chauffer-cire (le pli au-dessus de sa bougie, la cire noire
           rougit à la dernière image : seul rouge permis, celui du sceau), montrer (vers la crête,
           à droite)
  le mort : lever-bras (le bras raide se lève d'un coup, comme un panneau, puis ne bouge plus),
            tourner-tete (la tête se relève et se tourne vers Tobie, sans visage lisible),
            detourner-tete (elle retombe vers le chemin)

Le mort est une image figée bras levé : lever-bras part du bras pendant, et tourner-tete finit
tête tournée. Pour que ces gestes ne sautent pas au retour, le code doit garder leur dernière
image (voir la PR).

Usage : python3 tools/gen_gestes_e2.py
"""
from __future__ import annotations

import math

from gen_chr_pnj_e2 import DEFS, DST, ENCRE, LAVIS, PAPIER, ST, brisse, mort, planche
from gen_gestes_e1 import ROUGE, bras, main_index, main_ouverte, main_poing

# --- Brisse : le bras gauche (à gauche de l'image) quitte la boîte de conserve ------------------
BRISSE_BRAS = (f'<path d="M80 176 Q92 214 126 222 L132 208 Q104 200 96 170 Z" fill="url(#h2)" {ST} stroke-width="2.4"/>',
               f'<path d="M124 226 Q122 210 132 206 Q138 214 134 228 Z" fill="{PAPIER}" {ST} stroke-width="1.9"/>',
               f'<path d="M84 186 L92 180 L100 186 M84 194 L92 188 L100 194" fill="none" stroke="{PAPIER}" stroke-width="2.4"/>')
B_EPAULE = (90.0, 160.0)


def bras_brisse(coude, main) -> str:
    return f'<g {ST}>' + bras(B_EPAULE, coude, main, "url(#h2)", 20, 18, 15, 2.4) + '</g>'


def galon(coude) -> str:
    """Les deux chevrons de caporal sur le haut du bras, quelle que soit sa pente."""
    ex, ey = B_EPAULE
    a = math.degrees(math.atan2(coude[1] - ey, coude[0] - ex)) - 90
    return (f'<g transform="rotate({a:.0f} {ex} {ey})"><path d="M82 176 L90 170 L98 176 M82 184 L90 178 L98 184" '
            f'fill="none" stroke="{PAPIER}" stroke-width="2.4"/></g>')


def brisse_avec(dessin: str, i: int = 0) -> str:
    """Brisse sans son bras gauche, et le dessin donné posé dans le même repère que son buste."""
    corps = brisse(i)
    for m in BRISSE_BRAS:
        assert m in corps, m
        corps = corps.replace(m, "", 1)
    fin = corps.rindex("</g>")              # fin du groupe du haut du corps (penché de 10°)
    return corps[:fin] + f'<g {ST}>{dessin}</g>' + corps[fin:]


B_REPOS = "".join(BRISSE_BRAS)


def biscuit(x: float, y: float) -> str:
    return (f'<rect x="{x - 11:.1f}" y="{y - 8:.1f}" width="22" height="16" fill="{PAPIER}" stroke-width="1.8"/>'
            + "".join(f'<circle cx="{x + dx:.1f}" cy="{y + dy:.1f}" r="1.1" fill="{ENCRE}" stroke="none"/>'
                      for dx in (-6, 0, 6) for dy in (-3, 3)))


def pli_petit(x: float, y: float, ang: float, cire: str = ENCRE) -> str:
    """Le pli tenu par Brisse : papier, ruban rouge, cachet (noir, puis rouge une fois chauffé)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.0f})">'
            f'<path d="M-15 -11 L15 -11 L15 11 L-15 11 Z" fill="{PAPIER}" stroke-width="2"/>'
            f'<path d="M-15 -11 L0 -2 L15 -11" fill="none" stroke-width="1.2"/>'
            f'<path d="M0 -11 V18 M0 11 L-4 20" stroke="{ROUGE}" stroke-width="2.6"/>'
            f'<circle cx="0" cy="0" r="4.8" fill="{cire}" stroke="{ENCRE}" stroke-width="1"/></g>')


def brisse_lever_main() -> list[str]:
    haut = bras_brisse((66, 140), (64, 96))
    return [brisse_avec(B_REPOS),
            brisse_avec(bras_brisse((70, 176), (62, 140)) + galon((70, 176)) + main_ouverte(62, 132, -8)),
            brisse_avec(haut + galon((66, 140)) + main_ouverte(64, 88, -4)),
            brisse_avec(haut + galon((66, 140)) + main_ouverte(65, 87, -2)),
            brisse_avec(bras_brisse((76, 188), (86, 160)) + galon((76, 188)) + main_ouverte(84, 152, 10)),
            brisse_avec(B_REPOS)]


def brisse_tendre() -> list[str]:
    """La main ouverte, paume en l'air, tendue vers Tobie : « Montre ton pli. »"""
    tendu = bras_brisse((66, 196), (34, 196))
    paume = (f'<path d="M22 190 Q30 200 44 198 L46 190 Q34 186 22 190 Z" fill="{PAPIER}" stroke-width="1.9"/>'
             f'<path d="M24 190 L14 186 M26 194 L15 192 M30 197 L19 197" stroke-width="2.4"/>')
    return [brisse_avec(B_REPOS),
            brisse_avec(bras_brisse((76, 200), (56, 204)) + galon((76, 200)) + main_poing(54, 204, 8)),
            brisse_avec(tendu + galon((66, 196)) + paume),
            brisse_avec(tendu + galon((66, 196)) + paume.replace("M24 190 L14 186", "M24 190 L15 184")),
            brisse_avec(B_REPOS)]


def brisse_donner() -> list[str]:
    """Il tire un biscuit de sa capote et le tend : « Et prends ça. »"""
    return [brisse_avec(B_REPOS),
            brisse_avec(bras_brisse((86, 210), (118, 196)) + galon((86, 210)) + biscuit(120, 186) + main_poing(118, 196, 8)),
            brisse_avec(bras_brisse((70, 200), (52, 194)) + galon((70, 200)) + biscuit(44, 188) + main_poing(52, 194, 8)),
            brisse_avec(bras_brisse((66, 196), (34, 192)) + galon((66, 196)) + biscuit(26, 186) + main_poing(34, 192, 8)),
            brisse_avec(bras_brisse((66, 196), (36, 194)) + galon((66, 196)) + main_ouverte(32, 194, -96, .9)),
            brisse_avec(B_REPOS)]


def brisse_chauffer_cire() -> list[str]:
    """Le pli tenu au-dessus de la flamme ; la cire ramollit (elle coule) puis rougit."""
    au_feu = bras_brisse((104, 196), (138, 178))
    goutte = f'<path d="M148 180 q-2 5 0 8 q2 -3 0 -8 Z" fill="{ENCRE}"/>'
    return [brisse_avec(B_REPOS, 0),
            brisse_avec(bras_brisse((100, 200), (130, 184)) + galon((100, 200)) + pli_petit(144, 172, -8) + main_poing(130, 184, 8), 1),
            brisse_avec(au_feu + galon((104, 196)) + pli_petit(150, 170, -4) + main_poing(138, 178, 8), 2),
            brisse_avec(au_feu + galon((104, 196)) + pli_petit(150, 170, -2) + goutte + main_poing(138, 178, 8), 3),
            brisse_avec(au_feu + galon((104, 196)) + pli_petit(150, 170, -2, ROUGE) + main_poing(138, 178, 8), 0),
            brisse_avec(bras_brisse((92, 204), (116, 196)) + galon((92, 204)) + pli_petit(124, 184, -10, ROUGE) + main_poing(116, 196, 8), 1)]


def brisse_montrer() -> list[str]:
    """Il montre la crête, devant lui à droite, le bras en travers de la poitrine."""
    return [brisse_avec(B_REPOS),
            brisse_avec(bras_brisse((104, 186), (134, 172)) + galon((104, 186)) + main_poing(134, 172, 8)),
            brisse_avec(bras_brisse((112, 176), (160, 160)) + galon((112, 176)) + main_index(160, 160, 190, .9)),
            brisse_avec(bras_brisse((112, 174), (162, 156)) + galon((112, 174)) + main_index(162, 156, 186, .9)),
            brisse_avec(B_REPOS)]


# --- le mort ----------------------------------------------------------------------------------
MORT_BRAS = (f'<path d="M146 228 L206 256 L200 270 L142 244 Z" fill="{PAPIER}" {ST} stroke-width="3"/>',
             f'<path d="M150 238 L200 262" stroke="#8C877A" stroke-width="1.4"/>',
             f'<path d="M202 252 L212 258 L210 268 L198 268 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>',
             f'<path d="M210 262 L218 268" {ST} stroke-width="2.2"/>')
MORT_TETE = (f'<path d="M160 258 Q180 252 188 270 Q190 290 176 298 Q160 300 154 286 Q150 268 160 258 Z" fill="url(#h2)" {ST} stroke-width="2.2"/>',
             f'<path d="M158 300 Q150 272 170 256 Q192 248 200 272 Z" fill="{LAVIS}" {ST} stroke-width="2.4"/>',
             f'<path d="M150 306 L206 270 L208 278 L156 312 Z" fill="{ENCRE}" {ST} stroke-width="1.4"/>')
NUQUE = (156.0, 262.0)


def bras_raide(ang: float) -> str:
    """Le bras tendu, raide comme une planche, tourné de ang degrés autour de l'épaule (0 = la pose
    figée, vers la droite et le bas ; positif = vers le bas)."""
    return f'<g transform="rotate({ang:.0f} 144 236)">' + "".join(MORT_BRAS) + '</g>'


def tete(ang: float, miroir: bool, lever: float) -> str:
    """La tête et le casque, pivotés autour de la nuque ; miroir = tournée vers Tobie (à gauche)."""
    nx, ny = NUQUE
    m = f" translate({nx} 0) scale(-1 1) translate({-nx} 0)" if miroir else ""
    return f'<g transform="translate(0 {-lever:.0f}) rotate({ang:.0f} {nx} {ny}){m}">' + "".join(MORT_TETE) + '</g>'


def mort_avec(bras_svg: str | None = None, tete_svg: str | None = None) -> str:
    corps = mort()
    if bras_svg is not None:
        for p in MORT_BRAS:
            corps = corps.replace(p, "", 1)
        i = corps.index('<path d="M50 252 Q110 250')      # le fil reste par-dessus
        corps = corps[:i] + bras_svg + corps[i:]
    if tete_svg is not None:
        for p in MORT_TETE:
            corps = corps.replace(p, "", 1)
        i = corps.index('<path d="M156 270 L152 306"')      # avant la plaque d'identité
        corps = corps[:i] + tete_svg + corps[i:]
    return corps


def mort_lever_bras() -> list[str]:
    """D'un coup : pendant, à mi-course, un peu trop haut, puis figé à la pose de toujours."""
    return [mort_avec(bras_raide(62)), mort_avec(bras_raide(20)), mort_avec(bras_raide(-6)), mort_avec(bras_raide(0))]


def mort_tourner_tete() -> list[str]:
    return [mort_avec(tete_svg=tete(0, False, 0)),
            mort_avec(tete_svg=tete(-18, False, 8)),
            mort_avec(tete_svg=tete(-30, True, 18)),
            mort_avec(tete_svg=tete(-34, True, 20))]


def mort_detourner_tete() -> list[str]:
    return [mort_avec(tete_svg=tete(-34, True, 20)),
            mort_avec(tete_svg=tete(-18, False, 8)),
            mort_avec(tete_svg=tete(0, False, 0))]


GESTES = {
    "brisse_lever-main": brisse_lever_main, "brisse_tendre": brisse_tendre, "brisse_donner": brisse_donner,
    "brisse_chauffer-cire": brisse_chauffer_cire, "brisse_montrer": brisse_montrer,
    "mort_lever-bras": mort_lever_bras, "mort_tourner-tete": mort_tourner_tete, "mort_detourner-tete": mort_detourner_tete,
}


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    for nom, fn in GESTES.items():
        (DST / f"chr_{nom}_01.svg").write_text(planche(fn()), encoding="utf-8")
    print(f"{len(GESTES)} gestes de l'étape 2 dans art/src/chr")


if __name__ == "__main__":
    main()
