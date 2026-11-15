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


func test_tag_tenir() -> void:
	var g := OptionsDialogue.geste("Tobie", PackedStringArray(["geste=mort:tourner-tete", "tenir"]))
	assert_true(g["tenir"])
	assert_false(OptionsDialogue.geste("Lamarre", PackedStringArray(["geste=tendre"]))["tenir"])


func test_geste_tenu_garde_sa_derniere_image() -> void:
	_faux_geste(d.dessin, &"tendre")
	assert_true(d.jouer_geste_replique("Lamarre", PackedStringArray(["geste=tendre", "tenir"])))
	await wait_seconds(0.4)
	assert_eq(d.dessin.animation, &"tendre", "tenu jusqu'au geste suivant")
	assert_eq(d.dessin.frame, 1)
	_faux_geste(d.dessin, &"congedier")
	assert_true(d.jouer_geste_replique("Lamarre", PackedStringArray(["geste=congedier"])))
	await wait_seconds(0.4)
	assert_eq(d.dessin.animation, SilhouetteTobie.REPOS, "le geste suivant revient au repos")


func test_pose_debut_geste_immobile() -> void:
	_faux_geste(d.dessin, &"lever-bras")
	assert_true(d.dessin.poser_debut_geste(&"lever-bras"))
	assert_eq(d.dessin.animation, &"lever-bras")
	assert_eq(d.dessin.frame, 0)
	assert_false(d.dessin.is_playing())
	assert_false(d.dessin.poser_debut_geste(&"geste_inexistant"))


func test_le_mort_bras_pendant_avant_la_rencontre() -> void:
	if Personnage.chemin_geste(&"mort", &"lever-bras") == "":
		pass_test("planche du mort pas encore livrée (DA, #149)")
		return
	GameState.reinitialiser()
	var etape: EtapeBase = add_child_autofree(load("res://scenes/etapes/etape_02/etape_02.tscn").instantiate())
	var mort := etape.trouver_declencheur(&"e2_mort").dessin
	assert_eq(mort.animation, &"lever-bras")
	assert_eq(mort.frame, 0)


func test_geste_de_tobie_joue_par_le_messager_tourne_vers_la_croix() -> void:
	var messager: Messager = add_child_autofree(preload("res://scenes/messager/messager.tscn").instantiate())
	var silhouette := messager.get_node("%Silhouette") as SilhouetteTobie
	if not silhouette.est_dessine():
		pass_test("planches de Tobie absentes")
		return
	_faux_geste(silhouette, &"entailler")
	d.global_position = Vector2(500, 0)
	messager.global_position = Vector2(560, 0)
	assert_true(d.jouer_geste_replique("Tobie", PackedStringArray(["geste=tobie:entailler"])))
	assert_eq(messager.regard, -1, "tourné vers la croix, à sa gauche")
	assert_almost_eq(messager.global_position.x, 500.0 + d.ecart_geste_tobie, 0.01, "à une main de distance")
	assert_eq(messager.animation_voulue(0.0), &"entailler")
	assert_eq(silhouette.base.animation, &"entailler")
	await wait_seconds(0.4)
	assert_eq(messager.geste, &"", "geste fini")
	assert_ne(messager.animation_voulue(0.0), &"entailler")
	assert_eq(d.dessin.animation, SilhouetteTobie.REPOS, "Lamarre ne bouge pas")


## Faux geste de 2 images sur chaque calque (les vraies planches viennent de la DA).
func _faux_geste(silhouette: SilhouetteTobie, nom: StringName) -> void:
	for calque in silhouette.calques():
		calque.sprite_frames.add_animation(nom)
		calque.sprite_frames.set_animation_loop(nom, false)
		calque.sprite_frames.set_animation_speed(nom, 10.0)
		var image := calque.sprite_frames.get_frame_texture(SilhouetteTobie.REPOS, 0)
		calque.sprite_frames.add_frame(nom, image)
		calque.sprite_frames.add_frame(nom, image)


func test_geste_de_tobie_vers_le_repere_du_geste() -> void:
	var messager: Messager = add_child_autofree(preload("res://scenes/messager/messager.tscn").instantiate())
	var silhouette := messager.get_node("%Silhouette") as SilhouetteTobie
	if not silhouette.est_dessine():
		pass_test("planches de Tobie absentes")
		return
	_faux_geste(silhouette, &"graver")
	_faux_geste(silhouette, &"accrocher")
	var repere := Marker2D.new()
	repere.name = "geste_graver"
	repere.position = Vector2(140, 0)
	d.add_child(repere)
	d.global_position = Vector2(500, 0)
	assert_eq(d.repere_geste(&"graver"), repere)
	assert_eq(d.repere_geste(&"accrocher"), d, "sans repère, le déclencheur")
	messager.global_position = Vector2(300, 0)
	assert_true(d.jouer_geste_replique("Tobie", PackedStringArray(["geste=tobie:graver"])))
	assert_eq(messager.regard, 1)
	assert_almost_eq(messager.global_position.x, 640.0 - d.ecart_geste_tobie, 0.01, "devant la croix sans nom")
	await wait_seconds(0.4)
	assert_true(d.jouer_geste_replique("Tobie", PackedStringArray(["geste=tobie:accrocher"])))
	assert_eq(messager.regard, -1, "la croix d'Aubin est derrière lui")
	assert_almost_eq(messager.global_position.x, 500.0 + d.ecart_geste_tobie, 0.01)


func test_geste_de_tobie_sans_planche() -> void:
	var messager: Messager = add_child_autofree(preload("res://scenes/messager/messager.tscn").instantiate())
	assert_false(messager.jouer_geste(&"geste_inexistant"))
	assert_false(messager.jouer_geste(SilhouetteTobie.MARCHE), "les animations de base ne sont pas des gestes")
	assert_eq(messager.geste, &"")
