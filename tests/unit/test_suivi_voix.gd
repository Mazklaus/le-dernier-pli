extends GutTest
## Voix de surface : à l'étape 1, le gain des voix suit le messager à la surface et revient
## plein sous terre (AudioDirector.definir_suivi_voix / arreter_suivi_voix via EtapeBase).

const ETAPE := preload("res://scenes/etapes/etape_01/etape_01.tscn")

var _etape: EtapeBase


func before_each() -> void:
	_etape = ETAPE.instantiate()
	add_child_autofree(_etape)
	await wait_process_frames(2)


func after_each() -> void:
	AudioDirector.arreter_suivi_voix()


func _point(nom: String) -> Marker2D:
	return _etape.find_child(nom, true, false) as Marker2D


func test_quatre_reperes_nommes_comme_le_mixage() -> void:
	var noms: Array[StringName] = []
	for r in _etape.reperes_voix():
		noms.append(StringName(r.name))
	for nom: StringName in MixageSon.GAIN_VOIX_REPERES:
		assert_has(noms, nom)
	var reperes := _etape.reperes_voix()
	for r in reperes:
		assert_true(_etape.est_en_surface(r.global_position), "%s à la surface" % r.name)


func test_depart_sous_terre_voix_pleines() -> void:
	var messager := _etape.trouver_messager()
	assert_false(_etape.est_en_surface(messager.global_position), "départ dans la couchette")
	assert_null(AudioDirector._suivi_joueur)


func test_a_la_surface_le_gain_suit_puis_revient_sous_terre() -> void:
	var messager := _etape.trouver_messager()
	messager.teleporter(_point("porte_cantine").global_position)
	assert_eq(AudioDirector._suivi_joueur, messager, "surface : suivi actif")
	assert_eq(AudioDirector._points_voix.size(), 4)
	messager.teleporter(_point("entree_cantine").global_position)
	assert_null(AudioDirector._suivi_joueur, "sous terre : suivi arrêté")
	assert_almost_eq(AudioDirector._gain_voix, 1.0, 0.001)
