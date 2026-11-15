#!/usr/bin/env python3
"""Génère les personnages de l'étape 2 : le caporal Brisse et le mort qui montre le chemin.

Même repère que la planche n° 2 (240 x 420, sol à y 405), même échelle que Tobie (0,845) :
images de 200 x 320, sol à y 316, centre à x 100.

  chr_brisse_repos_01 : 4 images ; la flamme de sa bougie vacille, son souffle est lent.
                        Forme : l'arc, un dos rond penché sur une flamme qu'il protège.
  chr_mort_fige_01    : 1 image ; figé dans un reste de fil, le bras tendu vers la droite
                        et un peu vers le bas. Forme : la flèche. Plaque d'identité au cou.

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
    """Le mort, de profil, figé dans un reste de fil, le bras tendu vers la droite et vers le bas."""
    return (
        # piquets et fil où il est pris (le fil passe devant le corps)
        f'<path d="M40 405 L52 230" stroke="{ENCRE}" stroke-width="8" stroke-linecap="round"/>'
        # jambes fléchies, un genou au sol
        f'<path d="M96 300 L74 352 L92 404 L112 404 L96 356 L116 306 Z" fill="url(#mol)" {ST} stroke-width="2.4"/>'
        f'<path d="M124 300 L150 350 L132 392 L150 398 L172 352 L144 296 Z" fill="url(#mol)" {ST} stroke-width="2.4"/>'
        f'<path d="M88 396 L84 405 L118 405 L114 396 Z M128 388 L124 404 L156 404 L154 394 Z" fill="{ENCRE}" {ST} stroke-width="1.6"/>'
        # buste penché en avant (la flèche), capote raidie
        f'<path d="M86 300 Q84 236 112 180 Q140 150 176 160 L184 176 Q158 196 150 240 L148 306 L120 314 Z" fill="url(#h2)" {ST} stroke-width="2.8"/>'
        # bras arrière qui pend, accroché au fil
        f'<path d="M118 200 Q96 240 94 272 L108 276 Q114 244 132 214 Z" fill="url(#h2)" {ST} stroke-width="2.4"/>'
        # le bras tendu : la flèche, vers la droite et un peu vers le bas
        f'<path d="M160 176 L204 202 L200 214 L154 196 Z" fill="url(#h1)" {ST} stroke-width="2.4"/>'
        f'<path d="M200 198 L212 206 L210 212 L202 216 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>'
        f'<path d="M210 208 L216 212" {ST} stroke-width="2"/>'
        # tête penchée, casque glissé ; aucun visage lisible : une ombre en contre-hachure
        f'<path d="M168 128 Q190 122 200 140 Q204 160 190 172 Q172 176 164 160 Q160 142 168 128 Z" fill="url(#h2)" {ST} stroke-width="2.2"/>'
        f'<path d="M156 136 Q164 104 192 106 Q214 112 214 138 Z" fill="{LAVIS}" {ST} stroke-width="2.4"/>'
        f'<path d="M150 140 L218 132 L216 140 L152 148 Z" fill="{ENCRE}" {ST} stroke-width="1.4"/>'
        # plaque d'identité au cou, rongée (détail mort_plaque) : petit ovale clair, sans inscription
        f'<path d="M176 170 L180 182" {ST} stroke-width="1.2"/>'
        f'<ellipse cx="181" cy="188" rx="6" ry="4.4" fill="{PAPIER}" {ST} stroke-width="1.6"/>'
        f'<path d="M178 187 L183 189" stroke="{MINE}" stroke-width="1.2"/>'
        # le fil, par-dessus : trois brins, nœuds en X
        f'<path d="M52 250 Q120 236 180 268 M50 300 Q110 286 200 330 M48 350 Q120 342 210 380" fill="none" {ST} stroke-width="2.2"/>'
        + "".join(f'<path d="M{x - 4} {y - 4} L{x + 4} {y + 4} M{x + 4} {y - 4} L{x - 4} {y + 4}" {ST} stroke-width="1.4"/>'
                  for x, y in ((80, 244), (118, 246), (152, 256), (84, 293), (126, 298), (166, 314), (90, 346), (140, 352), (186, 368)))
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
