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


func test_etape_2_joue_surface_et_autre() -> void:
	var ad: Node = AudioDirectorScript.new()
	add_child_autofree(ad)
	ad.jouer_etape(2)
	assert_eq(ad._couches.keys(), ["surface", "autre"])


func test_les_fils_ne_s_entendent_que_dans_le_noir() -> void:
	var ad := _director_etape_1()
	var fils := AudioStreamPlayer2D.new()
	fils.volume_db = -6.0
	fils.add_to_group(AudioDirectorScript.GROUPE_SON_DU_NOIR)
	add_child_autofree(fils)
	ad._regler_son_du_noir(fils, 0.0)
	assert_eq(fils.volume_db, MixageSon.GAIN_MUET_DB, "muet hors du noir")
	ad._dans_le_noir = true
	ad._maj_sons_du_noir(0.0)
	assert_almost_eq(fils.volume_db, -6.0, 0.01, "retrouve le volume réglé dans la scène")
	ad._dans_le_noir = false
	ad._maj_sons_du_noir(0.0)
	assert_eq(fils.volume_db, MixageSon.GAIN_MUET_DB)


func test_un_seul_fondu_du_noir_par_emetteur() -> void:
	var ad := _director_etape_1()
	var fils := AudioStreamPlayer2D.new()
	fils.add_to_group(AudioDirectorScript.GROUPE_SON_DU_NOIR)
	add_child_autofree(fils)
	ad._dans_le_noir = true
	ad._regler_son_du_noir(fils, 3.0)
	var premier: Tween = fils.get_meta(&"fondu_noir")
	ad._dans_le_noir = false
	ad._regler_son_du_noir(fils, 3.0)
	assert_false(premier.is_valid(), "le premier fondu est tué")
	assert_ne(fils.get_meta(&"fondu_noir"), premier)


class EtapeFactice:
	extends Node
	signal phase_changee(nuit: bool)
	var nuit: bool = false


func test_etape_3_joue_jour_nuit_et_autre_de_jour() -> void:
	var ad: Node = AudioDirectorScript.new()
	add_child_autofree(ad)
	ad.jouer_etape(3)
	ad._appliquer_mixage(true)
	assert_eq(ad._couches.keys(), ["jour", "nuit", "autre"])
	assert_almost_eq(_volume(ad, "jour"), MixageSon.vers_db(ad._mix_reel), 0.01)
	assert_eq(_volume(ad, "nuit"), MixageSon.GAIN_MUET_DB)


func test_phase_changee_bascule_vers_la_nuit() -> void:
	var ad: Node = AudioDirectorScript.new()
	add_child_autofree(ad)
	ad.jouer_etape(3)
	ad._appliquer_mixage(true)
	var etape := EtapeFactice.new()
	add_child_autofree(etape)
	ad._sur_etape_prete(etape)
	etape.phase_changee.emit(true)
	assert_true(ad._fondu_phase != null and ad._fondu_phase.is_valid(), "fondu croisé lancé")
	ad.definir_nuit(true, 0.0)
	assert_eq(_volume(ad, "jour"), MixageSon.GAIN_MUET_DB)
	assert_almost_eq(_volume(ad, "nuit"), MixageSon.vers_db(ad._mix_reel), 0.01)


func test_etape_prete_reprend_l_etat_de_nuit() -> void:
	var ad: Node = AudioDirectorScript.new()
	add_child_autofree(ad)
	ad.jouer_etape(3)
	var etape := EtapeFactice.new()
	etape.nuit = true
	add_child_autofree(etape)
	ad._sur_etape_prete(etape)
	assert_eq(ad._mix_nuit, 1.0, "un chargement en pleine nuit démarre sans fondu")


func test_nouvelle_etape_repart_de_jour() -> void:
	var ad: Node = AudioDirectorScript.new()
	add_child_autofree(ad)
	ad.jouer_etape(3)
	ad.definir_nuit(true, 0.0)
	ad.jouer_etape(3)
	assert_eq(ad._mix_nuit, 0.0)


func test_etape_4_joue_hopital_et_autre() -> void:
	var ad: Node = AudioDirectorScript.new()
	add_child_autofree(ad)
	ad.jouer_etape(4)
	assert_eq(ad._couches.keys(), ["hopital", "autre"])


func test_etape_7_joue_salle_et_autre() -> void:
	var ad: Node = AudioDirectorScript.new()
	add_child_autofree(ad)
	ad.jouer_etape(7)
	assert_eq(ad._couches.keys(), ["salle", "autre"])


func test_epilogue_ne_boucle_pas_et_retire_l_ambiance() -> void:
	var ad: Node = AudioDirectorScript.new()
	add_child_autofree(ad)
	ad.audio_deverrouille = true
	ad.jouer_etape(7)
	ad.jouer_epilogue("fin-b", 0.0)
	assert_true(ad._musique.playing)
	assert_false((ad._musique.stream as AudioStreamOggVorbis).loop, "un épilogue se joue une fois")
	assert_true(ad._couches.is_empty(), "le Cantique reste seul sous le carton")
	var original: AudioStreamOggVorbis = load("res://assets/audio/mus_destinataire_fin-b.ogg")
	assert_true(original.loop, "la ressource partagée garde son réglage d'import")


func test_les_cinq_epilogues_existent() -> void:
	for lettre in ["a", "b", "c", "d", "e"]:
		assert_true(ResourceLoader.exists("res://assets/audio/mus_destinataire_fin-%s.ogg" % lettre), lettre)


func test_etapes_5_et_6_ont_leurs_couches() -> void:
	var ad: Node = AudioDirectorScript.new()
	add_child_autofree(ad)
	ad.jouer_etape(5)
	assert_eq(ad._couches.keys(), ["foret", "autre"])
	ad.jouer_etape(6)
	assert_eq(ad._couches.keys(), ["profondeur", "autre"])


func test_toutes_les_couches_existent() -> void:
	for numero: int in AudioDirectorScript.COUCHES_AMBIANCE:
		var slug: String = AudioDirectorScript.SLUGS_ETAPES[numero]
		for couche: String in AudioDirectorScript.COUCHES_AMBIANCE[numero]:
			var chemin := "res://assets/audio/amb_%s_%s.ogg" % [slug, couche]
			assert_true(ResourceLoader.exists(chemin), chemin)
