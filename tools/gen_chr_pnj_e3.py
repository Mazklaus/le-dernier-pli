#!/usr/bin/env python3
"""Génère les personnages de l'étape 3, le Village aux cloches muettes.

Même repère et même échelle que les PNJ des étapes 1 et 2 (source 240 x 420, sol à y 405,
centre à x 120, échelle 0,845) : images de 200 x 320, sol à y 316, centre à x 100.

  chr_enfants_repos_01     : 4 images ; deux enfants du verger, fusils de bâton (e3_lisiere).
  chr_ilde_repos_01        : 4 images ; Maîtresse Ilde, ronde et calme, trousseau de clés (e3_ilde).
  chr_rose_repos_01        : 4 images ; la mariée, robe blanche, voile qui bouge (e3_noce).
  chr_violoneux_repos_01   : 4 images ; le violon de la noce, l'archet va et vient (e3_noce).
  chr_sonneur_repos_01     : 4 images ; le vieux sonneur tire une corde qui ne tient à rien (e3_clocher).
  chr_procession_marche_01 : 4 images ; un villageois encapuchonné, cierge à la main ; la flamme
                             a sa réserve de papier nu, pour la nuit (e3_procession, chemin de nuit).

Village trop propre : beaucoup de papier, des visages tranquilles. Aucun rouge (les rubans de la
noce sont en papier : le rouge reste au sceau et au ruban du pli).

Usage : python3 tools/gen_chr_pnj_e3.py
"""
from __future__ import annotations

import math

from gen_chr_pnj_e2 import CADRE_L, DEFS, DST, ENCRE, LAVIS, MINE, PAPIER, ST, planche


def visage(cx: float, cy: float, r: float = 20, barbe: bool = False, sourire: bool = False, yeux_clos: bool = False) -> str:
    """Visage de trois quarts tourné vers la gauche (vers Tobie qui arrive) : traits simples."""
    s = [f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r * 1.15:.1f}" fill="{PAPIER}" {ST} stroke-width="2.2"/>']
    if barbe:
        # barbe blanche qui pend sous la mâchoire, hors du visage (la bouche reste lisible)
        s.append(f'<path d="M{cx - r * .85:.0f} {cy + r * .55:.0f} Q{cx - r * .6:.0f} {cy + r * 1.7:.0f} {cx:.0f} {cy + r * 1.8:.0f} Q{cx + r * .6:.0f} {cy + r * 1.6:.0f} {cx + r * .85:.0f} {cy + r * .55:.0f} Q{cx:.0f} {cy + r * 1.2:.0f} {cx - r * .85:.0f} {cy + r * .55:.0f} Z" fill="{PAPIER}" {ST} stroke-width="1.6"/>')
        s.append(f'<path d="M{cx - r * .3:.0f} {cy + r * 1.2:.0f} L{cx - r * .25:.0f} {cy + r * 1.5:.0f} M{cx + r * .2:.0f} {cy + r * 1.2:.0f} L{cx + r * .22:.0f} {cy + r * 1.5:.0f}" stroke="{MINE}" stroke-width="1.2"/>')
    oy = cy - r * .12
    if yeux_clos:
        s.append(f'<path d="M{cx - r * .55:.0f} {oy:.0f} Q{cx - r * .35:.0f} {oy + 3:.0f} {cx - r * .15:.0f} {oy:.0f} M{cx + r * .1:.0f} {oy:.0f} Q{cx + r * .3:.0f} {oy + 3:.0f} {cx + r * .5:.0f} {oy:.0f}" fill="none" {ST} stroke-width="1.6"/>')
    else:
        s.append(f'<path d="M{cx - r * .5:.0f} {oy:.0f} L{cx - r * .25:.0f} {oy:.0f} M{cx + r * .1:.0f} {oy:.0f} L{cx + r * .35:.0f} {oy:.0f}" {ST} stroke-width="2.4"/>')
    s.append(f'<path d="M{cx - r * .1:.0f} {oy + 2:.0f} L{cx - r * .22:.0f} {cy + r * .35:.0f} L{cx - r * .02:.0f} {cy + r * .38:.0f}" fill="none" {ST} stroke-width="1.4"/>')
    if sourire:
        s.append(f'<path d="M{cx - r * .35:.0f} {cy + r * .6:.0f} Q{cx - r * .1:.0f} {cy + r * .8:.0f} {cx + r * .2:.0f} {cy + r * .58:.0f}" fill="none" {ST} stroke-width="1.6"/>')
    else:
        s.append(f'<path d="M{cx - r * .3:.0f} {cy + r * .62:.0f} L{cx + r * .15:.0f} {cy + r * .62:.0f}" {ST} stroke-width="1.6"/>')
    return "".join(s)


def flamme(x: float, y: float, h: float) -> str:
    return (f'<path d="M{x:.1f} {y:.1f} Q{x - h * .24:.1f} {y - h * .45:.1f} {x:.1f} {y - h:.1f} '
            f'Q{x + h * .24:.1f} {y - h * .45:.1f} {x:.1f} {y:.1f} Z" fill="{PAPIER}" {ST} stroke-width="1.6"/>')


def souffle(i: int) -> float:
    return (0, 1, 2, 1)[i]


# ------------------------------------------------------------------ les enfants du verger

def enfants(i: int) -> str:
    s = souffle(i)
    out = []
    # le grand, à gauche : vise avec son bâton, en appui sur une jambe
    out.append(f'<path d="M70 330 L62 400 L80 400 L84 334 Z M90 330 L98 398 L116 398 L104 328 Z" fill="url(#h1)" {ST} stroke-width="2.2"/>')
    out.append(f'<path d="M56 396 L54 405 L82 405 L80 396 Z M96 394 L96 405 L122 405 L118 394 Z" fill="{ENCRE}" {ST} stroke-width="1.4"/>')
    out.append(f'<g transform="translate(0 {s * .6:.1f})">')
    out.append(f'<path d="M64 334 Q60 272 78 246 L104 244 Q118 280 110 334 Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>')
    out.append(f'<path d="M66 300 H108" {ST} stroke-width="1.4"/><path d="M80 246 L84 334" stroke="{MINE}" stroke-width="1.4"/>')
    # bretelles, culotte courte rapiécée
    out.append(f'<path d="M78 248 L74 330 M100 246 L104 330" {ST} stroke-width="2"/>')
    out.append(f'<rect x="88" y="306" width="14" height="12" fill="url(#h2)" {ST} stroke-width="1.4"/>')
    # le fusil de bâton, épaulé, pointé vers la gauche (vers Tobie)
    out.append(f'<path d="M100 262 L22 248 L22 242 L102 254 Z" fill="url(#h1)" {ST} stroke-width="2"/>')
    out.append(f'<path d="M96 254 Q110 262 104 276 L92 272 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>')
    out.append(f'<path d="M66 262 Q56 258 48 252 L52 246 Q62 250 72 252 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>')
    out.append(visage(88, 222, 18, sourire=True))
    out.append(f'<path d="M70 214 Q72 194 90 194 Q108 196 108 216 Q98 204 84 208 Q76 210 70 214 Z" fill="url(#h2)" {ST} stroke-width="2"/>')
    out.append('</g>')
    # le plus petit, à droite : le bâton sur l'épaule, il regarde en l'air
    out.append(f'<path d="M150 352 L146 400 L160 400 L162 354 Z M168 352 L172 400 L186 400 L178 350 Z" fill="url(#h1)" {ST} stroke-width="2"/>')
    out.append(f'<path d="M140 397 L140 405 L162 405 L160 397 Z M170 397 L170 405 L192 405 L188 397 Z" fill="{ENCRE}" {ST} stroke-width="1.4"/>')
    out.append(f'<g transform="translate(0 {s * .5:.1f})">')
    out.append(f'<path d="M144 356 Q140 310 156 290 L176 290 Q190 316 184 356 Z" fill="url(#h1)" {ST} stroke-width="2.2"/>')
    out.append(f'<path d="M176 296 L198 220 L204 222 L182 300 Z" fill="url(#h1)" {ST} stroke-width="1.8"/>')
    out.append(f'<path d="M172 300 Q182 294 186 284 L194 290 Q188 304 176 310 Z" fill="{PAPIER}" {ST} stroke-width="1.6"/>')
    out.append(visage(166, 272, 15))
    out.append(f'<path d="M150 266 Q150 248 166 248 Q182 248 182 266 Q172 256 160 260 Z" fill="url(#h2)" {ST} stroke-width="1.8"/>')
    out.append('</g>')
    return "".join(out)


# ------------------------------------------------------------------ Maîtresse Ilde

def ilde(i: int) -> str:
    s = souffle(i)
    out = [
        # sabots sous la robe longue
        f'<path d="M84 394 L80 405 L114 405 L112 394 Z M126 394 L126 405 L160 405 L156 394 Z" fill="{ENCRE}" {ST} stroke-width="1.4"/>',
        f'<g transform="translate(0 {s:.1f})">',
        # la robe : une cloche ronde et calme, sombre
        f'<path d="M92 170 Q66 210 64 290 Q62 360 70 398 L170 398 Q178 360 176 290 Q174 210 148 170 Z" fill="url(#h2)" {ST} stroke-width="2.8"/>',
        # le tablier blanc, très propre
        f'<path d="M96 236 Q92 320 98 392 L144 392 Q150 320 146 236 Z" fill="{PAPIER}" {ST} stroke-width="2.2"/>',
        f'<path d="M104 300 H138 M106 340 H136" stroke="{MINE}" stroke-width="1.4"/>',
        f'<path d="M80 236 Q120 246 160 236" fill="none" {ST} stroke-width="2.6"/>',
        # le trousseau de clés à la ceinture
        f'<path d="M150 238 L152 252" {ST} stroke-width="1.6"/><circle cx="153" cy="258" r="7" fill="none" {ST} stroke-width="2"/>',
    ]
    for k, (dx, dy) in enumerate(((-6, 12), (0, 16), (7, 13))):
        x, y = 153 + dx, 262 + dy
        out.append(f'<path d="M{x} {y - 6} V{y + 14} M{x} {y + 10} H{x + 5} M{x} {y + 14} H{x + 4}" {ST} stroke-width="1.8"/>')
    out += [
        # le châle croisé sur la poitrine
        f'<path d="M84 172 Q120 196 156 172 L162 214 Q120 246 78 214 Z" fill="url(#h1)" {ST} stroke-width="2.2"/>',
        # bras croisés, mains posées l'une sur l'autre
        f'<path d="M78 196 Q70 236 96 250 L140 246 Q150 238 140 230 L102 232 Q92 220 96 200 Z" fill="url(#h2)" {ST} stroke-width="2.2"/>',
        f'<path d="M128 228 Q146 224 148 236 Q142 246 128 244 Z M106 236 Q118 230 130 238 Q122 248 108 246 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>',
        # tête : visage rond, coiffe nouée
        visage(118, 138, 24, sourire=True),
        f'<path d="M90 160 Q82 104 120 96 Q156 102 148 160 Q146 126 120 118 Q96 124 90 160 Z" fill="{PAPIER}" {ST} stroke-width="2.2"/>',
        f'<path d="M96 120 Q120 108 144 120" fill="none" stroke="{MINE}" stroke-width="1.4"/>',
        f'<path d="M136 160 L146 174 M140 158 L154 168" {ST} stroke-width="1.6"/>',
        '</g>',
    ]
    return "".join(out)


# ------------------------------------------------------------------ Rose, la mariée

def rose(i: int) -> str:
    s = souffle(i)
    vent = (0, 3, 5, 3)[i]
    out = [
        f'<g transform="translate(0 {s * .8:.1f})">',
        # le voile, derrière : il bouge un peu (seul mouvement de la noce qui ne s'arrête pas)
        f'<path d="M108 108 Q86 170 78 {300 + vent} L{96 + vent} {306 + vent} Q104 200 124 112 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>',
        f'<path d="M100 150 Q90 220 {88 + vent / 2:.0f} 290" fill="none" stroke="{MINE}" stroke-width="1.2"/>',
        # la robe blanche, longue, la traîne posée au sol
        f'<path d="M104 176 Q92 260 70 400 L176 404 Q154 270 140 176 Z" fill="{PAPIER}" {ST} stroke-width="2.6"/>',
        f'<path d="M106 240 Q100 320 92 398 M138 240 Q146 320 154 402 M122 250 V400" fill="none" stroke="{MINE}" stroke-width="1.3"/>',
        f'<path d="M98 236 Q122 244 146 236" fill="none" {ST} stroke-width="2"/>',
        # corsage, bras, le bouquet de lavande (tiges et épis, pas de couleur)
        f'<path d="M104 176 Q122 166 140 176 L144 238 L100 238 Z" fill="{PAPIER}" {ST} stroke-width="2.2"/>',
        f'<path d="M104 182 Q92 220 110 248 L120 242 Q108 220 112 190 Z M140 182 Q152 220 134 248 L124 242 Q136 220 132 190 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>',
        f'<path d="M118 250 L110 214 M122 250 L122 210 M126 250 L134 214" {ST} stroke-width="1.4"/>',
        f'<path d="M108 214 L112 202 M120 210 L122 196 M132 214 L136 202" stroke="{LAVIS}" stroke-width="4" stroke-linecap="round"/>',
        f'<path d="M112 246 L132 246 L128 258 L116 258 Z" fill="{PAPIER}" {ST} stroke-width="1.6"/>',
        # rubans de la noce, en papier, qui pendent du bouquet
        f'<path d="M118 258 Q112 290 {116 + vent} 318 M126 258 Q132 286 {128 + vent} 312" fill="none" {ST} stroke-width="1.6"/>',
        visage(122, 140, 20, sourire=True),
        # cheveux relevés, couronne de fleurs des champs
        f'<path d="M102 134 Q102 108 122 106 Q142 108 142 134 Q132 120 122 120 Q110 120 102 134 Z" fill="url(#h1)" {ST} stroke-width="2"/>',
    ]
    for k in range(5):
        a = math.pi * (1.1 - k * .3)
        x, y = 122 + math.cos(a) * 20, 118 - math.sin(a) * 10
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="3.6" fill="{PAPIER}" {ST} stroke-width="1.4"/>')
    out.append('</g>')
    return "".join(out)


# ------------------------------------------------------------------ le violon de la noce

def violoneux(i: int) -> str:
    s = souffle(i)
    archet = (0, 14, 26, 14)[i]
    return (
        f'<path d="M98 300 L94 396 L116 396 L118 300 Z M126 300 L132 396 L154 396 L146 300 Z" fill="url(#mol)" {ST} stroke-width="2.2"/>'
        f'<path d="M88 392 L86 405 L120 405 L118 392 Z M128 392 L128 405 L162 405 L158 392 Z" fill="{ENCRE}" {ST} stroke-width="1.4"/>'
        f'<g transform="translate(0 {s * .8:.1f})">'
        # chemise blanche, gilet hachuré
        f'<path d="M92 170 Q84 240 94 306 L152 306 Q160 240 150 170 Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>'
        f'<path d="M96 178 Q92 240 98 304 L120 304 L118 180 Z M146 178 Q152 240 146 304 L124 304 L126 180 Z" fill="url(#h1)" {ST} stroke-width="2"/>'
        f'<circle cx="114" cy="230" r="2" fill="{ENCRE}"/><circle cx="114" cy="256" r="2" fill="{ENCRE}"/>'
        # le violon sous le menton, tenu de la main gauche (bras levé vers la gauche)
        f'<path d="M94 182 Q70 180 54 168 L58 158 Q76 168 98 170 Z" fill="{PAPIER}" {ST} stroke-width="2"/>'
        f'<path d="M58 160 L44 152 L48 146 L62 154 Z" fill="{PAPIER}" {ST} stroke-width="1.6"/>'
        f'<path d="M78 156 Q72 146 82 140 Q90 134 100 142 Q110 140 114 150 Q118 162 106 168 Q96 176 86 170 Q76 168 78 156 Z" fill="url(#h2)" {ST} stroke-width="2.2"/>'
        f'<path d="M54 160 L84 154" {ST} stroke-width="2.4"/>'
        # l'archet, de la main droite : il va et vient
        f'<path d="M150 186 Q140 200 {128 - archet / 2:.0f} {190 - archet / 4:.0f}" fill="none" {ST} stroke-width="10"/>'
        f'<path d="M{124 - archet / 2:.0f} {186 - archet / 4:.0f} Q{130 - archet / 2:.0f} {182 - archet / 4:.0f} {134 - archet / 2:.0f} {190 - archet / 4:.0f} Q{126 - archet / 2:.0f} {196 - archet / 4:.0f} {124 - archet / 2:.0f} {186 - archet / 4:.0f} Z" fill="{PAPIER}" {ST} stroke-width="1.6"/>'
        f'<path d="M{160 - archet:.0f} {176 - archet / 3:.0f} L{70 - archet:.0f} {148 - archet / 3:.0f}" {ST} stroke-width="2"/>'
        # tête inclinée sur l'instrument, yeux fermés, chapeau
        + visage(112, 136, 20, barbe=True, yeux_clos=True) +
        f'<path d="M88 118 L136 112 L136 104 Q132 84 112 84 Q94 86 92 108 L86 110 Z" fill="url(#h2)" {ST} stroke-width="2.2"/>'
        f'<path d="M80 116 L144 108" {ST} stroke-width="4"/>'
        '</g>'
    )


# ------------------------------------------------------------------ le sonneur

def sonneur(i: int) -> str:
    # il tire, lentement : les mains descendent puis remontent, la corde avec elles
    tire = (0, 10, 18, 10)[i]
    s = souffle(i)
    return (
        # la corde : elle pend de rien, son bout coupé net flotte au-dessus des mains
        f'<path d="M140 {44 + tire} V{210 + tire}" {ST} stroke-width="5"/>'
        f'<path d="M134 {44 + tire} H146" {ST} stroke-width="3"/>'
        f'<path d="M140 {210 + tire} Q144 {250 + tire} 138 {290 + tire}" fill="none" {ST} stroke-width="5"/>'
        f'<path d="M92 302 L88 396 L110 396 L114 302 Z M124 302 L130 396 L152 396 L144 302 Z" fill="url(#mol)" {ST} stroke-width="2.2"/>'
        f'<path d="M82 392 L80 405 L114 405 L112 392 Z M126 392 L126 405 L160 405 L156 392 Z" fill="{ENCRE}" {ST} stroke-width="1.4"/>'
        f'<g transform="translate(0 {s * .6 + tire * .25:.1f})">'
        # longue blouse de toile, dos un peu voûté
        f'<path d="M92 160 Q74 220 76 310 L156 314 Q156 230 140 164 Q118 150 92 160 Z" fill="url(#h1)" {ST} stroke-width="2.6"/>'
        f'<path d="M80 280 H154" stroke="{MINE}" stroke-width="1.4"/>'
        '</g>'
        # les bras levés vers la corde, les deux mains serrées dessus
        f'<path d="M100 {176 + tire * .25:.0f} Q112 {170 + tire} 132 {180 + tire} L136 {194 + tire} Q114 {188 + tire} 106 {200 + tire * .25:.0f} Z" fill="url(#h1)" {ST} stroke-width="2.2"/>'
        f'<path d="M134 {176 + tire} Q150 {160 + tire} 146 {148 + tire} L138 {146 + tire} Q140 {162 + tire} 126 {168 + tire} Z" fill="url(#h1)" {ST} stroke-width="2.2"/>'
        f'<path d="M132 {174 + tire} Q140 {170 + tire} 148 {176 + tire} L148 {192 + tire} Q140 {196 + tire} 132 {190 + tire} Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>'
        f'<path d="M134 {140 + tire} Q140 {134 + tire} 146 {140 + tire} L146 {154 + tire} Q140 {158 + tire} 134 {152 + tire} Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>'
        # tête levée vers le haut, vers rien ; vieux, tondu, barbe blanche
        f'<g transform="translate(0 {s * .6 + tire * .25:.1f})">'
        # tête renversée en arrière, le regard tout en haut, vers la baie vide : on voit le dessous
        # du menton, la barbe pointe vers l'avant, les yeux sont remontés au ras du front
        f'<path d="M98 150 Q104 168 122 166 Q134 160 130 146" fill="{PAPIER}" {ST} stroke-width="2"/>'
        f'<ellipse cx="112" cy="128" rx="21" ry="20" fill="{PAPIER}" {ST} stroke-width="2.2"/>'
        f'<path d="M92 138 Q84 150 86 166 Q100 160 106 146 Z" fill="{PAPIER}" {ST} stroke-width="1.6"/>'
        f'<path d="M88 150 L90 158 M94 148 L96 156" stroke="{MINE}" stroke-width="1.2"/>'
        f'<path d="M98 116 Q102 112 106 116 M114 114 Q118 110 122 114" fill="none" {ST} stroke-width="1.8"/>'
        f'<circle cx="102" cy="114" r="1.8" fill="{ENCRE}"/><circle cx="118" cy="112" r="1.8" fill="{ENCRE}"/>'
        f'<path d="M106 122 L100 128 L106 130" fill="none" {ST} stroke-width="1.4"/>'
        f'<ellipse cx="104" cy="138" rx="4" ry="2.6" fill="{ENCRE}"/>'
        f'<path d="M96 112 Q98 98 114 98 Q130 100 132 116 Q124 106 112 106 Q102 106 96 112 Z" fill="url(#pt)" {ST} stroke-width="1.8"/>'
'</g>'
    )


# ------------------------------------------------------------------ la procession

def procession(i: int) -> str:
    """Un villageois encapuchonné qui marche vers la droite, le cierge tenu bas, à deux mains."""
    pas = (0, 6, 0, -6)[i]
    hausse = (0, 2, 0, 2)[i]
    out = [
        # bas de la grande cape qui balaie le sol, pieds à peine visibles
        f'<path d="M{96 - pas} 394 L{92 - pas} 405 L{118 - pas} 405 L{116 - pas} 394 Z M{128 + pas} 394 L{128 + pas} 405 L{154 + pas} 405 L{150 + pas} 394 Z" fill="{ENCRE}" {ST} stroke-width="1.4"/>',
        f'<g transform="translate(0 {-hausse})">',
        f'<path d="M100 120 Q72 200 70 300 Q68 360 {78 - pas} 398 L{168 + pas} 398 Q174 350 168 290 Q164 200 140 120 Q120 100 100 120 Z" fill="url(#h2)" {ST} stroke-width="2.8"/>',
        f'<path d="M112 160 Q104 280 {108 - pas / 2:.0f} 396 M140 170 Q150 280 {150 + pas / 2:.0f} 396" fill="none" {ST} stroke-width="1.6"/>',
        # capuchon profond : le visage reste dans le noir
        f'<path d="M96 132 Q92 76 124 70 Q156 76 152 132 Q150 156 124 160 Q100 156 96 132 Z" fill="url(#h2)" {ST} stroke-width="2.6"/>',
        f'<path d="M110 118 Q112 92 132 90 Q148 96 146 126 Q140 146 124 148 Q110 142 110 118 Z" fill="{ENCRE}"/>',
        # les mains jointes sur le cierge, à hauteur de poitrine
        f'<circle cx="152" cy="196" r="24" fill="{PAPIER}"/>',
        f'<rect x="146" y="200" width="12" height="54" fill="{PAPIER}" {ST} stroke-width="1.8"/>',
        f'<path d="M136 236 Q150 228 166 236 L166 252 Q150 260 136 252 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>',
        flamme(152, 198, 28 + (i % 2) * 3),
        f'<path d="M152 198 V204" {ST} stroke-width="1.6"/>',
        f'<path d="M118 200 Q124 236 138 244" fill="none" {ST} stroke-width="2.2"/>',
        '</g>',
    ]
    return "".join(out)


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    planches = {
        "chr_enfants_repos_01": [enfants(i) for i in range(4)],
        "chr_ilde_repos_01": [ilde(i) for i in range(4)],
        "chr_rose_repos_01": [rose(i) for i in range(4)],
        "chr_violoneux_repos_01": [violoneux(i) for i in range(4)],
        "chr_sonneur_repos_01": [sonneur(i) for i in range(4)],
        "chr_procession_marche_01": [procession(i) for i in range(4)],
    }
    for nom, images in planches.items():
        (DST / f"{nom}.svg").write_text(planche(images), encoding="utf-8")
    print(f"{len(planches)} planches dans art/src/chr")


if __name__ == "__main__":
    main()
