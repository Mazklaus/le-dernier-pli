#!/usr/bin/env python3
"""Soldats de fond de la surface de l'étape 1 (#129 : on entendait des voix sans voir personne).

Trois calques assis, sans interaction, posés par DecorE1 derrière Tobie, au droit des repères de
voix forts (MixageSon.GAIN_VOIX_REPERES) :
  fx_soldats-pons-billard  x 1100 : Pons et Billard sur une caisse, qui parlent de leur permission
                                    (détail e1_detail_boyau_chuchoteurs)
  fx_soldats-boyau         x 1880 : l'un dort roulé dans sa capote, l'autre graisse son fusil
  fx_soldats-carrefour     x 4900 : trois hommes autour d'une gamelle, à gauche de la croix

Même dessin que les personnages de l'étape 1 (tools/donnees/pnj_e1.svgfrag) : corps ronds, têtes
rondes, calots, bandes molletières, à la même échelle (0,845, sol du calque à y = hauteur - 4).
Repère source : sol à y 405.

Usage : python3 tools/gen_fx_soldats_e1.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FX = ROOT / "art" / "src" / "fx"
SOURCE = ROOT / "tools" / "donnees" / "pnj_e1.svgfrag"
ECHELLE = 0.845
SOL = 405
ENCRE, PAPIER, LAVIS = "#15130F", "#E8E5DA", "#4A463D"
ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'


def defs() -> str:
    s = SOURCE.read_text(encoding="utf-8")
    pats = re.findall(r'<pattern id="(?:hach-1|hach-2|molletiere)".*?</pattern>', s, re.S)
    return "<defs>" + "".join(pats) + "</defs>"


def tete(x: float, y: float, f: int, yeux: str = "ouverts", calot: bool = True) -> str:
    """Tête ronde (r 26) tournée vers f (+1 droite, -1 gauche) ; yeux ouverts, clos ou baissés."""
    out = [f'<circle cx="{x}" cy="{y}" r="26" fill="{PAPIER}" {ST} stroke-width="2.2"/>']
    ex = x + 6 * f
    if yeux == "ouverts":
        out.append(f'<path d="M{ex - 11} {y - 2} h6 M{ex + 5} {y - 2} h6" fill="none" {ST} stroke-width="2"/>')
    elif yeux == "clos":
        out.append(f'<path d="M{ex - 11} {y} q3 3 6 0 M{ex + 5} {y} q3 3 6 0" fill="none" {ST} stroke-width="1.6"/>')
    else:  # baissés, vers les mains
        out.append(f'<path d="M{ex - 10} {y + 2} h5 M{ex + 5} {y + 2} h5" fill="none" {ST} stroke-width="2"/>'
                   f'<path d="M{ex - 11} {y - 4} l6 1 M{ex + 5} {y - 3} l6 -1" fill="none" {ST} stroke-width="1.2"/>')
    if calot:
        out.append(f'<path d="M{x - 26} {y - 12} Q{x - 20} {y - 34} {x + 2} {y - 34} Q{x + 22} {y - 32} {x + 28} {y - 18} '
                   f'L{x + 28} {y - 10} Q{x} {y - 24} {x - 26} {y - 6} Z" fill="url(#hach-2)" {ST} stroke-width="2.2"/>')
    return "".join(out)


def assis(x: float, siege: float, f: int, bras: str, tete_y: float = 0, yeux: str = "ouverts",
          bouche: str = "") -> str:
    """Soldat assis sur un siège à la hauteur siege (y du dessus), hanche en x, tourné vers f."""
    ty = siege - 140 + tete_y
    genou = x + 62 * f
    out = [
        # jambes : cuisse à plat, tibia jusqu'au sol, brodequin
        f'<path d="M{x} {siege - 22} L{genou} {siege - 26} L{genou + 4 * f} {siege - 4} L{x} {siege + 2} Z" fill="url(#hach-1)" {ST} stroke-width="2.2"/>',
        f'<path d="M{genou - 12 * f} {siege - 14} L{genou - 10 * f} {SOL - 20} L{genou + 12 * f} {SOL - 20} L{genou + 12 * f} {siege - 14} Z" fill="url(#molletiere)" {ST} stroke-width="2.2"/>',
        f'<path d="M{genou - 12 * f} {SOL - 22} L{genou - 14 * f} {SOL} L{genou + 26 * f} {SOL} L{genou + 18 * f} {SOL - 22} Z" fill="{ENCRE}" {ST} stroke-width="1.6"/>',
        # corps rond, un peu voûté
        f'<ellipse cx="{x + 4 * f}" cy="{siege - 62}" rx="44" ry="52" fill="url(#hach-1)" {ST} stroke-width="2.6"/>',
        f'<path d="M{x + 4 * f} {siege - 112} L{x + 4 * f} {siege - 12}" {ST} stroke-width="1.2"/>',
    ]
    out.append(tete(x + 10 * f, ty, f, yeux))
    if bouche == "parle":
        out.append(f'<path d="M{x + 18 * f} {ty + 14} q{5 * f} 3 {10 * f} 0" fill="none" {ST} stroke-width="1.8"/>'
                   f'<path d="M{x + 44 * f} {ty + 6} q{6 * f} 4 {4 * f} 10 M{x + 50 * f} {ty} q{8 * f} 8 {4 * f} 18" fill="none" {ST} stroke-width="1.1"/>')
    elif bouche == "sourit":
        out.append(f'<path d="M{x + 14 * f} {ty + 12} q{6 * f} 5 {12 * f} 0" fill="none" {ST} stroke-width="1.6"/>')
    # bras
    if bras == "genoux":       # mains jointes sur les genoux
        out.append(f'<path d="M{x + 30 * f} {siege - 96} Q{x + 52 * f} {siege - 60} {genou - 6 * f} {siege - 34} L{genou - 18 * f} {siege - 24} Q{x + 36 * f} {siege - 50} {x + 18 * f} {siege - 86} Z" fill="url(#hach-1)" {ST} stroke-width="2.2"/>'
                   f'<circle cx="{genou - 10 * f}" cy="{siege - 30}" r="9" fill="{PAPIER}" {ST} stroke-width="2"/>')
    elif bras == "geste":      # la main levée, il raconte
        out.append(f'<path d="M{x + 30 * f} {siege - 96} Q{x + 66 * f} {siege - 100} {x + 76 * f} {siege - 130} L{x + 64 * f} {siege - 136} Q{x + 56 * f} {siege - 112} {x + 22 * f} {siege - 84} Z" fill="url(#hach-1)" {ST} stroke-width="2.2"/>'
                   f'<circle cx="{x + 72 * f}" cy="{siege - 140}" r="9" fill="{PAPIER}" {ST} stroke-width="2"/>')
    elif bras == "gamelle":    # une gamelle tenue sur les genoux, cuillère
        out.append(f'<path d="M{x + 30 * f} {siege - 96} Q{x + 50 * f} {siege - 66} {x + 50 * f} {siege - 44} L{x + 36 * f} {siege - 44} Q{x + 36 * f} {siege - 66} {x + 18 * f} {siege - 86} Z" fill="url(#hach-1)" {ST} stroke-width="2.2"/>'
                   f'<path d="M{x + 30 * f} {siege - 40} Q{x + 50 * f} {siege - 22} {x + 74 * f} {siege - 40} Z" fill="{PAPIER}" {ST} stroke-width="2.2"/>'
                   f'<path d="M{x + 46 * f} {siege - 44} L{x + 66 * f} {siege - 74}" {ST} stroke-width="2.4"/>'
                   f'<circle cx="{x + 46 * f}" cy="{siege - 46}" r="8" fill="{PAPIER}" {ST} stroke-width="2"/>')
    elif bras == "fusil":      # le fusil en travers des genoux, le chiffon
        out.append(f'<path d="M{x - 70 * f} {siege - 34} L{x + 150 * f} {siege - 52}" {ST} stroke-width="6"/>'
                   f'<path d="M{x - 70 * f} {siege - 34} L{x - 84 * f} {siege - 20} L{x - 66 * f} {siege - 14} L{x - 54 * f} {siege - 30} Z" fill="{ENCRE}" {ST} stroke-width="1.6"/>'
                   f'<path d="M{x + 30 * f} {siege - 96} Q{x + 58 * f} {siege - 70} {x + 84 * f} {siege - 54} L{x + 76 * f} {siege - 44} Q{x + 48 * f} {siege - 58} {x + 18 * f} {siege - 86} Z" fill="url(#hach-1)" {ST} stroke-width="2.2"/>'
                   f'<path d="M{x + 72 * f} {siege - 62} q{10 * f} -6 {22 * f} 0 q{-4 * f} 10 {-20 * f} 8 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>')
    return "".join(out)


def caisse(x0: float, x1: float, haut: float) -> str:
    return (f'<rect x="{x0}" y="{haut}" width="{x1 - x0}" height="{SOL - haut}" fill="url(#hach-1)" {ST} stroke-width="2.4"/>'
            f'<path d="M{x0} {haut} L{x1} {SOL} M{x0} {(haut + SOL) / 2} H{x1}" {ST} stroke-width="1.6"/>')


def dormeur(x: float, f: int) -> str:
    """Roulé dans sa capote contre le parados, assis par terre, tête tombée sur l'épaule, calot sur
    les yeux ; les brodequins dépassent."""
    return (f'<path d="M{x - 60 * f} {SOL} Q{x - 70 * f} {SOL - 120} {x - 20 * f} {SOL - 150} Q{x + 30 * f} {SOL - 160} {x + 50 * f} {SOL - 110} '
            f'Q{x + 80 * f} {SOL - 40} {x + 110 * f} {SOL - 6} L{x + 110 * f} {SOL} Z" fill="url(#hach-2)" {ST} stroke-width="2.6"/>'
            f'<path d="M{x - 30 * f} {SOL - 130} Q{x + 10 * f} {SOL - 70} {x + 70 * f} {SOL - 30} M{x - 50 * f} {SOL - 60} Q{x} {SOL - 40} {x + 40 * f} {SOL - 10}" fill="none" {ST} stroke-width="1.4"/>'
            f'<path d="M{x + 104 * f} {SOL - 22} L{x + 108 * f} {SOL} L{x + 140 * f} {SOL} L{x + 132 * f} {SOL - 18} Z" fill="{ENCRE}" {ST} stroke-width="1.6"/>'
            + tete(x - 4 * f, SOL - 170, f, "clos", calot=False)
            + f'<path d="M{x - 32 * f} {SOL - 178} Q{x - 26 * f} {SOL - 204} {x - 2 * f} {SOL - 204} Q{x + 22 * f} {SOL - 200} {x + 26 * f} {SOL - 180} '
            f'L{x + 26 * f} {SOL - 166} Q{x} {SOL - 186} {x - 32 * f} {SOL - 164} Z" fill="url(#hach-2)" {ST} stroke-width="2.2"/>'
            f'<path d="M{x + 30 * f} {SOL - 196} q{6 * f} -8 {14 * f} -6 M{x + 40 * f} {SOL - 208} q{6 * f} -6 {12 * f} -4" fill="none" {ST} stroke-width="1.1"/>')


# respiration : étirement vertical depuis le sol, comme les personnages (3 px au plus)
SOUFFLE = (0.0, 0.004, 0.008, 0.004)


def calque(nom: str, largeur: int, contenu: str) -> None:
    """Planche de 4 images côte à côte (respiration en boucle, DecorE1 la joue lentement).
    Traits en lavis plutôt qu'en encre : ce sont des figurants, ils ne doivent jamais se confondre
    avec les personnages à qui l'on parle."""
    h = 320
    dy = (h - 4) - SOL * ECHELLE
    contenu = contenu.replace(f'stroke="{ENCRE}"', f'stroke="{LAVIS}"').replace(f'fill="{ENCRE}"', f'fill="{LAVIS}"')
    d = defs().replace(f'stroke="{ENCRE}"', f'stroke="{LAVIS}"').replace('stroke="#15130F"', f'stroke="{LAVIS}"')
    images = "".join(
        f'<g transform="translate({k * largeur} {dy:.2f}) scale({ECHELLE}) translate(0 {SOL}) scale(1 {1 + e}) translate(0 {-SOL})">{contenu}</g>'
        for k, e in enumerate(SOUFFLE))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{largeur * len(SOUFFLE)}" height="{h}" '
           f'viewBox="0 0 {largeur * len(SOUFFLE)} {h}">{d}{images}</svg>\n')
    (FX / f"{nom}.svg").write_text(svg, encoding="utf-8")


def main() -> None:
    FX.mkdir(parents=True, exist_ok=True)
    # Pons (raconte, la main levée) et Billard (écoute, sourit), face à face sur une caisse
    calque("fx_soldats-pons-billard", 400,
           caisse(110, 370, 330) + assis(170, 330, 1, "geste", bouche="parle")
           + assis(310, 330, -1, "genoux", tete_y=4, bouche="sourit"))
    # au boyau : un dormeur contre le parados, un homme qui graisse son fusil sur une caisse
    calque("fx_soldats-boyau", 440,
           dormeur(110, 1) + caisse(290, 420, 336) + assis(360, 336, -1, "fusil", tete_y=6, yeux="baisses"))
    # au carrefour : trois hommes autour d'une gamelle posée sur une caisse
    calque("fx_soldats-carrefour", 520,
           caisse(60, 200, 336) + assis(130, 336, 1, "gamelle", yeux="baisses")
           + caisse(250, 330, 360) + f'<path d="M262 360 Q290 340 318 360 Z" fill="{PAPIER}" {ST} stroke-width="2.2"/>'
           + f'<path d="M290 346 q-6 -14 0 -26 M300 344 q6 -12 0 -22" fill="none" stroke="{LAVIS}" stroke-width="1.6" stroke-dasharray="3 4"/>'
           + caisse(380, 560, 336) + assis(420, 336, -1, "geste", bouche="parle")
           + assis(520, 336, -1, "genoux", tete_y=2))
    print("3 calques fx_soldats-* dans art/src/fx/")


if __name__ == "__main__":
    main()
