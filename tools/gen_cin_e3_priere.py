#!/usr/bin/env python3
"""Génère la cinématique e3_priere_champs (lot 1, planche validée par le GD le 17/11, avec ses
retouches) : la nuit, dans le champ labouré, le village à genoux en cercle, front contre terre,
les cierges plantés ; une place vide. La ciné demandée par l'utilisateur : on doit lire des GENS
(dos ronds, fichus et bonnets posés au sol, mains à plat, plis), pas des formes.

  cin_e3-priere-champ      2160 x 1080 : le champ de nuit vu de côté, au ras des sillons (P1).
  cin_e3-priere-profil     les prosternés de profil, tournés vers la droite : 4 silhouettes
                           (femme au fichu, homme au bonnet, enfant, vieux tassé) x 2 images
                           (le dos se soulève : ils respirent). Grille 2 x 4 de 300 x 220, le sol
                           à y 210 ; image = silhouette x 2 + souffle.
  cin_e3-priere-sillons    2400 x 1400 : le champ vu d'en haut (P2, P3), posé en (-240, -160).
  cin_e3-priere-dessus     les mêmes vus d'en haut, la tête vers le haut (vers le centre du
                           cercle) : 4 silhouettes, 300 x 390 ; le moteur les tourne autour du
                           cercle, qui déborde du cadre (rien ne se compte).
  cin_e3-priere-cierge     un cierge planté, de côté : 3 images de 60 x 120 (droit, qui vacille,
                           penché par le vent), le pied en (30, 116).
  cin_e3-priere-lueur      le même vu d'en haut : 3 images de 90 x 90, centre (45, 45) ; la 4e
                           image est le cierge éteint de la place vide.
Peint de nuit, comme e3_procession_nuit : la lumière ne vient que des cierges (réserve de papier).
Aucun rouge.

Usage : python3 tools/gen_cin_e3_priere.py
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from gen_cin_epilogues import DEFS_CIN
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER

DST = Path(__file__).resolve().parent.parent / "art" / "src" / "cin"
W, H = 1920, 1080
ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
CLAIR = "#D3CFC2"
NUIT = "#2E2B25"          # le ciel et la terre de nuit : entre l'encre et le lavis
HORIZON = 430
JUPE = "#6E695D"   # la jupe, la culotte : un ton sous l'étoffe du dos, au-dessus de la terre


def svg(contenu: str, w: int = W, h: int = H) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{DEFS_CIN}{contenu}</svg>\n')


def grille(images: list[str], w: int, h: int, colonnes: int) -> str:
    lignes = math.ceil(len(images) / colonnes)
    corps = "".join(f'<g transform="translate({(i % colonnes) * w} {(i // colonnes) * h})">{c}</g>' for i, c in enumerate(images))
    return svg(corps, w * colonnes, h * lignes)


# --- P1 : de profil ------------------------------------------------------------------------------
CHAMP_W = W + 240                # le glissement de P1 ne montre aucun bord


def champ() -> str:
    r = random.Random(1701)
    W = CHAMP_W
    o = [f'<rect width="{W}" height="{H}" fill="{NUIT}"/>',
         f'<path d="M0 {HORIZON} Q480 {HORIZON - 16} 960 {HORIZON - 6} T{W} {HORIZON - 10} V{H} H0 Z" fill="{LAVIS}" {ST} stroke-width="3"/>']
    # quelques traits de ciel, une lisière d'arbres noire au loin
    for _ in range(8):
        y = r.randint(60, 300)
        o.append(f'<path d="M{r.randint(0, W)} {y} h{r.randint(120, 380)}" stroke="{LAVIS}" stroke-width="1.6"/>')
    lisiere = " ".join(f"L{x} {HORIZON - 30 - r.randint(0, 40)}" for x in range(0, W + 60, 60))
    o.append(f'<path d="M0 {HORIZON} {lisiere} L{W} {HORIZON} Z" fill="{ENCRE}"/>')
    # les sillons : des lignes qui s'écartent vers le bas (perspective), nettes
    y, pas = HORIZON + 14, 10
    while y < H:
        o.append(f'<path d="M0 {y:.0f} Q960 {y - 8:.0f} {W} {y + 4:.0f}" fill="none" stroke="{ENCRE}" stroke-width="{1.4 + (y - HORIZON) / 300:.1f}" opacity=".7"/>')
        y += pas
        pas *= 1.18
    return "".join(o)


def profil(variante: int, souffle: int) -> str:
    """Un prosterné de profil, tourné vers la droite : à genoux, assis sur les talons, le dos rond,
    le front contre la terre, les avant-bras et les mains à plat devant la tête. variante 0 femme
    au fichu, 1 homme au bonnet, 2 enfant (plus petit), 3 vieux plus tassé. souffle 1 : le dos se
    soulève un peu."""
    s = (1.0, 1.0, .72, .96)[variante]
    tasse = (0, 0, 0, 14)[variante]        # le vieux : les reins plus bas, le dos plus rond
    lev = -4 * souffle
    g = []
    # les pieds, à plat derrière lui, les semelles vers le ciel
    g.append(f'<path d="M34 208 L44 186 Q52 182 60 188 L70 208 Z" fill="{NUIT}" {ST} stroke-width="2.6"/>')
    # la cuisse repliée sous lui : du genou (au sol, à droite) aux fesses posées sur les talons
    rein = (92, 118 + tasse + lev)
    if variante in (0, 2):   # la jupe, ou la blouse longue, qui recouvre les jambes en cloche
        g.append(f'<path d="M46 208 Q40 150 {rein[0]} {rein[1]} L150 150 Q178 180 172 208 Z" fill="{JUPE}" {ST} stroke-width="3"/>'
                 f'<path d="M80 150 Q74 180 76 206 M118 156 Q122 186 124 206" fill="none" stroke="{ENCRE}" stroke-width="1.6"/>')
    else:                    # la culotte : la cuisse, le genou au sol, le mollet sous la cuisse
        g.append(f'<path d="M58 206 Q52 150 {rein[0]} {rein[1]} Q140 140 168 196 Q170 208 156 208 Z" fill="{JUPE}" {ST} stroke-width="3"/>'
                 f'<path d="M64 196 Q110 186 160 202" fill="none" stroke="{ENCRE}" stroke-width="1.8"/>')
    # le buste qui descend des reins jusqu'à la tête posée au sol : le dos rond, l'épaule
    ep = (196, 160 + lev / 2 + tasse / 3)
    g.append(f'<path d="M{rein[0] - 14} {rein[1] + 24} Q{rein[0] - 8} {rein[1] - 8} {rein[0] + 26} {rein[1] - 10} '
             f'Q{ep[0] - 30} {rein[1] - 4 + tasse / 2} {ep[0] + 20} {ep[1] + 4} L{ep[0] + 22} {ep[1] + 30} '
             f'Q{ep[0] - 30} {ep[1] + 34} {rein[0] + 40} {rein[1] + 40} Z" fill="{MINE}" {ST} stroke-width="3.4"/>')
    # la lumière des cierges, devant lui : un liseré sur le haut du dos et l'épaule
    g.append(f'<path d="M{rein[0] + 30} {rein[1] - 8} Q{ep[0] - 30} {rein[1] - 2 + tasse / 2} {ep[0] + 16} {ep[1] + 4}" fill="none" stroke="{PAPIER}" stroke-width="3"/>')
    # les plis de l'étoffe tirée sur le dos, vers l'aisselle
    for k in range(3):
        x = rein[0] + 34 + k * 26
        g.append(f'<path d="M{x} {rein[1] - 4 + k * 6} Q{x + 10} {rein[1] + 22 + k * 6} {x + 22} {rein[1] + 34 + k * 4}" fill="none" stroke="{ENCRE}" stroke-width="1.6"/>')
    if variante == 1:   # la ceinture de l'homme, à la taille
        g.append(f'<path d="M{rein[0] + 18} {rein[1] - 8} Q{rein[0] + 26} {rein[1] + 20} {rein[0] + 34} {rein[1] + 44}" fill="none" stroke="{ENCRE}" stroke-width="6"/>')
    # le bras : de l'épaule au coude posé par terre, l'avant-bras et la main à plat devant la tête
    g.append(f'<path d="M{ep[0] - 6} {ep[1] + 6} Q{ep[0] + 4} {ep[1] + 40} {ep[0] + 18} 206 L{ep[0] + 30} 206 Q{ep[0] + 24} {ep[1] + 30} {ep[0] + 16} {ep[1] + 4} Z" fill="{MINE}" {ST} stroke-width="3"/>'
             f'<path d="M{ep[0] + 18} 196 L270 198 L270 209 L{ep[0] + 18} 209 Z" fill="{MINE}" {ST} stroke-width="3"/>')
    g.append(f'<path d="M266 198 Q284 194 296 204 L296 209 L266 209 Z" fill="{CLAIR}" {ST} stroke-width="2.4"/>'
             f'<path d="M276 200 v9 M284 199 v10 M291 202 v7" stroke="{ENCRE}" stroke-width="1.2"/>')
    # la tête posée, le front sur la terre, couverte (devant l'épaule, sous le bras)
    hx, hy = 238, 186 + lev / 3
    if variante == 0:   # le fichu noué, la pointe qui pend sur la nuque
        g.append(f'<path d="M{hx - 24} {hy - 6} Q{hx - 10} {hy - 30} {hx + 16} {hy - 22} Q{hx + 32} {hy - 6} {hx + 26} {hy + 20} L{hx - 18} {hy + 20} Z" fill="{CLAIR}" {ST} stroke-width="3"/>'
                 f'<path d="M{hx - 22} {hy - 4} L{hx - 40} {hy + 10} L{hx - 26} {hy + 12} Z" fill="{CLAIR}" {ST} stroke-width="2.4"/>'
                 f'<path d="M{hx - 6} {hy - 20} Q{hx + 4} {hy} {hx - 2} {hy + 18}" fill="none" stroke="{ENCRE}" stroke-width="1.4"/>')
    elif variante == 1:  # le bonnet de laine, le bord roulé
        g.append(f'<path d="M{hx - 22} {hy + 4} Q{hx - 18} {hy - 30} {hx + 10} {hy - 26} Q{hx + 30} {hy - 14} {hx + 26} {hy + 20} L{hx - 18} {hy + 20} Z" fill="{LAVIS}" {ST} stroke-width="3"/>'
                 f'<path d="M{hx + 8} {hy - 22} L{hx + 22} {hy + 18}" stroke="{ENCRE}" stroke-width="7"/>'
                 f'<path d="M{hx - 10} {hy - 22} L{hx + 2} {hy + 18}" stroke="{MINE}" stroke-width="1.4"/>')
    elif variante == 2:  # l'enfant : les cheveux en épis, l'oreille
        g.append(f'<path d="M{hx - 20} {hy + 2} Q{hx - 16} {hy - 26} {hx + 10} {hy - 22} Q{hx + 28} {hy - 10} {hx + 24} {hy + 20} L{hx - 16} {hy + 20} Z" fill="{PAPIER}" {ST} stroke-width="3"/>'
                 f'<path d="M{hx - 14} {hy - 10} l-8 -8 M{hx - 4} {hy - 18} l-4 -10 M{hx + 8} {hy - 20} l2 -10" stroke="{ENCRE}" stroke-width="3"/>'
                 f'<path d="M{hx - 4} {hy - 4} Q{hx + 4} {hy - 8} {hx + 6} {hy + 2} Q{hx + 2} {hy + 8} {hx - 4} {hy + 4}" fill="none" stroke="{ENCRE}" stroke-width="2"/>')
    else:                # le vieux : la casquette, la nuque rase, maigre
        g.append(f'<path d="M{hx - 18} {hy + 4} Q{hx - 16} {hy - 22} {hx + 8} {hy - 20} Q{hx + 26} {hy - 10} {hx + 22} {hy + 20} L{hx - 14} {hy + 20} Z" fill="{PAPIER}" {ST} stroke-width="3"/>'
                 f'<path d="M{hx - 2} {hy - 24} Q{hx + 22} {hy - 20} {hx + 30} {hy + 14} L{hx + 40} {hy + 18} L{hx + 34} {hy - 4} Q{hx + 20} {hy - 30} {hx - 4} {hy - 30} Z" fill="{LAVIS}" {ST} stroke-width="2.6"/>'
                 f'<path d="M{hx - 16} {hy - 2} q4 6 2 12" stroke="{MINE}" stroke-width="1.4" fill="none"/>')
    # la mise à l'échelle autour du point au sol (150, 210)
    return f'<g transform="translate(150 210) scale({s}) translate(-150 -210)">{"".join(g)}</g>'


# --- P2, P3 : vus d'en haut ------------------------------------------------------------------------
SILLONS = (W + 480, H + 320)      # plus grand que l'écran : la poussée de P3 ne montre aucun bord


def sillons() -> str:
    r = random.Random(1702)
    W, H = SILLONS
    o = [f'<rect width="{W}" height="{H}" fill="{LAVIS}"/>']
    for y in range(-20, H + 40, 36):
        o.append(f'<path d="M0 {y + r.randint(-3, 3)} Q960 {y + 14} {W} {y + r.randint(-3, 3)}" fill="none" stroke="{ENCRE}" stroke-width="3"/>'
                 f'<path d="M0 {y + 10} Q960 {y + 24} {W} {y + 10}" fill="none" stroke="{NUIT}" stroke-width="2"/>')
    for _ in range(140):
        x, y = r.uniform(0, W), r.uniform(0, H)
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(2, 5):.1f}" fill="{NUIT}"/>')
    return "".join(o)


def dessus(variante: int) -> str:
    """Un prosterné vu d'en haut, la tête vers le haut : la tête couverte posée au sol, les mains à
    plat de chaque côté, les coudes au sol, le dos rond avec le creux de l'échine et les plis de
    l'étoffe, les talons et les semelles en bas. Éclairé depuis le haut (le cierge devant lui)."""
    s = (1.0, 1.04, .74, .94)[variante]
    large = (1.0, 1.08, 1.0, .92)[variante]
    g = []
    # les semelles et les talons, sous les reins
    for x in (118, 182):
        g.append(f'<ellipse cx="{x}" cy="370" rx="20" ry="13" fill="{NUIT}" {ST} stroke-width="2.6"/>')
    # le dos : une grande forme ronde, plus large aux hanches ; jupe ou veste
    w2 = 104 * large
    g.append(f'<path d="M{150 - w2 * .82:.0f} 150 Q{150 - w2:.0f} 250 {150 - w2 * .92:.0f} 330 Q150 384 {150 + w2 * .92:.0f} 330 '
             f'Q{150 + w2:.0f} 250 {150 + w2 * .82:.0f} 150 Q150 118 {150 - w2 * .82:.0f} 150 Z" fill="{MINE}" {ST} stroke-width="3.6"/>')
    # le creux de l'échine et les omoplates
    g.append(f'<path d="M150 136 Q146 240 150 350" fill="none" stroke="{ENCRE}" stroke-width="2.6"/>'
             f'<path d="M104 170 Q122 200 140 186 M196 170 Q178 200 160 186" fill="none" stroke="{ENCRE}" stroke-width="2"/>')
    # les plis de l'étoffe qui tirent vers les hanches
    for dx in (-60, -32, 32, 60):
        g.append(f'<path d="M{150 + dx * .8:.0f} 220 Q{150 + dx:.0f} 280 {150 + dx * 1.15:.0f} 330" fill="none" stroke="{ENCRE}" stroke-width="1.6"/>')
    if variante == 1:   # la ceinture de l'homme
        g.append(f'<path d="M{150 - w2 * .95:.0f} 300 Q150 318 {150 + w2 * .95:.0f} 300" fill="none" stroke="{ENCRE}" stroke-width="7"/>')
    if variante in (0, 2):  # le tablier noué de la femme / la blouse de l'enfant
        g.append(f'<path d="M140 300 l-16 22 M160 300 l16 22" stroke="{CLAIR}" stroke-width="5" stroke-linecap="round"/>')
    # la lumière du cierge, devant : le haut des épaules s'éclaire
    g.append(f'<path d="M{150 - w2 * .78:.0f} 152 Q150 124 {150 + w2 * .78:.0f} 152" fill="none" stroke="{PAPIER}" stroke-width="4"/>')
    # les bras : des épaules, les coudes écartés au sol, les mains à plat de chaque côté de la
    # tête, à sa hauteur, le dos de la main vers le ciel, les doigts vers le centre du cercle
    for sg in (-1, 1):
        cx, cy = 150 + sg * 100, 150          # le coude
        hx, hy = 150 + sg * 66, 92            # la main
        g.append(f'<path d="M{150 + sg * 66} 140 Q{150 + sg * 100} 132 {cx + sg * 10} {cy - 4} Q{cx + sg * 6} {cy + 22} {cx - sg * 16} {cy + 12} '
                 f'L{hx + sg * 2} {hy + 26} L{hx - sg * 18} {hy + 16} L{150 + sg * 50} 158 Z" fill="{MINE}" {ST} stroke-width="3"/>')
        g.append(f'<path d="M{hx - 16} {hy + 24} Q{hx - 20} {hy - 4} {hx - 2} {hy - 12} Q{hx + 18} {hy - 6} {hx + 16} {hy + 24} Z" fill="{CLAIR}" {ST} stroke-width="2.6"/>'
                 + "".join(f'<path d="M{hx + dx} {hy - 4} l{dx * .5:.1f} -16" stroke="{ENCRE}" stroke-width="5" stroke-linecap="round"/>'
                           f'<path d="M{hx + dx} {hy - 4} l{dx * .5:.1f} -16" stroke="{CLAIR}" stroke-width="2.6" stroke-linecap="round"/>' for dx in (-10, -3, 4, 11))
                 + f'<path d="M{hx - sg * 16} {hy + 14} l{-sg * 14} -12" stroke="{ENCRE}" stroke-width="2.4" stroke-linecap="round"/>')
    # la tête posée au sol, vue d'en haut : ce qu'on voit, c'est la coiffe
    if variante == 0:   # le fichu, le nœud et les deux pointes sur la nuque
        g.append(f'<path d="M150 46 Q114 54 112 96 Q118 132 150 138 Q182 132 188 96 Q186 54 150 46 Z" fill="{CLAIR}" {ST} stroke-width="3"/>'
                 f'<path d="M150 136 l-16 20 l12 2 Z M150 136 l16 20 l-12 2 Z" fill="{CLAIR}" {ST} stroke-width="2.4"/>'
                 f'<path d="M150 50 Q144 96 150 134 M128 70 Q140 100 146 130 M172 70 Q160 100 154 130" fill="none" stroke="{ENCRE}" stroke-width="1.4"/>')
    elif variante == 1:  # le bonnet, le bord roulé, les côtes de la laine
        g.append(f'<circle cx="150" cy="92" r="40" fill="{LAVIS}" {ST} stroke-width="3"/>'
                 f'<path d="M112 108 Q150 138 188 108" fill="none" stroke="{ENCRE}" stroke-width="9"/>'
                 + "".join(f'<path d="M{150 + dx} 56 Q{150 + dx * 1.2} 90 {150 + dx} 124" fill="none" stroke="{MINE}" stroke-width="1.4"/>' for dx in (-24, -8, 8, 24)))
    elif variante == 2:  # l'enfant : la tête nue, les cheveux, l'épi au sommet
        g.append(f'<circle cx="150" cy="96" r="34" fill="{PAPIER}" {ST} stroke-width="3"/>'
                 + "".join(f'<path d="M150 98 l{24 * math.cos(a):.0f} {24 * math.sin(a):.0f}" stroke="{ENCRE}" stroke-width="2"/>' for a in [i * .7 for i in range(9)])
                 + f'<circle cx="150" cy="98" r="3" fill="{ENCRE}"/>')
    else:                # le vieux : la casquette, la visière contre la terre, la nuque rase et maigre
        g.append(f'<circle cx="150" cy="98" r="34" fill="{LAVIS}" {ST} stroke-width="3"/>'
                 f'<path d="M118 76 Q150 34 182 76 L176 82 Q150 50 124 82 Z" fill="{NUIT}" {ST} stroke-width="2.4"/>'
                 f'<path d="M126 124 Q150 140 174 124 L170 138 Q150 150 130 138 Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
    return f'<g transform="translate(150 380) scale({s}) translate(-150 -380)">{"".join(g)}</g>'


# --- les cierges ---------------------------------------------------------------------------------------
def flamme(cx: float, cy: float, h: float, pente: float) -> str:
    tx = cx + pente * h
    return (f'<path d="M{cx:.1f} {cy:.1f} Q{cx - h * .26:.1f} {cy - h * .45:.1f} {tx:.1f} {cy - h:.1f} '
            f'Q{cx + h * .26:.1f} {cy - h * .45:.1f} {cx:.1f} {cy:.1f} Z" fill="{PAPIER}" {ST} stroke-width="1.6"/>')


def cierge(k: int) -> str:
    """Un cierge planté de biais dans le sillon, sa lueur ; k 0 droit, 1 qui vacille, 2 couché
    par le vent."""
    h = (26, 21, 24)[k]
    pente = (0, .2, .7)[k]
    return (f'<circle cx="{30 + pente * 8:.0f}" cy="56" r="{(24, 21, 22)[k]}" fill="{CLAIR}" opacity=".55"/>'
            f'<path d="M25 116 L27 62 L35 62 L35 116 Z" fill="{PAPIER}" {ST} stroke-width="2"/>'
            f'<path d="M31 62 V56" stroke="{ENCRE}" stroke-width="1.6"/>' + flamme(31, 57, h, pente))


def lueur(k: int) -> str:
    """Le cierge vu d'en haut : la lueur ronde, le bout du cierge, la flamme (k 0, 1, 2) ; k 3 :
    le cierge éteint de la place vide, la mèche noire, sans lueur."""
    if k == 3:
        return (f'<circle cx="45" cy="45" r="9" fill="{PAPIER}" {ST} stroke-width="2.4"/>'
                f'<circle cx="45" cy="45" r="2.6" fill="{ENCRE}"/>')
    r = (36, 31, 33)[k]
    pente = (0, 3, 10)[k]
    return (f'<circle cx="{45 + pente / 2}" cy="45" r="{r}" fill="{CLAIR}" opacity=".5"/>'
            f'<circle cx="{45 + pente / 2}" cy="45" r="{r * .55:.0f}" fill="{CLAIR}" opacity=".6"/>'
            f'<circle cx="45" cy="45" r="9" fill="{PAPIER}" {ST} stroke-width="2.4"/>'
            f'<path d="M45 45 Q{41 + pente} {38} {45 + pente} {30 - k} Q{49 + pente} {38} 45 45 Z" fill="{PAPIER}" {ST} stroke-width="1.6"/>')


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    fichiers = {
        "cin_e3-priere-champ": svg(champ(), CHAMP_W, H),
        "cin_e3-priere-profil": grille([profil(v, s) for v in range(4) for s in range(2)], 300, 220, 2),
        "cin_e3-priere-sillons": svg(sillons(), *SILLONS),
        "cin_e3-priere-dessus": grille([dessus(v) for v in range(4)], 300, 390, 4),
        "cin_e3-priere-cierge": grille([cierge(k) for k in range(3)], 60, 120, 3),
        "cin_e3-priere-lueur": grille([lueur(k) for k in range(4)], 90, 90, 4),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"e3_priere_champs : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
