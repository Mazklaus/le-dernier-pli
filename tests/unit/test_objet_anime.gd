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


func _noeud(chemin_scene: String, chemin: String) -> ObjetAnime:
	var lieu := (load(chemin_scene) as PackedScene).instantiate()
	autofree(lieu)
	return lieu.get_node_or_null(chemin) as ObjetAnime


func test_les_objets_animes_de_la_da_sont_poses() -> void:
	var buee := _noeud("res://scenes/etapes/etape_04/lieux/crypte.tscn", "BueeVitre1")
	assert_not_null(buee)
	if buee != null:
		assert_eq(buee.nom_objet, &"buee")
		assert_not_null(buee.boucle)
	assert_not_null(_noeud("res://scenes/etapes/etape_04/lieux/crypte.tscn", "BueeVitre2"))
	var fumee := _noeud("res://scenes/etapes/etape_05/etape_05.tscn", "Surface/Campement/FumeeGamelle")
	assert_not_null(fumee)
	for chemin in ["res://scenes/etapes/etape_07/lieux/anneau_cloches.tscn", "res://scenes/etapes/etape_07/lieux/mere_cloche.tscn"]:
		var cloche := _noeud(chemin, "ClocheFremit")
		assert_not_null(cloche, chemin)
		if cloche != null:
			assert_null(cloche.boucle, "la cloche ne bouge que sur balise")
			assert_true(cloche.gestes.has(&"fremir"))


func test_la_cloche_fremit_0_1_0_1_0_puis_se_tait_sur_l_image_0() -> void:
	var o := ObjetAnime.new()
	o.nom_objet = &"cloche"
	o.gestes = {&"fremir": preload("res://assets/graphics/fx/fx_cloche-fremir_01.png")}
	o.largeur_image = 200
	o.images_par_seconde = 10.0
	o.ordres = {&"fremir": [0, 1, 0, 1, 0]}
	add_child_autofree(o)
	assert_eq(o.sprite_frames.get_frame_count(&"fremir"), 5)
	var r0 := (o.sprite_frames.get_frame_texture(&"fremir", 0) as AtlasTexture).region
	var r1 := (o.sprite_frames.get_frame_texture(&"fremir", 1) as AtlasTexture).region
	assert_eq(r0.position.x, 0.0)
	assert_eq(r1.position.x, 200.0)
	assert_false(o.is_playing())
	assert_eq(o.frame, 0)
