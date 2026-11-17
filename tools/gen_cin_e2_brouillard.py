#!/usr/bin/env python3
"""Génère les planches de la cinématique e2_brouillard_dechire (lot 2, planche validée par le GD
le 17/11) : au début de e2_cantique, le brouillard roule, se déchire d'un coup sur la souche
brûlée ; très loin, un village et son clocher vide.

  cin_e2-brouillard-souche   le fond de P1 et P2, 1920 x 1080 : la terre retournée, l'horizon
                             bas, la souche brûlée au premier plan (même dessin qu'en jeu) ;
  cin_e2-brouillard-brume    7 images de brouillard en 960 x 540 (affichées ×2, la brume
                             n'a pas besoin de plus), en grille 4 x 2 : 0 à 2 il roule, plein cadre,
                             opaque ; 3 à 6 il se déchire autour de la souche, le trou grandit
                             jusqu'à ne laisser que des lambeaux dans les coins ;
  cin_e2-brouillard-village  P3 : très loin, le village, le clocher et sa baie vide (on voit le
                             ciel au travers : aucune cloche), une dernière bande de brume.

Aucun rouge.

Usage : python3 tools/gen_cin_e2_brouillard.py
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from gen_cin_epilogues import DEFS_CIN
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER

DST = Path(__file__).resolve().parent.parent / "art" / "src" / "cin"
W, H = 1920, 1080
BW, BH = 960, 540               # une image de brume (affichée ×2)
ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
CLAIR = "#D3CFC2"
HORIZON = 640
SOUCHE = (820, 980)             # pied de la souche, dans le fond
CENTRE_TROU = (SOUCHE[0] / 2, 300)  # dans l'image de brume (demi-échelle)
RAYONS = [0, 0, 0, 60, 150, 250, 380]
COLONNES = 4                    # grille 4 x 2 (au plus 4096 px de large)
CLOCHER = (1180, 700)           # pied du clocher, dans le plan du village


def svg(contenu: str, w: int = W, h: int = H) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{DEFS_CIN}{contenu}</svg>\n')


def souche_fond() -> str:
    r = random.Random(2301)
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>',
         f'<path d="M0 {HORIZON} Q500 {HORIZON - 12} 960 {HORIZON + 2} T{W} {HORIZON - 4} V{H} H0 Z" fill="{CLAIR}"/>',
         f'<path d="M0 {HORIZON + 160} Q600 {HORIZON + 130} 1200 {HORIZON + 170} T{W} {HORIZON + 150} V{H} H0 Z" fill="{MINE}"/>']
    # les piquets lointains, le fil
    for x in range(40, W, 170):
        hx = x + r.uniform(-30, 30)
        o.append(f'<path d="M{hx:.0f} {HORIZON + 2} l{r.uniform(-6, 6):.0f} -{r.uniform(30, 56):.0f}" stroke="{MINE}" stroke-width="5" stroke-linecap="round"/>')
    # les sillons et les trous de la terre retournée
    for _ in range(30):
        x, y = r.uniform(0, W), r.uniform(HORIZON + 20, HORIZON + 150)
        o.append(f'<path d="M{x:.0f} {y:.0f} q{r.uniform(20, 60):.0f} -6 {r.uniform(70, 160):.0f} 0" fill="none" stroke="{MINE}" stroke-width="3"/>')
    for _ in range(40):
        x, y = r.uniform(0, W), r.uniform(HORIZON + 180, H)
        o.append(f'<path d="M{x:.0f} {y:.0f} q{r.uniform(30, 80):.0f} -10 {r.uniform(90, 220):.0f} 0" fill="none" stroke="{LAVIS}" stroke-width="4"/>')
    for cx, cy, rx in ((300, HORIZON + 90, 120), (1500, HORIZON + 70, 90), (1640, HORIZON + 260, 200)):
        o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{rx * .22:.0f}" fill="{LAVIS}" {ST} stroke-width="4"/>')
    # la souche : le dessin du décor (souche du cantique), agrandi ×1,6
    sx, sy = SOUCHE
    e = 1.6
    def p(x: float, y: float) -> str:
        return f"{sx + x * e:.0f} {sy + (y - 900) * e:.0f}"
    o.append(f'<path d="M{p(-70, 900)} Q{p(-54, 860)} {p(-48, 700)} L{p(-40, 520)} L{p(-18, 470)} L{p(-4, 498)} L{p(10, 452)} '
             f'L{p(30, 506)} L{p(44, 640)} Q{p(52, 860)} {p(78, 900)} Z" fill="{ENCRE}" stroke="{ENCRE}" stroke-width="5"/>')
    o.append(f'<path d="M{p(-40, 520)} L{p(-90, 470)} M{p(36, 580)} L{p(92, 540)} L{p(110, 548)}" stroke="{ENCRE}" stroke-width="14" fill="none" stroke-linecap="round"/>')
    # les racines, le bois fendu, en papier
    o.append(f'<path d="M{p(-70, 900)} q-40 10 -70 6 M{p(78, 900)} q50 4 80 14" stroke="{ENCRE}" stroke-width="12" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="M{p(-10, 860)} L{p(-6, 620)} M{p(18, 850)} L{p(22, 700)}" stroke="{LAVIS}" stroke-width="4"/>')
    return "".join(o)


def volutes(r: random.Random, phase: int, y0: float, y1: float, rangs: int) -> str:
    """Les rouleaux de brume : des rangées de bosses cernées de mine, qui glissent d'une image
    à l'autre (une rangée sur deux dans l'autre sens)."""
    o = []
    for i in range(rangs):
        y = y0 + (y1 - y0) * i / max(rangs - 1, 1) + r.uniform(-10, 10)
        sens = 1 if i % 2 == 0 else -1
        pas = r.uniform(110, 170)
        decal = r.uniform(0, pas) + sens * phase * pas / 3
        x = -pas * 2 + (decal % pas)
        teinte = PAPIER if i % 2 == 0 else CLAIR
        d = f"M{-200} {BH + 20} L{-200} {y:.0f}"
        bosses = []
        while x < BW + pas * 2:
            h = r.uniform(.28, .46) * pas
            bosses.append((x, h))
            x += pas
        for bx, h in bosses:
            d += f" Q{bx + pas / 2:.0f} {y - 2 * h:.0f} {bx + pas:.0f} {y:.0f}"
        d += f" L{BW + 200} {BH + 20} Z"
        o.append(f'<path d="{d}" fill="{teinte}"/>')
        for bx, h in bosses:
            o.append(f'<path d="M{bx + pas * .1:.0f} {y - h * .6:.0f} Q{bx + pas / 2:.0f} {y - 2 * h:.0f} {bx + pas * .9:.0f} {y - h * .6:.0f}" '
                     f'fill="none" stroke="{MINE}" stroke-width="2.5" stroke-linecap="round"/>')
            if r.random() < .35:
                o.append(f'<path d="M{bx + pas * .4:.0f} {y - h * .9:.0f} q{pas * .12:.0f} -14 {pas * .26:.0f} -2" fill="none" stroke="{MINE}" stroke-width="2" stroke-linecap="round"/>')
    return "".join(o)


def trou(rayon: float, graine: int) -> tuple[str, list[tuple[float, float]]]:
    """Le contour déchiré du trou dans la brume (sens inverse, pour l'evenodd)."""
    r = random.Random(graine)
    cx, cy = CENTRE_TROU
    pts = []
    n = 34
    for i in range(n):
        a = -2 * math.pi * i / n
        k = 1 + r.uniform(-.22, .22) + (.18 if i % 3 == 0 else 0)
        pts.append((cx + rayon * 1.5 * k * math.cos(a), cy + rayon * k * math.sin(a)))
    d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts) + " Z"
    return d, pts


def brume(k: int) -> str:
    r = random.Random(2302)
    phase = k if k < 3 else 3 + (k - 3) // 2
    contenu = f'<rect x="-10" y="-10" width="{BW + 20}" height="{BH + 20}" fill="{PAPIER}"/>' + volutes(r, phase, 40, BH + 30, 8)
    rayon = RAYONS[k]
    if rayon <= 0:
        return contenu
    d, pts = trou(rayon, 2303 + k)
    # la brume découpée : on la garde hors du trou (masque), le bord déchiré cerné de mine
    masque = (f'<mask id="m{k}"><rect x="-10" y="-10" width="{BW + 20}" height="{BH + 20}" fill="#fff"/>'
              f'<path d="{d}" fill="#000"/></mask>')
    o = [f'<defs>{masque}</defs><g mask="url(#m{k})">{contenu}</g>']
    # des lambeaux qui flottent encore dans le trou, de plus en plus minces
    rr = random.Random(2310 + k)
    cx, cy = CENTRE_TROU
    for _ in range(4 if k < 6 else 3):
        a = rr.uniform(0, 2 * math.pi)
        x, y = cx + rayon * 1.2 * math.cos(a), cy + rayon * .8 * math.sin(a)
        lg = rr.uniform(40, 90) + rayon * .2
        o.append(f'<path d="M{x - lg:.0f} {y:.0f} Q{x:.0f} {y - 16:.0f} {x + lg:.0f} {y:.0f} Q{x:.0f} {y + 8:.0f} {x - lg:.0f} {y:.0f} Z" '
                 f'fill="{PAPIER}" stroke="{MINE}" stroke-width="2"/>')
    o.append(f'<path d="{d}" fill="none" stroke="{MINE}" stroke-width="3" stroke-linejoin="round"/>')
    return "".join(o)


def bande_brume() -> str:
    corps = "".join(f'<svg x="{(k % COLONNES) * BW}" y="{(k // COLONNES) * BH}" width="{BW}" height="{BH}" viewBox="0 0 {BW} {BH}">{brume(k)}</svg>'
                    for k in range(len(RAYONS)))
    return svg(corps, BW * COLONNES, BH * math.ceil(len(RAYONS) / COLONNES))


def village() -> str:
    r = random.Random(2304)
    vx, vy = CLOCHER
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>',
         f'<path d="M0 {vy} Q500 {vy - 10} 960 {vy + 4} T{W} {vy - 6} V{H} H0 Z" fill="{CLAIR}"/>']
    # les toits, en mine, serrés autour du clocher
    toits = [(-520, 110, 70), (-400, 140, 96), (-250, 120, 64), (-130, 100, 80), (60, 130, 82), (200, 160, 110),
             (370, 110, 60), (480, 140, 78)]
    for dx, larg, haut in toits:
        x0 = vx + dx
        o.append(f'<path d="M{x0} {vy} L{x0} {vy - haut} L{x0 + larg / 2:.0f} {vy - haut - 46} L{x0 + larg} {vy - haut} L{x0 + larg} {vy} Z" fill="{MINE}"/>')
        o.append(f'<rect x="{x0 + larg * .3:.0f}" y="{vy - haut * .6:.0f}" width="{larg * .14:.0f}" height="{haut * .26:.0f}" fill="{LAVIS}"/>')
    # le clocher, sa baie vide : le ciel passe au travers, rien n'y pend
    o.append(f'<path d="M{vx - 50} {vy} L{vx - 50} {vy - 300} L{vx} {vy - 400} L{vx + 50} {vy - 300} L{vx + 50} {vy} Z" fill="{MINE}"/>')
    o.append(f'<path d="M{vx - 26} {vy - 214} L{vx - 26} {vy - 268} Q{vx} {vy - 292} {vx + 26} {vy - 268} L{vx + 26} {vy - 214} Z" fill="{PAPIER}"/>')
    o.append(f'<path d="M{vx - 30} {vy - 210} h60" stroke="{LAVIS}" stroke-width="6"/>')
    o.append(f'<path d="M{vx} {vy - 400} v-34 M{vx - 14} {vy - 420} h28" stroke="{MINE}" stroke-width="6" stroke-linecap="round"/>')
    # la terre entre lui et nous, les piquets, une dernière bande de brume
    for _ in range(26):
        x, y = r.uniform(0, W), r.uniform(vy + 30, H)
        o.append(f'<path d="M{x:.0f} {y:.0f} q{r.uniform(30, 70):.0f} -8 {r.uniform(90, 200):.0f} 0" fill="none" stroke="{MINE}" stroke-width="3"/>')
    for x in range(80, W, 260):
        hx = x + r.uniform(-40, 40)
        y = vy + 200 + r.uniform(0, 80)
        o.append(f'<path d="M{hx:.0f} {y:.0f} l{r.uniform(-8, 8):.0f} -{r.uniform(70, 110):.0f}" stroke="{LAVIS}" stroke-width="8" stroke-linecap="round"/>')
    for y, op in ((vy - 60, .5), (vy + 10, .65), (vy + 90, .4)):
        o.append(f'<path d="M-20 {y} Q480 {y - 24} 960 {y + 6} T1940 {y - 10} V{y + 50} Q1440 {y + 70} 960 {y + 44} T-20 {y + 54} Z" fill="{PAPIER}" opacity="{op}"/>')
    return "".join(o)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    fichiers = {
        "cin_e2-brouillard-souche": svg(souche_fond()),
        "cin_e2-brouillard-brume": bande_brume(),
        "cin_e2-brouillard-village": svg(village()),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"e2_brouillard_dechire : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
