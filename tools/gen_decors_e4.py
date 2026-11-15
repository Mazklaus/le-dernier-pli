#!/usr/bin/env python3
"""Génère les fonds de l'étape 4, l'Hôpital des Recousus (maquette du Level Designer, #142).

Toute l'étape est faite de pièces fermées : un fond fixe par lieu, sans parallaxe, découpé en
tuiles de 2048 px au plus, art/src/env/e4/env_e4_plan3_<lieu>_NN.svg, posé en (0, 0) dans le
repère du lieu (scenes/decors/decor_e4.gd). Sol à y 900. Dans les lieux souterrains, le plafond
de collision va de y 330 à 450 ; le porche et la rue latérale sont à ciel ouvert.

  porche          1920  la rue, la façade de l'hôpital, le tronc (x 700), le perron de Maude
                        (x 1150), la grande porte (passage VersSalle, x 1520 à 1680)
  salle           3840  la salle commune : lits de fer numérotés, tous occupés ; la porte de la
                        lingerie toujours ouverte (x 1420 à 1580) ; une place vide dans la rangée
                        pour le lit de Fernand (son sprite porte son lit, x 2100) ; porte du fond
  lingerie        1440  rayonnages de draps pliés, les draps cousus en forme de corps (x 700)
  atelier         1920  l'atelier d'Anselme, presque vide et propre : bocaux (x 550), planche
                        anatomique (x 850), table d'opération (x 1250), porte de l'escalier
  escalier         960  les ex-voto de cire pendus aux clous, plus nombreux que les marches
  crypte          2880  niches des saints couchés sous verre, lampes à huile, plaques grattées
                        (x 1400) ; la zone sombre la recouvre en jeu à partir de x 650
  escalier-service 960  l'escalier de service, nu, qui remonte d'un coup vers la porte latérale
  rue-laterale    1920  la ruelle derrière l'hôpital, la petite porte (sortie x 300), la route

Garde-fous : rien de rouge (la correction du cœur sur la planche est à l'encre), aucune plaie,
aucun œil, aucun nom lisible (les étiquettes et les plaques sont des traits), aucune cloche qui
sonne. Les organes des bocaux sont des silhouettes sombres dans le liquide, jamais détaillées.
La grammaire est celle des lieux de l'étape 3 : chaux en papier nu, peu de hachures.

Usage : python3 tools/gen_decors_e4.py
"""
from __future__ import annotations

import math

from gen_decors_e1_surface import rnd
from gen_decors_e3_lieux import PLAFOND
from gen_decors_e3_surface import DEFS, ENCRE, H, LAVIS, MINE, PAPIER, ROOT, SOL, ST, TUILE, porte_bois

DST = ROOT / "art" / "src" / "env" / "e4"


# --------------------------------------------------------------------------- pièces
def voute(w: int, pierre: bool = False) -> str:
    """Le haut d'une pièce souterraine : voûtes en berceau sur doubleaux, dans l'ombre (le plafond
    de collision est de 330 à 450)."""
    out = [f'<rect width="{w}" height="{PLAFOND + 120}" fill="{MINE}"/>']
    for x in range(0, w + 320, 320):
        out.append(f'<path d="M{x - 160} {PLAFOND + 120} Q{x - 160} {PLAFOND - 140} {x} {PLAFOND - 150} '
                   f'Q{x + 160} {PLAFOND - 140} {x + 160} {PLAFOND + 120}" fill="{LAVIS if pierre else PAPIER}" {ST} stroke-width="2.4"/>')
        out.append(f'<rect x="{x + 140}" y="0" width="40" height="{PLAFOND + 120}" fill="url(#moellons)" {ST} stroke-width="2.4"/>')
    out.append(f'<rect y="{PLAFOND + 96}" width="{w}" height="24" fill="url(#h2)" {ST} stroke-width="2.6"/>')
    return "".join(out)


def mur(w: int, pierre: bool = False) -> str:
    """Mur chaulé (ou moellons nus sous terre), plinthe salie, dallage."""
    out = [f'<rect width="{w}" height="{H}" fill="{"url(#moellons)" if pierre else PAPIER}"/>', voute(w, pierre)]
    out.append(f'<rect y="{SOL - 50}" width="{w}" height="50" fill="url(#v1)"/>')
    out.append(f'<path d="M0 {SOL - 50} H{w}" {ST} stroke-width="1.6"/>')
    out.append(f'<rect y="{SOL}" width="{w}" height="{H - SOL}" fill="{PAPIER}"/>')
    for y in range(SOL + 30, H, 40):
        out.append(f'<path d="M0 {y} H{w}" {ST} stroke-width="1.2"/>')
    for x in range(0, w + 120, 120):
        out.append(f'<path d="M{x} {SOL} L{x - 50} {H}" {ST} stroke-width="1.2"/>')
    out.append(f'<path d="M0 {SOL} H{w}" {ST} stroke-width="3"/>')
    return "".join(out)


def porte_ouverte(x0: int, x1: int, dedans: str = "") -> str:
    """Une porte grande ouverte sur une pièce sombre : le vantail rabattu contre le mur."""
    haut = 600
    return (f'<path d="M{x0 - 16} {haut - 18} H{x1 + 16} V{haut} H{x0 - 16} Z" fill="url(#moellons)" {ST} stroke-width="2.4"/>'
            f'<rect x="{x0}" y="{haut}" width="{x1 - x0}" height="{SOL - haut}" fill="{ENCRE}"/>' + dedans +
            f'<path d="M{x0} {haut} L{x0 - 60} {haut + 24} V{SOL + 8} L{x0} {SOL} Z" fill="url(#vantail)" {ST} stroke-width="3"/>'
            f'<path d="M{x0 - 10} {SOL} H{x1 + 10} V{SOL - 10} H{x0 - 10} Z" fill="{PAPIER}" {ST} stroke-width="2"/>')


def soupirail(x: int, y: int = 470) -> str:
    """Haut soupirail à barreaux : le jour de la rue, en papier nu."""
    return (f'<path d="M{x} {y + 90} V{y + 20} Q{x + 50} {y - 10} {x + 100} {y + 20} V{y + 90} Z" fill="{PAPIER}" {ST} stroke-width="3"/>'
            f'<path d="M{x + 25} {y + 8} V{y + 90} M{x + 50} {y + 2} V{y + 90} M{x + 75} {y + 8} V{y + 90}" {ST} stroke-width="3"/>'
            f'<path d="M{x} {y + 90} L{x + 30} {SOL - 60}" stroke="{PAPIER}" stroke-width="0"/>')


# --------------------------------------------------------------------------- objets
def lit(x: int, numero_repeint: bool = False, dormeur: bool = True, r=None) -> str:
    """Un lit de fer vu dans sa longueur (même échelle que celui de Fernand : sommier à y 812,
    tête à gauche), un drap, un dormeur sous la couverture, le numéro peint sur le montant."""
    r = r or rnd(x)
    t, f = x, x + 200
    out = [f'<path d="M{t} {SOL} V754 M{t + 34} {SOL} V754 M{f - 14} {SOL} V790 M{f} {SOL} V790" {ST} stroke-width="3.4"/>',
           f'<path d="M{t} 758 Q{t + 17} 746 {t + 34} 758 M{t} 772 H{t + 34} M{t + 9} 768 V812 M{t + 17} 764 V812 M{t + 25} 768 V812 M{f - 14} 794 Q{f - 7} 788 {f} 794" fill="none" {ST} stroke-width="2"/>',
           f'<path d="M{t} 812 H{f} V834 H{t} Z" fill="url(#h1)" {ST} stroke-width="2"/>']
    if dormeur:
        # la couverture sur un corps allongé, la tête ronde sur l'oreiller, de dos au joueur
        bosse = r.randint(-6, 8)
        out.append(f'<path d="M{t + 34} 812 Q{t + 40} 800 {t + 56} 798 Q{t + 100} {788 + bosse} {t + 140} 796 Q{t + 176} 794 {f - 6} 806 L{f - 6} 838 Q{t + 120} 848 {t + 34} 838 Z" fill="{PAPIER}" {ST} stroke-width="2"/>')
        out.append(f'<path d="M{t + 70} 806 Q{t + 74} 822 {t + 70} 838 M{t + 130} 800 Q{t + 136} 820 {t + 130} 842" fill="none" stroke="{MINE}" stroke-width="1.2"/>')
        out.append(f'<path d="M{t + 34} 806 Q{t + 36} 794 {t + 52} 794 L{t + 60} 798 L{t + 58} 812 H{t + 34} Z" fill="{PAPIER}" {ST} stroke-width="1.6"/>')
        out.append(f'<circle cx="{t + 50}" cy="790" r="13" fill="url(#h2)" {ST} stroke-width="1.8"/>')
    else:
        out.append(f'<path d="M{t + 34} 806 H{f - 6} V834 Q{t + 120} 842 {t + 34} 834 Z" fill="{PAPIER}" {ST} stroke-width="2"/>')
    # le numéro à la peinture sur le montant de tête (des traits : aucun chiffre lisible requis)
    out.append(f'<rect x="{t - 4}" y="780" width="20" height="16" fill="{PAPIER}" {ST} stroke-width="1.4"/>')
    out.append(f'<path d="M{t} 784 V792 M{t + 5} 784 Q{t + 12} 784 {t + 6} 792 H{t + 12}" fill="none" {ST} stroke-width="1.6"/>')
    if numero_repeint:
        # repeint par-dessus, puis encore par-dessus (salle_lits) : couches décalées
        for k, dy in enumerate((-12, -24)):
            out.append(f'<rect x="{t - 6 + k * 2}" y="{780 + dy}" width="22" height="14" fill="{PAPIER}" {ST} stroke-width="1.2"/>')
            out.append(f'<path d="M{t - 2 + k * 2} {784 + dy} V{791 + dy} M{t + 4} {784 + dy} H{t + 12} L{t + 6} {791 + dy}" fill="none" {ST} stroke-width="1.4"/>')
        out.append(f'<path d="M{t - 6} 776 L{t + 18} 770 M{t - 6} 788 L{t + 18} 782" stroke="{MINE}" stroke-width="1.4"/>')
    return "".join(out)


def bocal(x: float, y: float, h: int, organe: str) -> str:
    """Un bocal de verre (contour fin, reflet en papier), liquide en lavis clair, une silhouette
    sombre dedans, une étiquette à traits (pas de lettres lisibles)."""
    w = h * .7
    out = [f'<rect x="{x - w / 2:.0f}" y="{y - h}" width="{w:.0f}" height="{h}" rx="6" fill="url(#h1)" {ST} stroke-width="2"/>',
           f'<rect x="{x - w / 2 - 3:.0f}" y="{y - h - 8}" width="{w + 6:.0f}" height="10" fill="{ENCRE}"/>']
    cx, cy = x, y - h * .55
    if organe == "main":
        out.append(f'<path d="M{cx - 10} {cy + 14} L{cx - 10} {cy - 4} L{cx - 12} {cy - 16} M{cx - 4} {cy - 4} L{cx - 4} {cy - 20} M{cx + 2} {cy - 4} L{cx + 3} {cy - 20} M{cx + 8} {cy - 2} L{cx + 10} {cy - 14}" stroke="{LAVIS}" stroke-width="5"/>'
                   f'<path d="M{cx - 12} {cy - 6} H{cx + 10} V{cy + 16} H{cx - 12} Z" fill="{LAVIS}"/>')
    elif organe == "coeur":
        out.append(f'<path d="M{cx} {cy + 14} Q{cx - 18} {cy} {cx - 10} {cy - 10} Q{cx - 2} {cy - 14} {cx} {cy - 6} Q{cx + 4} {cy - 16} {cx + 12} {cy - 8} Q{cx + 16} {cy + 2} {cx} {cy + 14} Z" fill="{LAVIS}"/>')
    elif organe == "oreille":
        out.append(f'<path d="M{cx - 4} {cy + 12} Q{cx - 12} {cy} {cx - 6} {cy - 12} Q{cx + 8} {cy - 18} {cx + 10} {cy - 4} Q{cx + 8} {cy + 4} {cx + 2} {cy + 6} Q{cx} {cy + 14} {cx - 4} {cy + 12} Z" fill="{LAVIS}"/>')
    else:
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{w / 4:.0f}" ry="{h / 6:.0f}" fill="{LAVIS}"/>')
    out.append(f'<path d="M{x - w / 2 + 5:.0f} {y - h + 8} V{y - 10}" stroke="{PAPIER}" stroke-width="3"/>')
    out.append(f'<rect x="{x - 14:.0f}" y="{y - 24}" width="28" height="14" fill="{PAPIER}" {ST} stroke-width="1.2"/>'
               f'<path d="M{x - 9:.0f} {y - 17} H{x + 9:.0f}" {ST} stroke-width="1.6"/>')
    return "".join(out)


def ex_voto(x: float, y: float, sorte: int, r) -> str:
    """Un membre de cire pendu à un clou par une ficelle : bras, jambe, main, pied, cœur de cire."""
    out = [f'<circle cx="{x:.0f}" cy="{y:.0f}" r="2.2" fill="{ENCRE}"/>',
           f'<path d="M{x:.0f} {y:.0f} L{x - 4:.0f} {y + 10:.0f} M{x:.0f} {y:.0f} L{x + 4:.0f} {y + 10:.0f}" {ST} stroke-width="1"/>']
    a = r.uniform(-8, 8)
    g = f'<g transform="translate({x:.0f} {y + 10:.0f}) rotate({a:.0f})">'
    if sorte == 0:    # jambe
        g += (f'<path d="M-7 0 H7 L6 44 L5 70 L16 74 L16 80 L-6 80 L-6 70 L-8 44 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>'
              f'<path d="M-6 40 Q0 44 6 40" fill="none" stroke="{MINE}" stroke-width="1.2"/>')
    elif sorte == 1:  # bras
        g += (f'<path d="M-6 0 H6 L5 50 L9 62 L4 70 L-4 70 L-6 60 L-5 50 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>'
              f'<path d="M-2 66 L-3 74 M2 66 L2 75" {ST} stroke-width="1.6"/>')
    elif sorte == 2:  # main
        g += (f'<path d="M-8 0 H8 L9 18 L12 30 M5 18 L6 34 M0 18 V36 M-5 18 L-6 33 M-8 14 L-14 24" fill="none" {ST} stroke-width="3.6"/>'
              f'<path d="M-8 0 H8 V20 H-8 Z" fill="{PAPIER}" {ST} stroke-width="1.6"/>')
    elif sorte == 3:  # pied
        g += f'<path d="M-6 0 H6 V24 L22 30 V36 H-6 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>'
    else:             # cœur de cire (pas d'organe : la forme des ex-voto, symétrique)
        g += f'<path d="M0 28 Q-16 14 -10 4 Q-4 -2 0 6 Q4 -2 10 4 Q16 14 0 28 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>'
    out.append(g + '</g>')
    return "".join(out)


def niche(x: int, saint: bool = True, lampe: bool = True) -> str:
    """Niche voûtée dans le mur de la crypte : un saint couché, drapé, sous une vitre embuée ;
    une plaque grattée sous la niche ; une petite lampe à huile devant."""
    out = [f'<path d="M{x} 800 V640 Q{x + 110} 580 {x + 220} 640 V800 Z" fill="{ENCRE}" {ST} stroke-width="3"/>',
           f'<path d="M{x - 12} 812 H{x + 232} V800 H{x - 12} Z" fill="url(#moellons)" {ST} stroke-width="2"/>']
    if saint:
        # le gisant : drapé en papier, mains jointes, visage de profil vers le haut (pas d'yeux)
        out.append(f'<path d="M{x + 30} 794 Q{x + 34} 760 {x + 70} 762 L{x + 190} 770 Q{x + 200} 784 {x + 196} 796 Z" fill="{PAPIER}" {ST} stroke-width="2"/>')
        out.append(f'<path d="M{x + 80} 768 Q{x + 86} 784 {x + 80} 796 M{x + 120} 768 Q{x + 128} 784 {x + 120} 796 M{x + 160} 770 Q{x + 166} 786 {x + 160} 796" fill="none" stroke="{MINE}" stroke-width="1.4"/>')
        out.append(f'<path d="M{x + 110} 764 L{x + 116} 748 L{x + 122} 764" fill="{PAPIER}" {ST} stroke-width="1.6"/>')
        out.append(f'<path d="M{x + 18} 790 Q{x + 14} 768 {x + 30} 762 Q{x + 44} 760 {x + 46} 776 L{x + 40} 792 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>')
        out.append(f'<path d="M{x + 18} 768 Q{x + 30} 752 {x + 44} 764" fill="none" stroke="{PAPIER}" stroke-width="5"/>')
    # la vitre : un rectangle à peine marqué, des traits de buée
    out.append(f'<rect x="{x + 10}" y="738" width="200" height="62" fill="none" stroke="{MINE}" stroke-width="2"/>')
    out.append(f'<path d="M{x + 30} 746 Q{x + 60} 742 {x + 90} 748 M{x + 120} 744 Q{x + 150} 740 {x + 180} 746" fill="none" stroke="{PAPIER}" stroke-width="1.4" stroke-dasharray="6 5"/>')
    # la plaque grattée : des lettres devenues rayures
    out.append(f'<rect x="{x + 70}" y="826" width="80" height="30" fill="{LAVIS}" {ST} stroke-width="1.8"/>')
    out.append(f'<path d="M{x + 78} 834 L{x + 142} 848 M{x + 80} 846 L{x + 140} 836 M{x + 84} 840 H{x + 136}" stroke="{PAPIER}" stroke-width="1.6"/>')
    if lampe:
        out.append(f'<path d="M{x + 100} {SOL} V880 H{x + 120} V{SOL} Z" fill="url(#h2)" {ST} stroke-width="1.6"/>'
                   f'<path d="M{x + 94} 880 Q{x + 110} 890 {x + 126} 880 Q{x + 120} 870 {x + 110} 870 Q{x + 100} 870 {x + 94} 880 Z" fill="{PAPIER}" {ST} stroke-width="1.6"/>'
                   f'<path d="M{x + 110} 870 Q{x + 104} 858 {x + 110} 848 Q{x + 116} 858 {x + 110} 870 Z" fill="{PAPIER}" {ST} stroke-width="1.2"/>')
    return "".join(out)


# --------------------------------------------------------------------------- les lieux
def porche() -> str:
    """La rue devant l'hôpital : ciel en papier, maisons basses à gauche, la façade de l'hôpital
    (pierre, hautes fenêtres grillagées, la cloche sans battant de la Tranchée-Mère au fronton),
    le tronc de l'aumône débordant de boutons, le perron, la grande porte ouverte."""
    w = 1920
    out = [f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>',
           f'<path d="M0 120 Q300 90 640 130 T1300 110 T1920 140" fill="none" stroke="{MINE}" stroke-width="2"/>',
           f'<path d="M0 200 Q400 170 820 210 T1920 190" fill="none" stroke="{MINE}" stroke-width="1.4"/>']
    # maisons basses de la rue, à gauche
    for x0, x1, m, fa in ((-40, 220, 560, 430), (230, 520, 600, 470)):
        out.append(f'<path d="M{x0} {SOL} V{m} L{(x0 + x1) / 2:.0f} {fa} L{x1} {m} V{SOL} Z" fill="{PAPIER}" {ST} stroke-width="3"/>')
        out.append(f'<path d="M{x0} {m} L{(x0 + x1) / 2:.0f} {fa} L{x1} {m} Z" fill="url(#tuiles)" {ST} stroke-width="2.4"/>')
        out.append(f'<rect x="{x0 + 60}" y="{m + 60}" width="54" height="80" fill="{ENCRE}"/>')
    # la façade de l'hôpital, de x 560 au bord droit
    out.append(f'<rect x="560" y="260" width="{w - 560}" height="{SOL - 260}" fill="url(#moellons)" {ST} stroke-width="3.4"/>')
    out.append(f'<path d="M540 260 H{w} V230 H540 Z" fill="url(#h1)" {ST} stroke-width="2.6"/>')
    out.append(f'<path d="M1060 230 L1260 120 L1460 230 Z" fill="{PAPIER}" {ST} stroke-width="3"/>')
    # au fronton, la cloche de la Tranchée-Mère, sans battant (rien ne sonne)
    out.append(f'<path d="M1236 200 Q1236 160 1260 156 Q1284 160 1284 200 L1290 208 H1230 Z" fill="url(#h2)" {ST} stroke-width="2.4"/>')
    out.append(f'<path d="M1240 202 Q1260 194 1280 202" fill="none" stroke="{PAPIER}" stroke-width="2"/>')
    # hautes fenêtres grillagées, aveugles
    for fx in (640, 860, 1700):
        out.append(f'<path d="M{fx} 640 V380 Q{fx + 50} 340 {fx + 100} 380 V640 Z" fill="{ENCRE}" {ST} stroke-width="3"/>')
        out.append(f'<path d="M{fx + 25} 366 V640 M{fx + 50} 358 V640 M{fx + 75} 366 V640 M{fx} 460 H{fx + 100} M{fx} 560 H{fx + 100}" stroke="{MINE}" stroke-width="3"/>')
        out.append(f'<rect x="{fx - 8}" y="640" width="116" height="12" fill="{PAPIER}" {ST} stroke-width="2"/>')
    # le tronc de l'aumône sur son poteau (porche_tronc, x 700) : couvercle soulevé, des boutons
    out.append(f'<path d="M690 {SOL} V770 H710 V{SOL} Z" fill="url(#h2)" {ST} stroke-width="2.4"/>')
    out.append(f'<rect x="652" y="700" width="96" height="74" fill="url(#vantail)" {ST} stroke-width="2.8"/>')
    out.append(f'<path d="M652 700 L664 676 H760 L748 700 Z" fill="url(#h1)" {ST} stroke-width="2.4"/>')
    out.append(f'<path d="M660 728 H740 M660 748 H740" {ST} stroke-width="2"/><rect x="692" y="712" width="16" height="10" fill="{ENCRE}"/>')
    r = rnd(404)
    for _ in range(26):
        bx, by = r.uniform(662, 742), r.uniform(686, 702)
        out.append(f'<circle cx="{bx:.0f}" cy="{by:.0f}" r="4" fill="{PAPIER}" {ST} stroke-width="1.2"/><circle cx="{bx:.0f}" cy="{by:.0f}" r="1" fill="{ENCRE}"/>')
    for bx in (636, 674, 768, 790):
        out.append(f'<circle cx="{bx}" cy="{SOL - 4}" r="4" fill="{PAPIER}" {ST} stroke-width="1.2"/>')
    # le perron de Maude (x 1150) : trois marches usées sous la grande arcade
    for k in range(3):
        out.append(f'<rect x="{1000 + k * 30}" y="{SOL - (k + 1) * 18}" width="{340 - k * 60}" height="18" fill="{PAPIER}" {ST} stroke-width="2.2"/>')
    out.append(f'<path d="M1030 {SOL - 54} V520 Q1150 420 1270 520 V{SOL - 54}" fill="none" {ST} stroke-width="4"/>')
    out.append(f'<path d="M1060 {SOL - 54} V530 Q1150 450 1240 530 V{SOL - 54} Z" fill="url(#h1)" {ST} stroke-width="2"/>')
    # la grande porte (VersSalle, 1520 à 1680), ouverte sur le noir, et une bassine à côté
    out.append(porte_ouverte(1520, 1680))
    out.append(f'<path d="M1400 {SOL} L1392 {SOL - 34} H1478 L1470 {SOL} Z" fill="url(#h2)" {ST} stroke-width="2.4"/>')
    out.append(f'<path d="M1396 {SOL - 30} Q1435 {SOL - 40} 1474 {SOL - 30}" fill="none" {ST} stroke-width="1.6"/>')
    # la rue pavée
    out.append(f'<rect y="{SOL}" width="{w}" height="{H - SOL}" fill="url(#paves)"/>')
    out.append(f'<path d="M0 {SOL} H{w}" {ST} stroke-width="3"/>')
    return "".join(out)


def salle() -> str:
    """La salle commune : une longue rangée de lits de fer, tous occupés ; hauts soupiraux ;
    la place de Fernand (son lit est dans son sprite) laissée libre autour de x 2100."""
    w = 3840
    out = [mur(w)]
    for x in range(260, w - 200, 520):
        out.append(soupirail(x))
    # entrée depuis le porche (x 200 : on arrive par cet escalier qui descend)
    out.append(porte_bois(60, 220))
    r = rnd(4401)
    # aucun lit devant une porte (lingerie 1360 à 1600 avec son vantail, fond 3400 à 3600)
    # ni à la place de Fernand (son sprite porte son lit, de x 2020 à 2200)
    libres = ((1340, 1600), (1990, 2230), (3380, 3600))
    xs = [x for x in range(300, w - 200, 240) if all(x + 200 < a or x > b for a, b in libres)]
    for x in xs:
        out.append(lit(x, numero_repeint=(x == 780), r=r))
    # la porte de la lingerie, toujours ouverte (x 1420 à 1580) : du linge blanc dans le noir
    linge = "".join(f'<rect x="{1440 + i * 38}" y="{700 + (i % 2) * 20}" width="30" height="{80 + (i % 3) * 20}" fill="{PAPIER}" {ST} stroke-width="1.2"/>' for i in range(3))
    out.append(porte_ouverte(1420, 1580, linge))
    # une table de chevet et une cuvette près de la place de Fernand
    out.append(f'<rect x="2290" y="{SOL - 70}" width="50" height="70" fill="url(#vantail)" {ST} stroke-width="2.2"/>')
    out.append(f'<path d="M2296 {SOL - 70} Q2315 {SOL - 82} 2334 {SOL - 70}" fill="{PAPIER}" {ST} stroke-width="1.8"/>')
    # la porte du fond, vers l'atelier (x 3420 à 3580)
    out.append(porte_bois(3420, 3580))
    return "".join(out)


def lingerie() -> str:
    """Rayonnages de draps pliés jusqu'à la voûte, et sur la grande table les draps cousus en
    forme de corps, épaules, bras, tête ronde (lingerie_draps, x 700)."""
    w = 1440
    out = [mur(w)]
    out.append(porte_bois(120, 280))
    for x0 in (330, 660):
        out.append(f'<rect x="{x0}" y="470" width="300" height="{SOL - 470}" fill="url(#h1)" {ST} stroke-width="3"/>')
        for y in range(530, SOL, 90):
            out.append(f'<rect x="{x0}" y="{y}" width="300" height="10" fill="{PAPIER}" {ST} stroke-width="2"/>')
            for k in range(5):
                out.append(f'<rect x="{x0 + 12 + k * 57}" y="{y - 46}" width="50" height="46" fill="{PAPIER}" {ST} stroke-width="1.6"/>'
                           f'<path d="M{x0 + 12 + k * 57} {y - 30} H{x0 + 62 + k * 57} M{x0 + 12 + k * 57} {y - 16} H{x0 + 62 + k * 57}" stroke="{MINE}" stroke-width="1"/>')
    # la table de coupe devant les rayonnages, et dessus, trois draps cousus en forme d'homme
    out.append(f'<rect x="520" y="{SOL - 120}" width="400" height="16" fill="url(#h1)" {ST} stroke-width="2.6"/>')
    out.append(f'<path d="M536 {SOL - 104} V{SOL} M904 {SOL - 104} V{SOL}" {ST} stroke-width="9"/>')
    for k in range(3):
        y = SOL - 128 - k * 14
        x = 560 + k * 10
        out.append(f'<path d="M{x} {y} Q{x + 4} {y - 22} {x + 24} {y - 24} Q{x + 44} {y - 22} {x + 46} {y - 8} L{x + 64} {y - 14} L{x + 110} {y - 22} '
                   f'L{x + 250} {y - 18} L{x + 320} {y - 10} L{x + 320} {y} Z" fill="{PAPIER}" {ST} stroke-width="2"/>')
        out.append(f'<path d="M{x + 60} {y - 12} L{x + 64} {y - 2} M{x + 110} {y - 20} L{x + 112} {y} M{x + 240} {y - 18} L{x + 240} {y}" stroke="{ENCRE}" stroke-width="1" stroke-dasharray="3 3"/>')
    # un mannequin de couturière, un mètre ruban (encre : rien de rouge), des ciseaux pendus
    out.append(f'<path d="M1300 {SOL} V780 M1270 {SOL} H1330 M1276 780 Q1270 700 1300 690 Q1330 700 1324 780 Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
    out.append(f'<path d="M1282 720 Q1300 740 1318 720" fill="none" {ST} stroke-width="1.4" stroke-dasharray="4 3"/>')
    out.append(porte_ouverte(1070, 1230))
    return "".join(out)


def atelier() -> str:
    """L'atelier d'Anselme, propre et presque vide : l'étagère de bocaux, la planche anatomique
    corrigée (encre), la table d'opération sous un drap, une lampe, la porte de l'escalier."""
    w = 1920
    out = [mur(w)]
    out.append(porte_bois(120, 280))
    # l'étagère des bocaux (x 550)
    out.append(f'<rect x="380" y="560" width="340" height="{SOL - 560}" fill="url(#h1)" {ST} stroke-width="3"/>')
    sortes = ("main", "coeur", "oreille", "autre", "coeur", "main", "autre", "oreille", "coeur", "autre", "main", "oreille")
    for rg, y in enumerate((660, 760, 860)):
        out.append(f'<rect x="380" y="{y}" width="340" height="10" fill="{PAPIER}" {ST} stroke-width="2"/>')
        for k in range(4):
            out.append(bocal(420 + k * 82, y, 70 - rg * 4, sortes[rg * 4 + k]))
    # la planche anatomique (x 850) : un homme ouvert comme un livre, flèches, légendes en traits
    out.append(f'<rect x="770" y="500" width="170" height="240" fill="{PAPIER}" {ST} stroke-width="3"/>')
    out.append(f'<path d="M855 530 Q840 532 840 550 Q842 566 855 568 Q868 566 870 550 Q870 532 855 530 Z M840 576 H870 L878 660 L866 720 H844 L832 660 Z" fill="none" {ST} stroke-width="1.8"/>')
    out.append(f'<path d="M832 600 L806 650 M878 600 L904 650" {ST} stroke-width="1.6"/>')
    out.append(f'<path d="M846 600 Q855 616 864 600 M846 640 H864" fill="none" stroke="{MINE}" stroke-width="1.2"/>')
    # le cœur barré et redessiné plus bas, à l'encre (le texte dit rouge : le rouge est réservé)
    out.append(f'<path d="M854 600 l6 6 M860 600 l-6 6" {ST} stroke-width="1.6"/><path d="M856 628 q-6 -6 0 -9 q6 3 0 9 Z" fill="{ENCRE}"/>')
    out.append(f'<path d="M870 612 Q890 614 886 626 L862 626" fill="none" {ST} stroke-width="1.4"/>')
    for y in (560, 590, 680, 710):
        out.append(f'<path d="M880 {y} H924 M786 {y + 10} H826" stroke="{MINE}" stroke-width="1.4"/>')
    # la table d'opération (x 1250), sous un drap blanc bien tiré, sangles de cuir
    out.append(f'<rect x="1080" y="{SOL - 150}" width="340" height="22" fill="{PAPIER}" {ST} stroke-width="2.6"/>')
    out.append(f'<path d="M1080 {SOL - 128} Q1250 {SOL - 116} 1420 {SOL - 128} V{SOL - 96} Q1250 {SOL - 84} 1080 {SOL - 96} Z" fill="{PAPIER}" {ST} stroke-width="2"/>')
    out.append(f'<path d="M1160 {SOL - 150} V{SOL - 92} M1340 {SOL - 150} V{SOL - 92}" stroke="{LAVIS}" stroke-width="5"/>')
    out.append(f'<path d="M1110 {SOL - 96} V{SOL} M1390 {SOL - 96} V{SOL} M1110 {SOL - 30} H1390" {ST} stroke-width="6"/>')
    # la lampe pendue au-dessus, éteinte, et le plateau d'instruments recouvert d'un linge
    out.append(f'<path d="M1250 {PLAFOND + 120} V560 M1210 600 Q1250 550 1290 600 Z" fill="url(#h2)" {ST} stroke-width="2.4"/>')
    out.append(f'<path d="M1460 {SOL} V{SOL - 120} M1440 {SOL - 120} H1530 V{SOL - 132} H1440 Z" fill="url(#h1)" {ST} stroke-width="2.4"/>')
    out.append(f'<path d="M1444 {SOL - 132} Q1486 {SOL - 150} 1526 {SOL - 132}" fill="{PAPIER}" {ST} stroke-width="1.8"/>')
    out.append(porte_bois(1620, 1780))
    return "".join(out)


def escalier() -> str:
    """L'escalier des ex-voto : le mur de pierre couvert de membres de cire pendus à des clous,
    plus nombreux que les marches ; la rampe de fer descend vers la crypte (porte x 700 à 860)."""
    w = 960
    out = [mur(w, pierre=True)]
    out.append(porte_bois(40, 200))
    # les marches peintes en biais dans le mur, et la rampe
    for k in range(12):
        x = 160 + k * 46
        y = 560 + k * 26
        out.append(f'<path d="M{x} {y} H{x + 46} V{y + 26}" fill="none" {ST} stroke-width="2.4"/>')
    out.append(f'<path d="M150 520 L700 830" {ST} stroke-width="5"/>')
    for k in range(10):
        out.append(f'<path d="M{170 + k * 52} {531 + k * 29} V{560 + k * 29}" {ST} stroke-width="2"/>')
    r = rnd(4404)
    for _ in range(64):
        x, y = r.uniform(40, w - 60), r.uniform(470, 760)
        if (690 < x < 870 or x < 220) and y > 560:
            continue
        out.append(ex_voto(x, y, r.randrange(5), r))
    out.append(porte_bois(700, 860))
    return "".join(out)


def crypte() -> str:
    """La crypte : les niches des saints couchés sous verre, les lampes à huile, les plaques
    grattées ; au pied d'une niche les ex-voto entassés ; l'escalier de service au fond."""
    w = 2880
    out = [mur(w, pierre=True)]
    out.append(porte_bois(40, 200))
    r = rnd(4405)
    for x in range(260, w - 560, 300):
        out.append(niche(x, saint=True, lampe=(x < 650 or x > 1600)))
    # au pied d'une niche (après l'entrée), le tas d'ex-voto : cire, chapelets, médailles
    for k in range(18):
        bx, by = r.uniform(560, 760), r.uniform(SOL - 30, SOL - 4)
        out.append(f'<ellipse cx="{bx:.0f}" cy="{by:.0f}" rx="{r.uniform(8, 16):.0f}" ry="5" fill="{PAPIER}" {ST} stroke-width="1.4"/>')
    out.append(f'<path d="M580 {SOL - 20} Q620 {SOL - 40} 660 {SOL - 18} Q700 {SOL - 36} 740 {SOL - 16}" fill="none" {ST} stroke-width="1.4" stroke-dasharray="2 4"/>')
    out.append(porte_bois(2520, 2680))
    return "".join(out)


def escalier_service() -> str:
    """L'escalier de service : moellons nus, une volée raide qui remonte d'un coup vers le jour
    de la porte latérale (passage x 670 à 830)."""
    w = 960
    out = [mur(w, pierre=True)]
    out.append(porte_bois(60, 220))
    for k in range(14):
        x = 300 + k * 30
        y = SOL - k * 34
        out.append(f'<path d="M{x} {y} V{y - 34} H{x + 30}" fill="none" {ST} stroke-width="2.6"/>')
    out.append(f'<path d="M300 {SOL} L720 {SOL - 476} V{SOL} Z" fill="url(#v1)" opacity=".5"/>')
    # en haut, le jour de la rue par la porte entrouverte
    out.append(f'<rect x="670" y="600" width="160" height="300" fill="{PAPIER}" {ST} stroke-width="3"/>')
    out.append(f'<path d="M670 600 L630 620 V{SOL + 8} L670 {SOL} Z" fill="url(#vantail)" {ST} stroke-width="3"/>')
    out.append(f'<path d="M670 {SOL} L840 {SOL - 40} M670 860 L820 600" stroke="{MINE}" stroke-width="1.4"/>')
    return "".join(out)


def rue_laterale() -> str:
    """La ruelle derrière l'hôpital : le mur aveugle, la petite porte (sortie x 300), une borne,
    puis la route qui quitte la ville vers la droite, sous un ciel bas."""
    w = 1920
    out = [f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>',
           f'<path d="M0 160 Q500 130 980 170 T1920 150" fill="none" stroke="{MINE}" stroke-width="2"/>']
    # le mur de l'hôpital sur la gauche, une petite porte basse
    out.append(f'<rect x="-20" y="300" width="900" height="{SOL - 300}" fill="url(#moellons)" {ST} stroke-width="3.4"/>')
    out.append(f'<path d="M-20 300 H900 V276 H-20 Z" fill="url(#h1)" {ST} stroke-width="2.4"/>')
    out.append(porte_bois(220, 380, 640))
    out.append(f'<path d="M260 600 Q300 570 340 600" fill="none" {ST} stroke-width="3"/>')
    # une niche au-dessus de la porte, vide (pas de cloche)
    out.append(f'<path d="M280 560 V500 Q300 480 320 500 V560 Z" fill="{ENCRE}" {ST} stroke-width="2"/>')
    # le bout du mur et la campagne : la route qui part, un poteau, des champs
    out.append(f'<path d="M900 {SOL} Q1300 820 {w} 780" fill="none" stroke="{MINE}" stroke-width="2"/>')
    out.append(f'<path d="M900 640 Q1300 610 {w} 620" fill="none" stroke="{LAVIS}" stroke-width="3"/>')
    out.append(f'<path d="M1500 {SOL} V700 M1490 720 H1540" {ST} stroke-width="4"/>')
    out.append(f'<rect x="1000" y="{SOL - 60}" width="40" height="60" fill="url(#moellons)" {ST} stroke-width="2"/>')
    out.append(f'<rect y="{SOL}" width="{w}" height="{H - SOL}" fill="url(#paves)"/>')
    out.append(f'<path d="M0 {SOL} H{w}" {ST} stroke-width="3"/>')
    return "".join(out)


def ecrire(nom: str, contenu: str, largeur: int) -> int:
    DST.mkdir(parents=True, exist_ok=True)
    n = math.ceil(largeur / TUILE)
    for i in range(n):
        x0 = i * TUILE
        w = min(TUILE, largeur - x0)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="{x0} 0 {w} {H}">'
               f'{DEFS}{contenu}</svg>\n')
        (DST / f"env_e4_plan3_{nom}_{i + 1:02d}.svg").write_text(svg, encoding="utf-8")
    return n


LIEUX = {"porche": (porche, 1920), "salle": (salle, 3840), "lingerie": (lingerie, 1440),
         "atelier": (atelier, 1920), "escalier": (escalier, 960), "crypte": (crypte, 2880),
         "escalier-service": (escalier_service, 960), "rue-laterale": (rue_laterale, 1920)}


def main() -> None:
    total = sum(ecrire(nom, fn(), w) for nom, (fn, w) in LIEUX.items())
    print(f"{total} tuiles de lieux dans art/src/env/e4")


if __name__ == "__main__":
    main()
