extends GutTest
## Valeurs du shader papier par étape (planche de style du DA, section VI).

const SHADER_PAPIER: Shader = preload("res://shaders/papier.gdshader")


func _materiau() -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = SHADER_PAPIER
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
