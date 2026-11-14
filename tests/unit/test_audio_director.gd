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
