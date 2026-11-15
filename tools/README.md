# Outils

- `check_assets.py` : vérifie nommage, formats et réglages d'import des assets (lancé en CI avant tout export).
- `export_svg.py` : exporte les SVG de `art/src/` en PNG dans `assets/graphics/` (resvg, Inkscape en secours).

Écrits par le Tools Programmer. Détails des conventions : `CONTRIBUTING.md` et `docs/architecture.md`.

## Tuiles de décor rognées (mémoire vidéo)
`python3 tools/rogner_tuiles.py` rogne les marges transparentes des tuiles de tous les plans (0 à 4) dont la partie utile fait moins de 80 % de la tuile. Le PNG est remplacé par sa partie utile et un `AtlasTexture` `<nom>.tres` est écrit à côté, avec une marge qui redonne la taille et la position d'origine. `DecorParallaxe.charger_tuile()` charge le `.tres` s'il existe, sinon le PNG. Le script est idempotent, et `export_svg.py` le relance après chaque export. En CI, `--verifier` avertit si une tuile presque vide n'est pas rognée. Options : `--plans 3,4`, `--seuil 0.8` (défauts : tous les plans, 0.8). Les `fx_` (voiles, brouillard, textures répétées) ne sont jamais rognés.
