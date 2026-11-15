extends GutTest
## Maquette grise de l'étape 6 (Cathédrale enterrée) : la fissure, la nef engloutie en zone
## sombre (ouverte par e6_nef, fermée par e6_eloi), le village enfoui reflet inversé de la
## place de l'étape 3, la niche du veilleur (seul aller-retour) et le seuil (fin d'étape).

const ETAPE := preload("res://scenes/etapes/etape_06/etape_06.tscn")
const ETAPE_3 := preload("res://scenes/etapes/etape_03/etape_03.tscn")
const RENCONTRES: Array[StringName] = [
	&"e6_nef", &"e6_eloi", &"e6_tablee", &"e6_veilleur", &"e6_seuil",
]
const DETAILS: Array[String] = [
	"nef_vitraux", "nef_racines", "village_lanternes", "tablee_couvert", "veilleur_uniforme",
	"seuil_porte",
]

var _etape: EtapeBase


func before_each() -> void:
	GameState.reinitialiser()
	_etape = ETAPE.instantiate()
	add_child_autofree(_etape)


func after_each() -> void:
	GameState.reinitialiser()


func _passage(nom: String) -> Passage:
	return _etape.find_child(nom, true, false) as Passage


func test_chaque_declencheur_joue_un_titre_qui_existe() -> void:
	var nb := 0
	for n in _etape.find_children("*", "Area2D", true, false):
		if n is DeclencheurDialogue:
			var d := n as DeclencheurDialogue
			nb += 1
			assert_not_null(d.dialogue, "dialogue manquant : %s" % d.name)
			if d.dialogue != null:
				assert_has(d.dialogue.get_cues(), d.titre, "titre %s absent pour %s" % [d.titre, d.name])
			assert_true(d.libelle != "" and d.libelle.length() <= 24, "libellé de %s" % d.name)
	assert_eq(nb, RENCONTRES.size() + DETAILS.size())


func test_chaque_rencontre_et_chaque_detail_est_place() -> void:
	for id in RENCONTRES:
		assert_not_null(_etape.trouver_declencheur(id), "rencontre manquante : %s" % id)
	for nom in DETAILS:
		assert_not_null(_etape.trouver_declencheur(StringName("e6_detail_%s" % nom)), nom)
	assert_true(_etape.trouver_declencheur(&"e6_seuil").fin_etape)
	for id in RENCONTRES:
		if id != &"e6_seuil":
			assert_true(_etape.trouver_declencheur(id).une_seule_fois, "%s se rejoue" % id)


func test_on_ne_contourne_pas_la_descente_dans_le_noir() -> void:
	var pente := _etape.find_child("Pente", true, false) as Verrou
	assert_eq(pente.rencontre, &"e6_nef")
	var nef := _etape.trouver_declencheur(&"e6_nef")
	var eloi := _etape.trouver_declencheur(&"e6_eloi")
	assert_gt(pente.global_position.x, nef.global_position.x)
	assert_lt(pente.global_position.x, eloi.global_position.x)


func test_eloi_ouvre_la_fin_de_la_nef_et_la_tablee_le_seuil() -> void:
	var eboulement := _etape.find_child("Eboulement", true, false) as Verrou
	assert_eq(eboulement.rencontre, &"e6_eloi")
	var seuil := _passage("VersSeuil")
	assert_false(seuil.est_disponible())
	GameState.marquer_rencontre_vue(&"e6_tablee")
	assert_true(seuil.est_disponible())


func test_une_seule_zone_sombre_dans_la_nef_entre_la_descente_et_eloi() -> void:
	var zones := get_tree().get_nodes_in_group(&"zones_sombres").filter(
		func(n: Node) -> bool: return _etape.is_ancestor_of(n))
	assert_eq(zones.size(), 1)
	assert_true(_etape.find_child("Nef", true, false).is_ancestor_of(zones[0]))
	var forme := (zones[0] as Node).get_node("Forme") as CollisionShape2D
	var demi := (forme.shape as RectangleShape2D).size.x / 2.0
	var nef := _etape.trouver_declencheur(&"e6_nef").global_position.x
	var eloi := _etape.trouver_declencheur(&"e6_eloi").global_position.x
	assert_gt(forme.global_position.x - demi, nef)
	assert_almost_eq(forme.global_position.x + demi, eloi, 1.0)


func test_pas_de_retour_vers_la_nef() -> void:
	for n in _etape.find_children("*", "Area2D", true, false):
		# Seule la fissure (surface) mène à la nef.
		if n is Passage and _etape.lieu_de(n) != &"":
			assert_ne((n as Passage).vers, &"nef", "%s ramène dans la nef" % n.name)
	assert_eq(_passage("PassageNiche").trouver_arrivee().name, &"porte_niche")


func test_le_village_reprend_la_composition_de_la_place_de_l_etape_3() -> void:
	var e3 := ETAPE_3.instantiate()
	add_child_autofree(e3)
	var place := e3.get_node("Surface/RuePlace") as Node2D
	var village := _etape.get_node("Lieux/Village") as Node2D
	var x3 := func(nom: String) -> float: return (e3.find_child(nom, true, false) as Node2D).global_position.x - place.global_position.x
	var x6 := func(nom: String) -> float: return (_etape.find_child(nom, true, false) as Node2D).global_position.x - village.global_position.x
	assert_eq(x6.call("e6_tablee"), x3.call("e3_noce"), "la tablée à la place de la noce")
	assert_eq(x6.call("VersNiche"), x3.call("VersClocher"), "la niche à la place du clocher")
	assert_eq(x6.call("e6_detail_village_lanternes"), x3.call("e3_detail_place_lampions"))


func test_le_messager_demarre_a_la_fissure() -> void:
	var depart: Marker2D = _etape.find_child("entree_fissure", true, false)
	assert_eq(_etape.trouver_messager().global_position, depart.global_position)


func test_les_points_d_interaction_sont_espaces() -> void:
	var points: Array[Node2D] = []
	for n in _etape.find_children("*", "Area2D", true, false):
		if n is DeclencheurDialogue or n is Passage:
			points.append(n)
	for a in points:
		for b in points:
			if a == b or absf(a.global_position.y - b.global_position.y) > 400.0:
				continue
			assert_true(absf(a.global_position.x - b.global_position.x) >= 200.0,
				"%s trop près de %s" % [a.name, b.name])


func test_chaque_lieu_a_son_ambiance_et_la_tablee_sa_musique() -> void:
	assert_true(_etape.get_node_or_null("Surface/Fissure/SonZone") is AudioStreamPlayer2D, "fissure")
	for lieu in _etape.get_node("Lieux").get_children():
		var son := lieu.get_node_or_null("SonLieu") as AudioStreamPlayer2D
		assert_not_null(son, "%s sans ambiance" % lieu.name)
		if son != null:
			assert_eq(son.bus, &"Ambiance", lieu.name)
			assert_true(son.stream.resource_path.contains("amb_cathedrale-enterree_"), lieu.name)
	var tablee := _etape.get_node("Lieux/Village/MusiqueTablee") as AudioStreamPlayer2D
	assert_eq(tablee.bus, &"Musique")
	assert_true(tablee.autoplay)
	var decl := _etape.trouver_declencheur(&"e6_tablee")
	assert_almost_eq(tablee.global_position.x, decl.global_position.x, 1.0, "posée sur la tablée")
