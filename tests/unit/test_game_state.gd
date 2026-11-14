extends GutTest
## Tests des bornes et des règles de jauges de GameState (spec jauges v0.1).

const GameStateScript := preload("res://autoload/game_state.gd")

var gs: Node


func before_each() -> void:
	gs = autofree(GameStateScript.new())


# --- Départ et bornes ---

func test_valeurs_de_depart() -> void:
	assert_eq(gs.vivres, 6)
	assert_eq(gs.huile, 4)
	assert_eq(gs.lucidite, 8)
	assert_eq(gs.lucidite_max, 10)
	assert_eq(gs.palier, &"clair")
	assert_false(gs.sceau_abime or gs.sceau_rechauffe or gs.sceau_ouvert)
	assert_eq(gs.etape, 1)


func test_bornes_hautes() -> void:
	gs.modifier_jauge(&"vivres", 50)
	gs.modifier_jauge(&"huile", 50)
	gs.modifier_jauge(&"lucidite", 50)
	assert_eq(gs.vivres, 10)
	assert_eq(gs.huile, 6)
	assert_eq(gs.lucidite, 10)


func test_bornes_basses() -> void:
	gs.modifier_jauge(&"huile", -50)
	gs.modifier_jauge(&"lucidite", -50)
	assert_eq(gs.huile, 0)
	assert_eq(gs.lucidite, 0)


func test_jauge_inconnue_ignoree() -> void:
	gs.modifier_jauge(&"or", 3)
	assert_push_error("Jauge inconnue")
	assert_eq(gs.vivres, 6)


func test_signal_jauge_changee() -> void:
	watch_signals(gs)
	gs.modifier_jauge(&"vivres", -2)
	assert_signal_emitted_with_parameters(gs, "jauge_changee", [&"vivres", 6, 4])


func test_pas_de_signal_si_deja_a_la_borne() -> void:
	gs.modifier_jauge(&"huile", 10)
	watch_signals(gs)
	gs.modifier_jauge(&"huile", 1)
	assert_signal_not_emitted(gs, "jauge_changee")


# --- Vivres et Affamé ---

func test_vivres_a_zero_affame_et_marque_la_faim_une_fois() -> void:
	watch_signals(gs)
	gs.modifier_jauge(&"vivres", -6)
	assert_true(gs.est_affame())
	assert_signal_emitted_with_parameters(gs, "etat_declenche", [&"affame"])
	assert_true(gs.possede_marque(&"la_faim"))
	gs.modifier_jauge(&"vivres", 2)
	gs.modifier_jauge(&"vivres", -2)
	var nb: int = gs.marques.filter(func(m): return m["id"] == &"la_faim").size()
	assert_eq(nb, 1, "La faim n'est gagnée que la première fois")


func test_cout_vivres_impayable_devient_moins_une_lucidite() -> void:
	gs.modifier_jauge(&"vivres", -6)
	var luc: int = gs.lucidite
	gs.appliquer_couts({"vivres": 1})
	assert_eq(gs.vivres, 0)
	assert_eq(gs.lucidite, luc - 1)


func test_cout_vivres_partiellement_payable() -> void:
	gs.modifier_jauge(&"vivres", -5)  # reste 1
	gs.appliquer_couts({"vivres": 2})
	assert_eq(gs.vivres, 0)
	assert_eq(gs.lucidite, 7, "un coût impayable, même en partie, vaut −1 Lucidité")


# --- Lucidité, paliers et Perdu ---

func test_paliers() -> void:
	assert_eq(gs.palier_pour(10), &"clair")
	assert_eq(gs.palier_pour(7), &"clair")
	assert_eq(gs.palier_pour(6), &"trouble")
	assert_eq(gs.palier_pour(4), &"trouble")
	assert_eq(gs.palier_pour(3), &"egare")
	assert_eq(gs.palier_pour(1), &"egare")
	assert_eq(gs.palier_pour(0), &"egare")


func test_palier_recalcule_et_signal() -> void:
	watch_signals(gs)
	gs.modifier_jauge(&"lucidite", -2)
	assert_eq(gs.palier, &"trouble")
	assert_signal_emitted_with_parameters(gs, "palier_change", [&"clair", &"trouble"])


func test_perdu_plafonne_lucidite_a_3() -> void:
	gs.modifier_jauge(&"lucidite", -8)
	assert_true(gs.est_perdu())
	assert_eq(gs.lucidite_max, 3)
	assert_true(gs.possede_marque(&"ce_qui_a_ete_vu"))
	gs.modifier_jauge(&"lucidite", 10)
	assert_eq(gs.lucidite, 3)
	assert_eq(gs.palier, &"egare")


# --- Huile et zones sombres ---

func test_zone_sombre_allumee_coute_une_huile() -> void:
	assert_true(gs.entrer_zone_sombre(true))
	assert_eq(gs.huile, 3)
	assert_eq(gs.lucidite, 8)


func test_zone_sombre_noir_coute_une_lucidite() -> void:
	assert_false(gs.entrer_zone_sombre(false))
	assert_eq(gs.huile, 4)
	assert_eq(gs.lucidite, 7)


func test_derniere_goutte_eclaire_la_zone() -> void:
	gs.modifier_jauge(&"huile", -3)
	assert_true(gs.entrer_zone_sombre(true))
	assert_eq(gs.huile, 0)


func test_sans_huile_noir_force() -> void:
	gs.modifier_jauge(&"huile", -4)
	assert_false(gs.entrer_zone_sombre(true))
	assert_eq(gs.lucidite, 7)


# --- Marques ---

func test_une_marque_par_rencontre() -> void:
	assert_true(gs.ajouter_marque(&"obei", Marques.RELIQUE, &"officier"))
	assert_false(gs.ajouter_marque(&"l_officier", Marques.NOM_RETENU, &"officier"))
	assert_eq(gs.marques.size(), 1)


func test_marque_jamais_en_double() -> void:
	gs.ajouter_marque(&"tibere", Marques.NOM_RETENU)
	assert_false(gs.ajouter_marque(&"tibere", Marques.NOM_RETENU))


func test_promesse_resolue_une_seule_fois() -> void:
	gs.ajouter_marque(&"promis_aubert", Marques.PROMESSE)
	assert_eq(gs.trouver_marque(&"promis_aubert")["etat"], Marques.OUVERTE)
	assert_true(gs.resoudre_promesse(&"promis_aubert", true))
	assert_false(gs.resoudre_promesse(&"promis_aubert", false))
	assert_eq(gs.trouver_marque(&"promis_aubert")["etat"], Marques.TENUE)


# --- Sceau ---

func test_rechauffer_coute_une_huile_et_implique_abime() -> void:
	assert_true(gs.rechauffer_sceau())
	assert_eq(gs.huile, 3)
	assert_true(gs.sceau_abime)
	assert_true(gs.sceau_rechauffe)


func test_une_ligne_du_pli_par_etape() -> void:
	gs.rechauffer_sceau()
	assert_true(gs.lire_ligne_pli())
	assert_false(gs.lire_ligne_pli())
	gs.passer_etape()
	assert_true(gs.lire_ligne_pli())
	assert_eq(gs.huile, 1)


func test_drapeaux_du_sceau_irreversibles() -> void:
	gs.abimer_sceau()
	gs.ouvrir_sceau()
	gs.abimer_sceau()
	assert_true(gs.sceau_abime)
	assert_true(gs.sceau_ouvert)


# --- Conditions et coûts affichés ---

func test_conditions() -> void:
	gs.ajouter_marque(&"doigt_de_saint", Marques.RELIQUE)
	assert_true(gs.condition_remplie({"jauge_min": {"huile": 4}, "marque": "doigt_de_saint", "sceau": "ferme", "palier": "clair"}))
	assert_false(gs.condition_remplie({"jauge_min": {"huile": 5}}))
	assert_false(gs.condition_remplie({"marque": "inconnue"}))
	assert_false(gs.condition_remplie({"sceau": "ouvert"}))
	assert_false(gs.condition_remplie({"palier": "egare"}))


func test_couts_affiches_exacts_hors_egare() -> void:
	var couts := {"vivres": 2, "huile": 1}
	assert_eq_deep(gs.couts_affiches(couts), couts)


func test_couts_affiches_au_plus_faux_de_un_en_egare() -> void:
	gs.modifier_jauge(&"lucidite", -6)
	var rng := RandomNumberGenerator.new()
	rng.seed = 42
	for i in 50:
		var affiches: Dictionary = gs.couts_affiches({"vivres": 1}, rng)
		assert_between(int(affiches["vivres"]), 0, 2)


# --- Étapes ---

func test_marche_entre_etapes() -> void:
	gs.passer_etape()  # 1 -> 2 : Vivres seulement
	assert_eq([gs.vivres, gs.lucidite, gs.etape], [5, 8, 2])
	gs.passer_etape()  # 2 -> 3 : Vivres et Lucidité
	assert_eq([gs.vivres, gs.lucidite, gs.etape], [4, 7, 3])


func test_parcours_etape_1_selon_spec() -> void:
	# Partage sa ration, allume, prie : entre en étape 2 à 6 / 3 / 9.
	gs.appliquer_effets({"vivres": 1})        # gamelle
	gs.appliquer_couts({"vivres": 1})         # partage
	gs.entrer_zone_sombre(true)               # sape allumée
	gs.appliquer_effets({"vivres": 1})        # ration trouvée
	gs.appliquer_effets({"lucidite": 1})      # prière
	gs.passer_etape()
	assert_eq([gs.vivres, gs.huile, gs.lucidite], [6, 3, 9])


# --- Sérialisation ---

func test_aller_retour_dictionnaire_json() -> void:
	gs.modifier_jauge(&"lucidite", -8)
	gs.ajouter_marque(&"promis_aubert", Marques.PROMESSE, &"camarade")
	gs.rechauffer_sceau()
	gs.passer_etape()
	var json := JSON.stringify(gs.vers_dictionnaire())
	var autre: Node = autofree(GameStateScript.new())
	autre.depuis_dictionnaire(JSON.parse_string(json))
	assert_eq_deep(autre.vers_dictionnaire(), gs.vers_dictionnaire())
	assert_eq(autre.lucidite_max, 3)
	assert_false(autre.ajouter_marque(&"autre", Marques.RELIQUE, &"camarade"))
