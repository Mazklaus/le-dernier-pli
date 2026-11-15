extends GutTest

const Reglages := preload("res://autoload/reglages.gd")


func test_valeurs_par_defaut() -> void:
	var r: Node = Reglages.new()
	r._valeurs = Reglages.DEFAUTS.duplicate()
	r.persistance = false
	assert_eq(r.valeur(&"taille_texte"), 1)
	assert_false(r.valeur(&"effets_attenues"))
	r.free()


func test_changer_emet_le_signal() -> void:
	var r: Node = Reglages.new()
	r._valeurs = Reglages.DEFAUTS.duplicate()
	r.persistance = false
	watch_signals(r)
	r.changer(&"effets_attenues", true)
	assert_signal_emitted_with_parameters(r, "reglage_change", [&"effets_attenues", true])
	r.free()


func test_volume_applique_au_bus() -> void:
	var r: Node = Reglages.new()
	r._valeurs = Reglages.DEFAUTS.duplicate()
	r.persistance = false
	r._valeurs[&"volume_Musique"] = 0.5
	r._appliquer(&"volume_Musique")
	var bus := AudioServer.get_bus_index("Musique")
	assert_almost_eq(AudioServer.get_bus_volume_db(bus), linear_to_db(0.5), 0.01)
	r.free()


func test_mouvement_reduit_faux_hors_web() -> void:
	# Le premier lancement web lit prefers-reduced-motion ; hors web, rien ne change.
	assert_false(Reglages.mouvement_reduit_demande())


func test_reponse_du_navigateur_entiere_ou_booleenne() -> void:
	# JavaScriptBridge.eval renvoie 0 / 1 en entier sur le web (#81).
	assert_true(Reglages.reponse_vraie(1))
	assert_false(Reglages.reponse_vraie(0))
	assert_true(Reglages.reponse_vraie(true))
	assert_false(Reglages.reponse_vraie(null))
	assert_false(Reglages.reponse_vraie("1"))


func test_sans_persistance_rien_n_est_ecrit() -> void:
	var r: Node = Reglages.new()
	r._valeurs = Reglages.DEFAUTS.duplicate()
	r.persistance = false
	var avant := FileAccess.get_modified_time(Reglages.FICHIER) if FileAccess.file_exists(Reglages.FICHIER) else -1
	r.changer(&"taille_texte", 3)
	var apres := FileAccess.get_modified_time(Reglages.FICHIER) if FileAccess.file_exists(Reglages.FICHIER) else -1
	assert_eq(apres, avant)
	assert_eq(r.valeur(&"taille_texte"), 3)
	r.free()


func test_les_tests_tournent_sans_persistance() -> void:
	# Posé par tests/pre_run.gd sur l'autoload.
	assert_false(get_tree().root.get_node(^"Reglages").persistance)
