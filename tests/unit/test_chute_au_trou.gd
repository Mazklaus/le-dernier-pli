extends GutTest
## Playtest (GD) : la chute de l'étape 6 (e6_chute_fissure) suit le choix « Se laisser tomber »
## au trou de la fissure, puis Tobie arrive dans la nef ; e6_nef ne la rejoue pas.

const ETAPE := preload("res://scenes/etapes/etape_06/etape_06.tscn")

var _etape: EtapeBase


func before_each() -> void:
	GameState.reinitialiser()
	Reglages.changer(&"effets_attenues", false)
	_etape = add_child_autofree(ETAPE.instantiate())


func after_each() -> void:
	GameState.reinitialiser()


func _trou() -> Passage:
	return _etape.get_node("Surface/Fissure/Descendre") as Passage


func test_le_trou_de_la_fissure_lance_la_chute() -> void:
	var trou := _trou()
	assert_eq(trou.cinematique, &"e6_chute_fissure")
	assert_eq(trou.libelle, "Se laisser tomber")
	assert_eq(trou.vers, &"nef")
	assert_true(trou.est_disponible(), "interactif dès l'arrivée")
	# La fente peinte (tools/gen_decors_e6.py : x 1080 à 1320) est sous la zone d'interaction.
	assert_between(trou.position.x, 1080.0, 1320.0)


func test_la_nef_ne_rejoue_pas_la_chute() -> void:
	var texte := FileAccess.get_file_as_string("res://dialogue/etape_06/e6_nef.dialogue")
	assert_false(texte.contains("Cinematiques.jouer(&\"e6_chute_fissure\")"))


func test_chute_puis_arrivee_dans_la_nef() -> void:
	var messager := _etape.trouver_messager()
	var cine := Cinematiques.trouver(&"e6_chute_fissure")
	assert_not_null(cine)
	if cine == null or cine.get_node_or_null("Animation") == null:
		return
	var depart := (_etape.get_node("Surface/Fissure/entree_fissure") as Marker2D).global_position
	messager.teleporter(depart)
	_trou().interagir(messager)
	assert_true(cine.en_cours, "la chute se joue au trou")
	assert_eq(messager.global_position, depart, "Tobie reste au bord pendant la ciné")
	assert_false(_trou().est_disponible(), "pas de second saut pendant la ciné")
	cine.sauter()
	var nef := _etape.find_child("entree_nef", true, false) as Marker2D
	assert_eq(messager.global_position, nef.global_position, "puis il arrive dans la nef")
	assert_true(GameState.rencontre_vue(Cinematique.drapeau(&"e6_chute_fissure")))
