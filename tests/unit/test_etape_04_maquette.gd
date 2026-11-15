extends GutTest
## Maquette grise de l'étape 4 (Hôpital des Recousus) : une descente fermée où l'on est
## conduit. Chaque porte s'ouvre sur la rencontre qui précède et aucun lieu ne ramène en
## arrière, sauf la lingerie (seul écart) ; la crypte est une zone sombre courte.

const ETAPE := preload("res://scenes/etapes/etape_04/etape_04.tscn")
const RENCONTRES: Array[StringName] = [
	&"e4_porche", &"e4_salle", &"e4_anselme", &"e4_crypte", &"e4_benediction",
]
const DETAILS: Array[String] = [
	"porche_tronc", "salle_lits", "lingerie_draps", "atelier_bocaux", "atelier_planche",
	"escalier_ex_voto", "crypte_noms",
]
## Ordre de la descente : chaque passage et la rencontre qui l'ouvre.
const VERROUS := {
	"VersSalle": &"e4_porche", "VersAtelier": &"e4_salle",
	"VersEscalier": &"e4_anselme", "VersEscalierService": &"e4_crypte",
}

var _etape: EtapeBase


func before_each() -> void:
	GameState.reinitialiser()
	_etape = ETAPE.instantiate()
	add_child_autofree(_etape)


func after_each() -> void:
	GameState.reinitialiser()


func _passage(nom: String) -> Passage:
	return _etape.find_child(nom, true, false) as Passage


func _passages() -> Array[Passage]:
	var liste: Array[Passage] = []
	for n in _etape.find_children("*", "Area2D", true, false):
		if n is Passage:
			liste.append(n as Passage)
	return liste


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
		var detail := _etape.trouver_declencheur(StringName("e4_detail_%s" % nom))
		assert_not_null(detail, "détail manquant : %s" % nom)
		if detail != null:
			assert_false(detail.une_seule_fois)


func test_les_rencontres_ne_se_rejouent_pas_et_la_benediction_finit_l_etape() -> void:
	for id in RENCONTRES:
		if id != &"e4_benediction":
			assert_true(_etape.trouver_declencheur(id).une_seule_fois, "%s se rejoue" % id)
	assert_true(_etape.trouver_declencheur(&"e4_benediction").fin_etape)


func test_chaque_porte_s_ouvre_sur_la_rencontre_qui_precede() -> void:
	for nom: String in VERROUS:
		var p := _passage(nom)
		assert_not_null(p, nom)
		assert_false(p.est_disponible(), "%s ouvert trop tôt" % nom)
		GameState.marquer_rencontre_vue(VERROUS[nom])
		assert_true(p.est_disponible(), "%s ne s'ouvre pas sur %s" % [nom, VERROUS[nom]])


func test_aucun_retour_sauf_la_lingerie() -> void:
	# Ordre de la descente : un passage ne mène jamais vers un lieu déjà traversé.
	var ordre: Array[StringName] = [&"", &"salle", &"atelier", &"escalier", &"crypte",
		&"escalier_service", &"rue_laterale"]
	for p in _passages():
		var depuis := _etape.lieu_de(p)
		if depuis == &"lingerie" or p.vers == &"lingerie":
			continue
		assert_gt(ordre.find(p.vers), ordre.find(depuis), "%s ramène en arrière" % p.name)
	assert_eq(_passage("PassageLingerie").trouver_arrivee().name, &"porte_lingerie")


func test_l_escalier_de_service_remonte_a_la_porte_laterale() -> void:
	var p := _passage("VersPorte")
	assert_eq(p.trouver_arrivee().name, &"sortie_hopital")
	assert_true(_etape.est_en_surface(p.trouver_arrivee().global_position))


func test_une_seule_zone_sombre_courte_dans_la_crypte() -> void:
	var zones := get_tree().get_nodes_in_group(&"zones_sombres").filter(
		func(n: Node) -> bool: return _etape.is_ancestor_of(n))
	assert_eq(zones.size(), 1)
	assert_true(_etape.find_child("Crypte", true, false).is_ancestor_of(zones[0]))
	var forme := (zones[0] as Node).get_node("Forme") as CollisionShape2D
	assert_lt((forme.shape as RectangleShape2D).size.x, 1.5 * 1920.0, "la crypte reste courte")


func test_le_messager_demarre_au_porche() -> void:
	var depart: Marker2D = _etape.find_child("entree_porche", true, false)
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
