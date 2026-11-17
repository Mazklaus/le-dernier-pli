extends GutTest
## Playtest : les cinématiques d'arrivée se jouent au passage d'entrée, avant le déplacement,
## et non quand on parle au personnage : le village sous terre (« Suivre Eloi », nef, étape 6)
## et la salle de la Mère-Cloche (« Passer la porte », étape 7).

const CAS := [
	{"etape": "res://scenes/etapes/etape_06/etape_06.tscn", "passage": "VersVillage",
		"cine": &"e6_village_sous_terre", "vers": &"village", "requise": &"",
		"dialogue": "res://dialogue/etape_06/e6_tablee.dialogue"},
	{"etape": "res://scenes/etapes/etape_07/etape_07.tscn", "passage": "VersMereCloche",
		"cine": &"e7_mere_cloche", "vers": &"mere_cloche", "requise": &"e7_sceau",
		"dialogue": "res://dialogue/etape_07/e7_mere_cloche.dialogue"},
]


func before_each() -> void:
	GameState.reinitialiser()
	Reglages.changer(&"effets_attenues", false)


func after_each() -> void:
	GameState.reinitialiser()


func test_passage_lance_la_cine_puis_arrivee(p = use_parameters(CAS)) -> void:
	var etape: EtapeBase = add_child_autofree(load(p.etape).instantiate())
	var passage := etape.find_child(p.passage, true, false) as Passage
	assert_not_null(passage)
	if passage == null:
		return
	assert_eq(passage.cinematique, p.cine)
	assert_eq(passage.vers, p.vers)
	if p.requise != &"":
		GameState.marquer_rencontre_vue(p.requise)
	var cine := Cinematiques.trouver(p.cine)
	assert_not_null(cine)
	if cine == null:
		return
	var messager := etape.trouver_messager()
	var depart := passage.global_position
	messager.teleporter(depart)
	passage.interagir(messager)
	assert_true(cine.en_cours, "la ciné se joue au passage")
	assert_eq(messager.global_position, depart, "Tobie reste devant le passage pendant la ciné")
	cine.sauter()
	var arrivee := cine.get_node_or_null("PlaceTobie") as Marker2D
	if arrivee == null:
		arrivee = etape.find_child("entree_" + String(p.vers), true, false) as Marker2D
	assert_eq(messager.global_position, arrivee.global_position, "puis il arrive là où le plan l'a laissé")


func test_raccord_mere_cloche_tobie_pres_d_elle() -> void:
	var lieu: Node = load("res://scenes/etapes/etape_07/lieux/mere_cloche.tscn").instantiate()
	var place := lieu.get_node_or_null("e7_mere_cloche/PlaceTobie") as Marker2D
	assert_not_null(place, "le jeu reprend à côté de la Mère-Cloche, comme à la fin du plan")
	if place != null:
		var mere := lieu.get_node("Rencontres/e7_mere_cloche") as Node2D
		assert_lt(absf(place.position.x - mere.position.x), 200.0)
	lieu.free()


func test_la_rencontre_ne_rejoue_pas_la_cine(p = use_parameters(CAS)) -> void:
	var texte := FileAccess.get_file_as_string(p.dialogue)
	assert_false(texte.contains("Cinematiques.jouer(&\"%s\")" % p.cine))
