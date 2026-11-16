extends GutTest
## Décor de l'étape 7, le Destinataire : un fond fixe pour la galerie et pour chaque lieu de la
## descente, à la largeur de la pièce, posé en (0, 0) derrière le jeu ; les gris de la maquette
## sont masqués ; aucun rouge (le ruban du pli est le dernier rouge du jeu).

const ETAPE := preload("res://scenes/etapes/etape_07/etape_07.tscn")
## [chemin du lieu, largeur du fond].
const ATTENDU := [
	["Surface/Galerie", 1920.0], ["Lieux/AnneauCloches", 2880.0], ["Lieux/AnneauLise", 2880.0],
	["Lieux/AnneauPorte", 2880.0], ["Lieux/MereCloche", 1920.0],
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
	assert_true(_etape.get_node("Decors") is DecorE7)
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


func test_aucun_rouge_dans_les_fonds() -> void:
	for a: Array in ATTENDU:
		for tuile: Node in _etape.get_node(String(a[0])).get_node("Dessin").get_children():
			var img := (tuile as Sprite2D).texture.get_image()
			if img.is_compressed():
				img.decompress()
			var rouge := false
			for y in range(0, img.get_height(), 6):
				for x in range(0, img.get_width(), 6):
					var c := img.get_pixel(x, y)
					if c.r - maxf(c.g, c.b) > 0.18:
						rouge = true
						break
				if rouge:
					break
			assert_false(rouge, "%s : pas de rouge" % a[0])
