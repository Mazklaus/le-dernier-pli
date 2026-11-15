extends GutTest
## Tuiles rognées par tools/rogner_tuiles.py : chargées par leur AtlasTexture, elles gardent
## la taille d'origine (la marge rend la place des bords transparents retirés).

const TUILE := "res://assets/graphics/env/e2/env_e2_plan4_premier-plan_01.png"


func test_tuile_rognee_chargee_par_son_atlas() -> void:
	var t := DecorParallaxe.charger_tuile(TUILE)
	assert_true(t is AtlasTexture, "le .tres est préféré au PNG")
	assert_eq(t.get_size(), Vector2(2048, 1300), "taille d'origine conservée")
	var atlas := t as AtlasTexture
	assert_lt(atlas.atlas.get_width() * atlas.atlas.get_height(), 2048 * 1300 / 4,
			"seul le dessin utile est en mémoire")


func test_tuile_non_rognee_chargee_en_png() -> void:
	var t := DecorParallaxe.charger_tuile("res://assets/graphics/env/e1/env_e1_plan3_surface_01.png")
	assert_false(t is AtlasTexture)


func test_largeur_du_plan_inchangee() -> void:
	var plan := DecorParallaxe.creer_plan("res://assets/graphics/env/e2/env_e2_plan4_premier-plan", 1.4, 20)
	assert_not_null(plan)
	# 10 tuiles de 2048 + la dernière de 1600.
	assert_eq(DecorParallaxe.largeur(plan), 10 * 2048.0 + 1600.0)
	plan.free()
