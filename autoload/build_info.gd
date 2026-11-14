extends CanvasLayer
## Autoload BuildInfo : affiche le SHA du commit en coin d'écran dans les builds debug,
## pour que le QA le reporte dans chaque issue. Le fichier build_sha.txt est écrit par la CI.

const FICHIER_SHA := "res://build_sha.txt"


func _ready() -> void:
	if not OS.has_feature("debug"):
		queue_free()
		return
	layer = 128
	# Style #12 (UI/UX) : mono 12 px, lavis #4A463D sur plaque papier, contour encre 1 px.
	var plaque := PanelContainer.new()
	var style := StyleBoxFlat.new()
	style.bg_color = Color("#E8E5DA")
	style.border_color = Color("#15130F")
	style.set_border_width_all(1)
	style.set_content_margin_all(4)
	plaque.add_theme_stylebox_override(&"panel", style)
	var label := Label.new()
	label.text = "build %s" % lire_sha()
	var police := SystemFont.new()
	police.font_names = PackedStringArray(["IBM Plex Mono", "monospace"])
	label.add_theme_font_override(&"font", police)
	label.add_theme_font_size_override(&"font_size", 12)
	label.add_theme_color_override(&"font_color", Color("#4A463D"))
	plaque.add_child(label)
	plaque.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT)
	plaque.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	plaque.grow_vertical = Control.GROW_DIRECTION_BEGIN
	plaque.offset_right = -24
	plaque.offset_bottom = -24
	plaque.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(plaque)


static func lire_sha() -> String:
	if FileAccess.file_exists(FICHIER_SHA):
		return FileAccess.get_file_as_string(FICHIER_SHA).strip_edges()
	return "local"
