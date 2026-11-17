#!/usr/bin/env python3
"""Vérifie les conventions d'assets du projet Godot (stdlib uniquement).

Usage : python3 tools/check_assets.py [racine_du_projet]
Code de sortie 1 si une erreur bloquante est trouvée.
"""
from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
AUDIO_DIR = ROOT / "assets" / "audio"
GFX_DIR = ROOT / "assets" / "graphics"
SVG_DIR = ROOT / "art" / "src"  # sources SVG, ignorées par Godot (.gdignore)
MAX_TEX = 4096

SEG = r"[a-z0-9]+(?:-[a-z0-9]+)*"  # minuscules ASCII, tirets autorisés (tranchee-mere)
AUDIO_RULES = {
    # préfixe : (regex du nom sans extension, extension attendue, boucle attendue)
    "amb": (rf"amb_{SEG}_{SEG}", ".ogg", True),
    "mus": (rf"mus_{SEG}_{SEG}", ".ogg", True),
    "sfx": (rf"sfx_{SEG}_{SEG}_\d{{2}}", ".ogg", False),
    "vox": (rf"vox_{SEG}_\d{{2}}", ".ogg", False),
}
GFX_RULES = [
    rf"chr_{SEG}_{SEG}_\d{{2}}",
    rf"env_e[1-7]_plan[0-4]_{SEG}(?:_\d{{2}})?",
    rf"fx_{SEG}(?:_\d{{2}})?",
    rf"ui_{SEG}(?:_\d{{2}})?",
    rf"cin_{SEG}(?:_\d{{2}})?",  # gravures plein écran (épilogues)
]

errors: list[str] = []
warnings: list[str] = []


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def import_options(p: Path) -> dict[str, str]:
    imp = p.with_name(p.name + ".import")
    if not imp.exists():
        return {}
    opts = {}
    for line in imp.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("["):
            k, v = line.split("=", 1)
            opts[k.strip()] = v.strip()
    return opts


def png_size(p: Path) -> tuple[int, int] | None:
    with p.open("rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


def check_audio() -> None:
    if not AUDIO_DIR.exists():
        return
    for p in sorted(AUDIO_DIR.rglob("*")):
        if p.is_dir() or p.suffix == ".import" or p.name.startswith("."):
            continue
        stem, ext = p.stem, p.suffix.lower()
        rule = AUDIO_RULES.get(stem.split("_", 1)[0])
        if rule is None or not re.fullmatch(rule[0], stem):
            errors.append(f"{rel(p)} : nom hors convention audio "
                          "(amb_<etape>_<couche>, mus_<etape>_<moment>, "
                          "sfx_<famille>_<action>_NN, vox_<personnage>_NN)")
            continue
        pattern, want_ext, want_loop = rule
        if ext != want_ext:
            errors.append(f"{rel(p)} : extension {ext}, attendu {want_ext}")
        opts = import_options(p)
        if not opts:
            errors.append(f"{rel(p)} : {p.name}.import manquant (ouvrir le projet dans Godot "
                          "ou lancer godot --headless --import, puis versionner le .import)")
        if want_loop and opts and opts.get("loop") != "true":
            errors.append(f"{rel(p)} : boucle non activée à l'import (loop=true)")


def check_graphics() -> None:
    if not GFX_DIR.exists():
        return
    pngs = {p.stem: p for p in GFX_DIR.rglob("*.png")}
    for stem, p in sorted(pngs.items()):
        base = stem[:-4] if stem.endswith("_red") else stem
        if not any(re.fullmatch(r, base) for r in GFX_RULES):
            errors.append(f"{rel(p)} : nom hors convention (chr_<perso>_<anim>_NN, "
                          "env_eN_planN_<nom>, fx_<nom>, ui_<nom>, cin_<nom>, suffixe _red optionnel)")
        if stem.endswith("_red") and base not in pngs:
            errors.append(f"{rel(p)} : calque rouge sans base {base}.png")
        size = png_size(p)
        if size is None:
            errors.append(f"{rel(p)} : fichier PNG invalide")
        elif max(size) > MAX_TEX:
            errors.append(f"{rel(p)} : {size[0]}x{size[1]} dépasse {MAX_TEX} px "
                          "(découper les décors en tuiles de 2048)")
        opts = import_options(p)
        if not opts:
            errors.append(f"{rel(p)} : {p.name}.import manquant (ouvrir le projet dans Godot "
                          "ou lancer godot --headless --import, puis versionner le .import)")
        if opts.get("mipmaps/generate") == "true":
            errors.append(f"{rel(p)} : mipmaps activées à l'import")
        if SVG_DIR.exists() and not stem.endswith("_red"):
            src_stem = re.sub(r"_\d{2}$", "", stem)
            if not list(SVG_DIR.rglob(f"{src_stem}*.svg")):
                warnings.append(f"{rel(p)} : aucune source SVG trouvée dans art/src/")
    for p in GFX_DIR.rglob("*.svg"):
        errors.append(f"{rel(p)} : les SVG vont dans art/src/, pas dans assets/")


def check_project() -> None:
    proj = ROOT / "project.godot"
    if not proj.exists():
        warnings.append("project.godot absent : vérifications projet ignorées")
        return
    text = proj.read_text(encoding="utf-8")
    if 'renderer/rendering_method="gl_compatibility"' not in text:
        errors.append("project.godot : le renderer doit être Compatibility (gl_compatibility)")
    if re.search(r"default_texture_filter\s*=\s*0", text):
        errors.append("project.godot : filtrage nearest interdit, garder le linéaire par défaut")
    if not (ROOT / "default_bus_layout.tres").exists():
        errors.append("default_bus_layout.tres absent (bus audio à versionner)")
    if SVG_DIR.exists() and not (SVG_DIR / ".gdignore").exists():
        errors.append("art/src/.gdignore absent : Godot importerait les SVG sources")


check_audio()
check_graphics()
check_project()
for w in warnings:
    print(f"::warning::{w}")
for e in errors:
    print(f"::error::{e}")
print(f"{len(errors)} erreur(s), {len(warnings)} avertissement(s)")
sys.exit(1 if errors else 0)
