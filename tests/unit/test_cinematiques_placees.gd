extends GutTest
## Placement des cinématiques par le Level Designer (directive animation du Game Director) :
## les neuf plans de départ, puis le lot 1 de l'arbitrage du 17/11 (plus de limite à deux par étape).

const PLANS := {
	1: [&"e1_remise_pli", &"e1_sortie_tranchee"],
	2: [&"e2_barbeles_foncer"],
	3: [&"e3_procession_nuit", &"e3_priere_champs", &"e3_danse_rose"],
	4: [&"e4_greffe", &"e4_descente_crypte"],
	5: [&"e5_autre_se_retourne"],
	6: [&"e6_chute_fissure", &"e6_eboulement", &"e6_village_sous_terre", &"e6_porte_scellee"],
	7: [&"e7_descente", &"e7_ouverture_sceau", &"e7_mere_cloche", &"e7_moule_brise", &"e7_corde_tiree"],
}
## Seul l'éboulement n'a pas de réplique : il part d'une Zone à l'entrée du village.
const PAR_ZONE: Array[StringName] = [&"e6_eboulement"]
const AU_DEBUT: Array[StringName] = []


func _etape(numero: int) -> Node:
	var scene := load("res://scenes/etapes/etape_%02d/etape_%02d.tscn" % [numero, numero]) as PackedScene
	var etape := scene.instantiate()
	add_child_autofree(etape)
	return etape


func _cines(etape: Node) -> Array[Cinematique]:
	var liste: Array[Cinematique] = []
	for n in etape.find_children("*", "Node2D", true, false):
		if n is Cinematique:
			liste.append(n)
	return liste


func test_chaque_plan_est_place_dans_son_etape() -> void:
	for numero in range(1, 8):
		var cines := _cines(_etape(numero))
		var attendus: Array = PLANS.get(numero, [])
		assert_eq(cines.size(), attendus.size(), "étape %d" % numero)
		for c in cines:
			assert_has(attendus, c.id, "étape %d : %s inattendue" % [numero, c.id])
			assert_true(String(c.id).begins_with("e%d_" % numero), String(c.id))


func test_chaque_plan_a_sa_camera_et_son_cadrage() -> void:
	for numero in PLANS:
		for c in _cines(_etape(numero)):
			assert_true(c.get_node_or_null("Camera") is Camera2D, "%s sans caméra" % c.id)
			assert_true(c.get_node_or_null("Depart") is Marker2D, "%s sans cadrage" % c.id)
			assert_between(c.duree, 5.0, 15.0, "%s : 5 à 15 s" % c.id)
			assert_true(c.une_seule_fois, String(c.id))


func test_les_plans_sans_replique_ont_leur_declencheur() -> void:
	for numero in [6, 7]:
		for c in _cines(_etape(numero)):
			var zone := c.get_node_or_null("Zone") as Area2D
			if c.id in PAR_ZONE:
				assert_not_null(zone, "%s sans Zone" % c.id)
				if zone != null:
					assert_eq(zone.collision_mask, 1, "%s : la Zone voit le messager" % c.id)
			else:
				assert_null(zone, String(c.id))
			assert_eq(c.au_debut_etape, c.id in AU_DEBUT, String(c.id))


func test_les_personnages_vises_par_les_gestes_portent_leur_nom() -> void:
	# Les répliques [#geste=…] visent un personnage par ce nom (Narrative Designer).
	var attendus := {
		2: {&"e2_mort": &"mort"}, 3: {&"e3_lisiere": &"enfants", &"e3_ilde": &"ilde"},
		4: {&"e4_porche": &"maude", &"e4_salle": &"fernand"}, 6: {&"e6_eloi": &"eloi", &"e6_veilleur": &"mathurin", &"e6_seuil": &"eloi"},
		7: {&"e7_lise": &"lise", &"e7_mere_cloche": &"mere-cloche"},
	}
	for numero in attendus:
		var etape := _etape(numero) as EtapeBase
		for id in attendus[numero]:
			var d := etape.trouver_declencheur(id)
			assert_not_null(d, String(id))
			if d != null:
				assert_eq(d.personnage, attendus[numero][id], String(id))
