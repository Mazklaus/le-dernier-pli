#!/usr/bin/env python3
"""Génère les planches d'animation de Tobie « Pied-Léger », le messager (planche de style n° 1).

Chaque animation est une planche horizontale d'images de 200 x 320 px, Tobie tourné vers la
droite, pieds à plat sur le sol à y 316, centre des hanches à x 100. 10 images par seconde.

  art/src/chr/chr_tobie_<anim>_01.svg           dessin de base (sans rouge, front nu)
  art/src/chr/chr_tobie_<anim>_01_red.svg       calque rouge : le ruban du pli, seul
  art/src/chr/chr_tobie-cendre_<anim>_01.svg    calque : la marque de cendre au front

La marche est construite sur un squelette (hanche, genou, cheville) résolu en cinématique
inverse : le pied d'appui reste collé au sol et recule de 64 px réels par demi-cycle, ce qui
correspond à 160 px/s à 10 i/s sur un cycle de 8 images. Aucun glissement.

Usage : python3 tools/gen_chr_tobie.py
"""
from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DST = ROOT / "art" / "src" / "chr"

PAPIER, ENCRE, ROUGE = "#E8E5DA", "#15130F", "#9B1C1C"
CADRE_L, CADRE_H = 200, 320
ECHELLE = 0.845                       # dessin de la planche (355 px) -> 300 px à l'écran
SOL_PLANCHE = 405                     # sol dans le repère de la planche de style
HANCHE = (134.0, 264.0)               # centre des hanches, repère planche
CUISSE, TIBIA = 66.0, 66.0
CHEVILLE_Y = 392.0                    # cheville au sol (la botte fait 13 px)
FOULEE = 64 / ECHELLE / 2             # demi-foulée dans le repère planche (pied de +F à -F)

DEFS = f"""<defs>
<pattern id="h1" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(38)"><rect width="5" height="5" fill="{PAPIER}"/><line x1="0" y1="0" x2="0" y2="5" stroke="{ENCRE}" stroke-width="1.2"/></pattern>
<pattern id="h2" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(38)"><rect width="4" height="4" fill="{PAPIER}"/><line x1="0" y1="0" x2="0" y2="4" stroke="{ENCRE}" stroke-width="1.3"/><line x1="0" y1="2" x2="4" y2="2" stroke="{ENCRE}" stroke-width=".8"/></pattern>
<pattern id="mol" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(-22)"><rect width="9" height="9" fill="{PAPIER}"/><line x1="0" y1="0" x2="9" y2="0" stroke="{ENCRE}" stroke-width="1.8"/><line x1="0" y1="4.5" x2="9" y2="4.5" stroke="{ENCRE}" stroke-width=".7"/></pattern>
<pattern id="pt" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="4" fill="{PAPIER}"/><circle cx="2" cy="2" r=".8" fill="{ENCRE}"/></pattern>
</defs>"""

ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'


# --- squelette ---------------------------------------------------------------------
def ik(hanche: tuple[float, float], cheville: tuple[float, float]) -> tuple[float, float]:
    """Genou d'une jambe à deux segments, plié vers l'avant (+x)."""
    hx, hy = hanche
    cx, cy = cheville
    dx, dy = cx - hx, cy - hy
    d = min(math.hypot(dx, dy), CUISSE + TIBIA - 0.01)
    a = math.atan2(dy, dx)
    # loi des cosinus : angle entre la droite hanche-cheville et la cuisse
    b = math.acos((CUISSE ** 2 + d ** 2 - TIBIA ** 2) / (2 * CUISSE * d))
    ang = a - b                       # genou du côté +x quand la jambe descend
    return hx + CUISSE * math.cos(ang), hy + CUISSE * math.sin(ang)


def membre(p0, p1, l0: float, l1: float) -> str:
    """Quadrilatère épais entre deux articulations (largeur l0 en haut, l1 en bas)."""
    (x0, y0), (x1, y1) = p0, p1
    ang = math.atan2(y1 - y0, x1 - x0) + math.pi / 2
    ox0, oy0 = math.cos(ang) * l0 / 2, math.sin(ang) * l0 / 2
    ox1, oy1 = math.cos(ang) * l1 / 2, math.sin(ang) * l1 / 2
    return (f"M{x0 + ox0:.1f} {y0 + oy0:.1f} L{x1 + ox1:.1f} {y1 + oy1:.1f} "
            f"L{x1 - ox1:.1f} {y1 - oy1:.1f} L{x0 - ox0:.1f} {y0 - oy0:.1f} Z")


def jambe(hanche, cheville, talon_leve: float = 0.0, sombre: bool = False) -> str:
    genou = ik(hanche, cheville)
    cx, cy = cheville
    remplissage = "url(#h2)" if sombre else "url(#mol)"
    out = [f'<path d="{membre(hanche, genou, 19, 16)}" fill="{remplissage}" {ST} stroke-width="2.5"/>',
           f'<path d="{membre(genou, cheville, 16, 13)}" fill="{remplissage}" {ST} stroke-width="2.5"/>',
           f'<circle cx="{genou[0]:.1f}" cy="{genou[1]:.1f}" r="7.5" fill="{remplissage}" stroke="none"/>']
    # botte : semelle à plat, pointe vers +x ; talon_leve fait pivoter autour de la pointe
    t = math.radians(talon_leve)
    pts = [(-8, -8), (6, -10), (22, -3), (26, 4), (26, 13), (-10, 13), (-10, 2)]
    pivot = (26, 13)
    rot = []
    for px, py in pts:
        rx, ry = px - pivot[0], py - pivot[1]
        rot.append((pivot[0] + rx * math.cos(t) + ry * math.sin(t), pivot[1] - rx * math.sin(t) + ry * math.cos(t)))
    d = "M" + " L".join(f"{cx + px:.1f} {cy + py:.1f}" for px, py in rot) + " Z"
    out.append(f'<path d="{d}" fill="{ENCRE}" {ST} stroke-width="1.8"/>')
    return "".join(out)


def bras(epaule, angle_deg: float, avant: bool) -> str:
    """Bras pendant de l'épaule, tourné de angle_deg (positif = vers l'avant)."""
    ex, ey = epaule
    a = math.radians(90 - angle_deg)
    coude = (ex + 42 * math.cos(a), ey + 42 * math.sin(a))
    a2 = a - math.radians(18 if avant else 10)          # avant-bras un peu plié vers l'avant
    main = (coude[0] + 40 * math.cos(a2), coude[1] + 40 * math.sin(a2))
    fill = PAPIER if avant else "url(#h2)"
    out = [f'<path d="{membre(epaule, coude, 20, 17)}" fill="{fill}" {ST} stroke-width="2.4"/>',
           f'<path d="{membre(coude, main, 17, 14)}" fill="{fill}" {ST} stroke-width="2.4"/>',
           f'<circle cx="{coude[0]:.1f}" cy="{coude[1]:.1f}" r="7.6" fill="{fill}" stroke="none"/>',
           f'<circle cx="{main[0]:.1f}" cy="{main[1]:.1f}" r="7" fill="{PAPIER}" {ST} stroke-width="1.9"/>']
    if avant:
        out.append(f'<path d="M{ex + 4:.1f} {ey + 12:.1f} L{coude[0] + 3:.1f} {coude[1]:.1f}" stroke="{ENCRE}" stroke-width=".9"/>')
    return "".join(out)


def bras_au_pli(epaule, t: float) -> str:
    """Interagir : la main monte vers le pli (t de 0 à 1)."""
    ex, ey = epaule
    main_bas = (ex + 18, ey + 80)
    main_pli = (ex + 8, ey + 24)
    main = (main_bas[0] + (main_pli[0] - main_bas[0]) * t, main_bas[1] + (main_pli[1] - main_bas[1]) * t)
    # coude posé le long du corps ; l'avant-bras remonte vers le pli en raccourci (vu de profil)
    coude_bas = (ex + 10, ey + 42)
    coude_pli = (ex + 14, ey + 40)
    coude = (coude_bas[0] + (coude_pli[0] - coude_bas[0]) * t, coude_bas[1] + (coude_pli[1] - coude_bas[1]) * t)
    return (f'<path d="{membre(epaule, coude, 20, 17)}" fill="{PAPIER}" {ST} stroke-width="2.4"/>'
            f'<path d="{membre(coude, main, 17, 14)}" fill="{PAPIER}" {ST} stroke-width="2.4"/>'
            f'<circle cx="{coude[0]:.1f}" cy="{coude[1]:.1f}" r="7.6" fill="{PAPIER}" stroke="none"/>'
            f'<circle cx="{main[0]:.1f}" cy="{main[1]:.1f}" r="7" fill="{PAPIER}" {ST} stroke-width="1.9"/>')


# --- buste (repris de la planche de style, jambes et bras retirés) -------------------------
def sacoche(dy: float) -> str:
    return (f'<g transform="translate(0 {dy:.1f})">'
            f'<path d="M78 196 L114 190 L118 238 L82 244 Z" fill="url(#h1)" {ST} stroke-width="2.4"/>'
            f'<path d="M78 196 L114 190 L113 204 L79 210 Z" fill="{PAPIER}" {ST} stroke-width="2.2"/>'
            f'<circle cx="96" cy="206" r="2.6" fill="{ENCRE}"/></g>')


def buste() -> str:
    return (
        # vareuse
        f'<path d="M116 100 Q144 96 156 112 Q166 150 160 196 L164 262 L156 258 L150 268 L142 260 L134 270 L126 260 L118 268 L110 258 L104 264 Q102 220 104 190 Q102 140 116 100 Z" fill="{PAPIER}" {ST} stroke-width="2.8"/>'
        f'<path d="M116 102 Q104 140 106 190 Q104 222 106 262 L118 266 Q114 210 118 150 Q120 120 128 101 Z" fill="url(#h2)" stroke="none"/>'
        # bandoulière, ceinture
        f'<path d="M150 108 L104 198" stroke="{ENCRE}" stroke-width="5.4" fill="none"/>'
        f'<path d="M150 108 L104 198" stroke="{PAPIER}" stroke-width="1.8" fill="none"/>'
        f'<path d="M104 200 Q132 206 162 198" stroke="{ENCRE}" stroke-width="5.4" fill="none" stroke-linecap="round"/>'
        # plaque de coureur
        # plaque de coureur, simplifiée pour se lire à 300 px : grand rectangle clair, un seul trait épais
        f'<rect x="120" y="158" width="22" height="16" fill="{PAPIER}" {ST} stroke-width="2.2" transform="rotate(-6 131 166)"/>'
        f'<path d="M125 167 L137 165.6" stroke="{ENCRE}" stroke-width="3" stroke-linecap="round"/>'
    )


def lanterne(angle: float) -> str:
    return (f'<g transform="rotate({angle:.1f} 164 206)">'
            f'<path d="M160 204 Q168 204 168 214" fill="none" {ST} stroke-width="2"/>'
            f'<path d="M160 214 L176 214 L174 238 L162 238 Z" fill="{PAPIER}" {ST} stroke-width="2.2"/>'
            f'<path d="M163 218 L173 218 L171 234 L165 234 Z" fill="url(#pt)" {ST} stroke-width="1.1"/>'
            f'<path d="M158 214 L178 214 M160 240 L176 240" stroke="{ENCRE}" stroke-width="2.6"/></g>')


def tete() -> str:
    return (
        f'<path d="M114 104 Q106 70 122 50 Q142 34 160 50 Q170 62 168 82 Q166 98 156 108 Q136 114 114 104 Z" fill="url(#h2)" {ST} stroke-width="2.8"/>'
        f'<path d="M146 60 Q160 58 164 70 Q166 86 158 98 Q150 102 144 96 Q140 80 146 60 Z" fill="{PAPIER}" {ST} stroke-width="2"/>'
        f'<path d="M154 76 L160 75" stroke="{ENCRE}" stroke-width="2.4" stroke-linecap="round"/>'
        f'<path d="M162 78 L166 86 L161 87" fill="none" {ST} stroke-width="1.6"/>'
        f'<path d="M156 93 L161 92" stroke="{ENCRE}" stroke-width="1.6" stroke-linecap="round"/>'
        # cloche sans battant au col
        # cloche sans battant, simplifiée : forme d'encre pleine, bouche vide en papier (aucun battant)
        f'<path d="M140 104 L140 110" stroke="{ENCRE}" stroke-width="2"/>'
        f'<path d="M131 126 Q132 110 140 110 Q148 110 149 126 Z" fill="{ENCRE}" {ST} stroke-width="2"/>'
        f'<ellipse cx="140" cy="126" rx="9" ry="2.6" fill="{PAPIER}" {ST} stroke-width="1.6"/>'
    )


# Le pli et son sceau de cire noire, portés sur la poitrine PAR-DESSUS le bras : c'est l'objet
# du jeu, il doit rester lisible à chaque image (le ruban rouge est sur le calque _red).
PLI = (f'<path d="M138 128 L160 124 L162 150 L140 154 Z" fill="{PAPIER}" {ST} stroke-width="2.2"/>'
       f'<circle cx="151" cy="139" r="5.2" fill="{ENCRE}"/>')

RUBAN = (f'<path d="M150 126 L152 152" stroke="{ROUGE}" stroke-width="2.8" stroke-linecap="round"/>'
         f'<path d="M152 152 L148 166 M152 152 L157 165" stroke="{ROUGE}" stroke-width="2.2" stroke-linecap="round"/>')
CENDRE = f'<path d="M152 66 Q157 63 160 68" stroke="#4A463D" stroke-width="3.4" fill="none" stroke-linecap="round"/>'


# --- une pose -------------------------------------------------------------------------------
def pose(bob: float, pied_arr, pied_av, bras_arr: float, bras_av, lant: float, sac: float,
         penche: float = 0.0, voute: float = 0.0) -> dict[str, str]:
    """Renvoie les trois calques d'une image, dans le repère de la planche de style.

    pied_* = (dx, dy, talon) : cheville relative à la hanche au repos, en px planche.
    bras_av = angle (float) ou ("pli", t) pour interagir.
    """
    hx, hy = HANCHE[0], HANCHE[1] + bob
    def cheville(p):
        return (hx + p[0], CHEVILLE_Y + p[1])
    # penche : le buste bascule vers l'avant autour des hanches ; voute : la tête rentre dans les épaules
    haut = f'<g transform="translate(0 {bob:.1f}) rotate({penche:.1f} {hx:.1f} {HANCHE[1]:.1f})">'
    base = [jambe((hx - 6, hy), cheville(pied_arr), pied_arr[2], sombre=True),
            haut, bras((118, 122), bras_arr, avant=False), sacoche(sac), buste(), '</g>',
            jambe((hx + 6, hy), cheville(pied_av), pied_av[2]),
            haut, lanterne(lant)]
    if isinstance(bras_av, tuple):
        base.append(bras_au_pli((146, 118), bras_av[1]))
        base.append(PLI)
        t = bras_av[1]
        mx, my = 146 + 18 + (8 - 18) * t, 118 + 80 + (24 - 80) * t
        base.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="7" fill="{PAPIER}" {ST} stroke-width="1.9"/>')
    else:
        base.append(bras((146, 118), bras_av, avant=True))
        base.append(PLI)
    base += [f'<g transform="translate({voute * 0.6:.1f} {voute:.1f})">', tete(), '</g>', '</g>']
    ruban = RUBAN
    if isinstance(bras_av, tuple):
        # interagir : la main se pose sur le pli, devant lui et devant le ruban
        ex, ey = 146, 118
        t = bras_av[1]
        mx, my = ex + 18 + (8 - 18) * t, ey + 80 + (24 - 80) * t
        mid = "main" + f"{t:.2f}".replace(".", "")
        ruban = (f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="240" height="420">'
                 f'<rect x="0" y="0" width="240" height="420" fill="#fff"/>'
                 f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="8.2" fill="#000"/></mask>'
                 f'<g mask="url(#{mid})">{RUBAN}</g>')
    return {"base": "".join(base),
            "red": f'{haut}{ruban}</g>',
            "cendre": f'{haut}<g transform="translate({voute * 0.6:.1f} {voute:.1f})">{CENDRE}</g></g>'}


def marche(i: int, n: int = 8) -> dict[str, str]:
    """Cycle de marche : chaque pied passe la moitié du cycle au sol (recule) et l'autre en l'air."""
    def pied(phase: float):
        phase %= 1.0
        if phase < 0.5:                                   # appui : recule de +F à -F, au sol
            u = phase / 0.5
            x = FOULEE - 2 * FOULEE * u
            talon = 0.0 if u < 0.75 else (u - 0.75) / 0.25 * 18
            return (x, 0.0, talon)
        u = (phase - 0.5) / 0.5                          # envol : avance de -F à +F, lève le pied
        x = -FOULEE + 2 * FOULEE * (0.5 - 0.5 * math.cos(math.pi * u))
        return (x, -22 * math.sin(math.pi * u), 18 * (1 - u) ** 2)
    ph = i / n
    pa, pv = pied(ph + 0.5), pied(ph)
    bob = -3.5 * abs(math.cos(2 * math.pi * ph))         # plus haut au passage des jambes
    swing = 16 * math.sin(2 * math.pi * ph)
    # coureur pressé et transi : buste penché de 7°, tête rentrée, bras libre qui balance franchement
    return pose(bob + 2, pa, pv, swing * 1.3, -swing * 1.5, -6 * math.sin(2 * math.pi * ph + 0.6), 1.5 * math.sin(2 * math.pi * ph),
                penche=7, voute=4)


def repos(i: int) -> dict[str, str]:
    souffle = (0, -1, -2, -1)[i]
    return pose(souffle, (-12, 0, 0), (14, 0, 0), 2, -3 + souffle * 0.5, 0, 0, penche=2, voute=2)


def interagir(i: int) -> dict[str, str]:
    t = (0.35, 0.75, 1.0)[i]
    return pose(0, (-12, 0, 0), (14, 0, 0), 2, ("pli", t), 0, 0)


ANIMS = {"repos": (repos, 4), "marche": (marche, 8), "interagir": (interagir, 3)}


def planche(images: list[str]) -> str:
    n = len(images)
    corps = []
    for i, contenu in enumerate(images):
        # hanche (134) -> x 100 ; sol planche (405) -> y 316
        tx = i * CADRE_L + 100 - HANCHE[0] * ECHELLE
        ty = 316 - SOL_PLANCHE * ECHELLE
        corps.append(f'<g transform="translate({tx:.2f} {ty:.2f}) scale({ECHELLE})">{contenu}</g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{CADRE_L * n}" height="{CADRE_H}" '
            f'viewBox="0 0 {CADRE_L * n} {CADRE_H}">{DEFS}{"".join(corps)}</svg>\n')


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    for nom, (f, n) in ANIMS.items():
        poses = [f(i) for i in range(n)]
        (DST / f"chr_tobie_{nom}_01.svg").write_text(planche([p["base"] for p in poses]), encoding="utf-8")
        (DST / f"chr_tobie_{nom}_01_red.svg").write_text(planche([p["red"] for p in poses]), encoding="utf-8")
        (DST / f"chr_tobie-cendre_{nom}_01.svg").write_text(planche([p["cendre"] for p in poses]), encoding="utf-8")
    print(f"{len(ANIMS) * 3} planches dans {DST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
