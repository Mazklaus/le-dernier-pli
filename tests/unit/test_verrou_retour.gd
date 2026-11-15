extends GutTest
## VerrouRetour : ouvert au départ, se ferme derrière le messager une fois la rencontre vue et
## le verrou franchi, ne se rouvre plus.

const SceneMessager := preload("res://scenes/messager/messager.tscn")

var v: VerrouRetour
var forme: CollisionShape2D
var m: Messager


func before_each() -> void:
	GameState.reinitialiser()
	v = VerrouRetour.new()
	v.rencontre = &"e9_ceinture"
	forme = CollisionShape2D.new()
	forme.shape = RectangleShape2D.new()
	v.add_child(forme)
	add_child_autofree(v)
	v.global_position = Vector2(1000, 500)
	m = add_child_autofree(SceneMessager.instantiate())
	m.gravite = 0.0
	m.global_position = Vector2(800, 500)
	await wait_physics_frames(2)


func after_all() -> void:
	GameState.reinitialiser()


func test_ouvert_au_depart() -> void:
	assert_false(v.visible)
	assert_true(forme.disabled)


func test_ne_se_ferme_qu_apres_la_rencontre_et_le_franchissement() -> void:
	assert_false(v.doit_se_fermer(1200.0), "rencontre pas vue")
	GameState.marquer_rencontre_vue(&"e9_ceinture")
	assert_false(v.doit_se_fermer(1050.0), "pas encore à la marge")
	assert_true(v.doit_se_fermer(1100.0))


func test_se_ferme_et_reste_ferme() -> void:
	GameState.marquer_rencontre_vue(&"e9_ceinture")
	watch_signals(v)
	m.global_position = Vector2(1200, 500)
	await wait_physics_frames(3)
	assert_true(v.est_ferme)
	assert_true(v.visible)
	assert_false(forme.disabled)
	assert_signal_emit_count(v, "ferme", 1)
	m.global_position = Vector2(800, 500)
	await wait_physics_frames(3)
	assert_true(v.est_ferme)
