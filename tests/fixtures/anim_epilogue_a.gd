extends Control
## Épilogue animé factice (tests de epilogue.gd) : l'interface que livre la DA.

signal finie

var temps_lignes: Array[float] = [0.1, 0.3, 0.5, 0.7]
var duree := 1.2
var jouee := false
var passee := false


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func jouer() -> void:
	jouee = true
	get_tree().create_timer(duree).timeout.connect(_finir)


func passer() -> void:
	passee = true
	_finir()


func _finir() -> void:
	if not is_inside_tree():
		return
	finie.emit()
