extends GutTest
## Playtest : la descente de l'étape 7 (e7_descente) part du bord de la galerie, au choix
## « Descendre », avant le déplacement ; e7_cloches (« Regarder les cloches ») ne la rejoue pas.

const ETAPE := preload("res://scenes/etapes/etape_07/etape_07.tscn")

var _etape: EtapeBase


func before_each() -> void:
	GameState.reinitialiser()
	Reglages.changer(&"effets_attenues", false)
	_etape = add_child_autofree(ETAPE.instantiate())


func after_each() -> void:
	GameState.reinitialiser()


func _bord() -> Passage:
	return _etape.get_node("Surface/Galerie/Descendre") as Passage


func test_le_bord_de_la_galerie_lance_la_descente() -> void:
	var bord := _bord()
	assert_eq(bord.cinematique, &"e7_descente")
	assert_eq(bord.vers, &"anneau_cloches")


func test_les_cloches_ne_rejouent_pas_la_descente() -> void:
	var texte := FileAccess.get_file_as_string("res://dialogue/etape_07/e7_cloches.dialogue")
	assert_false(texte.contains("Cinematiques.jouer(&\"e7_descente\")"))


func test_descente_puis_arrivee_aux_cloches() -> void:
	var messager := _etape.trouver_messager()
	var cine := Cinematiques.trouver(&"e7_descente")
	assert_not_null(cine)
	if cine == null:
		return
	var depart := (_etape.find_child("entree_galerie", true, false) as Marker2D).global_position
	messager.teleporter(depart)
	_bord().interagir(messager)
	assert_true(cine.en_cours, "la descente se joue au bord de la galerie")
	assert_eq(messager.global_position, depart, "Tobie reste au bord pendant la ciné")
	cine.sauter()
	var arrivee := _etape.find_child("entree_anneau_cloches", true, false) as Marker2D
	assert_eq(messager.global_position, arrivee.global_position, "puis il arrive aux cloches")
