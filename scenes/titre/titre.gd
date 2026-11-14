extends Control
## Écran titre provisoire. Le premier clic ou la première touche déverrouille l'audio
## (obligatoire sur le web) puis lance l'étape 1. Maquette finale : UI/UX Designer.


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"interagir") or event.is_action_pressed(&"clic"):
		get_viewport().set_input_as_handled()
		AudioDirector.deverrouiller()
		GameState.reinitialiser()
		SceneRouter.aller_etape(1)
