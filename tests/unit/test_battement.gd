extends GutTest
## Battement de Lucidité basse : deux coups puis un silence, à 10 i/s, partagé par le ruban de
## Tobie, le HUD et les tremblements.


func _opacites(palier: StringName, images: int) -> Array[float]:
	var liste: Array[float] = []
	for i in images:
		liste.append(Battement.opacite((i + 0.5) / 10.0, palier, false))
	return liste


func test_clair_ne_bat_pas() -> void:
	for a in _opacites(&"clair", 30):
		assert_eq(a, 1.0)


func test_trouble_deux_coups_puis_silence_en_1_2_s() -> void:
	var attendu: Array[float] = [1.0, 0.55, 1.0, 0.55, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
	assert_eq(_opacites(&"trouble", 12), attendu)
	assert_true(Battement.coup(0.15, &"trouble", false))
	assert_false(Battement.coup(0.55, &"trouble", false))


func test_egare_plus_rapide_en_0_8_s() -> void:
	# Hors disparition : le cycle de 8 images.
	assert_eq(Battement.IMAGES_CYCLE[&"egare"], 8)
	assert_true(Battement.coup(0.85 + 0.1, &"egare", false), "image 9 = image 1 du 2e cycle")


func test_effets_attenues_rien_ne_bat() -> void:
	for i in 200:
		var t := i / 10.0 + 0.05
		assert_eq(Battement.opacite(t, &"egare", true), 1.0)
		assert_false(Battement.coup(t, &"trouble", true))


func test_egare_disparait_2_images_toutes_les_4_a_7_s() -> void:
	var debuts: Array[float] = []
	var avant := false
	for i in 1200:
		var t := (i + 0.5) / 10.0
		var d := Battement.disparu(t, &"egare", false)
		if d and not avant:
			debuts.append(t)
		avant = d
	assert_gt(debuts.size(), 15)
	for k in range(1, debuts.size()):
		var ecart := debuts[k] - debuts[k - 1]
		assert_between(ecart, 3.95, 7.05, "écart %d" % k)
	var duree := 0
	# Fenêtre de 3 s : plus courte que l'écart minimal (4 s), une seule disparition dedans.
	for i in 30:
		if Battement.disparu(debuts[0] - 0.1 + i / 10.0, &"egare", false):
			duree += 1
	assert_eq(duree, 2, "2 images")
	assert_false(Battement.disparu(debuts[0], &"trouble", false), "seulement à l'Égaré")


func test_meme_instant_meme_opacite_pour_tous() -> void:
	var t := 123.45
	assert_eq(Battement.opacite(t, &"egare", false), Battement.opacite(t, &"egare", false))
