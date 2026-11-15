extends GutTest
## Garde-fou QA (demande du Game Director) : chaque scène d'étape présente dans le jeu
## porte l'écran gravure, avec le papier de SON étape. Sans ce test, l'écran gravure est
## resté débranché de toutes les étapes sans que personne ne le voie (tout sur #E8E5DA).
## Le test parcourt les étapes 1 à 7 qui existent déjà : une nouvelle étape est couverte
## dès que sa scène est créée.

const SHADER_GRAVURE: Shader = preload("res://shaders/ecran_gravure.gdshader")
## Nombre d'étapes déjà construites quand ce test a été écrit (1 à 3).
const ETAPES_MINIMUM := 3


func _etapes_existantes() -> Array[int]:
	var liste: Array[int] = []
	for numero in range(1, SceneRouter.NB_ETAPES + 1):
		if SceneRouter.etape_existe(numero):
			liste.append(numero)
	return liste


func _instancier(numero: int) -> EtapeBase:
	var scene := load(SceneRouter.chemin_etape(numero)) as PackedScene
	var etape := scene.instantiate() as EtapeBase
	add_child_autofree(etape)
	return etape


func before_each() -> void:
	GameState.reinitialiser()


func after_each() -> void:
	GameState.reinitialiser()


func test_les_etapes_construites_sont_toutes_trouvees() -> void:
	assert_gte(_etapes_existantes().size(), ETAPES_MINIMUM,
		"SceneRouter ne trouve plus les scènes d'étape : le test ne vérifierait plus rien")


func test_chaque_etape_porte_son_numero() -> void:
	for numero in _etapes_existantes():
		var etape := _instancier(numero)
		assert_not_null(etape, "étape %d : la racine n'est pas un EtapeBase" % numero)
		if etape != null:
			# numero_etape à 0 (oubli) donnerait silencieusement le papier de l'étape 1.
			assert_eq(etape.numero_etape, numero, "étape %d : numero_etape mal renseigné" % numero)


func test_chaque_etape_porte_l_ecran_gravure_avec_son_papier() -> void:
	for numero in _etapes_existantes():
		var etape := _instancier(numero)
		await wait_process_frames(2)
		var m := etape.materiau_gravure()
		assert_not_null(m, "étape %d : pas d'écran gravure" % numero)
		if m == null:
			continue
		assert_eq(m.shader, SHADER_GRAVURE, "étape %d : mauvais shader sur l'écran" % numero)
		var attendu: Color = PapierEtapes.ETAPES[numero]["papier"]
		assert_eq(m.get_shader_parameter(&"couleur_papier"), attendu,
			"étape %d : papier %s attendu" % [numero, attendu.to_html(false)])
		var couche := etape.get_node_or_null(EtapeBase.NOEUD_GRAVURE) as CanvasLayer
		assert_not_null(couche, "étape %d : calque de l'écran introuvable" % numero)
		if couche != null:
			assert_true(couche.visible, "étape %d : écran gravure masqué" % numero)
