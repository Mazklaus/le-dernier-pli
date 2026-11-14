extends GutTest
## Vérifie que chaque fichier .dialogue du projet se compile sans erreur.


func test_tous_les_dialogues_se_chargent() -> void:
	var fichiers := _trouver("res://dialogue")
	assert_gt(fichiers.size(), 0, "au moins un fichier .dialogue")
	for chemin in fichiers:
		var ressource: Resource = load(chemin)
		assert_not_null(ressource, "%s doit se compiler" % chemin)


func _trouver(dossier: String) -> PackedStringArray:
	var resultat := PackedStringArray()
	for sous in DirAccess.get_directories_at(dossier):
		resultat.append_array(_trouver(dossier.path_join(sous)))
	for f in DirAccess.get_files_at(dossier):
		if f.ends_with(".dialogue"):
			resultat.append(dossier.path_join(f))
	return resultat
