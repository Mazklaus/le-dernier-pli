extends CanvasLayer
## Autoload BuildInfo : affiche le SHA du commit en coin d'écran dans les builds debug,
## pour que le QA le reporte dans chaque issue. Le fichier build_sha.txt est écrit par la CI.

const FICHIER_SHA := "res://build_sha.txt"


func _ready() -> void:
	if not OS.has_feature("debug"):
		queue_free()
		return
	layer = 128
	var label := Label.new()
	label.text = "build %s" % lire_sha()
	label.modulate = Color(1, 1, 1, 0.6)
	label.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT)
	label.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	label.grow_vertical = Control.GROW_DIRECTION_BEGIN
	label.offset_right = -8
	label.offset_bottom = -4
	add_child(label)


static func lire_sha() -> String:
	if FileAccess.file_exists(FICHIER_SHA):
		return FileAccess.get_file_as_string(FICHIER_SHA).strip_edges()
	return "local"
