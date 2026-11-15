extends GutTest
## #164 : à l'arrivée dans chaque étape, la vue est celle du messager, pas celle d'une
## cinématique placée dans la scène.


func test_la_vue_suit_le_messager_dans_chaque_etape() -> void:
	for numero in range(1, 8):
		GameState.reinitialiser()
		var etape: EtapeBase = add_child_autofree(
			(load("res://scenes/etapes/etape_%02d/etape_%02d.tscn" % [numero, numero]) as PackedScene).instantiate())
		await wait_process_frames(2)
		var messager := etape.trouver_messager()
		if messager == null:
			continue
		var vue := get_viewport().get_camera_2d()
		assert_not_null(vue, "étape %d : une caméra tient la vue" % numero)
		if vue != null:
			assert_true(messager.is_ancestor_of(vue), "étape %d : vue sur le messager, pas sur %s" % [numero, vue.get_path()])
		for c in etape.find_children("*", "Node2D", true, false):
			if c is Cinematique and c.get_node_or_null("Camera") is Camera2D:
				assert_false((c.get_node("Camera") as Camera2D).enabled, "étape %d : caméra de %s éteinte" % [numero, c.id])
		etape.queue_free()
		await wait_process_frames(1)
	GameState.reinitialiser()
