#!/usr/bin/env python3
"""Génère la cinématique e3_procession_nuit : depuis la chambre, entre les lames du volet, la
procession passe dans la rue noire, cierges à deux mains, Ilde en tête.

Trois calques, à composer dans le moteur (directive animation : décors et sprites existants) :

  cin_procession-nuit_01   la rue, 1920 x 1080, opaque : façades d'en face en silhouette, chaussée.
                           Sol de la procession à y 820 (pieds des sprites).
  cin_procession-nuit_02   le volet vu de la chambre, 1920 x 1080, au premier plan : lames
                           horizontales, jours TRANSPARENTS entre elles (40 px, l'un centré sur les
                           flammes des cierges, à y 577), mur de la chambre
                           autour. Les sprites passent entre les deux calques.
  chr_ilde-cierge_marche_01  Ilde en tête, 4 images de 200 x 320 qui marchent vers la droite :
                           on la reconnaît à sa silhouette (robe en cloche ronde, tablier blanc,
                           coiffe nouée claire) et pas à son visage, qui reste dans le noir.

Derrière elle, la file : chr_procession_marche_01, déphasés. Échelle conseillée des sprites : 1,3.
Tout est déjà peint de nuit (noir de gravure, flammes en réserve de papier) : pendant la
cinématique, utiliser la teinte du chemin de nuit (0.85, 0.88, 1.0), pas celle de la chambre.

Usage : python3 tools/gen_cin_e3.py
"""
from __future__ import annotations

from gen_chr_pnj_e2 import planche
from gen_chr_pnj_e3 import flamme
from gen_cin_epilogues import DEFS_CIN
from gen_decors_e1_surface import ENCRE, LAVIS, MINE, PAPIER, rnd

ROOT_CIN = "art/src/cin"
W, H = 1920, 1080
ST = f'stroke="{ENCRE}" stroke-linejoin="round" stroke-linecap="round"'
SOL_RUE = 820
FENETRE = (360, 130, 1560, 950)       # embrasure du volet
LAME, JOUR = 56, 40
# un jour centré sur les flammes des cierges (sprites à l'échelle 1,3, pieds à SOL_RUE)
FLAMME_Y = SOL_RUE - 243
PREMIERE_LAME = FLAMME_Y - JOUR // 2 - LAME - 4 * (LAME + JOUR)


def svg(contenu: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'{DEFS_CIN}{contenu}</svg>\n')


def rue() -> str:
    """La rue noire : ciel en hachure sur lavis, façades en aplat d'encre, chaussée à peine plus claire."""
    r = rnd(303)
    out = [f'<rect width="{W}" height="{H}" fill="{LAVIS}"/>',
           f'<rect width="{W}" height="{H}" fill="url(#v1)"/>']
    # façades d'en face : toits, une fenêtre éteinte, une porte fermée ; aucune lumière chez personne
    x = -40
    while x < W:
        lg = r.randint(260, 420)
        haut = r.randint(240, 360)
        faite = haut - r.randint(90, 150)
        out.append(f'<path d="M{x} {SOL_RUE - 40} V{haut} L{x + lg / 2:.0f} {faite} L{x + lg} {haut} V{SOL_RUE - 40} Z" fill="{ENCRE}"/>')
        out.append(f'<path d="M{x} {haut} L{x + lg / 2:.0f} {faite} L{x + lg} {haut}" fill="none" stroke="{MINE}" stroke-width="2"/>')
        fx = x + r.randint(40, lg - 120)
        out.append(f'<rect x="{fx}" y="{haut + 80}" width="70" height="90" fill="none" stroke="{LAVIS}" stroke-width="3"/>'
                   f'<path d="M{fx + 35} {haut + 80} V{haut + 170} M{fx} {haut + 125} H{fx + 70}" stroke="{LAVIS}" stroke-width="2"/>')
        x += lg + r.randint(10, 40)
    # chaussée : contre-hachure, un filet de mine pour le bord du pavé
    out.append(f'<rect y="{SOL_RUE - 40}" width="{W}" height="{H - SOL_RUE + 40}" fill="{LAVIS}"/>')
    out.append(f'<rect y="{SOL_RUE - 40}" width="{W}" height="{H - SOL_RUE + 40}" fill="url(#v2)"/>')
    out.append(f'<path d="M0 {SOL_RUE + 6} H{W}" stroke="{MINE}" stroke-width="2.4" stroke-dasharray="70 26"/>')
    for k in range(40):
        px, py = r.uniform(0, W), r.uniform(SOL_RUE + 30, H)
        out.append(f'<path d="M{px:.0f} {py:.0f} q14 -4 28 0" fill="none" stroke="{MINE}" stroke-width="1.4"/>')
    return "".join(out)


def volet() -> str:
    """Le mur de la chambre et le volet fermé : lames de bois, jours transparents entre elles."""
    x0, y0, x1, y1 = FENETRE
    jours = "".join(f'<rect x="{x0 + 30}" y="{max(y, y0 + 40):.0f}" width="{x1 - x0 - 60}" height="{min(y + JOUR, y1 - 40) - max(y, y0 + 40):.0f}" fill="#000"/>'
                    for y in range(PREMIERE_LAME + LAME, y1 - 40, LAME + JOUR) if y + JOUR > y0 + 40 and y < y1 - 40)
    out = [f'<mask id="jours" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
           f'<rect width="{W}" height="{H}" fill="#fff"/>{jours}</mask>',
           f'<g mask="url(#jours)">',
           # mur de la chambre, nuit : lavis et contre-hachure
           f'<rect width="{W}" height="{H}" fill="{LAVIS}"/><rect width="{W}" height="{H}" fill="url(#v2)"/>',
           # embrasure : l'épaisseur du mur, un filet de mine
           f'<path d="M{x0 - 40} {y0 - 40} H{x1 + 40} V{y1 + 40} H{x0 - 40} Z M{x0} {y0} V{y1} H{x1} V{y0} Z" fill="{ENCRE}" fill-rule="evenodd"/>',
           f'<rect x="{x0 - 40}" y="{y0 - 40}" width="{x1 - x0 + 80}" height="{y1 - y0 + 80}" fill="none" stroke="{MINE}" stroke-width="2"/>',
           # le cadre du volet
           f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{LAVIS}" {ST} stroke-width="4"/>',
           f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#h3)" opacity=".9"/>']
    # les lames : bois, veines, quelques clous ; le haut de chaque lame a un filet clair
    r = rnd(311)
    out.append(f'<clipPath id="lames"><rect x="{x0 + 30}" y="{y0 + 40}" width="{x1 - x0 - 60}" height="{y1 - y0 - 80}"/></clipPath>'
               f'<g clip-path="url(#lames)">')
    y = PREMIERE_LAME
    while y < y1 - 40:
        out.append(f'<rect x="{x0 + 30}" y="{y}" width="{x1 - x0 - 60}" height="{LAME}" fill="{LAVIS}" {ST} stroke-width="3"/>')
        out.append(f'<rect x="{x0 + 30}" y="{y}" width="{x1 - x0 - 60}" height="{LAME}" fill="url(#v2)"/>')
        out.append(f'<path d="M{x0 + 34} {y + 3} H{x1 - 34}" stroke="{MINE}" stroke-width="2"/>')
        for _ in range(3):
            vx = r.uniform(x0 + 80, x1 - 300)
            out.append(f'<path d="M{vx:.0f} {y + r.randint(18, 46)} q90 -8 220 2" fill="none" stroke="{ENCRE}" stroke-width="1.4"/>')
        for nx in (x0 + 60, x1 - 60):
            out.append(f'<circle cx="{nx}" cy="{y + LAME / 2:.0f}" r="4" fill="{ENCRE}" stroke="{MINE}" stroke-width="1"/>')
        y += LAME + JOUR
    out.append('</g>')
    out.append('</g>')
    return "".join(out)


# --- Ilde en tête de la procession -------------------------------------------------------------
def ilde_cierge(i: int) -> str:
    """Ilde de profil vers la droite : la cloche ronde de sa robe, le tablier, la coiffe claire nouée
    derrière ; le visage est dans le noir ; le cierge tenu à deux mains, comme les autres."""
    pas = (0, 6, 0, -6)[i]
    hausse = (0, 2, 0, 2)[i]
    return "".join([
        f'<path d="M{92 - pas} 394 L{88 - pas} 405 L{120 - pas} 405 L{116 - pas} 394 Z M{128 + pas} 394 L{128 + pas} 405 L{160 + pas} 405 L{154 + pas} 394 Z" fill="{ENCRE}" {ST} stroke-width="1.4"/>',
        f'<g transform="translate(0 {-hausse})">',
        # la robe : la même cloche ronde qu'au repos, vue de profil
        f'<path d="M100 170 Q66 210 62 290 Q60 360 {70 - pas} 398 L{172 + pas} 398 Q180 360 176 290 Q172 210 140 170 Z" fill="url(#h2)" {ST} stroke-width="2.8"/>',
        # le tablier blanc, devant (à droite), qui accroche la lumière du cierge
        f'<path d="M140 232 Q160 310 {162 + pas / 2:.0f} 392 L{176 + pas / 2:.0f} 392 Q178 300 160 232 Z" fill="{PAPIER}" {ST} stroke-width="2"/>',
        f'<path d="M96 236 Q130 246 162 234" fill="none" {ST} stroke-width="2.6"/>',
        # le châle sur les épaules
        f'<path d="M96 172 Q124 192 150 172 L154 214 Q124 236 92 212 Z" fill="url(#h1)" {ST} stroke-width="2.2"/>',
        # tête : la coiffe claire, nouée derrière (deux pans), le visage dans le noir
        f'<path d="M98 150 Q94 102 124 96 Q152 100 150 148 Q140 168 120 168 Q104 164 98 150 Z" fill="{PAPIER}" {ST} stroke-width="2.4"/>',
        f'<path d="M122 122 Q124 108 140 108 Q150 116 148 140 Q142 156 128 158 Q120 150 122 122 Z" fill="{ENCRE}"/>',
        f'<path d="M100 150 L84 {176 + hausse * 2} M104 154 L92 {182 + hausse * 2}" {ST} stroke-width="3"/>',
        # le cierge à deux mains, la flamme en réserve de papier
        f'<circle cx="160" cy="196" r="24" fill="{PAPIER}"/>',
        f'<rect x="154" y="200" width="12" height="54" fill="{PAPIER}" {ST} stroke-width="1.8"/>',
        f'<path d="M144 236 Q158 228 174 236 L174 252 Q158 260 144 252 Z" fill="{PAPIER}" {ST} stroke-width="1.8"/>',
        flamme(160, 198, 28 + (i % 2) * 3),
        f'<path d="M160 198 V204" {ST} stroke-width="1.6"/>',
        '</g>'])


def main() -> None:
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    cin = root / ROOT_CIN
    cin.mkdir(parents=True, exist_ok=True)
    (cin / "cin_procession-nuit_01.svg").write_text(svg(rue()), encoding="utf-8")
    (cin / "cin_procession-nuit_02.svg").write_text(svg(volet()), encoding="utf-8")
    chr_ = root / "art" / "src" / "chr"
    (chr_ / "chr_ilde-cierge_marche_01.svg").write_text(planche([ilde_cierge(i) for i in range(4)]), encoding="utf-8")
    print("e3_procession_nuit : 2 calques + chr_ilde-cierge_marche_01")


if __name__ == "__main__":
    main()
