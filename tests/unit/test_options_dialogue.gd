extends GutTest
## Convention des tags de dialogue : coûts, options cachées, bavure, timbres.


func before_each() -> void:
	GameState.reinitialiser()


func after_all() -> void:
	GameState.reinitialiser()


func _o(texte: String, tags: Array, autorisee: bool = true) -> Dictionary:
	return {"texte": texte, "tags": PackedStringArray(tags), "autorisee": autorisee}


func test_couts_depuis_les_tags() -> void:
	var c := OptionsDialogue.couts(PackedStringArray(["cout_vivres=1", "cout_huile=2", "autre"]))
	assert_eq_deep(c, {&"vivres": 1, &"huile": 2})


func test_couts_inconnus_ou_nuls_ignores() -> void:
	var c := OptionsDialogue.couts(PackedStringArray(["cout_or=3", "cout_vivres=0", "cout_lucidite"]))
	assert_eq_deep(c, {})


func test_tags() -> void:
	var tags := PackedStringArray(["cache", "timbre=voix-sous-terre"])
	assert_true(OptionsDialogue.a_tag(tags, "cache"))
	assert_true(OptionsDialogue.a_tag(tags, "timbre"))
	assert_false(OptionsDialogue.a_tag(tags, "hallucination"))
	assert_eq(OptionsDialogue.valeur_tag(tags, "timbre"), "voix-sous-terre")


func test_presenter_hors_egare() -> void:
	var p := OptionsDialogue.presenter([
		_o("Partager ", ["cout_vivres=1"]),
		_o("Interdit", ["cache"], false),
		_o("Grisé", [], false),
		_o("Allumer", ["cout_huile=1", "sans_prelevement"]),
	])
	assert_eq(p.size(), 3, "l'option cachée n'apparaît pas")
	assert_eq(p[0]["texte"], "Partager")
	assert_eq(p[0]["index"], 0)
	assert_eq_deep(p[0]["couts_affiches"], {&"vivres": 1})
	assert_eq_deep(p[0]["a_prelever"], {&"vivres": 1})
	assert_false(p[0]["bave"])
	assert_eq(p[1]["index"], 2, "l'index d'origine saute l'option cachée")
	assert_false(p[1]["disponible"])
	assert_eq(p[2]["index"], 3)
	assert_eq_deep(p[2]["couts_affiches"], {&"huile": 1})
	# sans_prelevement : affiché, jamais prélevé
	assert_eq_deep(p[2]["a_prelever"], {})


func test_hallucination_bave() -> void:
	var p := OptionsDialogue.presenter([_o("Voir", ["hallucination"])])
	assert_true(p[0]["bave"])


func test_egare_coute_faux_sans_toucher_au_prelevement() -> void:
	GameState.modifier_jauge(&"lucidite", -6)
	var rng := RandomNumberGenerator.new()
	rng.seed = 3
	var options := [_o("A", ["cout_vivres=1"]), _o("B", ["cout_huile=2"])]
	var vu_bave := false
	for i in 40:
		var p := OptionsDialogue.presenter(options, rng)
		assert_eq_deep(p[0]["a_prelever"], {&"vivres": 1})
		assert_eq_deep(p[1]["a_prelever"], {&"huile": 2})
		if p[0]["bave"] or p[1]["bave"]:
			vu_bave = true
	assert_true(vu_bave, "à l'Égaré, des coûts finissent par baver")


func test_slug_timbre() -> void:
	assert_eq(OptionsDialogue.slug_timbre("Lamarre", PackedStringArray()), "lamarre")
	assert_eq(OptionsDialogue.slug_timbre("Aurèle", PackedStringArray()), "aurele")
	assert_eq(OptionsDialogue.slug_timbre("Aurèle", PackedStringArray(["timbre=ravaude"])), "ravaude")
	assert_eq(OptionsDialogue.slug_timbre("Voix sous terre", PackedStringArray()), "voix-sous-terre")
