#!/usr/bin/env python3
"""Génère les gestes de Tobie de l'étape 5 (directive animation, balises de la Narrative).

Même format que tools/gen_chr_tobie.py : planches horizontales d'images de 200 x 320, Tobie tourné
vers la droite, pieds à (100, 316), trois calques synchronisés (chr_tobie_<geste>_01, le ruban
rouge chr_tobie_<geste>_01_red, la cendre chr_tobie-cendre_<geste>_01). Joués une fois à 10 i/s.
La croix est dans le décor, devant Tobie (à sa droite) : Gameplay le place à une main d'elle.

  entailler (6)  le couteau sorti de la poche, une encoche à hauteur d'œil, deux coups tirés
                 vers le bas ; la main arrière tient le bois (e5_sentier)
  graver    (6)  les lettres à hauteur de poitrine ; à l'image 4 la main recule d'un coup (le
                 pouce coupé : une goutte, seul rouge permis avec le ruban, sur le calque _red),
                 puis il reprend (e5_croix)
  accrocher (5)  la petite cloche de la crypte sortie de la poche, pendue au clou à hauteur
                 d'œil ; la main la lâche et redescend. La cloche reste au clou dans les deux
                 dernières images : ensuite c'est au décor de la montrer (comme l'entaille).

La cloche est l'insigne des coureurs, sans battant : elle ne sonne pas (garde-fou de l'étape 7).

Usage : python3 tools/gen_gestes_tobie_e5.py
"""
from __future__ import annotations

from gen_chr_tobie import (CENDRE, CHEVILLE_Y, DST, ENCRE, HANCHE, PAPIER, PLI, ROUGE, RUBAN, ST, bras,
                           buste, jambe, lanterne, membre, planche, sacoche, tete)
from gen_gestes_e1 import coude_ik

EPAULE_AV = (146.0, 118.0)
EPAULE_AR = (118.0, 122.0)
LAVIS = "#4A463D"


def couteau(x: float, y: float, ang: float) -> str:
    """Le couteau de poche de Tobie : manche de bois, lame courte (pointe vers ang degrés)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.0f})">'
            f'<path d="M-12 -3 L2 -3 L2 3 L-12 3 Z" fill="url(#h2)" {ST} stroke-width="1.6"/>'
            f'<path d="M2 -2.6 L18 -1 L20 0 L2 2.6 Z" fill="{PAPIER}" {ST} stroke-width="1.4"/></g>')


def cloche(x: float, y: float) -> str:
    """La petite cloche de bronze des coureurs, sans battant, pendue par son anneau en (x, y)."""
    return (f'<circle cx="{x:.1f}" cy="{y + 2:.1f}" r="2.4" fill="none" {ST} stroke-width="1.4"/>'
            f'<path d="M{x - 6:.1f} {y + 15:.1f} Q{x - 6:.1f} {y + 4:.1f} {x:.1f} {y + 4:.1f} Q{x + 6:.1f} {y + 4:.1f} {x + 6:.1f} {y + 15:.1f} '
            f'L{x + 8:.1f} {y + 17:.1f} H{x - 8:.1f} Z" fill="url(#h2)" {ST} stroke-width="1.5"/>'
            f'<path d="M{x - 5:.1f} {y + 15:.1f} H{x + 5:.1f}" stroke="{PAPIER}" stroke-width="1"/>')


def main_vers(epaule, main, fill: str, cote: int) -> str:
    """Un bras de Tobie dont la main va au point donné (coude calculé)."""
    coude = coude_ik(epaule, main, cote, 41)
    return (f'<path d="{membre(epaule, coude, 20, 17)}" fill="{fill}" {ST} stroke-width="2.4"/>'
            f'<path d="{membre(coude, main, 17, 14)}" fill="{fill}" {ST} stroke-width="2.4"/>'
            f'<circle cx="{coude[0]:.1f}" cy="{coude[1]:.1f}" r="7.6" fill="{fill}" stroke="none"/>')


def pose_geste(main_av, objet: str = "", main_ar=None, penche: float = 3.0, voute: float = 2.0,
               goutte=None) -> dict[str, str]:
    """Tobie debout, pieds écartés au repos ; la main avant au point main_av (repère de la planche
    de style), un objet tenu (déjà placé), la main arrière au repos ou au point main_ar."""
    hx, hy = HANCHE
    haut = f'<g transform="rotate({penche:.1f} {hx:.1f} {hy:.1f})">'
    arriere = (bras(EPAULE_AR, 2, avant=False) if main_ar is None else
               main_vers(EPAULE_AR, main_ar, "url(#h2)", 0)
               + f'<circle cx="{main_ar[0]:.1f}" cy="{main_ar[1]:.1f}" r="7" fill="{PAPIER}" {ST} stroke-width="1.9"/>')
    base = [jambe((hx - 6, hy), (hx - 12, CHEVILLE_Y), 0, sombre=True),
            haut, arriere, sacoche(0), buste(), '</g>',
            jambe((hx + 6, hy), (hx + 14, CHEVILLE_Y), 0),
            haut, lanterne(0), PLI,
            f'<g transform="translate({voute * .6:.1f} {voute:.1f})">', tete(), '</g>',
            main_vers(EPAULE_AV, main_av, PAPIER, 0), objet,
            f'<circle cx="{main_av[0]:.1f}" cy="{main_av[1]:.1f}" r="7" fill="{PAPIER}" {ST} stroke-width="1.9"/>',
            '</g>']
    # le ruban passe sous le bras avant quand la main est devant la poitrine : on le masque là
    coude = coude_ik(EPAULE_AV, main_av, 0, 41)
    cle = f"{main_av[0]:.0f}_{main_av[1]:.0f}"
    red = (f'<mask id="bras{cle}" maskUnits="userSpaceOnUse" x="0" y="0" width="240" height="420">'
           f'<rect width="240" height="420" fill="#fff"/>'
           f'<path d="{membre(EPAULE_AV, coude, 22, 19)}" fill="#000"/><path d="{membre(coude, main_av, 19, 16)}" fill="#000"/>'
           f'<circle cx="{coude[0]:.1f}" cy="{coude[1]:.1f}" r="9" fill="#000"/>'
           f'<circle cx="{main_av[0]:.1f}" cy="{main_av[1]:.1f}" r="8.4" fill="#000"/></mask>'
           f'<g mask="url(#bras{cle})">{RUBAN}</g>')
    if goutte is not None:
        gx, gy = goutte
        red += f'<path d="M{gx:.1f} {gy:.1f} q-2.4 4 0 6 q2.4 -2 0 -6 Z" fill="{ROUGE}"/>'
    return {"base": "".join(base),
            "red": f'{haut}{red}</g>',
            "cendre": f'{haut}<g transform="translate({voute * .6:.1f} {voute:.1f})">{CENDRE}</g></g>'}


def entailler() -> list[dict[str, str]]:
    """Le couteau sort de la poche, monte à hauteur d'œil ; deux encoches tirées vers le bas."""
    tenir = (198.0, 116.0)
    return [pose_geste((154, 236), couteau(154, 236, 90)),
            pose_geste((176, 150), couteau(176, 150, -20), main_ar=(184, 128)),
            pose_geste((198, 90), couteau(198, 90, -10), main_ar=tenir, penche=5),
            pose_geste((196, 102), couteau(196, 102, 20), main_ar=tenir, penche=6),
            pose_geste((198, 89), couteau(198, 89, -10), main_ar=tenir, penche=5),
            pose_geste((196, 104), couteau(196, 104, 24), main_ar=tenir, penche=6)]


def graver() -> list[dict[str, str]]:
    """Les lettres à hauteur de poitrine ; le pouce coupé à l'image 4 (la main recule), il finit."""
    tenir = (198.0, 132.0)
    return [pose_geste((176, 150), couteau(176, 150, -10), main_ar=(184, 130)),
            pose_geste((194, 150), couteau(194, 150, 10), main_ar=tenir, penche=6),
            pose_geste((192, 160), couteau(192, 160, 40), main_ar=tenir, penche=6),
            pose_geste((196, 152), couteau(196, 152, 0), main_ar=tenir, penche=6),
            pose_geste((172, 140), couteau(172, 140, -40), main_ar=(184, 120), penche=2, goutte=(172, 132)),
            pose_geste((194, 156), couteau(194, 156, 20), main_ar=tenir, penche=6, goutte=(196, 125))]


def accrocher() -> list[dict[str, str]]:
    """La cloche sortie de la poche, pendue au clou à hauteur d'œil, lâchée."""
    clou = (198.0, 88.0)
    return [pose_geste((154, 238), cloche(154, 232)),
            pose_geste((174, 160), cloche(174, 154), penche=3),
            pose_geste(clou, cloche(clou[0], clou[1] - 2), penche=5),
            pose_geste((182, 104), cloche(clou[0], clou[1] - 2), penche=4),
            pose_geste((166, 170), cloche(clou[0], clou[1] - 2), penche=3)]


GESTES = {"entailler": entailler, "graver": graver, "accrocher": accrocher}


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    for nom, fn in GESTES.items():
        poses = fn()
        (DST / f"chr_tobie_{nom}_01.svg").write_text(planche([p["base"] for p in poses]), encoding="utf-8")
        (DST / f"chr_tobie_{nom}_01_red.svg").write_text(planche([p["red"] for p in poses]), encoding="utf-8")
        (DST / f"chr_tobie-cendre_{nom}_01.svg").write_text(planche([p["cendre"] for p in poses]), encoding="utf-8")
    print(f"{len(GESTES) * 3} planches des gestes de Tobie (étape 5) dans art/src/chr")


if __name__ == "__main__":
    main()
