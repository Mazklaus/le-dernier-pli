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
		for n in lieu.find_children("*", "DeclencheurDialogue", true, false):
			var d := n as DeclencheurDialogue
			if d.rencontre_id == e[1]:
				trouve = true
				assert_not_null(d.dessin, String(e[1]))
				if d.dessin != null:
					assert_eq(d.dessin.nom, e[2], String(e[1]))
		assert_true(trouve, String(e[1]))
