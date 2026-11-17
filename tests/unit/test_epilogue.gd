extends GutTest
## Carton d'épilogue : fin → titre, gravure, Cantique ; Noms retenus et Promesses ouvertes.

const SceneEpilogue := preload("res://scenes/epilogue/epilogue.tscn")


func before_each() -> void:
	GameState.reinitialiser()


func after_each() -> void:
	Epilogue.modele_animation = "res://scripts/epilogue/anim_epilogue_%s.gd"


func after_all() -> void:
	GameState.reinitialiser()


func test_table_des_fins_vers_les_lettres() -> void:
	assert_eq(EpilogueFin.cle(&"porteur", false), "porteur")
	assert_eq(EpilogueFin.cle(&"ordre", true), "ordre")
	assert_eq(EpilogueFin.cle(&"recousu", false), "recousu")
	assert_eq(EpilogueFin.cle(&"dernier_pli", false), "dernier_pli_tribut")
	assert_eq(EpilogueFin.cle(&"dernier_pli", true), "dernier_pli_cloches")
	var attendu := {"porteur": "a", "dernier_pli_tribut": "b", "dernier_pli_cloches": "c",
		"ordre": "d", "recousu": "e"}
	for c: String in attendu:
		assert_eq(EpilogueFin.lettre(c), attendu[c], c)
		assert_true(ResourceLoader.exists(EpilogueFin.gravure(c)), EpilogueFin.gravure(c))
		assert_eq(EpilogueFin.moment(c), "fin-" + attendu[c])


func test_chaque_epilogue_a_ses_lignes() -> void:
	for c: String in EpilogueFin.LETTRES:
		var lignes: PackedStringArray = await Epilogue.lire_lignes(EpilogueFin.DIALOGUE, EpilogueFin.titre(c))
		assert_between(lignes.size(), 4, 8, c)


func test_noms_retenus_et_promesses_ouvertes() -> void:
	var marques := [
		Marques.creer(&"jacquot", Marques.NOM_RETENU),
		Marques.creer(&"promis_a_jacquot", Marques.PROMESSE),
		Marques.creer(&"les_barbeles", Marques.CICATRICE),
		Marques.creer(&"il_s_appelait_gaspard", Marques.NOM_RETENU),
		{"id": &"promis_a_ilde", "famille": Marques.PROMESSE, "etat": Marques.TENUE},
		Marques.creer(&"un_nom_inconnu", Marques.NOM_RETENU),
	]
	assert_eq(EpilogueFin.noms_retenus(marques), PackedStringArray(["Jacquot", "Gaspard", "Un nom inconnu"]))
	assert_eq(EpilogueFin.promesses_ouvertes(marques), PackedStringArray(["Du pain blanc pour Jacquot"]))


func test_le_carton_du_porteur() -> void:
	GameState.ajouter_marque(&"jacquot", Marques.NOM_RETENU, &"e1_adieu")
	GameState.ajouter_marque(&"promis_a_ilde", Marques.PROMESSE, &"e3_ilde")
	assert_eq(GameState.fin(), &"porteur")
	var carton: Epilogue = add_child_autofree(SceneEpilogue.instantiate())
	await wait_until(func() -> bool: return carton.colonne_lignes.get_child_count() > 0, 3.0)
	assert_eq(carton.cle, "porteur")
	assert_string_contains(carton.gravure.texture.resource_path, "cin_epilogue-a")
	assert_eq(carton.lignes.size(), 4)
	assert_eq(carton.colonne_lignes.get_child_count(), 4)
	assert_eq(carton.etat, Epilogue.Etat.LIGNES)
	carton.passer()
	assert_eq(carton.etat, Epilogue.Etat.FINI)
	var memoire := ""
	for label in carton.colonne_memoire.get_children():
		memoire += (label as Label).text + "\n"
	assert_string_contains(memoire, "Jacquot")
	assert_string_contains(memoire, "Rester chez Ilde, volets clos")
	assert_eq(carton.invite.modulate.a, 1.0)


func test_apres_la_derniere_etape_le_routeur_va_a_l_epilogue() -> void:
	assert_true(ResourceLoader.exists(SceneRouter.ECRAN_EPILOGUE))
	assert_true(SceneRouter.est_derniere_etape(7), "la Mère-Cloche (fin_etape) mène au carton")
	assert_false(SceneRouter.etape_existe(8), "il n'y a pas d'étape 8 à charger")
	for n in range(1, 7):
		assert_false(SceneRouter.est_derniere_etape(n), "étape %d : on passe à la suivante" % n)


func test_le_carton_ramene_au_titre_une_fois_fini() -> void:
	var carton: Epilogue = add_child_autofree(SceneEpilogue.instantiate())
	await wait_until(func() -> bool: return carton.colonne_lignes.get_child_count() > 0, 3.0)
	carton.passer()
	assert_eq(carton.etat, Epilogue.Etat.FINI, "la prochaine pression appelle SceneRouter.retour_titre()")


func test_une_pression_avant_le_chargement_des_lignes_est_ignoree() -> void:
	var carton: Epilogue = autofree(Epilogue.new())
	assert_false(carton.accepte_entree(), "pas encore de séquence : rien à passer")
	var en_scene: Epilogue = add_child_autofree(SceneEpilogue.instantiate())
	await wait_until(func() -> bool: return en_scene.colonne_lignes.get_child_count() > 0, 3.0)
	assert_true(en_scene.accepte_entree())


func _carton_anime() -> Epilogue:
	Epilogue.modele_animation = "res://tests/fixtures/anim_epilogue_%s.gd"
	GameState.ajouter_marque(&"jacquot", Marques.NOM_RETENU, &"e1_adieu")
	var carton: Epilogue = add_child_autofree(SceneEpilogue.instantiate())
	await wait_until(func() -> bool: return carton.colonne_lignes.get_child_count() > 0, 3.0)
	return carton


func _visibles(carton: Epilogue) -> int:
	var n := 0
	for label in carton.colonne_lignes.get_children():
		if (label as CanvasItem).modulate.a > 0.0:
			n += 1
	return n


func test_sans_animation_la_gravure_reste() -> void:
	Epilogue.modele_animation = "res://tests/fixtures/absent_%s.gd"
	var carton: Epilogue = add_child_autofree(SceneEpilogue.instantiate())
	await wait_until(func() -> bool: return carton.colonne_lignes.get_child_count() > 0, 3.0)
	assert_null(carton.anime)
	assert_true(carton.gravure.visible)
	assert_null(carton.get_node_or_null("Bandeau"))


func test_l_animation_remplace_la_gravure_et_rythme_les_lignes() -> void:
	var carton := await _carton_anime()
	assert_not_null(carton.anime)
	assert_false(carton.gravure.visible, "l'animation remplace la gravure")
	assert_not_null(carton.get_node_or_null("Bandeau"), "les lignes sur un bandeau papier")
	assert_lt(carton.anime.get_index(), carton.colonne_lignes.get_index(), "l'animation derrière le texte")
	assert_eq(carton.anime.mouse_filter, Control.MOUSE_FILTER_IGNORE)
	assert_true(carton.anime.get(&"jouee"))
	assert_true(carton.suit_animation())
	# Lignes à 0,1 / 0,3 / 0,5 / 0,7 s, chacune en FONDU : la dernière ne commence qu'après les autres.
	assert_eq(carton.etat, Epilogue.Etat.LIGNES)
	await wait_seconds(0.2)
	assert_eq(_visibles(carton), 1, "la première ligne à son instant")
	await wait_until(func() -> bool: return carton.etat != Epilogue.Etat.LIGNES, 12.0)
	assert_eq(_visibles(carton), 4, "toutes les lignes avant la mémoire")
	await wait_until(func() -> bool: return carton.etat == Epilogue.Etat.FINI, 12.0)
	assert_eq(carton.invite.modulate.a, 1.0, "l'invite à la fin de l'animation")


func test_passer_saute_aussi_l_animation() -> void:
	var carton := await _carton_anime()
	carton.passer()
	assert_true(carton.anime.get(&"passee"), "l'animation va à sa dernière image")
	assert_eq(carton.etat, Epilogue.Etat.FINI)
	assert_eq(carton.invite.modulate.a, 1.0)
	assert_eq(_visibles(carton), 4)
