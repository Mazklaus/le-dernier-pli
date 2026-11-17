#!/usr/bin/env python3
"""Génère les planches de la cinématique e1_adieu_jacquot (lot 2, planche validée par le GD le
17/11) : à la fin de e1_adieu, Tobie s'en va dans le boyau ; derrière lui, Jacquot siffle et
lève la main sous la couverture anti-gaz de l'abri, de plus en plus petit ; la couverture
retombe.

  P1 et P2 : décor env_e1_plan3_sape-sortie_01 réemployé, gestes siffler et lever-main de
             Jacquot réemployés (pas de planche).
  P3, gros plan sur la porte de l'abri :
  cin_e1-adieu-porte    le fond 1920 x 1080 : le chambranle de planches, le noir de l'abri,
                        la couverture anti-gaz relevée par la main de Jacquot (image 0) ;
  cin_e1-adieu-main     4 images de ZONE_MAIN, grille 2 x 2 : 0 la main tient la couverture
                        relevée ; 1 les doigts s'ouvrent, un salut ; 2 la main lâche, la
                        couverture tombe ; 3 elle est retombée, la porte est close.

Aucun rouge.

Usage : python3 tools/gen_cin_e1_adieu.py
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
PORTE = (620, 1300)          # bords du chambranle
LINTEAU = 140
ZONE_MAIN = (560, 60, 800, 960)


def svg(contenu: str, w: int = W, h: int = H) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{DEFS_CIN}{contenu}</svg>\n')


def bande(images: list[str], zone: tuple[int, int, int, int], colonnes: int) -> str:
    x, y, w, h = zone
    lignes = math.ceil(len(images) / colonnes)
    corps = "".join(f'<svg x="{(i % colonnes) * w}" y="{(i // colonnes) * h}" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}">{c}</svg>'
                    for i, c in enumerate(images))
    return svg(corps, w * colonnes, h * lignes)


def boyau() -> str:
    """Les planches du boyau, le chambranle, le noir de l'abri."""
    r = random.Random(1101)
    g, d = PORTE
    o = [f'<rect width="{W}" height="{H}" fill="{MINE}"/>']
    for y in range(40, H, 86):
        o.append(f'<path d="M0 {y} H{W}" stroke="{ENCRE}" stroke-width="3"/>')
        for _ in range(4):
            x = r.uniform(0, W)
            o.append(f'<path d="M{x:.0f} {y} v86" stroke="{ENCRE}" stroke-width="2"/>')
    o.append(f'<rect x="{g}" y="{LINTEAU}" width="{d - g}" height="{H - LINTEAU}" fill="{ENCRE}"/>')
    o.append(f'<path d="M{g - 60} {H} V{LINTEAU - 50} H{d + 60} V{H} M{g} {H} V{LINTEAU} H{d} V{H}" fill="none" {ST} stroke-width="14"/>')
    o.append(f'<rect x="{g - 80}" y="{LINTEAU - 90}" width="{d - g + 160}" height="50" fill="{CLAIR}" {ST} stroke-width="6"/>')
    # la tringle de la couverture
    o.append(f'<path d="M{g - 20} {LINTEAU + 20} H{d + 20}" {ST} stroke-width="10"/>')
    return "".join(o)


def couverture(k: int) -> str:
    """La couverture anti-gaz : relevée sur la gauche par la main (k 0, 1), qui tombe (2),
    retombée (3)."""
    g, d = PORTE
    haut = LINTEAU + 20
    if k <= 1:
        # relevée : un pan drapé tiré vers la gauche et le haut, le noir de l'abri à droite
        pan = (f'M{g} {haut} H{d} Q{d - 60} {haut + 160} {g + 330} {haut + 260} '
               f'Q{g + 230} {haut + 290} {g + 170} {haut + 230} L{g + 120} {H} H{g} Z')
        plis = [f'M{g + 60 + i * 90} {haut} Q{g + 120 + i * 60} {haut + 150} {g + 170 + i * 40} {haut + 250}' for i in range(5)]
    elif k == 2:
        pan = f'M{g} {haut} H{d} L{d - 20} {H - 260} Q{(g + d) / 2} {H - 160} {g + 30} {H - 300} Z'
        plis = [f'M{g + 80 + i * 120} {haut} L{g + 70 + i * 125} {H - 260}' for i in range(6)]
    else:
        pan = f'M{g} {haut} H{d} L{d + 6} {H} H{g - 6} Z'
        plis = [f'M{g + 80 + i * 120} {haut} Q{g + 90 + i * 120} {haut + 400} {g + 74 + i * 120} {H}' for i in range(6)]
    o = [f'<path d="{pan}" fill="{CLAIR}" {ST} stroke-width="6"/>']
    for p in plis:
        o.append(f'<path d="{p}" fill="none" stroke="{MINE}" stroke-width="4"/>')
    # l'ourlet cousu, en pointillé le long du bas
    if k == 3:
        o.append(f'<path d="M{g + 10} {H - 40} H{d - 10}" fill="none" stroke="{ENCRE}" stroke-width="3" stroke-dasharray="14 10"/>')
    return "".join(o)


def main_jacquot(k: int) -> str:
    """La manche et la main de Jacquot qui tiennent le pan relevé (0) ou saluent (1)."""
    if k > 1:
        return ""
    g, _ = PORTE
    mx, my = g + 260, LINTEAU + 260
    manche = (f'<path d="M{mx - 40} {H + 20} L{mx - 70} {my + 120} Q{mx - 30} {my + 80} {mx + 40} {my + 110} L{mx + 90} {H + 20} Z" '
              f'fill="{CLAIR}" {ST} stroke-width="6"/>'
              f'<path d="M{mx - 72} {my + 130} Q{mx - 20} {my + 100} {mx + 44} {my + 126}" fill="none" {ST} stroke-width="5"/>')
    if k == 0:
        # le poing fermé sur l'étoffe
        main = (f'<path d="M{mx - 60} {my + 110} Q{mx - 70} {my + 40} {mx - 20} {my + 20} Q{mx + 40} {my + 10} {mx + 50} {my + 60} '
                f'Q{mx + 50} {my + 110} {mx + 30} {my + 120} Z" fill="{PAPIER}" {ST} stroke-width="5"/>')
        for i in range(4):
            main += f'<path d="M{mx - 40 + i * 22} {my + 26 + i * 2} q8 20 -2 40" fill="none" {ST} stroke-width="3"/>'
    else:
        # les doigts ouverts : un salut, la paume vers Tobie
        main = (f'<path d="M{mx - 50} {my + 110} Q{mx - 60} {my + 50} {mx - 20} {my + 40} L{mx + 30} {my + 40} '
                f'Q{mx + 50} {my + 70} {mx + 30} {my + 120} Z" fill="{PAPIER}" {ST} stroke-width="5"/>')
        for i, (dx, lg) in enumerate(((-38, 70), (-14, 92), (10, 88), (32, 66))):
            main += (f'<path d="M{mx + dx} {my + 44} l{(i - 1.5) * 6:.0f} {-lg}" {ST} stroke-width="20"/>'
                     f'<path d="M{mx + dx} {my + 44} l{(i - 1.5) * 6:.0f} {-lg}" stroke="{PAPIER}" stroke-width="12" stroke-linecap="round"/>')
        main += f'<path d="M{mx - 50} {my + 80} l-50 -30" {ST} stroke-width="20"/><path d="M{mx - 50} {my + 80} l-50 -30" stroke="{PAPIER}" stroke-width="12" stroke-linecap="round"/>'
    return manche + main


def plan(k: int) -> str:
    return boyau() + couverture(k) + main_jacquot(k)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    fichiers = {
        "cin_e1-adieu-porte": svg(plan(0)),
        "cin_e1-adieu-main": bande([plan(k) for k in range(4)], ZONE_MAIN, 2),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"e1_adieu_jacquot : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
