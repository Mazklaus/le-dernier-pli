# Le Dernier Pli

Un coureur de tranchée reçoit un pli scellé à porter derrière les lignes. Plus il avance, plus le monde se défait, et plus il comprend que ce message parle de lui.

Jeu narratif 2D en vue latérale, environ 90 minutes en sept étapes, sans combat. Projet pilote du studio Sentient Team.

## Démarrer

1. Installer **Godot 4.7.2-stable** (version standard, pas .NET).
2. Ouvrir `project.godot`. Les addons Dialogue Manager et GUT sont inclus dans `addons/`.
3. F5 lance l'écran titre, puis l'étape 1.

Tests : panneau GUT dans l'éditeur, ou en ligne de commande :

```sh
godot --headless --import
godot --headless -s addons/gut/gut_cmdln.gd -gconfig=res://.gutconfig.json
```

Conventions d'assets : `python3 tools/check_assets.py`.

## Builds

Chaque pull request produit des builds **debug** Web, Windows et Linux (onglet Actions, artefacts `build-<plateforme>-debug`), avec le menu de débogage (F1) et le SHA du commit en bas à droite. Chaque merge sur `main` publie la version release sur GitHub Pages.

## Documentation

- [Architecture](docs/architecture.md) : autoloads, scènes, flux de données.
- [Conventions](CONTRIBUTING.md) : code, nommage, branches, PR, bugs.
