#!/usr/bin/env python3
"""Génère les planches de la cinématique e5_boucle (lot 2, planche validée par le GD le 17/11) :
au second passage à la croix-repère (e5_sentier, titre debut), Tobie marche entre les croix
toutes pareilles, la même croix revient, et de près, sur son poteau, l'encoche ancienne,
noircie. Jamais une main.

Les plans 1 et 2 réemploient le décor de la boucle (env_e5_plan3_boucle_01 et _02). Seul le
gros plan est nouveau :
  cin_e5-boucle-poteau    1920 x 1080 : le poteau de la croix-repère, de près, son bois veiné,
                          la brume derrière ; l'encoche ancienne, noircie, ses bords brûlés ;
  cin_e5-boucle-entaille  l'entaille fraîche de Tobie (bois clair, éclats), posée au-dessus
                          par la ciné seulement s'il l'a faite au premier passage.

L'écran de l'étape 5 inverse l'image : dessiné à l'endroit (le noirci reste de l'encre).
Aucun rouge.

Usage : python3 tools/gen_cin_e5_boucle.py
"""
from __future__ import annotations

import random
from pathlib import Path

from gen_cin_epilogues import DEFS_CIN
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER

DST = Path(__file__).resolve().parent.parent / "art" / "src" / "cin"
W, H = 1920, 1080
ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
CLAIR = "#D3CFC2"
POTEAU = (700, 1220)            # bords du poteau
ANCIENNE = (960, 720)           # centre de l'encoche ancienne
ZONE_ENTAILLE = (780, 300, 360, 260)   # où se pose l'entaille fraîche


def svg(contenu: str, w: int = W, h: int = H) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{DEFS_CIN}{contenu}</svg>\n')


def encoche(cx: float, cy: float, larg: float, haut: float, fond: str, bord: str) -> str:
    """Une encoche taillée en V dans le bois, vue de face : deux pans, le fond de la taille."""
    g, d = cx - larg / 2, cx + larg / 2
    return (f'<path d="M{g:.0f} {cy - haut / 2:.0f} L{d:.0f} {cy - haut / 2 - 16:.0f} L{d - 20:.0f} {cy + haut / 2 - 6:.0f} '
            f'L{g + 16:.0f} {cy + haut / 2 + 6:.0f} Z" fill="{fond}" {ST} stroke-width="6"/>'
            f'<path d="M{g + 10:.0f} {cy:.0f} L{d - 12:.0f} {cy - 10:.0f}" stroke="{bord}" stroke-width="5"/>')


def poteau() -> str:
    r = random.Random(5201)
    g, d = POTEAU
    o = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>']
    # la brume derrière : d'autres poteaux, pâles, flous de distance (aplats, pas de flou)
    for x, ep, op in ((180, 26, .35), (420, 18, .25), (1450, 30, .4), (1700, 22, .3), (1860, 16, .2)):
        o.append(f'<rect x="{x}" y="-20" width="{ep}" height="{H + 40}" fill="{MINE}" opacity="{op}"/>')
    o.append(f'<rect x="0" y="380" width="{W}" height="120" fill="{MINE}" opacity=".12"/>')
    # le poteau, son bois, ses veines
    o.append(f'<rect x="{g}" y="-20" width="{d - g}" height="{H + 40}" fill="{CLAIR}" {ST} stroke-width="8"/>')
    for i in range(14):
        x = g + 20 + i * (d - g - 40) / 13 + r.uniform(-6, 6)
        dx = r.uniform(-10, 10)
        o.append(f'<path d="M{x:.0f} -20 Q{x + dx:.0f} 300 {x + dx * .4:.0f} 560 T{x + dx:.0f} {H + 20}" fill="none" stroke="{MINE}" stroke-width="{r.uniform(2, 4):.1f}"/>')
    # un nœud du bois, une fente
    o.append(f'<ellipse cx="{d - 120}" cy="160" rx="34" ry="54" fill="none" stroke="{LAVIS}" stroke-width="5"/>')
    o.append(f'<ellipse cx="{d - 120}" cy="160" rx="12" ry="22" fill="{LAVIS}"/>')
    o.append(f'<path d="M{d - 80} 860 L{d - 92} 1000 L{d - 84} {H + 20}" fill="none" {ST} stroke-width="4"/>')
    # l'encoche ancienne : noircie, bords brûlés, le bois autour terni
    cx, cy = ANCIENNE
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="150" ry="74" fill="{MINE}" opacity=".45"/>')
    o.append(encoche(cx, cy, 200, 80, ENCRE, LAVIS))
    for _ in range(12):
        x, y = cx + r.uniform(-120, 120), cy + r.uniform(-60, 60)
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(3, 7):.0f}" fill="{LAVIS}"/>')
    # des coulures de suie sous l'encoche
    for dx in (-60, 10, 70):
        o.append(f'<path d="M{cx + dx} {cy + 40} q6 50 -2 {r.uniform(70, 120):.0f}" fill="none" stroke="{LAVIS}" stroke-width="5" stroke-linecap="round"/>')
    return "".join(o)


def entaille() -> str:
    """L'entaille fraîche de Tobie : le bois clair mis à nu, des éclats (fond transparent)."""
    x, y, w, h = ZONE_ENTAILLE
    cx, cy = x + w / 2, y + h / 2
    o = [encoche(cx, cy, 200, 84, PAPIER, MINE)]
    for dx, dy, a in ((-110, -40, -30), (100, -60, 20), (-90, 50, 200), (110, 40, 160)):
        o.append(f'<g transform="rotate({a} {cx + dx} {cy + dy})"><path d="M{cx + dx - 18} {cy + dy} L{cx + dx + 18} {cy + dy - 4} '
                 f'L{cx + dx + 14} {cy + dy + 4} Z" fill="{PAPIER}" {ST} stroke-width="3"/></g>')
    corps = f'<svg x="0" y="0" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}">{"".join(o)}</svg>'
    return svg(corps, w, h)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    fichiers = {
        "cin_e5-boucle-poteau": svg(poteau()),
        "cin_e5-boucle-entaille": entaille(),
    }
    for nom, contenu in fichiers.items():
        (DST / f"{nom}.svg").write_text(contenu, encoding="utf-8")
    print(f"e5_boucle : {len(fichiers)} planches dans art/src/cin/")


if __name__ == "__main__":
    main()
