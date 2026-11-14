extends GutTest
## Déplacement latéral et choix de la cible d'interaction du messager.

const SceneMessager := preload("res://scenes/messager/messager.tscn")
const SceneDeclencheur := preload("res://scenes/interactions/declencheur_dialogue/declencheur_dialogue.tscn")
const Dialogue := preload("res://scenes/bac_a_sable/bac_a_sable.dialogue")

var m: Messager


func before_each() -> void:
	GameState.reinitialiser()
	m = add_child_autofree(SceneMessager.instantiate())
	m.gravite = 0.0
	m.global_position = Vector2(500, 500)


func after_each() -> void:
	Input.action_release(&"deplacer_droite")
	Input.action_release(&"deplacer_gauche")


func _declencheur(x: float, id: StringName) -> DeclencheurDialogue:
	var d: DeclencheurDialogue = add_child_autofree(SceneDeclencheur.instantiate())
	d.rencontre_id = id
	d.dialogue = Dialogue
	d.global_position = Vector2(x, 500)
	return d


func test_valeurs_du_plan() -> void:
	assert_eq(m.vitesse, 160.0)
	assert_eq(Messager.RAYON_INTERACTION, 96.0)


func test_marche_a_droite_puis_a_gauche() -> void:
	Input.action_press(&"deplacer_droite")
	await wait_physics_frames(10)
	assert_gt(m.global_position.x, 500.0)
	assert_eq(m.regard, 1)
	Input.action_release(&"deplacer_droite")
	var x := m.global_position.x
	Input.action_press(&"deplacer_gauche")
	await wait_physics_frames(10)
	assert_lt(m.global_position.x, x)
	assert_eq(m.regard, -1)


func test_bloque_ne_bouge_pas() -> void:
	m.bloque = true
	Input.action_press(&"deplacer_droite")
	await wait_physics_frames(10)
	assert_eq(m.global_position.x, 500.0)


func test_cible_la_plus_proche() -> void:
	var loin := _declencheur(580.0, &"e1_loin")
	var proche := _declencheur(540.0, &"e1_proche")
	await wait_physics_frames(5)
	assert_eq(m.cible, proche)
	proche.une_seule_fois = true
	proche.terminer(false)
	await wait_physics_frames(2)
	assert_eq(m.cible, loin, "un déclencheur épuisé n'est plus ciblé")


func test_hors_de_portee() -> void:
	_declencheur(900.0, &"e1_loin")
	await wait_physics_frames(5)
	assert_null(m.cible)


func test_saut_de_debogage_place_devant_le_declencheur() -> void:
	var d := _declencheur(1500.0, &"e1_parapet")
	m.placer_devant(d)
	assert_eq(m.global_position.x, 1500.0 - Messager.ECART_PLACEMENT)


func _pente(degres: float) -> StaticBody2D:
	# Plat de x 0 à 400 (y 600), puis pente montante de 600 px vers la droite.
	var sol := StaticBody2D.new()
	var forme := CollisionPolygon2D.new()
	var dy := 600.0 * tan(deg_to_rad(degres))
	forme.polygon = PackedVector2Array([Vector2(0, 600), Vector2(400, 600), Vector2(1000, 600 - dy),
		Vector2(1400, 600 - dy), Vector2(1400, 900), Vector2(0, 900)])
	sol.add_child(forme)
	add_child_autofree(sol)
	return sol


func test_monte_et_descend_une_pente_de_30_degres() -> void:
	_pente(30.0)
	m.gravite = 2400.0
	m.global_position = Vector2(300, 560)
	await wait_physics_frames(20)
	Input.action_press(&"deplacer_droite")
	await wait_physics_frames(300)
	Input.action_release(&"deplacer_droite")
	assert_gt(m.global_position.x, 600.0, "la pente ne bloque pas")
	assert_lt(m.global_position.y, 560.0, "il a monté")
	Input.action_press(&"deplacer_gauche")
	var decolle := 0
	for i in 120:
		await wait_physics_frames(1)
		if not m.is_on_floor():
			decolle += 1
	Input.action_release(&"deplacer_gauche")
	assert_lt(decolle, 3, "collé au sol en descente")


func test_immobile_a_l_arret_sur_la_pente() -> void:
	_pente(30.0)
	m.gravite = 2400.0
	m.global_position = Vector2(700, 300)
	await wait_physics_frames(60)
	var x := m.global_position.x
	await wait_physics_frames(60)
	assert_almost_eq(m.global_position.x, x, 0.5, "ne glisse pas")
