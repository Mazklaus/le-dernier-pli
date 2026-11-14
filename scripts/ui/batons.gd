class_name Batons
extends Control
## Bâtons gravés comptés par cinq (le cinquième barre les quatre premiers), comme sur un mur
## de tranchée : les points pleins à l'encre, les points perdus en pointillé de mine.

const ECART := 7.0
const HAUTEUR := 22.0

@export var maximum: int = 10:
	set(v):
		maximum = v
		_redimensionner()
@export var valeur: int = 0:
	set(v):
		valeur = clampi(v, 0, maximum)
		queue_redraw()


func _ready() -> void:
	_redimensionner()


func _draw() -> void:
	var x := 2.0
	for i in maximum:
		var plein := i < valeur
		var couleur := StylePapier.ENCRE if plein else StylePapier.MINE
		var epaisseur := 2.4 if plein else 1.2
		if i % 5 == 4:
			_trait(Vector2(x - 4.0 * ECART - 2.0, HAUTEUR - 2.0), Vector2(x - 2.0, 2.0), couleur, epaisseur, plein)
			x += ECART
		else:
			_trait(Vector2(x, 2.0), Vector2(x + (0.6 if i % 2 else -0.6), HAUTEUR - 2.0), couleur, epaisseur, plein)
			x += ECART


func _trait(a: Vector2, b: Vector2, couleur: Color, epaisseur: float, plein: bool) -> void:
	if plein:
		draw_line(a, b, couleur, epaisseur, true)
	else:
		draw_dashed_line(a, b, couleur, epaisseur, 2.0)


func _redimensionner() -> void:
	custom_minimum_size = Vector2(maximum * ECART + 6.0, HAUTEUR)
	queue_redraw()
