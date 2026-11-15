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
  cimetiere  2880  de petites croix d'âges divers, cloches sans battant (pendues,
                   tombées ou disparues) ; les objets
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
battant. Les noms des croix sont griffés, illisibles, sauf celui que Tobie grave ; aucune série
de signes ne peut se compter.

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


def griffures(x: float, y: float, larg: float, seed: int, op: float = 1.0) -> str:
    """Un nom griffé au couteau, vu d'ici : un trait qui court en travers, boucles et
    accrocs irréguliers, illisible et impossible à compter."""
    r = rnd(seed)
    d = [f"M{x:.1f} {y + r.uniform(-1, 1):.1f}"]
    cx = x
    while cx < x + larg:
        pas = r.uniform(2.5, 6)
        d.append(f"q{pas / 2:.1f} {r.uniform(-4, 4):.1f} {pas:.1f} {r.uniform(-1.5, 1.5):.1f}")
        cx += pas
    return f'<path d="{" ".join(d)}" fill="none" stroke="{ENCRE}" stroke-width="1" opacity="{op:.2f}"/>'


def mousse(x: float, y: float, seed: int) -> str:
    """Une touffe de mousse sur le bois pourri : de petites bosses, sans compte possible."""
    r = rnd(seed)
    return "".join(f'<ellipse cx="{x + r.uniform(-7, 7):.1f}" cy="{y + r.uniform(-2, 2):.1f}" rx="{r.uniform(2, 5):.1f}" '
                   f'ry="{r.uniform(1.5, 3):.1f}" fill="{MINE}" opacity=".8"/>' for _ in range(r.randint(3, 6)))


def petite_croix(r, x: float, pied: float, h: float, larg: float) -> tuple[str, dict]:
    """Une croix du cimetière : son âge (pourrie, ordinaire ou récente), son inclinaison, sa
    cloche (pendue, tombée dans l'herbe ou disparue) et un nom griffé, ou rien.
    Rend le dessin et ce qu'il faut pour y accrocher un objet (angle, sommet, traverse)."""
    age = r.random()
    a = r.uniform(-4, 4) if age > .25 else r.choice((-1, 1)) * r.uniform(6, 13)
    b = h * r.uniform(.2, .3)
    ty = pied - h * r.uniform(.7, .78)
    fond = "url(#h1)" if age > .8 else ("url(#h2)" if age < .25 else "url(#h1)")
    bois = PAPIER if age > .8 else None
    g = [f'<g transform="rotate({a:.1f} {x:.0f} {pied:.0f})">']
    haut = pied - h
    if age < .25:     # bois pourri : sommet rongé, un bras cassé court
        g.append(f'<path d="M{x - larg / 2:.1f} {pied:.0f} V{haut + 6:.0f} L{x - 1:.0f} {haut:.0f} L{x + 2:.0f} {haut + 8:.0f} '
                 f'L{x + larg / 2:.1f} {haut + 3:.0f} V{pied:.0f} Z" fill="{fond}" {ST} stroke-width="2.2"/>')
        bg, bd = b, b * r.uniform(.35, .6)
        if r.random() < .5:
            bg, bd = bd, bg
        g.append(f'<path d="M{x - bg:.1f} {ty - larg / 2:.1f} H{x + bd:.1f} l-3 {larg * .45:.1f} l3 {larg * .55:.1f} H{x - bg:.1f} Z" '
                 f'fill="{fond}" {ST} stroke-width="2.2"/>')
        g.append(mousse(x - bg * .4, ty - larg / 2, int(x) + 1))
    else:
        f = bois or fond
        g.append(f'<rect x="{x - larg / 2:.1f}" y="{haut:.0f}" width="{larg:.1f}" height="{h:.0f}" fill="{f}" {ST} stroke-width="2.2"/>')
        g.append(f'<rect x="{x - b:.1f}" y="{ty - larg / 2:.1f}" width="{2 * b:.1f}" height="{larg:.1f}" fill="{f}" {ST} stroke-width="2.2"/>')
    if r.random() < .65:
        g.append(griffures(x - b * .7, ty, b * 1.4, int(x) + 2, .9 if age > .25 else .55))
    cl = r.random()
    if cl < .55:
        g.append(cloche(x + r.uniform(-4, 2), ty + larg / 2 + 1, larg / 13))
    g.append('</g>')
    if .55 <= cl < .72:   # tombée dans l'herbe, couchée au pied
        cx = x + r.choice((-1, 1)) * r.uniform(14, 30)
        g.append(f'<g transform="rotate({r.choice((-1, 1)) * r.uniform(70, 110):.0f} {cx:.0f} {SOL - 6:.0f})">'
                 f'{cloche(cx, SOL - 14, larg / 13)}</g>')
    return "".join(g), {"x": x, "a": a, "pied": pied, "haut": haut, "ty": ty, "larg": larg}


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
    """Un cimetière qui a grandi lentement : petites croix d'âges divers, cloches pendues, tombées
    ou disparues, noms griffés ; les objets
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
    # le cimetière a grandi lentement : deux lignes lâches, espacement, hauteur, âge et
    # inclinaison inégaux ; rien ne s'aligne ni ne se compte
    lignes: list[list[dict]] = [[], []]
    for ligne, (pied, hmin, hmax, pmin, pmax) in enumerate(((SOL - 56, 110, 180, 80, 210), (SOL, 150, 250, 100, 240))):
        x = 100 + r.uniform(0, 80)
        while x < w - 320:
            if abs(x - AUBIN_X) > 130 and abs(x - SANS_NOM_X) > 130:
                dessin, info = petite_croix(r, x, pied + r.uniform(-6, 4), r.uniform(hmin, hmax), r.uniform(10, 14))
                out.append(f'<g opacity="{.8 if ligne == 0 else 1}">{dessin}</g>')
                lignes[ligne].append(info)
            x += r.uniform(pmin, pmax)

    def proche(ligne: int, cible: float) -> dict:
        return min(lignes[ligne], key=lambda c: abs(c["x"] - cible))

    def sur(c: dict, svg: str) -> str:
        return f'<g transform="rotate({c["a"]:.1f} {c["x"]:.0f} {c["pied"]:.0f})">{svg}</g>'

    # objets laissés sur les croix (autour de x 900) : un calot, une écharpe nouée, une sangle
    c = proche(1, 880)
    out.append(sur(c, f'<path d="M{c["x"] - 14:.0f} {c["haut"] + 4:.0f} Q{c["x"]:.0f} {c["haut"] - 14:.0f} {c["x"] + 16:.0f} {c["haut"] + 4:.0f} Z" fill="url(#h2)" {ST} stroke-width="1.8"/>'))
    c = proche(1, 1020)
    out.append(sur(c, f'<path d="M{c["x"] + 4:.0f} {c["ty"]:.0f} q14 30 0 60 M{c["x"] + 10:.0f} {c["ty"]:.0f} q-8 26 6 52" fill="none" {ST} stroke-width="3"/>'))
    c = proche(0, 800)
    out.append(sur(c, f'<path d="M{c["x"] + 2:.0f} {c["ty"]:.0f} q20 40 4 90" fill="none" stroke="{LAVIS}" stroke-width="5"/>'))
    # des rubans délavés, noués sur quelques croix seulement, à des âges différents : le même
    # ruban que celui du pli de Tobie, mais lavé par les hivers (lavis : pâle à l'écran inversé,
    # jamais le rouge) ; du plus récent au plus vieux, il pâlit et raccourcit
    def ruban(c: dict, couleur: str, l1: float, l2: float, ep: float) -> str:
        x, y = c["x"], c["ty"]
        return sur(c, f'<path d="M{x - 7:.0f} {y - 3:.0f} l14 6 M{x + 7:.0f} {y - 3:.0f} l-14 6" stroke="{couleur}" stroke-width="{ep:.1f}"/>'
                      f'<path d="M{x + 2:.0f} {y + 3:.0f} q8 {l1 * .5:.0f} 2 {l1:.0f} M{x - 1:.0f} {y + 3:.0f} q-9 {l2 * .5:.0f} -4 {l2:.0f}" '
                      f'fill="none" stroke="{couleur}" stroke-width="{ep * .8:.1f}" stroke-linecap="round"/>')
    out.append(ruban(proche(1, 420), LAVIS, 52, 38, 6.5))
    out.append(ruban(proche(0, 1360), LAVIS, 32, 20, 5.5))
    out.append(ruban(proche(1, 2140), LAVIS, 18, 0, 5))
    out.append(ruban(proche(0, 2480), MINE, 8, 0, 4.5))
    # la croix d'Aubin (x 1750) : pas de cloche, le clou et une trace plus claire sur le bois
    out.append(croix_bois(AUBIN_X, SOL, 300, 16, 5303, .2))
    cx, cy = CLOU
    out.append(f'<path d="M{cx - 7} {cy + 2} Q{cx - 8} {cy + 14} {cx} {cy + 20} Q{cx + 8} {cy + 14} {cx + 7} {cy + 2} Z" fill="{PAPIER}" opacity=".9"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="2.6" fill="{ENCRE}"/><path d="M{cx} {cy} l-4 -2" {ST} stroke-width="1.4"/>')
    out.append(griffures(AUBIN_X - 24, cy + 62, 48, 5304))
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
    """TOBIE, gravé au couteau par un homme qui vient de se couper le pouce, sur la traverse :
    lettres inégales et peu profondes, ligne qui monte et descend, le trait du I qui dérape, et
    le E plus faible, à peine marqué."""
    trait = f'fill="none" stroke="{ENCRE}" stroke-linecap="round" stroke-linejoin="round"'
    return (f'<path d="M7 17.5 L57 16.5 L56.5 32 L7.5 31.5 Z" fill="{PAPIER}" opacity=".8"/>'   # bois frais, raclé
            f'<g {trait} stroke-width="1.4" opacity=".85">'
            '<path d="M9 19.6 L18.6 18.1 M13.5 18.9 L14.3 30.6"/>'                             # T
            '<path d="M24 19.2 Q20.2 20.4 20.6 25.2 Q21.2 31 25.1 30.4 Q28.6 29.4 28 24 Q27.2 18.8 23.4 19.8"/>'  # O
            '<path d="M31.6 18.6 L32.4 30.9 M31.9 18.5 Q38.4 17.9 35.4 23.7 L32.3 24.3 '
            'M33.1 24.1 Q39.8 25.8 35.8 29.9 Q34 31.1 32.4 30.7"/>'                            # B
            '<path d="M42.4 19.4 L43.3 29.2 L47.4 33"/>'                                        # I, et le dérapage
            '</g>'
            f'<path d="M53.2 20.2 L47.9 19.6 L48.5 29.6 L52.1 30.3 M48.2 24.9 L50.8 24.5" {trait} stroke-width="1" opacity=".45"/>')  # E


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
