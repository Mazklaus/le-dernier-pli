extends GutTest
## Gestes des personnages (directive animation) : planches de 200×320, 3 à 6 images, balisées
## dans les dialogues ; Tobie qui grimpe, la couverture qui retombe, la remise du pli.

const GESTES := {
	&"lamarre": [&"tendre", &"montrer-pli", &"congedier", &"lever-main"],
	&"jacquot": [&"siffler", &"lever-main", &"secouer", &"montrer", &"prendre"],
	&"cassien": [&"cendrer", &"tendre"],
	&"ravaude": [&"servir", &"montrer", &"tendre"],
	&"guetteur": [&"montrer"],
}


func test_chaque_geste_a_sa_planche_de_3_a_6_images() -> void:
	for nom: StringName in GESTES:
		for geste: StringName in GESTES[nom]:
			var chemin := Personnage.chemin_geste(nom, geste)
			assert_ne(chemin, "", "%s : %s" % [nom, geste])
			if chemin == "":
				continue
			var t := load(chemin) as Texture2D
			assert_eq(t.get_height(), 320, chemin)
			assert_eq(t.get_width() % 200, 0, chemin)
			var n := t.get_width() / 200
			assert_between(n, 3, 6, chemin)


func test_le_geste_se_joue_puis_revient_a_la_respiration() -> void:
	var p := Personnage.creer(&"jacquot")
	add_child_autofree(p)
	assert_true(p.jouer_geste(&"siffler"))
	assert_eq(p.animation, &"siffler")
	assert_false(p.sprite_frames.get_animation_loop(&"siffler"))


func test_tobie_grimpe_en_4_images_avec_ses_calques() -> void:
	for f in ["chr_tobie_grimper_01.png", "chr_tobie_grimper_01_red.png", "chr_tobie-cendre_grimper_01.png"]:
		var t := load("res://assets/graphics/chr/" + f) as Texture2D
		assert_not_null(t, f)
		if t != null:
			assert_eq(t.get_size(), Vector2(800, 320), f)


func test_la_couverture_retombe_en_6_images() -> void:
	var t := load("res://assets/graphics/fx/fx_rideau-sape-tombe.png") as Texture2D
	assert_eq(t.get_size(), Vector2(840, 460))


func test_la_remise_du_pli_tient_dans_des_textures_de_4096() -> void:
	var tailles := {"01": Vector2(1920, 1080), "02": Vector2(2880, 2520), "03": Vector2(1920, 1080), "04": Vector2(2400, 1560)}
	for k: String in tailles:
		var t := load("res://assets/graphics/cin/cin_remise-pli_%s.png" % k) as Texture2D
		assert_eq(t.get_size(), tailles[k], k)


## Étape 2 (#138) : Brisse et le mort.
const GESTES_E2 := {
	&"brisse": [&"lever-main", &"tendre", &"donner", &"chauffer-cire", &"montrer"],
	&"mort": [&"lever-bras"],
}


func test_les_gestes_de_l_etape_2_ont_leur_planche() -> void:
	for nom: StringName in GESTES_E2:
		for geste: StringName in GESTES_E2[nom]:
			var chemin := Personnage.chemin_geste(nom, geste)
			assert_ne(chemin, "", "%s : %s" % [nom, geste])
			if chemin != "":
				var t := load(chemin) as Texture2D
				assert_eq(t.get_height(), 320, chemin)
				assert_between(t.get_width() / 200, 3, 6, chemin)


## Étape 3 (#139) : les enfants, Ilde, Rose, le sonneur.
const GESTES_E3 := {
	&"enfants": [&"viser", &"hausser-epaules"],
	&"ilde": [&"regarder-sacoche", &"tendre"],
	&"rose": [&"danser"],
	&"sonneur": [&"tirer-corde", &"serrer"],
}


func test_les_gestes_de_l_etape_3_ont_leur_planche() -> void:
	for nom: StringName in GESTES_E3:
		for geste: StringName in GESTES_E3[nom]:
			var chemin := Personnage.chemin_geste(nom, geste)
			assert_ne(chemin, "", "%s : %s" % [nom, geste])
			if chemin != "":
				var t := load(chemin) as Texture2D
				assert_eq(t.get_height(), 320, chemin)
				assert_between(t.get_width() / 200, 3, 6, chemin)


func test_la_procession_de_nuit_a_ses_calques_et_ilde_en_tete() -> void:
	var rue := load("res://assets/graphics/cin/cin_procession-nuit_01.png") as Texture2D
	var volet := load("res://assets/graphics/cin/cin_procession-nuit_02.png") as Texture2D
	assert_eq(rue.get_size(), Vector2(1920, 1080))
	assert_eq(volet.get_size(), Vector2(1920, 1080))
	# les jours du volet sont transparents : on y voit passer les cierges
	assert_lt(volet.get_image().get_pixel(960, 577).a, 0.1)
	assert_gt(volet.get_image().get_pixel(960, 530).a, 0.9)
	var ilde := load("res://assets/graphics/chr/chr_ilde-cierge_marche_01.png") as Texture2D
	assert_eq(ilde.get_size(), Vector2(800, 320))


## Étape 4 : sœur Maude, le caporal Fernand, frère Anselme.
const GESTES_E4 := {
	&"maude": [&"laver", &"baiser-ruban"],
	&"fernand": [&"se-redresser", &"hocher-tete", &"montrer"],
	&"anselme": [&"examiner", &"ranger-bocal", &"montrer", &"cendrer"],
}


func test_les_gestes_de_l_etape_4_ont_leur_planche() -> void:
	for nom: StringName in GESTES_E4:
		assert_true(ResourceLoader.exists("res://assets/graphics/chr/chr_%s_repos_01.png" % nom), String(nom))
		for geste: StringName in GESTES_E4[nom]:
			var chemin := Personnage.chemin_geste(nom, geste)
			assert_ne(chemin, "", "%s : %s" % [nom, geste])
			if chemin != "":
				var t := load(chemin) as Texture2D
				assert_eq(t.get_height(), 320, chemin)
				assert_between(t.get_width() / 200, 3, 6, chemin)


func test_la_greffe_en_ombre_a_ses_planches() -> void:
	# plan A : le drap et ses 6 images (2 x 3) ; plan B : la lampe et ses 4 images (2 x 2)
	var tailles := {1: Vector2(1920, 1080), 2: Vector2(2560, 2520), 3: Vector2(1920, 1080), 4: Vector2(1600, 1600)}
	for i: int in tailles:
		var t := load("res://assets/graphics/cin/cin_greffe_%02d.png" % i) as Texture2D
		assert_not_null(t, str(i))
		if t != null:
			assert_eq(t.get_size(), tailles[i], str(i))
## Étape 5 : les gestes de Tobie, chacun avec ses trois calques (base, ruban, cendre).
func test_les_gestes_de_tobie_de_l_etape_5_ont_leurs_trois_calques() -> void:
	for geste: String in ["entailler", "graver", "accrocher"]:
		var largeur := -1
		for motif: String in ["chr_tobie_%s_01.png", "chr_tobie_%s_01_red.png", "chr_tobie-cendre_%s_01.png"]:
			var t := load("res://assets/graphics/chr/" + motif % geste) as Texture2D
			assert_not_null(t, motif % geste)
			if t == null:
				continue
			assert_eq(t.get_height(), 320, motif % geste)
			if largeur < 0:
				largeur = t.get_width()
			assert_eq(t.get_width(), largeur, "calques synchronisés : " + motif % geste)
		assert_between(largeur / 200, 3, 6, geste)


func test_l_autre_se_retourne_a_ses_planches() -> void:
	# le fond, et 6 images de 200 x 170 (3 x 2) autour de l'Autre, au bout du sentier
	var fond := load("res://assets/graphics/cin/cin_autre_01.png") as Texture2D
	var images := load("res://assets/graphics/cin/cin_autre_02.png") as Texture2D
	assert_eq(fond.get_size(), Vector2(1920, 1080))
	assert_eq(images.get_size(), Vector2(600, 340))


func test_la_chute_dans_la_fissure_a_ses_planches() -> void:
	# e6_chute_fissure (tools/gen_cin_e6.py) : plan A (fond, 6 images de 600×560 en grille 3 × 2),
	# plan B (fond, la chute lourde : 7 images de 240×240 transparentes, en ligne).
	var tailles := {"01": Vector2(1920, 1080), "02": Vector2(1800, 1120), "03": Vector2(1920, 1080), "04": Vector2(1680, 240)}
	for k: String in tailles:
		var t := load("res://assets/graphics/cin/cin_chute_%s.png" % k) as Texture2D
		assert_not_null(t, k)
		if t != null:
			assert_eq(t.get_size(), tailles[k], k)
