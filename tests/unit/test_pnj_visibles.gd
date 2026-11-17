extends GutTest
## Relevé PNJ de la QA (17/11) : les personnages qui parlent sont à l'écran. Anselme dessiné à
## l'atelier et à la bénédiction ; Ilde qui entre en cours de rencontre ([#entree=ilde]).

const SceneDeclencheur := preload("res://scenes/interactions/declencheur_dialogue/declencheur_dialogue.tscn")


func _declencheur(chemin_scene: String, chemin_noeud: String) -> DeclencheurDialogue:
	var lieu := (load(chemin_scene) as PackedScene).instantiate()
	autofree(lieu)
	return lieu.get_node(chemin_noeud) as DeclencheurDialogue


func test_anselme_est_dessine_a_l_atelier_et_a_la_benediction() -> void:
	var atelier := _declencheur("res://scenes/etapes/etape_04/lieux/atelier.tscn", "Rencontres/e4_anselme")
	assert_eq(atelier.personnage, &"anselme")
	var rue := _declencheur("res://scenes/etapes/etape_04/etape_04.tscn", "Surface/RueLaterale/e4_benediction")
	assert_eq(rue.personnage, &"anselme")
	for geste: StringName in [&"examiner", &"montrer", &"ranger-bocal", &"cendrer"]:
		assert_ne(Personnage.chemin_geste(&"anselme", geste), "", String(geste))


func test_un_personnage_entrant_reste_cache_jusqu_a_sa_replique() -> void:
	var d: DeclencheurDialogue = SceneDeclencheur.instantiate()
	d.entrees = {&"ilde": Vector2(450, 0)}
	add_child_autofree(d)
	var ilde := d.get_node_or_null("Entree_ilde") as Personnage
	assert_not_null(ilde)
	if ilde == null:
		return
	assert_false(ilde.visible)
	assert_eq(ilde.position, Vector2(450, 0))
	assert_false(d.entrer_replique(PackedStringArray(["geste=tendre"])))
	assert_true(d.entrer_replique(PackedStringArray(["entree=ilde"])))
	assert_true(ilde.visible)
	assert_false(d.entrer_replique(PackedStringArray(["entree=ilde"])), "déjà là")
	assert_eq(d.personnage_nomme(&"ilde"), ilde, "ses gestes la trouvent")


func test_ilde_entre_dans_la_chambre_et_sur_la_route_de_nuit() -> void:
	var chambre := _declencheur("res://scenes/etapes/etape_03/lieux/chambre.tscn", "Rencontres/e3_procession")
	assert_true(chambre.entrees.has(&"ilde"))
	var route := _declencheur("res://scenes/etapes/etape_03/lieux/chemin_nuit.tscn", "Rencontres/e3_route")
	assert_true(route.entrees.has(&"ilde"))
	var texte := FileAccess.get_file_as_string("res://dialogue/etape_03/e3_procession.dialogue")
	assert_eq(texte.count("[#entree=ilde]"), 2)


func test_la_tablee_et_le_vieux_de_la_noce_sont_a_table() -> void:
	var tablee := _declencheur("res://scenes/etapes/etape_06/lieux/village.tscn", "Rencontres/e6_tablee")
	for nom: StringName in [&"femme", &"enfant", &"mere", &"fillette"]:
		assert_true(tablee.compagnons.has(nom), String(nom))
	var gauche_a_droite: Array = [&"femme", &"enfant", &"mere", &"fillette"].map(
		func(n: StringName) -> float: return (tablee.compagnons[n] as Vector2).x)
	var tries := gauche_a_droite.duplicate()
	tries.sort()
	assert_eq(gauche_a_droite, tries, "femme, enfant, mère, fillette")
	var noce := _declencheur("res://scenes/etapes/etape_03/etape_03.tscn", "Surface/RuePlace/e3_noce")
	assert_true(noce.compagnons.has(&"vieux"))
	var texte := FileAccess.get_file_as_string("res://dialogue/etape_03/e3_noce.dialogue")
	assert_true(texte.contains("[#geste=vieux:parler]"))
