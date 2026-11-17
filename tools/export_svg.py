#!/usr/bin/env python3
"""Exporte les sources SVG de art/src/ en PNG dans assets/graphics/.

Le chemin relatif est conservé : art/src/chr/messager/chr_messager_marche_01.svg
-> assets/graphics/chr/messager/chr_messager_marche_01.png.
Le SVG est dessiné à l'échelle 1920x1080 (sa taille en px = sa taille à l'écran).
Outil : resvg (rendu déterministe, gère motifs et filtres), sinon Inkscape 1.x.
N'exporte que les SVG plus récents que leur PNG, sauf avec --all.

Usage : python3 tools/export_svg.py [--all]
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "art" / "src"
DST = ROOT / "assets" / "graphics"


def renderer() -> list[str]:
    if shutil.which("resvg"):
        return ["resvg", "{src}", "{dst}"]
    if shutil.which("inkscape"):
        return ["inkscape", "{src}", "--export-type=png", "--export-filename={dst}"]
    sys.exit("Ni resvg ni inkscape trouvé. Installer resvg : cargo install resvg "
             "(ou paquet de la distribution).")


def main() -> None:
    force = "--all" in sys.argv
    cmd = renderer()
    done = 0
    exportes: list[Path] = []
    for svg in sorted(SRC.rglob("*.svg")):
        png = DST / svg.relative_to(SRC).with_suffix(".png")
        if not force and png.exists() and png.stat().st_mtime >= svg.stat().st_mtime:
            continue
        png.parent.mkdir(parents=True, exist_ok=True)
        args = [a.format(src=svg, dst=png) for a in cmd]
        subprocess.run(args, check=True)
        print(f"{svg.relative_to(ROOT)} -> {png.relative_to(ROOT)}")
        done += 1
        exportes.append(png)
    print(f"{done} fichier(s) exporté(s)")
    a_reduire = [str(p) for p in exportes if p.name.startswith(("env_", "cin_", "chr_", "fx_"))]
    if a_reduire:
        # Palette réduite pour le budget web (exceptions : dégradés et EXCLUSIONS de quantifier_env.py).
        subprocess.run([sys.executable, str(ROOT / "tools" / "quantifier_env.py"), *a_reduire], check=True)
    if done:
        # Les tuiles de premier plan réexportées en taille pleine sont rognées à nouveau.
        subprocess.run([sys.executable, str(ROOT / "tools" / "rogner_tuiles.py")], check=True)


if __name__ == "__main__":
    main()
