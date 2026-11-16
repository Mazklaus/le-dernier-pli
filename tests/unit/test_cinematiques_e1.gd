extends GutTest
## Cinématiques de l'étape 1 construites depuis les planches de la DA : la remise du pli (deux
## plans plein écran) et la sortie de tranchée (Tobie qui grimpe). Pas de lecture réelle :
## on vérifie l'animation construite et son état final (celui d'un saut).

const ABRI := "res://scenes/etapes/etape_01/lieux/abri_sergent.tscn"
const ETAPE := "res://scenes/etapes/etape_01/etape_01.tscn"

var _attenues := false


func before_each() -> void:
	_attenues = bool(Reglages.valeur(&"effets_attenues"))
	Reglages.changer(&"effets_attenues", false)


func after_each() -> void:
	Reglages.changer(&"effets_attenues", _attenues)


func _cine(scene: String, chemin: String) -> CinematiquePlans:
	var racine: Node = add_child_autofree((load(scene) as PackedScene).instantiate())
	return racine.get_node(chemin) as CinematiquePlans


func _anim(c: Cinematique) -> Animation:
	return (c.get_node("Animation") as AnimationPlayer).get_animation(Cinematique.ANIMATION_PAR_DEFAUT)


func test_remise_du_pli_deux_plans_plein_ecran() -> void:
	var c := _cine(ABRI, "e1_remise_pli")
	assert_not_null(c, "script de plans sur le nœud du Level Designer")
	var anim := _anim(c)
	assert_not_null(anim)
	assert_between(anim.length, 5.0, 15.0)
	var plans := c.get_node("Plans") as CanvasLayer
	assert_false(plans.visible, "masqués hors de la cinématique")
	assert_lt(plans.layer, EtapeBase.COUCHE_GRAVURE, "sous l'écran gravure (même papier que le jeu)")
	assert_eq((c.get_node("Plans/A/Geste") as Sprite2D).hframes * (c.get_node("Plans/A/Geste") as Sprite2D).vframes, 6)
	assert_eq((c.get_node("Plans/B/Geste") as Sprite2D).position, Vector2(300, 300))


func test_remise_du_pli_clefs_au_pas_de_10_images_par_seconde() -> void:
	var anim := _anim(_cine(ABRI, "e1_remise_pli"))
	for piste in anim.get_track_count():
		for k in anim.track_get_key_count(piste):
			var t := anim.track_get_key_time(piste, k)
			assert_almost_eq(fmod(t + 0.0001, Cinematique.PAS), 0.0, 0.001, "clé à %.3f s" % t)


func test_remise_du_pli_sautee_les_plans_disparaissent() -> void:
	var c := _cine(ABRI, "e1_remise_pli")
	GameState.reinitialiser()
	c.jouer()
	assert_true(c.en_cours)
	assert_true((c.get_node("Plans") as CanvasLayer).visible)
	c.sauter()
	assert_false((c.get_node("Plans") as CanvasLayer).visible)
	assert_true(c.deja_vue())
	GameState.reinitialiser()


func test_sortie_la_camera_suit_la_montee_puis_le_parapet_et_lamarre() -> void:
	var c := _cine(ETAPE, "Surface/PiedEchelle/e1_sortie_tranchee")
	assert_not_null(c)
	var anim := _anim(c)
	assert_between(anim.length, 5.0, 6.0, "entre 5 et 6 s (GD)")
	var piste := anim.find_track(NodePath("Grimpeur:position"), Animation.TYPE_VALUE)
	assert_ne(piste, -1)
	var cam := anim.find_track(NodePath("Camera:position"), Animation.TYPE_VALUE)
	assert_gt(anim.track_get_key_count(cam), 10, "la caméra suit Tobie vers le haut")
	var haut: Vector2 = anim.track_get_key_value(cam, anim.track_get_key_count(cam) - 1)
	var zoom: Vector2 = anim.track_get_key_value(anim.find_track(NodePath("Camera:zoom"), Animation.TYPE_VALUE), 0)
	var bas: Vector2 = anim.track_get_key_value(cam, 0)
	var demi := Vector2(960.0, 540.0) / zoom
	assert_gte(haut.y - demi.y, 0.0, "la vue ne sort jamais du décor peint par le haut")
	assert_lte(bas.y + demi.y, 1080.0, "ni par le bas")
	assert_lte(bas.x + demi.x, 1330.0, "ni à droite, où finit la tranchée")
	assert_eq((c.get_node("Plans/B/Tobie") as Sprite2D).hframes * (c.get_node("Plans/B/Tobie") as Sprite2D).vframes, 4)
	assert_eq((c.get_node("Plans/C/Lamarre") as Sprite2D).hframes, 2)
	var lamarre := anim.find_track(NodePath("Plans/C/Lamarre:frame"), Animation.TYPE_VALUE)
	assert_eq(anim.track_get_key_value(lamarre, anim.track_get_key_count(lamarre) - 1), 1, "il baisse la tête")
	assert_ne(anim.find_track(NodePath("/root/AudioDirector"), Animation.TYPE_METHOD), -1, "l'échelle sonne")


func test_sortie_effets_attenues_deux_plans_fixes() -> void:
	Reglages.changer(&"effets_attenues", true)
	var anim := _anim(_cine(ETAPE, "Surface/PiedEchelle/e1_sortie_tranchee"))
	var cam := anim.find_track(NodePath("Camera:position"), Animation.TYPE_VALUE)
	assert_eq(anim.track_get_key_count(cam), 1, "la caméra ne bouge pas : l'échelle, puis le parapet")
	assert_ne(anim.find_track(NodePath("Plans/B:visible"), Animation.TYPE_VALUE), -1)


func test_sortie_clefs_au_pas_de_10_images_par_seconde() -> void:
	var anim := _anim(_cine(ETAPE, "Surface/PiedEchelle/e1_sortie_tranchee"))
	for piste in anim.get_track_count():
		for k in anim.track_get_key_count(piste):
			var t := anim.track_get_key_time(piste, k)
			assert_almost_eq(fmod(t + 0.0001, Cinematique.PAS), 0.0, 0.001, "clé à %.3f s" % t)


func test_sortie_masque_le_messager() -> void:
	var etape: EtapeBase = add_child_autofree((load(ETAPE) as PackedScene).instantiate())
	var c := etape.get_node("Surface/PiedEchelle/e1_sortie_tranchee") as CinematiquePlans
	var messager := get_tree().get_first_node_in_group(Messager.GROUPE) as Messager
	if messager == null:
		pass_test("pas de messager dans l'étape instanciée seule")
		return
	GameState.reinitialiser()
	c.jouer()
	assert_false(messager.visible)
	c.sauter()
	assert_false(c.grimpeur.visible)
	assert_false(c.couche.visible)
	GameState.reinitialiser()
