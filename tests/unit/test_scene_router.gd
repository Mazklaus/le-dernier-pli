extends GutTest

const SceneRouter := preload("res://autoload/scene_router.gd")


func test_numero_etape_depuis_identifiant_de_rencontre() -> void:
	assert_eq(SceneRouter.numero_etape_de(&"e1_sergent"), 1)
	assert_eq(SceneRouter.numero_etape_de(&"e7_destinataire"), 7)


func test_identifiant_invalide() -> void:
	assert_eq(SceneRouter.numero_etape_de(&"sergent"), 0)
	assert_eq(SceneRouter.numero_etape_de(&"ex_sergent"), 0)


func test_chaque_etape_a_un_chemin_conventionnel() -> void:
	var routeur: Node = SceneRouter.new()
	assert_eq(routeur.chemin_etape(1), "res://scenes/etapes/etape_01/etape_01.tscn")
	assert_true(routeur.etape_existe(1))
	assert_false(routeur.etape_existe(8))
	routeur.free()
