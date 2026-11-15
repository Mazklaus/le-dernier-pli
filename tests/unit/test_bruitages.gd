extends GutTest
## Bruitages du jeu (liste du Sound Designer, #37) : correspondances et branchements.

const SceneMessager := preload("res://scenes/messager/messager.tscn")
const ScenePassage := preload("res://scenes/interactions/passage/passage.tscn")


func before_each() -> void:
	GameState.reinitialiser()


func after_all() -> void:
	GameState.reinitialiser()


func test_sons_du_sceau() -> void:
	assert_eq(BruitagesJeu.son_sceau(&"abime"), "sfx_sceau_abimer")
	assert_eq(BruitagesJeu.son_sceau(&"rechauffe"), "sfx_sceau_rechauffer")
	assert_eq(BruitagesJeu.son_sceau(&"ouvert"), "sfx_sceau_ouvrir")
	assert_eq(BruitagesJeu.son_sceau(&"autre"), "")


func test_seules_les_hausses_de_jauge_sonnent() -> void:
	assert_eq(BruitagesJeu.son_jauge(&"huile", 1, 2), "sfx_lanterne_remplir")
	assert_eq(BruitagesJeu.son_jauge(&"vivres", 3, 5), "sfx_pain_manger")
	assert_eq(BruitagesJeu.son_jauge(&"vivres", 5, 3), "", "un coût ne sonne pas")
	assert_eq(BruitagesJeu.son_jauge(&"lucidite", 1, 2), "")


func test_tous_les_sons_existent() -> void:
	var bases: Array[String] = ["sfx_carnet_fremir", "sfx_lanterne_allumer", "sfx_lanterne_eteindre",
		"sfx_cendre_front", "sfx_passage_escalier", "sfx_passage_toile", "sfx_pas_planche",
		"sfx_pas_boue", "sfx_pas_terre", "sfx_ui_survol", "sfx_ui_valider", "sfx_ui_refus"]
	for b: String in BruitagesJeu.SONS_SCEAU.values() + bases:
		assert_false(AudioDirector.variantes_de(b).is_empty(), b)


func test_audio_director_pose_les_bruitages() -> void:
	assert_not_null(AudioDirector.get_node_or_null("BruitagesJeu"))


func test_le_pied_qui_se_pose_fait_un_pas() -> void:
	var s: SilhouetteTobie = add_child_autofree(SilhouetteTobie.new())
	watch_signals(s)
	s.jouer(SilhouetteTobie.MARCHE)
	await wait_seconds(0.85)
	var n: int = get_signal_emit_count(s, "pas_pose")
	assert_between(n, 2, 3, "deux appuis par cycle de 0,8 s")
	s.jouer(SilhouetteTobie.REPOS)
	await wait_seconds(0.5)
	assert_eq(get_signal_emit_count(s, "pas_pose"), n, "pas de pas au repos")


func test_son_des_pas_et_des_passages_selon_le_niveau() -> void:
	var etape: EtapeBase = EtapeBase.new()
	etape.limite_surface_y = 1000.0
	etape.pas_surface = "sfx_pas_planche"
	var m: Messager = SceneMessager.instantiate()
	m.gravite = 0.0
	etape.add_child(m)
	add_child_autofree(etape)
	m.teleporter(Vector2(100, 900))
	assert_eq(m.son_pas, "sfx_pas_planche")
	m.teleporter(Vector2(100, 1600))
	assert_eq(m.son_pas, "sfx_pas_terre")
	assert_eq(etape.son_passage(Vector2(0, 900), Vector2(0, 1600)), "sfx_passage_escalier")
	assert_eq(etape.son_passage(Vector2(0, 1600), Vector2(500, 1700)), "sfx_passage_toile")


func test_etape_1_marche_sur_les_caillebotis() -> void:
	var etape: EtapeBase = load("res://scenes/etapes/etape_01/etape_01.tscn").instantiate()
	assert_eq(etape.pas_surface, "sfx_pas_planche")
	etape.free()


func test_les_sons_des_gestes_existent() -> void:
	for b: String in ["sfx_pli_lire", "sfx_periscope_regarder", "sfx_echelle_monter"]:
		assert_false(AudioDirector.variantes_de(b).is_empty(), b)


func test_lire_une_ligne_du_pli_emet_le_signal_du_son() -> void:
	watch_signals(GameState)
	GameState.passer_etape()
	GameState.rechauffer_sceau()
	assert_eq(GameState.lire_ligne_pli(), 0)
	assert_signal_emitted_with_parameters(GameState, "ligne_pli_lue", [0])
	assert_eq(GameState.lire_ligne_pli(), -1)
	assert_signal_emit_count(GameState, "ligne_pli_lue", 1, "pas de son sans lecture")
	var ecoute := false
	for c: Dictionary in GameState.ligne_pli_lue.get_connections():
		ecoute = ecoute or (c["callable"] as Callable).get_object() is BruitagesJeu
	assert_true(ecoute, "BruitagesJeu joue sfx_pli_lire")


func test_periscope_et_echelle_a_l_etape_1() -> void:
	var etape: EtapeBase = add_child_autofree(load("res://scenes/etapes/etape_01/etape_01.tscn").instantiate())
	assert_eq(etape.trouver_declencheur(&"e1_guetteur").son_debut, "sfx_periscope_regarder")
	# l'échelle sonne dans la cinématique de sortie, quand Tobie commence à monter
	assert_eq(etape.trouver_declencheur(&"e1_parapet").son_fin, "")


func test_un_passage_peut_imposer_son_son() -> void:
	var p: Passage = ScenePassage.instantiate()
	assert_eq(p.son, "", "par défaut l'étape choisit")
	p.son = "sfx_echelle_monter"
	assert_eq(p.son, "sfx_echelle_monter")
	p.free()
