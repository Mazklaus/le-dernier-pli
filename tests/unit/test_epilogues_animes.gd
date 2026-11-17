extends GutTest
## Épilogues animés de la DA (scripts/epilogue/anim_epilogue_<lettre>.gd) : l'interface attendue
## par epilogue.gd (Control plein écran, temps_lignes, duree, jouer, passer, finie), et les planches.

const LETTRES := ["a", "b", "c", "d"]

var _attenues := false


func before_each() -> void:
	_attenues = bool(Reglages.valeur(&"effets_attenues"))
	Reglages.changer(&"effets_attenues", false)


func after_each() -> void:
	Reglages.changer(&"effets_attenues", _attenues)


func _anim(lettre: String) -> AnimationEpilogue:
	var n := (load("res://scripts/epilogue/anim_epilogue_%s.gd" % lettre) as GDScript).new() as AnimationEpilogue
	add_child_autofree(n)
	return n


func _animation(a: AnimationEpilogue) -> Animation:
	return (a.get_node("Animation") as AnimationPlayer).get_animation(AnimationEpilogue.NOM_ANIMATION)


func test_interface_et_duree() -> void:
	for l: String in LETTRES:
		var a := _anim(l)
		assert_eq(a.mouse_filter, Control.MOUSE_FILTER_IGNORE, l)
		assert_between(a.duree, 25.0, 40.0, "%s : 25 à 40 s (GD)" % l)
		assert_eq(a.temps_lignes.size(), 4, "%s : une ligne par plan" % l)
		for i in range(1, a.temps_lignes.size()):
			assert_gt(a.temps_lignes[i], a.temps_lignes[i - 1])
		assert_lt(a.temps_lignes[a.temps_lignes.size() - 1], a.duree)
		assert_true(a.has_signal(&"finie"))


func test_clefs_au_pas_de_10_images_par_seconde() -> void:
	for l: String in LETTRES:
		var anim := _animation(_anim(l))
		for piste in anim.get_track_count():
			for k in anim.track_get_key_count(piste):
				var t := anim.track_get_key_time(piste, k)
				assert_almost_eq(fmod(t + 0.0001, AnimationEpilogue.PAS), 0.0, 0.001, "%s : clé à %.3f s" % [l, t])


func test_un_seul_plan_a_la_fois() -> void:
	for l: String in LETTRES:
		var a := _anim(l)
		var anim := _animation(a)
		var lecteur := a.get_node("Animation") as AnimationPlayer
		for t in [1.0, 9.0, 17.0, 20.0, 27.0, 31.0]:
			lecteur.seek(t, true)
			var vus := 0
			for p in a.cadre.get_children():
				if (p as CanvasItem).visible:
					vus += 1
			assert_eq(vus, 1, "%s à %.0f s" % [l, t])
		assert_ne(anim, null)


func test_passer_saute_a_la_fin_et_emet_finie() -> void:
	var a := _anim("b")
	watch_signals(a)
	a.jouer()
	a.passer()
	assert_signal_emitted(a, "finie")
	assert_almost_eq((a.get_node("Animation") as AnimationPlayer).current_animation_position, a.duree, 0.01)


func test_cloches_la_grande_cloche_se_balance_sur_les_chocs() -> void:
	var anim := _animation(_anim("c"))
	var piste := anim.find_track(NodePath("Cadre/P1/Grande:rotation_degrees"), Animation.TYPE_VALUE)
	assert_ne(piste, -1, "la grande cloche bouge (décision du GD)")
	# au choc de 0,0 s et de 1,8 s (grille du Sound Designer), elle est à une extrémité
	assert_ne(anim.value_track_interpolate(piste, 0.0), 0.0)
	assert_ne(anim.value_track_interpolate(piste, 1.8), 0.0)
	assert_eq(signf(anim.value_track_interpolate(piste, 0.0)), -signf(anim.value_track_interpolate(piste, 1.8)))


func test_effets_attenues_pas_de_glissement_de_camera() -> void:
	Reglages.changer(&"effets_attenues", true)
	var anim := _animation(_anim("b"))
	var piste := anim.find_track(NodePath("Cadre/P2/Abri:position"), Animation.TYPE_VALUE)
	assert_eq(anim.track_get_key_count(piste), 2, "deux plans fixes au lieu d'un panoramique")


func test_la_corde_tire_au_plus_bas_sur_chaque_coup_de_la_piste() -> void:
	var c: GDScript = load("res://scripts/epilogue/anim_epilogue_c.gd")
	for t: float in [18.0, 19.9, 22.0, 24.4]:
		assert_almost_eq(c.tirage(t), 1.0, 0.001, "coup à %.1f s" % t)
	assert_lt(c.tirage(18.95), -0.99, "au plus haut entre deux coups")
