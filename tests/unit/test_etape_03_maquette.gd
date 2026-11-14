extends GutTest
## Maquette grise de l'étape 3 (Village aux cloches muettes) : hub de jour, bascule en nuit
## par le lit chez Ilde, et deux chemins de sortie (nuit, aube) selon la procession.

const ETAPE := preload("res://scenes/etapes/etape_03/etape_03.tscn")
const RENCONTRES: Array[StringName] = [
	&"e3_lisiere", &"e3_noce", &"e3_ilde", &"e3_clocher", &"e3_procession",
]
const DETAILS: Array[String] = [
	"lisiere_fusils", "place_lampions", "ilde_pain", "clocher_cordes", "chambre_volet", "champs_cierges",
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
	# 5 rencontres, les champs, deux routes (nuit, aube), 6 détails.
	assert_eq(nb, RENCONTRES.size() + 3 + DETAILS.size())


func test_chaque_rencontre_et_chaque_detail_est_place() -> void:
	for id in RENCONTRES:
		assert_not_null(_etape.trouver_declencheur(id), "rencontre manquante : %s" % id)
	for nom in DETAILS:
		var detail := _etape.trouver_declencheur(StringName("e3_detail_%s" % nom))
		assert_not_null(detail, "détail manquant : %s" % nom)
		if detail != null:
			assert_false(detail.une_seule_fois)


func test_les_rencontres_ne_se_rejouent_pas() -> void:
	for id in RENCONTRES + ([&"e3_procession_champs"] as Array[StringName]):
		assert_true(_etape.trouver_declencheur(id).une_seule_fois, "%s se rejoue" % id)


func test_les_deux_routes_terminent_l_etape() -> void:
	for id in [&"e3_route", &"e3_route_aube"]:
		var route := _etape.trouver_declencheur(id)
		assert_eq(route.titre, "route")
		assert_true(route.fin_etape, "%s doit finir l'étape" % id)


func test_le_lit_demande_ilde_et_fond_au_noir() -> void:
	var lit := _passage("Lit")
	assert_false(lit.est_disponible())
	GameState.marquer_rencontre_vue(&"e3_ilde")
	assert_true(lit.est_disponible())
	assert_gt(lit.fondu_noir, 0.0)
	assert_eq(lit.trouver_arrivee().name, &"entree_chambre")


func test_la_chambre_n_a_pas_de_retour_vers_le_hub() -> void:
	var chambre := _etape.find_child("Chambre", true, false)
	for n in chambre.find_children("*", "Area2D", true, false):
		if n is Passage:
			assert_true((n as Passage).vers in [&"chemin_nuit", &"chemin_aube"],
				"%s ramène ailleurs que vers les champs" % n.name)


func test_la_procession_ouvre_un_seul_chemin() -> void:
	var nuit := _passage("VersCheminNuit")
	var aube := _passage("VersCheminAube")
	assert_false(nuit.est_disponible())
	assert_false(aube.est_disponible())
	GameState.marquer_rencontre_vue(&"e3_rester")
	assert_false(nuit.est_disponible())
	assert_true(aube.est_disponible())


func test_la_nuit_couvre_la_chambre_et_le_chemin_de_nuit() -> void:
	assert_eq(_etape.lieux_nuit, [&"chambre", &"chemin_nuit"] as Array[StringName])


func test_une_seule_zone_sombre_sur_le_chemin_de_nuit() -> void:
	var zones := get_tree().get_nodes_in_group(&"zones_sombres").filter(
		func(n: Node) -> bool: return _etape.is_ancestor_of(n))
	assert_eq(zones.size(), 1)
	assert_true(_etape.find_child("CheminNuit", true, false).is_ancestor_of(zones[0]))


func test_le_retour_d_un_lieu_de_jour_arrive_devant_sa_porte() -> void:
	assert_eq(_passage("PassageMaison").trouver_arrivee().name, &"porte_maison_ilde")
	assert_eq(_passage("PassageClocher").trouver_arrivee().name, &"porte_clocher")


func test_le_messager_demarre_a_la_lisiere() -> void:
	var depart: Marker2D = _etape.find_child("entree_lisiere", true, false)
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
