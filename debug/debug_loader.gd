## Autoload "DebugLoader". N'instancie le menu de débogage que dans les
## builds debug (éditeur et exports --export-debug). Absent en release.
extends Node

const DEBUG_MENU_PATH := "res://debug/debug_menu.gd"


func _ready() -> void:
	if not OS.has_feature("debug"):
		queue_free()
		return
	var menu_script: GDScript = load(DEBUG_MENU_PATH)
	var menu: CanvasLayer = menu_script.new()
	add_child(menu)
