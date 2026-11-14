extends GutTest
## Maquette grise de l'étape 1 : chaque rencontre du plan de niveau a son déclencheur,
## chaque lieu souterrain ses points d'entrée et de sortie.

const ETAPE := preload("res://scenes/etapes/etape_01/etape_01.tscn")
const RENCONTRES: Array[StringName] = [
	&"e1_reveil", &"e1_ordre", &"e1_cantine", &"e1_cendre",
	&"e1_guetteur", &"e1_sape", &"e1_adieu", &"e1_parapet",
]
const LIEUX: Array[String] = [
	"couchette", "abri_sergent", "cantine", "chapelle", "vieille_sape", "sape_sortie",
]

var _etape: Node2D


func before_each() -> void:
	_etape = ETAPE.instantiate()
	add_child_autofree(_etape)


func test_chaque_rencontre_a_un_declencheur() -> void:
	for id in RENCONTRES:
		var declencheur: Area2D = _etape.call(&"declencheur", id)
		assert_not_null(declencheur, "déclencheur manquant : %s" % id)


func test_identifiants_de_rencontre_valides() -> void:
	var router := preload("res://autoload/scene_router.gd")
	for id in RENCONTRES:
		assert_eq(router.numero_etape_de(id), 1, String(id))


func test_chaque_lieu_a_ses_points_entree_et_sortie() -> void:
	for lieu in LIEUX:
		assert_not_null(_etape.find_child("entree_%s" % lieu, true, false), "entree_%s" % lieu)
		assert_not_null(_etape.find_child("sortie_%s" % lieu, true, false), "sortie_%s" % lieu)


func test_une_seule_zone_sombre() -> void:
	var zones := get_tree().get_nodes_in_group(&"zones_sombres").filter(
		func(n: Node) -> bool: return _etape.is_ancestor_of(n))
	assert_eq(zones.size(), 1)


func test_saut_de_rencontre_deplace_la_camera() -> void:
	var camera: Camera2D = _etape.get_node(^"CameraBlockout")
	_etape.call(&"aller_rencontre", &"e1_parapet")
	var cible: Area2D = _etape.call(&"declencheur", &"e1_parapet")
	assert_eq(camera.global_position, cible.global_position)
