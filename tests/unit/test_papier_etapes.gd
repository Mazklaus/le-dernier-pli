extends GutTest
## Valeurs du shader papier par étape (planche de style du DA, section VI).

const SHADER_GRAVURE: Shader = preload("res://shaders/ecran_gravure.gdshader")


func _materiau() -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = SHADER_GRAVURE
	return m


func test_sept_etapes_definies() -> void:
	for etape: int in range(1, 8):
		assert_true(PapierEtapes.ETAPES.has(etape), "étape %d" % etape)


func test_etape_1_papier_de_ligne() -> void:
	var m := _materiau()
	PapierEtapes.appliquer(m, 1)
	assert_eq(m.get_shader_parameter(&"couleur_papier"), Color("#E8E5DA"))
	assert_eq(m.get_shader_parameter(&"couleur_encre"), Color("#15130F"))


func test_etapes_5_et_6_inversees() -> void:
	for etape: int in [5, 6]:
		var v: Dictionary = PapierEtapes.ETAPES[etape]
		var papier: Color = v["papier"]
		var encre: Color = v["encre"]
		assert_lt(papier.get_luminance(), encre.get_luminance(), "étape %d inversée" % etape)


func test_etape_hors_bornes_ramenee() -> void:
	var m := _materiau()
	PapierEtapes.appliquer(m, 12)
	assert_eq(m.get_shader_parameter(&"couleur_papier"), Color("#F7F6F1"))


func test_accent_seulement_aux_etapes_5_a_7() -> void:
	var m := _materiau()
	PapierEtapes.appliquer(m, 1)
	assert_false(m.get_shader_parameter(&"accent_actif"))
	PapierEtapes.appliquer(m, 6)
	assert_true(m.get_shader_parameter(&"accent_actif"))
	assert_eq(m.get_shader_parameter(&"couleur_accent"), Color("#5F7F72"))
	PapierEtapes.appliquer(m, 1)
	assert_false(m.get_shader_parameter(&"accent_actif"))


func test_grain_reduit_sur_papier_fonce() -> void:
	for etape: int in [5, 6]:
		var fonce: float = PapierEtapes.ETAPES[etape]["grain"]
		assert_lt(fonce, 0.08, "étape %d" % etape)
