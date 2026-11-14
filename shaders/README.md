# Shaders du DA : trait tremblé et papier (Tools Programmer)

À copier dans `res://shaders/`. Testés le 14/11 sous Godot 4.7.2, renderer Compatibility (OpenGL 3, même GLSL que WebGL2) : compilation sans erreur, rendu vérifié (captures dans la PR).

## Mise en place dans une scène d'étape
Deux `CanvasLayer` au-dessus du monde et sous l'interface, chacun avec un `ColorRect` plein écran (`mouse_filter = Ignore`) :
1. calque 10 : `trait_tremble.gdshader`
2. calque 11 : `papier.gdshader`
3. calque 20 et plus : l'UI (ni tremblement ni remappage).

## trait_tremble.gdshader
Déformation plein écran par bruit, 3 variantes qui tournent à 6 images/s. Paramètres : `amplitude_px` (1,5 au repos, à monter quand la Lucidité baisse), `echelle_px`, `images_par_seconde`, `variantes`. Indépendant de la résolution (calé sur 1080p).

## papier.gdshader
Remappe l'encre de référence `#15130F` et le papier `#E8E5DA` vers l'encre et le papier de l'étape (inversion possible aux étapes 5 et 6), laisse passer le rouge, ajoute un grain qui change 6 fois par seconde. Paramètres : `couleur_papier`, `couleur_encre`, `couleur_rouge`, `seuil_rouge`, `rouge_efface` (0 à 1, pour les effets de Lucidité), `grain`, `taille_grain_px`, `grain_par_seconde`.

`papier_etapes.gd` (`PapierEtapes.appliquer(materiau, etape)`) contient les valeurs des 7 étapes de la planche de style. Les couleurs d'accent des étapes 5 et 6 (ocre, vert-de-gris) restent dans les assets.

## Contrainte pour les assets
Le remappage suppose des assets dessinés avec la palette de la planche (encre, lavis, mine, papier, rouge). Un rouge doit rester bien saturé (`r - max(g, b)` au-dessus de 0,18) pour être reconnu.
