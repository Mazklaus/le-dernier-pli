#!/usr/bin/env python3
"""Génère les cinq gravures d'épilogue de l'étape 7 : art/src/cin/cin_epilogue-<a..e>.svg.

Plein écran fixe (1920 x 1080) : la gravure est tirée dans un cadre, en haut, et le bas reste au
papier pour le carton de texte (e7_epilogues.dialogue, 4 à 5 lignes). Les lettres suivent la table
du Sound Designer (tools/son/README.md) ; les noms des fins n'apparaissent dans aucun nom de fichier.
La variante c reprend la composition de b.

Grammaire : encre, lavis, mine sur papier, hachures nettes, aucun dégradé ni flou (le flou d'un
premier plan se dit par un contour doublé). Le rouge n'est que le ruban.

Usage : python3 tools/gen_cin_epilogues.py
"""
from __future__ import annotations

import math
from pathlib import Path

from gen_decors_e1_surface import DEFS, ENCRE, LAVIS, MINE, PAPIER, ROUGE, rnd

ROOT = Path(__file__).resolve().parent.parent
DST = ROOT / "art" / "src" / "cin"
W, H = 1920, 1080
# cadre de la gravure ; le carton de texte se pose sous lui (y 800 à 1040)
CX0, CY0, CX1, CY1 = 150, 50, 1770, 770
ST = f'stroke="{ENCRE}" fill="none"'

DEFS_CIN = DEFS.replace("</defs>", (
    f'<pattern id="h3" width="3" height="3" patternUnits="userSpaceOnUse" patternTransform="rotate(-52)">'
    f'<rect width="3" height="3" fill="{PAPIER}"/><line x1="0" y1="0" x2="0" y2="3" stroke="{ENCRE}" stroke-width="1.2"/>'
    f'<line x1="0" y1="1.5" x2="3" y2="1.5" stroke="{ENCRE}" stroke-width="1"/></pattern>'
    f'<pattern id="v3" width="3" height="3" patternUnits="userSpaceOnUse" patternTransform="rotate(-52)">'
    f'<line x1="0" y1="0" x2="0" y2="3" stroke="{ENCRE}" stroke-width="1.2"/><line x1="0" y1="1.5" x2="3" y2="1.5" stroke="{ENCRE}" stroke-width="1"/></pattern>'
    f'<pattern id="pierre" width="90" height="60" patternUnits="userSpaceOnUse"><rect width="90" height="60" fill="{PAPIER}"/>'
    f'<path d="M6 14 l20 -3 M40 40 l26 4 M60 12 l14 2 M12 48 l10 -2" stroke="{MINE}" stroke-width="1.4"/>'
    f'<circle cx="74" cy="30" r="1.6" fill="{MINE}"/><circle cx="24" cy="30" r="1.2" fill="{LAVIS}"/></pattern>'
    f'<clipPath id="cadre"><rect x="{CX0}" y="{CY0}" width="{CX1 - CX0}" height="{CY1 - CY0}"/></clipPath>'
    "</defs>"))


def planche(contenu: str) -> str:
    """Le papier, la gravure tirée dans son cadre (filet double), le carton vide en dessous."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{DEFS_CIN}'
            f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>'
            f'<g clip-path="url(#cadre)">{contenu}</g>'
            f'<rect x="{CX0}" y="{CY0}" width="{CX1 - CX0}" height="{CY1 - CY0}" {ST} stroke-width="5"/>'
            f'<rect x="{CX0 - 14}" y="{CY0 - 14}" width="{CX1 - CX0 + 28}" height="{CY1 - CY0 + 28}" {ST} stroke-width="1.6"/>'
            f'</svg>\n')


def ruban(d: str, epais: float = 9) -> str:
    """Le ruban rouge : un aplat rouge cerné d'encre fine (lisible à la détection du rouge)."""
    return (f'<path d="{d}" fill="none" stroke="{ENCRE}" stroke-width="{epais + 4}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{ROUGE}" stroke-width="{epais}" stroke-linecap="round" stroke-linejoin="round"/>')


def cire(cx: float, cy: float, r: float, ang: float = 0.0) -> str:
    """Un cachet de cire noire vu de dessus : galette irrégulière, empreinte de la cloche sans battant."""
    rr = rnd(int(cx + cy))
    pts = []
    for k in range(18):
        a = 2 * math.pi * k / 18
        rk = r * rr.uniform(.9, 1.08)
        pts.append(f"{cx + rk * math.cos(a):.1f} {cy + rk * .62 * math.sin(a):.1f}")
    return (f'<path d="M{" L".join(pts)} Z" fill="{ENCRE}"/>'
            f'<path d="M{cx - r * .32:.0f} {cy + r * .18:.0f} Q{cx - r * .3:.0f} {cy - r * .3:.0f} {cx:.0f} {cy - r * .34:.0f} '
            f'Q{cx + r * .3:.0f} {cy - r * .3:.0f} {cx + r * .32:.0f} {cy + r * .18:.0f} Z" fill="none" stroke="{LAVIS}" stroke-width="2.4"/>')


# --- a : la grande cloche vue d'en dessous --------------------------------------------------

def epilogue_a() -> str:
    r = rnd(71)
    out = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#h1)"/>']
    # la cloche : flancs qui montent hors du cadre, lèvre épaisse, bouche opaque
    bx, by, rx, ry = 960, 400, 760, 150
    out.append(f'<path d="M{bx - rx} {by} C{bx - rx + 60} {by - 200} {bx - 430} {by - 300} {bx - 380} {CY0 - 40} '
               f'L{bx + 380} {CY0 - 40} C{bx + 430} {by - 300} {bx + rx - 60} {by - 200} {bx + rx} {by} Z" fill="url(#h2)" {ST} stroke-width="5"/>')
    # cerclages du bronze
    for k, y in enumerate((by - 120, by - 70)):
        dx = rx - 50 - k * 40
        out.append(f'<path d="M{bx - dx} {y} Q{bx} {y + 70} {bx + dx} {y}" {ST} stroke-width="4"/>')
        out.append(f'<path d="M{bx - dx} {y + 12} Q{bx} {y + 82} {bx + dx} {y + 12}" {ST} stroke-width="1.6"/>')
    # lèvre et bouche : un ovale d'encre pleine, rien ne s'y lit
    out.append(f'<ellipse cx="{bx}" cy="{by}" rx="{rx}" ry="{ry}" fill="url(#h3)" {ST} stroke-width="5"/>')
    out.append(f'<ellipse cx="{bx}" cy="{by + 8}" rx="{rx - 50}" ry="{ry - 34}" fill="{ENCRE}"/>')
    # sous la cloche : le sol de pierre en perspective, la plaque, le ruban défait, la cire brisée
    sol = 600
    out.append(f'<path d="M{CX0} {sol} L{CX1} {sol} L{CX1} {CY1} L{CX0} {CY1} Z" fill="url(#pierre)" {ST} stroke-width="3"/>')
    for x in range(CX0 - 400, CX1 + 400, 180):
        out.append(f'<path d="M{960 + (x - 960) * .35:.0f} {sol} L{x} {CY1}" {ST} stroke-width="1.6"/>')
    for y in (630, 670, 720):
        out.append(f'<path d="M{CX0} {y} H{CX1}" {ST} stroke-width="1.4"/>')
    # l'ombre portée de la cloche sur le sol (contre-hachure, bord net)
    out.append(f'<ellipse cx="960" cy="{sol + 30}" rx="700" ry="40" fill="url(#v2)"/>')
    # plaque de bronze sur un socle, noms gravés ; le dernier plus net
    px, py, pw, ph = 1180, 470, 320, 200
    out.append(f'<rect x="{px - 20}" y="{py + ph - 10}" width="{pw + 40}" height="40" fill="url(#pierre)" {ST} stroke-width="3"/>')
    out.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="url(#h1)" {ST} stroke-width="4"/>')
    out.append(f'<rect x="{px + 10}" y="{py + 10}" width="{pw - 20}" height="{ph - 20}" {ST} stroke-width="1.4"/>')
    for k in range(9):
        y = py + 28 + k * 17
        lg = r.randint(150, 260)
        if k < 8:  # noms usés : traits de mine, interrompus
            x = px + 30
            while x < px + 30 + lg:
                seg = r.randint(14, 40)
                out.append(f'<path d="M{x} {y} h{seg}" stroke="{MINE}" stroke-width="2.4"/>')
                x += seg + r.randint(4, 10)
        else:  # le dernier : net, en encre, frais
            out.append(f'<path d="M{px + 30} {y} h{lg}" stroke="{PAPIER}" stroke-width="5"/>')
            for xs in range(px + 34, px + 30 + lg, 12):
                out.append(f'<path d="M{xs} {y - 5} l4 10" stroke="{ENCRE}" stroke-width="1.8"/>')
            out.append(f'<path d="M{px + 30} {y + 6} h{lg}" stroke="{ENCRE}" stroke-width="1.2"/>')
    # le ruban défait sur les dalles, et le cachet brisé en deux
    out.append(ruban("M520 700 C580 640 660 690 700 660 S800 610 860 650 C900 676 940 700 1000 690 C1040 684 1060 712 1100 724", 10))
    out.append(ruban("M640 735 C660 712 700 724 730 704", 8))
    out.append(f'<g transform="rotate(-14 760 690)">{cire(740, 690, 34)}</g>')
    out.append(f'<path d="M742 668 L752 690 L744 712" stroke="{PAPIER}" stroke-width="5" fill="none"/>')
    out.append(f'<g transform="translate(30 6) rotate(18 790 700)"><path d="M760 680 Q800 668 820 690 Q812 714 772 712 Z" fill="{ENCRE}"/></g>')
    return planche("".join(out))


# --- b et c : la table de pierre, le moule, la main ------------------------------------------

def table_pierre() -> str:
    out = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#v2)"/>',
           f'<rect x="0" y="0" width="{W}" height="{H}" fill="{LAVIS}" opacity=".55"/>']
    # le plateau, vu de haut en oblique, qui sort du cadre par le bas
    out.append(f'<path d="M260 330 L1660 300 L1820 {CY1 + 40} L100 {CY1 + 40} Z" fill="url(#pierre)" {ST} stroke-width="5"/>')
    out.append(f'<path d="M260 330 L1660 300" {ST} stroke-width="9"/>')
    out.append(f'<path d="M300 352 L1630 324" {ST} stroke-width="1.4"/>')
    # la lumière vient d'en haut à droite : voile de hachure sur la moitié gauche du plateau
    out.append(f'<path d="M260 330 L700 320 L560 {CY1 + 40} L100 {CY1 + 40} Z" fill="url(#v1)"/>')
    return "".join(out)


def main_ouverte(x: float, y: float) -> str:
    """La main droite de Tobie, ouverte, paume vers le ciel, posée à plat ; la manche de toile
    huilée sort du cadre à gauche. Rien d'autre de lui. Doigts détendus, légèrement repliés."""
    doigts = []
    # (base x, base y, longueur, angle en degrés, largeur) : index, majeur, annulaire, auriculaire
    for bx, by, lg, ang, lw in ((96, 6, 96, -14, 22), (104, 30, 104, -2, 23), (98, 54, 94, 10, 21), (84, 76, 74, 22, 18)):
        rad = math.radians(ang)
        ex, ey = bx + lg * math.cos(rad), by + lg * math.sin(rad)
        nx, ny = -math.sin(rad) * lw / 2, math.cos(rad) * lw / 2
        # phalanges : deux plis, le bout arrondi qui remonte un peu (doigt replié vers le ciel)
        doigts.append(f'<path d="M{bx - nx:.1f} {by - ny:.1f} L{ex - nx:.1f} {ey - ny:.1f} '
                      f'Q{ex + lw * .7 * math.cos(rad):.1f} {ey + lw * .7 * math.sin(rad):.1f} {ex + nx:.1f} {ey + ny:.1f} '
                      f'L{bx + nx:.1f} {by + ny:.1f}" fill="{PAPIER}" {ST} stroke-width="3.4" stroke-linejoin="round"/>')
        for t in (.42, .74):
            jx, jy = bx + lg * t * math.cos(rad), by + lg * t * math.sin(rad)
            doigts.append(f'<path d="M{jx - nx * .7:.1f} {jy - ny * .7:.1f} Q{jx + 3 * math.cos(rad):.1f} {jy + 3 * math.sin(rad):.1f} {jx + nx * .7:.1f} {jy + ny * .7:.1f}" {ST} stroke-width="1.4"/>')
    return (f'<g transform="translate({x} {y})">'
            # ombre portée sur la pierre (contre-hachure nette, décalée vers le bas)
            f'<path d="M-110 112 L90 104 Q200 100 210 130 Q190 160 120 158 L-110 142 Z" fill="url(#v2)"/>'
            # manche
            f'<path d="M-520 30 L-130 -6 Q-104 46 -116 104 L-520 150 Z" fill="url(#h2)" {ST} stroke-width="4"/>'
            f'<path d="M-150 -4 Q-126 48 -138 104" {ST} stroke-width="3"/>'
            f'<path d="M-420 40 Q-300 60 -200 30 M-430 110 Q-320 100 -230 120" {ST} stroke-width="1.6"/>'
            # paume, vue de dessus, creusée
            f'<path d="M-122 6 Q-60 -8 10 -6 Q70 -4 100 0 L106 88 Q60 108 -10 104 Q-80 102 -120 96 Z" fill="{PAPIER}" {ST} stroke-width="4"/>'
            + "".join(doigts) +
            # pouce, côté loin, qui s'écarte
            f'<path d="M-10 -4 Q16 -46 56 -60 Q82 -66 88 -48 Q84 -30 56 -22 Q36 -14 30 -2" fill="{PAPIER}" {ST} stroke-width="3.6"/>'
            f'<path d="M52 -48 Q62 -50 70 -44" {ST} stroke-width="1.4"/>'
            # lignes de la main et le creux (une hachure légère au centre)
            f'<path d="M-20 14 Q30 34 96 26 M-40 44 Q20 62 98 54 M-60 80 Q-20 60 6 20" {ST} stroke-width="1.8"/>'
            f'<ellipse cx="20" cy="52" rx="44" ry="24" fill="url(#v1)"/>'
            f'</g>')


def moule(cx: float, cy: float, brise: bool) -> str:
    """Le moule à sceaux, en fer : deux mâchoires montées sur charnière, l'empreinte de la cloche au
    fond. Brisé : deux moitiés écartées, la cire coulée entre elles. Intact : renversé, fermé."""
    if brise:
        g = (f'<g transform="translate({cx - 120} {cy}) rotate(-16)">'
             f'<path d="M-90 -40 L60 -46 L66 40 L-84 46 Z" fill="url(#h3)" {ST} stroke-width="4"/>'
             f'<path d="M60 -46 L50 -10 L70 4 L58 40" fill="none" stroke="{PAPIER}" stroke-width="5"/>'
             f'<ellipse cx="-14" cy="0" rx="40" ry="26" fill="{LAVIS}" {ST} stroke-width="3"/>'
             f'<path d="M-30 12 Q-30 -12 -14 -14 Q2 -12 2 12 Z" fill="none" stroke="{PAPIER}" stroke-width="2.4"/>'
             f'<path d="M-90 -10 L-150 -14 L-150 6 L-90 10" fill="url(#h2)" {ST} stroke-width="3"/></g>'
             f'<g transform="translate({cx + 130} {cy + 24}) rotate(22)">'
             f'<path d="M-66 -44 L90 -40 L84 44 L-58 40 Z" fill="url(#h3)" {ST} stroke-width="4"/>'
             f'<path d="M-66 -44 L-54 -6 L-72 8 L-58 40" fill="none" stroke="{PAPIER}" stroke-width="5"/>'
             f'<ellipse cx="14" cy="0" rx="40" ry="26" fill="{LAVIS}" {ST} stroke-width="3"/>'
             f'<path d="M90 -10 L150 -6 L150 14 L88 10" fill="url(#h2)" {ST} stroke-width="3"/></g>')
        # la cire noire coulée entre les moitiés, figée en coulure jusqu'au bord
        cire_coulee = (f'<path d="M{cx - 70} {cy + 10} Q{cx - 20} {cy - 20} {cx + 40} {cy + 10} Q{cx + 70} {cy + 40} {cx + 40} {cy + 70} '
                       f'Q{cx + 20} {cy + 110} {cx + 50} {cy + 170} Q{cx + 60} {cy + 196} {cx + 36} {cy + 200} Q{cx + 10} {cy + 190} {cx + 14} {cy + 150} '
                       f'Q{cx + 4} {cy + 100} {cx - 40} {cy + 70} Q{cx - 90} {cy + 40} {cx - 70} {cy + 10} Z" fill="{ENCRE}"/>'
                       f'<path d="M{cx - 30} {cy + 6} Q{cx} {cy - 4} {cx + 24} {cy + 12}" stroke="{LAVIS}" stroke-width="3" fill="none"/>')
        return cire_coulee + g
    return (f'<g transform="translate({cx} {cy}) rotate(-6)">'
            f'<path d="M-130 -52 L130 -58 L140 50 L-124 58 Z" fill="url(#h3)" {ST} stroke-width="5"/>'
            f'<path d="M-128 -2 L136 -6" {ST} stroke-width="3"/>'
            f'<path d="M130 -58 L200 -64 L206 -40 L136 -34" fill="url(#h2)" {ST} stroke-width="3"/>'
            f'<circle cx="-100" cy="-28" r="7" fill="{PAPIER}" {ST} stroke-width="2.4"/>'
            f'<circle cx="104" cy="28" r="7" fill="{PAPIER}" {ST} stroke-width="2.4"/></g>')


def epilogue_b() -> str:
    out = [table_pierre(), moule(980, 470, brise=True), main_ouverte(560, 560)]
    # le ruban posé, intact, en boucle, à droite du moule
    out.append(ruban("M1270 600 C1330 560 1420 570 1440 620 C1456 664 1400 690 1350 668 C1310 650 1320 600 1380 590 "
                     "C1450 580 1520 620 1580 610", 11))
    return planche("".join(out))


def main_serree(x: float, y: float, ang: float) -> str:
    """La main de Tobie serrée sur la corde (corde inclinée de ang degrés)."""
    return (f'<g transform="translate({x} {y}) rotate({ang})">'
            f'<path d="M-60 -380 L-60 60 Q-40 70 -20 60 L-20 -380 Z" fill="none"/>'
            f'<path d="M-900 -150 L-60 -40 Q-50 0 -60 44 L-900 160 Z" fill="url(#h2)" {ST} stroke-width="4"/>'
            f'<path d="M-80 -42 Q-70 0 -80 46" {ST} stroke-width="3"/>'
            f'<path d="M-64 -40 Q-30 -54 10 -46 Q40 -40 44 -18 L44 26 Q40 50 10 54 Q-30 58 -64 44 Z" fill="{PAPIER}" {ST} stroke-width="4"/>'
            # doigts repliés sur la corde : quatre jointures
            + "".join(f'<path d="M14 {yy} Q44 {yy + 2} 44 {yy + 14} Q40 {yy + 24} 14 {yy + 22}" fill="{PAPIER}" {ST} stroke-width="3"/>'
                      for yy in (-44, -22, 0, 22))
            + f'<path d="M-40 -46 Q-20 -76 14 -70 Q30 -64 24 -48" fill="{PAPIER}" {ST} stroke-width="3.4"/>'
            f'</g>')


def epilogue_c() -> str:
    r = rnd(73)
    out = [table_pierre(), moule(980, 470, brise=False)]
    # la corde de la grande cloche, tendue en diagonale depuis le haut du cadre
    x0, y0, x1, y1 = 1600, CY0 - 40, 470, CY1 + 40
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0)) - 90
    out.append(f'<path d="M{x0} {y0} L{x1} {y1}" stroke="{ENCRE}" stroke-width="34" stroke-linecap="butt"/>')
    out.append(f'<path d="M{x0} {y0} L{x1} {y1}" stroke="{PAPIER}" stroke-width="24"/>')
    n = 40
    for k in range(n):
        t = k / n
        cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        out.append(f'<path d="M{cx - 12:.0f} {cy - 8:.0f} L{cx + 10:.0f} {cy + 10:.0f}" stroke="{ENCRE}" stroke-width="3"/>')
    # la main serrée sur la corde, aux deux tiers
    t = .78
    out.append(main_serree(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, ang))
    # le son : ondes en arcs de hachure nets qui partent du haut de la corde
    for k, rr in enumerate((180, 300, 440, 600)):
        motif = "v2" if k % 2 == 0 else "v1"
        out.append(f'<path d="M{x0 - rr} {y0} A{rr} {rr} 0 0 0 {x0 + rr} {y0} L{x0 + rr - 40} {y0} A{rr - 40} {rr - 40} 0 0 1 {x0 - rr + 40} {y0} Z" fill="url(#{motif})"/>')
        out.append(f'<path d="M{x0 - rr} {y0} A{rr} {rr} 0 0 0 {x0 + rr} {y0}" {ST} stroke-width="2.4" stroke-dasharray="{18 + k * 6} 10"/>')
    # poussière et gouttes de cire qui tombent d'en haut
    for _ in range(90):
        px, py = r.randint(CX0, CX1), r.randint(CY0, 640)
        out.append(f'<circle cx="{px}" cy="{py}" r="{r.uniform(1.2, 3):.1f}" fill="{PAPIER}" stroke="{ENCRE}" stroke-width=".8"/>')
    for _ in range(14):
        px, py = r.randint(400, 1700), r.randint(CY0 + 40, 600)
        out.append(f'<path d="M{px} {py} q-6 12 0 18 q6 -6 0 -18 Z" fill="{ENCRE}"/>')
        out.append(f'<path d="M{px} {py - 30} v22" stroke="{ENCRE}" stroke-width="1" stroke-dasharray="3 4"/>')
    return planche("".join(out))


# --- d : l'étagère des plis ----------------------------------------------------------------

def pli(x: float, y: float, s: float, neuf: bool) -> str:
    """Un pli vu de face, debout sur l'étagère : papier plié, cachet noir, ruban.
    Les anciens : papier jauni (hachure), ruban passé (lavis, plus rouge). Le sien : papier net,
    ruban rouge."""
    w, h = 120 * s, 160 * s
    fond = PAPIER if neuf else "url(#h1)"
    trait = 4 if neuf else 2.6
    out = [f'<path d="M{x} {y} L{x + w} {y} L{x + w} {y - h} L{x} {y - h} Z" fill="{fond}" {ST} stroke-width="{trait}"/>',
           f'<path d="M{x} {y - h} L{x + w / 2} {y - h * .62} L{x + w} {y - h}" {ST} stroke-width="{trait * .7:.1f}"/>']
    if neuf:
        out.append(ruban(f"M{x + w / 2} {y} V{y - h}", 7 * s))
    else:
        out.append(f'<path d="M{x + w / 2} {y} V{y - h}" stroke="{ENCRE}" stroke-width="{10 * s:.1f}"/>'
                   f'<path d="M{x + w / 2} {y} V{y - h}" stroke="{MINE}" stroke-width="{6 * s:.1f}"/>')
    out.append(f'<ellipse cx="{x + w / 2}" cy="{y - h * .58}" rx="{20 * s:.1f}" ry="{18 * s:.1f}" fill="{ENCRE}"/>')
    out.append(f'<path d="M{x + w / 2 - 7 * s:.1f} {y - h * .54:.1f} Q{x + w / 2 - 7 * s:.1f} {y - h * .64:.1f} {x + w / 2:.1f} {y - h * .65:.1f} '
               f'Q{x + w / 2 + 7 * s:.1f} {y - h * .64:.1f} {x + w / 2 + 7 * s:.1f} {y - h * .54:.1f}" {ST.replace(ENCRE, LAVIS)} stroke-width="1.6"/>')
    return "".join(out)


def epilogue_d() -> str:
    out = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#v2)"/>',
           f'<rect x="0" y="0" width="{W}" height="{H}" fill="{ENCRE}" opacity=".35"/>']
    # l'étagère : une planche qui file vers la gauche et se perd dans le noir (point de fuite x 120)
    fx, fy = 120, 360
    out.append(f'<path d="M{CX1 + 20} 620 L{fx} {fy + 8} L{fx} {fy + 14} L{CX1 + 20} 660 Z" fill="url(#h2)" {ST} stroke-width="4"/>')
    out.append(f'<path d="M{CX1 + 20} 660 L{fx} {fy + 14} L{fx} {fy + 30} L{CX1 + 20} 720 Z" fill="{ENCRE}"/>')
    # treize anciens et le sien, au bout du rang (devant), tous de même taille réelle
    n = 14
    for k in range(n):
        t = (k / (n - 1)) ** 1.6       # du fond (0) au plus proche (1)
        s = .28 + .82 * t
        x = fx + (1500 - fx) * t
        y = fy + 8 + (620 - fy - 8) * (x - fx) / (CX1 + 20 - fx)
        out.append(pli(x - 60 * s, y, s, neuf=(k == n - 1)))
    # le noir avale le fond : voile net au-delà du sixième pli
    for x_cran, op in ((760, .25), (520, .35), (330, .45)):
        out.append(f'<rect x="0" y="0" width="{x_cran}" height="{H}" fill="{ENCRE}" opacity="{op}"/>')
    return planche("".join(out))


# --- e : depuis le fond d'une tranchée ------------------------------------------------------

def epilogue_e() -> str:
    """Vu du fond de la tranchée, en contre-plongée : le parapet coupe le cadre, le ciel blanc
    au-dessus (contre-jour). Une silhouette pâle sort de la terre au bord, de dos, tête basse sous le
    capuchon ; il lui reste un bout de ruban au poignet. Au premier plan, le canon d'un fusil levé,
    hors de net : contour doublé, jamais de flou."""
    r = rnd(75)
    par = 420                                   # bord du parapet, vu d'en bas
    out = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPIER}"/>']
    # le ciel : quelques traits de mine horizontaux, rien d'autre
    for _ in range(10):
        y = r.randint(CY0 + 20, par - 140)
        x = r.randint(CX0, CX1 - 300)
        out.append(f'<path d="M{x} {y} h{r.randint(160, 520)}" stroke="{MINE}" stroke-width="1.4"/>')
    # la silhouette, de dos : torse qui sort de la terre, épaules, capuchon baissé
    sx, sy = 1040, par + 6
    corps = (f"M{sx - 130} {sy} Q{sx - 132} {sy - 120} {sx - 112} {sy - 180} Q{sx - 96} {sy - 214} {sx - 54} {sy - 226} "
             f"Q{sx - 60} {sy - 270} {sx - 44} {sy - 300} Q{sx - 18} {sy - 338} {sx + 18} {sy - 336} "
             f"Q{sx + 54} {sy - 330} {sx + 62} {sy - 290} Q{sx + 66} {sy - 254} {sx + 56} {sy - 226} "
             f"Q{sx + 100} {sy - 214} {sx + 118} {sy - 176} Q{sx + 136} {sy - 120} {sx + 132} {sy} Z")
    out.append(f'<path d="{corps}" fill="{PAPIER}" {ST} stroke-width="4"/>')
    # plis du capuchon et de la toile, ombre propre du côté opposé au jour (hachure fine)
    out.append(f'<path d="M{sx - 54} {sy - 226} Q{sx} {sy - 206} {sx + 56} {sy - 226}" {ST} stroke-width="2.6"/>')
    out.append(f'<path d="M{sx + 4} {sy - 334} Q{sx + 12} {sy - 280} {sx + 2} {sy - 228}" {ST} stroke-width="1.6"/>')
    out.append(f'<path d="M{sx + 56} {sy - 226} Q{sx + 100} {sy - 214} {sx + 118} {sy - 176} Q{sx + 136} {sy - 120} {sx + 132} {sy} L{sx + 70} {sy} Q{sx + 80} {sy - 120} {sx + 56} {sy - 226} Z" fill="url(#v1)"/>')
    out.append(f'<path d="M{sx - 20} {sy - 190} Q{sx - 10} {sy - 100} {sx - 30} {sy} M{sx + 40} {sy - 170} Q{sx + 50} {sy - 90} {sx + 36} {sy}" {ST} stroke-width="1.6"/>')
    # bras gauche tendu vers le parapet, la main agrippée à la terre ; le ruban au poignet
    BRAS = (f'<path d="M{sx - 112} {sy - 170} Q{sx - 200} {sy - 110} {sx - 270} {sy + 50} L{sx - 240} {sy + 62} Q{sx - 176} {sy - 70} {sx - 100} {sy - 128} Z" fill="{PAPIER}" {ST} stroke-width="3.6"/>'
            f'<path d="M{sx - 300} {sy + 70} Q{sx - 280} {sy + 44} {sx - 250} {sy + 46} Q{sx - 222} {sy + 52} {sx - 224} {sy + 78} Z" fill="{PAPIER}" {ST} stroke-width="3.4"/>'
            f'<path d="M{sx - 300} {sy + 70} l-14 26 M{sx - 284} {sy + 76} l-8 30 M{sx - 266} {sy + 80} l-2 30 M{sx - 248} {sy + 80} l6 28" {ST} stroke-width="5" stroke-linecap="round"/>'
            + ruban(f"M{sx - 262} {sy + 22} q16 8 30 6 M{sx - 246} {sy + 30} q4 20 -6 36", 6))
    # la terre qui tombe des épaules et du bras
    for _ in range(46):
        dx, dy = r.randint(-150, 150), r.randint(-220, -10)
        out.append(f'<circle cx="{sx + dx}" cy="{sy + dy}" r="{r.uniform(1.6, 4.4):.1f}" fill="{LAVIS}"/>')
    for _ in range(10):
        dx = r.randint(-130, 130)
        y0 = sy - r.randint(60, 200)
        out.append(f'<path d="M{sx + dx} {y0} v{r.randint(30, 70)}" stroke="{LAVIS}" stroke-width="1.6" stroke-dasharray="3 6"/>')
    # le parapet : bord de terre déchiré (le bras, posé dessus, est dessiné après), sacs, puis la paroi de la tranchée dans l'ombre
    bord = " L".join(f"{x} {par + r.randint(-10, 10)}" for x in range(CX1 + 40, CX0 - 41, -60))
    out.append(f'<path d="M{CX0 - 40} {H} L{CX1 + 40} {H} L{bord} Z" fill="url(#terre)" {ST} stroke-width="4"/>')
    # pas de sacs : la paroi est de terre nue, la silhouette en sort ; monticule et lèvres de terre
    # rabattues sur le torse (enfouie jusqu'à la poitrine), fissures qui rayonnent
    butte = (f'M{sx - 330} {par + 6} Q{sx - 220} {par - 90} {sx - 120} {sy - 96} Q{sx} {sy - 120} {sx + 124} {sy - 92} '
             f'Q{sx + 230} {par - 80} {sx + 340} {par + 8}')
    out.append(f'<path d="{butte} L{sx + 340} {par + 40} L{sx - 330} {par + 40} Z" fill="url(#terre)"/>')
    out.append(f'<path d="{butte}" {ST} stroke-width="4"/>')
    for dx, dy in ((-120, -96), (-60, -112), (10, -118), (70, -110), (124, -92)):
        out.append(f'<path d="M{sx + dx - 26} {sy + dy + 4} Q{sx + dx} {sy + dy - 16} {sx + dx + 26} {sy + dy + 6}" fill="url(#terre)" {ST} stroke-width="3"/>')
    for x0, x1 in ((-140, -300), (-80, -180), (60, 200), (130, 330), (0, 30)):
        out.append(f'<path d="M{sx + x0} {sy - 80} L{sx + (x0 + x1) // 2} {par + 40} L{sx + x1} {par + 120}" {ST} stroke-width="2"/>')
    out.append(f'<path d="M{CX0 - 40} {par + 60} L{CX1 + 40} {par + 40} L{CX1 + 40} {H} L{CX0 - 40} {H} Z" fill="url(#v2)"/>')
    out.append(f'<path d="M{CX0 - 40} {par + 260} L{CX1 + 40} {par + 230} L{CX1 + 40} {H} L{CX0 - 40} {H} Z" fill="url(#v1f)"/>')
    out.append(BRAS)
    # premier plan : le canon levé, fin et court, hors de net : contours doublés, sans aplat ;
    # il pointe vers la silhouette mais l'œil la trouve d'abord
    canon = "M300 1100 L860 560 L882 580 L338 1100 Z"
    for dx, dy, coul, ep in ((-10, 7, PAPIER, 3), (10, -7, PAPIER, 3), (0, 0, PAPIER, 1.6)):
        out.append(f'<path d="{canon}" fill="none" stroke="{coul}" stroke-width="{ep}" transform="translate({dx} {dy})"/>')
    out.append(f'<ellipse cx="871" cy="570" rx="9" ry="6" fill="none" stroke="{ENCRE}" stroke-width="2" transform="rotate(-44 871 570)"/>')
    out.append(f'<path d="M560 860 L580 878 M548 872 L568 890" stroke="{LAVIS}" stroke-width="3"/>')
    return planche("".join(out))


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    for lettre, fn in (("a", epilogue_a), ("b", epilogue_b), ("c", epilogue_c), ("d", epilogue_d), ("e", epilogue_e)):
        (DST / f"cin_epilogue-{lettre}.svg").write_text(fn(), encoding="utf-8")
    print("5 gravures dans art/src/cin/")


if __name__ == "__main__":
    main()
