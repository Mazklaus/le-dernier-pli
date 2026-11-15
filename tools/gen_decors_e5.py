#!/usr/bin/env python3
"""Génère les fonds de l'étape 5, la Forêt de Croix (maquette du Level Designer).

Les cinq sections de surface sont des tronçons fermés, sans parallaxe : un fond fixe par section,
env_e5_plan3_<section>_NN (tuiles de 2048 px au plus), posé en (0, 0) dans la section par
scenes/decors/decor_e5.gd. Sol à y 900, ciel de brouillard.

  oree       1920  la lisière : un champ nu, les premières croix ; la croix-borne (x 1000)
  boucle     3840  le sentier qui boucle entre les croix, toutes pareilles ; la croix-repère au
                   poteau centré sur le déclencheur (x 600) ; la trouée de « Quitter le sentier »
                   (x 1020 à 1180) ; les traces (x 1700) ; la branche cassée (x 2500) ; le fourré
                   (x 3410) ; le sentier qui repart dans la brume (x 3640)
  campement  1920  un abri de capote tendu entre deux croix, la gamelle (x 700), le feu tiède
                   qui fume encore (x 1250)
  cimetiere  2880  les petites croix rangées, chacune sa cloche sans battant clouée ; les objets
                   laissés (x 900) ; la croix d'Aubin (x 1750 : le clou vide et la trace claire) ;
                   la croix sans nom au bout du rang (x 1890), la terre fraîche à son pied
  clairiere  1920  les croix s'espacent, le ciel s'ouvre (fin d'étape)

Calques posés par le code (fx, fond transparent, à l'échelle du monde) :
  fx_entaille-croix l'encoche de Tobie sur la croix-repère, et l'ancienne, noircie, dessous
  fx_cloche-aubin   la cloche de la crypte pendue au clou de la croix d'Aubin
  fx_nom-grave      TOBIE gravé au couteau sur la croix sans nom
Chacun est dessiné dans un carré de 64 x 96 ; DecorE5 le pose avec son coin haut-gauche
en ANCRES, dans le repère du déclencheur (son pied).

Garde-fous : aucun nombre (ni total, ni date, ni ordre), aucun rouge, les cloches n'ont pas de
battant. Les noms des croix sont des rayures, sauf celui que Tobie grave.

Usage : python3 tools/gen_decors_e5.py
"""
from __future__ import annotations

import math

from gen_decors_e1_surface import rnd
from gen_decors_e3_surface import DEFS, ENCRE, H, LAVIS, MINE, PAPIER, ROOT, SOL, ST, TUILE

DST = ROOT / "art" / "src" / "env" / "e5"
FX = ROOT / "art" / "src" / "fx"
HORIZON = 600

# x des déclencheurs dans leur section (maquette du LD) ; la croix est centrée dessus
REPERE_X = 600
AUBIN_X = 1750
SANS_NOM_X = 1890
# le clou : là où la main de Tobie lâche la cloche quand il est à 60 px de la croix
CLOU = (AUBIN_X - 6, 632)
ENTAILLE_Y = 640
NOM_Y = 693


# --------------------------------------------------------------------------- briques
def ciel(w: int) -> str:
    return (f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>'
            '<defs><linearGradient id="brume5" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{PAPIER}"/><stop offset=".5" stop-color="{PAPIER}"/>'
            f'<stop offset=".83" stop-color="{MINE}" stop-opacity=".35"/><stop offset="1" stop-color="{MINE}" stop-opacity=".5"/>'
            '</linearGradient></defs>'
            f'<rect width="{w}" height="{H}" fill="url(#brume5)"/>')


def croix(x: float, pied: float, h: float, couleur: str, ep: float, penche: float = 0.0, op: float = 1.0) -> str:
    b = h * .24
    return (f'<g transform="rotate({penche:.1f} {x:.0f} {pied:.0f})" opacity="{op:.2f}"><path d="M{x:.0f} {pied:.0f} V{pied - h:.0f} '
            f'M{x - b:.0f} {pied - h * .74:.0f} H{x + b:.0f}" stroke="{couleur}" stroke-width="{ep:.1f}" stroke-linecap="square"/></g>')


def croix_bois(x: float, pied: float = SOL, h: float = 300, larg: float = 16, seed: int = 0, bras: float = .3) -> str:
    """Une croix de premier rang, en bois : poteau et traverse hachurés, veines, un peu penchée."""
    r = rnd(seed or int(x))
    b = h * bras
    ty = pied - h * .74
    a = r.uniform(-2.5, 2.5)
    return (f'<g transform="rotate({a:.1f} {x:.0f} {pied:.0f})">'
            f'<rect x="{x - larg / 2:.0f}" y="{pied - h:.0f}" width="{larg:.0f}" height="{h:.0f}" fill="url(#h1)" {ST} stroke-width="2.4"/>'
            f'<rect x="{x - b:.0f}" y="{ty - larg / 2:.0f}" width="{2 * b:.0f}" height="{larg:.0f}" fill="url(#h1)" {ST} stroke-width="2.4"/>'
            f'<path d="M{x - 2:.0f} {pied - h + 20:.0f} V{pied - 30:.0f}" stroke="{MINE}" stroke-width="1.2"/></g>')


def rangs(w: int, seed: int, trous: tuple[tuple[int, int], ...] = (), densite: float = 1.0, clair: float = 0.0) -> str:
    """Les rangs de croix derrière le sentier, du plus lointain (pâle, au ras de l'horizon) au plus
    proche (encre). Les trous laissent passer un chemin ; clair (0 à 1) éclaircit la forêt."""
    r = rnd(seed)
    out = []
    for rang in range(7):
        t = rang / 6
        pied = HORIZON + 14 + t * 250
        h = 40 + t * 200
        couleur = MINE if t < .5 else LAVIS
        ep = 1.4 + t * 3.2
        op = .55 + t * .35
        pas = (60 + t * 150) / densite * (1 + clair * 2)
        x = r.uniform(-pas, 0)
        while x < w + pas:
            libre = all(not (a - h * .4 < x < b + h * .4) for a, b in trous) or t < .3
            libre = libre and h * .3 < x < w - h * .3   # rien de coupé au raccord des sections
            if libre:
                out.append(croix(x, pied + r.uniform(-4, 4), h * r.uniform(.9, 1.1), couleur, ep, r.uniform(-3, 3), op))
            x += pas * r.uniform(.8, 1.2)
    return "".join(out)


def sol(w: int, seed: int) -> str:
    """La terre du sentier : boue piétinée, touffes d'herbe rase, ornières."""
    r = rnd(seed)
    out = [f'<rect y="{SOL}" width="{w}" height="{H - SOL}" fill="{PAPIER}"/>',
           f'<rect y="{SOL}" width="{w}" height="{H - SOL}" fill="url(#h1)" opacity=".35"/>',
           f'<path d="M0 {SOL} H{w}" {ST} stroke-width="3"/>']
    for _ in range(w // 60):
        x, y = r.uniform(0, w), r.uniform(SOL + 20, H - 10)
        out.append(f'<path d="M{x:.0f} {y:.0f} q18 -5 36 0" fill="none" stroke="{MINE}" stroke-width="1.4"/>')
    for _ in range(w // 90):
        x = r.uniform(0, w)
        out.append(f'<path d="M{x:.0f} {SOL} l-4 -12 M{x + 5:.0f} {SOL} l1 -15 M{x + 10:.0f} {SOL} l5 -10" stroke="{ENCRE}" stroke-width="1.4"/>')
    return "".join(out)


def cloche(x: float, y: float, s: float = 1.0) -> str:
    """La petite cloche des coureurs, sans battant, pendue par son anneau en (x, y)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s})">'
            f'<circle cx="0" cy="2" r="2.4" fill="none" {ST} stroke-width="1.4"/>'
            f'<path d="M-6 15 Q-6 4 0 4 Q6 4 6 15 L8 17 H-8 Z" fill="url(#h2)" {ST} stroke-width="1.5"/>'
            f'<path d="M-5 15 H5" stroke="{PAPIER}" stroke-width="1"/></g>')


def rayures(x: float, y: float, n: int, seed: int) -> str:
    """Un nom gravé, vu d'ici : des rayures de couteau, illisibles."""
    r = rnd(seed)
    return "".join(f'<path d="M{x + i * 5:.0f} {y + r.uniform(-1, 1):.0f} l{r.uniform(-1, 2):.0f} 8" stroke="{ENCRE}" stroke-width="1.2"/>'
                   for i in range(n))


# --------------------------------------------------------------------------- sections
def oree() -> str:
    w = 1920
    out = [ciel(w)]
    # le champ nu à gauche, les croix qui commencent après x 700
    out.append(rangs(w, 5001, trous=((-200, 700),)))
    out.append(f'<path d="M0 {HORIZON + 30} Q400 {HORIZON + 10} 700 {HORIZON + 40}" fill="none" stroke="{MINE}" stroke-width="2"/>')
    # la croix-borne (sentier_bornes, x 1000) : plus haute, une pierre à son pied, une entaille de
    # passage (une seule, sans chiffre)
    out.append(croix_bois(1000, SOL, 340, 20, 5002))
    out.append(f'<path d="M972 {SOL} Q976 {SOL - 30} 1000 {SOL - 32} Q1026 {SOL - 30} 1030 {SOL} Z" fill="url(#moellons)" {ST} stroke-width="2"/>')
    for x in (1280, 1560, 1800):
        out.append(croix_bois(x, SOL, 250, 14))
    out.append(sol(w, 5003))
    return "".join(out)


def boucle() -> str:
    w = 3840
    out = [ciel(w)]
    out.append(rangs(w, 5101, trous=((1020, 1180), (3560, 3840))))
    # premier rang : des croix toutes pareilles, régulières, tous les 300 px (la boucle)
    for x in range(140, w, 300):
        if abs(x - REPERE_X) < 120 or 980 < x < 1220 or 2400 < x < 2640 or x > 3500:
            continue
        out.append(croix_bois(x, SOL, 260, 14, 7))     # même graine : toutes pareilles
    # la croix-repère (e5_sentier, x 600), poteau centré sur le déclencheur
    out.append(croix_bois(REPERE_X, SOL, 300, 18, 5103))
    # la trouée de « Quitter le sentier » (x 1020 à 1180) : une sente, des ronces de part et d'autre
    out.append(f'<path d="M1040 {SOL} Q1080 760 1100 {HORIZON + 30} M1160 {SOL} Q1120 760 1104 {HORIZON + 30}" fill="none" stroke="{MINE}" stroke-width="2"/>')
    r = rnd(5104)
    for cx in (1000, 1210):
        for _ in range(9):
            a = r.uniform(0, math.pi)
            out.append(f'<path d="M{cx:.0f} {SOL} q{40 * math.cos(a):.0f} {-60 * math.sin(a) - 20:.0f} {80 * math.cos(a):.0f} {-40 * math.sin(a):.0f}" '
                       f'fill="none" {ST} stroke-width="2" stroke-dasharray="6 3"/>')
    # les traces (x 1700) : des empreintes qui coupent entre les croix
    for k in range(7):
        x = 1600 + k * 34
        out.append(f'<ellipse cx="{x}" cy="{SOL + 18 + (k % 2) * 12}" rx="9" ry="4" fill="{LAVIS}"/>')
    # la branche cassée (x 2500) : un arbre mort entre les croix, une branche pendante à hauteur
    # d'épaule
    out.append(f'<path d="M2540 {SOL} L2530 520 L2500 430 M2530 600 L2600 520 M2532 690 L2470 704 L2452 760" fill="none" {ST} stroke-width="12"/>')
    out.append(f'<path d="M2470 704 l-6 -8 l10 2 l-2 -10" fill="none" {ST} stroke-width="2"/>')
    # le fourré (x 3410) et le sentier qui repart dans la brume (x 3640)
    for k in range(14):
        x = 3330 + k * 12
        out.append(f'<path d="M{x} {SOL} q{(k % 3) * 8 - 8} -80 {(k % 2) * 30 - 15} -150" fill="none" {ST} stroke-width="3"/>')
    out.append(f'<path d="M3560 {SOL} Q3680 760 3800 {HORIZON + 30}" fill="none" stroke="{MINE}" stroke-width="2"/>')
    out.append(sol(w, 5105))
    return "".join(out)


def campement() -> str:
    w = 1920
    out = [ciel(w), rangs(w, 5201)]
    # l'abri : une capote tendue entre deux croix, des piquets
    out.append(croix_bois(860, SOL, 260, 14))
    out.append(croix_bois(1100, SOL, 260, 14))
    out.append(f'<path d="M860 700 L1100 700 L1160 {SOL - 10} L800 {SOL - 10} Z" fill="url(#h2)" {ST} stroke-width="2.6"/>')
    out.append(f'<path d="M940 700 L920 {SOL - 10} M1020 700 L1030 {SOL - 10}" stroke="{MINE}" stroke-width="1.6"/>')
    out.append(f'<path d="M870 {SOL - 60} Q980 {SOL - 40} 1090 {SOL - 60}" fill="none" stroke="{PAPIER}" stroke-width="2"/>')
    # la gamelle encore grasse (x 700)
    out.append(f'<path d="M680 {SOL} V{SOL - 22} H720 V{SOL} Z" fill="url(#h1)" {ST} stroke-width="2"/>'
               f'<path d="M676 {SOL - 22} H724 M716 {SOL - 22} L736 {SOL - 34}" {ST} stroke-width="2.4"/>')
    # le feu tiède (x 1250) : un cercle de pierres, des braises en papier, un filet de fumée
    for k in range(7):
        a = math.pi * k / 6
        out.append(f'<ellipse cx="{1250 + 50 * math.cos(a):.0f}" cy="{SOL - 6 + 6 * math.sin(a):.0f}" rx="14" ry="9" fill="url(#moellons)" {ST} stroke-width="1.8"/>')
    out.append(f'<path d="M1220 {SOL - 8} L1280 {SOL - 20} M1226 {SOL - 20} L1276 {SOL - 6}" {ST} stroke-width="6"/>')
    out.append(f'<path d="M1250 {SOL - 24} Q1236 {SOL - 90} 1262 {SOL - 150} Q1284 {SOL - 210} 1256 {SOL - 280}" fill="none" stroke="{MINE}" stroke-width="3" opacity=".7"/>')
    out.append(sol(w, 5202))
    return "".join(out)


def cimetiere() -> str:
    """Les petites croix bien rangées, chacune sa cloche clouée et un nom en rayures ; les objets
    laissés ; la croix d'Aubin (clou vide, trace claire) ; la croix sans nom au bout du rang."""
    w = 2880
    out = [ciel(w), rangs(w, 5301, densite=.7)]
    r = rnd(5302)
    # le carré du cimetière : un talus pâle au fond, sur lequel tient la ligne de derrière
    out.append('<defs><linearGradient id="talus" x1="0" y1="0" x2="1" y2="0">'
               f'<stop offset=".85" stop-color="{PAPIER}" stop-opacity=".55"/><stop offset="1" stop-color="{PAPIER}" stop-opacity="0"/>'
               '</linearGradient></defs>'
               f'<rect y="{SOL - 56}" width="{w}" height="56" fill="url(#talus)"/>'
               f'<path d="M0 {SOL - 56} H{w - 400} Q{w - 200} {SOL - 56} {w - 120} {SOL}" fill="none" stroke="{MINE}" stroke-width="1.6"/>')
    # les rangs du cimetière : petites croix alignées, en deux lignes (celle de derrière en quinconce)
    for ligne, (pied, h, pas, dx) in enumerate(((SOL - 56, 150, 150, 75), (SOL, 210, 150, 0))):
        for x in range(120 + dx, w - 300, pas):
            if abs(x - AUBIN_X) < 130 or abs(x - SANS_NOM_X) < 130:
                continue
            out.append(f'<g opacity="{.8 if ligne == 0 else 1}">')
            out.append(croix_bois(x, pied, h, 11 if ligne == 0 else 13, 11 + ligne, .24))
            ty = pied - h * .74
            out.append(cloche(x - 3, ty + 12, .8 if ligne == 0 else 1))
            out.append(rayures(x - 10, ty - 30 if ligne else ty - 24, 4, int(x)))
            out.append('</g>')
    # objets laissés sur les croix (x 800 à 1030) : un calot, une écharpe nouée, une sangle
    out.append(f'<path d="M856 {SOL - 208} Q870 {SOL - 226} 886 {SOL - 208} Z" fill="url(#h2)" {ST} stroke-width="1.8"/>')
    out.append(f'<path d="M1028 {SOL - 150} q14 30 0 60 M1034 {SOL - 150} q-8 26 6 52" fill="none" {ST} stroke-width="3"/>')
    out.append(f'<path d="M806 {SOL - 164} q20 40 4 90" fill="none" stroke="{LAVIS}" stroke-width="5"/>')
    # la croix d'Aubin (x 1750) : pas de cloche, le clou et une trace plus claire sur le bois
    out.append(croix_bois(AUBIN_X, SOL, 300, 16, 5303, .2))
    cx, cy = CLOU
    out.append(f'<path d="M{cx - 7} {cy + 2} Q{cx - 8} {cy + 14} {cx} {cy + 20} Q{cx + 8} {cy + 14} {cx + 7} {cy + 2} Z" fill="{PAPIER}" opacity=".9"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="2.6" fill="{ENCRE}"/><path d="M{cx} {cy} l-4 -2" {ST} stroke-width="1.4"/>')
    out.append(rayures(AUBIN_X - 12, cy + 40, 5, 5304))
    # la croix sans nom, au bout du rang (x 1890) : bois neuf, pas de cloche, terre fraîche au pied
    out.append(croix_bois(SANS_NOM_X, SOL, 280, 16, 5305, .2))
    out.append(f'<path d="M{SANS_NOM_X - 90} {SOL} Q{SANS_NOM_X} {SOL - 34} {SANS_NOM_X + 90} {SOL} Z" fill="{LAVIS}" {ST} stroke-width="2"/>')
    out.append(f'<path d="M{SANS_NOM_X - 60} {SOL - 8} q20 -6 40 0 M{SANS_NOM_X + 10} {SOL - 14} q20 -6 40 0" fill="none" stroke="{MINE}" stroke-width="1.4"/>')
    out.append(sol(w, 5306))
    return "".join(out)


def clairiere() -> str:
    """Les croix s'espacent puis cessent ; le brouillard s'ouvre en haut : du papier nu, une
    trouée de ciel, un liseré de lumière sur l'herbe."""
    w = 1920
    out = [ciel(w),                                   # même brume que le cimetière au raccord
           '<defs><linearGradient id="ouvert" x1="0" y1="0" x2="1" y2="0">'
           f'<stop offset="0" stop-color="{PAPIER}" stop-opacity="0"/><stop offset=".6" stop-color="{PAPIER}" stop-opacity="1"/>'
           '</linearGradient></defs>',
           rangs(900, 5401, clair=.6),
           f'<rect width="{w}" height="{SOL}" fill="url(#ouvert)"/>']
    out.append(f'<path d="M900 200 Q1300 120 1920 160 M1000 280 Q1400 230 1920 250" fill="none" stroke="{MINE}" stroke-width="1.6"/>')
    out.append(f'<path d="M600 {HORIZON + 30} Q1100 {HORIZON + 20} 1920 {HORIZON + 60}" fill="none" stroke="{MINE}" stroke-width="2"/>')
    out.append(sol(w, 5402))
    out.append(f'<path d="M1100 {SOL + 5} H1920" stroke="{PAPIER}" stroke-width="5"/>')
    return "".join(out)


# --------------------------------------------------------------------------- calques fx
# Ancre de chaque calque dans le repère du déclencheur (son pied) : coin haut-gauche du dessin.
ANCRES = {"entaille": (-32, ENTAILLE_Y - SOL - 48), "cloche": (CLOU[0] - AUBIN_X - 32, CLOU[1] - SOL - 8),
          "nom-grave": (-32, NOM_Y - SOL - 24)}


def fx_entaille() -> str:
    """Deux encoches sur le poteau : la fraîche (bois clair) et dessous l'ancienne, noircie."""
    return (f'<path d="M24 46 L40 42 L38 52 L26 54 Z" fill="{PAPIER}" {ST} stroke-width="1.6"/>'
            f'<path d="M27 50 L37 47" stroke="{MINE}" stroke-width="1"/>'
            f'<path d="M25 70 L39 67 L37 76 L27 78 Z" fill="{LAVIS}" {ST} stroke-width="1.4"/>')


def fx_cloche() -> str:
    return cloche(32, 8)


def fx_nom_grave() -> str:
    """TOBIE, gravé au couteau en lettres maladroites, sur la traverse."""
    l = [f'<path d="M7 17 L57 16 L57 32 L7 32 Z" fill="{PAPIER}" opacity=".85"/>',  # bois frais, raclé
         f'<path d="M9 18 H19 M14 18 V30" {ST} stroke-width="1.8" fill="none"/>',          # T
         f'<ellipse cx="25" cy="24" rx="4" ry="6" {ST} stroke-width="1.8" fill="none"/>',   # O
         f'<path d="M32 18 V30 M32 18 Q39 19 36 24 Q40 28 32 30 M32 24 H36" {ST} stroke-width="1.8" fill="none"/>',  # B
         f'<path d="M43 18 V30" {ST} stroke-width="1.8"/>',                                 # I
         f'<path d="M54 18 H48 V30 H54 M48 24 H52" {ST} stroke-width="1.8" fill="none"/>']  # E
    return "".join(l)


def ecrire(nom: str, contenu: str, largeur: int) -> int:
    DST.mkdir(parents=True, exist_ok=True)
    n = math.ceil(largeur / TUILE)
    for i in range(n):
        x0 = i * TUILE
        w = min(TUILE, largeur - x0)
        (DST / f"env_e5_plan3_{nom}_{i + 1:02d}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="{x0} 0 {w} {H}">{DEFS}{contenu}</svg>\n',
            encoding="utf-8")
    return n


SECTIONS = {"oree": (oree, 1920), "boucle": (boucle, 3840), "campement": (campement, 1920),
            "cimetiere": (cimetiere, 2880), "clairiere": (clairiere, 1920)}


def main() -> None:
    total = sum(ecrire(nom, fn(), w) for nom, (fn, w) in SECTIONS.items())
    FX.mkdir(parents=True, exist_ok=True)
    for nom, fn in (("entaille-croix", fx_entaille), ("cloche-aubin", fx_cloche), ("nom-grave", fx_nom_grave)):
        (FX / f"fx_{nom}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="96" viewBox="0 0 64 96">{DEFS}{fn()}</svg>\n',
            encoding="utf-8")
    print(f"{total} tuiles de l'étape 5 et 3 calques fx")


if __name__ == "__main__":
    main()
