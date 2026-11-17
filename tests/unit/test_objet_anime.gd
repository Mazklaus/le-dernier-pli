extends GutTest
## ObjetAnime : boucle, geste joué une fois sur balise, accélération, silence sans planche.

const SceneDeclencheur := preload("res://scenes/interactions/declencheur_dialogue/declencheur_dialogue.tscn")
## Une planche fx existante (6 images de 140 px) sert de geste d'essai.
const PLANCHE := preload("res://assets/graphics/fx/fx_rideau-sape-tombe.png")


func _objet(avec_boucle: bool) -> ObjetAnime:
	var o := ObjetAnime.new()
	o.nom_objet = &"cloche"
	o.largeur_image = 140
	if avec_boucle:
		o.boucle = PLANCHE
	o.gestes = {&"fremir": PLANCHE}
	return o


func test_la_boucle_tourne_des_le_depart() -> void:
	var o: ObjetAnime = add_child_autofree(_objet(true))
	assert_eq(o.sprite_frames.get_frame_count(ObjetAnime.BOUCLE), 6)
	assert_eq(o.animation, ObjetAnime.BOUCLE)
	assert_true(o.is_playing())


func test_sans_boucle_l_objet_reste_immobile_puis_joue_son_geste() -> void:
	var o: ObjetAnime = add_child_autofree(_objet(false))
	assert_false(o.is_playing())
	assert_eq(o.frame, 0)
	assert_true(o.jouer_geste(&"fremir"))
	assert_eq(o.animation, &"fremir")
	assert_false(o.sprite_frames.get_animation_loop(&"fremir"))
	assert_false(o.jouer_geste(&"sonner"), "pas de planche, rien ne bouge")


func test_accelerer_presse_la_boucle() -> void:
	var o: ObjetAnime = add_child_autofree(_objet(true))
	assert_true(o.jouer_geste(ObjetAnime.ACCELERER))
	assert_eq(o.speed_scale, o.acceleration)
	var sans: ObjetAnime = add_child_autofree(_objet(false))
	assert_false(sans.jouer_geste(ObjetAnime.ACCELERER))


func test_la_balise_d_une_replique_anime_l_objet_vise() -> void:
	var lieu := Node2D.new()
	add_child_autofree(lieu)
	var d: DeclencheurDialogue = SceneDeclencheur.instantiate()
	d.name = "e7_cloches"
	lieu.add_child(d)
	var o := _objet(false)
	o.declencheurs = [NodePath("../e7_cloches")]
	lieu.add_child(o)
	d.jouer_geste_replique("Tobie", PackedStringArray(["geste=lise:fremir"]))
	assert_false(o.is_playing(), "autre cible")
	d.jouer_geste_replique("Tobie", PackedStringArray(["geste=cloche:fremir"]))
	assert_eq(o.animation, &"fremir")
	assert_true(o.is_playing())
