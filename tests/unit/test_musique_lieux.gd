extends GutTest
## Musique par lieu (étape 1) : le thème monte en entrant dans l'abri du sergent ou la
## chapelle, et se retire en remontant (Passage.franchi -> EtapeBase).

const ETAPE := preload("res://scenes/etapes/etape_01/etape_01.tscn")
const THEME := "res://assets/audio/mus_tranchee-mere_theme.ogg"

var _etape: EtapeBase
var _deverrouille: bool


func before_each() -> void:
	_deverrouille = AudioDirector.audio_deverrouille
	AudioDirector.audio_deverrouille = true
	_etape = ETAPE.instantiate()
	add_child_autofree(_etape)
	await wait_process_frames(2)


func after_each() -> void:
	AudioDirector.arreter_musique(0.0)
	AudioDirector.audio_deverrouille = _deverrouille


func test_reglage_de_l_etape_1() -> void:
	assert_eq(_etape.numero_etape, 1)
	assert_eq(_etape.lieux_musique.get(&"abri_sergent"), "theme")
	assert_eq(_etape.lieux_musique.get(&"chapelle"), "theme")


func test_tous_les_passages_sont_relies() -> void:
	var nb := 0
	for n in get_tree().get_nodes_in_group(&"passages"):
		if n is Passage and _etape.is_ancestor_of(n):
			nb += 1
			assert_true((n as Passage).franchi.is_connected(_etape._sur_passage_franchi), n.name)
	assert_gt(nb, 0)


func test_entrer_lance_le_theme_ressortir_l_arrete() -> void:
	_etape._sur_passage_franchi(null, &"chapelle")
	assert_eq(AudioDirector._musique.stream.resource_path, THEME)
	assert_true(AudioDirector._musique.playing)
	_etape._sur_passage_franchi(null, &"carrefour")
	assert_true(AudioDirector._fondu_musique.is_valid(), "fondu sortant en cours")
	await wait_seconds(AudioDirector.DUREE_FONDU_MUSIQUE + 0.3)
	assert_false(AudioDirector._musique.playing, "silence d'exploration")


func test_lieu_sans_musique_reste_silencieux() -> void:
	_etape._sur_passage_franchi(null, &"cantine")
	assert_false(AudioDirector._musique.playing)
