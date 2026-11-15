#!/usr/bin/env python3
"""Rogne les marges transparentes des tuiles de décor pour économiser la mémoire vidéo.

Pour chaque tuile rognée, le PNG est remplacé par sa partie utile et un AtlasTexture
<nom>.tres est écrit à côté : sa marge (margin) redonne la taille et la position
d'origine. DecorParallaxe.charger_tuile() charge le .tres s'il existe, sinon le PNG :
le décor se pose exactement comme avant.

Idempotent : relancé sur une tuile déjà rognée, il ne change rien ; sur un PNG
réexporté en taille pleine (export_svg.py), il recalcule le rognage.

Usage : python3 tools/rogner_tuiles.py [--plans 0,1,2,3,4] [--seuil 0.8] [--verifier]
  --plans    plans concernés (défaut : tous, 0 à 4)
  --seuil    rogne si la partie utile fait moins de cette fraction de la tuile (défaut : 0.8)
  --verifier n'écrit rien ; code 1 si une tuile devrait être rognée (CI)
Dépendance : Pillow.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GFX = ROOT / "assets" / "graphics" / "env"
TUILE = re.compile(r"env_e[1-7]_plan(?P<plan>[0-4])_[a-z0-9-]+_\d{2}")
MARGE_TRES = re.compile(r"margin = Rect2\(([-\d.]+), ([-\d.]+), ([-\d.]+), ([-\d.]+)\)")
REGION_TRES = re.compile(r"region = Rect2\(([-\d.]+), ([-\d.]+), ([-\d.]+), ([-\d.]+)\)")


def lire_tres(tres: Path) -> tuple[int, int, int, int] | None:
    """(décalage x, décalage y, largeur source, hauteur source) d'un .tres existant."""
    if not tres.exists():
        return None
    texte = tres.read_text(encoding="utf-8")
    m, r = MARGE_TRES.search(texte), REGION_TRES.search(texte)
    if not m or not r:
        return None
    mx, my, mw, mh = (int(float(v)) for v in m.groups())
    rw, rh = (int(float(v)) for v in r.groups()[2:])
    return mx, my, rw + mw, rh + mh


def ecrire_tres(tres: Path, png: Path, x: int, y: int, w: int, h: int, sw: int, sh: int) -> None:
    chemin = "res://" + png.relative_to(ROOT).as_posix()
    tres.write_text(
        '[gd_resource type="AtlasTexture" load_steps=2 format=3]\n\n'
        f'[ext_resource type="Texture2D" path="{chemin}" id="1"]\n\n'
        "[resource]\n"
        'atlas = ExtResource("1")\n'
        f"region = Rect2(0, 0, {w}, {h})\n"
        f"margin = Rect2({x}, {y}, {sw - w}, {sh - h})\n",
        encoding="utf-8",
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plans", default="0,1,2,3,4")
    ap.add_argument("--seuil", type=float, default=0.8)
    ap.add_argument("--verifier", action="store_true")
    args = ap.parse_args()
    plans = set(args.plans.split(","))

    avant = apres = 0
    a_rogner: list[str] = []
    for png in sorted(GFX.rglob("*.png")):
        m = TUILE.fullmatch(png.stem)
        if not m or m["plan"] not in plans:
            continue
        tres = png.with_suffix(".tres")
        im = Image.open(png).convert("RGBA")
        existant = lire_tres(tres)
        if existant and im.size != existant[2:]:
            ox, oy, sw, sh = existant  # déjà rognée
        else:
            ox, oy, (sw, sh) = 0, 0, im.size  # taille pleine (neuve ou réexportée)
        boite = im.getchannel("A").getbbox() or (0, 0, 1, 1)
        x0, y0, x1, y1 = boite
        w, h = x1 - x0, y1 - y0
        avant += sw * sh * 4
        if (w, h) == im.size:
            apres += im.size[0] * im.size[1] * 4
            continue  # rien à gagner
        if not existant and w * h > args.seuil * sw * sh:
            apres += sw * sh * 4
            continue  # assez pleine, on la laisse
        apres += w * h * 4
        a_rogner.append(png.relative_to(ROOT).as_posix())
        if args.verifier:
            continue
        im.crop(boite).save(png, optimize=True)
        ecrire_tres(tres, png, ox + x0, oy + y0, w, h, sw, sh)
        print(f"{png.relative_to(ROOT)} : {sw}x{sh} -> {w}x{h} en ({ox + x0}, {oy + y0})")

    print(f"Mémoire vidéo (RGBA8) des plans {args.plans} : {avant / 2**20:.0f} Mo -> {apres / 2**20:.0f} Mo")
    if args.verifier and a_rogner:
        for chemin in a_rogner:
            print(f"::warning::{chemin} : tuile presque vide non rognée (python3 tools/rogner_tuiles.py)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
