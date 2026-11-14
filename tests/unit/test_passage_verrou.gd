extends GutTest
## Passages entre lieux et verrous levés par une rencontre vue.

const SceneMessager := preload("res://scenes/messager/messager.tscn")
const ScenePassage := preload("res://scenes/interactions/passage/passage.tscn")

var etape: EtapeBase
var m: Messager


func before_each() -> void:
	GameState.reinitialiser()
	etape = add_child_autofree(EtapeBase.new())
	m = SceneMessager.instantiate()
	m.gravite = 0.0
	etape.add_child(m)
	m.global_position = Vector2(100, 900)


func after_all() -> void:
	GameState.reinitialiser()


func _marqueur(nom: String, pos: Vector2, parent: Node = null) -> Marker2D:
	var marqueur := Marker2D.new()
	marqueur.name = nom
	(parent if parent != null else etape).add_child(marqueur)
	marqueur.global_position = pos
	return marqueur


func _passage(vers: StringName) -> Passage:
	var p: Passage = ScenePassage.instantiate()
	p.vers = vers
	etape.add_child(p)
	return p


func test_passage_vers_entree_du_lieu() -> void:
	# Le marqueur peut être au fond d'une sous-scène de lieu.
	var lieu := Node2D.new()
	etape.add_child(lieu)
	_marqueur("entree_couchette", Vector2(-5000, 400), lieu)
	var p := _passage(&"couchette")
	watch_signals(p)
	assert_true(p.est_disponible())
	p.interagir(m)
	assert_eq(m.global_position, Vector2(-5000, 400))
	assert_signal_emitted_with_parameters(p, "franchi", [p, &"couchette"])


func test_passage_sans_destination_indisponible() -> void:
	var p := _passage(&"nulle_part")
	assert_false(p.est_disponible())
	p.interagir(m)
	assert_eq(m.global_position, Vector2(100, 900))


func test_passage_ferme_par_une_rencontre() -> void:
	_marqueur("entree_sape_sortie", Vector2(3000, 900))
	var p := _passage(&"sape_sortie")
	p.rencontre_requise = &"e1_cendre"
	assert_false(p.est_disponible())
	GameState.marquer_rencontre_vue(&"e1_cendre")
	assert_true(p.est_disponible())


func test_passage_lit_la_metadonnee_vers_de_la_maquette() -> void:
	_marqueur("entree_cantine", Vector2(200, 200))
	var p: Passage = ScenePassage.instantiate()
	p.set_meta(&"vers", "cantine")
	etape.add_child(p)
	assert_eq(p.vers, &"cantine")
	assert_true(p.est_disponible())


func test_passage_est_une_cible_du_messager() -> void:
	_marqueur("entree_couchette", Vector2(-5000, 400))
	var p := _passage(&"couchette")
	p.global_position = Vector2(140, 900)
	await wait_physics_frames(5)
	assert_eq(m.cible, p)


func test_verrou_s_ouvre_quand_la_rencontre_est_vue() -> void:
	var v := Verrou.new()
	v.rencontre = &"e1_ordre"
	var forme := CollisionShape2D.new()
	forme.shape = RectangleShape2D.new()
	v.add_child(forme)
	etape.add_child(v)
	assert_true(v.visible)
	assert_false(forme.disabled)
	watch_signals(v)
	GameState.marquer_rencontre_vue(&"e1_ordre")
	await wait_process_frames(2)
	assert_false(v.visible)
	assert_true(forme.disabled)
	assert_signal_emitted(v, "ouvert")


func test_verrou_deja_ouvert_au_chargement() -> void:
	GameState.marquer_rencontre_vue(&"e1_cendre")
	var v := Verrou.new()
	v.rencontre = &"e1_cendre"
	etape.add_child(v)
	assert_false(v.visible)


func test_signal_rencontre_vue_marquee_une_seule_fois() -> void:
	watch_signals(GameState)
	GameState.marquer_rencontre_vue(&"e1_ordre")
	GameState.marquer_rencontre_vue(&"e1_ordre")
	assert_signal_emit_count(GameState, "rencontre_vue_marquee", 1)
