extends GutTest
## Décor de surface de l'étape 2 : cinq plans de la planche du DA (#56), brouillard en
## tout-ou-rien entre x 4800 et 10100, cheval de frise, fil qui retombe, sacoche, gris masqués.

const ETAPE := preload("res://scenes/etapes/etape_02/etape_02.tscn")
## [vitesse, largeur attendue] (planche du DA, niveau de 16320 px).
const ATTENDU := [[0.05, 2640.0], [0.2, 4800.0], [0.5, 9120.0], [1.0, 16320.0], [1.4, 22080.0]]

var _etape: EtapeBase
var _decor: DecorE2


func before_each() -> void:
	GameState.reinitialiser()
	_etape = ETAPE.instantiate()
	add_child_autofree(_etape)
	await wait_process_frames(2)
	_decor = _etape.get_node("Decors") as DecorE2


func after_all() -> void:
	GameState.reinitialiser()


func _aller(x: float) -> void:
	var messager := _etape.trouver_messager()
	messager.gravite = 0.0
	messager.teleporter(Vector2(x, 880.0))


func test_cinq_plans_aux_bonnes_vitesses_et_largeurs() -> void:
	assert_eq(_decor.plans.size(), 5)
	for i in mini(_decor.plans.size(), ATTENDU.size()):
		var plan := _decor.plans[i]
		assert_almost_eq(plan.scroll_scale.x, float(ATTENDU[i][0]), 0.001, plan.name)
		assert_almost_eq(DecorParallaxe.largeur(plan), float(ATTENDU[i][1]), 1.0, plan.name)
		assert_eq((plan.get_child(0) as Sprite2D).texture.get_height(), 1300, plan.name)


func test_camera_bornee_a_la_surface() -> void:
	var camera := _etape.trouver_messager().get_node("%Camera") as Camera2D
	_aller(3000.0)
	assert_eq(camera.limit_left, 0)
	assert_eq(camera.limit_right, 16320)


func test_brouillard_tout_ou_rien_de_4800_a_10100() -> void:
	assert_eq(_decor.bandes.size(), 3)
	assert_lt(_decor.bandes[0].z_index, _decor.plans[2].z_index, "bande lointaine derrière le plan 2")
	assert_lt(_decor.bandes[1].z_index, _decor.plans[3].z_index, "bande moyenne derrière le jeu")
	assert_gt(_decor.bandes[2].z_index, _decor.plans[3].z_index, "bande proche devant le plan 3")
	assert_lt(_decor.bandes[2].z_index, 0, "mais derrière le messager et les personnages")
	assert_eq(_decor.bandes[2].scroll_scale.x, 1.0, "collée au sol")
	_aller(3000.0)
	await wait_process_frames(3)
	assert_false(_decor.bandes[0].visible, "pas de brouillard avant la ceinture")
	_aller(7000.0)
	await wait_seconds(0.2)
	for bande in _decor.bandes:
		assert_true(bande.visible, bande.name)
		assert_almost_eq(bande.modulate.a, 1.0, 0.001, bande.name)
	_aller(10500.0)
	await wait_seconds(0.3)
	var x := _etape.trouver_messager().global_position.x
	assert_false(_decor.bandes[0].visible, "masqué après la seconde ceinture (messager à x %.0f, alpha %.2f)" % [x, _decor.bandes[0].modulate.a])
	assert_true(_decor.dans_le_brouillard(8256.0), "le mort est dans le brouillard")
	assert_eq(_decor.bornes_brouillard, Vector2(4800, 10100), "bornes lues sur la ZoneSombre")


func test_gris_de_la_maquette_masques() -> void:
	for section in _etape.get_node("Surface").get_children():
		var fond := section.get_node_or_null("Fond") as CanvasItem
		if fond != null:
			assert_false(fond.visible, section.name)
	assert_false((_etape.get_node("Surface/Sol/Visuel") as CanvasItem).visible)
	for chemin: String in DecorE2.GRIS_MAQUETTE:
		assert_false((_etape.get_node(chemin) as CanvasItem).visible, chemin)


func test_cheval_de_frise_part_avec_la_chicane() -> void:
	var chicane := _etape.get_node("Surface/Poste/Chicane") as Verrou
	assert_not_null(_decor.cheval_frise)
	assert_eq(_decor.cheval_frise.get_parent(), chicane)
	assert_false((chicane.get_node("Visuel") as CanvasItem).visible)
	assert_almost_eq(_decor.cheval_frise.global_position.x, DecorE2.X_CHEVAL_FRISE, 0.5)
	assert_almost_eq(_decor.cheval_frise.global_position.y + 110.0, 780.0, 0.5, "posé sur la crête")
	GameState.marquer_rencontre_vue(&"e2_poste_passe")
	await wait_process_frames(2)
	assert_false(chicane.is_visible_in_tree())


func test_le_fil_retombe_derriere_tobie_apres_la_seconde_ceinture() -> void:
	var verrou := _etape.get_node("Surface/Brouillard/FilRetour") as VerrouRetour
	assert_not_null(_decor.fil_retombe)
	assert_eq(_decor.fil_retombe.get_parent(), verrou, "le dessin est posé sur le verrou")
	assert_almost_eq(verrou.global_position.x, 10030.0, 0.5)
	assert_false(verrou.is_visible_in_tree())
	_aller(10300.0)
	await wait_physics_frames(3)
	assert_false(verrou.est_ferme, "ceinture pas encore ouverte : rien ne tombe")
	GameState.marquer_rencontre_vue(&"e2_barbeles_ceinture2")
	_aller(9900.0)
	await wait_physics_frames(3)
	assert_false(verrou.est_ferme, "pas encore franchie")
	_aller(10300.0)
	await wait_physics_frames(3)
	assert_true(verrou.est_ferme)
	assert_true(verrou.is_visible_in_tree())
	assert_false((verrou.get_node("Forme") as CollisionShape2D).disabled, "le retour est fermé")
	_aller(9900.0)
	await wait_physics_frames(3)
	assert_true(verrou.est_ferme, "le fil reste tombé")


func test_sacoche_au_fond_du_grand_trou() -> void:
	assert_not_null(_decor.sacoche)
	assert_almost_eq(_decor.sacoche.global_position.x, 12900.0, 0.5)
	assert_almost_eq(_decor.sacoche.global_position.y + 45.0, 1060.0, 0.5)
