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


func test_l_etape_ajoute_l_interface_en_jeu() -> void:
	var etape: EtapeBase = add_child_autofree(load("res://scenes/bac_a_sable/bac_a_sable.tscn").instantiate())
	var interfaces := etape.get_children().filter(func(n: Node) -> bool: return n is InterfaceJeu)
	assert_eq(interfaces.size(), 1)
	assert_eq(etape.ajouter_interface(), interfaces[0], "pas de deuxième interface")


func test_le_cout_suit_le_texte_de_l_option() -> void:
	var bulle: Node = await _ouvrir("couts")
	var phrase := bulle._boutons[0].find_child("Phrase", true, false) as HBoxContainer
	assert_not_null(phrase)
	var texte := phrase.get_child(0) as Label
	assert_eq(texte.size_flags_horizontal, Control.SIZE_SHRINK_BEGIN, "le texte ne pousse plus le coût à droite")
	assert_gt(phrase.get_child_count(), 1, "le coût est dans la même phrase")


func test_le_focus_d_une_option_montre_l_apercu_sur_le_hud() -> void:
	var hud := HudJauges.new()
	add_child_autofree(hud)
	var bulle: Node = await _ouvrir("couts")
	(bulle._boutons[0] as Button).grab_focus()
	await wait_process_frames(2)
	assert_false(hud.apercu.is_empty(), "aperçu du coût de l'option qui a le focus")
	bulle._vider_options()
	assert_true(hud.apercu.is_empty())
