extends GutTest
## QA (étapes 5 et 7) : sans bornes_camera_surface, la caméra est bornée au tronçon de surface où
## se trouve le messager (sections Surface/* bout à bout réunies), pas au vide qui les sépare.

var _etape: EtapeBase


func _charger(numero: int) -> Messager:
	GameState.reinitialiser()
	_etape = add_child_autofree(
		(load("res://scenes/etapes/etape_%02d/etape_%02d.tscn" % [numero, numero]) as PackedScene).instantiate())
	return _etape.trouver_messager()


func after_each() -> void:
	GameState.reinitialiser()


func _camera(messager: Messager) -> Camera2D:
	return messager.get_node("%Camera") as Camera2D


## La vue (bornes de la caméra) reste dans le rectangle, centrée s'il est plus petit que l'écran.
func _assert_bornee(camera: Camera2D, rect: Rect2, quoi: String) -> void:
	assert_almost_eq((camera.limit_left + camera.limit_right) / 2.0, rect.get_center().x, 1.0, quoi)
	assert_almost_eq((camera.limit_top + camera.limit_bottom) / 2.0, rect.get_center().y, 1.0, quoi)
	var vue := camera.get_viewport_rect().size / camera.zoom
	if rect.size.x >= vue.x:
		assert_eq(camera.limit_left, int(rect.position.x), quoi + " : bord gauche")
		assert_eq(camera.limit_right, int(rect.end.x), quoi + " : bord droit")


func test_etape_5_deux_troncons() -> void:
	var messager := _charger(5)
	var oree_boucle := Rect2(0, 0, 5760, EtapeBase.HAUTEUR_LIEU)
	var campement_clairiere := Rect2(6720, 0, 13440 - 6720, EtapeBase.HAUTEUR_LIEU)
	assert_eq(_etape.rect_troncon(Vector2(500, 700)), oree_boucle, "Orée et Boucle bout à bout")
	assert_eq(_etape.rect_troncon(Vector2(5000, 700)), oree_boucle)
	assert_eq(_etape.rect_troncon(Vector2(9000, 700)), campement_clairiere, "Campement, Cimetière, Clairière")
	assert_eq(_etape.rect_troncon(Vector2(6000, 700)), Rect2(), "le vide entre deux tronçons")
	messager.teleporter((_etape.find_child("boucle_debut", true, false) as Node2D).global_position)
	_assert_bornee(_camera(messager), oree_boucle, "dans la boucle")
	messager.teleporter((_etape.find_child("entree_campement", true, false) as Node2D).global_position)
	_assert_bornee(_camera(messager), campement_clairiere, "au campement")


func test_etape_7_la_galerie() -> void:
	var messager := _charger(7)
	messager.teleporter((_etape.find_child("entree_galerie", true, false) as Node2D).global_position)
	_assert_bornee(_camera(messager), Rect2(0, 0, 1920, EtapeBase.HAUTEUR_LIEU), "galerie")


func test_etape_4_troncons_separes() -> void:
	_charger(4)
	assert_eq(_etape.rect_troncon(Vector2(500, 700)), Rect2(0, 0, 1920, EtapeBase.HAUTEUR_LIEU), "porche")
	assert_eq(_etape.rect_troncon(Vector2(3000, 700)), Rect2(2880, 0, 1920, EtapeBase.HAUTEUR_LIEU), "rue latérale")


func test_les_etapes_a_bornes_fixes_ne_changent_pas() -> void:
	var messager := _charger(1)
	messager.teleporter((_etape.find_child("porte_cantine", true, false) as Node2D).global_position)
	assert_eq(_camera(messager).limit_left, 0)
	assert_eq(_camera(messager).limit_right, 10624)
