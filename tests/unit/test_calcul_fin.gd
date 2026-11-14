extends GutTest
## Tests de la fonction pure de fin (spec jauges v0.1, § Calcul de la fin).


func _m(id: String, famille: StringName, etat: StringName = &"") -> Dictionary:
	var m := Marques.creer(StringName(id), famille)
	if etat != &"":
		m["etat"] = etat
	return m


func test_aucune_marque_egalite_penche_vers_visage() -> void:
	assert_eq(CalculFin.calculer([], false), CalculFin.FIN_PORTEUR)
	assert_eq(CalculFin.calculer([], true), CalculFin.FIN_DERNIER_PLI)


func test_les_quatre_fins() -> void:
	var visage := [_m("tibere", Marques.NOM_RETENU)]
	var ombre := [_m("la_faim", Marques.CICATRICE)] + [_m("doigt", Marques.RELIQUE)]
	ombre.append(_m("x", Marques.NOM_RETENU))
	assert_eq(CalculFin.calculer(visage, false), CalculFin.FIN_PORTEUR)
	assert_eq(CalculFin.calculer(ombre, false), CalculFin.FIN_ORDRE)
	assert_eq(CalculFin.calculer(visage, true), CalculFin.FIN_DERNIER_PLI)
	assert_eq(CalculFin.calculer(ombre, true), CalculFin.FIN_RECOUSU)


func test_egalite_stricte_donne_visage() -> void:
	var marques := [_m("a", Marques.NOM_RETENU), _m("b", Marques.CICATRICE)]
	assert_eq(CalculFin.score_visage(marques), 1)
	assert_eq(CalculFin.score_ombre(marques), 1)
	assert_true(CalculFin.garde_un_visage(marques))


func test_promesses_selon_etat() -> void:
	var ouverte := _m("p1", Marques.PROMESSE)
	var tenue := _m("p2", Marques.PROMESSE, Marques.TENUE)
	var trahie := _m("p3", Marques.PROMESSE, Marques.TRAHIE)
	assert_eq(CalculFin.score_visage([ouverte]), 0, "une promesse ouverte compte 0")
	assert_eq(CalculFin.score_ombre([ouverte]), 0, "une promesse ouverte compte 0")
	assert_eq(CalculFin.score_visage([tenue]), 1)
	assert_eq(CalculFin.score_ombre([tenue]), 0)
	assert_eq(CalculFin.score_visage([trahie]), 0)
	assert_eq(CalculFin.score_ombre([trahie]), 1)


func test_reliques_comptent_en_ombre() -> void:
	var marques := [_m("obei", Marques.RELIQUE), _m("medaille", Marques.RELIQUE), _m("aubert", Marques.NOM_RETENU)]
	assert_eq(CalculFin.score_ombre(marques), 2)
	assert_eq(CalculFin.calculer(marques, false), CalculFin.FIN_ORDRE)


func test_fonction_pure_ne_modifie_pas_ses_entrees() -> void:
	var marques := [_m("a", Marques.PROMESSE, Marques.TENUE)]
	var copie := marques.duplicate(true)
	CalculFin.calculer(marques, true)
	assert_eq_deep(marques, copie)


func test_marques_relues_en_string_apres_sauvegarde() -> void:
	# Après un aller-retour JSON, les StringName deviennent des String.
	var marques := [{"id": "a", "famille": "nom_retenu", "etat": ""}, {"id": "b", "famille": "promesse", "etat": "trahie"}, {"id": "c", "famille": "cicatrice", "etat": ""}]
	assert_eq(CalculFin.score_visage(marques), 1)
	assert_eq(CalculFin.score_ombre(marques), 2)
	assert_eq(CalculFin.calculer(marques, false), CalculFin.FIN_ORDRE)
