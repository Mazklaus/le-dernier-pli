#!/usr/bin/env python3
"""Génère la cinématique e4_greffe : la greffe de l'œil de saint Ivo, en ombre chinoise seulement.
Elle ne joue que si Tobie accepte la greffe (e4_anselme).

Garde-fous du GD : aucune lame dans les silhouettes (une loupe, une pince à bouts ronds, un flacon),
coupe au noir AVANT tout contact avec le visage (le son prend le relais), le dernier plan est la
lampe qu'on baisse, jamais le résultat. On ne voit ni l'œil ni la plaie.

  Plan A  derrière un drap tendu, éclairé par la lampe d'Anselme : l'ombre de Tobie assis, la tête
          qui part en arrière ; l'ombre d'Anselme qui pose le flacon, lève la loupe puis la pince,
          et grandit à chaque image (il se penche vers la lampe).
          cin_greffe_01 fond 1920 x 1080 (image 0), cin_greffe_02 : 6 images de 1280 x 840 en
          (320, 120), grille 2 x 3.
  noir    coupe franche au noir après l'image 5 (la pince est encore loin du visage), 0,6 s.
  Plan B  gros plan sur la lampe : la main d'Anselme tourne la molette, la flamme baisse et
          s'éteint. cin_greffe_03 fond (image 0), cin_greffe_04 : 4 images de 800 x 800 en
          (560, 140), grille 2 x 2. Le dialogue reprend sur « la lampe a deux lumières ».

Usage : python3 tools/gen_cin_e4.py
"""
from __future__ import annotations

import math

from gen_cin_e1 import DST, H, W, bande, svg
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER

STP = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
ZONE_A = (320, 120, 1280, 840)
ZONE_B = (560, 140, 800, 800)
DRAP = (340, 140, 1580, 950)

# Tobie : inclinaison de la tête (degrés, en arrière) ; Anselme : échelle de son ombre, penché.
TETE = (0, -14, -26, -36, -42, -44)
ECHELLE = (1.0, 1.0, 1.1, 1.24, 1.38, 1.52)
FLOU = (0, 0, 0, 1.6, 3.2, 4.8)    # le bord de l'ombre se brouille quand il s'approche de la lampe
PENCHE = (0, 0, -4, -7, -10, -11)


# --- plan A : les ombres sur le drap -----------------------------------------------------------
def chambre_et_drap() -> str:
    x0, y0, x1, y1 = DRAP
    return (f'<rect width="{W}" height="{H}" fill="{ENCRE}"/>'
            f'<rect width="{W}" height="{H}" fill="url(#v2)" opacity=".5"/>'
            '<defs><radialGradient id="lueur" cx="50%" cy="42%" r="70%">'
            f'<stop offset="0" stop-color="{PAPIER}"/><stop offset=".62" stop-color="{PAPIER}"/>'
            f'<stop offset="1" stop-color="{MINE}"/></radialGradient>'
            f'<clipPath id="drap"><path d="M{x0} {y0} H{x1} V{y1} Q{(x0 + x1) / 2} {y1 + 14} {x0} {y1} Z"/></clipPath></defs>'
            # le cadre de bois du paravent, le drap tendu (un peu lâche en bas), éclairé par derrière
            f'<path d="M{x0 - 24} {H} V{y0 - 30} M{x1 + 24} {H} V{y0 - 30} M{x0 - 40} {y0 - 20} H{x1 + 40}" stroke="{LAVIS}" stroke-width="22"/>'
            f'<path d="M{x0} {y0} H{x1} V{y1} Q{(x0 + x1) / 2} {y1 + 14} {x0} {y1} Z" fill="url(#lueur)" {STP} stroke-width="3"/>'
            + "".join(f'<circle cx="{x}" cy="{y0 - 6}" r="7" fill="{LAVIS}" {STP} stroke-width="2"/>' for x in range(x0 + 40, x1, 150))
            + f'<path d="M{x0 + 200} {y0 + 4} Q{x0 + 210} {y0 + 300} {x0 + 196} {y1 - 6} M{x1 - 260} {y0 + 4} Q{x1 - 250} {y0 + 360} {x1 - 268} {y1 - 6}" fill="none" stroke="{MINE}" stroke-width="1.6" opacity=".6"/>')


def ombre_tobie(k: int) -> str:
    """Tobie assis de profil, tourné vers la droite : la chaise, les mains sur les genoux, la tête
    qui part en arrière à mesure que le breuvage agit."""
    a = TETE[k]
    return (f'<g fill="{ENCRE}">'
            f'<path d="M470 940 V700 M640 940 V712 M470 700 H660 V716 H470 Z M478 700 V500 H496 V700" stroke="{ENCRE}" stroke-width="14"/>'
            f'<path d="M520 706 Q506 600 548 520 Q584 486 624 500 Q648 560 640 706 Z"/>'
            f'<path d="M560 706 H760 L772 732 H560 Z M738 720 L760 920 H800 L806 940 H736 L720 728 Z"/>'
            + (f'<path d="M600 530 Q650 590 700 660 L716 690 L700 702 L676 676 Q620 620 584 560 Z"/>' if k < 3 else
               # la main crispée sur le bord du siège, les doigts repliés dessous : sa seule peur
               f'<path d="M600 530 Q636 610 650 690 L668 700 L654 716 L634 700 Q616 620 584 560 Z"/>'
               f'<path d="M648 712 Q{652 + k} {732 + k * 2} {666 + k} {724 + k}" fill="none" stroke="{ENCRE}" stroke-width="{8 + k}" stroke-linecap="round"/>')
            + 
            f'<g transform="rotate({a} 588 498)">'
            f'<path d="M574 500 L580 470 H604 L606 500 Z"/>'
            f'<path d="M560 420 Q556 372 600 364 Q644 366 652 408 L664 430 L652 436 Q650 462 624 472 Q590 478 570 458 Q558 444 560 420 Z"/>'
            f'<path d="M560 400 Q566 360 604 358 Q628 356 640 372 Q622 362 600 368 Q574 376 570 404 Z"/>'
            '</g></g>')


def _ombre_pt(x: float, y: float, k: int) -> tuple[float, float]:
    """Où tombe un point du corps d'Anselme une fois son ombre grandie et penchée (pivot : ses pieds)."""
    s, p = ECHELLE[k], math.radians(PENCHE[k])
    dx, dy = (x - 1260) * s, (y - 960) * s
    return 1260 + dx * math.cos(p) - dy * math.sin(p), 960 + dx * math.sin(p) + dy * math.cos(p)


def _bras(epaule: tuple[float, float], main: tuple[float, float], ep: float) -> str:
    """Un bras d'ombre, de l'épaule à la main, un peu fléchi vers le bas."""
    (x0, y0), (x1, y1) = epaule, main
    cx, cy = (x0 + x1) / 2, max(y0, y1) + 40
    return (f'<path d="M{x0:.0f} {y0:.0f} Q{cx:.0f} {cy:.0f} {x1:.0f} {y1:.0f}" fill="none" stroke="{ENCRE}" '
            f'stroke-width="{ep:.0f}" stroke-linecap="round"/>')


def ombre_anselme(k: int) -> str:
    """Anselme debout de profil, tourné vers la gauche : la robe, la tonsure ; le flacon, puis la
    loupe et la pince à bouts ronds. Son ombre grandit, penche et se brouille (il se rapproche de
    la lampe) jusqu'à mordre le haut du drap. Les outils restent loin du visage de Tobie."""
    s, p = ECHELLE[k], PENCHE[k]
    corps = [f'<path d="M1180 960 L1206 540 Q1250 488 1300 532 L1336 960 Z"/>',
             f'<path d="M1232 492 L1236 470 H1262 L1268 494 Z"/>',
             # la tête tonsurée : la couronne de cheveux fait deux bosses au-dessus des oreilles
             f'<path d="M1206 424 Q1204 380 1250 372 Q1294 378 1296 424 Q1294 462 1252 474 Q1220 470 1210 450 L1196 440 L1208 430 Z"/>',
             f'<path d="M1210 404 Q1216 388 1228 386 L1226 400 Z M1290 404 Q1284 388 1272 386 L1274 400 Z"/>']
    if k == 0:
        corps.append(f'<path d="M1222 548 Q1170 600 1166 626 L1190 636 Q1200 600 1250 566 Z"/>'
                     f'<path d="M1160 640 Q1154 612 1168 606 H1186 Q1196 616 1190 642 Z"/>'
                     f'<path d="M1164 606 V572 Q1164 560 1170 556 V536 H1182 V556 Q1188 560 1188 572 V606 Z"/>')
    elif k == 1:
        corps.append(f'<path d="M1222 548 Q1190 640 1180 740 L1204 746 Q1214 650 1250 566 Z"/>'
                     f'<path d="M1176 742 V790 Q1176 802 1184 806 V820 H1194 V806 Q1202 802 1202 790 V742 Z"/>')
    out = [f'<g transform="translate(1260 960) rotate({p}) scale({s}) translate(-1260 -960)">' + "".join(corps) + '</g>']
    ep = 22 * s
    if k >= 2:
        # la loupe, au bout du bras avant : l'anneau vide laisse voir le drap
        lx, ly = {2: (1010, 446), 3: (880, 420), 4: (790, 400), 5: (740, 388)}[k]
        out.append(_bras(_ombre_pt(1222, 556, k), (lx + 40, ly + 24), ep))
        out.append(f'<path d="M{lx + 40} {ly + 24} L{lx + 16} {ly + 10}" stroke="{ENCRE}" stroke-width="{9 * s:.0f}"/>'
                   f'<circle cx="{lx}" cy="{ly}" r="{28 * s:.0f}" fill="none" stroke="{ENCRE}" stroke-width="{10 * s:.0f}"/>')
    if k >= 3:
        # la pince : deux branches à bouts ronds ; à A5 elle est encore à une main du visage
        px, py = {3: (930, 500), 4: (830, 476), 5: (770, 460)}[k]
        out.append(_bras(_ombre_pt(1272, 560, k), (px + 40, py + 6), ep))
        out.append(f'<path d="M{px + 44} {py + 4} L{px - 28} {py - 8} M{px + 44} {py + 4} L{px - 28} {py + 12}" stroke="{ENCRE}" stroke-width="{6 * s:.0f}"/>'
                   f'<circle cx="{px - 30}" cy="{py - 8}" r="{5 * s:.0f}"/><circle cx="{px - 30}" cy="{py + 12}" r="{5 * s:.0f}"/>')
    flou = FLOU[k]
    filtre = (f'<defs><filter id="flou{k}" x="-20%" y="-20%" width="140%" height="140%">'
              f'<feGaussianBlur stdDeviation="{flou}"/></filter></defs>') if flou else ""
    return filtre + f'<g fill="{ENCRE}"' + (f' filter="url(#flou{k})"' if flou else "") + '>' + "".join(out) + '</g>'


def plan_a(k: int) -> str:
    return (chambre_et_drap() + '<g clip-path="url(#drap)" opacity=".94">'
            + ombre_tobie(k) + ombre_anselme(k) + '</g>')


# --- plan B : la lampe qu'on baisse -------------------------------------------------------------
FLAMME = (130, 92, 50, 0)
LUEUR = (360, 260, 150, 0)


def lampe(k: int) -> str:
    """La lampe à pétrole d'Anselme en gros plan : réservoir, molette, verre ; la main douce qui
    tourne la molette ; la flamme en papier nu baisse puis s'éteint."""
    f, r = FLAMME[k], LUEUR[k]
    out = [f'<rect width="{W}" height="{H}" fill="{ENCRE}"/>']
    if r:
        out.append('<defs><radialGradient id="halo">'
                   f'<stop offset="0" stop-color="{PAPIER}" stop-opacity=".95"/><stop offset=".5" stop-color="{MINE}" stop-opacity=".55"/>'
                   f'<stop offset="1" stop-color="{ENCRE}" stop-opacity="0"/></radialGradient></defs>'
                   f'<circle cx="960" cy="470" r="{r}" fill="url(#halo)"/>')
    trait = LAVIS if k == 3 else ENCRE
    clair = MINE if k == 3 else PAPIER
    # le verre de lampe (cheminée), la galerie, le réservoir sur son pied
    out.append(f'<path d="M920 300 Q910 380 900 420 Q880 470 900 560 H1020 Q1040 470 1020 420 Q1010 380 1000 300 Z" fill="none" stroke="{clair}" stroke-width="5"/>')
    out.append(f'<path d="M880 560 H1040 L1050 600 H870 Z" fill="{LAVIS}" stroke="{trait}" stroke-width="3"/>')
    out.append(f'<path d="M860 600 H1060 Q1110 680 1060 760 H860 Q810 680 860 600 Z" fill="url(#h2)" stroke="{trait}" stroke-width="4"/>')
    out.append(f'<path d="M900 760 L880 900 H1040 L1020 760 Z" fill="url(#h2)" stroke="{trait}" stroke-width="4"/>')
    if f:
        out.append(f'<path d="M960 560 Q{960 - f * .3:.0f} {560 - f * .45:.0f} 960 {560 - f} Q{960 + f * .3:.0f} {560 - f * .45:.0f} 960 560 Z" fill="{PAPIER}" stroke="{ENCRE}" stroke-width="2"/>')
        out.append(f'<path d="M952 560 H968 V548 H952 Z" fill="{ENCRE}"/>')
    else:
        # éteinte : un fil de fumée en mine, la mèche ne rougeoie pas (pas de rouge)
        out.append(f'<path d="M960 556 Q950 520 966 490 Q980 460 960 420" fill="none" stroke="{MINE}" stroke-width="2.4"/>')
    # la molette et la main qui la tourne (manche de bure, doigts posés, sans hâte)
    ang = (0, 30, 60, 90)[k]
    out.append(f'<g transform="rotate({ang} 1072 584)"><circle cx="1072" cy="584" r="16" fill="{LAVIS}" stroke="{trait}" stroke-width="3"/>'
               f'<path d="M1072 568 V600 M1056 584 H1088" stroke="{trait}" stroke-width="2"/></g>')
    # la manche sort du cadre à droite (au-delà de la zone animée, elle reste celle du fond)
    out.append(f'<path d="M1960 760 Q1500 720 1140 620 L1160 580 Q1520 640 1960 660 Z" fill="url(#h2)" stroke="{ENCRE}" stroke-width="3"/>')
    out.append(f'<path d="M1150 624 Q1100 610 1086 596 Q1084 580 1098 576 L1130 578 Q1150 560 1162 580 Z" fill="{clair}" stroke="{trait}" stroke-width="2.4"/>')
    out.append(f'<path d="M1100 578 Q1090 566 1080 568 M1110 600 Q1094 604 1086 598" fill="none" stroke="{trait}" stroke-width="2"/>')
    return "".join(out)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    (DST / "cin_greffe_01.svg").write_text(svg(plan_a(0)), encoding="utf-8")
    (DST / "cin_greffe_02.svg").write_text(bande([plan_a(k) for k in range(6)], ZONE_A, 2), encoding="utf-8")
    (DST / "cin_greffe_03.svg").write_text(svg(lampe(0)), encoding="utf-8")
    (DST / "cin_greffe_04.svg").write_text(bande([lampe(k) for k in range(4)], ZONE_B, 2), encoding="utf-8")
    print("cin_greffe : 2 fonds et 2 bandes dans art/src/cin/")


if __name__ == "__main__":
    main()
