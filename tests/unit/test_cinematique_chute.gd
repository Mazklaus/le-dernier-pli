extends GutTest
## Cinématique e6_chute_fissure : plan A (la fente s'ouvre), plan B (Tobie dévale le chemin de la
## DA, posé par son centre), au pas de 1/10 s, sous la gravure. Planches de la DA (#179).

const NEF := "res://scenes/etapes/etape_06/lieux/nef.tscn"


func _planches_livrees() -> bool:
	return ResourceLoader.exists("res://assets/graphics/cin/cin_chute_04.png")


func _cine() -> CinematiquePlans:
	var lieu: Node = add_child_autofree((load(NEF) as PackedScene).instantiate())
	return lieu.get_node("e6_chute_fissure") as CinematiquePlans


func _anim() -> Animation:
	return (_cine().get_node("Animation") as AnimationPlayer).get_animation(&"jouer")


func _valeurs(anim: Animation, chemin: String) -> Array:
	var piste := anim.find_track(NodePath(chemin), Animation.TYPE_VALUE)
	var v: Array = []
	for k in anim.track_get_key_count(piste):
		v.append(anim.track_get_key_value(piste, k))
	return v


func _dixiemes(anim: Animation, chemin: String) -> Array:
	var piste := anim.find_track(NodePath(chemin), Animation.TYPE_VALUE)
	var v: Array = []
	for k in anim.track_get_key_count(piste):
		v.append(roundi(anim.track_get_key_time(piste, k) * 10.0))
	return v


func test_script_de_plans_sur_le_noeud_du_level_designer() -> void:
	var c := _cine()
	assert_not_null(c)
	if not _planches_livrees():
		assert_null(c.get_node_or_null("Plans"), "sans planche, rien n'est construit")
		return
	var plans := c.get_node("Plans") as CanvasLayer
	assert_lt(plans.layer, EtapeBase.COUCHE_GRAVURE)
	assert_eq(plans.get_child_count(), 2, "plan A, plan B")
	var fente := c.get_node("Plans/A/Fente") as Sprite2D
	assert_eq([fente.hframes, fente.vframes], [3, 2])
	assert_eq(fente.position, Vector2(660, 300))
	var tobie := c.get_node("Plans/B/Tobie") as Sprite2D
	assert_eq([tobie.hframes, tobie.vframes], [6, 1])
	assert_eq(tobie.position, Vector2(210, 70), "centre (330, 190) au départ")


func test_plan_a_puis_plan_b() -> void:
	if not _planches_livrees():
		pass_test("planches de la DA pas encore livrées (#179)")
		return
	var anim := _anim()
	assert_eq(_valeurs(anim, "Plans/A/Fente:frame"), [0, 1, 2, 3, 4, 5])
	assert_eq(_dixiemes(anim, "Plans/A/Fente:frame"), [0, 6, 7, 8, 9, 10])
	assert_eq(_dixiemes(anim, "Plans/B:visible"), [0, 16])
	assert_eq(_valeurs(anim, "Plans/B:visible"), [false, true])
	assert_eq(_dixiemes(anim, "Plans/A:visible"), [0, 16])
	assert_almost_eq(anim.length, 5.2, 0.001)
	assert_between(anim.length, 5.0, 15.0)


func test_tobie_suit_le_chemin_par_son_centre() -> void:
	if not _planches_livrees():
		pass_test("planches de la DA pas encore livrées (#179)")
		return
	var anim := _anim()
	assert_eq(_valeurs(anim, "Plans/B/Tobie:frame"), [0, 0, 1, 2, 3, 1, 2, 3, 1, 2, 3, 4, 5])
	assert_eq(_dixiemes(anim, "Plans/B/Tobie:frame"),
		[16, 19, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42])
	var positions := _valeurs(anim, "Plans/B/Tobie:position")
	assert_eq(positions.size(), 13)
	assert_eq(positions[-1], Vector2(1380, 660), "centre (1500, 780) à l'arrivée")
	var piste := anim.find_track(NodePath("Plans/B/Tobie:position"), Animation.TYPE_VALUE)
	assert_eq(anim.value_track_get_update_mode(piste), Animation.UPDATE_DISCRETE, "pas de glissé")


func test_le_sol_cede_quand_la_fente_s_ouvre() -> void:
	if not _planches_livrees():
		pass_test("planches de la DA pas encore livrées (#179)")
		return
	var anim := _anim()
	var piste := anim.find_track(NodePath("/root/AudioDirector"), Animation.TYPE_METHOD)
	assert_ne(piste, -1)
	assert_eq(anim.track_get_key_count(piste), 1)
	assert_almost_eq(anim.track_get_key_time(piste, 0), 0.6, 0.001)
	assert_eq(anim.method_track_get_params(piste, 0), ["sfx_sol_ceder"])
