extends GutTest
## Décor de surface de l'étape 1 : cinq plans aux vitesses et largeurs de la planche du DA,
## cendre en boucle, fonds gris de la maquette masqués, Chicane habillée.

const ETAPE := preload("res://scenes/etapes/etape_01/etape_01.tscn")
## [vitesse, largeur attendue] (planche du DA, niveau de 10624 px).
const ATTENDU := [[0.05, 2355.0], [0.2, 3661.0], [0.5, 6272.0], [1.0, 10624.0], [1.4, 14106.0]]

var _etape: EtapeBase
var _decor: DecorE1


func before_each() -> void:
	_etape = ETAPE.instantiate()
	add_child_autofree(_etape)
	await wait_process_frames(2)
	_decor = _etape.get_node("Decors") as DecorE1


func test_cinq_plans_aux_bonnes_vitesses_et_largeurs() -> void:
	assert_eq(_decor.plans.size(), 5)
	for i in mini(_decor.plans.size(), ATTENDU.size()):
		var plan := _decor.plans[i]
		assert_almost_eq(plan.scroll_scale.x, float(ATTENDU[i][0]), 0.001, plan.name)
		assert_almost_eq(DecorParallaxe.largeur(plan), float(ATTENDU[i][1]), 1.0, plan.name)


func test_premier_plan_devant_les_autres_derriere() -> void:
	for plan in _decor.plans:
		if plan.scroll_scale.x > 1.0:
			assert_gt(plan.z_index, 0, plan.name)
		else:
			assert_lt(plan.z_index, 0, plan.name)


func test_cendre_entre_le_plan_2_et_le_plan_3() -> void:
	assert_not_null(_decor.cendre)
	var z := (_decor.cendre.get_parent() as Node2D).z_index
	assert_gt(z, _decor.plans[2].z_index)
	assert_lt(z, _decor.plans[3].z_index)
	var avant := _decor.cendre.region_rect.position.y
	await wait_process_frames(10)
	assert_ne(_decor.cendre.region_rect.position.y, avant, "la cendre tombe")


func test_fonds_maquette_masques_et_chicane_habillee() -> void:
	for section in _etape.get_node("Surface").get_children():
		var fond := section.get_node_or_null("Fond") as CanvasItem
		if fond != null:
			assert_false(fond.visible, section.name)
	var chicane := _etape.get_node("Surface/BoyauArriere/Chicane")
	assert_not_null(chicane.get_node_or_null("Dessin"))
	assert_false((chicane.get_node("Visuel") as CanvasItem).visible)


func test_camera_bornee_a_la_surface_libre_sous_terre() -> void:
	var messager := _etape.trouver_messager()
	var camera := messager.get_node("%Camera") as Camera2D
	messager.teleporter(_etape.find_child("porte_cantine", true, false).global_position)
	assert_eq(camera.limit_left, 0)
	assert_eq(camera.limit_right, 10624)
	messager.teleporter(_etape.find_child("entree_cantine", true, false).global_position)
	assert_lt(camera.limit_left, -100000, "sous terre : pas de borne")


func test_decalage_parallaxe_depuis_le_bord_gauche_de_l_ecran() -> void:
	# Planche du DA : x du plan = bord gauche de la caméra × (1 − vitesse), et non le centre.
	var messager := _etape.trouver_messager()
	messager.teleporter(_etape.find_child("porte_cantine", true, false).global_position)
	await wait_process_frames(5)
	var bord_gauche := -get_viewport().get_canvas_transform().origin.x
	assert_gt(bord_gauche, 0.0)
	for plan in _decor.plans:
		var attendu := bord_gauche * (1.0 - plan.scroll_scale.x)
		assert_almost_eq(plan.get_child(0).global_position.x, attendu, 2.0, plan.name)


func test_echelle_dans_l_ombre_puis_claire_apres_l_adieu() -> void:
	GameState.reinitialiser()
	_decor.actualiser_echelle()
	assert_not_null(_decor.echelle)
	assert_eq(_decor.echelle.texture.resource_path, DecorE1.ECHELLE_OMBRE)
	GameState.marquer_rencontre_vue(&"e1_adieu")
	assert_eq(_decor.echelle.texture.resource_path, DecorE1.ECHELLE_CLAIRE)
	GameState.reinitialiser()


func test_sols_et_murs_gris_masques() -> void:
	for chemin in ["Surface/BoyauArriere/Sol", "Surface/Carrefour/Sol", "Surface/PiedEchelle/Sol",
			"Surface/BoyauArriere/MurGauche", "Surface/Carrefour/MurDroit"]:
		var visuel := _etape.get_node(chemin + "/Visuel") as CanvasItem
		assert_false(visuel.visible, chemin)


func test_voiles_en_tout_ou_rien_selon_l_abscisse() -> void:
	assert_eq(_decor.voiles.size(), 2)
	var hachure: Sprite2D = _decor.voiles[0][0]
	var contre: Sprite2D = _decor.voiles[1][0]
	var z := (hachure.get_parent() as Node2D).z_index
	assert_gt(z, _decor.plans[2].z_index)
	assert_lt(z, _decor.plans[3].z_index)
	var messager := _etape.trouver_messager()
	messager.teleporter(Vector2(7000, 700))
	await wait_seconds(0.25)
	assert_almost_eq(hachure.modulate.a, 1.0, 0.01, "après x 6600")
	assert_false(contre.visible, "avant x 9000")
	messager.teleporter(Vector2(9500, 700))
	await wait_seconds(0.25)
	assert_almost_eq(contre.modulate.a, 1.0, 0.01, "après x 9000")
	messager.teleporter(Vector2(3000, 700))
	await wait_seconds(0.25)
	assert_false(hachure.visible, "retour en arrière : caché")
	assert_false(contre.visible)
