extends GutTest
## Cinématique e5_autre_se_retourne : un plan, l'Autre s'arrête, tourne la tête à moitié,
## repart ; au pas de 1/10 s, sous la gravure. Attend les planches de la DA (#174).

const ETAPE := "res://scenes/etapes/etape_05/etape_05.tscn"


func _planches_livrees() -> bool:
	return ResourceLoader.exists("res://assets/graphics/cin/cin_autre_02.png")


func _cine() -> CinematiquePlans:
	var etape: Node = add_child_autofree((load(ETAPE) as PackedScene).instantiate())
	return etape.get_node("Surface/Boucle/e5_autre_se_retourne") as CinematiquePlans


func test_script_de_plans_sur_le_noeud_du_level_designer() -> void:
	var c := _cine()
	assert_not_null(c)
	if not _planches_livrees():
		assert_null(c.get_node_or_null("Plans"), "sans planche, rien n'est construit")
		return
	assert_lt((c.get_node("Plans") as CanvasLayer).layer, EtapeBase.COUCHE_GRAVURE)
	var autre := c.get_node("Plans/Cadre/Autre") as Sprite2D
	assert_eq(autre.hframes * autre.vframes, 6)
	assert_eq(autre.position, Vector2(880, 500))
	assert_eq(autre.scale, Vector2(0.5, 0.5), "planches rendues au double")
	assert_not_null(c.get_node_or_null("Plans/Brume"), "la brume qui dérive")


func test_il_marche_sur_place_s_arrete_tourne_la_tete_et_repart() -> void:
	if not _planches_livrees():
		pass_test("planches de la DA pas encore livrées (#174)")
		return
	var anim := (_cine().get_node("Animation") as AnimationPlayer).get_animation(&"jouer")
	var piste := anim.find_track(NodePath("Plans/Cadre/Autre:frame"), Animation.TYPE_VALUE)
	var images: Array = []
	var temps: Array = []
	for k in anim.track_get_key_count(piste):
		images.append(anim.track_get_key_value(piste, k))
		temps.append(roundi(anim.track_get_key_time(piste, k) * 10.0))  # en dixièmes
	# deux images pour tourner (2, 3), la tête tenue 1,2 s, deux pour revenir (4, 1)
	assert_eq(images, [0, 5, 0, 5, 0, 5, 1, 2, 3, 4, 1, 0, 5, 0, 5, 0, 5])
	assert_eq(temps, [0, 3, 7, 10, 13, 17, 20, 21, 22, 34, 35, 36, 39, 43, 46, 49, 53])
	assert_almost_eq(anim.length, 6.1, 0.001, "dans la fourchette 5 à 15 s")


func test_le_sprite_ne_bouge_jamais() -> void:
	if not _planches_livrees():
		pass_test("planches de la DA pas encore livrées (#174)")
		return
	var anim := (_cine().get_node("Animation") as AnimationPlayer).get_animation(&"jouer")
	assert_eq(anim.find_track(NodePath("Plans/Cadre/Autre:position"), Animation.TYPE_VALUE), -1)


func test_la_camera_pousse_vers_l_autre_sans_qu_il_bouge() -> void:
	if not _planches_livrees():
		pass_test("planches de la DA pas encore livrées (#174)")
		return
	var anim := (_cine().get_node("Animation") as AnimationPlayer).get_animation(&"jouer")
	var piste := anim.find_track(NodePath("Plans/Cadre:scale"), Animation.TYPE_VALUE)
	assert_ne(piste, -1)
	var n := anim.track_get_key_count(piste)
	assert_gt(n, 50, "une clé tous les dixièmes : un mouvement continu")
	assert_eq(anim.track_get_key_value(piste, 0), Vector2.ONE)
	assert_almost_eq((anim.track_get_key_value(piste, n - 1) as Vector2).x, 2.5, 0.01)
	var brume := anim.find_track(NodePath("Plans/Brume:position"), Animation.TYPE_VALUE)
	assert_ne(brume, -1, "la brume dérive")
