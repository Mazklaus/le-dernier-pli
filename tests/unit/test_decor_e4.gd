extends GutTest
## Décor de l'étape 4, l'Hôpital des Recousus : un fond fixe par section et par lieu, à la
## largeur de la pièce, posé en (0, 0) derrière le jeu ; les gris de la maquette sont masqués.

const ETAPE := preload("res://scenes/etapes/etape_04/etape_04.tscn")
## [chemin du lieu, largeur du fond].
const ATTENDU := [
	["Surface/Porche", 1920.0], ["Lieux/Salle", 3840.0], ["Lieux/Lingerie", 1440.0],
	["Lieux/Atelier", 1920.0], ["Lieux/Escalier", 960.0], ["Lieux/Crypte", 2880.0],
	["Lieux/EscalierService", 960.0], ["Surface/RueLaterale", 1920.0],
]

var _etape: EtapeBase


func before_each() -> void:
	GameState.reinitialiser()
	_etape = ETAPE.instantiate()
	add_child_autofree(_etape)
	await wait_process_frames(2)


func after_all() -> void:
	GameState.reinitialiser()


func test_chaque_lieu_a_son_fond_a_la_bonne_largeur() -> void:
	assert_true(_etape.get_node("Decors") is DecorE4)
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


func test_les_gris_de_la_maquette_sont_masques() -> void:
	for a: Array in ATTENDU:
		var lieu := _etape.get_node(String(a[0]))
		assert_false((lieu.get_node("Fond") as CanvasItem).visible, String(a[0]))
		assert_false((lieu.get_node("Sol/Visuel") as CanvasItem).visible, String(a[0]))
