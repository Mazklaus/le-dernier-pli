extends GutTest
## La bulle affiche les options et prélève les coûts déclarés en tags au moment du choix.

const SceneBulle := preload("res://scenes/ui/bulle_dialogue/bulle_dialogue.tscn")
const Dialogue := preload("res://scenes/bac_a_sable/bac_a_sable.dialogue")


func before_each() -> void:
	GameState.reinitialiser()


func after_all() -> void:
	GameState.reinitialiser()


func _ouvrir(titre: String) -> Node:
	var bulle: Node = add_child_autofree(SceneBulle.instantiate())
	bulle.start(Dialogue, titre)
	await wait_process_frames(3)
	bulle._replique.skip_typing()
	await wait_process_frames(3)
	return bulle


func test_options_visibles_et_grisees() -> void:
	var bulle: Node = await _ouvrir("couts")
	assert_eq(bulle.ligne.character, "Ravaude")
	var options: Array = bulle.options_affichees
	assert_eq(options.size(), 4, "l'option [#cache] dont la condition échoue est cachée")
	assert_true(options[0]["disponible"])
	assert_false(options[2]["disponible"], "condition non remplie : grisée")


func test_choisir_preleve_les_couts_declares() -> void:
	var bulle: Node = await _ouvrir("couts")
	bulle.choisir(0)
	await wait_process_frames(3)
	assert_eq(GameState.vivres, 5)
	assert_eq(bulle.ligne.text, "Merci.")


func test_sans_prelevement_ne_preleve_rien() -> void:
	var bulle: Node = await _ouvrir("couts")
	bulle.choisir(1)
	await wait_process_frames(3)
	assert_eq(GameState.huile, 4)


func test_option_grisee_non_choisissable() -> void:
	var bulle: Node = await _ouvrir("couts")
	bulle.choisir(2)
	await wait_process_frames(3)
	assert_eq(bulle.ligne.text, "Choisis.")


func test_glyphe_et_libelle_de_l_invite() -> void:
	var texte := InviteInteraction.texte_pour("Parler à Jacquot")
	assert_true(texte.ends_with("] Parler à Jacquot"))
	assert_true(texte.begins_with("["))
	var long := InviteInteraction.texte_pour("Un libellé beaucoup trop long pour la plaque")
	assert_true(long.length() <= 24 + 4 + InviteInteraction.glyphe_action(&"interagir").length())
