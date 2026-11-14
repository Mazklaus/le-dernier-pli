extends GutTest
## Règles du mixage d'ambiance selon la Lucidité (scripts/regles/mixage_son.gd).


func test_clair_ne_joue_que_le_reel() -> void:
	var c := MixageSon.cible(&"clair", false, false)
	assert_eq(c["reel"], 1.0)
	assert_eq(c["autre"], 0.0)
	assert_eq(c["coupure_hz"], 20000.0)


func test_paliers_trouble_et_egare() -> void:
	assert_almost_eq(MixageSon.cible(&"trouble", false, false)["autre"], 0.45, 0.001)
	var egare := MixageSon.cible(&"egare", false, false)
	assert_almost_eq(egare["reel"], 0.25, 0.001)
	assert_eq(egare["autre"], 1.0)


func test_perdu_remplace_le_palier() -> void:
	var c := MixageSon.cible(&"egare", true, false)
	assert_almost_eq(c["reel"], 0.10, 0.001)
	assert_eq(c["coupure_hz"], MixageSon.COUPURE_PERDU)
	# Perdu suit le drapeau, pas la valeur : même remonté en Trouble, on reste Perdu.
	assert_almost_eq(MixageSon.cible(&"trouble", true, false)["reel"], 0.10, 0.001)


func test_le_noir_fait_monter_l_autre_sans_depasser_1() -> void:
	assert_almost_eq(MixageSon.cible(&"clair", false, true)["autre"], 0.20, 0.001)
	assert_almost_eq(MixageSon.cible(&"trouble", false, true)["autre"], 0.65, 0.001)
	assert_eq(MixageSon.cible(&"egare", false, true)["autre"], 1.0)


func test_palier_inconnu_retombe_sur_clair() -> void:
	assert_eq(MixageSon.cible(&"inconnu", false, false)["reel"], 1.0)


func test_gain_voix_interpole_entre_reperes() -> void:
	var points := MixageSon.points_depuis_reperes({
		&"pied_echelle": 3000.0, &"boyau_arriere": 0.0, &"carrefour": 1000.0,
		&"periscope": 2000.0, &"autre_chose": 500.0,
	})
	assert_eq(points.size(), 4)
	assert_eq(MixageSon.gain_voix(-50.0, points), 1.0)
	assert_almost_eq(MixageSon.gain_voix(500.0, points), 0.85, 0.001)
	assert_almost_eq(MixageSon.gain_voix(2000.0, points), 0.35, 0.001)
	assert_almost_eq(MixageSon.gain_voix(9999.0, points), 0.1, 0.001)


func test_gain_voix_sans_repere_vaut_1() -> void:
	var vide: Array[Vector2] = []
	assert_eq(MixageSon.gain_voix(123.0, vide), 1.0)


func test_vers_db_plancher_muet() -> void:
	assert_eq(MixageSon.vers_db(0.0), MixageSon.GAIN_MUET_DB)
	assert_almost_eq(MixageSon.vers_db(1.0), 0.0, 0.001)
