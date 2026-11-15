#!/usr/bin/env python3
"""Génère les gestes de l'étape 3 (directive animation, balises de la Narrative #139).

Même format que tools/gen_gestes_e1.py : chr_<perso>_<geste>_01, images de 200 x 320, pieds à
(100, 316), jouées une fois à 10 i/s puis retour au repos. Les dessins viennent de
tools/gen_chr_pnj_e3.py, dont les fonctions prennent les réglages du geste en paramètres.

  enfants : viser (« Pan ! » : le fusil de bâton se relève d'un coup, le grand recule d'un pas),
            hausser-epaules (les deux épaules montent, le bâton s'abaisse)
  ilde    : regarder-sacoche (la tête penche vers la cire noire, une seconde de trop),
            tendre (le pain blanc, tiré du tablier)
  rose    : danser (un tour lent : tout le corps se balance autour des pieds, le voile suit)
  sonneur : tirer-corde (un grand coup sur la corde attachée à rien : aucune cloche ne sonne),
            serrer (le pain contre lui ; finit serré : à tenir avec [#tenir])

Aucun rouge à l'étape 3.

Usage : python3 tools/gen_gestes_e3.py
"""
from __future__ import annotations

from gen_chr_pnj_e2 import DST, PAPIER, ST, planche
from gen_chr_pnj_e3 import enfants, ilde, rose, sonneur
from gen_gestes_e1 import bras, main_ouverte


def pain(x: float, y: float, s: float = 1.0) -> str:
    """Une miche de pain blanc : ovale de papier, trois grignes."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s})">'
            f'<ellipse cx="0" cy="0" rx="17" ry="11" fill="{PAPIER}" {ST} stroke-width="2"/>'
            f'<path d="M-9 -4 L-4 4 M-1 -6 L4 3 M7 -5 L11 2" {ST} stroke-width="1.4"/></g>')


def g(dessin: str) -> str:
    return f'<g {ST}>{dessin}</g>'


def enfants_viser() -> list[str]:
    return [enfants(0, recul=r) for r in (0, 12, 18, 8, 3, 0)]


def enfants_hausser_epaules() -> list[str]:
    return [enfants(0, hausse=h) for h in (0, 4, 8, 8, 4, 0)]


def ilde_regarder_sacoche() -> list[str]:
    return [ilde(0, tete=t) for t in (0, 6, 12, 12, 12, 4)]


I_EPAULE = (88.0, 184.0)
I_MAIN_DROITE = f'<path d="M128 228 Q146 224 148 236 Q142 246 128 244 Z" fill="{PAPIER}" stroke-width="1.8"/>'


def bras_ilde(coude, main) -> str:
    return bras(I_EPAULE, coude, main, "url(#h2)", 20, 18, 15, 2.2)


def ilde_tendre() -> list[str]:
    """« Assieds-toi. Tiens. » : elle décroise les bras et tend le pain blanc."""
    return [ilde(0),
            ilde(0, bras=g(I_MAIN_DROITE + bras_ilde((80, 226), (108, 214)) + pain(114, 204) + '<circle cx="108" cy="214" r="8" fill="#E8E5DA" stroke-width="1.8"/>')),
            ilde(1, bras=g(I_MAIN_DROITE + bras_ilde((70, 220), (46, 208)) + pain(38, 198) + '<circle cx="46" cy="208" r="8" fill="#E8E5DA" stroke-width="1.8"/>')),
            ilde(2, bras=g(I_MAIN_DROITE + bras_ilde((70, 218), (42, 206)) + pain(34, 196) + '<circle cx="42" cy="206" r="8" fill="#E8E5DA" stroke-width="1.8"/>')),
            ilde(1, bras=g(I_MAIN_DROITE + bras_ilde((70, 218), (44, 208)) + main_ouverte(40, 208, -90, .9))),
            ilde(0)]


def rose_danser() -> list[str]:
    return [rose(0, pivot=p, vent=v) for p, v in ((0, 0), (6, -4), (10, -8), (3, -2), (-7, 7), (-3, 3))]


def sonneur_tirer_corde() -> list[str]:
    return [sonneur(0, tire=t) for t in (0, 16, 30, 38, 20, 6)]


S_EPAULE_G, S_EPAULE_D = (100.0, 178.0), (138.0, 174.0)


def bras_sonneur(serre: float, pain_present: bool = True) -> str:
    """Les deux bras ramenés sur la poitrine, le pain dessous ; serre = les mains se rejoignent."""
    mg = (114 + serre, 214 - serre * .4)
    md = (136 - serre, 212 - serre * .4)
    out = [bras(S_EPAULE_G, (92, 204), mg, "url(#h1)", 16, 14, 12, 2.2),
           bras(S_EPAULE_D, (150, 198), md, "url(#h1)", 16, 14, 12, 2.2)]
    if pain_present:
        out.insert(0, pain(125, 214, 1 - serre * .02))
    out += [f'<ellipse cx="{mg[0]:.1f}" cy="{mg[1]:.1f}" rx="8" ry="7" fill="{PAPIER}" stroke-width="1.8"/>',
            f'<ellipse cx="{md[0]:.1f}" cy="{md[1]:.1f}" rx="8" ry="7" fill="{PAPIER}" stroke-width="1.8"/>']
    return g("".join(out))


def sonneur_serrer() -> list[str]:
    """Il lâche la corde et serre le pain d'Ilde contre lui, de plus en plus fort."""
    mi = g(bras(S_EPAULE_G, (96, 186), (122, 184), "url(#h1)", 16, 14, 12, 2.2)
           + bras(S_EPAULE_D, (152, 178), (140, 186), "url(#h1)", 16, 14, 12, 2.2)
           + pain(130, 196) + f'<ellipse cx="122" cy="184" rx="8" ry="7" fill="{PAPIER}" stroke-width="1.8"/>'
           + f'<ellipse cx="140" cy="186" rx="8" ry="7" fill="{PAPIER}" stroke-width="1.8"/>')
    return [sonneur(0),
            sonneur(0, tire=0, bras=mi),
            sonneur(0, tire=0, bras=bras_sonneur(0)),
            sonneur(0, tire=0, bras=bras_sonneur(4)),
            sonneur(0, tire=0, bras=bras_sonneur(6)),
            sonneur(0, tire=0, bras=bras_sonneur(6))]


GESTES = {
    "enfants_viser": enfants_viser, "enfants_hausser-epaules": enfants_hausser_epaules,
    "ilde_regarder-sacoche": ilde_regarder_sacoche, "ilde_tendre": ilde_tendre,
    "rose_danser": rose_danser,
    "sonneur_tirer-corde": sonneur_tirer_corde, "sonneur_serrer": sonneur_serrer,
}


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    for nom, fn in GESTES.items():
        (DST / f"chr_{nom}_01.svg").write_text(planche(fn()), encoding="utf-8")
    print(f"{len(GESTES)} gestes de l'étape 3 dans art/src/chr")


if __name__ == "__main__":
    main()
