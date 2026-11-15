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
## Aperçu d'un coût (UI/UX) : les `apercu` derniers bâtons pleins passent en pointillé de
## lavis ; `apercu_plein` les remet pleins le temps d'un clignement ; `decalage_apercu`
## les fait trembler avec le chiffre qui bave.
var apercu: int = 0:
	set(v):
		apercu = clampi(v, 0, maximum)
		queue_redraw()
var apercu_plein: bool = false:
	set(v):
		if v != apercu_plein:
			apercu_plein = v
			queue_redraw()
var decalage_apercu: Vector2 = Vector2.ZERO:
	set(v):
		if v != decalage_apercu:
			decalage_apercu = v
			queue_redraw()


func _ready() -> void:
	_redimensionner()


func _draw() -> void:
	var x := 2.0
	for i in maximum:
		var plein := i < valeur
		var couleur := StylePapier.ENCRE if plein else StylePapier.MINE
		var epaisseur := 2.4 if plein else 1.2
		var decalage := Vector2.ZERO
		if en_apercu(i):
			decalage = decalage_apercu
			if not apercu_plein:
				plein = false
				couleur = StylePapier.LAVIS
		if i % 5 == 4:
			_trait(Vector2(x - 4.0 * ECART - 2.0, HAUTEUR - 2.0) + decalage, Vector2(x - 2.0, 2.0) + decalage, couleur, epaisseur, plein)
			x += ECART
		else:
			_trait(Vector2(x, 2.0) + decalage, Vector2(x + (0.6 if i % 2 else -0.6), HAUTEUR - 2.0) + decalage, couleur, epaisseur, plein)
			x += ECART


## Le bâton i est-il retiré par l'aperçu du coût ?
func en_apercu(i: int) -> bool:
	return i < valeur and i >= valeur - apercu


func _trait(a: Vector2, b: Vector2, couleur: Color, epaisseur: float, plein: bool) -> void:
	if plein:
		draw_line(a, b, couleur, epaisseur, true)
	else:
		draw_dashed_line(a, b, couleur, epaisseur, 2.0)


func _redimensionner() -> void:
	custom_minimum_size = Vector2(maximum * ECART + 6.0, HAUTEUR)
	queue_redraw()
