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
	var autre := c.get_node("Plans/Autre") as Sprite2D
	assert_eq(autre.hframes * autre.vframes, 6)
	assert_eq(autre.position, Vector2(880, 500))


func test_les_six_images_dans_l_ordre_avec_les_tenues() -> void:
	if not _planches_livrees():
		pass_test("planches de la DA pas encore livrées (#174)")
		return
	var anim := (_cine().get_node("Animation") as AnimationPlayer).get_animation(&"jouer")
	var piste := anim.find_track(NodePath("Plans/Autre:frame"), Animation.TYPE_VALUE)
	var images: Array = []
	for k in anim.track_get_key_count(piste):
		images.append(anim.track_get_key_value(piste, k))
	assert_eq(images, [0, 1, 2, 3, 4, 5])
	var tenue_tete := anim.track_get_key_time(piste, 4) - anim.track_get_key_time(piste, 3)
	assert_almost_eq(tenue_tete, 0.8, 0.001, "la tête tournée tient 0,8 s")
	assert_almost_eq(anim.length - anim.track_get_key_time(piste, 5), 1.0, 0.001, "une seconde sur la dernière")
