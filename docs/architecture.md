# Architecture

Moteur : Godot 4.7.2-stable, GDScript typé, renderer **Compatibility** (WebGL2) sur toutes les plateformes. Pas de C# : la version .NET de Godot n'exporte pas pour le web.

## Autoloads (ordre de chargement)

| Autoload | Fichier | Rôle | Propriétaire |
|---|---|---|---|
| `GameState` | `autoload/game_state.gd` | Jauges, marques, sceau, étape. Fonction unique `modifier_jauge`. Émet des signaux, ne connaît personne. | Gameplay Prog |
| `AudioDirector` | `autoload/audio_director.gd` | Seul point de lecture du son. S'abonne à GameState. | Sound Designer + Gameplay Prog |
| `Reglages` | `autoload/reglages.gd` | Options du joueur (user://reglages.cfg), volumes appliqués aux bus. | Lead Prog |
| `SceneRouter` | `autoload/scene_router.gd` | Titre → étapes 1 à 7, `aller_etape`, `etape_suivante`, `aller_rencontre`. | Lead Prog |
| `DialogueManager` | `addons/dialogue_manager/` | Runtime des fichiers `.dialogue`. | addon |
| `BuildInfo` | `autoload/build_info.gd` | SHA du build en coin d'écran (debug seulement). | Lead Prog |
| `DebugLoader` | `debug/debug_loader.gd` | Menu F1 du QA (debug seulement). | Tools Prog |

## Sens des dépendances

```
Scènes d'étape, UI, dialogues ──appellent──▶ GameState (API publique)
GameState ──signaux──▶ AudioDirector, HUD, carnet
SceneRouter ──▶ GameState.passer_etape(), AudioDirector.jouer_etape()
```

GameState ne dépend de rien. Personne n'écrit ses variables directement : tout passe par `modifier_jauge`, `appliquer_couts`, `appliquer_effets`, `ajouter_marque`, les fonctions du sceau, et `depuis_dictionnaire` pour l'autosave (jalon 2). Les règles pures (calcul de la fin) sont dans `scripts/regles/`, testables sans scène.

## Arborescence

```
addons/            Dialogue Manager 4.2.0, GUT 9.7.1 (vendorisés, ne pas modifier)
autoload/          singletons
scenes/titre/      écran titre
scenes/etapes/etape_NN/   une scène racine par étape : etape_NN.tscn + etape_NN.gd
scripts/regles/    logique pure (pas de Node)
scripts/ui/        scripts d'interface
dialogue/etape_NN/ fichiers .dialogue du Narrative Designer
assets/graphics/   PNG exportés (depuis art/src/)
assets/audio/      OGG (boucles) et WAV (SFX, UI, voix)
art/src/           sources SVG du DA (ignorées par Godot)
shaders/           shaders du DA, compatibles renderer Compatibility
debug/             menu de débogage (debug seulement)
tests/unit/        tests GUT
tools/             scripts Python du pipeline (ignorés par Godot)
```

## Une étape

La racine de `etape_NN.tscn` est un `Node2D` dont le script peut exposer `aller_rencontre(id: StringName)` pour le saut de débogage. Identifiants de rencontre : `&"eN_nom"` (ex. `&"e1_sergent"`). Pour finir l'étape, appeler `SceneRouter.etape_suivante()`, qui applique le coût de la marche puis charge l'étape suivante.

## Dialogues

Fichiers `.dialogue` (Dialogue Manager 4). Conditions et effets appellent l'API publique de GameState, par exemple `[if GameState.valeur(&"vivres") >= 2]` et `do GameState.appliquer_couts({&"vivres": 1})`. Voir `dialogue/etape_01/exemple.dialogue`. Tout fichier qui ne compile pas fait échouer la CI (import et test `test_dialogues.gd`).

## Rendu et assets

Base 1920x1080, stretch `canvas_items`, aspect `expand`. Filtrage linéaire sans mipmaps (jamais `nearest`). Textures ≤ 4096 px, décors découpés en tuiles de 2048. Calques rouges suffixés `_red`. Une seule passe plein écran. Budget du build web de l'étape 1 : 60 Mo.

## Web

Export sans threads (`variant/thread_support=false`) : pas d'en-têtes COOP/COEP, fonctionne sur GitHub Pages et itch.io. Aucun son avant la première interaction : l'écran titre appelle `AudioDirector.deverrouiller()`.

## Hors jalon 1

Sauvegarde (autosave entre étapes au jalon 2, via `vers_dictionnaire`), manette (toutes les entrées passent déjà par l'Input Map).
