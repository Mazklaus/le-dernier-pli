extends GutTest
## AudioDirector applique bien les règles de MixageSon aux couches de l'étape.

const AudioDirectorScript := preload("res://autoload/audio_director.gd")


func _director_etape_1() -> Node:
	var ad: Node = AudioDirectorScript.new()
	add_child_autofree(ad)
	ad.jouer_etape(1)
	return ad


func _volume(ad: Node, couche: String) -> float:
	return (ad._couches[couche] as AudioStreamPlayer).volume_db


func test_jouer_etape_cree_les_trois_couches() -> void:
	var ad := _director_etape_1()
	assert_eq(ad._couches.keys(), ["surface-lit", "surface-voix", "autre"])


func test_le_noir_sans_lanterne_fait_monter_l_autre() -> void:
	var ad := _director_etape_1()
	var attendu := MixageSon.cible(GameState.palier, GameState.est_perdu(), true)
	ad._dans_le_noir = true
	ad._appliquer_mixage(true)
	assert_almost_eq(_volume(ad, "autre"), MixageSon.vers_db(attendu["autre"]), 0.01)
	assert_almost_eq(_volume(ad, "surface-lit"), MixageSon.vers_db(attendu["reel"]), 0.01)


func test_les_voix_suivent_le_gain_de_position() -> void:
	var ad := _director_etape_1()
	ad._appliquer_mixage(true)
	ad._gain_voix = 0.5
	ad._maj_volumes()
	var reel: float = ad._mix_reel
	assert_almost_eq(_volume(ad, "surface-voix"), MixageSon.vers_db(reel * 0.5), 0.01)
	assert_almost_eq(_volume(ad, "surface-lit"), MixageSon.vers_db(reel), 0.01)


func test_jouer_timbre_inconnu_ne_joue_rien() -> void:
	var ad := _director_etape_1()
	ad.audio_deverrouille = true
	var avant := ad.get_child_count()
	ad.jouer_timbre("personne")
	assert_eq(ad.get_child_count(), avant, "aucun lecteur créé sans fichier vox_")


func test_arreter_musique_sans_musique_ne_fait_rien() -> void:
	var ad := _director_etape_1()
	ad.arreter_musique()
	assert_false(ad._musique.playing)


func test_jouer_musique_absente_ne_joue_rien() -> void:
	var ad := _director_etape_1()
	ad.audio_deverrouille = true
	ad.jouer_musique(1, "inexistant", 0.0)
	assert_false(ad._musique.playing)


func test_jouer_musique_theme_joue_a_plein_volume_sans_fondu() -> void:
	var ad := _director_etape_1()
	ad.audio_deverrouille = true
	ad.jouer_musique(1, "theme", 0.0)
	assert_true(ad._musique.playing)
	assert_almost_eq(ad._musique.volume_db, 0.0, 0.01)
	ad.arreter_musique(0.0)
	assert_false(ad._musique.playing)


func test_variantes_de_trouve_les_fichiers_numerotes() -> void:
	var ad := _director_etape_1()
	assert_eq(ad.variantes_de("sfx_pas_boue").size(), 6)
	assert_eq(ad.variantes_de("vox_tobie"), ["vox_tobie_01", "vox_tobie_02", "vox_tobie_03"])
	assert_eq(ad.variantes_de("sfx_inexistant").size(), 0)


func test_jouer_variante_ne_repete_pas_deux_fois_de_suite() -> void:
	var ad := _director_etape_1()
	ad.audio_deverrouille = true
	var precedente := ""
	for i in 20:
		ad.jouer_variante("sfx_pas_planche")
		var choix: String = ad._derniere_variante["sfx_pas_planche"]
		assert_ne(choix, precedente)
		precedente = choix


func test_arreter_sfx_coupe_le_maintien() -> void:
	var ad := _director_etape_1()
	ad.audio_deverrouille = true
	ad.jouer_variante("sfx_ui_maintien", AudioDirectorScript.BUS_UI)
	var en_cours := ad.get_children().filter(func(n: Node) -> bool: return n.has_meta(&"sfx"))
	assert_eq(en_cours.size(), 1)
	ad.arreter_sfx("sfx_ui_maintien")
	assert_false((en_cours[0] as AudioStreamPlayer).playing)
