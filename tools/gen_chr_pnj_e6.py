#!/usr/bin/env python3
"""Génère les personnages de l'étape 6, la Cathédrale enterrée, et leurs gestes.

Même repère et même échelle que les PNJ des étapes 1 à 4 (source 240 x 420, sol à y 405,
centre à x 120, échelle 0,845) : images de 200 x 320, sol à y 316, centre à x 100. Tournés de
trois quarts vers la gauche, vers Tobie qui arrive.

L'étape 6 est inversée à l'écran (encre blanche sur nuit, scripts/rendu/papier_etapes.gd) : le
papier devient la nuit et l'encre devient blanche. Pour qu'un visage reste un visage, la peau
est un gris foncé (PEAU, pâle à l'écran) et les traits du visage, yeux, sourcils, bouche, sont
tracés en papier (sombres à l'écran). Le contour reste à l'encre (blanc), comme tout le reste.
Le vert-de-gris de l'étape (ACCENT, #5F7F72) est gardé exact par l'écran : les vers luisants
du bocal d'Éloi et l'uniforme de Mathurin, « une couleur jamais vue sur un soldat ».

  Éloi (eloi) : le jeune Enfoui, l'âge de Tobie, « pâle comme une racine ». Mince, pieds nus,
      blouse trop grande serrée d'une corde, cheveux en épis ; un visage jeune et chaud, de
      grands yeux, un sourire doux : c'est la première fois que l'ennemi a un visage. Il tient à
      deux mains un bocal de vers luisants. Gestes : lever-bocal (« par ici »), front-terre (à
      genoux, le front contre la terre, comme la nuit chez Ilde), se-retourner (il part devant
      et regarde par-dessus l'épaule), poser-bocal (devant la porte de la Mère-Cloche).
  Mathurin (mathurin) : le veilleur, un très vieil homme assis sur un tabouret, barbe blanche,
      gilet usé, l'uniforme de l'autre camp plié sur les genoux, boutons recousus. Geste :
      caresser-uniforme.

Aucun rouge. Les cloches n'apparaissent pas.

Usage : python3 tools/gen_chr_pnj_e6.py
"""
from __future__ import annotations

import math

from gen_chr_pnj_e2 import DST, ENCRE, LAVIS, MINE, PAPIER, ST, planche
from gen_gestes_e1 import bras, main_ouverte, main_poing

SOUFFLE = (0, 1, 2, 1)
PEAU = "#5E5A52"      # gris foncé : peau pâle une fois l'écran inversé
ACCENT = "#5F7F72"    # vert-de-gris exact de l'étape 6 (papier_etapes.gd)
TRAIT = PAPIER        # traits du visage : sombres une fois l'écran inversé


def g(dessin: str) -> str:
    return f'<g {ST}>{dessin}</g>'


def peau(svg: str) -> str:
    """Les mains des gestes de l'étape 1, en peau."""
    return svg.replace(f'fill="{PAPIER}"', f'fill="{PEAU}"')


def poing(x: float, y: float, r: float = 7) -> str:
    return peau(main_poing(x, y, r))


def ouverte(x: float, y: float, ang: float, s: float = .85) -> str:
    return peau(main_ouverte(x, y, ang, s))


# ----------------------------------------------------------------------------- le bocal
def bocal(x: float, y: float, s: float = 1.0) -> str:
    """Le bocal de vers luisants, (x, y) au milieu du fond : verre à l'encre, lumière en
    vert-de-gris, quelques vers plus vifs ; une ficelle nouée au col."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s})">'
            f'<path d="M-13 0 Q-15 -14 -12 -26 L-8 -30 V-35 H8 V-30 L12 -26 Q15 -14 13 0 Q0 4 -13 0 Z" fill="{ACCENT}" stroke="{ENCRE}" stroke-width="2"/>'
            f'<path d="M-9 -35 H9 V-39 H-9 Z" fill="{LAVIS}" stroke="{ENCRE}" stroke-width="1.4"/>'
            f'<path d="M-8 -39 Q0 -50 8 -39" fill="none" stroke="{ENCRE}" stroke-width="1.4"/>'
            + "".join(f'<path d="M{a} {b} q2 -1.5 4 0" fill="none" stroke="{ENCRE}" stroke-width="1.6"/>'
                      for a, b in ((-8, -8), (2, -14), (-4, -21), (4, -4), (-2, -27)))
            + f'<path d="M-10 -22 Q-11 -12 -9 -4" fill="none" stroke="{PAPIER}" stroke-width="1.6" opacity=".7"/>'
            '</g>')


# ----------------------------------------------------------------------------- Éloi
E_EPAULE_G, E_EPAULE_D = (108.0, 168.0), (140.0, 166.0)
E_TETE = (122.0, 130.0)


def tete_eloi(rot: float = 0.0, sourire: int = 1, cligne: bool = False, dy: float = 0.0) -> str:
    """La tête d'Éloi, de trois quarts vers la gauche ; rot en degrés (positif : penchée vers
    Tobie) autour du cou ; sourire 0 (calme), 1 (doux), 2 (franc)."""
    cx, cy = E_TETE
    out = [f'<g transform="translate(0 {dy:.1f}) rotate({-rot:.1f} 124 152)">',
           f'<path d="M116 146 L130 146 L131 166 L115 166 Z" fill="{PEAU}" {ST} stroke-width="1.8"/>',
           f'<ellipse cx="{cx}" cy="{cy}" rx="17" ry="21" fill="{PEAU}" {ST} stroke-width="2.2"/>',
           # l'oreille, côté droit
           f'<path d="M137 128 Q144 126 143 134 Q142 140 137 139" fill="{PEAU}" {ST} stroke-width="1.6"/>',
           # les cheveux en épis, comme des radicelles douces
           f'<path d="M104 126 Q102 104 122 104 Q144 104 142 128 Q138 118 132 116 L134 108 L126 114 L124 104 '
           f'L118 113 L112 106 L112 116 Q106 118 104 126 Z" fill="url(#h2)" {ST} stroke-width="1.8"/>']
    # les yeux : grands, sombres à l'écran, un reflet ; sourcils doux, levés
    if cligne:
        out.append(f'<path d="M107 128 Q110 131 114 128 M119 128 Q123 131 127 128" fill="none" stroke="{TRAIT}" stroke-width="2"/>')
    else:
        out.append(f'<ellipse cx="110.5" cy="128" rx="3" ry="3.8" fill="{TRAIT}"/><ellipse cx="123" cy="128" rx="3.2" ry="4" fill="{TRAIT}"/>'
                   f'<circle cx="109.6" cy="126.6" r="1.1" fill="{ENCRE}"/><circle cx="122" cy="126.6" r="1.2" fill="{ENCRE}"/>')
    out.append(f'<path d="M106 120 Q110 117 114 119 M119 119 Q123 116 128 119" fill="none" stroke="{TRAIT}" stroke-width="1.5"/>'
               f'<path d="M115 130 L112 138 L116 139" fill="none" stroke="{TRAIT}" stroke-width="1.3"/>')
    bouche = {0: "M111 144 Q116 145 121 144",
              1: "M110 143 Q116 147 122 143",
              2: "M109 142 Q116 150 123 142"}[sourire]
    out.append(f'<path d="{bouche}" fill="none" stroke="{TRAIT}" stroke-width="1.6"/>')
    if sourire:
        out.append(f'<path d="M106 139 Q107 142 109 142 M125 141 Q127 141 128 138" fill="none" stroke="{TRAIT}" stroke-width="1.1"/>')
    out.append('</g>')
    return "".join(out)


def corps_eloi(i: int, bras_svg: str | None, penche: float = 0.0) -> str:
    """Le corps debout : pieds nus, pantalon roulé, blouse trop grande serrée d'une corde.
    bras_svg remplace les deux bras qui tiennent le bocal ; penche incline le buste (degrés)."""
    s = SOUFFLE[i]
    out = [  # pieds nus et chevilles
        f'<path d="M100 384 L96 398 Q92 405 104 405 L118 405 L116 384 Z M130 384 L128 405 L148 405 Q152 400 144 396 L142 384 Z" fill="{PEAU}" {ST} stroke-width="1.8"/>',
        f'<path d="M98 404 V401 M102 405 V401 M136 405 V401 M140 405 V401" stroke="{ENCRE}" stroke-width=".9"/>',
        # le pantalon roulé aux mollets
        f'<path d="M104 296 L98 386 L118 388 L124 320 L128 388 L146 386 L142 296 Z" fill="url(#h1)" {ST} stroke-width="2.2"/>',
        f'<path d="M98 378 L118 380 M128 380 L146 378" {ST} stroke-width="2"/>',
        f'<g transform="translate(0 {s * .6:.1f}) rotate({-penche:.1f} 124 300)">',
        # la blouse, trop grande : épaules tombantes, pans qui flottent, une corde à la taille
        f'<path d="M108 160 Q124 152 142 160 Q152 210 154 252 Q158 290 150 312 L98 312 Q92 290 96 252 Q98 210 108 160 Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>',
        f'<path d="M118 160 Q124 172 132 160" fill="none" {ST} stroke-width="1.6"/>',
        f'<path d="M110 196 Q112 250 106 306 M140 196 Q142 250 146 306 M124 180 V230" fill="none" stroke="{MINE}" stroke-width="1.3"/>',
        f'<path d="M96 256 Q124 264 154 256" fill="none" {ST} stroke-width="2.4"/>',
        f'<path d="M104 258 Q100 272 104 284 M104 258 Q110 270 108 280" fill="none" {ST} stroke-width="1.6"/>',
    ]
    if bras_svg is None:
        out.append(bras_bocal(118, 250))
    else:
        out.append(g(bras_svg))
    return "".join(out)


def manche(epaule, coude, main) -> str:
    return bras(epaule, coude, main, PAPIER, 15, 13, 11, 2.2)


def bras_bocal(x: float, y: float) -> str:
    """Les deux mains autour du bocal, tenu devant le ventre en (x, y)."""
    return g(manche(E_EPAULE_D, (146, 214), (x + 14, y - 10)) + manche(E_EPAULE_G, (100, 212), (x - 14, y - 12))
             + bocal(x, y)
             + f'<ellipse cx="{x - 14:.1f}" cy="{y - 12:.1f}" rx="6" ry="7" fill="{PEAU}" stroke-width="1.8"/>'
             + f'<ellipse cx="{x + 14:.1f}" cy="{y - 10:.1f}" rx="6" ry="7" fill="{PEAU}" stroke-width="1.8"/>')


def eloi(i: int = 0, bras_svg: str | None = None, tete: float = 0.0, sourire: int = 1,
         penche: float = 0.0, cligne: bool = False) -> str:
    return (corps_eloi(i, bras_svg, penche)
            + tete_eloi(tete, sourire, cligne) + '</g>')


def bras_pendant() -> str:
    return manche(E_EPAULE_D, (148, 214), (146, 262)) + poing(146, 264, 6.5)


def eloi_lever_bocal() -> list[str]:
    """Il lève le bocal vers Tobie et un peu au-dessus de lui, pour éclairer le chemin : par ici."""
    def m(main, coude) -> str:
        return (bras_pendant() + manche(E_EPAULE_G, coude, main)
                + bocal(main[0], main[1] + 6) + f'<ellipse cx="{main[0]:.1f}" cy="{main[1] - 12:.1f}" rx="6" ry="7" fill="{PEAU}" stroke-width="1.8"/>')
    return [eloi(0),
            eloi(1, m((102, 224), (98, 204))),
            eloi(2, m((84, 178), (88, 208)), 3),
            eloi(3, m((64, 136), (80, 172)), 6, 2),
            eloi(0, m((64, 138), (80, 173)), 6, 2),
            eloi(1, m((98, 222), (96, 202)))]


# --- à genoux
def eloi_a_genoux(i: int, incline: float, sourire: int = 1, bocal_pose: bool = True) -> str:
    """À genoux, les tibias à plat derrière lui ; incline : le buste se penche vers la gauche
    (0 droit, 78 le front contre la terre), autour de la hanche ; les mains à plat devant."""
    s = SOUFFLE[i]
    t = incline / 88
    hx, hy = 128.0 + 16 * t, 336.0 + 34 * t   # la hanche : elle recule et descend sur les talons
    out = []
    if bocal_pose:
        out.append(bocal(176, 404, .95))
    out += [  # tibias et pieds nus, derrière ; genoux posés
        f'<path d="M106 384 L166 392 Q174 394 172 404 L104 405 Q96 398 106 384 Z" fill="url(#h1)" {ST} stroke-width="2.2"/>',
        f'<path d="M164 392 L186 396 Q192 404 182 405 L166 405 Z" fill="{PEAU}" {ST} stroke-width="1.6"/>',
        # cuisses, de la hanche aux genoux
        f'<path d="M{hx - 18:.1f} {hy - 8:.1f} L100 386 L122 396 L{hx + 16:.1f} {hy + 4:.1f} Z" fill="url(#h1)" {ST} stroke-width="2.2"/>',
    ]
    # les bras : descendent vers le sol à mesure qu'il s'incline
    mg = (96 - 44 * t, 330 + 72 * t)
    md = (110 - 40 * t, 334 + 68 * t)
    dxh, dyh = hx - 128, hy - 336
    out.append(f'<g transform="translate({dxh:.1f} {dyh + s * .4:.1f}) rotate({-incline:.1f} 128 336)">')
    # le buste à genoux : la blouse (192 px de moins que debout)
    out.append(f'<path d="M110 240 Q126 232 144 240 Q152 280 152 312 Q154 334 148 344 L104 344 Q98 330 100 312 Q100 280 110 240 Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
    out.append(f'<path d="M120 240 Q126 252 134 240" fill="none" {ST} stroke-width="1.6"/>'
               f'<path d="M100 318 Q126 326 152 318" fill="none" {ST} stroke-width="2.4"/>'
               f'<path d="M114 270 Q116 300 110 340 M140 270 Q142 300 146 340" fill="none" stroke="{MINE}" stroke-width="1.3"/>')
    out.append('</g>')
    # les mains à plat (repère du monde), puis les bras qui les rejoignent depuis les épaules
    # tournées avec le buste
    a = math.radians(-incline)
    def tourne(p):
        x, y = p[0] - 128, p[1] - 336
        return (hx + x * math.cos(a) - y * math.sin(a), hy + x * math.sin(a) + y * math.cos(a) + s * .4)
    eg, ed = tourne((110, 248)), tourne((142, 246))
    for ep, mn in ((ed, md), (eg, mg)):
        cx_, cy_ = (ep[0] + mn[0]) / 2 - 8, (ep[1] + mn[1]) / 2 + 6
        out.append(g(manche(ep, (cx_, cy_), mn)))
        out.append(f'<ellipse cx="{mn[0]:.1f}" cy="{mn[1]:.1f}" rx="8" ry="5" fill="{PEAU}" {ST} stroke-width="1.8"/>')
    # la tête suit le buste (le cou en (124, 232) dans le buste à genoux, 82 px plus bas que debout)
    out.append(f'<g transform="translate({dxh:.1f} {dyh + s * .4:.1f}) rotate({-incline:.1f} 128 336)">')
    out.append(tete_eloi(0, sourire, cligne=incline > 50, dy=82))
    out.append('</g>')
    return "".join(out)


def eloi_prosterne(i: int) -> str:
    """La prosternation : toujours à genoux, assis sur les talons, le dos rond, le front posé
    contre la terre et les mains à plat de chaque côté de la tête. Pas une chute."""
    s = SOUFFLE[i] * .3
    return (bocal(176, 404, .95)
            # la main de derrière, à plat au-delà de la tête
            + g(manche((100, 360 + s), (70, 386), (46, 400)) + f'<ellipse cx="44" cy="401" rx="9" ry="4.5" fill="{PEAU}"/>')
            # tibias et pieds sous lui, cuisses repliées : assis sur les talons
            + f'<path d="M106 384 L166 392 Q174 394 172 404 L104 405 Q96 398 106 384 Z" fill="url(#h1)" {ST} stroke-width="2.2"/>'
            + f'<path d="M164 392 L186 396 Q192 404 182 405 L166 405 Z" fill="{PEAU}" {ST} stroke-width="1.6"/>'
            + f'<path d="M160 360 Q166 384 152 394 L104 398 Q98 386 110 378 Z" fill="url(#h1)" {ST} stroke-width="2.2"/>'
            # le dos rond de la blouse, de la hanche aux épaules penchées vers le sol
            + f'<path d="M164 376 Q166 330 132 {322 + s:.1f} Q102 {322 + s:.1f} 86 {362 + s:.1f} L94 {378 + s:.1f} Q120 {372 + s:.1f} 150 394 Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>'
            + f'<path d="M156 360 Q150 334 124 {330 + s:.1f} M140 384 Q130 360 110 {356 + s:.1f}" fill="none" stroke="{MINE}" stroke-width="1.3"/>'
            + f'<path d="M150 344 Q158 366 160 384" fill="none" {ST} stroke-width="2.4"/>'
            # la tête, le front contre la terre, le visage vers le sol, les yeux fermés
            + f'<g transform="translate(-52 {256 + s:.1f}) rotate(-100 122 130)">{tete_eloi(0, 0, True)}</g>'
            # la main de devant, à plat de ce côté-ci de la tête
            + g(manche((96, 366 + s), (98, 388), (86, 400)) + f'<ellipse cx="84" cy="401" rx="9" ry="4.5" fill="{PEAU}"/>'))


def eloi_front_terre() -> list[str]:
    """Il pose le bocal, s'agenouille, met le front contre la terre, se redresse et sourit."""
    return [eloi(0),
            eloi_a_genoux(1, 0, 1),
            eloi_a_genoux(2, 44, 0),
            eloi_prosterne(0),
            eloi_a_genoux(1, 0, 2),
            eloi(0, sourire=2)]


# --- se retourner
def tete_dos(regarde: bool, sourire: int = 1) -> str:
    """La tête vue de dos : la nuque et les épis ; quand il regarde par-dessus l'épaule, le
    profil perdu apparaît à gauche, vers Tobie : un œil, le nez, le sourire."""
    cx, cy = E_TETE
    out = [f'<path d="M116 146 L130 146 L131 166 L115 166 Z" fill="{PEAU}" {ST} stroke-width="1.8"/>',
           f'<ellipse cx="{cx}" cy="{cy}" rx="17" ry="21" fill="{PEAU}" {ST} stroke-width="2.2"/>']
    if regarde:
        out.append(f'<path d="M106 124 Q102 128 103 133 L100 136 L104 138 Q104 146 110 148" fill="{PEAU}" {ST} stroke-width="1.8"/>'
                   f'<ellipse cx="109" cy="127" rx="2.6" ry="3.8" fill="{TRAIT}"/><circle cx="108.4" cy="125.8" r=".9" fill="{ENCRE}"/>'
                   f'<path d="M105 120 Q108 118 112 120" fill="none" stroke="{TRAIT}" stroke-width="1.4"/>'
                   + (f'<path d="M104 143 Q107 146 111 143" fill="none" stroke="{TRAIT}" stroke-width="1.5"/>' if sourire else '')
                   + (f'<path d="M111 143 Q113 141 112 139" fill="none" stroke="{TRAIT}" stroke-width="1.1"/>' if sourire > 1 else '')
                   + f'<path d="M108 128 Q104 104 124 104 Q144 104 141 132 Q140 150 128 151 Q118 150 116 140 L120 134 '
                   f'Q114 132 112 126 Z" fill="url(#h2)" {ST} stroke-width="1.8"/>')
    else:
        out.append(f'<path d="M104 132 Q100 104 122 104 Q144 104 140 132 Q138 150 122 151 Q106 150 104 132 Z" fill="url(#h2)" {ST} stroke-width="1.8"/>'
                   f'<path d="M104 128 Q100 126 101 134 Q102 139 106 138" fill="{PEAU}" {ST} stroke-width="1.6"/>')
    return "".join(out)


def eloi_dos(i: int, large: float, regarde: bool, sourire: int = 1) -> str:
    """De dos, parti devant vers la droite (le corps en miroir ; large de 0,6, encore de biais, à
    1) ; le bocal est devant lui, caché, ses bras le tiennent."""
    bras_dos = (manche(E_EPAULE_G, (104, 212), (112, 244)) + manche(E_EPAULE_D, (146, 212), (138, 246)))
    corps = corps_eloi(i, bras_dos)
    lueur = bocal(120 + 30 * large, 252, .9)      # le bocal devant lui : sa lumière dépasse
    return (lueur + f'<g transform="translate({120 * (1 + large):.1f} 0) scale({-large:.2f} 1)">{corps}</g></g>'
            f'<g transform="translate(0 {SOUFFLE[i] * .6:.1f})">{tete_dos(regarde, sourire)}</g>')


def eloi_se_retourner() -> list[str]:
    """Il part devant, puis se retourne à demi : il regarde Tobie par-dessus l'épaule et sourit."""
    return [eloi(0),
            eloi_dos(1, .7, False),
            eloi_dos(2, 1, True),
            eloi_dos(3, 1, True, 2),
            eloi_dos(0, .7, False),
            eloi(1)]


# --- poser le bocal
def eloi_poser_bocal() -> list[str]:
    """Devant la porte, il se penche, pose le bocal sur le sol devant Tobie, et se redresse les
    mains vides : il n'ira pas plus loin."""
    def tenu(x, y) -> str:
        return bras_bocal(x, y)

    def lache(x) -> str:
        # les mains ouvertes juste au-dessus du bocal posé (repère du monde), ramenées dans le
        # repère du buste penché de 30 degrés autour de (124, 300)
        a = math.radians(30)
        def local(p):
            dx, dy = p[0] - 124, p[1] - 300
            return (124 + dx * math.cos(a) - dy * math.sin(a), 300 + dx * math.sin(a) + dy * math.cos(a))
        mg, md = local((x - 12, 372)), local((x + 12, 374))
        return (manche(E_EPAULE_D, local((128, 330)), md) + manche(E_EPAULE_G, local((100, 320)), mg)
                + ouverte(mg[0], mg[1], 150) + ouverte(md[0], md[1], -150))
    vides = (manche(E_EPAULE_D, (146, 214), (130, 256)) + manche(E_EPAULE_G, (102, 214), (114, 258))
             + f'<ellipse cx="122" cy="258" rx="10" ry="8" fill="{PEAU}" stroke-width="1.8"/>')
    return [eloi(0),
            eloi(1, tenu(112, 290), 4, 1, 12),
            eloi(2, tenu(104, 330), 8, 0, 26),
            bocal(80, 404) + eloi(3, lache(80), 10, 1, 30),
            bocal(80, 404) + eloi(0, vides, 4, 1),
            bocal(80, 404) + eloi(1, vides, 2, 2)]


# ----------------------------------------------------------------------------- Mathurin
def mathurin(i: int = 0, main_d=(116.0, 300.0), tete: float = 0.0, yeux_clos: bool = False) -> str:
    """Assis sur un tabouret, voûté ; l'uniforme vert-de-gris plié sur les genoux ; main_d : la
    main droite posée sur l'uniforme ; tete : la tête se penche vers l'uniforme (degrés)."""
    s = SOUFFLE[i]
    out = [  # le tabouret de bois
        f'<path d="M108 318 H176 V328 H108 Z" fill="url(#h1)" {ST} stroke-width="2.2"/>',
        f'<path d="M114 328 L106 405 M170 328 L178 405 M142 328 V398 M110 372 H174" fill="none" {ST} stroke-width="3"/>',
        # les jambes : pantalon sombre, chaussons
        f'<path d="M150 316 L86 306 L82 326 L132 336 Z" fill="url(#h2)" {ST} stroke-width="2.2"/>',
        f'<path d="M86 310 L80 394 L100 396 L104 324 Z" fill="url(#h2)" {ST} stroke-width="2.2"/>',
        f'<path d="M74 392 L70 405 L104 405 L100 392 Z" fill="{LAVIS}" {ST} stroke-width="1.6"/>',
        f'<path d="M148 316 L104 318 L100 334 L140 336 Z" fill="url(#h2)" {ST} stroke-width="2.2"/>',
        f'<path d="M102 322 L104 396 L122 396 L118 330 Z" fill="url(#h2)" {ST} stroke-width="2.2"/>',
        f'<path d="M98 392 L96 405 L128 405 L122 392 Z" fill="{LAVIS}" {ST} stroke-width="1.6"/>',
        f'<g transform="translate(0 {s * .5:.1f})">',
        # le buste voûté : chemise et gilet usé, reprisé
        f'<path d="M120 206 Q146 196 164 214 Q174 260 160 318 L104 318 Q100 270 120 206 Z" fill="url(#h1)" {ST} stroke-width="2.4"/>',
        f'<path d="M124 210 Q134 232 130 318" fill="none" {ST} stroke-width="1.6"/>',
        f'<path d="M140 248 l8 0 l0 8 l-8 0 Z" fill="{PAPIER}" {ST} stroke-width="1"/>',
        f'<path d="M140 248 l8 8 M148 248 l-8 8" stroke="{ENCRE}" stroke-width=".8"/>',
        # le bras gauche, l'avant-bras posé sur la cuisse
        f'<path d="M162 220 Q170 262 150 290 L138 282 Q154 258 146 226 Z" fill="url(#h1)" {ST} stroke-width="2.2"/>',
        # l'uniforme plié sur les genoux : une pile nette, col et rangée de boutons recousus
        f'<path d="M78 290 L140 290 L144 312 L80 314 Z" fill="{ACCENT}" {ST} stroke-width="2.2"/>',
        f'<path d="M80 302 L142 301" stroke="{ENCRE}" stroke-width="1.3"/>',
        f'<path d="M82 290 L92 280 L112 280 L118 290" fill="{ACCENT}" {ST} stroke-width="2"/>',
        ''.join(f'<circle cx="{x}" cy="296" r="2.4" fill="{PAPIER}" {ST} stroke-width="1"/>'
                f'<path d="M{x - 2} 293 l4 6" stroke="{ENCRE}" stroke-width=".7"/>' for x in (96, 108, 120, 132)),
        f'<ellipse cx="140" cy="292" rx="9" ry="7" fill="{PEAU}" {ST} stroke-width="1.8"/>',
    ]
    # le bras droit et la main qui caresse l'uniforme
    out.append(g(bras((128, 214), (110, 258), main_d, "url(#h1)", 16, 14, 12, 2.2)
                 + f'<path d="M{main_d[0] - 11:.1f} {main_d[1] - 2:.1f} Q{main_d[0]:.1f} {main_d[1] - 10:.1f} {main_d[0] + 12:.1f} {main_d[1] - 2:.1f} '
                   f'Q{main_d[0] + 8:.1f} {main_d[1] + 5:.1f} {main_d[0] - 9:.1f} {main_d[1] + 4:.1f} Z" fill="{PEAU}" stroke-width="1.8"/>'
                 + f'<path d="M{main_d[0] - 6:.1f} {main_d[1]:.1f} l10 -1 M{main_d[0] - 6:.1f} {main_d[1] + 3:.1f} l10 -1" stroke-width=".8"/>'))
    # la tête : chauve, ridée, grande barbe blanche (lavis : claire à l'écran), regard baissé
    out.append(f'<g transform="rotate({-tete:.1f} 128 204)">')
    out.append(f'<path d="M120 190 L136 190 L136 208 L120 208 Z" fill="{PEAU}" {ST} stroke-width="1.8"/>')
    out.append(f'<ellipse cx="124" cy="168" rx="19" ry="23" fill="{PEAU}" {ST} stroke-width="2.2"/>')
    out.append(f'<path d="M141 164 Q148 162 147 171 Q146 177 141 176" fill="{PEAU}" {ST} stroke-width="1.6"/>')
    out.append(f'<path d="M106 172 Q104 196 116 206 Q126 214 136 204 Q144 194 142 176 Q132 184 124 182 Q114 182 106 172 Z" fill="{LAVIS}" {ST} stroke-width="1.8"/>')
    out.append(f'<path d="M112 186 Q114 196 118 202 M122 186 Q122 198 126 206 M132 186 Q132 196 134 200" fill="none" stroke="{MINE}" stroke-width="1.1"/>')
    out.append(f'<path d="M108 176 Q116 172 124 178 Q130 174 138 176" fill="none" stroke="{MINE}" stroke-width="2"/>')
    if yeux_clos:
        out.append(f'<path d="M108 162 Q112 165 116 162 M122 162 Q126 165 130 162" fill="none" stroke="{TRAIT}" stroke-width="1.8"/>')
    else:
        out.append(f'<path d="M108 161 Q112 159 116 161 M122 161 Q126 159 130 161" fill="none" stroke="{TRAIT}" stroke-width="1.4"/>'
                   f'<ellipse cx="112" cy="163.5" rx="2.4" ry="2" fill="{TRAIT}"/><ellipse cx="126" cy="163.5" rx="2.4" ry="2" fill="{TRAIT}"/>')
    out.append(f'<path d="M106 154 Q112 151 118 154 M121 154 Q127 151 133 154 M110 147 Q122 143 134 147" fill="none" stroke="{TRAIT}" stroke-width="1.2"/>'
               f'<path d="M119 164 L116 172 L120 173" fill="none" stroke="{TRAIT}" stroke-width="1.3"/>'
               f'<path d="M104 166 Q103 172 106 176 M141 158 Q144 150 140 146" fill="none" stroke="{TRAIT}" stroke-width="1"/>')
    out.append('</g></g>')
    return "".join(out)


def mathurin_caresser_uniforme() -> list[str]:
    """La main glisse sur l'uniforme plié, d'un bord à l'autre, et revient ; la tête se baisse,
    les yeux se ferment un instant."""
    return [mathurin(0),
            mathurin(1, (104, 296), 3),
            mathurin(2, (94, 294), 7, True),
            mathurin(3, (112, 294), 9, True),
            mathurin(0, (126, 296), 8, True),
            mathurin(1, (116, 300), 3)]


PLANCHES = {
    "chr_eloi_repos_01": lambda: [eloi(i) for i in range(4)],
    "chr_eloi_lever-bocal_01": eloi_lever_bocal,
    "chr_eloi_front-terre_01": eloi_front_terre,
    "chr_eloi_se-retourner_01": eloi_se_retourner,
    "chr_eloi_poser-bocal_01": eloi_poser_bocal,
    "chr_mathurin_repos_01": lambda: [mathurin(i) for i in range(4)],
    "chr_mathurin_caresser-uniforme_01": mathurin_caresser_uniforme,
}


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    for nom, fn in PLANCHES.items():
        (DST / f"{nom}.svg").write_text(planche(fn()), encoding="utf-8")
    print(f"{len(PLANCHES)} planches de l'étape 6 dans art/src/chr")


if __name__ == "__main__":
    main()
