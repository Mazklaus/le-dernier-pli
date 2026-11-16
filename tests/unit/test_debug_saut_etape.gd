extends GutTest
## Un saut F1 vers une rencontre pose l'étape de GameState (demande QA) : à e7_sceau, les
## gestes du sceau et l'usure de Lucidité doivent valoir l'étape 7, pas l'étape 1.

const MENU := preload("res://debug/debug_menu.gd")


func before_each() -> void:
	GameState.reinitialiser()


func after_each() -> void:
	GameState.reinitialiser()


func test_le_saut_pose_l_etape_de_la_rencontre() -> void:
	watch_signals(GameState)
	MENU.poser_etape_de(&"e7_sceau")
	assert_eq(GameState.etape, 7)
	assert_signal_emitted_with_parameters(GameState, "etape_changee", [7])
	assert_true(GameState.gestes_sceau_permis(), "Briser le sceau redevient possible")


func test_un_saut_dans_la_meme_etape_ne_change_rien() -> void:
	watch_signals(GameState)
	MENU.poser_etape_de(&"e1_ordre")
	assert_eq(GameState.etape, 1)
	assert_signal_not_emitted(GameState, "etape_changee")
