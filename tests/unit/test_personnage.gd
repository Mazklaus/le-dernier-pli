extends GutTest
## Personnages des rencontres (planches de la DA, #68) : posés aux pieds du déclencheur,
## respiration lente, rectangle de la maquette masqué.

const SceneDeclencheur := preload("res://scenes/interactions/declencheur_dialogue/declencheur_dialogue.tscn")
## [scène, rencontre, personnage] de l'étape 1.
const ETAPE_1 := [
	["res://scenes/etapes/etape_01/lieux/couchette.tscn", &"e1_reveil", &"jacquot"],
	["res://scenes/etapes/etape_01/lieux/abri_sergent.tscn", &"e1_ordre", &"lamarre"],
	["res://scenes/etapes/etape_01/lieux/chapelle.tscn", &"e1_cendre", &"cassien"],
	["res://scenes/etapes/etape_01/lieux/cantine.tscn", &"e1_cantine", &"ravaude"],
	["res://scenes/etapes/etape_01/lieux/sape_sortie.tscn", &"e1_adieu", &"jacquot"],
]


func test_planche_decoupee_en_4_images_lentes() -> void:
	var p := Personnage.creer(&"cassien")
	assert_not_null(p)
	assert_eq(p.sprite_frames.get_frame_count(SilhouetteTobie.REPOS), 4)
	assert_almost_eq(p.sprite_frames.get_animation_speed(SilhouetteTobie.REPOS), 10.0 / 3.0, 0.001)
	assert_eq(p.offset, Vector2(-100, -316))
	p.free()


func test_le_mort_est_une_image_figee() -> void:
	var p := Personnage.creer(&"mort")
	assert_not_null(p)
	assert_eq(p.sprite_frames.get_frame_count(SilhouetteTobie.REPOS), 1)
	p.free()


func test_brisse_et_le_mort_a_l_etape_2() -> void:
	var etape: EtapeBase = add_child_autofree(load("res://scenes/etapes/etape_02/etape_02.tscn").instantiate())
	assert_eq(etape.trouver_declencheur(&"e2_poste").dessin.nom, &"brisse")
	assert_eq(etape.trouver_declencheur(&"e2_mort").dessin.nom, &"mort")


func test_personnage_inconnu_ou_vide() -> void:
	assert_null(Personnage.creer(&""))
	assert_null(Personnage.creer(&"personne"))


func test_le_declencheur_pose_son_personnage_et_masque_la_maquette() -> void:
	var d: DeclencheurDialogue = SceneDeclencheur.instantiate()
	d.rencontre_id = &"e9_test"
	d.personnage = &"guetteur"
	var visuel := ColorRect.new()
	visuel.name = "Visuel"
	d.add_child(visuel)
	add_child_autofree(d)
	assert_not_null(d.dessin)
	assert_eq(d.dessin.get_parent(), d)
	assert_eq(d.dessin.position, Vector2.ZERO, "aux pieds du déclencheur")
	assert_false(visuel.visible)
	await wait_process_frames(2)
	assert_true(d.dessin.is_playing(), "il respire")


func test_les_personnages_de_l_etape_1_sont_poses() -> void:
	for e: Array in ETAPE_1:
		var lieu: Node = add_child_autofree((load(String(e[0])) as PackedScene).instantiate())
		var trouve := false
		for n in lieu.find_children("*", "", true, false):
			var d := n as DeclencheurDialogue
			if d != null and d.rencontre_id == e[1]:
				trouve = true
				assert_not_null(d.dessin, String(e[1]))
				if d.dessin != null:
					assert_eq(d.dessin.nom, e[2], String(e[1]))
		assert_true(trouve, String(e[1]))


## [scène, rencontre, personnage] de l'étape 3 (#84).
const ETAPE_3 := [
	["res://scenes/etapes/etape_03/lieux/maison_ilde.tscn", &"e3_ilde", &"ilde"],
	["res://scenes/etapes/etape_03/lieux/clocher.tscn", &"e3_clocher", &"sonneur"],
	["res://scenes/etapes/etape_03/lieux/chemin_nuit.tscn", &"e3_procession_champs", &"procession"],
]


func _declencheur(lieu: Node, rencontre: StringName) -> DeclencheurDialogue:
	for n in lieu.find_children("*", "", true, false):
		var d := n as DeclencheurDialogue
		if d != null and d.rencontre_id == rencontre:
			return d
	return null


func test_la_procession_marche_sur_place_en_4_images() -> void:
	var p := Personnage.creer(&"procession")
	assert_not_null(p)
	assert_eq(p.sprite_frames.get_frame_count(SilhouetteTobie.REPOS), 4)
	p.free()


func test_un_cortege_aligne_et_dephase() -> void:
	var d: DeclencheurDialogue = SceneDeclencheur.instantiate()
	d.rencontre_id = &"e9_cortege"
	d.personnage = &"procession"
	d.cortege = 4
	add_child_autofree(d)
	assert_not_null(d.dessin)
	assert_eq(d.dessin.frame, 0)
	for i in range(1, 4):
		var suivant := d.get_node_or_null("Cortege%d" % i) as Personnage
		assert_not_null(suivant, "Cortege%d" % i)
		if suivant != null:
			assert_eq(suivant.position, Vector2(-140.0 * i, 0.0))
			assert_eq(suivant.frame, i % 4, "déphasé d'une image")
	assert_null(d.get_node_or_null("Cortege4"))


func test_les_compagnons_sont_poses_a_leur_decalage() -> void:
	var d: DeclencheurDialogue = SceneDeclencheur.instantiate()
	d.rencontre_id = &"e9_noce"
	d.compagnons = {&"rose": Vector2(-200, 0), &"violoneux": Vector2(200, 0), &"personne": Vector2.ZERO}
	var visuel := ColorRect.new()
	visuel.name = "Visuel"
	d.add_child(visuel)
	add_child_autofree(d)
	assert_null(d.dessin)
	assert_eq((d.get_node("Compagnon_rose") as Node2D).position, Vector2(-200, 0))
	assert_eq((d.get_node("Compagnon_violoneux") as Node2D).position, Vector2(200, 0))
	assert_null(d.get_node_or_null("Compagnon_personne"), "planche absente : rien")
	assert_false(visuel.visible)


func test_les_personnages_de_l_etape_3_sont_poses() -> void:
	for e: Array in ETAPE_3:
		var lieu: Node = add_child_autofree((load(String(e[0])) as PackedScene).instantiate())
		var d := _declencheur(lieu, e[1])
		assert_not_null(d, String(e[1]))
		if d != null:
			assert_not_null(d.dessin, String(e[1]))
			if d.dessin != null:
				assert_eq(d.dessin.nom, e[2], String(e[1]))
	var etape: EtapeBase = add_child_autofree(load("res://scenes/etapes/etape_03/etape_03.tscn").instantiate())
	assert_eq(etape.trouver_declencheur(&"e3_lisiere").dessin.nom, &"enfants")
	var noce := etape.trouver_declencheur(&"e3_noce")
	assert_not_null(noce.get_node_or_null("Compagnon_rose"))
	assert_not_null(noce.get_node_or_null("Compagnon_violoneux"))
	var champs := _declencheur(etape, &"e3_procession_champs")
	if champs != null:
		assert_not_null(champs.get_node_or_null("Cortege3"), "quatre silhouettes dans les champs")


func test_la_procession_passe_sous_la_fenetre_de_la_chambre() -> void:
	var chambre: Node = add_child_autofree(load("res://scenes/etapes/etape_03/lieux/chambre.tscn").instantiate())
	var fenetre := chambre.get_node("ProcessionFenetre") as ProcessionFenetre
	assert_eq(fenetre.silhouettes.size(), 5)
	assert_true(fenetre.decoupe.clip_contents, "découpée dans la vitre")
	assert_eq(fenetre.decoupe.position, Vector2(300, 520))
	assert_eq(fenetre.decoupe.size, Vector2(200, 220))
	var tete := fenetre.silhouettes[0]
	assert_almost_eq(tete.scale.x, 0.28, 0.001)
	assert_almost_eq(tete.global_position.y, 735.0, 0.5, "pieds au ras de l'appui")
	assert_eq(fenetre.silhouettes[1].frame, 1, "déphasée d'une image")
	var depart := fenetre.x_silhouette(0)
	await wait_seconds(0.5)
	assert_gt(fenetre.x_silhouette(0), depart, "elles vont vers la droite")
	for i in 5:
		var x := fenetre.x_silhouette(i)
		assert_between(x, 260.0, 610.0, "dans la boucle")
	var croisee := fenetre.get_child(fenetre.get_child_count() - 1) as CanvasItem
	assert_gt(croisee.get_index(), fenetre.decoupe.get_index(), "la croisée reste devant")
	assert_false((chambre.get_node("Rencontres/e3_procession/Visuel") as CanvasItem).visible)
