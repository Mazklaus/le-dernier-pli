#!/usr/bin/env python3
"""Génère les gestes de l'étape 1 (directive « montrer plutôt que dire » du Game Director).

Format du Gameplay (PR #134) : chr_<perso>_<geste>_01, bande horizontale d'images de 200 x 320,
pieds à (100, 316), jouée une fois à 10 i/s, puis retour à la respiration (repos).

  art/src/chr/chr_<perso>_<geste>_01.svg   15 gestes balisés par la Narrative (voir GESTES)
  art/src/chr/chr_tobie_grimper_01.svg     4 images, Tobie de dos sur l'échelle (cinématique de
                                           sortie de tranchée) ; calques _red et -cendre vides
                                           (ni le ruban ni le front ne se voient de dos)
  art/src/fx/fx_rideau-sape-tombe.svg      6 images de 140 x 460 : la couverture anti-gaz se
                                           soulève au passage de Tobie et retombe derrière lui

Les personnages reprennent les dessins de tools/donnees/pnj_e1.svgfrag (repère 240 x 420, sol
à y 405, échelle 0,845) : seuls le bras qui bouge, la main et la bouche changent d'une image à
l'autre ; la dernière image est proche du repos pour que le retour à la respiration ne saute pas.

Grimper : le cycle fait monter Tobie de deux barreaux (128 px) en 4 images. Le sprite doit monter
de 32 px par image, à 6 i/s conseillé (190 px/s). Barreaux de fx_echelle-* tous les 64 px : à
l'image 0, la main droite tient le barreau situé à y 60 de l'image (la gauche à y 124, les pieds à
252 et 316). Chaque main ou pied posé reste sur son barreau tant qu'il tient.

Usage : python3 tools/gen_gestes_e1.py
"""
from __future__ import annotations

import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHR = ROOT / "art" / "src" / "chr"
FX = ROOT / "art" / "src" / "fx"
SOURCE = ROOT / "tools" / "donnees" / "pnj_e1.svgfrag"

PAPIER, ENCRE, LAVIS, ROUGE = "#E8E5DA", "#15130F", "#4A463D", "#9B1C1C"
CADRE_L, CADRE_H = 200, 320
ECHELLE = 0.845
SOL = 405
CENTRE_X = 120
ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'


def quad(p0, p1, l0: float, l1: float) -> str:
    """Segment de membre épais entre deux articulations."""
    (x0, y0), (x1, y1) = p0, p1
    a = math.atan2(y1 - y0, x1 - x0) + math.pi / 2
    c, s = math.cos(a), math.sin(a)
    return (f"M{x0 + c * l0 / 2:.1f} {y0 + s * l0 / 2:.1f} L{x1 + c * l1 / 2:.1f} {y1 + s * l1 / 2:.1f} "
            f"L{x1 - c * l1 / 2:.1f} {y1 - s * l1 / 2:.1f} L{x0 - c * l0 / 2:.1f} {y0 - s * l0 / 2:.1f} Z")


def bras(epaule, coude, main, fill: str, l0=22.0, l1=19.0, l2=16.0, trait=2.4) -> str:
    return (f'<path d="{quad(epaule, coude, l0, l1)}" fill="{fill}" stroke-width="{trait}"/>'
            f'<path d="{quad(coude, main, l1, l2)}" fill="{fill}" stroke-width="{trait}"/>'
            f'<circle cx="{coude[0]:.1f}" cy="{coude[1]:.1f}" r="{l1 / 2 - .6:.1f}" fill="{fill}" stroke="none"/>')


# --- personnages de la planche n° 2 --------------------------------------------------------
def groupe_pnj(gid: str) -> tuple[str, str]:
    src = SOURCE.read_text(encoding="utf-8")
    defs = re.search(r"<defs>.*?</defs>", src, re.S).group(0)
    groupe = re.search(rf'<g id="{gid}".*?\n    </g>', src, re.S).group(0)
    return defs, groupe


def retirer(groupe: str, *morceaux: str) -> str:
    for m in morceaux:
        assert m in groupe, m
        groupe = groupe.replace(m, "", 1)
    return groupe


def planche_pnj(defs: str, images: list[str]) -> str:
    corps = []
    for i, contenu in enumerate(images):
        tx = i * CADRE_L + 100 - CENTRE_X * ECHELLE
        ty = 316 - SOL * ECHELLE
        corps.append(f'<g transform="translate({tx:.2f} {ty:.2f}) scale({ECHELLE})">{contenu}</g>')
    n = len(images)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{CADRE_L * n}" height="{CADRE_H}" '
            f'viewBox="0 0 {CADRE_L * n} {CADRE_H}">{defs}{"".join(corps)}</svg>\n')


def geste(gid: str, enlever: tuple[str, ...], images: list[str], avant: str | None = None) -> str:
    """Planche d'un geste : le personnage sans les morceaux `enlever`, et pour chaque image le
    dessin qui bouge, posé à la fin du groupe ou juste avant le commentaire `avant`."""
    defs, g = groupe_pnj(gid)
    base = retirer(g, *enlever)
    ou = base.index(avant) if avant else base.rindex("</g>")
    return planche_pnj(defs, [base[:ou] + f'<g {ST}>{d}</g>' + base[ou:] for d in images])


def pli_tenu(x: float, y: float, ang: float, s: float = 1.0) -> str:
    """Le pli tenu, vu de face : papier, cachet noir, ruban rouge."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.0f}) scale({s})">'
            f'<path d="M-15 -11 L15 -11 L15 11 L-15 11 Z" fill="{PAPIER}" {ST} stroke-width="2"/>'
            f'<path d="M-15 -11 L0 -2 L15 -11" fill="none" {ST} stroke-width="1.2"/>'
            f'<path d="M0 -11 V18 M0 11 L-4 20" stroke="{ROUGE}" stroke-width="2.6" stroke-linecap="round"/>'
            f'<circle cx="0" cy="0" r="4.6" fill="{ENCRE}"/></g>')


def main_poing(x: float, y: float, r: float = 9) -> str:
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{PAPIER}" stroke-width="2"/>'


def main_ouverte(x: float, y: float, ang: float, s: float = 1.0) -> str:
    """Main ouverte, doigts serrés vers le haut (ang = 0), pouce écarté vers la gauche."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.0f}) scale({s})">'
            f'<path d="M-8 6 L-8 -10 Q-8 -16 -3 -16 L5 -16 Q9 -16 9 -10 L9 6 Q0 12 -8 6 Z" fill="{PAPIER}" stroke-width="2"/>'
            f'<path d="M-3 -16 V-6 M2 -16 V-6" stroke-width=".9"/>'
            f'<path d="M-8 0 Q-16 -4 -15 -10 Q-12 -12 -8 -6" fill="{PAPIER}" stroke-width="1.8"/></g>')


def main_index(x: float, y: float, ang: float, s: float = 1.0) -> str:
    """Poing, index tendu dans la direction ang (0 = vers la gauche de l'image)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.0f}) scale({s})">'
            f'<path d="M-24 -5 L-6 -5 L-6 2 L-24 2 Q-27 -1.5 -24 -5 Z" fill="{PAPIER}" stroke-width="1.8"/>'
            f'<circle cx="0" cy="1" r="9" fill="{PAPIER}" stroke-width="2"/>'
            f'<path d="M-4 -3 Q2 -6 6 -2" fill="none" stroke-width="1"/></g>')


# Lamarre : le bras gauche (à gauche de l'image, côté de Tobie) et sa main sont redessinés ;
# la main droite garde la bougie. Les galons suivent le haut du bras, qui bouge peu.
LAMARRE = ('<path d="M66 124 L52 258 L74 264 L88 150 Z" fill="url(#hach-2)" stroke-width="2.4"/>',
           '<path d="M52 258 Q50 276 62 278 Q74 276 74 264 Z" fill="#E8E5DA" stroke-width="2"/>',
           '<path d="M56 170 L68 160 L80 170 M57 180 L69 170 L81 180" stroke="#E8E5DA" stroke-width="3" fill="none"/>\n'
           '      <path d="M56 170 L68 160 L80 170 M57 180 L69 170 L81 180" stroke-width="1" fill="none"/>')
L_EPAULE = (77.0, 137.0)


def moufle(x: float, y: float, ang: float, ouverte: bool = False) -> str:
    """La main carrée de Lamarre : un pavé de doigts serrés, le pouce dessus (ang 0 = doigts à droite)."""
    if ouverte:
        d = "M-8 -9 L12 -9 Q16 -2 12 9 L-8 9 Z"
        doigts = '<path d="M-2 -5 H11 M-2 0 H13 M-2 5 H11" stroke-width="1"/>'
    else:
        d = "M-9 -10 L8 -10 Q14 0 8 10 L-9 10 Z"
        doigts = '<path d="M2 -6 Q7 -4 7 0 M2 3 Q7 4 6 7" stroke-width="1"/>'
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.0f})">'
            f'<path d="{d}" fill="{PAPIER}" stroke-width="2"/>{doigts}'
            f'<path d="M-6 -10 Q-2 -16 4 -13" fill="none" stroke-width="1.6"/></g>')


def bras_lamarre(coude, main) -> str:
    """Le bras de capote et ses galons, posés sur le haut du bras quelle que soit sa pente."""
    ex, ey = L_EPAULE
    a = math.degrees(math.atan2(coude[1] - ey, coude[0] - ex)) - 90
    galons = (f'<g transform="rotate({a:.0f} {ex} {ey})">'
              '<path d="M68 170 L77 162 L86 170 M69 180 L78 172 L87 180" stroke="#E8E5DA" stroke-width="3" fill="none"/>'
              '<path d="M68 170 L77 162 L86 170 M69 180 L78 172 L87 180" stroke-width="1" fill="none"/></g>')
    return bras(L_EPAULE, coude, main, "url(#hach-2)") + galons


L_REPOS = bras_lamarre((60, 200), (63, 262)) + moufle(63, 262, 90)
L_FIN = bras_lamarre((58, 226), (56, 258)) + moufle(56, 258, 100)
PAN = '<path d="M92 172 L128 168 L130 182 L94 186 Z" fill="url(#hach-2)" stroke-width="2"/>'


def lamarre_tendre() -> list[str]:
    """La main sort le pli de la capote, le tend vers Tobie, le lâche, redescend."""
    tendu = bras_lamarre((60, 202), (14, 192))
    return [L_REPOS,
            bras_lamarre((62, 214), (104, 186)) + pli_tenu(106, 172, -12) + PAN + moufle(104, 186, -30),
            bras_lamarre((56, 206), (36, 196)) + moufle(36, 196, 180) + pli_tenu(26, 194, -6),
            tendu + moufle(14, 192, 180) + pli_tenu(4, 190, -6),
            tendu + moufle(16, 194, 180, True),
            L_FIN]


def lamarre_montrer_pli() -> list[str]:
    """Il sort le pli et le tient debout devant sa poitrine, cachet vers Tobie, puis le rentre."""
    devant = bras_lamarre((56, 214), (96, 176))
    return [L_REPOS,
            bras_lamarre((62, 214), (104, 186)) + pli_tenu(106, 172, -12) + PAN + moufle(104, 186, -30),
            devant + pli_tenu(98, 152, 0, 1.25) + moufle(96, 176, -90),
            devant + pli_tenu(97, 150, -4, 1.25) + moufle(96, 175, -94),
            bras_lamarre((62, 214), (104, 186)) + pli_tenu(106, 176, -12) + PAN + moufle(104, 186, -30),
            L_FIN]


def lamarre_congedier() -> list[str]:
    """Un revers de main vers la sortie : « Va. »"""
    return [L_REPOS,
            bras_lamarre((52, 212), (70, 186)) + moufle(70, 186, -110, True),
            bras_lamarre((50, 206), (22, 196)) + moufle(22, 196, 200, True),
            bras_lamarre((54, 214), (34, 236)) + moufle(34, 236, 140, True),
            L_FIN]


def lamarre_lever_main() -> list[str]:
    """Au parapet : la main levée, paume ouverte, tenue un instant (« Cours »)."""
    haut = bras_lamarre((44, 130), (40, 74))
    return [L_REPOS,
            bras_lamarre((46, 190), (40, 150)) + moufle(40, 150, -90, True),
            haut + moufle(40, 74, -90, True),
            haut + moufle(41, 73, -92, True),
            bras_lamarre((46, 190), (42, 160)) + moufle(42, 160, -90, True),
            L_FIN]


# Jacquot : le bras gauche (pendant) est redessiné ; le droit garde le fusil à l'épaule.
JACQUOT = ('<path d="M72 216 Q56 250 64 286 Q72 292 80 284 Q74 254 86 226 Z" fill="url(#hach-1)" stroke-width="2.2"/>',
           '<circle cx="68" cy="290" r="9" fill="#E8E5DA" stroke-width="2"/>')
JACQUOT_AIR = '<path d="M127 175 Q134 173 140 175" fill="none" stroke-width="1.1"/>'
J_EPAULE = (80.0, 222.0)


def bras_jacquot(coude, main) -> str:
    return bras(J_EPAULE, coude, main, "url(#hach-1)", 20, 18, 15, 2.2)


J_REPOS = bras_jacquot((64, 256), (68, 288)) + main_poing(68, 288)
J_FIN = bras_jacquot((60, 252), (64, 280)) + main_poing(64, 280)


def bouche_sifflet(n: int) -> str:
    """Lèvres en cul de poule et n petits traits d'air qui partent vers la gauche, hors du visage."""
    out = ['<circle cx="120" cy="175" r="3" fill="#E8E5DA" stroke-width="1.4"/>']
    for k in range(n):
        out.append(f'<path d="M{90 - k * 4} {170 + k * 6} Q{84 - k * 6} {168 + k * 6} {78 - k * 8} {171 + k * 6}" fill="none" stroke-width="1.2"/>')
    return "".join(out)


def jacquot_siffler() -> list[str]:
    """L'air du dépôt : lèvres pincées, traits d'air qui s'allongent puis s'éteignent. Pas de note
    de musique (code de bande dessinée, refusé par le GD) : le sifflement est porté par le son."""
    return [J_REPOS + bouche_sifflet(0),
            J_REPOS + bouche_sifflet(1),
            J_REPOS + bouche_sifflet(2),
            J_REPOS + bouche_sifflet(3),
            J_REPOS + bouche_sifflet(2),
            J_REPOS + bouche_sifflet(0)]


def jacquot_lever_main() -> list[str]:
    haut = bras_jacquot((44, 196), (52, 150))
    return [J_REPOS,
            bras_jacquot((50, 236), (54, 204)) + main_ouverte(54, 196, -10),
            haut + main_ouverte(52, 142, -6),
            bras_jacquot((44, 196), (44, 148)) + main_ouverte(44, 140, -22),
            haut + main_ouverte(56, 142, 4),
            J_FIN]


def jacquot_secouer() -> list[str]:
    """Il secoue Tobie endormi par l'épaule : bras tendu bas vers la gauche, trois secousses."""
    return [J_REPOS,
            bras_jacquot((50, 250), (24, 262)) + main_ouverte(18, 262, -100),
            bras_jacquot((50, 246), (20, 252)) + main_ouverte(14, 252, -96),
            bras_jacquot((52, 252), (26, 268)) + main_ouverte(20, 268, -104),
            bras_jacquot((50, 246), (20, 254)) + main_ouverte(14, 254, -96),
            J_FIN]


def jacquot_montrer() -> list[str]:
    tendu = bras_jacquot((50, 214), (22, 204))
    return [J_REPOS,
            bras_jacquot((56, 240), (36, 230)) + main_index(36, 230, 10),
            tendu + main_index(22, 204, 6),
            bras_jacquot((50, 212), (20, 200)) + main_index(20, 200, 2),
            J_FIN]


def jacquot_prendre() -> list[str]:
    """Il tend la main ouverte, la referme sur ce qu'on lui donne et la ramène contre lui."""
    return [J_REPOS,
            bras_jacquot((52, 240), (24, 236)) + main_ouverte(16, 236, -96),
            bras_jacquot((52, 240), (22, 236)) + main_poing(20, 236),
            bras_jacquot((70, 262), (100, 246)) + main_poing(100, 246),
            bras_jacquot((70, 262), (102, 248)) + main_poing(102, 248)]


# Cassien : la main droite (à droite de l'image) quitte les mains jointes ; la gauche reste.
CASSIEN_DROIT = ('<path d="M138 112 Q148 150 136 180 L126 176 Q134 150 128 118 Z" fill="#15130F" stroke-width="2"/>',
                 '<path d="M108 176 Q120 168 132 176 L128 194 Q120 200 112 194 Z" fill="#E8E5DA" stroke-width="2"/>',
                 '<path d="M120 172 L120 196" stroke-width="1"/>')
C_EPAULE_D = (134.0, 116.0)
C_EPAULE_G = (106.0, 116.0)
C_MAIN_G = '<path d="M106 176 Q114 170 122 176 L120 194 Q112 198 108 192 Z" fill="#E8E5DA" stroke-width="2"/>'
C_JOINTES = ('<path d="M138 112 Q148 150 136 180 L126 176 Q134 150 128 118 Z" fill="#15130F" stroke-width="2"/>'
             '<path d="M108 176 Q120 168 132 176 L128 194 Q120 200 112 194 Z" fill="#E8E5DA" stroke-width="2"/>'
             '<path d="M120 172 L120 196" stroke-width="1"/>')


def bras_soutane(epaule, coude, main) -> str:
    return bras(epaule, coude, main, ENCRE, 13, 12, 10, 2)


def pouce_cendre(x: float, y: float, ang: float) -> str:
    """Poing, pouce levé et gris de cendre (lavis)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.0f})">'
            f'<circle cx="0" cy="0" r="7" fill="{PAPIER}" stroke-width="1.8"/>'
            f'<path d="M-3 -6 Q-4 -15 1 -16 Q5 -15 4 -6" fill="{PAPIER}" stroke-width="1.6"/>'
            f'<path d="M-2 -13 Q1 -16 3 -13" stroke="{LAVIS}" stroke-width="3"/></g>')


def cassien_cendrer() -> list[str]:
    """Le pouce dans la coupelle de cendre, puis vers le front de Tobie : un trait, et les mains se rejoignent."""
    g = C_MAIN_G
    return [C_JOINTES,
            g + bras_soutane(C_EPAULE_D, (146, 184), (146, 240)) + main_poing(146, 242, 7),
            g + bras_soutane(C_EPAULE_D, (150, 160), (118, 136)) + pouce_cendre(118, 136, -10),
            g + bras_soutane(C_EPAULE_D, (100, 140), (54, 92)) + pouce_cendre(54, 92, -70),
            g + bras_soutane(C_EPAULE_D, (100, 142), (52, 100)) + pouce_cendre(52, 100, -80),
            C_JOINTES]


CASSIEN_GAUCHE = ('<path d="M102 112 Q92 150 104 180 L114 176 Q106 150 112 118 Z" fill="#15130F" stroke-width="2"/>',
                  '<path d="M108 176 Q120 168 132 176 L128 194 Q120 200 112 194 Z" fill="#E8E5DA" stroke-width="2"/>',
                  '<path d="M120 172 L120 196" stroke-width="1"/>',
                  '<circle cx="113" cy="186" r="3.6" fill="#15130F" stroke="#E8E5DA" stroke-width="1"/>')
C_MAIN_D = '<path d="M118 176 Q126 170 134 176 L132 192 Q126 198 120 194 Z" fill="#E8E5DA" stroke-width="2"/>'
C_JOINTES_G = ('<path d="M102 112 Q92 150 104 180 L114 176 Q106 150 112 118 Z" fill="#15130F" stroke-width="2"/>'
               '<path d="M108 176 Q120 168 132 176 L128 194 Q120 200 112 194 Z" fill="#E8E5DA" stroke-width="2"/>'
               '<path d="M120 172 L120 196" stroke-width="1"/>'
               '<circle cx="113" cy="186" r="3.6" fill="#15130F" stroke="#E8E5DA" stroke-width="1"/>')


def medaille(x: float, y: float, ang: float) -> str:
    """La médaille au bout de son cordon : la cloche sans battant en relief."""
    return (f'<g transform="rotate({ang:.0f} {x:.1f} {y:.1f})">'
            f'<path d="M{x:.1f} {y:.1f} V{y + 16:.1f}" stroke-width="1.2"/>'
            f'<circle cx="{x:.1f}" cy="{y + 23:.1f}" r="7" fill="{PAPIER}" stroke-width="1.8"/>'
            f'<path d="M{x - 3.5:.1f} {y + 26:.1f} Q{x - 3.5:.1f} {y + 19:.1f} {x:.1f} {y + 19:.1f} Q{x + 3.5:.1f} {y + 19:.1f} {x + 3.5:.1f} {y + 26:.1f} Z" fill="{ENCRE}" stroke="none"/></g>')


def bague(x: float, y: float) -> str:
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.6" fill="{ENCRE}" stroke="{PAPIER}" stroke-width="1"/>'


def cassien_tendre() -> list[str]:
    """Il sort la médaille de sa soutane et la tend, pendue au cordon, qui oscille."""
    d = C_MAIN_D
    return [C_JOINTES_G,
            d + bras_soutane(C_EPAULE_G, (94, 156), (112, 150)) + medaille(112, 150, 0) + main_poing(112, 150, 7) + bague(108, 154),
            d + bras_soutane(C_EPAULE_G, (86, 150), (60, 150)) + medaille(60, 150, 14) + main_poing(60, 150, 7) + bague(60, 156),
            d + bras_soutane(C_EPAULE_G, (82, 146), (40, 140)) + medaille(40, 140, -12) + main_poing(40, 140, 7) + bague(40, 146),
            d + bras_soutane(C_EPAULE_G, (82, 146), (40, 140)) + main_ouverte(38, 142, -90, .8),
            C_JOINTES_G]


# La Ravaude : bras gauche à la louche, bras droit à la marmite.
RAVAUDE_LOUCHE = ('<path d="M88 146 Q64 160 58 130 Q56 118 66 116 Q76 120 76 136 Q84 140 92 156 Z" fill="url(#hach-2)" stroke-width="2.2"/>',
                  '<circle cx="64" cy="112" r="8" fill="#E8E5DA" stroke-width="2"/>',
                  '<path d="M62 106 L56 60" stroke-width="3"/>',
                  '<path d="M44 60 Q56 76 68 60 Z" fill="#15130F" stroke-width="1.6"/>')
R_EPAULE_G = (86.0, 148.0)
R_EPAULE_D = (154.0, 148.0)


def louche(x: float, y: float, ang: float, pleine: bool = False) -> str:
    """La louche tenue en (x, y), manche de 46 px, cuilleron au bout (ang 0 = vers le haut)."""
    soupe = f'<path d="M-10 -46 Q0 -42 10 -46" stroke="{LAVIS}" stroke-width="3"/>' if pleine else ""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.0f})">'
            f'<path d="M0 0 L0 -46" stroke-width="3"/><path d="M-12 -48 Q0 -32 12 -48 Z" fill="{ENCRE}" stroke-width="1.6"/>{soupe}</g>')


def bras_ravaude(epaule, coude, main) -> str:
    return bras(epaule, coude, main, "url(#hach-2)", 18, 16, 14, 2.2)


R_REPOS = bras_ravaude(R_EPAULE_G, (62, 132), (64, 112)) + louche(64, 108, -8) + main_poing(64, 112, 8)


def ravaude_servir() -> list[str]:
    """La louche plonge dans la marmite, remonte pleine, se vide dans une gamelle tendue à gauche."""
    return [R_REPOS,
            bras_ravaude(R_EPAULE_G, (108, 186), (146, 160)) + louche(146, 160, 150) + main_poing(146, 160, 8),
            bras_ravaude(R_EPAULE_G, (90, 186), (110, 150)) + louche(110, 150, 170, True) + main_poing(110, 150, 8),
            bras_ravaude(R_EPAULE_G, (64, 170), (40, 150)) + louche(40, 150, 230) + main_poing(40, 150, 8)
            + f'<path d="M14 206 Q24 200 30 210" stroke="{LAVIS}" stroke-width="3" fill="none"/>',
            R_REPOS]


def ravaude_montrer() -> list[str]:
    """Elle montre avec la louche, comme avec un doigt."""
    return [R_REPOS,
            bras_ravaude(R_EPAULE_G, (62, 160), (48, 140)) + louche(48, 140, -50) + main_poing(48, 140, 8),
            bras_ravaude(R_EPAULE_G, (62, 160), (38, 152)) + louche(38, 152, -86) + main_poing(38, 152, 8),
            bras_ravaude(R_EPAULE_G, (62, 162), (36, 156)) + louche(36, 156, -92) + main_poing(36, 156, 8),
            R_REPOS]


RAVAUDE_MARMITE = ('<path d="M152 146 Q176 170 180 204 Q170 212 162 204 Q160 180 146 160 Z" fill="url(#hach-2)" stroke-width="2.2"/>',)
RAVAUDE_PIPE = '<path d="M112 330 L120 312 L132 312 Q136 312 136 318 L128 318" fill="none" stroke-width="2.4"/>'
R_MAIN_MARMITE = (bras_ravaude(R_EPAULE_D, (176, 176), (172, 204)) + main_poing(172, 206, 8))


def pipe(x: float, y: float, ang: float) -> str:
    """La pipe d'Aurèle tenue par le fourneau, le tuyau vers la gauche."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.0f})">'
            f'<path d="M-4 0 L-30 -6" stroke-width="2.6"/>'
            f'<path d="M-6 -8 L6 -8 L5 6 Q0 9 -5 6 Z" fill="{ENCRE}" stroke-width="1.4"/></g>')


def ravaude_tendre() -> list[str]:
    """Elle tire la pipe d'Aurèle de la poche du tablier (trop basse pour la main : la pipe quitte la
    poche dès la première image) et la tend devant elle, le tuyau vers Tobie."""
    poche = RAVAUDE_PIPE
    return [R_MAIN_MARMITE + poche,
            bras_ravaude(R_EPAULE_D, (168, 196), (140, 232)) + pipe(136, 226, -40) + main_poing(140, 232, 8),
            bras_ravaude(R_EPAULE_D, (158, 200), (112, 222)) + pipe(106, 218, 0) + main_poing(112, 222, 8),
            bras_ravaude(R_EPAULE_D, (148, 196), (94, 210)) + pipe(88, 206, 4) + main_poing(94, 210, 8),
            bras_ravaude(R_EPAULE_D, (148, 196), (94, 212)) + main_ouverte(92, 212, -90, .9),
            R_MAIN_MARMITE]


# Le Guetteur : il ne lâche pas le périscope ; son autre bras sort de derrière son dos et pointe.
def bras_guetteur(coude, main) -> str:
    return bras((96.0, 190.0), coude, main, "url(#hach-2)", 18, 16, 14, 2.2)


def guetteur_montrer() -> list[str]:
    return ["",
            bras_guetteur((76, 214), (60, 196)) + main_poing(58, 196, 7),
            bras_guetteur((70, 200), (36, 186)) + main_index(36, 186, 0, .9),
            bras_guetteur((70, 202), (32, 188)) + main_index(32, 188, -4, .9),
            bras_guetteur((72, 204), (38, 190)) + main_index(38, 190, 2, .9),
            bras_guetteur((78, 218), (66, 204)) + main_poing(66, 204, 7)]


GESTES = {
    "lamarre_tendre": ("p-lamarre", LAMARRE, lamarre_tendre, None),
    "lamarre_montrer-pli": ("p-lamarre", LAMARRE, lamarre_montrer_pli, None),
    "lamarre_congedier": ("p-lamarre", LAMARRE, lamarre_congedier, None),
    "lamarre_lever-main": ("p-lamarre", LAMARRE, lamarre_lever_main, None),
    "jacquot_siffler": ("p-jacquot", JACQUOT + (JACQUOT_AIR,), jacquot_siffler, None),
    "jacquot_lever-main": ("p-jacquot", JACQUOT, jacquot_lever_main, None),
    "jacquot_secouer": ("p-jacquot", JACQUOT, jacquot_secouer, None),
    "jacquot_montrer": ("p-jacquot", JACQUOT, jacquot_montrer, None),
    "jacquot_prendre": ("p-jacquot", JACQUOT, jacquot_prendre, None),
    "cassien_cendrer": ("p-cassien", CASSIEN_DROIT, cassien_cendrer, "<!-- bague"),
    "cassien_tendre": ("p-cassien", CASSIEN_GAUCHE, cassien_tendre, "<!-- tremblement"),
    "ravaude_servir": ("p-ravaude", RAVAUDE_LOUCHE, ravaude_servir, None),
    "ravaude_montrer": ("p-ravaude", RAVAUDE_LOUCHE, ravaude_montrer, None),
    "ravaude_tendre": ("p-ravaude", RAVAUDE_MARMITE + (RAVAUDE_PIPE,), ravaude_tendre, "<!-- tête large"),
    "guetteur_montrer": ("p-guetteur", (), guetteur_montrer, "<!-- bras levé"),
}


# --- Tobie de dos, sur l'échelle --------------------------------------------------------------
DEFS_TOBIE = f"""<defs>
<pattern id="h1" width="4.2" height="4.2" patternUnits="userSpaceOnUse" patternTransform="rotate(38)"><rect width="4.2" height="4.2" fill="{PAPIER}"/><line x1="0" y1="0" x2="0" y2="4.2" stroke="{ENCRE}" stroke-width="1"/></pattern>
<pattern id="h2" width="3.4" height="3.4" patternUnits="userSpaceOnUse" patternTransform="rotate(38)"><rect width="3.4" height="3.4" fill="{PAPIER}"/><line x1="0" y1="0" x2="0" y2="3.4" stroke="{ENCRE}" stroke-width="1.1"/><line x1="0" y1="1.7" x2="3.4" y2="1.7" stroke="{ENCRE}" stroke-width=".7"/></pattern>
<pattern id="mol" width="7.6" height="7.6" patternUnits="userSpaceOnUse" patternTransform="rotate(-22)"><rect width="7.6" height="7.6" fill="{PAPIER}"/><line x1="0" y1="0" x2="7.6" y2="0" stroke="{ENCRE}" stroke-width="1.5"/><line x1="0" y1="3.8" x2="7.6" y2="3.8" stroke="{ENCRE}" stroke-width=".6"/></pattern>
<pattern id="pt" width="3.4" height="3.4" patternUnits="userSpaceOnUse"><rect width="3.4" height="3.4" fill="{PAPIER}"/><circle cx="1.7" cy="1.7" r=".7" fill="{ENCRE}"/></pattern>
</defs>"""

CUISSE = 54.0
MAIN_A = (60, 92, 124, 92)          # main droite et pied gauche : posés à l'image 0
MAIN_B = (124, 92, 60, 92)          # main gauche et pied droit : posés à l'image 2
PIED_A = (252, 284, 316, 284)
PIED_B = (316, 284, 252, 284)
EN_L_AIR_A = (False, False, False, True)
EN_L_AIR_B = (False, True, False, False)


def genou(hanche, pied, cote: int) -> tuple[float, float]:
    """Genou vu de dos : plus la jambe est repliée, plus il part sur le côté et remonte."""
    hx, hy = hanche
    px, py = pied
    d = math.hypot(px - hx, py - hy)
    ecart = math.sqrt(max(0.0, CUISSE ** 2 - (d / 2) ** 2))
    return (hx + px) / 2 + cote * ecart * .55, (hy + py) / 2 - ecart * .25


def coude_ik(epaule, main, cote: int, l: float = 31.0) -> tuple[float, float]:
    """Coude d'un bras à deux segments égaux, sorti vers l'extérieur (cote) et vers le bas."""
    (ex, ey), (mx, my) = epaule, main
    dx, dy = mx - ex, my - ey
    d = min(math.hypot(dx, dy), 2 * l - .01)
    h = math.sqrt(l * l - (d / 2) ** 2)
    nx, ny = -dy / d, dx / d                 # normale à la droite épaule-main
    if nx * cote + ny * .6 < 0:
        nx, ny = -nx, -ny
    return ex + dx / 2 + nx * h, ey + dy / 2 + ny * h


def tobie_dos(k: int) -> str:
    cx = 100
    sway = (2, 0, -2, 0)[k]           # le corps penche vers le côté qui tient
    tete_y = 66
    out = [f'<g {ST}>']
    # jambes (derrière la vareuse)
    for cote, ys, air in ((-1, PIED_A, EN_L_AIR_A), (1, PIED_B, EN_L_AIR_B)):
        hanche = (cx + sway + cote * 12, 206)
        py = ys[k]
        px = cx + cote * 18 + (cote * 6 if air[k] else 0)
        g = genou(hanche, (px, py - 14), cote)
        out.append(f'<path d="{quad(hanche, g, 19, 16)}" fill="url(#h2)" stroke-width="2.1"/>')
        out.append(f'<path d="{quad(g, (px, py - 14), 16, 13)}" fill="url(#mol)" stroke-width="2.1"/>')
        out.append(f'<circle cx="{g[0]:.1f}" cy="{g[1]:.1f}" r="7.4" fill="url(#mol)" stroke="none"/>')
        if air[k]:
            # pied levé : on voit la semelle
            out.append(f'<path d="M{px - 9} {py - 18} L{px + 9} {py - 18} L{px + 8} {py - 2} L{px - 8} {py - 2} Z" fill="{ENCRE}" stroke-width="1.6"/>'
                       f'<path d="M{px - 5} {py - 12} H{px + 5} M{px - 5} {py - 7} H{px + 5}" stroke="{LAVIS}" stroke-width="1.2"/>')
        else:
            # talon posé sur le barreau
            out.append(f'<path d="M{px - 10} {py - 16} L{px + 10} {py - 16} L{px + 11} {py} L{px - 11} {py} Z" fill="{ENCRE}" stroke-width="1.6"/>')
    # vareuse vue de dos, pans fendus
    x0 = cx + sway
    out.append(f'<path d="M{x0 - 28} 98 Q{x0} 90 {x0 + 28} 98 Q{x0 + 34} 150 {x0 + 30} 200 L{x0 + 32} 222 L{x0 + 4} 218 L{x0} 212 L{x0 - 4} 218 '
               f'L{x0 - 32} 222 L{x0 - 30} 200 Q{x0 - 34} 150 {x0 - 28} 98 Z" fill="{PAPIER}" stroke-width="2.4"/>')
    out.append(f'<path d="M{x0 - 28} 100 Q{x0 - 34} 150 {x0 - 30} 200 L{x0 - 32} 220 L{x0 - 16} 220 Q{x0 - 20} 150 {x0 - 14} 96 Z" fill="url(#h2)" stroke="none"/>')
    out.append(f'<path d="M{x0} 104 V196" stroke-width="1" stroke-dasharray="6 5"/>')
    # ceinturon, bandoulière (de l'épaule droite à la hanche gauche), sacoche, lanterne
    out.append(f'<path d="M{x0 - 31} 196 Q{x0} 202 {x0 + 31} 196" stroke-width="4.6" fill="none"/>')
    out.append(f'<path d="M{x0 + 22} 98 L{x0 - 26} 194" stroke-width="4.6" fill="none"/>'
               f'<path d="M{x0 + 22} 98 L{x0 - 26} 194" stroke="{PAPIER}" stroke-width="1.5" fill="none"/>')
    out.append(f'<path d="M{x0 - 42} 190 L{x0 - 18} 188 L{x0 - 17} 226 L{x0 - 41} 228 Z" fill="url(#h1)" stroke-width="2"/>'
               f'<path d="M{x0 - 42} 190 L{x0 - 18} 188 L{x0 - 18} 200 L{x0 - 42} 202 Z" fill="{PAPIER}" stroke-width="1.8"/>')
    bal = (-8, 4, 8, -4)[k]
    out.append(f'<g transform="rotate({bal} {x0 + 30} 200)"><path d="M{x0 + 30} 200 V208" stroke-width="1.7"/>'
               f'<path d="M{x0 + 24} 208 H{x0 + 37} L{x0 + 35} 228 H{x0 + 26} Z" fill="url(#pt)" stroke-width="1.8"/>'
               f'<path d="M{x0 + 22} 208 H{x0 + 39} M{x0 + 24} 230 H{x0 + 37}" stroke-width="2.2"/></g>')
    # col, tête de dos : cheveux en contre-hachure, oreilles, nuque
    out.append(f'<path d="M{x0 - 12} 96 Q{x0} 102 {x0 + 12} 96 L{x0 + 11} 86 L{x0 - 11} 86 Z" fill="url(#h1)" stroke-width="2"/>')
    out.append(f'<ellipse cx="{x0 - 23}" cy="{tete_y + 4}" rx="4" ry="6" fill="{PAPIER}" stroke-width="1.6"/>'
               f'<ellipse cx="{x0 + 23}" cy="{tete_y + 4}" rx="4" ry="6" fill="{PAPIER}" stroke-width="1.6"/>')
    out.append(f'<path d="M{x0 - 22} {tete_y + 12} Q{x0 - 26} {tete_y - 22} {x0} {tete_y - 26} Q{x0 + 26} {tete_y - 22} {x0 + 22} {tete_y + 12} '
               f'Q{x0 + 14} {tete_y + 24} {x0} {tete_y + 24} Q{x0 - 14} {tete_y + 24} {x0 - 22} {tete_y + 12} Z" fill="url(#h2)" stroke-width="2.3"/>')
    out.append(f'<path d="M{x0 - 10} {tete_y + 20} Q{x0} {tete_y + 26} {x0 + 10} {tete_y + 20}" fill="none" stroke-width="1.2"/>')
    # bras : épaules -> barreaux
    for cote, ys, air in ((1, MAIN_A, EN_L_AIR_A), (-1, MAIN_B, EN_L_AIR_B)):
        epaule = (x0 + cote * 24, 104)
        my = ys[k] - (6 if air[k] else 0)
        mx = cx + cote * (31 + (6 if air[k] else 0))
        coude = coude_ik(epaule, (mx, my), cote)
        out.append(bras(epaule, coude, (mx, my), "url(#h1)", 17, 14, 12, 2.1))
        if air[k]:
            out.append(f'<path d="M{mx - 6} {my + 4} Q{mx - 7} {my - 8} {mx} {my - 9} Q{mx + 7} {my - 8} {mx + 6} {my + 4} Z" fill="{PAPIER}" stroke-width="1.7"/>')
        else:
            # le poing serré sur le barreau, les doigts dessus
            out.append(f'<ellipse cx="{mx}" cy="{my}" rx="7.5" ry="6.4" fill="{PAPIER}" stroke-width="1.8"/>'
                       f'<path d="M{mx - 5} {my - 2} H{mx + 5}" stroke-width=".9"/>')
    out.append("</g>")
    return "".join(out)


def planche(images: list[str], defs: str, l: int = CADRE_L, h: int = CADRE_H) -> str:
    corps = "".join(f'<g transform="translate({i * l} 0)">{c}</g>' for i, c in enumerate(images))
    n = len(images)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{l * n}" height="{h}" '
            f'viewBox="0 0 {l * n} {h}">{defs}{corps}</svg>\n')


# --- la couverture anti-gaz de la sape de sortie ----------------------------------------------
DEFS_RIDEAU = f"""<defs>
<pattern id="h1" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(38)"><rect width="5" height="5" fill="{PAPIER}"/><line x1="0" y1="0" x2="0" y2="5" stroke="{ENCRE}" stroke-width="1"/></pattern>
<pattern id="h2" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(38)"><rect width="4" height="4" fill="{PAPIER}"/><line x1="0" y1="0" x2="0" y2="4" stroke="{ENCRE}" stroke-width="1.1"/><line x1="0" y1="2" x2="4" y2="2" stroke="{ENCRE}" stroke-width=".8"/></pattern>
</defs>"""


def couverture(bg: tuple[float, float], bd: tuple[float, float], creux: float, ventre: float = 0.0) -> str:
    """La couverture clouée à la traverse : coins du bas bg et bd, ourlet qui pend de creux,
    ventre = poussée latérale du milieu (le passage de Tobie)."""
    w, h = 140, 460
    (gx, gy), (dx, dy) = bg, bd
    mx, my = (gx + dx) / 2, max(gy, dy) - creux
    out = [f'<path d="M8 18 L132 18 Q{136 + ventre * .4:.0f} {h * .5:.0f} {dx:.0f} {dy:.0f} Q{(mx + dx) / 2:.0f} {my + creux * .3:.0f} {mx:.0f} {my:.0f} '
           f'Q{(mx + gx) / 2:.0f} {my + creux * .3:.0f} {gx:.0f} {gy:.0f} Q{4 + ventre:.0f} {h * .5:.0f} 8 18 Z" fill="url(#h1)" {ST} stroke-width="3"/>']
    plis = []
    for i, x in enumerate(range(24, w - 10, 22)):
        t = (x - 8) / 124
        bx = gx + (dx - gx) * t
        by = (gy + (dy - gy) * t) - 6 - creux * (1 - abs(2 * t - 1)) * .8
        plis.append(f"M{x} 22 Q{x + 6 + ventre * (1 - abs(2 * t - 1)):.0f} {h * .5:.0f} {bx:.0f} {by:.0f}")
    out.append(f'<path d="{" ".join(plis)}" fill="none" {ST} stroke-width="1.6"/>')
    out.append(f'<rect x="0" y="4" width="{w}" height="18" fill="url(#h2)" {ST} stroke-width="3"/>')
    return "".join(out)


def rideau_tombe() -> str:
    images = [couverture((4, 456), (136, 456), 12),              # tendue
              couverture((26, 444), (138, 452), 10, 22),         # Tobie pousse : le bas gonfle
              couverture((84, 290), (138, 420), -30, 30),        # soulevée, rabattue sur la droite
              couverture((44, 400), (138, 446), 4, 18),          # elle retombe
              couverture((0, 456), (124, 452), 14, -12),         # balance de l'autre côté
              couverture((4, 456), (136, 456), 12)]              # tendue, de nouveau
    return planche(images, DEFS_RIDEAU, 140, 460)


def main() -> None:
    CHR.mkdir(parents=True, exist_ok=True)
    FX.mkdir(parents=True, exist_ok=True)
    for nom, (gid, enlever, fn, avant) in GESTES.items():
        (CHR / f"chr_{nom}_01.svg").write_text(geste(gid, enlever, fn(), avant), encoding="utf-8")
    images = [tobie_dos(k) for k in range(4)]
    (CHR / "chr_tobie_grimper_01.svg").write_text(planche(images, DEFS_TOBIE), encoding="utf-8")
    vide = planche([""] * 4, "")
    (CHR / "chr_tobie_grimper_01_red.svg").write_text(vide, encoding="utf-8")
    (CHR / "chr_tobie-cendre_grimper_01.svg").write_text(vide, encoding="utf-8")
    (FX / "fx_rideau-sape-tombe.svg").write_text(rideau_tombe(), encoding="utf-8")
    print(f"{len(GESTES)} gestes, grimper (et ses 2 calques), fx_rideau-sape-tombe")


if __name__ == "__main__":
    main()
