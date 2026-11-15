extends GutTest
## Gestes déclenchés depuis les répliques (directive animation du GD) : tag [#geste=…],
## personnage visé, retour à la respiration, planche absente sans effet.

const SceneDeclencheur := preload("res://scenes/interactions/declencheur_dialogue/declencheur_dialogue.tscn")

var d: DeclencheurDialogue


func before_each() -> void:
	d = SceneDeclencheur.instantiate()
	d.rencontre_id = &"e1_ordre"
	d.personnage = &"lamarre"
	d.compagnons = {&"rose": Vector2(-200, 0)}
	add_child_autofree(d)


## Ajoute à un personnage un faux geste de 2 images (les vraies planches viendront de la DA).
func _faux_geste(p: Personnage, geste: StringName) -> void:
	p.sprite_frames.add_animation(geste)
	p.sprite_frames.set_animation_loop(geste, false)
	p.sprite_frames.set_animation_speed(geste, 10.0)
	var image := p.sprite_frames.get_frame_texture(SilhouetteTobie.REPOS, 0)
	p.sprite_frames.add_frame(geste, image)
	p.sprite_frames.add_frame(geste, image)


func test_tag_geste_vise_le_locuteur() -> void:
	var g := OptionsDialogue.geste("Lamarre", PackedStringArray(["geste=tendre"]))
	assert_eq(g["cible"], &"lamarre")
	assert_eq(g["geste"], &"tendre")
	assert_false(g["explicite"])


func test_tag_geste_avec_cible_explicite() -> void:
	var g := OptionsDialogue.geste("Le sonneur", PackedStringArray(["timbre=x", "geste=rose:danser"]))
	assert_eq(g["cible"], &"rose")
	assert_eq(g["geste"], &"danser")
	assert_true(g["explicite"])


func test_sans_tag_geste() -> void:
	assert_eq_deep(OptionsDialogue.geste("Lamarre", PackedStringArray(["cout_vivres=1"])), {})
	assert_eq_deep(OptionsDialogue.geste("Lamarre", PackedStringArray(["geste=rose:"])), {})


func test_planche_absente_ou_reservee() -> void:
	assert_eq(Personnage.chemin_geste(&"lamarre", &"geste_inexistant"), "")
	assert_eq(Personnage.chemin_geste(&"lamarre", &"repos"), "")
	assert_false(d.dessin.jouer_geste(&"geste_inexistant"))
	assert_eq(d.dessin.animation, SilhouetteTobie.REPOS)


func test_geste_joue_puis_retour_a_la_respiration() -> void:
	_faux_geste(d.dessin, &"tendre")
	assert_true(d.jouer_geste_replique("Lamarre", PackedStringArray(["geste=tendre"])))
	assert_eq(d.dessin.animation, &"tendre")
	assert_true(d.dessin.is_playing())
	await wait_seconds(0.4)
	assert_eq(d.dessin.animation, SilhouetteTobie.REPOS)


func test_geste_sur_un_compagnon() -> void:
	var rose := d.personnage_nomme(&"rose")
	assert_not_null(rose)
	_faux_geste(rose, &"danser")
	assert_true(d.jouer_geste_replique("Lamarre", PackedStringArray(["geste=rose:danser"])))
	assert_eq(rose.animation, &"danser")
	assert_eq(d.dessin.animation, SilhouetteTobie.REPOS)


func test_locuteur_sans_dessin_propre_retombe_sur_le_principal() -> void:
	_faux_geste(d.dessin, &"tendre")
	assert_true(d.jouer_geste_replique("Un soldat", PackedStringArray(["geste=tendre"])))
	assert_eq(d.dessin.animation, &"tendre")


func test_replique_de_tobie_ne_fait_pas_bouger_le_personnage() -> void:
	_faux_geste(d.dessin, &"tendre")
	watch_signals(d)
	assert_false(d.jouer_geste_replique("Tobie", PackedStringArray(["geste=tendre"])))
	assert_eq(d.dessin.animation, SilhouetteTobie.REPOS)
	assert_signal_emitted_with_parameters(d, "geste_demande", [&"tobie", &"tendre"])
