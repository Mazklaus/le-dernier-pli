# Conventions

## Code GDScript

- **Typage statique partout** : variables, paramètres, retours (`var vivres: int`, `func valeur(nom: StringName) -> int`). L'avertissement `untyped_declaration` est activé.
- **Langue** : les identifiants du jeu sont en **français**, en ASCII sans accents (`modifier_jauge`, `lucidite`, `jouer_etape`). Les commentaires sont en français, avec accents.
- Nommage : `snake_case` pour fichiers, fonctions, variables et signaux ; `PascalCase` pour les nœuds et `class_name` ; `MAJUSCULES` pour les constantes. Fonctions privées préfixées `_`. Signaux au participe passé (`jauge_changee`).
- Identifiants de données en `StringName` (`&"vivres"`), pas en chaînes libres.
- Ordre dans un script : `extends`, `class_name`, doc `##`, signaux, constantes, `@export`, variables, `_init`/`_ready`, fonctions publiques, fonctions privées.
- Pas de `class_name` sur un autoload. Pas de chemin de nœud fragile (`get_node("../../X")`) : préférer `@export` ou `%NomUnique`.
- Aucune touche codée en dur : toujours une action de l'Input Map. Actions actuelles : `deplacer_gauche`, `deplacer_droite`, `interagir`, `annuler`, `clic`, `debug_menu`. Les touches sont en `physical_keycode` (A/D = Q/D en AZERTY).
- Personne n'écrit les variables de `GameState` directement : passer par son API.
- Une règle de jeu non triviale vient avec un test GUT dans `tests/unit/`.
- Indentation : tabulations (`.editorconfig`).

## Scènes et ressources

- Fichiers `.tscn` / `.tres` en texte, relus en PR. Éviter de modifier une scène qu'un autre poste a ouverte dans une PR en cours.
- Une scène = un dossier avec son script du même nom.
- Ne pas modifier `addons/` : mettre à jour un addon se fait dans une PR dédiée.

## Assets

Nommage et formats vérifiés par `tools/check_assets.py` (voir `tools/README` du Tools Programmer et `docs/architecture.md`) :
- Graphismes : `chr_<perso>_<anim>_NN`, `env_eN_planN_<nom>[_NN]`, `fx_<nom>`, `ui_<nom>`, calque rouge `<nom>_red`.
- Audio : `amb_<etape>_<couche>.ogg`, `mus_<etape>_<moment>.ogg`, `sfx_<famille>_<action>_NN.wav`, `vox_<personnage>_NN.wav`.

## Branches et commits

- `main` est protégée : tout passe par pull request, CI verte obligatoire.
- Branches : `<poste>/<sujet>`, par exemple `gameplay/deplacement-messager`, `narration/etape-01`, `tools/shader-papier`, `fix/123-jauge-negative`.
- Commits en français, à l'impératif, courts : `Ajoute le déplacement latéral du messager`.

## Pull requests

- Une PR = un sujet. Description : quoi, pourquoi, comment tester, captures si c'est visible.
- Relecture : le **Lead Programmer** relit toute PR qui touche au code, aux scènes ou à la CI. Le poste concerné relit le contenu de son domaine (Narrative Designer pour les dialogues, DA pour les visuels, Sound Designer pour l'audio).
- Le QA teste les builds debug de la PR (artefacts `build-<plateforme>-debug`).
- Une bloquante sur l'export web empêche le merge.

## Bugs

Issues GitHub avec le modèle « Bug ». Toujours indiquer le SHA affiché en bas à droite du build. Labels :
- `type:bug`
- `sev:bloquante`, `sev:majeure`, `sev:mineure`, `sev:cosmetique`
- `plateforme:web`, `plateforme:windows`, `plateforme:linux`
- `zone:gameplay`, `zone:dialogue`, `zone:ui`, `zone:audio`, `zone:build`
