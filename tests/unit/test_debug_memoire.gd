extends GutTest
## Menu F1 : la mémoire vidéo des textures s'affiche (mesure du budget web).

const MenuDebug := preload("res://debug/debug_menu.gd")


func test_texte_de_la_memoire_video() -> void:
	var texte: String = MenuDebug.texte_memoire()
	assert_true(texte.begins_with("textures : "), texte)
	assert_string_contains(texte, " Mo")


func test_le_menu_affiche_la_memoire() -> void:
	var menu: CanvasLayer = add_child_autofree(MenuDebug.new())
	var label := menu.find_child("MemoireVideo", true, false) as Label
	assert_not_null(label)
