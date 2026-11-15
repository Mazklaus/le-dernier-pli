#!/usr/bin/env python3
"""Génère les personnages de l'étape 4, l'abbaye des Recousus, et leurs gestes.

Même repère et même échelle que les PNJ des étapes 1 à 3 (source 240 x 420, sol à y 405,
centre à x 120, échelle 0,845) : images de 200 x 320, sol à y 316, centre à x 100. Tournés de
trois quarts vers la gauche, vers Tobie qui arrive.

  sœur Maude (maude) : la portière. Forme : le croissant, une vieille courbée sous une grande
      cornette blanche aux ailes raides. Gestes : laver (les pieds de Tobie dans la bassine),
      baiser-ruban (elle porte à ses lèvres le bout du ruban rouge du pli).
  le caporal Fernand (fernand) : un Recousu assis au bord de son lit, en chemise de nuit, l'écusson
      de la Tranchée-Mère cousu dessus ; sa jambe droite est une jambe de statue (pierre et
      drapé). Forme : le carré tassé. Gestes : se-redresser, hocher-tete, montrer.
  frère Anselme (anselme) : le chirurgien. Forme : la lame, long et net, tablier de cuir clair,
      manches retroussées, loupe sur le front. Gestes : examiner (il prend le visage de Tobie à
      deux mains et le tourne vers la lampe), ranger-bocal, montrer, cendrer.

Le rouge n'apparaît que sur le ruban du pli (baiser-ruban). Aucune plaie ni aucun œil montré.

Usage : python3 tools/gen_chr_pnj_e4.py
"""
from __future__ import annotations

import math

from gen_chr_pnj_e2 import DST, ENCRE, LAVIS, MINE, PAPIER, ST, planche
from gen_gestes_e1 import ROUGE, bras, main_index, main_ouverte, main_poing

SOUFFLE = (0, 1, 2, 1)
PIERRE = "#F6F4EE"          # pierre lavée de la jambe de saint : plus pâle que le papier de la peau


def g(dessin: str) -> str:
    return f'<g {ST}>{dessin}</g>'


# ----------------------------------------------------------------------------- sœur Maude
def maude(i: int = 0, penche: float = 0.0, mains: str | None = None, bassine: bool = False,
          tete: float = 0.0) -> str:
    """penche : le buste se courbe encore vers l'avant (degrés) ; mains : remplace les mains qui
    tiennent le linge ; bassine : la bassine posée devant elle ; tete : la tête s'incline."""
    s = SOUFFLE[i]
    out = []
    if bassine:
        out.append(f'<path d="M14 372 L22 404 L84 404 L92 372 Z" fill="url(#h1)" {ST} stroke-width="2.4"/>'
                   f'<ellipse cx="53" cy="372" rx="40" ry="8" fill="{PAPIER}" {ST} stroke-width="2.2"/>'
                   f'<path d="M26 372 Q40 368 52 373 Q66 377 80 371" fill="none" stroke="{MINE}" stroke-width="1.6"/>')
    # pieds, bas de la robe noire
    out.append(f'<path d="M96 396 L92 405 L120 405 L118 396 Z M126 396 L126 405 L152 405 L150 396 Z" fill="{ENCRE}" {ST} stroke-width="1.4"/>')
    out.append(f'<g transform="translate(0 {s * .6:.1f}) rotate({-penche:.1f} 130 330)">')
    # la robe : un croissant noir, le dos très rond, le ventre creux
    out.append(f'<path d="M150 150 Q176 190 172 260 Q170 330 160 400 L86 400 Q90 320 98 270 Q100 230 92 196 Q100 160 150 150 Z" fill="{ENCRE}" {ST} stroke-width="2.6"/>')
    out.append(f'<path d="M140 172 Q160 240 150 396" fill="none" stroke="{LAVIS}" stroke-width="2"/>')
    # le chapelet qui pend de la ceinture : grains de papier
    for k in range(7):
        out.append(f'<circle cx="{104 + k * 1.5:.1f}" cy="{262 + k * 10}" r="2.6" fill="{PAPIER}" stroke="{ENCRE}" stroke-width="1"/>')
    out.append(f'<path d="M112 336 V350 M107 343 H117" stroke="{PAPIER}" stroke-width="2"/>')
    # les mains et le linge plié
    if mains is None:
        out.append(f'<path d="M88 226 L132 224 L134 244 L90 248 Z" fill="{PAPIER}" {ST} stroke-width="2"/>'
                   f'<path d="M90 236 H132" stroke="{MINE}" stroke-width="1.2"/>'
                   f'<path d="M86 222 Q78 234 88 248 Q96 246 96 236 Q96 226 86 222 Z M134 220 Q142 232 134 246 Q126 244 126 234 Q126 224 134 220 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>')
    else:
        out.append(g(mains))
    # tête, inclinée vers Tobie : petit visage ridé dans la guimpe, sous la cornette
    out.append(f'<g transform="rotate({-tete:.1f} 122 176)">')
    out.append(f'<path d="M96 170 Q100 140 124 136 Q148 140 150 170 Q140 186 122 188 Q104 186 96 170 Z" fill="{PAPIER}" {ST} stroke-width="2"/>')
    out.append(f'<ellipse cx="116" cy="150" rx="15" ry="18" fill="{PAPIER}" {ST} stroke-width="2"/>')
    out.append(f'<path d="M106 146 Q109 149 112 146 M118 146 Q121 149 124 146" fill="none" {ST} stroke-width="1.5"/>'
               f'<path d="M104 154 Q106 158 110 158 M122 158 Q126 158 128 154 M110 162 Q116 160 122 162" fill="none" {ST} stroke-width="1.1"/>'
               f'<path d="M114 150 L111 156 L115 157" fill="none" {ST} stroke-width="1.2"/>')
    # la grande cornette blanche, deux ailes raides
    out.append(f'<path d="M100 140 Q84 132 54 104 Q78 108 104 122 Q116 112 132 118 Q160 102 196 96 Q170 124 146 140 Q124 128 100 140 Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
    out.append(f'<path d="M66 110 Q86 122 102 132 M184 102 Q160 120 142 134" fill="none" stroke="{MINE}" stroke-width="1.4"/>')
    out.append('</g></g>')
    return "".join(out)


M_EPAULE_G, M_EPAULE_D = (104.0, 196.0), (144.0, 190.0)


def mains_maude(gauche, droite, coude_g, coude_d, extra: str = "") -> str:
    # les manches noires sur la robe noire : un trait de mine pour qu'on les lise
    return (f'<g stroke="{MINE}">' + bras(M_EPAULE_G, coude_g, gauche, ENCRE, 16, 14, 12, 2.2)
            + bras(M_EPAULE_D, coude_d, droite, ENCRE, 16, 14, 12, 2.2) + '</g>' + extra
            + f'<ellipse cx="{gauche[0]}" cy="{gauche[1]}" rx="8" ry="7" fill="{PAPIER}" stroke-width="1.8"/>'
            + f'<ellipse cx="{droite[0]}" cy="{droite[1]}" rx="8" ry="7" fill="{PAPIER}" stroke-width="1.8"/>')


def maude_laver() -> list[str]:
    """Elle se penche sur la bassine, frotte doigt par doigt, se relève à demi."""
    def frotte(dx: float, p: float, k: int) -> str:
        return maude(k % 4, penche=p, bassine=True,
                     mains=mains_maude((70 + dx, 300), (96 - dx, 302), (96, 260), (130, 262),
                                       f'<path d="M66 304 L104 300" stroke="{PAPIER}" stroke-width="8"/>'))
    return [maude(0, bassine=True),
            maude(1, penche=12, bassine=True, mains=mains_maude((80, 270), (108, 268), (98, 240), (134, 240))),
            frotte(0, 24, 2), frotte(8, 24, 3), frotte(-4, 24, 0),
            maude(1, penche=10, bassine=True, mains=mains_maude((84, 262), (112, 262), (98, 236), (134, 236)))]


def maude_baiser_ruban() -> list[str]:
    """Le bout du ruban rouge (il vient du pli de Tobie, à gauche) monte jusqu'à ses lèvres."""
    def ruban(x: float, y: float) -> str:
        return (f'<path d="M0 {y + 40:.0f} Q{x / 2:.0f} {y + 30:.0f} {x:.0f} {y:.0f}" fill="none" stroke="{ENCRE}" stroke-width="5"/>'
                f'<path d="M0 {y + 40:.0f} Q{x / 2:.0f} {y + 30:.0f} {x:.0f} {y:.0f}" fill="none" stroke="{ROUGE}" stroke-width="3"/>')
    return [maude(0),
            maude(1, mains=mains_maude((90, 228), (112, 226), (96, 214), (132, 216), ruban(98, 226))),
            maude(2, tete=4, mains=mains_maude((100, 176), (118, 176), (90, 210), (140, 206), ruban(108, 172))),
            maude(3, tete=14, mains=mains_maude((104, 166), (120, 166), (90, 204), (140, 200), ruban(110, 162))),
            maude(0, tete=14, mains=mains_maude((104, 166), (120, 166), (90, 204), (140, 200), ruban(110, 162))),
            maude(1, tete=4, mains=mains_maude((92, 226), (114, 224), (96, 212), (132, 214), ruban(100, 222)))]


# ----------------------------------------------------------------------------- Fernand
def fernand(i: int = 0, droit: float = 0.0, tete: float = 0.0, bras_g: str | None = None) -> str:
    """Assis au bord du lit. droit : de 0 (tassé) à 1 (redressé) ; tete : hochement (degrés, vers
    le bas) ; bras_g : remplace le bras gauche posé sur la cuisse."""
    s = SOUFFLE[i]
    tasse = 1 - droit
    out = [
        # le lit de fer d'hôpital, derrière lui, dans sa longueur : barreaux de tête à gauche, oreiller,
        # drap qui retombe, pied de lit bas à droite
        f'<path d="M26 232 V405 M66 232 V405 M218 270 V405 M234 270 V405" {ST} stroke-width="4"/>',
        f'<path d="M26 236 Q46 222 66 236 M26 252 H66 M36 246 V300 M46 242 V300 M56 246 V300 M218 274 Q226 266 234 274 M218 288 H234" fill="none" {ST} stroke-width="2.4"/>',
        f'<path d="M26 300 H234 V332 H26 Z" fill="url(#h1)" {ST} stroke-width="2.2"/>',
        f'<path d="M30 296 H230 V326 Q200 340 176 330 Q150 342 120 332 Q96 342 70 330 Q50 338 30 330 Z" fill="{PAPIER}" {ST} stroke-width="2"/>',
        f'<path d="M92 300 Q96 318 92 336 M200 300 Q204 316 200 334 M150 300 Q146 320 150 338" fill="none" stroke="{MINE}" stroke-width="1.3"/>',
        f'<path d="M32 296 Q34 282 56 282 L80 284 Q88 290 80 298 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>',
        f'<path d="M44 332 V405 M210 332 V405" {ST} stroke-width="3"/>',
        # jambe gauche : la sienne, nue, pantoufle
        f'<path d="M126 306 L92 316 L96 330 L120 324 Z" fill="{PAPIER}" {ST} stroke-width="2"/>',
        f'<path d="M92 316 L86 396 L100 398 L104 328 Z" fill="{PAPIER}" {ST} stroke-width="2"/>',
        f'<path d="M98 332 Q96 360 94 392" fill="none" stroke="{MINE}" stroke-width="1.2"/>',
        f'<path d="M78 394 L76 405 L106 405 L102 394 Z" fill="{ENCRE}" {ST} stroke-width="1.4"/>',
        # jambe droite : une jambe de saint en pierre lavée, plus pâle que la peau, avancée presque
        # tendue vers le joueur, devant l'autre ; pas de jonction (la chemise la couvre jusqu'à la
        # hanche). Genou de pierre net, drapé sculpté sur la cuisse seulement, sandale large et nette.
        f'<path d="M126 306 L156 304 L172 340 L150 346 Z" fill="{PIERRE}" {ST} stroke-width="2.2"/>',
        f'<path d="M136 310 Q150 318 158 334 M146 306 Q160 316 166 330 M130 316 Q142 326 150 342" fill="none" stroke="{MINE}" stroke-width="1.5"/>',
        f'<path d="M150 346 Q160 350 172 340" fill="none" {ST} stroke-width="1.8"/>',
        f'<path d="M152 344 L160 388 L182 386 L172 338 Z" fill="{PIERRE}" {ST} stroke-width="2.2"/>',
        f'<path d="M162 348 Q166 352 164 358" fill="none" stroke="{MINE}" stroke-width="1.3"/>',
        f'<path d="M166 360 l5 7 l-3 6 l6 7 M140 320 l6 6 l-2 5" fill="none" stroke="{ENCRE}" stroke-width="1"/>',
        ''.join(f'<circle cx="{x}" cy="{y}" r=".9" fill="{MINE}"/>' for x, y in ((158, 366), (170, 374), (164, 380), (176, 360), (148, 326), (156, 338))),
        # la sandale de saint : semelle épaisse, lanières croisées, cinq orteils de pierre
        f'<path d="M156 386 L184 384 L200 396 L200 402 L152 402 Z" fill="{PIERRE}" {ST} stroke-width="2"/>',
        f'<path d="M148 401 H204 V405.5 H148 Z" fill="{LAVIS}" {ST} stroke-width="1.4"/>',
        f'<path d="M160 388 L182 400 M180 386 L162 400 M171 384 V392" stroke="{LAVIS}" stroke-width="2.2"/>',
        ''.join(f'<path d="M{x} 401 q2.6 -6 5.2 0" fill="{PIERRE}" {ST} stroke-width="1.1"/>' for x in (180, 185, 190, 194.5, 198.5)),
        f'<g transform="translate({tasse * 4:.1f} {s * .5 + tasse * 10:.1f}) rotate({tasse * -8:.1f} 140 310)">',
        # la chemise de nuit, l'écusson de la Tranchée-Mère cousu (la cloche sans battant)
        f'<path d="M110 180 Q140 168 170 182 Q182 240 176 312 L112 312 Q104 250 110 180 Z" fill="{PAPIER}" {ST} stroke-width="2.6"/>',
        f'<path d="M140 186 V230" {ST} stroke-width="1.2"/><path d="M118 200 Q124 260 120 308" fill="none" stroke="{MINE}" stroke-width="1.4"/>',
        f'<path d="M150 214 L168 214 L168 232 Q159 240 150 232 Z" fill="url(#h2)" {ST} stroke-width="1.6"/>',
        f'<path d="M154 230 Q155 220 159 220 Q163 220 164 230 Z" fill="{PAPIER}" stroke="none"/>',
        f'<path d="M152 214 L148 210 M168 214 L172 210" stroke="{ENCRE}" stroke-width="1" stroke-dasharray="2 2"/>',
        # bras droit, posé sur la jambe de pierre
        f'<path d="M170 190 Q186 240 168 290 L154 284 Q168 240 158 196 Z" fill="{PAPIER}" {ST} stroke-width="2.2"/>',
        f'<ellipse cx="160" cy="292" rx="10" ry="8" fill="{PAPIER}" {ST} stroke-width="1.8"/>',
    ]
    if bras_g is None:
        out.append(f'<path d="M112 188 Q96 240 108 290 L122 286 Q112 240 124 196 Z" fill="{PAPIER}" {ST} stroke-width="2.2"/>'
                   f'<ellipse cx="114" cy="294" rx="10" ry="8" fill="{PAPIER}" {ST} stroke-width="1.8"/>')
    else:
        out.append(g(bras_g))
    # tête : rasée, joues creuses ; une couture fine au cou (recousu), le regard droit
    out.append(f'<g transform="rotate({tete - tasse * 10:.1f} 140 178)">')
    out.append(f'<path d="M132 166 L148 166 L148 180 L132 180 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>')
    out.append(f'<path d="M132 174 H148" stroke="{ENCRE}" stroke-width="1" stroke-dasharray="2 2"/>')
    out.append(f'<ellipse cx="138" cy="144" rx="20" ry="24" fill="{PAPIER}" {ST} stroke-width="2.2"/>')
    out.append(f'<path d="M124 140 L132 140 M140 140 L148 140" {ST} stroke-width="2.2"/>'
               f'<path d="M132 144 L128 152 L133 153" fill="none" {ST} stroke-width="1.3"/>'
               f'<path d="M128 160 L140 160" {ST} stroke-width="1.5"/>'
               f'<path d="M122 150 Q124 158 128 162 M152 150 Q150 158 146 162" fill="none" stroke="{MINE}" stroke-width="1.2"/>'
               f'<path d="M120 132 Q124 116 140 116 Q154 118 158 132" fill="url(#pt)" {ST} stroke-width="1.6"/>')
    out.append('</g></g>')
    return "".join(out)


F_EPAULE = (116.0, 194.0)


def fernand_se_redresser() -> list[str]:
    return [fernand(0, d) for d in (0, .3, .6, .9, 1, 1)]


def fernand_hocher_tete() -> list[str]:
    return [fernand(0, 1, t) for t in (0, 10, 2, 10, 0)]


def fernand_montrer() -> list[str]:
    """Il montre la porte de l'atelier, à gauche, du bras tendu."""
    def b(coude, main, ang, poing=False) -> str:
        m = main_poing(main[0], main[1], 8) if poing else main_index(main[0], main[1], ang, .9)
        return bras(F_EPAULE, coude, main, PAPIER, 18, 16, 14, 2.2) + m
    return [fernand(0, 1),
            fernand(1, 1, bras_g=b((96, 214), (80, 196), 0, True)),
            fernand(2, 1, bras_g=b((92, 200), (60, 186), 4)),
            fernand(3, 1, bras_g=b((92, 200), (58, 184), 2)),
            fernand(0, 1)]


# ----------------------------------------------------------------------------- frère Anselme
def anselme(i: int = 0, bras_svg: str | None = None, tete: float = 0.0) -> str:
    """bras_svg : remplace les mains jointes sur le tablier ; tete : inclinaison vers la gauche."""
    s = SOUFFLE[i]
    out = [
        f'<path d="M100 394 L96 405 L124 405 L122 394 Z M128 394 L128 405 L156 405 L152 394 Z" fill="{ENCRE}" {ST} stroke-width="1.4"/>',
        f'<g transform="translate(0 {s * .7:.1f})">',
        # la robe de bure, longue et droite : la lame
        f'<path d="M104 128 Q124 118 146 128 Q156 200 158 280 L162 398 L92 398 L96 280 Q96 200 104 128 Z" fill="url(#h2)" {ST} stroke-width="2.6"/>',
        # le tablier de cuir clair, net, noué haut
        f'<path d="M106 150 L144 150 L150 392 L100 392 Z" fill="{PAPIER}" {ST} stroke-width="2.2"/>',
        f'<path d="M106 150 Q124 132 144 150" fill="none" {ST} stroke-width="1.6"/>',
        f'<path d="M100 196 Q124 202 150 196" fill="none" {ST} stroke-width="2.4"/>',
        f'<path d="M114 230 V380 M136 230 V380" stroke="{MINE}" stroke-width="1.2"/>',
        # trousse d'outils fins à la ceinture
        f'<path d="M148 200 L164 202 L162 246 L148 244 Z" fill="url(#h1)" {ST} stroke-width="1.8"/>',
        f'<path d="M152 202 V190 M156 202 V186 M160 202 V192" {ST} stroke-width="1.6"/>',
    ]
    if bras_svg is None:
        # avant-bras nus, retroussés, mains jointes sur le tablier
        out.append(f'<path d="M104 136 Q92 180 108 214 L118 208 Q106 180 114 144 Z M146 136 Q158 180 142 214 L132 208 Q144 180 136 144 Z" fill="url(#h2)" {ST} stroke-width="2.2"/>'
                   f'<path d="M108 210 Q124 202 142 210 L138 228 Q124 234 112 228 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>'
                   f'<path d="M124 206 V230" {ST} stroke-width="1"/>')
    else:
        out.append(g(bras_svg))
    # tête longue, tonsure, loupe relevée sur le front ; un visage calme
    out.append(f'<g transform="rotate({-tete:.1f} 124 120)">')
    out.append(f'<ellipse cx="124" cy="92" rx="17" ry="26" fill="{PAPIER}" {ST} stroke-width="2.2"/>')
    out.append(f'<path d="M108 82 Q110 64 124 64 Q138 64 140 82 Q132 74 124 74 Q116 74 108 82 Z" fill="url(#h1)" {ST} stroke-width="1.6"/>')
    out.append(f'<circle cx="124" cy="72" r="7" fill="{PAPIER}" {ST} stroke-width="1.8"/><path d="M110 76 L117 73 M131 73 L138 76" {ST} stroke-width="1.2"/>')
    out.append(f'<path d="M112 92 L120 92 M128 92 L136 92" {ST} stroke-width="1.8"/>'
               f'<path d="M122 94 L119 104 L123 105" fill="none" {ST} stroke-width="1.3"/>'
               f'<path d="M117 112 Q124 114 131 112" fill="none" {ST} stroke-width="1.5"/>')
    out.append('</g></g>')
    return "".join(out)


A_EPAULE_G, A_EPAULE_D = (106.0, 136.0), (144.0, 136.0)


def bras_anselme(epaule, coude, main) -> str:
    return bras(epaule, coude, main, "url(#h2)", 16, 14, 12, 2.2)


def anselme_examiner() -> list[str]:
    """Il prend le visage de Tobie entre ses deux mains et le tourne vers la lampe."""
    def m(g_, d_, cg, cd, ang=0) -> str:
        return (bras_anselme(A_EPAULE_D, cd, d_) + main_ouverte(d_[0], d_[1], -80 + ang, .9)
                + bras_anselme(A_EPAULE_G, cg, g_) + main_ouverte(g_[0], g_[1], -100 + ang, .9))
    return [anselme(0),
            anselme(1, m((60, 140), (84, 150), (84, 170), (110, 176))),
            anselme(2, m((30, 110), (54, 118), (70, 150), (96, 156)), 6),
            anselme(3, m((30, 104), (56, 112), (70, 146), (96, 150), -14), 8),
            anselme(0, m((30, 104), (56, 112), (70, 146), (96, 150), -14), 8),
            anselme(1)]


def bocal(x: float, y: float) -> str:
    """Un bocal de verre fermé, quelque chose d'indistinct dans le liquide (lavis)."""
    return (f'<rect x="{x - 13:.1f}" y="{y - 30:.1f}" width="26" height="34" rx="4" fill="{PAPIER}" stroke-width="2"/>'
            f'<rect x="{x - 14:.1f}" y="{y - 36:.1f}" width="28" height="7" fill="{ENCRE}" stroke-width="1"/>'
            f'<path d="M{x - 13:.1f} {y - 18:.1f} H{x + 13:.1f}" stroke="{MINE}" stroke-width="1.2"/>'
            f'<ellipse cx="{x:.1f}" cy="{y - 8:.1f}" rx="6" ry="5" fill="{LAVIS}" stroke="none"/>')


def anselme_ranger_bocal() -> list[str]:
    """Il range un bocal sur l'étagère, haut à droite, et le tourne d'un quart pour l'aligner."""
    def m(main, coude, b=True) -> str:
        jointe = f'<path d="M108 210 Q118 204 126 210 L124 226 Q116 230 110 226 Z" fill="{PAPIER}" stroke-width="1.8"/>'
        gauche = f'<path d="M104 136 Q92 180 108 214 L118 208 Q106 180 114 144 Z" fill="url(#h2)" stroke-width="2.2"/>'
        return gauche + jointe + bras_anselme(A_EPAULE_D, coude, main) + (bocal(main[0], main[1] - 4) if b else "") + main_poing(main[0], main[1], 7)
    return [anselme(0),
            anselme(1, m((150, 200), (162, 172))),
            anselme(2, m((176, 130), (170, 160))),
            anselme(3, m((188, 92), (178, 124))),
            anselme(0, m((188, 92), (178, 124))),
            anselme(1, m((158, 196), (166, 168), False))]


def anselme_montrer() -> list[str]:
    """La main ouverte vers le siège : « Assieds-toi. »"""
    def m(main, coude, ang) -> str:
        droite = f'<path d="M146 136 Q158 180 142 214 L132 208 Q144 180 136 144 Z" fill="url(#h2)" stroke-width="2.2"/>'
        return droite + f'<path d="M126 208 Q136 204 142 210 L138 226 Q130 230 126 226 Z" fill="{PAPIER}" stroke-width="1.8"/>' \
            + bras_anselme(A_EPAULE_G, coude, main) + main_ouverte(main[0], main[1], ang, .9)
    return [anselme(0),
            anselme(1, m((80, 196), (88, 176), -110)),
            anselme(2, m((40, 210), (76, 186), -120)),
            anselme(3, m((38, 214), (76, 188), -124)),
            anselme(0)]


def pot_cendre(x: float, y: float) -> str:
    return (f'<path d="M{x - 14:.1f} {y - 10:.1f} L{x + 14:.1f} {y - 10:.1f} L{x + 10:.1f} {y + 12:.1f} L{x - 10:.1f} {y + 12:.1f} Z" fill="url(#h1)" stroke-width="2"/>'
            f'<ellipse cx="{x:.1f}" cy="{y - 10:.1f}" rx="14" ry="4" fill="url(#pt)" stroke-width="1.6"/>')


def pouce(x: float, y: float, ang: float) -> str:
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.0f})">'
            f'<circle cx="0" cy="0" r="7" fill="{PAPIER}" stroke-width="1.8"/>'
            f'<path d="M-3 -6 Q-4 -15 1 -16 Q5 -15 4 -6" fill="{PAPIER}" stroke-width="1.6"/>'
            f'<path d="M-2 -13 Q1 -16 3 -13" stroke="{LAVIS}" stroke-width="3"/></g>')


def anselme_cendrer() -> list[str]:
    """Le pot de cendre dans la main droite ; le pouce gauche y plonge, puis appuie fort sur le front
    de Tobie (à gauche, à hauteur de son front) : une croix par-dessus celle de Cassien."""
    pot = bras_anselme(A_EPAULE_D, (156, 176), (140, 206)) + pot_cendre(140, 196) + main_poing(140, 210, 7)
    return [anselme(0),
            anselme(1, pot + bras_anselme(A_EPAULE_G, (100, 180), (132, 190)) + main_poing(132, 190, 7)),
            anselme(2, pot + bras_anselme(A_EPAULE_G, (92, 160), (110, 132)) + pouce(110, 132, -20)),
            anselme(3, pot + bras_anselme(A_EPAULE_G, (80, 130), (40, 100)) + pouce(40, 100, -70), 4),
            anselme(0, pot + bras_anselme(A_EPAULE_G, (80, 132), (38, 108)) + pouce(38, 108, -80), 4),
            anselme(1)]


PLANCHES = {
    "chr_maude_repos_01": lambda: [maude(i) for i in range(4)],
    "chr_maude_laver_01": maude_laver,
    "chr_maude_baiser-ruban_01": maude_baiser_ruban,
    "chr_fernand_repos_01": lambda: [fernand(i) for i in range(4)],
    "chr_fernand_se-redresser_01": fernand_se_redresser,
    "chr_fernand_hocher-tete_01": fernand_hocher_tete,
    "chr_fernand_montrer_01": fernand_montrer,
    "chr_anselme_repos_01": lambda: [anselme(i) for i in range(4)],
    "chr_anselme_examiner_01": anselme_examiner,
    "chr_anselme_ranger-bocal_01": anselme_ranger_bocal,
    "chr_anselme_montrer_01": anselme_montrer,
    "chr_anselme_cendrer_01": anselme_cendrer,
}


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    for nom, fn in PLANCHES.items():
        (DST / f"{nom}.svg").write_text(planche(fn()), encoding="utf-8")
    print(f"{len(PLANCHES)} planches de l'étape 4 dans art/src/chr")


if __name__ == "__main__":
    main()
