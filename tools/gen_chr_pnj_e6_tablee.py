#!/usr/bin/env python3
"""Génère les villageois de la tablée de l'étape 6 (e6_tablee) : quatre Enfouis assis à la table
servie, tournés de trois quarts vers la gauche comme Mathurin. Même repère que les PNJ (source
240 x 420, sol à y 405, centre x 120 ; images de 200 x 320, pieds en (100, 316)).

Ce sont des gens, pas des monstres : des visages humains, doux et fatigués (paupières lourdes,
cernes), la peau pâle (PEAU, gris foncé que l'écran inversé rend clair), les habits couleur de
terre (hachures et lavis). Écran inversé : les traits du visage sont en papier.

  femme     (chr_femme)     une femme d'âge mûr, le fichu noué derrière la nuque, un tablier ;
  mere      (chr_mere)      la mère, cheveux en chignon bas, un châle sur les épaules ;
  enfant    (chr_enfant)    son fils, sept ou huit ans, cheveux en épis, sur un tabouret bas ;
  fillette  (chr_fillette)  une petite fille, deux nattes, un tablier trop long.

Deux têtes de base (adulte, enfant) habillées chacune de deux coiffures. D'abord les poses de
repos (4 images de souffle), à montrer au GD avant les gestes. Aucun rouge.

Usage : python3 tools/gen_chr_pnj_e6_tablee.py
"""
from __future__ import annotations

from gen_chr_pnj_e2 import DST, LAVIS, MINE, PAPIER, ST, planche
from gen_chr_pnj_e6 import PEAU, SOUFFLE, TRAIT, g
from gen_gestes_e1 import bras

ENFANT = .74   # les enfants : tout le dessin réduit autour des pieds


def tete(cx: float, cy: float, coiffure: str, enfant: bool) -> str:
    """Une tête de trois quarts vers la gauche ; enfant : plus ronde, les yeux plus grands et plus
    bas. Les yeux sont mi-clos (la paupière tombe), un cerne dessous ; la bouche au repos."""
    rx, ry = (17, 19) if enfant else (16, 21)
    o = [f'<path d="M{cx - 6} {cy + ry - 6} L{cx + 8} {cy + ry - 6} L{cx + 8} {cy + ry + 14} L{cx - 6} {cy + ry + 14} Z" fill="{PEAU}" {ST} stroke-width="1.8"/>']
    # derrière la tête : le chignon, les nattes, le nœud du fichu
    if coiffure == "chignon":
        o.append(f'<ellipse cx="{cx + 15}" cy="{cy + 8}" rx="9" ry="8" fill="url(#h2)" {ST} stroke-width="1.8"/>')
    elif coiffure == "nattes":
        o.append(f'<path d="M{cx + 12} {cy + 2} Q{cx + 22} {cy + 20} {cx + 18} {cy + 40}" fill="none" {ST} stroke-width="6"/>'
                 f'<path d="M{cx + 12} {cy + 2} Q{cx + 22} {cy + 20} {cx + 18} {cy + 40}" fill="none" stroke="{MINE}" stroke-width="3" stroke-dasharray="3 3"/>'
                 f'<path d="M{cx + 15} {cy + 40} l6 4 l1 -6 Z" fill="{LAVIS}" {ST} stroke-width="1.2"/>')
    elif coiffure == "fichu":
        o.append(f'<path d="M{cx + 14} {cy - 2} L{cx + 26} {cy + 6} L{cx + 20} {cy + 10} L{cx + 28} {cy + 22} L{cx + 16} {cy + 12} Z" fill="{LAVIS}" {ST} stroke-width="1.6"/>')
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{PEAU}" {ST} stroke-width="2.2"/>')
    o.append(f'<path d="M{cx + 14} {cy - 2} Q{cx + 21} {cy - 4} {cx + 20} {cy + 4} Q{cx + 19} {cy + 10} {cx + 14} {cy + 9}" fill="{PEAU}" {ST} stroke-width="1.6"/>')
    # les cheveux
    if coiffure == "chignon":
        o.append(f'<path d="M{cx - 17} {cy - 2} Q{cx - 18} {cy - 24} {cx} {cy - 23} Q{cx + 18} {cy - 22} {cx + 17} {cy} '
                 f'Q{cx + 10} {cy - 10} {cx - 2} {cy - 13} Q{cx - 12} {cy - 11} {cx - 17} {cy - 2} Z" fill="url(#h2)" {ST} stroke-width="1.8"/>')
    elif coiffure == "fichu":
        o.append(f'<path d="M{cx - 19} {cy + 2} Q{cx - 22} {cy - 26} {cx} {cy - 26} Q{cx + 20} {cy - 26} {cx + 19} {cy + 2} '
                 f'Q{cx + 12} {cy - 10} {cx} {cy - 12} Q{cx - 12} {cy - 10} {cx - 19} {cy + 2} Z" fill="{LAVIS}" {ST} stroke-width="2"/>'
                 f'<path d="M{cx - 12} {cy - 20} Q{cx} {cy - 24} {cx + 12} {cy - 20}" fill="none" stroke="{MINE}" stroke-width="1.2"/>')
    elif coiffure == "epis":
        o.append(f'<path d="M{cx - 17} {cy - 1} Q{cx - 19} {cy - 22} {cx} {cy - 21} Q{cx + 19} {cy - 21} {cx + 17} {cy} '
                 f'Q{cx + 13} {cy - 9} {cx + 8} {cy - 10} L{cx + 10} {cy - 17} L{cx + 3} {cy - 12} L{cx + 1} {cy - 21} '
                 f'L{cx - 4} {cy - 11} L{cx - 10} {cy - 18} L{cx - 10} {cy - 9} Q{cx - 15} {cy - 7} {cx - 17} {cy - 1} Z" fill="url(#h2)" {ST} stroke-width="1.8"/>')
    else:  # nattes : la raie au milieu, les cheveux tirés
        o.append(f'<path d="M{cx - 17} {cy} Q{cx - 19} {cy - 21} {cx} {cy - 20} Q{cx + 19} {cy - 21} {cx + 17} {cy + 1} '
                 f'Q{cx + 8} {cy - 12} {cx - 2} {cy - 12} Q{cx - 12} {cy - 10} {cx - 17} {cy} Z" fill="url(#h2)" {ST} stroke-width="1.8"/>'
                 f'<path d="M{cx - 1} {cy - 20} Q{cx - 3} {cy - 15} {cx - 2} {cy - 12}" fill="none" stroke="{PAPIER}" stroke-width="1.4"/>')
    # le visage : yeux mi-clos, cernes, nez, bouche au repos
    ey = cy + (3 if enfant else 0)
    ry_oeil = 3.2 if enfant else 2.6
    for x in (cx - 10, cx + 2):
        o.append(f'<ellipse cx="{x}" cy="{ey + .8}" rx="{ry_oeil}" ry="{ry_oeil * .8:.1f}" fill="{TRAIT}"/>'
                 f'<path d="M{x - 4} {ey - .6} Q{x} {ey - 2.6} {x + 4} {ey - .6}" fill="none" stroke="{TRAIT}" stroke-width="1.8"/>')
        if not enfant:
            o.append(f'<path d="M{x - 3} {ey + 5} Q{x} {ey + 6.5} {x + 3} {ey + 5}" fill="none" stroke="{TRAIT}" stroke-width=".9"/>')
    o.append(f'<path d="M{cx - 14} {ey - 7} Q{cx - 10} {ey - 9} {cx - 6} {ey - 7} M{cx - 1} {ey - 7} Q{cx + 3} {ey - 9} {cx + 7} {ey - 7}" fill="none" stroke="{TRAIT}" stroke-width="1.3"/>'
             f'<path d="M{cx - 5} {ey + 2} L{cx - 7} {ey + 9} L{cx - 4} {ey + 10}" fill="none" stroke="{TRAIT}" stroke-width="1.2"/>'
             f'<path d="M{cx - 9} {ey + 15} Q{cx - 4} {ey + 16} {cx + 1} {ey + 15}" fill="none" stroke="{TRAIT}" stroke-width="1.5"/>')
    return "".join(o)


def assis(i: int, coiffure: str, enfant: bool = False, chale: bool = False, tablier: bool = False,
          jupe: bool = True, phase: int = 0, penche: float = 0.0, croisees: bool = False,
          main: tuple[float, float] | None = None, objet: str = "") -> str:
    """Assis sur un tabouret, de trois quarts vers la gauche, les mains posées sur les genoux.
    phase décale le souffle (ils ne respirent pas ensemble) ; penche incline le buste vers la
    gauche autour des hanches (degrés ; négatif : il se redresse, raide) ; croisees : les mains
    croisées sur le giron. Un buste penché laisse glisser le châle de l'épaule basse.
    main : la main droite quitte le giron et va en (x, y), avec objet : cuillere, pain, ouverte
    (elle fait signe) ou pince (elle tient une manche, hors du cadre à gauche)."""
    s = SOUFFLE[(i + phase) % 4]
    o = [  # le tabouret
        f'<path d="M108 318 H176 V328 H108 Z" fill="url(#h1)" {ST} stroke-width="2.2"/>',
        f'<path d="M114 328 L106 405 M170 328 L178 405 M142 328 V398 M110 372 H174" fill="none" {ST} stroke-width="3"/>']
    if jupe:  # la jupe longue, plis sur les genoux, les sabots dessous
        o += [f'<path d="M160 316 L100 300 Q82 302 80 326 L72 394 L128 396 L120 334 L150 336 Z" fill="url(#h2)" {ST} stroke-width="2.2"/>',
              f'<path d="M94 312 L88 392 M106 330 L104 394" fill="none" stroke="{PAPIER}" stroke-width="1.6"/>',
              f'<path d="M74 392 L70 405 L100 405 L98 392 Z M104 392 L102 405 L128 405 L124 392 Z" fill="{LAVIS}" {ST} stroke-width="1.6"/>']
    else:  # culotte courte, mollets nus, galoches
        o += [f'<path d="M150 316 L88 304 L84 326 L132 336 Z" fill="url(#h2)" {ST} stroke-width="2.2"/>',
              f'<path d="M88 324 L84 392 L98 392 L102 328 Z M112 330 L110 392 L124 392 L124 334 Z" fill="{PEAU}" {ST} stroke-width="1.8"/>',
              f'<path d="M78 390 L74 405 L102 405 L98 390 Z M106 390 L104 405 L130 405 L126 390 Z" fill="{LAVIS}" {ST} stroke-width="1.6"/>']
    o.append(f'<g transform="translate(0 {s * .5:.1f}) rotate({-penche:.1f} 132 316)">')
    # le buste droit, un peu las ; un corsage boutonné
    o.append(f'<path d="M120 208 Q146 198 162 214 Q170 262 160 318 L104 318 Q102 264 120 208 Z" fill="url(#h1)" {ST} stroke-width="2.4"/>')
    o.append(f'<path d="M126 214 Q132 260 128 316" fill="none" {ST} stroke-width="1.4"/>'
             + "".join(f'<circle cx="{128 + (y - 230) * .02:.1f}" cy="{y}" r="1.8" fill="{PAPIER}" {ST} stroke-width=".9"/>' for y in (232, 252, 272)))
    if tablier:
        o.append(f'<path d="M106 270 L142 268 L140 300 Q120 312 96 308 L84 300 Q96 286 106 270 Z" fill="{PAPIER}" {ST} stroke-width="2"/>'
                 f'<path d="M100 296 Q118 302 136 296" fill="none" stroke="{MINE}" stroke-width="1.1"/>')
    # le bras gauche (au fond), l'avant-bras sur la cuisse
    o.append(f'<path d="M160 222 Q168 262 148 290 L136 282 Q152 258 144 228 Z" fill="url(#h1)" {ST} stroke-width="2.2"/>')
    if chale and penche:
        # l'épaule avant plus basse : le châle a glissé, il pend de ce côté jusqu'au giron
        o.append(f'<path d="M116 216 Q140 198 166 216 L168 246 L150 232 L132 262 L116 290 L102 284 L108 246 Z" fill="{LAVIS}" {ST} stroke-width="2"/>'
                 + "".join(f'<path d="M{x} {y} l-1 7" stroke="{MINE}" stroke-width="1"/>' for x, y in ((104, 286), (112, 290), (134, 258), (150, 236), (160, 242))))
    elif chale:
        o.append(f'<path d="M114 212 Q140 196 166 216 L170 256 L150 236 L136 270 L124 236 L108 250 Z" fill="{LAVIS}" {ST} stroke-width="2"/>'
                 + "".join(f'<path d="M{x} {y} l-1 7" stroke="{MINE}" stroke-width="1"/>' for x, y in ((140, 266), (146, 254), (154, 244), (128, 252), (118, 246))))
    if main is not None:
        o.append(g(bras_geste(main, objet)))
        if croisees:  # la main gauche reste seule sur le giron
            o.append(g(f'<ellipse cx="126" cy="293" rx="9" ry="6" fill="{PEAU}" stroke-width="1.8"/>'))
    elif croisees:
        # les mains croisées sur le giron, serrées : le bras droit plié, coude au corps
        o.append(g(bras((128, 216), (118, 262), (118, 292), "url(#h1)", 15, 13, 11, 2.2)
                   + f'<ellipse cx="128" cy="292" rx="9" ry="6" fill="{PEAU}" stroke-width="1.8"/>'
                   + f'<ellipse cx="116" cy="295" rx="9" ry="6.5" fill="{PEAU}" stroke-width="1.8"/>'
                   + '<path d="M110 297 l10 -1 M110 300 l9 -1" stroke-width=".8"/>'))
    else:
        # le bras droit, la main posée sur le genou
        o.append(g(bras((128, 216), (112, 260), (96, 296), "url(#h1)", 15, 13, 11, 2.2)
                   + f'<ellipse cx="94" cy="298" rx="9" ry="6.5" fill="{PEAU}" stroke-width="1.8"/>'
                   + '<path d="M88 300 l10 -1 M88 303 l9 -1" stroke-width=".8"/>'))
    # les enfants ont la tête plus grosse pour leur corps
    t = tete(122, 172, coiffure, enfant)
    o.append(f'<g transform="translate(122 206) scale(1.28) translate(-122 -206)">{t}</g>' if enfant else t)
    o.append('</g>')
    corps = "".join(o)
    if enfant:
        return f'<g transform="translate(120 405) scale({ENFANT}) translate(-120 -405)">{corps}</g>'
    return corps


def bras_geste(main: tuple[float, float], objet: str) -> str:
    """Le bras droit, de l'épaule à la main en (x, y), le coude qui tombe naturellement ; la main
    et ce qu'elle tient."""
    x, y = main
    coude = ((128 + x) / 2 + 12, max((216 + y) / 2 + 16, y - 10))
    o = [bras((128, 216), coude, main, "url(#h1)", 15, 13, 11, 2.2)]
    if objet == "cuillere":  # le manche dans le poing, le cuilleron vers la bouche
        o.append(f'<path d="M{x + 4} {y + 4} L{x - 12} {y - 10}" stroke-width="2.6"/>'
                 f'<ellipse cx="{x - 14}" cy="{y - 12}" rx="5" ry="3.4" transform="rotate(-40 {x - 14} {y - 12})" fill="{LAVIS}" stroke-width="1.4"/>'
                 f'<ellipse cx="{x}" cy="{y}" rx="7" ry="6.5" fill="{PEAU}" stroke-width="1.8"/>')
    elif objet == "pain":  # un gros quignon, croûte hachurée, serré dans la main
        o.append(f'<g transform="translate({x} {y}) scale(1.8)">'
                 '<path d="M-12 0 Q-11 -11 1 -10 Q12 -7 9 3 Q0 9 -12 0 Z" fill="url(#h1)" stroke-width="1.2"/>'
                 '<path d="M-7 -6 l3 3 M0 -8 l3 3 M5 -6 l2 3" stroke-width=".8"/></g>'
                 f'<ellipse cx="{x + 4}" cy="{y + 4}" rx="7" ry="6" fill="{PEAU}" stroke-width="1.8"/>')
    elif objet == "ouverte":  # la paume levée, les doigts ouverts
        o.append(f'<path d="M{x - 6} {y + 4} Q{x - 10} {y - 8} {x - 6} {y - 18} L{x - 1} {y - 16} L{x} {y - 8} L{x + 3} {y - 21} L{x + 8} {y - 19} '
                 f'L{x + 7} {y - 7} L{x + 12} {y - 15} L{x + 16} {y - 12} Q{x + 12} {y + 4} {x + 2} {y + 6} Z" fill="{PEAU}" stroke-width="1.8"/>')
    elif objet == "pince":  # deux doigts qui serrent un pli d'étoffe, au bord gauche du cadre
        o.append(f'<path d="M{x - 18} {y - 8} Q{x - 10} {y - 4} {x - 18} {y + 8}" fill="none" stroke="{MINE}" stroke-width="2.4"/>'
                 f'<path d="M{x - 8} {y - 6} L{x - 16} {y - 4} L{x - 16} {y + 2} L{x - 6} {y + 4} Q{x + 6} {y + 6} {x + 6} {y - 2} Q{x + 4} {y - 8} {x - 8} {y - 6} Z" fill="{PEAU}" stroke-width="1.8"/>')
    else:
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="7" ry="6.5" fill="{PEAU}" stroke-width="1.8"/>')
    return "".join(o)


# les trajets de la main droite, image par image (le souffle continue)
CUILLERE = ((100, 284), (106, 250), (122, 204), (124, 198), (112, 240), (100, 284))
CUILLERE_ENFANT = ((100, 284), (106, 248), (120, 206), (122, 200), (110, 242), (100, 284))
SIGNE = ((100, 270), (92, 222), (84, 196), (96, 192), (84, 196), (96, 230))
PAIN = ((96, 290), (60, 262), (40, 250), (52, 258), (112, 286), (150, 300))
MANCHE = ((96, 290), (70, 270), (46, 258), (40, 256), (40, 256), (42, 257))


def geste(trajet, objets, **perso) -> list[str]:
    return [assis(i % 4, main=m, objet=o, **perso) for i, (m, o) in enumerate(zip(trajet, objets))]


FEMME = dict(coiffure="fichu", tablier=True, penche=-3, croisees=True)
MERE = dict(coiffure="chignon", chale=True, phase=1, penche=9)
ENFANT_ = dict(coiffure="epis", enfant=True, jupe=False, phase=2)
FILLETTE = dict(coiffure="nattes", enfant=True, tablier=True, phase=3)
C6 = ["cuillere"] * 6

PLANCHES = {
    "chr_femme_repos_01": lambda: [assis(i, "fichu", tablier=True, penche=-3, croisees=True) for i in range(4)],
    "chr_mere_repos_01": lambda: [assis(i, "chignon", chale=True, phase=1, penche=9) for i in range(4)],
    "chr_enfant_repos_01": lambda: [assis(i, "epis", enfant=True, jupe=False, phase=2) for i in range(4)],
    "chr_fillette_repos_01": lambda: [assis(i, "nattes", enfant=True, tablier=True, phase=3) for i in range(4)],
    "chr_femme_lever-cuillere_01": lambda: geste(CUILLERE, C6, **FEMME),
    "chr_mere_lever-cuillere_01": lambda: geste(CUILLERE, C6, **MERE),
    "chr_enfant_lever-cuillere_01": lambda: geste(CUILLERE_ENFANT, C6, **ENFANT_),
    "chr_fillette_lever-cuillere_01": lambda: geste(CUILLERE_ENFANT, C6, **FILLETTE),
    "chr_femme_faire-signe_01": lambda: geste(SIGNE, ["", "ouverte", "ouverte", "ouverte", "ouverte", "ouverte"], **FEMME),
    "chr_enfant_voler-pain_01": lambda: geste(PAIN, ["", "", "", "pain", "pain", "pain"], **ENFANT_),
    "chr_fillette_tenir-manche_01": lambda: geste(MANCHE, ["", "", "", "pince", "pince", "pince"], **FILLETTE),
}


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    for nom, fn in PLANCHES.items():
        (DST / f"{nom}.svg").write_text(planche(fn()), encoding="utf-8")
    print(f"{len(PLANCHES)} planches de la tablée dans art/src/chr")


if __name__ == "__main__":
    main()
