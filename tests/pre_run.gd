extends GutHookScript
## Pré-hook GUT : isole les tests du fichier de réglages du joueur (user://reglages.cfg).
## Sans lui, un test qui appelle Reglages.changer() modifie les lancements locaux suivants.


func run() -> void:
	var reglages := (Engine.get_main_loop() as SceneTree).root.get_node_or_null(^"Reglages")
	if reglages != null:
		reglages.isoler_pour_tests()
