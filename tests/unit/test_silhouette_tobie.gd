extends GutTest
## Tobie dessiné (planche de la DA, #65) : planches découpées en images de 200×320 à 10 i/s,
## calques synchronisés, cendre au front après e1_cendre, animation selon le mouvement.

const SceneMessager := preload("res://scenes/messager/messager.tscn")

var m: Messager
var s: SilhouetteTobie


func before_each() -> void:
	GameState.reinitialiser()
	m = add_child_autofree(SceneMessager.instantiate())
	m.gravite = 0.0
	m.global_position = Vector2(500, 500)
	s = m.get_node("%Silhouette") as SilhouetteTobie


func after_each() -> void:
	Input.action_release(&"deplacer_droite")


func after_all() -> void:
	GameState.reinitialiser()


func test_planches_decoupees_au_format_convenu() -> void:
	assert_true(s.est_dessine())
	var images := s.base.sprite_frames
	assert_eq(images.get_frame_count(SilhouetteTobie.REPOS), 4)
	assert_eq(images.get_frame_count(SilhouetteTobie.MARCHE), 8)
	assert_eq(images.get_frame_count(SilhouetteTobie.INTERAGIR), 3)
	assert_eq(images.get_animation_speed(SilhouetteTobie.MARCHE), 10.0)
	assert_false(images.get_animation_loop(SilhouetteTobie.INTERAGIR), "interagir reste sur la main au pli")
	assert_eq(images.get_frame_texture(SilhouetteTobie.MARCHE, 0).get_size(), Vector2(200, 320))
	assert_eq(s.base.offset, Vector2(-100, -316), "origine aux pieds, hanches centrées")


func test_marche_sans_glisser() -> void:
	# 8 images à 10 i/s = 0,8 s par cycle ; la DA fait reculer le pied de 128 px par cycle.
	assert_almost_eq(128.0 / (8.0 / SilhouetteTobie.IMAGES_PAR_SECONDE), m.vitesse, 0.01)


func test_trois_calques_synchronises() -> void:
	assert_eq(s.calques().size(), 3)
	s.jouer(SilhouetteTobie.MARCHE)
	for c in s.calques():
		assert_eq(c.animation, SilhouetteTobie.MARCHE, c.name)


func test_cendre_au_front_apres_la_rencontre() -> void:
	assert_false(s.cendre.visible)
	GameState.marquer_rencontre_vue(&"e1_cendre")
	assert_true(s.cendre.visible)


func test_marche_puis_repos() -> void:
	await wait_physics_frames(2)
	assert_eq(s.animation, SilhouetteTobie.REPOS)
	Input.action_press(&"deplacer_droite")
	await wait_physics_frames(5)
	assert_eq(s.animation, SilhouetteTobie.MARCHE)
	Input.action_release(&"deplacer_droite")
	await wait_physics_frames(3)
	assert_eq(s.animation, SilhouetteTobie.REPOS)


func test_interagir_pendant_un_dialogue() -> void:
	m._sur_dialogue_commence(null)
	await wait_physics_frames(2)
	assert_eq(s.animation, SilhouetteTobie.INTERAGIR)
	m._sur_dialogue_fini(null)
	await wait_physics_frames(3)
	assert_eq(s.animation, SilhouetteTobie.REPOS)


func test_tourne_a_gauche_par_retournement() -> void:
	Input.action_press(&"deplacer_gauche")
	await wait_physics_frames(3)
	Input.action_release(&"deplacer_gauche")
	assert_eq(s.scale.x, -1.0)


func test_ruban_bat_au_palier_trouble() -> void:
	GameState.palier = GameState.TROUBLE
	var opacites := {}
	for i in 20:
		await wait_process_frames(1)
		opacites[snappedf(s.ruban.modulate.a, 0.01)] = true
		await wait_seconds(0.05)
	GameState.palier = GameState.palier_pour(GameState.lucidite)
	assert_true(opacites.has(0.55), "le ruban bat")
	assert_true(opacites.has(1.0))
