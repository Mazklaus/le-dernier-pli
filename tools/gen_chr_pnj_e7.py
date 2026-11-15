#!/usr/bin/env python3
"""Génère les personnages de l'étape 7, le Destinataire, et leurs gestes.

Même repère et même échelle que les PNJ des étapes précédentes (source 240 x 420, sol à y 405,
centre à x 120, échelle 0,845) : images de 200 x 320, sol à y 316, centre à x 100. Tournées de
trois quarts vers la gauche, vers Tobie qui arrive.

L'étape 7 n'est plus inversée : papier presque blanc, encre noire, pas d'accent
(papier_etapes.gd). Le trait se fait rare, comme la page : peu de hachures, des aplats de papier.

  Lise (lise) : la vieille Enfouie de l'anneau 3, assise contre la rambarde sur un tabouret,
      fichu noué, châle sur les épaules ; elle tricote sans regarder, les yeux blancs, levés
      dans le vide. Une pelote au sol. Gestes : lire-doigts (la lettre de Matthieu dans les
      mains, l'index suit les lignes, puis elle la glisse sous son châle, contre elle), montrer
      (le bras tendu vers le bas de l'escalier : « Descends, petit »).
  La Mère-Cloche (mere-cloche) : une très vieille femme assise sous la plus grande des cloches,
      sur un bloc de pierre ; un voile sombre lui encadre le visage, la robe s'étale jusqu'au
      sol. Ses yeux ne voient plus, ses mains, si : sur ses genoux, une lame de bronze couverte
      de noms gravés trop fins pour être lus, que ses doigts parcourent. Gestes : lire-doigts
      (elle brise la cire noire du pli et le lit du bout des doigts), graver (le nom de Tobie
      au poinçon, sous les autres), toucher-sceau (deux doigts sur la cire, sans l'ouvrir :
      « Quatorze »).

Le sceau est de cire NOIRE : aucun rouge. Aucune cloche dessinée (elle est au-dessus du cadre).

Usage : python3 tools/gen_chr_pnj_e7.py
"""
from __future__ import annotations

from gen_chr_pnj_e2 import DST, ENCRE, LAVIS, MINE, PAPIER, ST, planche
from gen_gestes_e1 import bras, main_index, main_ouverte, main_poing

SOUFFLE = (0, 1, 2, 1)


def g(dessin: str) -> str:
    return f'<g {ST}>{dessin}</g>'


# ----------------------------------------------------------------------------- accessoires
def lettre(x: float, y: float, ang: float = 0.0, s: float = 1.0) -> str:
    """La lettre de Matthieu, une feuille dépliée, (x, y) au milieu ; quelques lignes d'écriture."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.0f}) scale({s})">'
            f'<path d="M-15 -11 L15 -12 L16 11 L-14 12 Z" fill="{PAPIER}" {ST} stroke-width="1.6"/>'
            f'<path d="M-15 0 L16 -1" stroke="{MINE}" stroke-width=".8"/>'
            f'<path d="M-10 -7 Q-2 -9 9 -8 M-10 -3 Q0 -5 11 -4 M-10 4 Q-1 2 10 3 M-10 8 Q-4 7 3 8" '
            f'fill="none" stroke="{ENCRE}" stroke-width=".9"/></g>')


def pli(x: float, y: float, ang: float = 0.0, ouvert: int = 0) -> str:
    """Le pli de Tobie, (x, y) au milieu : fermé, cacheté de cire noire (ouvert 0) ; cire brisée,
    la feuille qui s'ouvre (1) ; feuille dépliée, l'écriture serrée (2)."""
    if ouvert == 0:
        corps = (f'<path d="M-17 -11 H17 V11 H-17 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>'
                 f'<path d="M-17 -11 L0 1 L17 -11" fill="none" {ST} stroke-width="1.2"/>'
                 f'<path d="M-4.5 -2 Q-6 3 -1 5.5 Q5 6 5.5 0.5 Q5 -5 0 -5 Q-4 -5 -4.5 -2 Z" fill="{ENCRE}" stroke="{ENCRE}" stroke-width="1"/>')
    elif ouvert == 1:
        corps = (f'<path d="M-17 -11 H17 V11 H-17 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>'
                 f'<path d="M-17 -11 L-2 -24 L17 -11" fill="{PAPIER}" {ST} stroke-width="1.4"/>'
                 f'<path d="M-6 -3 l3 -3 l3 2 l-2 4 Z M4 2 l3 -2 l2 3 l-3 3 Z" fill="{ENCRE}" stroke="{ENCRE}" stroke-width=".8"/>')
    else:
        corps = (f'<path d="M-19 -15 L19 -16 L20 15 L-18 16 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>'
                 f'<path d="M-19 -1 L20 -2" stroke="{MINE}" stroke-width=".8"/>'
                 + "".join(f'<path d="M-14 {yy} Q0 {yy - 1.5} 15 {yy - .5}" fill="none" stroke="{ENCRE}" stroke-width=".8"/>'
                           for yy in (-11, -7, -4, 3, 7, 11)))
    e = 1.3 if ouvert == 2 else 1.0
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.0f}) scale({e})">{corps}</g>'


# ----------------------------------------------------------------------------- Lise
L_EPAULE_G, L_EPAULE_D = (116.0, 222.0), (150.0, 220.0)


def tete_lise(rot: float = 0.0, dy: float = 0.0) -> str:
    """La tête de Lise, fichu noué, yeux blancs ouverts sans pupille ; rot (degrés, positif :
    penchée vers la gauche, vers Tobie) autour du cou."""
    return (f'<g transform="translate(0 {dy:.1f}) rotate({-rot:.1f} 128 206)">'
            f'<path d="M118 192 L136 192 L136 212 L118 212 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>'
            f'<ellipse cx="124" cy="170" rx="18" ry="22" fill="{PAPIER}" {ST} stroke-width="2.2"/>'
            # le fichu : sur la tête, noué sur la nuque, un pan qui pend
            f'<path d="M103 168 Q100 138 125 135 Q150 137 148 168 Q148 186 142 198 L139 170 Q128 150 106 166 Z" fill="url(#h2)" {ST} stroke-width="2"/>'
            f'<path d="M144 186 L156 198 L150 210 L141 196 Z" fill="url(#h2)" {ST} stroke-width="1.6"/>'
            # des mèches blanches qui s'échappent
            f'<path d="M107 160 Q105 168 107 174 M111 156 Q109 162 110 167" fill="none" stroke="{MINE}" stroke-width="1"/>'
            # les yeux blancs, ouverts, sans pupille ; paupières lourdes
            f'<path d="M108 168 Q112 165 117 168 Q112 170.5 108 168 Z M123 168 Q127 165 132 168 Q127 170.5 123 168 Z" fill="{PAPIER}" stroke="{ENCRE}" stroke-width="1.2"/>'
            f'<path d="M107 165 Q112 162 118 165 M122 165 Q127 162 133 165" fill="none" stroke="{ENCRE}" stroke-width="1.3"/>'
            f'<path d="M108 172 Q112 174 116 172 M123 172 Q127 174 131 172" fill="none" stroke="{MINE}" stroke-width=".9"/>'
            # nez, bouche mince, rides
            f'<path d="M119 169 L115 179 L120 180" fill="none" stroke="{ENCRE}" stroke-width="1.3"/>'
            f'<path d="M112 186 Q117 188 123 186" fill="none" stroke="{ENCRE}" stroke-width="1.4"/>'
            f'<path d="M108 182 Q110 188 113 190 M128 182 Q127 188 124 191 M109 158 Q118 155 127 158" fill="none" stroke="{MINE}" stroke-width=".9"/>'
            '</g>')


def corps_lise(i: int) -> str:
    """Le tabouret, la jupe longue, le buste voûté et le châle (sans les bras)."""
    s = SOUFFLE[i] * .5
    return "".join([
        # le tabouret
        f'<path d="M110 318 H176 V328 H110 Z" fill="url(#h1)" {ST} stroke-width="2.2"/>',
        f'<path d="M116 328 L108 405 M170 328 L178 405 M112 372 H174" fill="none" {ST} stroke-width="3"/>',
        # la pelote, au sol, et son fil
        f'<circle cx="58" cy="396" r="9" fill="{PAPIER}" {ST} stroke-width="1.8"/>',
        f'<path d="M51 392 Q58 388 65 394 M52 399 Q58 395 64 401" fill="none" stroke="{ENCRE}" stroke-width=".9"/>',
        # la jupe : les cuisses à l'horizontale jusqu'aux genoux, puis le tombé jusqu'aux sabots
        f'<path d="M158 298 Q120 294 78 302 Q66 308 70 322 L72 400 H142 L146 334 Q158 324 158 298 Z" fill="url(#h2)" {ST} stroke-width="2.2"/>',
        f'<path d="M80 304 Q118 298 150 304" fill="none" stroke="{PAPIER}" stroke-width="1.4"/>',
        f'<path d="M92 322 Q88 360 94 398 M118 324 Q122 360 118 398" fill="none" stroke="{PAPIER}" stroke-width="1.2"/>',
        f'<path d="M70 398 Q68 405 74 405 H100 Q102 398 96 396 Z M110 398 Q108 405 114 405 H138 Q140 398 134 396 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>',
        f'<g transform="translate(0 {s:.1f})">',
        # le buste, la blouse claire, le châle croisé
        f'<path d="M118 212 Q146 200 164 218 Q172 262 158 312 L100 312 Q98 268 118 212 Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>',
        f'<path d="M110 214 Q140 198 168 216 L162 266 Q132 280 104 262 Z" fill="url(#h1)" {ST} stroke-width="2.2"/>',
        f'<path d="M112 222 L136 262 M164 224 L136 262" fill="none" {ST} stroke-width="1.4"/>',
        f'<path d="M132 264 l-4 12 M138 266 l2 12 M144 264 l5 11" fill="none" stroke="{ENCRE}" stroke-width="1.2"/>',
        '</g>',
    ])


def tricot(m1, m2, sur_genoux: bool = False) -> str:
    """Les deux aiguilles et le tricot qui pend entre les mains m1 et m2 ; sur_genoux : posé
    sur la jupe, les aiguilles à plat."""
    if sur_genoux:
        return (f'<path d="M94 304 L132 302 L134 314 L96 316 Z" fill="url(#h1)" {ST} stroke-width="1.6"/>'
                f'<path d="M84 300 L142 298 M88 296 L140 304" stroke="{ENCRE}" stroke-width="1.6"/>'
                f'<path d="M96 312 Q80 340 62 388" fill="none" stroke="{ENCRE}" stroke-width=".9"/>')
    (x1, y1), (x2, y2) = m1, m2
    return (f'<path d="M{x1:.1f} {y1:.1f} L{x1 + 22:.1f} {y1 - 26:.1f} M{x2:.1f} {y2:.1f} L{x2 - 26:.1f} {y2 - 22:.1f}" stroke="{ENCRE}" stroke-width="1.8"/>'
            f'<path d="M{x1 + 6:.1f} {y1 + 2:.1f} L{x2 - 6:.1f} {y2 + 2:.1f} L{x2 - 8:.1f} {y2 + 20:.1f} L{x1 + 6:.1f} {y1 + 22:.1f} Z" fill="url(#h1)" {ST} stroke-width="1.6"/>'
            f'<path d="M{x1 + 8:.1f} {y1 + 22:.1f} Q80 350 62 388" fill="none" stroke="{ENCRE}" stroke-width=".9"/>')


def bras_lise(epaule, coude, main) -> str:
    return bras(epaule, coude, main, "url(#h1)", 15, 13, 11, 2.2)


def lise(i: int = 0, mains: str | None = None, tete: float = 0.0, dy_tete: float = 0.0) -> str:
    """Lise assise ; mains : bras et mains (et ce qu'elles tiennent), sinon elle tricote."""
    s = SOUFFLE[i] * .5
    if mains is None:
        a = (0, 1.5, 0, -1.5)[i]
        m1, m2 = (102.0, 290.0 - a), (128.0, 288.0 + a)
        mains = (tricot(m1, m2) + g(bras_lise(L_EPAULE_G, (106, 262), m1) + bras_lise(L_EPAULE_D, (146, 264), m2)
                                   + main_poing(*m1, 6) + main_poing(*m2, 6)))
    return corps_lise(i) + f'<g transform="translate(0 {s:.1f})">' + mains + tete_lise(tete, dy_tete) + '</g>'


def lise_lire_doigts() -> list[str]:
    """La lettre dans les mains ; elle la monte contre sa poitrine, l'index droit suit les
    lignes de gauche à droite, la tête levée vers rien ; puis elle la glisse sous son châle."""
    def tient(lx, ly, md, doigt: bool = True, ang: float = 0) -> str:
        mg = (lx - 22, ly + 4)
        d = (main_index(md[0], md[1], -100, .7) if doigt else main_poing(*md, 6))
        return (tricot((0, 0), (0, 0), True) + lettre(lx, ly, ang, 1.4)
            + g(bras_lise(L_EPAULE_G, (104, 262), mg) + main_poing(*mg, 6)
                + bras_lise(L_EPAULE_D, (150, 266), md) + d))
    return [lise(0, tient(112, 290, (134, 294), False)),
            lise(1, tient(116, 262, (138, 266), False, -6), 4),
            lise(2, tient(116, 262, (104, 238)), 8, -1),
            lise(3, tient(116, 262, (116, 238)), 9, -1),
            lise(0, tient(116, 262, (128, 238)), 10, -1),
            lise(1, tricot((0, 0), (0, 0), True)
                 + f'<path d="M124 236 L140 234 L138 244 L124 246 Z" fill="{PAPIER}" {ST} stroke-width="1.4"/>'
                 + g(bras_lise(L_EPAULE_G, (110, 258), (126, 246)) + main_ouverte(126, 246, -60, .75)
                     + bras_lise(L_EPAULE_D, (152, 262), (138, 250)) + main_ouverte(138, 250, -80, .75)), 2)]


def lise_montrer() -> list[str]:
    """Le bras gauche quitte le tricot et se tend vers le bas de l'escalier, l'index pointé ;
    la tête suit, sans regarder ; puis le bras revient."""
    def montre(coude, main, ang, s: float = .8) -> str:
        m2 = (128.0, 290.0)
        return (f'<path d="M{m2[0]:.1f} {m2[1]:.1f} L{m2[0] - 26:.1f} {m2[1] - 22:.1f}" stroke="{ENCRE}" stroke-width="1.8"/>'
                f'<path d="M{m2[0] - 4:.1f} {m2[1] + 2:.1f} L{m2[0] - 20:.1f} {m2[1] + 2:.1f} L{m2[0] - 22:.1f} {m2[1] + 22:.1f} L{m2[0] - 4:.1f} {m2[1] + 20:.1f} Z" fill="url(#h1)" {ST} stroke-width="1.6"/>'
                + g(bras_lise(L_EPAULE_D, (146, 264), m2) + main_poing(*m2, 6)
                    + bras_lise(L_EPAULE_G, coude, main) + main_index(main[0], main[1], ang, s)))
    return [lise(0),
            lise(1, montre((96, 250), (82, 268), -20), 3),
            lise(2, montre((86, 244), (58, 270), -38), 8, 1),
            lise(3, montre((86, 244), (56, 272), -40), 9, 1),
            lise(0, montre((86, 244), (58, 270), -38), 8, 1),
            lise(1, montre((98, 252), (86, 272), -20), 3)]


# ----------------------------------------------------------------------------- la Mère-Cloche
M_EPAULE_G, M_EPAULE_D = (108.0, 206.0), (150.0, 204.0)


def tete_mere(rot: float = 0.0, dy: float = 0.0) -> str:
    """La tête, très vieille, sous un voile sombre qui l'encadre ; les yeux clos, creusés."""
    return (f'<g transform="translate(0 {dy:.1f}) rotate({-rot:.1f} 128 196)">'
            f'<ellipse cx="124" cy="160" rx="18" ry="23" fill="{PAPIER}" {ST} stroke-width="2.2"/>'
            # le voile : du sommet du crâne aux épaules, ouvert sur le visage
            f'<path d="M96 206 Q90 140 124 126 Q160 130 158 206 Q150 168 140 146 Q126 136 110 146 Q100 168 96 206 Z" fill="url(#h2)" {ST} stroke-width="2.2"/>'
            f'<path d="M104 140 Q124 128 146 140" fill="none" stroke="{PAPIER}" stroke-width="1.2"/>'
            # les yeux clos, profonds
            f'<path d="M107 158 Q112 161 117 158 M122 158 Q127 161 132 158" fill="none" stroke="{ENCRE}" stroke-width="1.6"/>'
            f'<path d="M106 154 Q112 151 118 154 M121 154 Q127 151 133 154" fill="none" stroke="{MINE}" stroke-width="1"/>'
            f'<path d="M108 163 Q112 165 116 163 M123 163 Q127 165 131 163" fill="none" stroke="{MINE}" stroke-width=".9"/>'
            # nez, bouche, rides profondes
            f'<path d="M119 159 L115 170 L120 171" fill="none" stroke="{ENCRE}" stroke-width="1.3"/>'
            f'<path d="M112 177 Q118 179 124 177" fill="none" stroke="{ENCRE}" stroke-width="1.4"/>'
            f'<path d="M107 168 Q108 176 112 181 M130 168 Q130 176 126 182 M110 146 Q120 143 130 146 M113 185 Q118 187 122 185" fill="none" stroke="{MINE}" stroke-width=".9"/>'
            '</g>')


def lame(grave: float = 0.0) -> str:
    """La lame de bronze sur ses genoux, couverte de noms trop fins pour être lus ; grave : la
    longueur (0 à 1) du nom en train d'être gravé, sous les autres."""
    r = [(70, 293, 22), (96, 292, 30), (130, 291, 14), (72, 297, 16), (92, 296.5, 12), (108, 296, 26),
         (138, 295.5, 8), (70, 301, 28), (102, 300.5, 18), (124, 300, 20)]
    out = [f'<path d="M64 288 L150 285 L152 308 L66 312 Z" fill="{LAVIS}" {ST} stroke-width="2"/>',
           f'<path d="M66 309 L152 305" stroke="{MINE}" stroke-width="1"/>']
    for x, y, l in r:
        out.append(f'<path d="M{x} {y} q{l * .3:.1f} -1 {l * .5:.1f} 0 t{l * .5:.1f} 0" fill="none" stroke="{PAPIER}" stroke-width=".9"/>')
    if grave > 0:
        out.append(f'<path d="M84 305 l{40 * grave:.1f} -1" stroke="{PAPIER}" stroke-width="1.4"/>')
    return "".join(out)


def corps_mere(i: int, grave: float = 0.0, lame_visible: bool = True) -> str:
    """Le bloc de pierre, la robe qui s'étale jusqu'au sol, le buste (sans les bras)."""
    s = SOUFFLE[i] * .5
    return "".join([
        # le bloc de pierre où elle est assise
        f'<path d="M140 286 H200 V405 H140 Z" fill="url(#h1)" {ST} stroke-width="2.4"/>',
        f'<path d="M140 330 H200 M170 286 V330 M156 330 V405" fill="none" stroke="{ENCRE}" stroke-width="1.2"/>',
        # la robe : des genoux au sol, en grands plis
        f'<path d="M156 288 Q170 340 186 402 L30 402 Q46 346 62 296 Q104 282 156 288 Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>',
        f'<path d="M80 306 Q68 350 56 400 M106 304 Q100 352 96 400 M132 304 Q138 352 142 400 M150 300 Q162 350 170 400" fill="none" stroke="{ENCRE}" stroke-width="1.2"/>',
        f'<path d="M30 402 Q108 392 186 402 L188 405 H28 Z" fill="{LAVIS}" {ST} stroke-width="1.6"/>',
        f'<g transform="translate(0 {s:.1f})">',
        # le buste, large, la robe montée jusqu'au cou
        f'<path d="M106 198 Q130 190 154 200 Q168 250 158 294 L74 294 Q90 250 106 198 Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>',
        f'<path d="M118 200 Q124 246 116 294 M140 200 Q146 250 142 292" fill="none" stroke="{ENCRE}" stroke-width="1.2"/>',
        lame(grave) if lame_visible else '',
        '</g>',
    ])


def bras_mere(epaule, coude, main) -> str:
    """La manche large de la robe."""
    return bras(epaule, coude, main, PAPIER, 22, 18, 14, 2.2)


def main_lisante(x: float, y: float, ang: float = -90, s: float = 1.0) -> str:
    """Une grande main de vieille, à plat, les doigts vers la gauche (ang -90), qui lit."""
    return main_ouverte(x, y, ang, s)


def mere(i: int = 0, mains: str | None = None, tete: float = 0.0, dy_tete: float = 0.0, grave: float = 0.0) -> str:
    """La Mère-Cloche assise ; mains : bras et mains, sinon posées sur la lame, les doigts sur
    les noms (ils glissent un peu au fil de la respiration)."""
    s = SOUFFLE[i] * .5
    if mains is None:
        d = (0, 2, 4, 2)[i]
        mains = g(bras_mere(M_EPAULE_G, (96, 256), (86 - d, 294)) + main_lisante(86 - d, 294)
                  + bras_mere(M_EPAULE_D, (150, 254), (128 - d, 292)) + main_lisante(128 - d, 292))
    return corps_mere(i, grave) + f'<g transform="translate(0 {s:.1f})">' + mains + tete_mere(tete, dy_tete) + '</g>'


def tient_pli(cx: float, cy: float, ouvert: int, md=None, doigt: bool = False) -> str:
    """Le pli tenu à deux mains au-dessus de la lame ; md : la main droite ailleurs (qui lit)."""
    l = 27 if ouvert == 2 else 20
    mg = (cx - l, cy + 4)
    md = md or (cx + l, cy + 4)
    droite = main_index(md[0], md[1], -100, .8) if doigt else main_poing(*md, 7)
    return (pli(cx, cy, 0, ouvert)
            + g(bras_mere(M_EPAULE_G, (98, 252), mg) + main_poing(*mg, 7)
                + bras_mere(M_EPAULE_D, (152, 252), md) + droite))


def mere_lire_doigts() -> list[str]:
    """Le pli fermé dans ses mains ; elle brise la cire sans hésiter, la feuille s'ouvre ; ses
    doigts lisent, de gauche à droite, la tête levée ; puis la feuille redescend sur la lame."""
    return [mere(0, tient_pli(112, 262, 0)),
            mere(1, tient_pli(112, 262, 1), 2),
            mere(2, tient_pli(112, 258, 2, (100, 236), True), 6, -1),
            mere(3, tient_pli(112, 258, 2, (112, 236), True), 7, -1),
            mere(0, tient_pli(112, 258, 2, (124, 236), True), 8, -1),
            mere(1, tient_pli(110, 280, 2), 3)]


def mere_graver() -> list[str]:
    """Le poinçon dans la main droite, la gauche à plat sur la lame : elle grave le nom sous
    les autres, d'un trait ; puis ses doigts passent sur le nom frais."""
    def grave(pointe, mg, doigts_sur_nom: bool = False) -> str:
        px, py = pointe
        poincon = (f'<path d="M{px:.1f} {py:.1f} L{px + 10:.1f} {py - 26:.1f}" stroke="{ENCRE}" stroke-width="2"/>'
                   f'<path d="M{px + 8:.1f} {py - 22:.1f} L{px + 16:.1f} {py - 42:.1f}" stroke="{ENCRE}" stroke-width="8" stroke-linecap="round"/>'
                   f'<path d="M{px + 8:.1f} {py - 22:.1f} L{px + 16:.1f} {py - 42:.1f}" stroke="{LAVIS}" stroke-width="4" stroke-linecap="round"/>')
        md = (px + 12, py - 30)
        gauche = main_lisante(mg[0], mg[1] - (4 if doigts_sur_nom else 0), -90, 1.0)
        return (poincon + g(bras_mere(M_EPAULE_G, (94, 256), mg) + gauche
                            + bras_mere(M_EPAULE_D, (152, 254), md) + main_poing(*md, 7)))
    return [mere(0, grave((88, 286), (74, 298))),
            mere(1, grave((86, 304), (72, 298)), 3, 0, 0.05),
            mere(2, grave((104, 303), (72, 298)), 4, 0, 0.5),
            mere(3, grave((124, 302), (72, 298)), 4, 0, 1.0),
            mere(0, grave((132, 286), (104, 304), True), 6, -1, 1.0),
            mere(1, grave((132, 286), (122, 302), True), 6, -1, 1.0)]


def mere_toucher_sceau() -> list[str]:
    """Le pli fermé dans la main gauche ; deux doigts de la droite se posent sur la cire, y
    restent, sans l'ouvrir ; puis le pli redescend sur la lame."""
    def touche(md, ang: float, cy: float = 262) -> str:
        mg = (92.0, cy + 4)
        return (pli(112, cy, 0, 0)
                + g(bras_mere(M_EPAULE_G, (96, 254), mg) + main_poing(*mg, 7)
                    + bras_mere(M_EPAULE_D, (152, 254), md) + main_index(md[0], md[1], ang, .8)))
    return [mere(0, tient_pli(112, 262, 0)),
            mere(1, touche((134, 254), -150), 2),
            mere(2, touche((128, 258), -140), 5),
            mere(3, touche((128, 258), -140), 7),
            mere(0, touche((128, 258), -140), 7),
            mere(1, tient_pli(112, 280, 0), 3)]


PLANCHES = {
    "chr_lise_repos_01": lambda: [lise(i) for i in range(4)],
    "chr_lise_lire-doigts_01": lise_lire_doigts,
    "chr_lise_montrer_01": lise_montrer,
    "chr_mere-cloche_repos_01": lambda: [mere(i) for i in range(4)],
    "chr_mere-cloche_lire-doigts_01": mere_lire_doigts,
    "chr_mere-cloche_graver_01": mere_graver,
    "chr_mere-cloche_toucher-sceau_01": mere_toucher_sceau,
}


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    for nom, fn in PLANCHES.items():
        (DST / f"{nom}.svg").write_text(planche(fn()), encoding="utf-8")
    print(f"{len(PLANCHES)} planches de l'étape 7 dans art/src/chr")


if __name__ == "__main__":
    main()
