extends GutTest
## Lucidité → écran gravure : tremblé et rouge par palier (DA), fondu de 0,6 s, effets atténués.

var _attenues: Variant
var etape: EtapeBase


func before_all() -> void:
	_attenues = Reglages.valeur(&"effets_attenues")


func before_each() -> void:
	GameState.reinitialiser()
	Reglages.changer(&"effets_attenues", false)
	etape = add_child_autofree(EtapeBase.new())


func after_all() -> void:
	Reglages.changer(&"effets_attenues", _attenues)
	GameState.reinitialiser()


func _param(nom: StringName) -> float:
	return float(etape.materiau_gravure().get_shader_parameter(nom))


func test_valeurs_de_la_da() -> void:
	assert_eq(LuciditeEcran.valeurs_pour(&"clair"), Vector2(1.5, 0.0))
	assert_eq(LuciditeEcran.valeurs_pour(&"trouble"), Vector2(3.0, 0.0))
	assert_eq(LuciditeEcran.valeurs_pour(&"egare"), Vector2(5.0, 0.3))


func test_l_etape_pose_le_lien_et_le_repos() -> void:
	await wait_process_frames(2)
	assert_almost_eq(_param(&"amplitude_px"), 1.5, 0.001)
	assert_almost_eq(_param(&"rouge_efface"), 0.0, 0.001)


func test_fondu_vers_l_egare() -> void:
	await wait_process_frames(2)
	GameState.palier = GameState.EGARE
	GameState.palier_change.emit(&"clair", GameState.EGARE)
	await wait_seconds(0.25)
	var milieu := _param(&"amplitude_px")
	assert_between(milieu, 1.6, 4.9, "en cours de fondu")
	await wait_seconds(0.6)
	assert_almost_eq(_param(&"amplitude_px"), 5.0, 0.001)
	assert_almost_eq(_param(&"rouge_efface"), 0.3, 0.001)


func test_effets_attenues_amplitude_nulle_rouge_garde() -> void:
	await wait_process_frames(2)
	GameState.palier = GameState.EGARE
	GameState.palier_change.emit(&"clair", GameState.EGARE)
	await wait_seconds(0.8)
	Reglages.changer(&"effets_attenues", true)
	await wait_process_frames(2)
	assert_eq(_param(&"amplitude_px"), 0.0)
	assert_almost_eq(_param(&"rouge_efface"), 0.3, 0.001)
