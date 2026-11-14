extends GutTest
## Maquette grise de l'étape 1 : chaque rencontre du plan de niveau a son
## DeclencheurDialogue réglé, chaque lieu souterrain ses points d'entrée et de sortie,
## et le messager démarre dans la couchette.

const ETAPE := preload("res://scenes/etapes/etape_01/etape_01.tscn")
const RENCONTRES: Array[StringName] = [
	&"e1_reveil", &"e1_ordre", &"e1_cantine", &"e1_cendre",
	&"e1_guetteur", &"e1_sape", &"e1_adieu", &"e1_parapet",
]
const LIEUX: Array[String] = [
	"couchette", "abri_sergent", "cantine", "chapelle", "vieille_sape", "sape_sortie",
]

var _etape: EtapeBase


func before_each() -> void:
	_etape = ETAPE.instantiate()
	add_child_autofree(_etape)


func test_chaque_rencontre_a_un_declencheur_avec_son_dialogue() -> void:
	for id in RENCONTRES:
		var declencheur := _etape.trouver_declencheur(id)
		assert_not_null(declencheur, "déclencheur manquant : %s" % id)
		if declencheur != null:
			assert_not_null(declencheur.dialogue, "dialogue manquant : %s" % id)
			assert_true(declencheur.libelle.length() <= 24, "libellé trop long : %s" % id)


func test_jacquot_bloque_sans_la_cendre() -> void:
	var adieu := _etape.trouver_declencheur(&"e1_adieu")
	assert_eq(adieu.rencontre_requise, &"e1_cendre")
	assert_eq(adieu.titre_si_verrouille, "refus_sans_cendre")


func test_le_parapet_termine_l_etape() -> void:
	assert_true(_etape.trouver_declencheur(&"e1_parapet").fin_etape)


func test_chaque_lieu_a_ses_points_entree_et_sortie() -> void:
	for lieu in LIEUX:
		assert_not_null(_etape.find_child("entree_%s" % lieu, true, false), "entree_%s" % lieu)
		assert_not_null(_etape.find_child("sortie_%s" % lieu, true, false), "sortie_%s" % lieu)


func test_une_seule_zone_sombre() -> void:
	var zones := get_tree().get_nodes_in_group(&"zones_sombres").filter(
		func(n: Node) -> bool: return _etape.is_ancestor_of(n))
	assert_eq(zones.size(), 1)


func test_le_messager_demarre_dans_la_couchette() -> void:
	var messager := _etape.trouver_messager()
	var depart: Marker2D = _etape.find_child("entree_couchette", true, false)
	assert_not_null(messager)
	assert_eq(messager.global_position, depart.global_position)


func test_chaque_passage_a_une_arrivee_et_un_libelle() -> void:
	var passages := get_tree().get_nodes_in_group(&"passages").filter(
		func(n: Node) -> bool: return _etape.is_ancestor_of(n))
	assert_eq(passages.size(), 13)
	for p in passages:
		var passage := p as Passage
		assert_not_null(passage, "%s n'a pas le script Passage" % p.name)
		if passage != null:
			assert_not_null(passage.trouver_arrivee(), "pas d'arrivée pour %s" % passage.name)
			assert_true(passage.libelle != "" and passage.libelle.length() <= 24, "libellé de %s" % passage.name)


func test_le_retour_d_un_lieu_arrive_devant_sa_porte() -> void:
	var retour: Passage = _etape.find_child("PassageCantine", true, false)
	assert_eq(retour.trouver_arrivee().name, &"porte_cantine")


func test_les_verrous_s_ouvrent_apres_leur_rencontre() -> void:
	GameState.reinitialiser()
	var chicane: Verrou = _etape.find_child("Chicane", true, false)
	var cendre: Verrou = _etape.find_child("VerrouCendre", true, false)
	assert_eq(chicane.rencontre, &"e1_ordre")
	# L'adieu de Jacquot est obligatoire : il ne se joue qu'avec la Cendre (rencontre_requise).
	assert_eq(cendre.rencontre, &"e1_adieu")
	assert_false(chicane.est_ouvert())
	GameState.marquer_rencontre_vue(&"e1_ordre")
	assert_true(chicane.est_ouvert())
	assert_false(cendre.est_ouvert())
	GameState.marquer_rencontre_vue(&"e1_cendre")
	assert_false(cendre.est_ouvert(), "la Cendre seule ne suffit plus : il faut l'adieu")
	GameState.marquer_rencontre_vue(&"e1_adieu")
	assert_true(cendre.est_ouvert())
	GameState.reinitialiser()


func test_le_reveil_est_a_portee_des_le_depart() -> void:
	var depart: Marker2D = _etape.find_child("entree_couchette", true, false)
	var reveil := _etape.trouver_declencheur(&"e1_reveil")
	assert_true(absf(reveil.global_position.x - depart.global_position.x) < 96.0)


func test_on_ne_quitte_pas_la_couchette_sans_le_reveil() -> void:
	GameState.reinitialiser()
	var sortie: Passage = _etape.find_child("SortieCouchette", true, false)
	assert_false(sortie.est_disponible())
	GameState.marquer_rencontre_vue(&"e1_reveil")
	assert_true(sortie.est_disponible())
	GameState.reinitialiser()


const DETAILS: Array[String] = [
	"couchette_lettre", "couchette_abecedaire", "boyau_chuchoteurs", "boyau_ecriteau",
	"abri_carte", "abri_gamelle", "carrefour_croix", "carrefour_cloches",
	"cantine_tableau", "chapelle_ex_voto", "sortie_sifflet", "echelle_barreaux",
]


func test_chaque_detail_est_un_declencheur_rejouable() -> void:
	for nom in DETAILS:
		var detail := _etape.trouver_declencheur(StringName("e1_detail_%s" % nom))
		assert_not_null(detail, "détail manquant : %s" % nom)
		if detail != null:
			assert_eq(detail.titre, nom)
			assert_eq(detail.dialogue.resource_path, "res://dialogue/etape_01/e1_details.dialogue")
			assert_has(detail.dialogue.get_cues(), nom, "titre absent du dialogue : %s" % nom)
			assert_false(detail.une_seule_fois, "%s doit rester rejouable" % nom)
			assert_false(detail.fin_etape)
			assert_eq(detail.rencontre_requise, &"")
			assert_true(detail.libelle != "" and detail.libelle.length() <= 24, "libellé de %s" % nom)


func test_aucun_detail_ne_chevauche_un_autre_point_d_interaction() -> void:
	var points: Array[Node2D] = []
	for n in _etape.find_children("*", "Area2D", true, false):
		if n is DeclencheurDialogue or n is Passage:
			points.append(n)
	for a in points:
		if not String(a.name).begins_with("e1_detail_"):
			continue
		for b in points:
			if a == b or absf(a.global_position.y - b.global_position.y) > 400.0:
				continue
			assert_true(absf(a.global_position.x - b.global_position.x) >= 200.0,
				"%s trop près de %s" % [a.name, b.name])


func test_les_rencontres_ne_se_rejouent_pas_sauf_le_guetteur() -> void:
	for id in RENCONTRES:
		var attendu := id != &"e1_guetteur"
		assert_eq(_etape.trouver_declencheur(id).une_seule_fois, attendu, "une_seule_fois de %s" % id)
