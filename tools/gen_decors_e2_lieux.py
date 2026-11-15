#!/usr/bin/env python3
"""Génère le fond du seul lieu de l'étape 2 : le vieux boyau sous le poste de Brisse (détour).

art/src/env/e2/env_e2_plan3_boyau-detour_01.svg, repère local de
scenes/etapes/etape_02/lieux/boyau_detour.tscn : sol à y 900, plafond de collision de 330 à 450,
sortie vers le poste aval à x 1700 (passage de 160 x 300). Tobie arrive par l'échelle du poste.

Texte (e2_poste, ~ boyau) : « Il sent la terre mouillée et la bougie froide. Le plafond tient
avec des planches et des prières. » Tobie a allumé sa lampe : la galerie est sous une simple
hachure uniforme, sans anneau fixe (la lampe le suit, voir la vieille sape de l'étape 1).
Mêmes pièces que les sapes de l'étape 1 (tools/gen_decors_e1_lieux.py), en plus vieux et mouillé.

Usage : python3 tools/gen_decors_e2_lieux.py
"""
from __future__ import annotations

from gen_decors_e1_lieux import (BAS_PLAFOND, DEFS, ENCRE, H, LAVIS, MINE, PAPIER, PLAFOND, SOL, ST,
                                 escalier, etai)
from gen_decors_e1_surface import rnd
from gen_decors_e2_surface import DST, fil

W = 1920


def bougie_froide(x: int, y: int, h: int) -> str:
    """Bout de bougie éteinte, la cire coulée sur la planche, mèche noire."""
    top = y - h
    return (f'<path d="M{x - 6} {y} V{top} H{x + 6} V{y} Z" fill="{PAPIER}" {ST} stroke-width="2"/>'
            f'<path d="M{x - 6} {top + 6} q-4 8 -2 16 M{x + 6} {top + 4} q5 10 2 {h - 6}" {ST} stroke-width="1.6"/>'
            f'<path d="M{x - 12} {y} Q{x} {y - 6} {x + 12} {y}" fill="{PAPIER}" {ST} stroke-width="1.6"/>'
            f'<path d="M{x} {top} q2 -6 -1 -10" {ST} stroke-width="2"/>')


def priere(x: int, y: int, ang: float) -> str:
    """Bout de papier plié, cloué à un étai : une prière (texte en traits illisibles)."""
    return (f'<g transform="rotate({ang:.0f} {x} {y})">'
            f'<rect x="{x - 14}" y="{y}" width="28" height="36" fill="{PAPIER}" {ST} stroke-width="2.2"/>'
            f'<path d="M{x - 9} {y + 11} H{x + 8} M{x - 9} {y + 18} H{x + 5} M{x - 9} {y + 25} H{x + 8}" {ST} stroke-width="1.1"/>'
            f'<circle cx="{x}" cy="{y + 4}" r="2" fill="{ENCRE}"/></g>')


def boyau_detour() -> str:
    r = rnd(21)
    out = [f'<rect width="{W}" height="{H}" fill="url(#terre)"/>',
           f'<rect width="{W}" height="{PLAFOND}" fill="{LAVIS}"/>',
           f'<rect y="{BAS_PLAFOND}" width="{W}" height="{SOL - BAS_PLAFOND}" fill="url(#terre)" {ST} stroke-width="3"/>']
    # coffrage ancien : planches inégales, plusieurs gauchies, des trous où la terre suinte
    x = 0
    while x < W:
        lg = r.randint(140, 300)
        for y in range(470, SOL - 30, 46):
            if r.random() < .72:
                ang = r.uniform(-2.5, 2.5)
                out.append(f'<rect x="{x}" y="{y}" width="{lg}" height="40" fill="{PAPIER}" {ST} stroke-width="2.2" '
                           f'transform="rotate({ang:.1f} {x + lg // 2} {y + 20})"/>')
                out.append(f'<path d="M{x + 12} {y + 14} H{x + lg // 2}" stroke="{MINE}" stroke-width="1.3"/>')
        x += lg + r.randint(0, 30)
    # plafond : planches de travers, l'une cassée qui pend
    out.append(f'<rect y="{PLAFOND}" width="{W}" height="{BAS_PLAFOND - PLAFOND - 30}" fill="url(#h2)" {ST} stroke-width="3"/>')
    x = 0
    while x < W:
        lg = r.randint(160, 280)
        dy = r.randint(-4, 8)
        out.append(f'<rect x="{x}" y="{BAS_PLAFOND - 40 + dy}" width="{lg}" height="30" fill="url(#h1)" {ST} stroke-width="2.6"/>')
        x += lg + r.randint(10, 40)
    out.append(f'<path d="M1040 {BAS_PLAFOND - 12} L1180 {BAS_PLAFOND + 70} L1172 {BAS_PLAFOND + 84} L1030 {BAS_PLAFOND + 4} Z" fill="url(#h1)" {ST} stroke-width="2.6"/>')
    # gouttes et filets d'eau
    for xg in range(130, W, 210):
        lg = r.randint(30, 90)
        out.append(f'<path d="M{xg} {BAS_PLAFOND - 8} q3 {lg // 2} 0 {lg}" {ST} stroke-width="1.4"/>')
        out.append(f'<path d="M{xg} {BAS_PLAFOND + lg + 10} q-4 6 0 10 q4 -4 0 -10 Z" fill="{PAPIER}" {ST} stroke-width="1.4"/>')
    # étais, chacun avec ses prières clouées
    for xe, pen in ((220, 0), (520, .04), (860, -.05), (1240, .06), (1520, -.03), (1880, 0)):
        out.append(etai(xe, r, pen))
        for k in range(r.randint(1, 3)):
            out.append(priere(xe + r.randint(-8, 8), 520 + k * 70 + r.randint(0, 20), r.uniform(-14, 14)))
    # l'échelle du poste par où Tobie est descendu (à gauche, hors passage)
    out.append(f'<rect x="60" y="0" width="120" height="{SOL}" fill="{ENCRE}"/>')
    out.append(f'<path d="M80 0 V{SOL} M160 0 V{SOL}" stroke="{PAPIER}" stroke-width="7"/>')
    for y in range(40, SOL, 64):
        out.append(f'<path d="M80 {y} H160" stroke="{PAPIER}" stroke-width="5"/>')
    # rebord taillé dans la terre : les bougies froides (« la bougie froide »)
    out.append(f'<path d="M640 720 H900" {ST} stroke-width="8"/>')
    for bx, bh in ((670, 18), (712, 30), (760, 12), (820, 24), (870, 16)):
        out.append(bougie_froide(bx, 716, bh))
    # sortie vers le poste aval
    out.append(escalier(1700, vers_droite=True))
    # sol : caillebotis pourri, flaques en papier
    out.append(f'<rect y="{SOL}" width="{W}" height="{H - SOL}" fill="url(#terre)" {ST} stroke-width="3"/>')
    for xc in range(0, W, 36):
        if r.random() < .6:
            out.append(f'<path d="M{xc + 4} {SOL + 2} V{SOL + 34 + r.randint(-6, 4)}" {ST} stroke-width="2"/>')
    out.append(f'<path d="M0 {SOL + 36} H{W}" {ST} stroke-width="2.4" stroke-dasharray="120 40"/>')
    for fx_, rx in ((420, 90), (1010, 140), (1420, 70)):
        out.append(f'<ellipse cx="{fx_}" cy="{SOL + 22}" rx="{rx}" ry="10" fill="{PAPIER}" {ST} stroke-width="2"/>')
        out.append(f'<path d="M{fx_ - rx // 2} {SOL + 20} H{fx_ + rx // 3}" stroke="{MINE}" stroke-width="1.4"/>')
    # la lampe allumée de Tobie : simple hachure uniforme, échelle et sortie comprises
    out.append(f'<rect width="{W}" height="{H}" fill="url(#v1)"/>')
    return "".join(out)


def ceinture_fermee() -> str:
    """Calque du Verrou de chaque ceinture de barbelés (CeintureUne, CeintureDeux) : la chicane
    peinte dans le plan 3 est barrée par un piquet en X, trois brins tendus et un rouleau de
    concertina. Calque de 180 x 320 centré sur le Verrou (y 750) : le sol (y 900) est à 310, les
    piquets peints de part et d'autre (xc ± 70) à x 20 et 160. Il part avec le Verrou une fois la
    ceinture passée (e2_barbeles) : reste la chicane ouverte et son fil arraché, déjà peints."""
    w, h = 180, 320
    sol = 310
    out = [f'<path d="M68 {sol} L108 {sol - 176} M112 {sol} L72 {sol - 176}" stroke="{ENCRE}" stroke-width="7"/>']
    for k, dy in enumerate((60, 110, 155)):
        out.append(fil(20, 90, sol - dy, 7 + k))
        out.append(fil(90, 160, sol - dy, 17 + k))
    # rouleau de concertina posé au pied, en travers de la chicane
    for k in range(7):
        cx = 30 + k * 20
        out.append(f'<ellipse cx="{cx}" cy="{sol - 26}" rx="16" ry="24" fill="none" stroke="{ENCRE}" stroke-width="1.6"/>')
    out.append(f'<path d="M14 {sol - 26} H166" stroke="{ENCRE}" stroke-width="1.2" stroke-dasharray="5 6"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{"".join(out)}</svg>\n'


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'{DEFS}{boyau_detour()}</svg>\n')
    (DST / "env_e2_plan3_boyau-detour_01.svg").write_text(svg, encoding="utf-8")
    fx = DST.parent.parent / "fx"
    (fx / "fx_ceinture-fermee.svg").write_text(ceinture_fermee(), encoding="utf-8")
    print("1 tuile dans art/src/env/e2/ + fx_ceinture-fermee")


if __name__ == "__main__":
    main()
