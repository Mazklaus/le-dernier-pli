extends GutTest
## Maquette grise de l'étape 5 (Forêt de Croix) : une boucle. Le bout du sentier ramène devant
## la même croix-repère ; la sortie s'ouvre au second passage (e5_sentier), puis campement,
## cimetière et clairière en ligne. Pas de zone sombre.

const ETAPE := preload("res://scenes/etapes/etape_05/etape_05.tscn")
const RENCONTRES: Array[StringName] = [
	&"e5_sentier", &"e5_autre", &"e5_campement", &"e5_croix", &"e5_clairiere",
]
const DETAILS: Array[String] = [
	"sentier_bornes", "sentier_traces", "autre_branche", "campement_gamelle", "croix_objets",
	"clairiere_ciel",
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
				if d.titre_si_verrouille != "":
					assert_has(d.dialogue.get_cues(), d.titre_si_verrouille, d.name)
			assert_true(d.libelle != "" and d.libelle.length() <= 24, "libellé de %s" % d.name)
	assert_eq(nb, RENCONTRES.size() + DETAILS.size())


func test_chaque_rencontre_et_chaque_detail_est_place() -> void:
	for id in RENCONTRES:
		assert_not_null(_etape.trouver_declencheur(id), "rencontre manquante : %s" % id)
	for nom in DETAILS:
		assert_not_null(_etape.trouver_declencheur(StringName("e5_detail_%s" % nom)), nom)
	assert_true(_etape.trouver_declencheur(&"e5_clairiere").fin_etape)


func test_la_croix_joue_premier_passage_jusqu_au_bout_du_premier_tour() -> void:
	var croix := _etape.trouver_declencheur(&"e5_sentier")
	assert_eq(croix.titre_a_jouer(), "premier_passage")
	GameState.marquer_rencontre_vue(&"e5_entaille")
	assert_eq(croix.titre_a_jouer(), "premier_passage", "pas de second passage sur place (QA #108)")
	GameState.marquer_rencontre_vue(&"e5_autre")
	assert_eq(croix.titre_a_jouer(), "debut")
	assert_true(croix.est_disponible(), "le second passage doit se jouer")
	GameState.marquer_rencontre_vue(&"e5_sentier")
	assert_false(croix.est_disponible(), "puis la croix ne se rejoue plus")


func test_on_ne_finit_pas_le_tour_sans_croiser_l_autre() -> void:
	var fourre := _etape.find_child("Fourre", true, false) as Verrou
	assert_eq(fourre.rencontre, &"e5_autre")
	var autre := _etape.trouver_declencheur(&"e5_autre")
	var continuer := _passage("Continuer")
	assert_lt(autre.global_position.x, fourre.global_position.x)
	assert_lt(fourre.global_position.x, continuer.global_position.x)


func test_l_entaille_se_voit_des_que_tobie_l_a_faite() -> void:
	var entaille := _etape.trouver_declencheur(&"e5_sentier").get_node("Entaille") as CanvasItem
	assert_false(entaille.visible)
	GameState.marquer_rencontre_vue(&"e5_entaille_faite")
	assert_true(entaille.visible)


func test_le_retour_de_boucle_lance_la_croix_tout_seul() -> void:
	GameState.marquer_rencontre_vue(&"e5_entaille")
	GameState.marquer_rencontre_vue(&"e5_autre")
	var croix := _etape.trouver_declencheur(&"e5_sentier")
	watch_signals(croix)
	_etape._sur_retour_de_boucle(_passage("Continuer"), &"boucle")
	await wait_process_frames(2)
	assert_signal_emitted(croix, "dialogue_commence")
	DialogueManager.dialogue_ended.emit(croix.dialogue)


func test_plus_aucun_emplacement_reserve() -> void:
	# La durée convient (GD, 2026-11-15) : les emplacements de détails réservés sont libérés.
	assert_eq(_etape.find_children("reserve_detail_*", "", true, false).size(), 0)


func test_aucun_placeholder_rouge() -> void:
	for n in _etape.find_children("*", "ColorRect", true, false):
		var c := (n as ColorRect).color
		assert_false(c.r - maxf(c.g, c.b) > 0.15, "placeholder rouge : %s" % _etape.get_path_to(n))


func test_le_bout_du_sentier_ramene_devant_la_croix() -> void:
	var continuer := _passage("Continuer")
	assert_true(continuer.est_disponible())
	assert_eq(continuer.fondu_noir, 0.0, "la boucle se fait sans fondu")
	var arrivee := continuer.trouver_arrivee()
	assert_eq(arrivee.name, &"boucle_debut")
	var croix := _etape.trouver_declencheur(&"e5_sentier")
	assert_lt(arrivee.global_position.x, croix.global_position.x, "on revient avant la croix")


func test_les_ronces_forcent_la_croix_au_premier_passage() -> void:
	var ronces := _etape.find_child("Ronces", true, false) as Verrou
	assert_eq(ronces.rencontre, &"e5_entaille")
	var croix := _etape.trouver_declencheur(&"e5_sentier")
	assert_gt(ronces.global_position.x, croix.global_position.x)


func test_la_sortie_s_ouvre_au_second_passage() -> void:
	var sortie := _passage("QuitterSentier")
	assert_false(sortie.est_disponible())
	GameState.marquer_rencontre_vue(&"e5_entaille")
	assert_false(sortie.est_disponible(), "pas au premier passage")
	GameState.marquer_rencontre_vue(&"e5_sentier")
	assert_true(sortie.est_disponible())
	assert_eq(sortie.trouver_arrivee().name, &"entree_campement")


func test_la_clairiere_s_ouvre_sur_le_cimetiere() -> void:
	var mur := _etape.find_child("MurClairiere", true, false) as Verrou
	assert_eq(mur.rencontre, &"e5_croix")


func test_pas_de_zone_sombre() -> void:
	var zones := get_tree().get_nodes_in_group(&"zones_sombres").filter(
		func(n: Node) -> bool: return _etape.is_ancestor_of(n))
	assert_eq(zones.size(), 0)


func test_le_messager_demarre_a_l_oree() -> void:
	var depart: Marker2D = _etape.find_child("entree_oree", true, false)
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


func test_le_raccord_de_boucle_et_les_ambiances_de_la_foret() -> void:
	assert_eq(_passage("Continuer").son, "sfx_boucle_raccord", "même oiseau, même craquement")
	for zone in ["Oree", "Boucle", "Campement", "Cimetiere", "Clairiere"]:
		var son := _etape.get_node_or_null("Surface/%s/SonZone" % zone) as AudioStreamPlayer2D
		assert_not_null(son, "%s sans ambiance" % zone)
		if son != null:
			assert_eq(son.bus, &"Ambiance", zone)
			assert_true(son.autoplay, zone)
			assert_true(son.stream.resource_path.contains("amb_foret-de-croix_"), zone)
	assert_eq((_etape.get_node("Surface/Cimetiere/SonZone") as AudioStreamPlayer2D).volume_db, -3.0)
