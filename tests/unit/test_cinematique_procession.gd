extends GutTest
## Cinématique e3_procession_nuit : trois calques (rue, file, volet), la file marche vers la
## droite au pas de 1/10 s, et l'écran gravure prend la teinte du chemin de nuit le temps de
## la cinématique. Les tests attendent les planches de la DA (#152).

const ETAPE := "res://scenes/etapes/etape_03/etape_03.tscn"


func _planches_livrees() -> bool:
	return ResourceLoader.exists("res://assets/graphics/cin/cin_procession-nuit_01.png") \
		and ResourceLoader.exists("res://assets/graphics/chr/chr_ilde-cierge_marche_01.png")


func _cine(etape: Node) -> CinematiquePlans:
	for n in etape.find_children("e3_procession_nuit", "Node2D", true, false):
		return n as CinematiquePlans
	return null


func test_script_de_plans_sur_le_noeud_du_level_designer() -> void:
	var etape: Node = add_child_autofree((load(ETAPE) as PackedScene).instantiate())
	var c := _cine(etape)
	assert_not_null(c)
	if not _planches_livrees():
		assert_null(c.get_node_or_null("Plans"), "sans planche, rien n'est construit")
		return
	var plans := c.get_node("Plans") as CanvasLayer
	assert_lt(plans.layer, EtapeBase.COUCHE_GRAVURE)
	assert_eq(plans.get_child(0).name, &"Rue", "la rue derrière")
	assert_eq(plans.get_child(plans.get_child_count() - 1).name, &"Volet", "le volet devant")
	assert_eq(c.marcheurs.size(), 6, "Ilde et cinq silhouettes")


func test_la_file_avance_vers_la_droite() -> void:
	if not _planches_livrees():
		pass_test("planches de la DA pas encore livrées (#152)")
		return
	var etape: Node = add_child_autofree((load(ETAPE) as PackedScene).instantiate())
	var c := _cine(etape)
	var anim := (c.get_node("Animation") as AnimationPlayer).get_animation(&"jouer")
	assert_between(anim.length, 8.0, 12.0)
	var piste := anim.find_track(NodePath("Plans/Marcheur0:position"), Animation.TYPE_VALUE)
	var debut: Vector2 = anim.track_get_key_value(piste, 0)
	var fin: Vector2 = anim.track_get_key_value(piste, anim.track_get_key_count(piste) - 1)
	assert_gt(fin.x, 1560.0, "Ilde sort de l'embrasure à droite")
	assert_lt(debut.x, 360.0, "et y entre par la gauche")
	assert_eq(debut.y, 820.0)


func test_teinte_du_chemin_de_nuit_puis_retour() -> void:
	if not _planches_livrees():
		pass_test("planches de la DA pas encore livrées (#152)")
		return
	GameState.reinitialiser()
	var etape: EtapeBase = add_child_autofree((load(ETAPE) as PackedScene).instantiate())
	etape.definir_teinte(Color(0.32, 0.35, 0.48))
	var c := _cine(etape)
	c.jouer()
	assert_eq(etape.teinte_actuelle(), Color(0.85, 0.88, 1.0))
	c.sauter()
	assert_eq(etape.teinte_actuelle(), Color(0.32, 0.35, 0.48))
	assert_false((c.get_node("Plans") as CanvasLayer).visible)
	GameState.reinitialiser()


func test_aucun_marcheur_hors_des_lames_du_volet() -> void:
	if not _planches_livrees():
		pass_test("planches de la DA pas encore livrées (#152)")
		return
	var etape: Node = add_child_autofree((load(ETAPE) as PackedScene).instantiate())
	var c := _cine(etape)
	var anim := (c.get_node("Animation") as AnimationPlayer).get_animation(&"jouer")
	var demi: float = SilhouetteTobie.PIEDS.x * c.ECHELLE
	for i in c.marcheurs.size():
		var chemin := "Plans/Marcheur%d" % i
		var pos := anim.find_track(NodePath(chemin + ":position"), Animation.TYPE_VALUE)
		var vis := anim.find_track(NodePath(chemin + ":visible"), Animation.TYPE_VALUE)
		assert_ne(vis, -1, chemin)
		for k in anim.track_get_key_count(pos):
			var t := anim.track_get_key_time(pos, k)
			var x: float = (anim.track_get_key_value(pos, k) as Vector2).x
			var visible: bool = anim.value_track_interpolate(vis, t)
			if visible:
				assert_true(x + demi > c.EMBRASURE.x and x - demi < c.EMBRASURE.y,
					"%s visible hors des lames à %.1f s (écran plus large que 16:9)" % [chemin, t])
	var piste := anim.find_track(NodePath("Plans/Marcheur0:visible"), Animation.TYPE_VALUE)
	assert_false(anim.track_get_key_value(piste, anim.track_get_key_count(piste) - 1), "Ilde finit derrière le mur")
