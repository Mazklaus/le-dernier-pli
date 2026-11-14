extends GutTest
## Verrou, usage unique et fin d'étape des DeclencheurDialogue (sans afficher de dialogue).

const SceneDeclencheur := preload("res://scenes/interactions/declencheur_dialogue/declencheur_dialogue.tscn")
const Dialogue := preload("res://scenes/bac_a_sable/bac_a_sable.dialogue")

var d: DeclencheurDialogue


func before_each() -> void:
	GameState.reinitialiser()
	d = add_child_autofree(SceneDeclencheur.instantiate())
	d.rencontre_id = &"e1_adieu"
	d.dialogue = Dialogue


func after_all() -> void:
	GameState.reinitialiser()


func test_disponible_par_defaut() -> void:
	assert_true(d.est_disponible())
	assert_eq(d.titre_a_jouer(), "debut")
	assert_true(d.is_in_group(DeclencheurDialogue.GROUPE))


func test_sans_dialogue_indisponible() -> void:
	d.dialogue = null
	assert_false(d.est_disponible())


func test_verrou_tant_que_la_rencontre_requise_n_est_pas_vue() -> void:
	d.rencontre_requise = &"e1_cendre"
	d.titre_si_verrouille = "refus_sans_cendre"
	assert_eq(d.titre_a_jouer(), "refus_sans_cendre")
	GameState.marquer_rencontre_vue(&"e1_cendre")
	assert_eq(d.titre_a_jouer(), "debut")


func test_dialogue_verrouille_ne_compte_pas_la_rencontre() -> void:
	d.rencontre_requise = &"e1_cendre"
	d.titre_si_verrouille = "refus_sans_cendre"
	d.terminer(true)
	assert_false(GameState.rencontre_vue(&"e1_adieu"))
	d.terminer(false)
	assert_true(GameState.rencontre_vue(&"e1_adieu"))


func test_usage_unique() -> void:
	d.une_seule_fois = true
	d.terminer(false)
	assert_false(d.est_disponible())


func test_usage_multiple_par_defaut() -> void:
	d.terminer(false)
	assert_true(d.est_disponible())


func test_indisponible_pendant_le_dialogue() -> void:
	d.en_cours = true
	assert_false(d.est_disponible())


func test_signal_dialogue_termine() -> void:
	watch_signals(d)
	d.terminer(false)
	assert_signal_emitted(d, "dialogue_termine")
