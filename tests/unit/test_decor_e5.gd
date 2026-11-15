extends GutTest
## Décor de l'étape 5, la Forêt de Croix : un fond fixe par section, et trois calques qui
## montrent les gestes de Tobie (entaille, cloche raccrochée, nom gravé) quand ils sont faits.

const ETAPE := preload("res://scenes/etapes/etape_05/etape_05.tscn")
## [chemin de la section, largeur du fond].
const ATTENDU := [
	["Surface/Oree", 1920.0], ["Surface/Boucle", 3840.0], ["Surface/Campement", 1920.0],
	["Surface/Cimetiere", 2880.0], ["Surface/Clairiere", 1920.0],
]

var _etape: EtapeBase


func before_each() -> void:
	GameState.reinitialiser()
	_etape = ETAPE.instantiate()
	add_child_autofree(_etape)
	await wait_process_frames(2)


func after_all() -> void:
	GameState.reinitialiser()


func test_chaque_section_a_son_fond_a_la_bonne_largeur() -> void:
	assert_true(_etape.get_node("Decors") is DecorE5)
	for a: Array in ATTENDU:
		var lieu := _etape.get_node(String(a[0]))
		var dessin := lieu.get_node_or_null("Dessin") as Node2D
		assert_not_null(dessin, String(a[0]))
		if dessin == null:
			continue
		assert_eq(dessin.position, Vector2.ZERO, String(a[0]))
		assert_lt(dessin.z_index, 0, "derrière le jeu : %s" % a[0])
		var largeur := 0.0
		for tuile: Node in dessin.get_children():
			largeur += (tuile as Sprite2D).texture.get_width()
		assert_almost_eq(largeur, float(a[1]), 1.0, String(a[0]))
		assert_false((lieu.get_node("Fond") as CanvasItem).visible, String(a[0]))
		assert_false((lieu.get_node("Sol/Visuel") as CanvasItem).visible, String(a[0]))


func test_l_entaille_est_dessinee_et_suit_l_etape() -> void:
	var entaille := _etape.get_node("Surface/Boucle/e5_sentier/Entaille") as ColorRect
	assert_eq(entaille.color.a, 0.0, "le gris de la maquette est transparent")
	var dessin := entaille.get_node_or_null("Dessin") as Sprite2D
	assert_not_null(dessin)
	assert_false(entaille.visible, "pas d'entaille avant le geste")
	GameState.marquer_rencontre_vue(&"e5_entaille_faite")
	assert_true(entaille.is_visible_in_tree())


func test_la_cloche_et_le_nom_apparaissent_apres_le_geste() -> void:
	var croix := _etape.get_node("Surface/Cimetiere/e5_croix")
	var cloche := croix.get_node("Cloche") as Sprite2D
	var nom := croix.get_node("NomGrave") as Sprite2D
	assert_false(cloche.visible)
	assert_false(nom.visible)
	GameState.marquer_rencontre_vue(&"insigne_rendu")
	assert_true(cloche.visible)
	assert_false(nom.visible)
	GameState.marquer_rencontre_vue(&"nom_grave")
	assert_true(nom.visible)
	assert_gt(nom.position.x, 100.0, "le nom est sur la croix sans nom, à droite")


func test_graver_vise_la_croix_sans_nom() -> void:
	var repere := _etape.get_node_or_null("Surface/Cimetiere/e5_croix/geste_graver") as Marker2D
	assert_not_null(repere)
	if repere != null:
		assert_eq(repere.position, Vector2(140, 0))
