#!/usr/bin/env python3
"""Réduit les planches (env_, cin_, chr_, fx_) à une petite palette, sans tramage, pour le budget web.

Les décors sont gravés : encre, papier, lavis, hachures. Une palette de 32 couleurs suffit à
l'œil (64 pour une tuile où une petite surface claire s'éteindrait ; une tuile à dégradé, brume ou halo,
est laissée telle quelle), et l'export web (texture « Lossless », WebP sans perte) compresse alors deux fois mieux.
L'import « Lossy » (WebP avec perte) fait l'inverse sur des hachures : il double la taille.
Les couleurs réservées restent exactes : le rouge (sang, sceau, ruban) et les accents des étapes
5 et 6 (papier_etapes.gd), que le shader ecran_gravure reconnaît à la couleur près. L'alpha est
conservé tel quel.

Les décors partent de 32 couleurs, les autres familles de 64 (validé par la DA le 17/11 sur
comparaisons). EXCLUSIONS liste les planches à dégradé que la détection laisse passer.

Usage : python3 tools/quantifier_env.py [--couleurs N] fichier.png...
        (sans fichier : toutes les planches env_, cin_, chr_ et fx_ de assets/graphics)
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
PAPIER = (0xE8, 0xE5, 0xDA)
RESERVEES = [(0x9B, 0x1C, 0x1C), (0xB0, 0x8A, 0x3E), (0x5F, 0x7F, 0x72)]


## Écart toléré (sur 255) entre un pixel et sa couleur de palette : au-delà, une petite surface
## claire (un halo de cierge, une flamme) serait ternie ; la tuile reprend alors plus de couleurs.
ECART_MAX = 24
## Au-delà, la tuile porte un dégradé (brume, halo) qui ferait des marches : on n'y touche pas.
COULEURS_MAX = 64
## Palette de départ par famille (préfixe du nom) ; --couleurs force la même pour tous.
DEPART = {"env": 32, "cin": 64, "chr": 64, "fx": 64}
## Dégradés jamais réduits : ceux que l'écart maximal ne voit pas (halo de greffe_04 en anneaux)
## et les brouillards (fondus d'alpha), validé par la DA le 17/11.
EXCLUSIONS = {"cin_greffe_04", "fx_brouillard_01", "fx_brouillard_02", "fx_brouillard_03"}


def _reduire(rgb: Image.Image, n: int, reservees: list) -> Image.Image:
    q = rgb.quantize(n - len(reservees), method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = q.getpalette()[:(n - len(reservees)) * 3]
    for c in reservees:
        pal += list(c)
    p = Image.new("P", (1, 1))
    p.putpalette(pal + [0] * (768 - len(pal)))
    return rgb.quantize(palette=p, dither=Image.Dither.NONE).convert("RGB")


def quantifier(chemin: Path, n: int) -> tuple[int, int, int]:
    """Réduit une tuile en place ; rend (taille avant, taille après, couleurs gardées)."""
    avant = chemin.stat().st_size
    im = Image.open(chemin).convert("RGBA")
    alpha = im.getchannel("A")
    # Couleurs brutes (non mélangées au papier) : sinon chaque passage rapproche les bords
    # semi-transparents du papier et le script n'est pas idempotent. Seuls les pixels
    # entièrement transparents prennent la couleur du papier (ils ne comptent pas).
    rgb = Image.new("RGB", im.size, PAPIER)
    rgb.paste(im.convert("RGB"), mask=alpha.point(lambda a: 255 if a else 0))
    couleurs = rgb.getcolors(1 << 24) or []
    if len(couleurs) <= max(n, COULEURS_MAX):
        # Déjà une petite palette (une planche déjà réduite, peut-être à 64) : la réduire encore
        # changerait l'image à chaque passage. Idempotent.
        return avant, avant, len(couleurs)
    presentes = {c for _, c in couleurs}
    reservees = [c for c in RESERVEES if c in presentes]
    visible = alpha.point(lambda a: 255 if a > 8 else 0)
    while True:
        out = _reduire(rgb, n, reservees)
        ecart = ImageChops.difference(rgb, out).convert("L")
        ecart = ImageChops.multiply(ecart, visible).getextrema()[1]
        if ecart <= ECART_MAX:
            break
        if n * 2 > COULEURS_MAX:
            return avant, avant, 0   # dégradé (brume, halo) : la tuile reste telle quelle
        n *= 2
    out = out.convert("RGBA")
    out.putalpha(alpha)
    out.save(chemin, optimize=True)
    return avant, chemin.stat().st_size, n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--couleurs", type=int, default=0)
    ap.add_argument("fichiers", nargs="*", type=Path)
    a = ap.parse_args()
    gfx = ROOT / "assets" / "graphics"
    fichiers = a.fichiers or sorted(
        p for p in gfx.rglob("*.png") if p.name.split("_")[0] in DEPART)
    total_avant = total_apres = 0
    for f in fichiers:
        if f.stem in EXCLUSIONS:
            print(f"  {f.name} : exclue (EXCLUSIONS)")
            continue
        depart = a.couleurs or DEPART.get(f.name.split("_")[0], 32)
        av, ap_, n = quantifier(f, depart)
        if n == 0:
            print(f"  {f.name} : dégradé, laissée telle quelle")
        elif n > depart:
            print(f"  {f.name} : {n} couleurs")
        total_avant += av
        total_apres += ap_
    print(f"{len(fichiers)} planches : {total_avant / 1e6:.1f} Mo -> {total_apres / 1e6:.1f} Mo (PNG)")


if __name__ == "__main__":
    main()
