#!/usr/bin/env python3
"""Génère les plans de la cinématique e1_remise_pli : la main de Lamarre tend le pli, Tobie le prend
et le glisse contre sa poitrine (directive animation du Game Director, étape 1).

Deux plans plein écran (1920 x 1080), chacun en deux fichiers : un fond fixe et une planche d'images
de la seule zone qui bouge, à poser par-dessus le fond à la position indiquée. Les images de la
bande sont opaques : elles recouvrent exactement leur zone du fond. 10 i/s, jouées une fois ; la
caméra peut glisser lentement sur le plan (le fond déborde de rien : cadrer à 1920 x 1080).

  cin_remise-pli_01   plan A, fond : l'abri du sergent à la bougie, la manche de Lamarre
  cin_remise-pli_02   plan A, 6 images de 1440 x 840 en grille de 2 x 3 (hframes 2, vframes 3),
                      posées en (0, 240) :
                      la main tend le pli ; la main de Tobie entre, le saisit ; Lamarre lâche
  cin_remise-pli_03   plan B, fond : la poitrine de Tobie, la bandoulière, la cloche au col
  cin_remise-pli_04   plan B, 4 images de 1200 x 780 en grille de 2 x 2 (hframes 2, vframes 2),
                      posées en (300, 300) :
                      le pli monte, se glisse sous la bandoulière, la main se pose dessus

La lumière est celle de la bougie de Lamarre (en haut à droite du plan A) : anneaux de hachure
nets, aucun dégradé. Le rouge n'est que le ruban ; le cachet est de cire noire.

Usage : python3 tools/gen_cin_e1.py
"""
from __future__ import annotations

import math
from pathlib import Path

from gen_cin_epilogues import DEFS_CIN, cire, ruban
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER

ROOT = Path(__file__).resolve().parent.parent
DST = ROOT / "art" / "src" / "cin"
W, H = 1920, 1080
ST = f'stroke="{ENCRE}" fill="none" stroke-linejoin="round" stroke-linecap="round"'
STP = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'

ZONE_A = (0, 240, 1440, 840)
ZONE_B = (300, 300, 1200, 780)
BOUGIE = (1640, 190)


def svg(contenu: str, vb: tuple[int, int, int, int] = (0, 0, W, H)) -> str:
    x, y, w, h = vb
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}">'
            f'{DEFS_CIN}{contenu}</svg>\n')


def bande(images: list[str], zone: tuple[int, int, int, int], colonnes: int) -> str:
    """Les images en grille (de gauche à droite puis de haut en bas : hframes = colonnes),
    chacune découpée à la zone ; aucune texture ne dépasse 4096 px de côté."""
    x, y, w, h = zone
    lignes = math.ceil(len(images) / colonnes)
    corps = "".join(f'<svg x="{(i % colonnes) * w}" y="{(i // colonnes) * h}" width="{w}" height="{h}" '
                    f'viewBox="{x} {y} {w} {h}">{c}</svg>' for i, c in enumerate(images))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w * colonnes}" height="{h * lignes}" '
            f'viewBox="0 0 {w * colonnes} {h * lignes}">{DEFS_CIN}{corps}</svg>\n')


def anneaux(cx: float, cy: float, r0: float) -> str:
    """Lumière de bougie : cœur au papier, un anneau de hachure simple, le reste en contre-hachure."""
    r1 = r0 * 1.8
    return (f'<mask id="m-coeur" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
            f'<rect width="{W}" height="{H}" fill="#fff"/><circle cx="{cx}" cy="{cy}" r="{r0}" fill="#000"/></mask>'
            f'<mask id="m-anneau" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
            f'<rect width="{W}" height="{H}" fill="#fff"/><circle cx="{cx}" cy="{cy}" r="{r1}" fill="#000"/></mask>'
            f'<rect width="{W}" height="{H}" fill="url(#v1)" mask="url(#m-coeur)"/>'
            f'<rect width="{W}" height="{H}" fill="url(#v2)" mask="url(#m-anneau)"/>')


# --- plan A : la remise ---------------------------------------------------------------------
def mur_abri() -> str:
    """Le coffrage de l'abri, flou de premier plan dit par un contour doublé (planches au loin)."""
    out = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>']
    for y in range(40, H, 150):
        out.append(f'<path d="M0 {y} H{W}" {ST} stroke-width="3"/><path d="M0 {y + 7} H{W}" {ST} stroke-width="1.2"/>')
    for k, x in enumerate(range(170, W, 420)):
        out.append(f'<path d="M{x + (k % 2) * 60} 0 V{H}" {ST} stroke-width="2"/>')
    out.append(anneaux(*BOUGIE, 420))
    return "".join(out)


def bougie() -> str:
    """La main droite de Lamarre, en haut à droite, qui tient le bout de bougie ; flamme cernée, nette."""
    x, y = BOUGIE
    return (f'<path d="M{x + 120} {H * 0 + 0} L{x + 280} 0 L{x + 260} 300 L{x + 90} 330 Z" fill="url(#h2)" {STP} stroke-width="5"/>'
            f'<path d="M{x - 26} {y + 40} L{x + 26} {y + 40} L{x + 26} {y + 150} L{x - 26} {y + 150} Z" fill="{PAPIER}" {STP} stroke-width="4"/>'
            f'<path d="M{x - 26} {y + 60} q-10 26 -4 50 M{x + 26} {y + 52} q12 30 4 70" {ST} stroke-width="3"/>'
            f'<path d="M{x} {y + 40} V{y + 22}" {ST} stroke-width="4"/>'
            f'<path d="M{x} {y + 24} Q{x - 22} {y - 10} {x} {y - 70} Q{x + 22} {y - 10} {x} {y + 24} Z" fill="{PAPIER}" {STP} stroke-width="3.4"/>'
            f'<path d="M{x} {y + 10} Q{x - 8} {y - 10} {x} {y - 34}" {ST} stroke-width="1.6"/>'
            # le poing autour de la bougie
            f'<path d="M{x - 60} {y + 120} Q{x - 64} {y + 90} {x - 30} {y + 86} L{x + 70} {y + 82} Q{x + 104} {y + 90} {x + 100} {y + 130} '
            f'L{x + 96} {y + 220} Q{x + 40} {y + 250} {x - 30} {y + 230} Q{x - 64} {y + 200} {x - 60} {y + 120} Z" fill="{PAPIER}" {STP} stroke-width="4.4"/>'
            f'<path d="M{x - 52} {y + 128} Q{x} {y + 116} {x + 60} {y + 124} M{x - 50} {y + 168} Q{x} {y + 156} {x + 66} {y + 164} '
            f'M{x - 44} {y + 206} Q{x} {y + 196} {x + 64} {y + 202}" {ST} stroke-width="2.2"/>')


def manche_lamarre() -> str:
    """La manche de capote qui entre par la droite, galons de sergent, parement retourné."""
    return (f'<path d="M{W + 10} 470 L1430 540 Q1410 640 1430 760 L{W + 10} 840 Z" fill="url(#h2)" {STP} stroke-width="5"/>'
            f'<path d="M1430 540 L1340 552 Q1320 650 1342 750 L1430 760 Q1410 640 1430 540 Z" fill="url(#h1)" {STP} stroke-width="4.4"/>'
            f'<path d="M1700 520 L1640 600 L1700 680 M1760 516 L1700 596 L1760 676" stroke="{PAPIER}" stroke-width="16" fill="none"/>'
            f'<path d="M1700 520 L1640 600 L1700 680 M1760 516 L1700 596 L1760 676" {ST} stroke-width="3"/>'
            f'<path d="M1500 560 Q1600 600 1800 560 M1520 740 Q1640 720 1820 780" {ST} stroke-width="1.8"/>')


def main_lamarre(ouverte: bool) -> str:
    """La main carrée de Lamarre, dos vers nous, qui pince le bord droit du pli entre pouce et index.
    Ouverte : les doigts se sont écartés, le pli n'est plus là."""
    if ouverte:
        doigts = (f'<path d="M1210 572 L1110 520 Q1092 512 1086 530 Q1084 546 1100 554 L1196 606" fill="{PAPIER}" {STP} stroke-width="4"/>'
                  f'<path d="M1200 612 L1094 590 Q1076 588 1074 606 Q1076 622 1094 624 L1196 650" fill="{PAPIER}" {STP} stroke-width="4"/>'
                  f'<path d="M1200 656 L1104 660 Q1086 662 1088 680 Q1092 696 1110 694 L1206 694" fill="{PAPIER}" {STP} stroke-width="4"/>'
                  f'<path d="M1240 720 Q1180 760 1126 760 Q1108 758 1110 742 Q1116 728 1132 726 Q1180 720 1214 698" fill="{PAPIER}" {STP} stroke-width="4"/>')
    else:
        doigts = (f'<path d="M1210 568 L1150 556 Q1128 556 1126 576 L1130 610 L1196 618" fill="{PAPIER}" {STP} stroke-width="4"/>'
                  f'<path d="M1200 618 L1140 614 Q1120 616 1120 636 Q1122 654 1142 656 L1198 660" fill="{PAPIER}" {STP} stroke-width="4"/>'
                  f'<path d="M1200 660 L1148 664 Q1130 668 1132 686 Q1136 702 1154 700 L1208 698" fill="{PAPIER}" {STP} stroke-width="4"/>'
                  # le pouce, dessous, qui serre le papier
                  f'<path d="M1250 716 Q1200 744 1150 734 Q1132 728 1138 712 Q1146 700 1166 704 Q1196 708 1220 694" fill="{PAPIER}" {STP} stroke-width="4"/>')
    return (f'<path d="M1342 556 Q1280 540 1226 556 Q1196 600 1200 650 Q1204 700 1240 724 Q1300 744 1344 748 Q1326 650 1342 556 Z" fill="{PAPIER}" {STP} stroke-width="4.6"/>'
            f'<path d="M1300 580 Q1270 620 1290 690 M1262 600 L1240 610" {ST} stroke-width="1.8"/>'
            + doigts)


def pli_grand(cx: float, cy: float, ang: float) -> str:
    """Le pli, gros plan : papier plié en enveloppe, ruban rouge, cachet de cire noire."""
    w, h = 420, 290
    x0, y0 = cx - w / 2, cy - h / 2
    return (f'<g transform="rotate({ang:.1f} {cx:.0f} {cy:.0f})">'
            f'<path d="M{x0 + 10} {y0 + h + 12} L{x0 + w + 10} {y0 + h + 12} L{x0 + w + 10} {y0 + 12}" stroke="{ENCRE}" stroke-width="8" fill="none"/>'
            f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{PAPIER}" {STP} stroke-width="5"/>'
            f'<path d="M{x0} {y0} L{cx} {cy - 10} L{x0 + w} {y0}" {ST} stroke-width="3"/>'
            f'<path d="M{x0} {y0 + h} L{cx - 60} {cy + 30} M{x0 + w} {y0 + h} L{cx + 60} {cy + 30}" {ST} stroke-width="1.8"/>'
            f'<path d="M{x0 + 30} {y0 + 40} H{x0 + 120} M{x0 + w - 130} {y0 + h - 30} H{x0 + w - 40}" stroke="{MINE}" stroke-width="2"/>'
            + ruban(f"M{cx} {y0 - 4} V{y0 + h + 4}", 16)
            + ruban(f"M{cx} {y0 + h} Q{cx - 20} {y0 + h + 60} {cx - 44} {y0 + h + 110}", 14)
            + ruban(f"M{cx} {y0 + h} Q{cx + 16} {y0 + h + 50} {cx + 30} {y0 + h + 120}", 14)
            + cire(cx, cy, 70) +
            '</g>')


def main_tobie(bout_x: float, cy: float, prise: bool) -> str:
    """La main de Tobie, plus fine, qui entre par la gauche dans la manche de toile de sa vareuse.
    bout_x : bout des doigts ; prise : les doigts se referment sur le bord du pli (pouce dessus)."""
    poignet = bout_x - 170
    manche = (f'<path d="M-20 {cy - 120} L{poignet - 30} {cy - 78} Q{poignet - 6} {cy + 6} {poignet - 26} {cy + 92} L-20 {cy + 150} Z" '
              f'fill="{PAPIER}" {STP} stroke-width="5"/>'
              f'<path d="M-20 {cy - 120} L{poignet - 30} {cy - 78} L{poignet - 60} {cy - 40} L-20 {cy - 70} Z" fill="url(#h2)" stroke="none"/>'
              f'<path d="M{poignet - 70} {cy - 74} Q{poignet - 46} {cy + 6} {poignet - 66} {cy + 86}" {ST} stroke-width="3"/>'
              f'<path d="M{poignet - 300} {cy - 60} Q{poignet - 200} {cy - 20} {poignet - 140} {cy - 60} M{poignet - 320} {cy + 90} Q{poignet - 220} {cy + 60} {poignet - 150} {cy + 80}" {ST} stroke-width="1.8"/>')
    paume = (f'<path d="M{poignet - 30} {cy - 60} Q{poignet + 40} {cy - 72} {poignet + 100} {cy - 56} L{poignet + 110} {cy + 50} '
             f'Q{poignet + 40} {cy + 70} {poignet - 30} {cy + 60} Q{poignet - 46} {cy} {poignet - 30} {cy - 60} Z" fill="{PAPIER}" {STP} stroke-width="4"/>')
    doigts = []
    for k, dy in enumerate((-44, -14, 16, 44)):
        lg = (70, 76, 72, 58)[k] if not prise else (40, 44, 42, 34)[k]
        x1 = poignet + 100 + lg
        doigts.append(f'<path d="M{poignet + 96} {cy + dy - 12} L{x1} {cy + dy - 10} Q{x1 + 14} {cy + dy} {x1} {cy + dy + 10} '
                      f'L{poignet + 98} {cy + dy + 12}" fill="{PAPIER}" {STP} stroke-width="3.4"/>')
    if prise:
        # le pouce par-dessus le papier, les doigts dessous (on n'en voit que les bouts repliés)
        doigts.append(f'<path d="M{poignet + 40} {cy - 58} Q{poignet + 110} {cy - 104} {poignet + 190} {cy - 86} Q{poignet + 206} {cy - 72} '
                      f'{poignet + 190} {cy - 60} Q{poignet + 120} {cy - 58} {poignet + 80} {cy - 30}" fill="{PAPIER}" {STP} stroke-width="3.6"/>')
    else:
        doigts.append(f'<path d="M{poignet + 30} {cy - 60} Q{poignet + 70} {cy - 104} {poignet + 120} {cy - 110} Q{poignet + 138} {cy - 104} '
                      f'{poignet + 130} {cy - 88} Q{poignet + 100} {cy - 76} {poignet + 80} {cy - 52}" fill="{PAPIER}" {STP} stroke-width="3.6"/>')
    return manche + paume + "".join(doigts)


def plan_a(k: int) -> str:
    """k de 0 à 5 ; le fond est l'image 0."""
    pli_x, pli_y, ang = 970, 620, -4
    if k == 5:
        pli_x, pli_y, ang = 780, 650, -9
    elif k == 4:
        pli_x, pli_y, ang = 900, 630, -6
    out = [mur_abri(), bougie(), manche_lamarre()]
    lamarre_tient = k <= 3
    if lamarre_tient:
        out.append(pli_grand(pli_x, pli_y, ang))
        out.append(main_lamarre(False))
    else:
        out.append(pli_grand(pli_x, pli_y, ang))
        out.append(main_lamarre(True))
    bouts = {1: 470, 2: 680, 3: 860, 4: 790, 5: 600}
    if k in bouts:
        out.append(main_tobie(bouts[k], pli_y + 10, prise=k >= 3))
    return "".join(out)


# --- plan B : contre la poitrine --------------------------------------------------------------
def poitrine() -> str:
    """La vareuse de Tobie en gros plan : boutons, bandoulière, la petite cloche sans battant au col."""
    out = [f'<rect width="{W}" height="{H}" fill="{PAPIER}"/>',
           # col et cou, en haut
           f'<path d="M720 -10 Q960 140 1200 -10 Z" fill="url(#h2)" {STP} stroke-width="5"/>',
           f'<path d="M660 -10 L720 -10 Q960 140 1200 -10 L1260 -10 Q1240 60 1180 90 Q960 200 740 90 Q680 60 660 -10 Z" fill="{PAPIER}" {STP} stroke-width="5"/>',
           # parement, boutons
           f'<path d="M1020 170 Q1010 600 1040 {H + 10}" {ST} stroke-width="4"/>',
           f'<path d="M1046 180 Q1036 600 1066 {H + 10}" {ST} stroke-width="1.6"/>']
    for y in (300, 560, 820):
        out.append(f'<circle cx="{1048 + (y - 300) * .03:.0f}" cy="{y}" r="16" fill="{PAPIER}" {STP} stroke-width="3.4"/>'
                   f'<path d="M{1040 + (y - 300) * .03:.0f} {y - 4} h16 M{1040 + (y - 300) * .03:.0f} {y + 4} h16" {ST} stroke-width="1.4"/>')
    # plis de la toile
    out.append(f'<path d="M300 300 Q420 420 380 640 M520 180 Q600 400 560 760 M1400 260 Q1340 520 1420 800 M1620 340 Q1560 600 1640 980" {ST} stroke-width="2"/>')
    # la cloche sans battant au col
    out.append(f'<path d="M960 120 V160" {ST} stroke-width="5"/>'
               f'<path d="M906 270 Q912 160 960 160 Q1008 160 1014 270 Z" fill="{ENCRE}" {STP} stroke-width="4"/>'
               f'<ellipse cx="960" cy="270" rx="56" ry="14" fill="{PAPIER}" {STP} stroke-width="3.4"/>')
    # la lumière vient de la bougie, en haut à droite hors champ : voile sur la gauche
    out.append(f'<path d="M0 0 L520 0 Q380 500 600 {H} L0 {H} Z" fill="url(#v1)"/>')
    return "".join(out)


def bandouliere() -> str:
    """La bandoulière qui barre la poitrine, de l'épaule droite (à gauche de l'image) à la hanche."""
    d = f"M300 -20 L1720 {H + 20}"
    return (f'<path d="{d}" stroke="{ENCRE}" stroke-width="130"/>'
            f'<path d="{d}" stroke="{PAPIER}" stroke-width="110"/>'
            f'<path d="{d}" stroke="url(#h1)" stroke-width="110"/>'
            f'<path d="M300 -20 L1720 {H + 20}" stroke="{ENCRE}" stroke-width="2" stroke-dasharray="18 14" transform="translate(0 -40)"/>'
            f'<path d="M300 -20 L1720 {H + 20}" stroke="{ENCRE}" stroke-width="2" stroke-dasharray="18 14" transform="translate(0 40)"/>')


def main_plate(cx: float, cy: float, ang: float) -> str:
    """La main de Tobie à plat, doigts vers le haut-droite, qui tient ou appuie."""
    return (f'<g transform="rotate({ang:.0f} {cx:.0f} {cy:.0f})">'
            f'<path d="M{cx - 360} {cy + 260} L{cx - 120} {cy + 120} Q{cx - 80} {cy + 200} {cx - 60} {cy + 260} L{cx - 280} {cy + 420} Z" fill="{PAPIER}" {STP} stroke-width="5"/>'
            f'<path d="M{cx - 360} {cy + 260} L{cx - 120} {cy + 120} L{cx - 110} {cy + 160} L{cx - 330} {cy + 300} Z" fill="url(#h2)" stroke="none"/>'
            f'<path d="M{cx - 130} {cy + 110} Q{cx - 40} {cy + 40} {cx + 40} {cy + 60} L{cx + 70} {cy + 160} Q{cx} {cy + 240} {cx - 70} {cy + 250} Q{cx - 120} {cy + 190} {cx - 130} {cy + 110} Z" fill="{PAPIER}" {STP} stroke-width="4"/>'
            + "".join(f'<path d="M{cx + 30 - k * 26} {cy + 70 - k * 8} L{cx + 110 - k * 30} {cy - 40 - k * 4} Q{cx + 126 - k * 30} {cy - 40 - k * 4} {cx + 124 - k * 30} {cy - 24 - k * 4} '
                      f'L{cx + 52 - k * 26} {cy + 86 - k * 8}" fill="{PAPIER}" {STP} stroke-width="3.4"/>' for k in range(4))
            + f'<path d="M{cx - 120} {cy + 130} Q{cx - 150} {cy + 60} {cx - 110} {cy + 20} Q{cx - 92} {cy + 14} {cx - 90} {cy + 34} Q{cx - 100} {cy + 80} {cx - 80} {cy + 120}" fill="{PAPIER}" {STP} stroke-width="3.6"/>'
            '</g>')


def plan_b(k: int) -> str:
    out = [poitrine()]
    # le pli monte (0), arrive à hauteur du cœur (1), se glisse sous la bandoulière (2, 3)
    poses = [(1100, 1000, -18), (1060, 690, -10), (930, 610, 34), (900, 650, 30)]
    cx, cy, ang = poses[k]
    sous = k >= 2
    if sous:
        out.append(pli_grand(cx, cy, ang))
        out.append(bandouliere())
    else:
        out.append(bandouliere())
        out.append(pli_grand(cx, cy, ang))
    mains = [(cx - 40, cy + 120, -10), (cx - 60, cy + 100, -14), (cx - 120, cy + 120, 0), (cx - 60, cy + 150, 10)]
    out.append(main_plate(*mains[k]))
    return "".join(out)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    (DST / "cin_remise-pli_01.svg").write_text(svg(plan_a(0)), encoding="utf-8")
    (DST / "cin_remise-pli_02.svg").write_text(bande([plan_a(k) for k in range(6)], ZONE_A, 2), encoding="utf-8")
    (DST / "cin_remise-pli_03.svg").write_text(svg(plan_b(0)), encoding="utf-8")
    (DST / "cin_remise-pli_04.svg").write_text(bande([plan_b(k) for k in range(4)], ZONE_B, 2), encoding="utf-8")
    print("cin_remise-pli : 2 fonds et 2 bandes dans art/src/cin/")


if __name__ == "__main__":
    main()
