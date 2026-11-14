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
