extends GutTest
## Règle du Game Director : le rouge est réservé au sang et au sceau, maquette comprise.
## Aucun ColorRect d'aucune étape (placeholders de rencontres, détails, verrous) n'est rouge,
## même dans un lieu pas encore habillé, pour qu'aucun test ne nous habitue au rouge ailleurs.

const SEUIL := 0.15


func test_aucun_color_rect_rouge_dans_les_etapes() -> void:
	var echecs: Array[String] = []
	for numero in range(1, SceneRouter.NB_ETAPES + 1):
		if not SceneRouter.etape_existe(numero):
			continue
		var etape := (load(SceneRouter.chemin_etape(numero)) as PackedScene).instantiate()
		for n in etape.find_children("*", "ColorRect", true, false):
			var c := (n as ColorRect).color
			if c.a > 0.0 and c.r - maxf(c.g, c.b) > SEUIL:
				echecs.append("étape %d : %s" % [numero, etape.get_path_to(n)])
		etape.free()
	assert_eq(echecs.size(), 0, "placeholders rouges :\n%s" % "\n".join(echecs))
