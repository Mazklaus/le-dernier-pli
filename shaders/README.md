# Shader écran gravure (Tools Programmer)

`ecran_gravure.gdshader` : une seule passe plein écran (une seule copie d'écran par image) qui applique le trait tremblé, le papier de l'étape avec son grain, et préserve exactement le rouge `#9B1C1C` et la couleur d'accent des étapes 5 et 6. Testé sous Godot 4.7.2, renderer Compatibility (OpenGL 3, même GLSL que WebGL2).

## Mise en place dans une scène d'étape
Posé automatiquement par `EtapeBase.ajouter_gravure()` : `CanvasLayer` « EcranGravure » (calque 10), `ColorRect` plein écran (`mouse_filter = Ignore`). Calques au-dessus, non déformés : InterfaceJeu 15, BulleDialogue 16, fondu des Passages 20, BuildInfo et menu debug 128. Pour piloter la Lucidité : `etape.materiau_gravure()` (`amplitude_px`, `rouge_efface`). Le réglage `effets_attenues` met `amplitude_px` à 0.
Au changement d'étape : `PapierEtapes.appliquer(materiau, etape)` (`scripts/rendu/papier_etapes.gd`).

## Paramètres
- Trait tremblé : `amplitude_px` (1,5 au repos, à monter quand la Lucidité baisse), `echelle_px`, `images_par_seconde` (6), `variantes` (3).
- Papier : `couleur_papier`, `couleur_encre` (inversion aux étapes 5 et 6), `grain` (réduit d'un tiers sur papier foncé), `taille_grain_px`, `grain_par_seconde`.
- Teinte : `teinte` (blanc par défaut), nuit et éclairage par lieu, posée par `EtapeBase.definir_teinte()` ; ne touche ni le rouge ni l'accent.
- Rouge : `couleur_rouge` (jamais remappé, granuleux ni teinté), `seuil_rouge`, `rouge_efface` (0 à 1, effets de Lucidité).
- Accent : `accent_actif`, `couleur_accent` (ocre `#B08A3E` en 5, vert-de-gris `#5F7F72` en 6), `tolerance_accent`.

## Contrainte pour les assets
Dessiner avec la palette exacte de la planche (encre `#15130F`, papier `#E8E5DA`, lavis, mine, rouge, accents). Le rouge doit rester saturé (`r - max(g, b)` > 0,18) et l'accent à moins de 0,12 de sa valeur exacte pour être reconnus.
