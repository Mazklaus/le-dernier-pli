extends GutTest
## Bug #10 : un clic sur l'écran titre doit passer de l'invite au menu.

const SCENE := preload("res://scenes/titre/titre.tscn")


func test_clic_a_l_invite_ouvre_le_menu() -> void:
	var titre: Control = SCENE.instantiate()
	add_child_autofree(titre)
	await wait_process_frames(2)
	assert_eq(titre.ecran, titre.Ecran.INVITE)
	var clic := InputEventMouseButton.new()
	clic.button_index = MOUSE_BUTTON_LEFT
	clic.pressed = true
	clic.position = Vector2(960, 540)
	clic.global_position = clic.position
	get_viewport().push_input(clic)
	await wait_process_frames(2)
	assert_eq(titre.ecran, titre.Ecran.MENU)


func test_touche_a_l_invite_ouvre_le_menu() -> void:
	var titre: Control = SCENE.instantiate()
	add_child_autofree(titre)
	await wait_process_frames(2)
	var touche := InputEventKey.new()
	touche.pressed = true
	touche.physical_keycode = KEY_SPACE
	get_viewport().push_input(touche)
	await wait_process_frames(2)
	assert_eq(titre.ecran, titre.Ecran.MENU)
