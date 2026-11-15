extends GutTest
## Maquette grise de l'étape 7 (le Destinataire) : la descente en spirale le long de la plus
## grande cloche. Galerie en surface, puis trois anneaux superposés et la salle sous la
## Mère-Cloche. Chaque anneau s'ouvre sur le suivant après sa rencontre ; aucun retour vers le haut.

const ETAPE := preload("res://scenes/etapes/etape_07/etape_07.tscn")
const RENCONTRES: Array[StringName] = [&"e7_cloches", &"e7_lise", &"e7_sceau", &"e7_mere_cloche"]
const DETAILS: Array[String] = ["cloches_battants", "lise_lettre", "porte_cire"]
## Passage vers l'anneau suivant → rencontre qui l'ouvre, et marqueur d'arrivée attendu.
const DESCENTE := {
	"VersAnneauLise": [&"e7_cloches", &"entree_anneau_lise"],
	"VersAnneauPorte": [&"e7_lise", &"entree_anneau_porte"],
	"VersMereCloche": [&"e7_sceau", &"entree_mere_cloche"],
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
		assert_not_null(_etape.trouver_declencheur(StringName("e7_detail_%s" % nom)), nom)


func test_seule_la_mere_cloche_termine_l_etape() -> void:
	for id in RENCONTRES:
		assert_eq(_etape.trouver_declencheur(id).fin_etape, id == &"e7_mere_cloche", String(id))


func test_chaque_anneau_s_ouvre_apres_sa_rencontre() -> void:
	for nom in DESCENTE:
		var p := _passage(nom)
		assert_not_null(p, nom)
		assert_eq(p.rencontre_requise, DESCENTE[nom][0], nom)
		assert_false(p.est_disponible(), "%s fermé au départ" % nom)
		GameState.marquer_rencontre_vue(DESCENTE[nom][0])
		assert_true(p.est_disponible(), nom)
		assert_eq(p.trouver_arrivee().name, DESCENTE[nom][1], nom)
		assert_eq(p.fondu_noir, 0.0, "%s : on passe derrière la cloche, sans fondu" % nom)


func test_la_spirale_descend_toujours() -> void:
	for nom in DESCENTE:
		var p := _passage(nom)
		assert_gt(p.trouver_arrivee().global_position.y, p.global_position.y,
			"%s doit mener plus bas" % nom)


func test_aucun_retour_vers_le_haut() -> void:
	for n in _etape.find_children("*", "Area2D", true, false):
		if n is Passage:
			var p := n as Passage
			var arrivee := p.trouver_arrivee()
			if arrivee != null:
				assert_true(arrivee.global_position.y >= p.global_position.y,
					"%s remonte" % p.name)


func test_le_messager_demarre_dans_la_galerie() -> void:
	var depart: Marker2D = _etape.find_child("entree_galerie", true, false)
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
