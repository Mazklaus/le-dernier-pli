#!/usr/bin/env python3
"""Génère les planches de la cinématique e6_porte_scellee (lot 1, planche validée par le GD le
17/11) : au début de e6_seuil, la porte couverte de cire noire vue d'en bas (lent panoramique
vers le haut), puis Éloi pose son bocal devant Tobie et recule dans l'ombre ; le bocal reste
seul devant la porte. Rien de ce qu'il y a derrière la porte.

L'écran de l'étape 6 est inversé : la cire noire est le papier (noire à l'écran), ses coulures
et ses bords sont à l'encre (clairs à l'écran), comme dans le décor env_e6_plan3_seuil_01.

  P1, 0 à 3 s, contre-plongée :
  cin_e6-porte-cire    1920 x 2160 : la porte, plus étroite vers le haut, couche de cire sur
                       couche de cire (coulures, gouttes figées), l'arc, le plafond de terre.
  P2 et P3, 3 à 10 s (décor du seuil réemployé, gestes d'Éloi réemployés) :
  cin_e6-porte-eloi    200 x 320, pieds à (100, 316) : Éloi debout, les mains jointes,
                       l'image 5 de chr_eloi_poser-bocal_01 sans le bocal (il recule sans lui) ;
  cin_e6-porte-bocal   CADRE_BOCAL de la même image : le bocal posé, seul (même place).
Les deux dernières sont tirées de la planche du geste (le dessin d'origine, rien de redessiné)
et gardées en SVG (image intégrée) pour que art/src/ reste la source de tout.

Aucun rouge, aucune cloche.

Usage : python3 tools/gen_cin_e6_porte.py
"""
from __future__ import annotations

import base64
import io
import math
import random
from pathlib import Path

from PIL import Image

from gen_cin_epilogues import DEFS_CIN
from gen_decors_e1_surface import ENCRE, MINE, PAPIER

ROOT = Path(__file__).resolve().parent.parent
DST = ROOT / "art" / "src" / "cin"
GESTE = ROOT / "assets" / "graphics" / "chr" / "chr_eloi_poser-bocal_01.png"
W, H = 1920, 2160
ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
IMAGE_POSE = 5                       # Éloi debout, le bocal à ses pieds
CADRE_BOCAL = (40, 268, 40, 52)      # x, y, l, h du bocal dans une image de 200 x 320
PIED_GAUCHE = 79                     # à gauche de cette colonne, sous y 268 : le bocal


def svg(contenu: str, w: int, h: int) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{DEFS_CIN}{contenu}</svg>\n')


def bord(y: float) -> tuple[float, float]:
    """Les bords de la porte à la hauteur y : elle se resserre vers le haut (contre-plongée)."""
    u = (H - y) / (H - 300)
    return 240 + 300 * u, 1680 - 300 * u


def cire() -> str:
    r = random.Random(6064)
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>']
    # le plafond de terre et ses racines, au-dessus de l'arc
    o.append(f'<path d="M0 0 H{W} V150 Q1500 120 960 170 T0 140 Z" fill="url(#terre)" {ST} stroke-width="3"/>')
    for _ in range(40):
        x = r.uniform(0, W)
        o.append(f'<path d="M{x:.0f} 150 q{r.uniform(-10, 10):.0f} 40 {r.uniform(-4, 4):.0f} {r.uniform(50, 110):.0f}" fill="none" {ST} stroke-width="2"/>')
    # l'arc et le chambranle
    g0, d0 = bord(300)
    gb, db = bord(H)
    o.append(f'<path d="M{gb - 90:.0f} {H} L{g0 - 70:.0f} 300 Q960 60 {d0 + 70:.0f} 300 L{db + 90:.0f} {H}" fill="none" {ST} stroke-width="14"/>')
    o.append(f'<path d="M{gb - 40:.0f} {H} L{g0 - 30:.0f} 300 Q960 120 {d0 + 30:.0f} 300 L{db + 40:.0f} {H}" fill="none" {ST} stroke-width="5"/>')
    o.append(f'<path d="M{gb:.0f} {H} L{g0:.0f} 300 Q960 170 {d0:.0f} 300 L{db:.0f} {H}" fill="{PAPIER}" {ST} stroke-width="8"/>')
    o.append(f'<path d="M960 {H} V190" {ST} stroke-width="5"/>')
    # les couches de cire : des bords ondulés, des coulures figées avec leur goutte
    y = 330
    while y < H - 60:
        g, d = bord(y)
        pts = []
        x = g + 6
        while x < d - 6:
            pts.append((x, y + r.uniform(-26, 26)))
            x += r.uniform(50, 110)
        pts.append((d - 6, y + r.uniform(-20, 20)))
        dd = "M" + " L".join(f"{px:.0f} {py:.0f}" for px, py in pts)
        o.append(f'<path d="{dd}" fill="none" {ST} stroke-width="{3 + y / H * 2:.1f}"/>')
        o.append(f'<path d="{dd} L{d - 6:.0f} {y + 34:.0f} L{g + 6:.0f} {y + 34:.0f} Z" fill="{MINE}" opacity=".18"/>')
        for px, py in pts[:-1]:
            if r.random() < .55:
                lg = r.uniform(30, 120) * (.6 + y / H)
                o.append(f'<path d="M{px:.0f} {py:.0f} q{r.uniform(-3, 3):.0f} {lg / 2:.0f} 0 {lg:.0f}" fill="none" {ST} stroke-width="2.5"/>'
                         f'<circle cx="{px:.0f}" cy="{py + lg + 5:.0f}" r="{4 + y / H * 4:.1f}" fill="{PAPIER}" {ST} stroke-width="2.5"/>')
        y += r.uniform(110, 170) * (.7 + y / H * .6)
    # le seuil, en bas
    o.append(f'<path d="M0 {H - 40} H{W} V{H} H0 Z" fill="url(#terre)" {ST} stroke-width="4"/>')
    o.append(f'<path d="M{gb:.0f} {H - 40} Q960 {H - 70} {db:.0f} {H - 40}" fill="none" {ST} stroke-width="4"/>')
    return "".join(o)


def image_integree(im: Image.Image) -> str:
    tampon = io.BytesIO()
    im.save(tampon, "PNG", optimize=True)
    donnees = base64.b64encode(tampon.getvalue()).decode("ascii")
    return svg(f'<image width="{im.width}" height="{im.height}" href="data:image/png;base64,{donnees}"/>', im.width, im.height)


def eloi_et_bocal() -> tuple[str, str]:
    planche = Image.open(GESTE).convert("RGBA")
    pose = planche.crop((IMAGE_POSE * 200, 0, IMAGE_POSE * 200 + 200, 320))
    x, y, l, h = CADRE_BOCAL
    bocal = pose.crop((x, y, x + l, y + h))
    sans = pose.copy()
    px = sans.load()
    for i in range(0, PIED_GAUCHE):
        for j in range(y, 320):
            px[i, j] = (0, 0, 0, 0)
    return image_integree(sans), image_integree(bocal)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    eloi, bocal = eloi_et_bocal()
    fichiers = {
        "cin_e6-porte-cire": svg(cire(), W, H),
        "cin_e6-porte-eloi": eloi,
        "cin_e6-porte-bocal": bocal,
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"e6_porte_scellee : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
