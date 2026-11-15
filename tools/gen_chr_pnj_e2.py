#!/usr/bin/env python3
"""Génère les personnages de l'étape 2 : le caporal Brisse et le mort qui montre le chemin.

Même repère que la planche n° 2 (240 x 420, sol à y 405), même échelle que Tobie (0,845) :
images de 200 x 320, sol à y 316, centre à x 100.

  chr_brisse_repos_01 : 4 images ; la flamme de sa bougie vacille, son souffle est lent.
                        Forme : l'arc, un dos rond penché sur une flamme qu'il protège.
  chr_mort_fige_01    : 1 image ; un cadavre affaissé sur un reste de fil, jambes molles, tête
                        tombée ; seul le bras tendu vers la droite et le bas est raide.

Aucun rouge : l'ennemi et la mort restent sans sang visible à l'étape 2.

Usage : python3 tools/gen_chr_pnj_e2.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DST = ROOT / "art" / "src" / "chr"

PAPIER, ENCRE, LAVIS, MINE = "#E8E5DA", "#15130F", "#4A463D", "#8C877A"
ECHELLE, CADRE_L, CADRE_H, SOL, CENTRE_X = 0.845, 200, 320, 405, 120
ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'

DEFS = f"""<defs>
<pattern id="h1" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(38)"><rect width="5" height="5" fill="{PAPIER}"/><line x1="0" y1="0" x2="0" y2="5" stroke="{ENCRE}" stroke-width="1.1"/></pattern>
<pattern id="h2" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(38)"><rect width="4" height="4" fill="{PAPIER}"/><line x1="0" y1="0" x2="0" y2="4" stroke="{ENCRE}" stroke-width="1.2"/><line x1="0" y1="2" x2="4" y2="2" stroke="{ENCRE}" stroke-width=".8"/></pattern>
<pattern id="mol" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(-22)"><rect width="9" height="9" fill="{PAPIER}"/><line x1="0" y1="0" x2="9" y2="0" stroke="{ENCRE}" stroke-width="1.8"/><line x1="0" y1="4.5" x2="9" y2="4.5" stroke="{ENCRE}" stroke-width=".7"/></pattern>
<pattern id="pt" width="4" height="4" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r=".8" fill="{ENCRE}"/></pattern>
</defs>"""


def brisse(i: int) -> str:
    """Le caporal Brisse, de trois quarts, penché sur sa bougie dans une boîte de conserve."""
    souffle = (0, 1, 2, 1)[i]
    # flamme en papier nu : quatre formes nettes (jamais de halo peint)
    flammes = ["M148 214 Q141 200 148 184 Q155 200 148 214 Z",
               "M148 214 Q140 202 150 186 Q156 202 148 214 Z",
               "M148 214 Q142 198 146 182 Q156 198 148 214 Z",
               "M148 214 Q141 204 149 190 Q155 204 148 214 Z"]
    # le dos rond : tout le haut du corps bascule vers la flamme, la tête plus encore
    haut = f'<g transform="translate(0 {souffle:.1f}) rotate(10 120 330)">'
    return (
        # jambes, bottes
        f'<path d="M92 316 L90 386 L116 386 L118 316 Z M126 316 L130 386 L156 386 L152 316 Z" fill="url(#mol)" {ST} stroke-width="2.4"/>'
        f'<path d="M84 382 L80 405 L120 405 L118 382 Z M126 382 L126 405 L166 405 L160 382 Z" fill="{ENCRE}" {ST} stroke-width="1.6"/>'
        + haut +
        # capote : l'arc, dos rond, pans élargis en bas
        f'<path d="M84 146 Q110 120 150 132 Q170 150 172 200 L184 326 L150 330 L144 318 L120 328 L96 318 L90 330 L58 324 L72 210 Q70 170 84 146 Z" fill="url(#h2)" {ST} stroke-width="2.8"/>'
        f'<path d="M120 140 L120 324" stroke="{PAPIER}" stroke-width="2.6"/><path d="M120 140 L120 324" stroke="{ENCRE}" stroke-width="1"/>'
        # cache-nez de laine, plusieurs tours
        f'<path d="M96 136 Q124 150 154 136 L156 152 Q124 168 94 152 Z" fill="url(#h1)" {ST} stroke-width="2.2"/>'
        f'<path d="M100 146 Q124 158 150 146" fill="none" {ST} stroke-width="1.2"/>'
        # avant-bras repliés : les mains en coupe autour de la boîte
        f'<path d="M80 176 Q92 214 126 222 L132 208 Q104 200 96 170 Z" fill="url(#h2)" {ST} stroke-width="2.4"/>'
        f'<path d="M168 178 Q170 214 160 226 L148 220 Q156 204 154 180 Z" fill="url(#h2)" {ST} stroke-width="2.4"/>'
        # la boîte de conserve et la bougie
        f'<rect x="132" y="214" width="32" height="30" fill="url(#h1)" {ST} stroke-width="2.2"/>'
        f'<path d="M132 214 L126 202 M164 214 L170 204" {ST} stroke-width="2"/>'
        f'<rect x="143" y="214" width="10" height="14" fill="{PAPIER}" {ST} stroke-width="1.6"/>'
        f'<path d="{flammes[i]}" fill="{PAPIER}" {ST} stroke-width="1.8"/>'
        # mains : deux formes claires qui encadrent la flamme
        f'<path d="M124 226 Q122 210 132 206 Q138 214 134 228 Z" fill="{PAPIER}" {ST} stroke-width="1.9"/>'
        f'<path d="M168 228 Q172 212 164 204 Q156 212 160 228 Z" fill="{PAPIER}" {ST} stroke-width="1.9"/>'
        '<g transform="rotate(14 126 142)">'
        # visage penché : front lourd, barbe de plusieurs jours, regard sur la flamme
        f'<path d="M104 92 Q128 82 150 96 Q158 120 150 138 Q128 148 106 138 Q98 116 104 92 Z" fill="{PAPIER}" {ST} stroke-width="2.2"/>'
        f'<path d="M108 122 Q128 134 148 122 L148 136 Q128 146 108 136 Z" fill="url(#pt)" stroke="none"/>'
        f'<path d="M112 108 L124 111 M134 111 L146 108" {ST} stroke-width="2.6"/>'
        f'<path d="M116 116 L122 117 M136 117 L142 116" {ST} stroke-width="1.6"/>'
        f'<path d="M128 114 L126 124 L131 125" fill="none" {ST} stroke-width="1.4"/>'
        f'<path d="M122 131 L136 131" {ST} stroke-width="1.6"/>'
        # casque à bord large, cabossé
        f'<path d="M96 98 Q100 62 128 60 Q156 62 160 98 Z" fill="url(#h2)" {ST} stroke-width="2.6"/>'
        f'<path d="M84 100 L172 96 L170 104 L86 108 Z" fill="{ENCRE}" {ST} stroke-width="1.6"/>'
        f'<path d="M140 66 L146 76 L152 70" fill="none" stroke="{PAPIER}" stroke-width="1.6"/>'
        '</g>'
        # galon de caporal : deux chevrons clairs sur la manche
        f'<path d="M84 186 L92 180 L100 186 M84 194 L92 188 L100 194" fill="none" stroke="{PAPIER}" stroke-width="2.4"/>'
        '</g>'
    )


def mort() -> str:
    """Le mort, affaissé sur un reste de fil : un cadavre mou dont seul le bras tendu est raide."""
    return (
        # piquets du reste de fil
        f'<path d="M40 405 L50 236" stroke="{ENCRE}" stroke-width="8" stroke-linecap="round"/>'
        f'<path d="M214 405 L206 300" stroke="{ENCRE}" stroke-width="6" stroke-linecap="round"/>'
        # jambes molles : genoux au sol, tibias qui traînent derrière, pieds tournés sur le côté
        f'<path d="M92 300 L104 372 L118 370 L110 302 Z" fill="url(#mol)" {ST} stroke-width="2.4"/>'
        f'<path d="M104 362 L62 392 L68 402 L114 378 Z" fill="url(#mol)" {ST} stroke-width="2.4"/>'
        f'<path d="M110 304 L130 380 L144 376 L126 300 Z" fill="url(#mol)" {ST} stroke-width="2.4"/>'
        f'<path d="M132 368 L92 398 L98 405 L142 384 Z" fill="url(#mol)" {ST} stroke-width="2.4"/>'
        f'<path d="M56 392 L48 404 L70 405 L72 396 Z M86 396 L80 405 L104 405 L102 398 Z" fill="{ENCRE}" {ST} stroke-width="1.6"/>'
        # buste qui pend en avant, plié sur le fil, la capote retombée
        f'<path d="M84 306 Q86 272 112 248 Q138 230 166 240 L172 262 Q150 268 138 290 L132 318 L104 322 Z" fill="url(#h2)" {ST} stroke-width="2.8"/>'
        # bras arrière qui pend tout droit, sans force
        f'<path d="M134 250 Q146 290 150 334 L138 336 Q132 296 122 260 Z" fill="url(#h2)" {ST} stroke-width="2.4"/>'
        f'<path d="M138 334 Q138 348 146 350 Q152 344 150 334 Z" fill="{PAPIER}" {ST} stroke-width="1.6"/>'
        # tête tombée sur la poitrine, plus bas que les épaules ; aucun visage lisible
        f'<path d="M160 258 Q180 252 188 270 Q190 290 176 298 Q160 300 154 286 Q150 268 160 258 Z" fill="url(#h2)" {ST} stroke-width="2.2"/>'
        # casque glissé vers l'avant, de travers
        f'<path d="M158 300 Q150 272 170 256 Q192 248 200 272 Z" fill="{LAVIS}" {ST} stroke-width="2.4"/>'
        f'<path d="M150 306 L206 270 L208 278 L156 312 Z" fill="{ENCRE}" {ST} stroke-width="1.4"/>'
        # plaque d'identité qui pend du cou (détail mort_plaque), sans inscription
        f'<path d="M156 270 L152 306" {ST} stroke-width="1.2"/>'
        f'<ellipse cx="151" cy="311" rx="4.4" ry="6" fill="{PAPIER}" {ST} stroke-width="1.6"/>'
        f'<path d="M150 308 L152 313" stroke="{MINE}" stroke-width="1.2"/>'
        # la fausse note : le bras tendu, droit et raide, vers la droite et vers le bas
        f'<path d="M146 228 L206 256 L200 270 L142 244 Z" fill="{PAPIER}" {ST} stroke-width="3"/>'
        f'<path d="M150 238 L200 262" stroke="{MINE}" stroke-width="1.4"/>'
        f'<path d="M202 252 L212 258 L210 268 L198 268 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>'
        f'<path d="M210 262 L218 268" {ST} stroke-width="2.2"/>'
        # le fil, par-dessus : un brin tendu sous la poitrine, deux brins retombés
        f'<path d="M50 252 Q110 250 170 262 Q192 270 206 304 M48 300 Q100 300 140 320 Q170 336 206 340 M46 356 Q110 360 210 384" fill="none" {ST} stroke-width="2.2"/>'
        + "".join(f'<path d="M{x - 4} {y - 4} L{x + 4} {y + 4} M{x + 4} {y - 4} L{x - 4} {y + 4}" {ST} stroke-width="1.4"/>'
                  for x, y in ((74, 251), (112, 252), (150, 258), (196, 284), (72, 300), (118, 309), (176, 337), (80, 357), (150, 370), (196, 380)))
    )


def planche(images: list[str]) -> str:
    corps = []
    for i, contenu in enumerate(images):
        tx = i * CADRE_L + 100 - CENTRE_X * ECHELLE
        ty = 316 - SOL * ECHELLE
        corps.append(f'<g transform="translate({tx:.2f} {ty:.2f}) scale({ECHELLE})">{contenu}</g>')
    n = len(images)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{CADRE_L * n}" height="{CADRE_H}" '
            f'viewBox="0 0 {CADRE_L * n} {CADRE_H}">{DEFS}{"".join(corps)}</svg>\n')


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    (DST / "chr_brisse_repos_01.svg").write_text(planche([brisse(i) for i in range(4)]), encoding="utf-8")
    (DST / "chr_mort_fige_01.svg").write_text(planche([mort()]), encoding="utf-8")
    print("2 planches dans art/src/chr")


if __name__ == "__main__":
    main()
