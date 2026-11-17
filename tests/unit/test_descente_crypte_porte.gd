extends GutTest
## Playtest : la descente dans la crypte (e4_descente_crypte) part de la porte de l'escalier,
## la pièce d'avant, et se joue avant le déplacement ; e4_crypte ne la rejoue pas.

const ETAPE := preload("res://scenes/etapes/etape_04/etape_04.tscn")

var _etape: EtapeBase


func before_each() -> void:
	GameState.reinitialiser()
	Reglages.changer(&"effets_attenues", false)
	_etape = add_child_autofree(ETAPE.instantiate())


func after_each() -> void:
	GameState.reinitialiser()


func _porte() -> Passage:
	return _etape.get_node("Lieux/Escalier/Passages/VersCrypte") as Passage


func test_la_porte_de_l_escalier_lance_la_descente() -> void:
	var porte := _porte()
	assert_eq(porte.cinematique, &"e4_descente_crypte")
	assert_eq(porte.vers, &"crypte")


func test_la_crypte_ne_rejoue_pas_la_descente() -> void:
	var texte := FileAccess.get_file_as_string("res://dialogue/etape_04/e4_crypte.dialogue")
	assert_false(texte.contains("Cinematiques.jouer(&\"e4_descente_crypte\")"))


func test_descente_puis_arrivee_dans_la_crypte() -> void:
	var messager := _etape.trouver_messager()
	var cine := Cinematiques.trouver(&"e4_descente_crypte")
	assert_not_null(cine)
	if cine == null:
		return
	var depart := (_etape.find_child("entree_escalier", true, false) as Marker2D).global_position
	messager.teleporter(depart)
	_porte().interagir(messager)
	assert_true(cine.en_cours, "la descente se joue à la porte")
	assert_eq(messager.global_position, depart, "Tobie reste devant la porte pendant la ciné")
	cine.sauter()
	var crypte := _etape.find_child("entree_crypte", true, false) as Marker2D
	assert_eq(messager.global_position, crypte.global_position, "puis il arrive dans la crypte")
