extends GutTest
## Lieux habillés : plus aucun rectangle « Visuel » d'Interactif ou de Verrou, ni étiquette de
## maquette (noms des rencontres, titres, notes du Level Designer) visibles (QA, #96).

const RougeLisible := preload("res://tests/unit/test_rouge_lisible.gd")


func before_each() -> void:
	GameState.reinitialiser()


func after_all() -> void:
	GameState.reinitialiser()


func test_aucun_rectangle_ni_etiquette_de_maquette_dans_un_lieu_habille() -> void:
	var echecs: Array[String] = []
	for numero in range(1, SceneRouter.NB_ETAPES + 1):
		if not SceneRouter.etape_existe(numero):
			continue
		var etape := (load(SceneRouter.chemin_etape(numero)) as PackedScene).instantiate() as EtapeBase
		add_child_autofree(etape)
		await wait_process_frames(2)
		for n in etape.find_children("*", "", true, false):
			var item: CanvasItem = null
			if n is Label and (n as Label).get_canvas_layer_node() == null:
				item = n as Label
			elif n is ColorRect and n.name == &"Visuel" and (n.get_parent() is Interactif or n.get_parent() is Verrou):
				item = n as ColorRect
			if item == null or not item.is_visible_in_tree():
				continue
			if RougeLisible._lieu_habille(etape, etape.lieu_de(item)):
				echecs.append("étape %d : %s" % [numero, etape.get_path_to(item)])
	assert_eq(echecs.size(), 0, "Maquette visible dans un lieu habillé :\n%s" % "\n".join(echecs))


func test_les_ceintures_de_l_etape_2_ne_font_plus_de_barre_rouge() -> void:
	var etape: EtapeBase = add_child_autofree(load("res://scenes/etapes/etape_02/etape_02.tscn").instantiate())
	await wait_process_frames(2)
	for chemin: String in ["Surface/Brouillard/CeintureUne/Visuel", "Surface/Brouillard/CeintureDeux/Visuel"]:
		var visuel := etape.get_node_or_null(chemin) as CanvasItem
		if visuel != null:
			assert_false(visuel.visible, chemin)


func test_le_dessin_d_un_personnage_et_le_repere_restent_visibles() -> void:
	var etape: EtapeBase = add_child_autofree(load("res://scenes/etapes/etape_02/etape_02.tscn").instantiate())
	await wait_process_frames(2)
	var poste := etape.trouver_declencheur(&"e2_poste")
	assert_true(poste.dessin.is_visible_in_tree(), "Brisse reste dessiné")
	var cheval := (etape.get_node("Decors") as DecorE2).cheval_frise
	assert_true(cheval.is_visible_in_tree(), "le cheval de frise reste sur la chicane")
