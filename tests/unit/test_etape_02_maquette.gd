extends GutTest
## Maquette grise de l'étape 2 (No Man's Land) : chaque rencontre et chaque détail du plan
## de niveau a son DeclencheurDialogue, le chemin est fermé par trois verrous qui s'ouvrent
## sur des rencontres marquées par les dialogues, et le messager démarre sur le parapet.

const ETAPE := preload("res://scenes/etapes/etape_02/etape_02.tscn")
const RENCONTRES: Array[StringName] = [
	&"e2_poste", &"e2_barbeles", &"e2_mort", &"e2_sacoche", &"e2_cantique",
]
const DETAILS: Array[String] = [
	"parapet_sac", "poste_registre", "poste_bougie", "brouillard_piquet",
	"brouillard_casque", "mort_plaque", "souche_entailles", "souche_village",
]

var _etape: EtapeBase


func before_each() -> void:
	GameState.reinitialiser()
	_etape = ETAPE.instantiate()
	add_child_autofree(_etape)


func after_each() -> void:
	GameState.reinitialiser()


func _declencheurs() -> Array[DeclencheurDialogue]:
	var liste: Array[DeclencheurDialogue] = []
	for n in _etape.find_children("*", "Area2D", true, false):
		if n is DeclencheurDialogue:
			liste.append(n as DeclencheurDialogue)
	return liste


func test_chaque_declencheur_joue_un_titre_qui_existe() -> void:
	var declencheurs := _declencheurs()
	assert_eq(declencheurs.size(), RENCONTRES.size() + DETAILS.size() + 2)
	for d in declencheurs:
		assert_not_null(d.dialogue, "dialogue manquant : %s" % d.name)
		if d.dialogue != null:
			assert_has(d.dialogue.get_cues(), d.titre, "titre %s absent pour %s" % [d.titre, d.name])
		assert_true(d.libelle != "" and d.libelle.length() <= 24, "libellé de %s" % d.name)


func test_chaque_rencontre_et_chaque_detail_est_place() -> void:
	for id in RENCONTRES:
		assert_not_null(_etape.trouver_declencheur(id), "rencontre manquante : %s" % id)
	for nom in DETAILS:
		var detail := _etape.trouver_declencheur(StringName("e2_detail_%s" % nom))
		assert_not_null(detail, "détail manquant : %s" % nom)
		if detail != null:
			assert_eq(detail.titre, nom)
			assert_false(detail.une_seule_fois, "%s doit rester rejouable" % nom)


func test_la_seconde_ceinture_et_le_boyau_jouent_leur_titre() -> void:
	var ceinture := _etape.trouver_declencheur(&"e2_barbeles_ceinture2")
	assert_eq(ceinture.titre, "seconde_ceinture")
	assert_eq(ceinture.dialogue.resource_path, "res://dialogue/etape_02/e2_barbeles.dialogue")
	var boyau := _etape.trouver_declencheur(&"e2_boyau")
	assert_eq(boyau.titre, "boyau")
	assert_eq(boyau.dialogue.resource_path, "res://dialogue/etape_02/e2_poste.dialogue")


func test_le_cantique_termine_l_etape() -> void:
	assert_true(_etape.trouver_declencheur(&"e2_cantique").fin_etape)


func test_le_messager_demarre_sur_le_parapet() -> void:
	var depart: Marker2D = _etape.find_child("entree_parapet", true, false)
	assert_eq(_etape.trouver_messager().global_position, depart.global_position)


func test_les_verrous_s_ouvrent_sur_les_rencontres_des_dialogues() -> void:
	var attendus := {
		"Chicane": &"e2_poste_passe",
		"CeintureUne": &"e2_barbeles",
		"CeintureDeux": &"e2_barbeles_ceinture2",
	}
	for nom in attendus:
		var verrou: Verrou = _etape.find_child(nom, true, false)
		assert_not_null(verrou, nom)
		assert_eq(verrou.rencontre, attendus[nom])
		assert_false(verrou.est_ouvert())
		GameState.marquer_rencontre_vue(attendus[nom])
		assert_true(verrou.est_ouvert())


func test_le_detour_du_poste_passe_par_le_boyau() -> void:
	var entree: Passage = _etape.find_child("VersBoyau", true, false)
	var sortie: Passage = _etape.find_child("SortieBoyau", true, false)
	var chicane: Verrou = _etape.find_child("Chicane", true, false)
	assert_false(entree.est_disponible())
	GameState.marquer_rencontre_vue(&"e2_poste_detour")
	assert_true(entree.est_disponible())
	assert_false(sortie.est_disponible(), "on ne ressort pas sans avoir allumé la lampe")
	GameState.marquer_rencontre_vue(&"e2_boyau")
	assert_true(sortie.est_disponible())
	assert_gt(sortie.trouver_arrivee().global_position.x, chicane.global_position.x,
		"le boyau ressort après la chicane")


func test_une_seule_zone_sombre_qui_couvre_le_mort() -> void:
	var zones := get_tree().get_nodes_in_group(&"zones_sombres").filter(
		func(n: Node) -> bool: return _etape.is_ancestor_of(n))
	assert_eq(zones.size(), 1)
	var zone := zones[0] as Area2D
	var forme := (zone.get_node("Forme") as CollisionShape2D).shape as RectangleShape2D
	var gauche := zone.global_position.x - forme.size.x / 2.0
	var droite := zone.global_position.x + forme.size.x / 2.0
	for id in [&"e2_barbeles", &"e2_mort", &"e2_barbeles_ceinture2"]:
		var x := _etape.trouver_declencheur(id).global_position.x
		assert_between(x, gauche, droite, "%s hors du brouillard" % id)


func test_aucun_detail_dans_la_zone_de_la_sacoche() -> void:
	var sacoche := _etape.trouver_declencheur(&"e2_sacoche").global_position.x
	for nom in DETAILS:
		var x := _etape.trouver_declencheur(StringName("e2_detail_%s" % nom)).global_position.x
		assert_true(absf(x - sacoche) > 1440.0, "%s trop près de la sacoche" % nom)


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
