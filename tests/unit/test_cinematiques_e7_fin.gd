extends GutTest
## Cinématiques de fin de l'étape 7 (planche « Le Dernier Pli », tools/gen_cin_e7_fin.py) :
## e7_moule_brise et e7_corde_tiree, construites en code. Le Gameplay Prog les place dans la salle
## de la Mère-Cloche ; ici on construit les nœuds seuls et on vérifie l'animation.

const MOULE := "res://scripts/cinematique/plans/cin_e7_moule_brise.gd"
const CORDE := "res://scripts/cinematique/plans/cin_e7_corde_tiree.gd"


func _cine(script: String, id: StringName) -> CinematiquePlans:
	var c := Node2D.new()
	c.set_script(load(script))
	c.set("id", id)
	var camera := Camera2D.new()
	camera.name = "Camera"
	c.add_child(camera)
	add_child_autofree(c)
	return c as CinematiquePlans


func _anim(c: Cinematique) -> Animation:
	return (c.get_node("Animation") as AnimationPlayer).get_animation(Cinematique.ANIMATION_PAR_DEFAUT)


func _au_pas(anim: Animation) -> void:
	for piste in anim.get_track_count():
		for k in anim.track_get_key_count(piste):
			var t := anim.track_get_key_time(piste, k)
			assert_almost_eq(fmod(t + 0.0001, Cinematique.PAS), 0.0, 0.001, "clé à %.3f s" % t)


func test_moule_six_images_qui_finissent_figees() -> void:
	var c := _cine(MOULE, &"e7_moule_brise")
	var anim := _anim(c)
	assert_almost_eq(anim.length, 8.0, 0.05, "8 s (planche validée)")
	var moule := c.get_node("Plans/Moule") as Sprite2D
	assert_eq(moule.hframes * moule.vframes, 6)
	var piste := anim.find_track(NodePath("Plans/Moule:frame"), Animation.TYPE_VALUE)
	assert_eq(anim.track_get_key_value(piste, anim.track_get_key_count(piste) - 1), 5, "la cire figée")
	assert_ne(anim.find_track(NodePath("/root/AudioDirector"), Animation.TYPE_METHOD), -1, "le fer qui se fend")
	_au_pas(anim)


func test_corde_la_main_tire_puis_noir_avant_le_son() -> void:
	var c := _cine(CORDE, &"e7_corde_tiree")
	var anim := _anim(c)
	assert_almost_eq(anim.length, 6.0, 0.05)
	var prise := anim.find_track(NodePath("Plans/Prise:position"), Animation.TYPE_VALUE)
	var debut: Vector2 = anim.track_get_key_value(prise, 0)
	var fin: Vector2 = anim.track_get_key_value(prise, anim.track_get_key_count(prise) - 1)
	assert_gt(fin.y, debut.y, "la corde descend : il tire")
	assert_lt(fin.x, debut.x, "le long de la corde, vers le bas à gauche")
	var noir := anim.find_track(NodePath("Plans/Noir:visible"), Animation.TYPE_VALUE)
	assert_true(anim.track_get_key_value(noir, anim.track_get_key_count(noir) - 1), "on finit au noir")
	assert_lt(anim.track_get_key_time(noir, anim.track_get_key_count(noir) - 1), anim.length - 1.0, "un noir tenu, silencieux")
	# aucun son de cloche : seulement la corde
	var sons := anim.find_track(NodePath("/root/AudioDirector"), Animation.TYPE_METHOD)
	for k in anim.track_get_key_count(sons):
		var nom: String = anim.track_get_key_value(sons, k)["args"][0]
		assert_false(nom.contains("cloche"), "pas de cloche avant l'épilogue (%s)" % nom)
	_au_pas(anim)


func test_aucune_piste_de_camera() -> void:
	for s in [[MOULE, &"e7_moule_brise"], [CORDE, &"e7_corde_tiree"]]:
		var anim := _anim(_cine(s[0], s[1]))
		for i in anim.get_track_count():
			assert_false(String(anim.track_get_path(i)).begins_with("Camera"))
