extends GutTest
## Cinématiques de l'étape 7, planches de la DA (#187) : e7_descente (quatre plans, pan du plan 2,
## Tobie entre fond et avant-plan) et e7_ouverture_sceau (un gros plan, dix images).

const CLOCHES := "res://scenes/etapes/etape_07/lieux/anneau_cloches.tscn"
const PORTE := "res://scenes/etapes/etape_07/lieux/anneau_porte.tscn"


func _planches_livrees() -> bool:
	return ResourceLoader.exists("res://assets/graphics/cin/cin_descente_06.png") \
		and ResourceLoader.exists("res://assets/graphics/cin/cin_sceau_02.png")


func _cine(scene: String, id: String) -> CinematiquePlans:
	var lieu: Node = add_child_autofree((load(scene) as PackedScene).instantiate())
	return lieu.get_node(id) as CinematiquePlans


func _anim(c: CinematiquePlans) -> Animation:
	return (c.get_node("Animation") as AnimationPlayer).get_animation(&"jouer")


func _cles(anim: Animation, chemin: String) -> Array:
	var piste := anim.find_track(NodePath(chemin), Animation.TYPE_VALUE)
	assert_ne(piste, -1, chemin)
	var v: Array = []
	for k in anim.track_get_key_count(piste):
		v.append([roundi(anim.track_get_key_time(piste, k) * 10.0), anim.track_get_key_value(piste, k)])
	return v


func _valeur_a(anim: Animation, chemin: String, dixiemes: int) -> Variant:
	var valeur: Variant = null
	for c: Array in _cles(anim, chemin):
		if c[0] <= dixiemes:
			valeur = c[1]
	return valeur


func test_scripts_de_plans_sur_les_noeuds_du_level_designer() -> void:
	var descente := _cine(CLOCHES, "e7_descente")
	var sceau := _cine(PORTE, "e7_ouverture_sceau")
	assert_not_null(descente)
	assert_not_null(sceau)
	if not _planches_livrees():
		pass_test("planches de la DA pas encore livrées (#187)")
		return
	for c in [descente, sceau]:
		assert_lt((c.get_node("Plans") as CanvasLayer).layer, EtapeBase.COUCHE_GRAVURE)


func test_le_sceau_dix_images_en_huit_secondes() -> void:
	if not _planches_livrees():
		pass_test("planches de la DA pas encore livrées (#187)")
		return
	var c := _cine(PORTE, "e7_ouverture_sceau")
	var s := c.get_node("Plans/Sceau") as Sprite2D
	assert_eq([s.hframes, s.vframes], [3, 4])
	assert_eq(s.position, Vector2(300, 140))
	var anim := _anim(c)
	assert_almost_eq(anim.length, 8.0, 0.001)
	assert_eq(_cles(anim, "Plans/Sceau:frame"),
		[[0, 0], [15, 1], [23, 2], [26, 3], [29, 4], [32, 5], [36, 6], [44, 7], [52, 8], [55, 9]])


func test_la_descente_quatre_plans_un_seul_visible() -> void:
	if not _planches_livrees():
		pass_test("planches de la DA pas encore livrées (#187)")
		return
	var anim := _anim(_cine(CLOCHES, "e7_descente"))
	assert_almost_eq(anim.length, 10.0, 0.001)
	for instant: int in [0, 23, 24, 53, 54, 73, 74, 99]:
		var visibles: Array = []
		for p in [1, 2, 3, 4]:
			if _valeur_a(anim, "Plans/P%d:visible" % p, instant):
				visibles.append(p)
		var attendu := 1 if instant < 24 else 2 if instant < 54 else 3 if instant < 74 else 4
		assert_eq(visibles, [attendu], "à %d dixièmes" % instant)


func test_le_pan_du_plan_2() -> void:
	if not _planches_livrees():
		pass_test("planches de la DA pas encore livrées (#187)")
		return
	var anim := _anim(_cine(CLOCHES, "e7_descente"))
	assert_eq(_valeur_a(anim, "Plans/P2/Fond:position", 24), Vector2.ZERO)
	assert_eq(_valeur_a(anim, "Plans/P2/Fond:position", 25), Vector2.ZERO)
	assert_eq(_valeur_a(anim, "Plans/P2/Fond:position", 38), Vector2(0, -205))
	assert_eq(_valeur_a(anim, "Plans/P2/Fond:position", 51), Vector2(0, -410))
	assert_eq(_valeur_a(anim, "Plans/P2/AvantPlan:position", 51), Vector2(0, -820))
	assert_eq(_cles(anim, "Plans/P2/Fond:position").size(), 28, "une clé par pas de 0,1 à 2,7 s")


func test_tobie_par_ses_pieds_entre_fond_et_avant_plan() -> void:
	if not _planches_livrees():
		pass_test("planches de la DA pas encore livrées (#187)")
		return
	var c := _cine(CLOCHES, "e7_descente")
	var t1 := c.get_node("Plans/P1/Tobie") as Sprite2D
	assert_eq(t1.offset, Vector2(-60, -196))
	assert_eq(t1.scale, Vector2(0.55, 0.55))
	assert_false(t1.flip_h, "de profil vers la droite, sans retournement")
	var t2 := c.get_node("Plans/P2/Fond/Tobie") as Sprite2D
	assert_eq(t2.scale, Vector2.ONE)
	assert_lt(c.get_node("Plans/P2/Fond").get_index(), c.get_node("Plans/P2/AvantPlan").get_index())
	assert_eq((c.get_node("Plans/P4/Tobie") as Sprite2D).scale, Vector2(0.35, 0.35))
	var anim := _anim(c)
	assert_eq(_cles(anim, "Plans/P1/Tobie:visible").front(), [0, false])
	assert_eq(_valeur_a(anim, "Plans/P1/Tobie:visible", 6), true)
	assert_eq(_valeur_a(anim, "Plans/P1/Tobie:visible", 22), false, "caché derrière la grande cloche")
	assert_eq(_valeur_a(anim, "Plans/P1/Tobie:position", 6), Vector2(980, 400))
	assert_eq(_valeur_a(anim, "Plans/P2/Fond/Tobie:position", 51), Vector2(1612, 970))
	assert_eq(_valeur_a(anim, "Plans/P2/Fond/Tobie:frame", 51), 1)
	assert_eq(_valeur_a(anim, "Plans/P4/Tobie:position", 99), Vector2(1209, 677))
	assert_eq(_cles(anim, "Plans/P4/Tobie:frame").size(), 12)
