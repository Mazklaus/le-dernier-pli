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
	var nb: int = gs.marques.filter(func(m: Dictionary) -> bool: return m["id"] == &"la_faim").size()
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

func test_gestes_sceau_interdits_a_l_etape_1() -> void:
	assert_false(gs.rechauffer_sceau())
	assert_false(gs.ouvrir_sceau())
	assert_eq(gs.lire_ligne_pli(), -1)
	assert_eq(gs.huile, 4)
	gs.abimer_sceau()
	assert_true(gs.sceau_abime, "abîmer est un accident, possible dès l'étape 1")


func test_rechauffer_coute_une_huile_et_implique_abime() -> void:
	gs.passer_etape()
	assert_true(gs.rechauffer_sceau())
	assert_eq(gs.huile, 3)
	assert_true(gs.sceau_abime)
	assert_true(gs.sceau_rechauffe)


func test_rechauffer_gratuit_sans_huile_ni_prelevement() -> void:
	gs.passer_etape()
	gs.modifier_jauge(&"huile", 2)
	assert_eq(gs.huile, 6, "huile au maximum")
	assert_true(gs.rechauffer_sceau(true))
	assert_eq(gs.huile, 6, "rien de prélevé")
	assert_true(gs.sceau_rechauffe)
	assert_true(gs.sceau_abime)
	gs.reinitialiser()
	gs.passer_etape()
	gs.modifier_jauge(&"huile", -10)
	assert_false(gs.peut_rechauffer_sceau(), "payant : il faut 1 Huile")
	assert_true(gs.peut_rechauffer_sceau(true), "gratuit : possible sans Huile")


func test_lignes_du_pli_dans_l_ordre_une_par_etape() -> void:
	gs.passer_etape()
	gs.rechauffer_sceau()
	assert_eq(gs.lire_ligne_pli(), 0)
	assert_eq(gs.lire_ligne_pli(), -1, "une seule ligne par étape")
	gs.passer_etape()
	assert_eq(gs.lire_ligne_pli(), 1)
	assert_eq(gs.pli_lignes_lues, 2)
	assert_eq(gs.huile, 1)


func test_six_lignes_au_plus() -> void:
	gs.passer_etape()
	gs.rechauffer_sceau()
	for i in 6:
		gs.modifier_jauge(&"huile", 10)
		gs.modifier_jauge(&"vivres", 10)
		assert_eq(gs.lire_ligne_pli(), i)
		gs.passer_etape()
	gs.modifier_jauge(&"huile", 10)
	assert_eq(gs.pli_lignes_lues, 6)
	assert_eq(gs.lire_ligne_pli(), -1)


func test_drapeaux_du_sceau_irreversibles() -> void:
	gs.passer_etape()
	gs.abimer_sceau()
	assert_true(gs.ouvrir_sceau())
	assert_false(gs.ouvrir_sceau())
	assert_true(gs.sceau_abime)
	assert_true(gs.sceau_ouvert)


# --- Objets et promesses ---

func test_pain_promis_mange_trahit_la_promesse() -> void:
	gs.ajouter_marque(&"promis_jacquot", Marques.PROMESSE)
	gs.ajouter_objet(&"pain_jacquot")
	assert_true(gs.manger_objet_promis(&"pain_jacquot", 2, &"promis_jacquot"))
	assert_eq(gs.vivres, 8)
	assert_false(gs.possede_objet(&"pain_jacquot"))
	assert_eq(gs.trouver_marque(&"promis_jacquot")["etat"], Marques.TRAHIE)
	assert_false(gs.manger_objet_promis(&"pain_jacquot", 2, &"promis_jacquot"))


func test_promesses_resolues_avant_fin() -> void:
	gs.ajouter_marque(&"p1", Marques.PROMESSE)
	gs.ajouter_marque(&"p2", Marques.PROMESSE)
	gs.ajouter_marque(&"p3", Marques.PROMESSE)
	gs.resoudre_promesses_avant_fin({"p1": true, "p2": false})
	assert_eq(gs.trouver_marque(&"p1")["etat"], Marques.TENUE)
	assert_eq(gs.trouver_marque(&"p2")["etat"], Marques.TRAHIE)
	assert_eq_deep(gs.promesses_ouvertes(), [&"p3"] as Array[StringName])


# --- Conditions et coûts affichés ---

func test_conditions() -> void:
	gs.ajouter_marque(&"doigt_de_saint", Marques.RELIQUE)
	assert_true(gs.condition_remplie({"jauge_min": {"huile": 4}, "marque": "doigt_de_saint", "sceau": "ferme", "palier": "clair"}))
	assert_false(gs.condition_remplie({"jauge_min": {"huile": 5}}))
	assert_false(gs.condition_remplie({"marque": "inconnue"}))
	assert_false(gs.condition_remplie({"sceau": "ouvert"}))
	assert_false(gs.condition_remplie({"palier": "egare"}))


func test_condition_objet() -> void:
	assert_false(gs.condition_remplie({"objet": "pain_jacquot"}))
	gs.ajouter_objet(&"pain_jacquot")
	assert_true(gs.condition_remplie({"objet": "pain_jacquot"}))


func test_couts_affiches_exacts_hors_egare() -> void:
	var options := [{"vivres": 2}, {}, {"huile": 1}]
	var affiches: Array[Dictionary] = gs.couts_affiches_rencontre(options)
	for i in options.size():
		assert_eq_deep(affiches[i]["couts"], options[i])
		assert_false(affiches[i]["cout_douteux"])


func test_cout_faux_jamais_affiche_a_zero() -> void:
	# #30 : un vrai coût de 1 qui ment vers le bas afficherait « −0 » et trahirait le mensonge.
	gs.modifier_jauge(&"lucidite", -6)
	var options := [{"vivres": 1}, {"huile": 1}]
	var rng := RandomNumberGenerator.new()
	rng.seed = 7
	var nb_faux := 0
	for essai in 200:
		var affiches: Array[Dictionary] = gs.couts_affiches_rencontre(options, rng)
		for i in options.size():
			for cle in affiches[i]["couts"]:
				assert_true(int(affiches[i]["couts"][cle]) >= 1, "coût affiché à 0")
			if affiches[i]["cout_faux"]:
				nb_faux += 1
	assert_gt(nb_faux, 50, "le tirage ment bien")


func test_couts_affiches_en_egare_tirage_par_rencontre() -> void:
	gs.modifier_jauge(&"lucidite", -6)
	var options := [{"vivres": 1}, {}, {"huile": 0, "vivres": 2}, {"huile": 1}]
	var rng := RandomNumberGenerator.new()
	rng.seed = 42
	var nb_mensonge := 0
	var nb_leurre_seul := 0
	var nb_rien := 0
	for essai in 400:
		var affiches: Array[Dictionary] = gs.couts_affiches_rencontre(options, rng)
		var douteuses := 0
		var faux := 0
		for i in options.size():
			var vrai: Dictionary = options[i]
			var vu: Dictionary = affiches[i]["couts"]
			if affiches[i]["cout_douteux"]:
				douteuses += 1
				assert_false(vrai.is_empty(), "une option sans coût ne bave jamais")
			if affiches[i]["cout_faux"]:
				faux += 1
				assert_true(affiches[i]["cout_douteux"], "un coût faux bave toujours")
				var ecarts := 0
				for cle in vrai:
					assert_true(int(vu[cle]) >= 0)
					ecarts += absi(int(vu[cle]) - int(vrai[cle]))
				assert_eq(ecarts, 1, "exactement un coût faux de 1")
			else:
				assert_eq_deep(vu, vrai)
		if faux == 1:
			assert_eq(douteuses, 2, "un mensonge vient toujours avec un leurre")
			nb_mensonge += 1
		elif douteuses == 1:
			nb_leurre_seul += 1
		else:
			assert_eq([douteuses, faux], [0, 0])
			nb_rien += 1
	assert_between(nb_mensonge, 160, 240, "environ 50 %")
	assert_between(nb_leurre_seul, 70, 130, "environ 25 %")
	assert_between(nb_rien, 70, 130, "environ 25 %")
	assert_eq(options[0]["vivres"], 1, "les coûts réels ne sont jamais modifiés")


func test_un_seul_cout_affiche_ne_ment_jamais() -> void:
	gs.modifier_jauge(&"lucidite", -6)
	var options := [{"vivres": 2}, {}, {}]
	var rng := RandomNumberGenerator.new()
	rng.seed = 7
	for essai in 50:
		var affiches: Array[Dictionary] = gs.couts_affiches_rencontre(options, rng)
		for i in options.size():
			assert_false(affiches[i]["cout_douteux"])
			assert_eq_deep(affiches[i]["couts"], options[i])


func test_rencontres_vues() -> void:
	assert_false(gs.rencontre_vue(&"e1_cendre"))
	assert_false(gs.condition_remplie({"rencontre_vue": "e1_cendre"}))
	gs.marquer_rencontre_vue(&"e1_cendre")
	gs.marquer_rencontre_vue(&"e1_cendre")
	assert_true(gs.rencontre_vue(&"e1_cendre"))
	assert_true(gs.condition_remplie({"rencontre_vue": "e1_cendre"}))
	assert_eq(gs.rencontres_vues.size(), 1)


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
	gs.ajouter_objet(&"objet_d_ombre")
	gs.marquer_rencontre_vue(&"e1_cendre")
	gs.passer_etape()
	gs.rechauffer_sceau()
	gs.lire_ligne_pli()
	var json := JSON.stringify(gs.vers_dictionnaire())
	var autre: Node = autofree(GameStateScript.new())
	watch_signals(autre)
	autre.depuis_dictionnaire(JSON.parse_string(json))
	assert_signal_emitted(autre, "etat_charge")
	assert_eq_deep(autre.vers_dictionnaire(), gs.vers_dictionnaire())
	assert_eq(autre.lucidite_max, 3)
	assert_false(autre.ajouter_marque(&"autre", Marques.RELIQUE, &"camarade"))
