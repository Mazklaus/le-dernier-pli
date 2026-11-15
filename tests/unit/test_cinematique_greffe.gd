extends GutTest
## Cinématique e4_greffe : plan A, noir franc sans texte, plan B, au pas de 1/10 s ; plans
## sous l'écran gravure, masqués après la lecture. Attend les planches de la DA (#166).

const ATELIER := "res://scenes/etapes/etape_04/lieux/atelier.tscn"


func _planches_livrees() -> bool:
	return ResourceLoader.exists("res://assets/graphics/cin/cin_greffe_04.png")


func _cine() -> CinematiquePlans:
	var lieu: Node = add_child_autofree((load(ATELIER) as PackedScene).instantiate())
	return lieu.get_node("e4_greffe") as CinematiquePlans


func test_script_de_plans_sur_le_noeud_du_level_designer() -> void:
	var c := _cine()
	assert_not_null(c)
	if not _planches_livrees():
		assert_null(c.get_node_or_null("Plans"), "sans planche, rien n'est construit")
		return
	var plans := c.get_node("Plans") as CanvasLayer
	assert_lt(plans.layer, EtapeBase.COUCHE_GRAVURE)
	assert_eq(plans.get_child_count(), 3, "plan A, noir, plan B")
	assert_eq(plans.find_children("*", "Label", true, false).size(), 0, "aucun texte")


func test_ordre_des_plans_et_noir_de_six_dixiemes() -> void:
	if not _planches_livrees():
		pass_test("planches de la DA pas encore livrées (#166)")
		return
	var c := _cine()
	var anim := (c.get_node("Animation") as AnimationPlayer).get_animation(&"jouer")
	assert_between(anim.length, 5.0, 15.0)
	var noir := anim.find_track(NodePath("Plans/Noir:visible"), Animation.TYPE_VALUE)
	var debut := anim.track_get_key_time(noir, 1)
	var fin := anim.track_get_key_time(noir, 2)
	assert_true(anim.track_get_key_value(noir, 1), "noir allumé")
	assert_almost_eq(fin - debut, 0.6, 0.001)
	var b := anim.find_track(NodePath("Plans/B:visible"), Animation.TYPE_VALUE)
	assert_almost_eq(anim.track_get_key_time(b, 1), fin, 0.001, "coupe franche vers le plan B")


func test_sautee_les_plans_disparaissent() -> void:
	if not _planches_livrees():
		pass_test("planches de la DA pas encore livrées (#166)")
		return
	GameState.reinitialiser()
	var c := _cine()
	c.jouer()
	assert_true((c.get_node("Plans") as CanvasLayer).visible)
	c.sauter()
	assert_false((c.get_node("Plans") as CanvasLayer).visible)
	GameState.reinitialiser()
