extends GutTest
## Ciné e6_eboulement construite depuis les planches de la DA (tools/gen_cin_e6_eboulement.py) :
## un plan plein écran, 8 images de la voûte qui cède, environ 6 s, sans mouvement de caméra.

const VILLAGE := "res://scenes/etapes/etape_06/lieux/village.tscn"


func _cine() -> CinematiquePlans:
	var racine: Node = add_child_autofree((load(VILLAGE) as PackedScene).instantiate())
	return racine.get_node("e6_eboulement") as CinematiquePlans


func _anim(c: Cinematique) -> Animation:
	return (c.get_node("Animation") as AnimationPlayer).get_animation(Cinematique.ANIMATION_PAR_DEFAUT)


func test_un_plan_plein_ecran_de_huit_images() -> void:
	var c := _cine()
	assert_not_null(c, "script de plans sur le nœud du Level Designer")
	var anim := _anim(c)
	assert_not_null(anim)
	assert_between(anim.length, 5.5, 7.0, "une vraie ciné d'environ 6 s (GD)")
	var plans := c.get_node("Plans") as CanvasLayer
	assert_false(plans.visible, "masqué hors de la cinématique")
	assert_lt(plans.layer, EtapeBase.COUCHE_GRAVURE, "sous l'écran gravure (même papier, même inversion)")
	var voute := c.get_node("Plans/Voute") as Sprite2D
	assert_eq(voute.hframes * voute.vframes, 9)
	var piste := anim.find_track(NodePath("Plans/Voute:frame"), Animation.TYPE_VALUE)
	assert_eq(anim.track_get_key_count(piste), 8)
	assert_eq(anim.track_get_key_value(piste, 7), 7, "finit sur l'éboulis")


func test_la_taille_des_images_colle_a_la_zone() -> void:
	var c := _cine()
	var voute := c.get_node("Plans/Voute") as Sprite2D
	var image := Vector2(voute.texture.get_size()) / Vector2(voute.hframes, voute.vframes) * voute.scale
	assert_almost_eq(image.x, 1100.0, 2.0)
	assert_almost_eq(image.y, 820.0, 2.0)
	assert_eq((c.get_node("Plans/Fond") as Sprite2D).texture.get_size(), Vector2(1920, 1080))


func test_pas_de_camera_qui_bouge_et_la_voute_sonne() -> void:
	var anim := _anim(_cine())
	for i in anim.get_track_count():
		assert_false(String(anim.track_get_path(i)).begins_with("Camera"), "aucune piste de caméra")
	assert_ne(anim.find_track(NodePath("/root/AudioDirector"), Animation.TYPE_METHOD), -1)


func test_clefs_au_pas_de_10_images_par_seconde() -> void:
	var anim := _anim(_cine())
	for piste in anim.get_track_count():
		for k in anim.track_get_key_count(piste):
			var t := anim.track_get_key_time(piste, k)
			assert_almost_eq(fmod(t + 0.0001, Cinematique.PAS), 0.0, 0.001, "clé à %.3f s" % t)


func test_sautee_le_plan_disparait() -> void:
	var c := _cine()
	GameState.reinitialiser()
	c.jouer()
	assert_true((c.get_node("Plans") as CanvasLayer).visible)
	c.sauter()
	assert_false((c.get_node("Plans") as CanvasLayer).visible)
	GameState.reinitialiser()
