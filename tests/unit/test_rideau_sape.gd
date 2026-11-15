extends GutTest
## Couverture anti-gaz de la sape de sortie (étape 1) : fermée, rien ne bouge ; ouverte après
## e1_adieu, Tobie la soulève en passant et elle retombe en 6 images à 10 i/s.

var _verrou: Verrou
var _rideau: RideauSape


func before_each() -> void:
	GameState.reinitialiser()
	_verrou = Verrou.new()
	_verrou.rencontre = &"e1_adieu"
	_verrou.position = Vector2(1580, 675)
	add_child_autofree(_verrou)
	var image := Image.create(840, 460, false, Image.FORMAT_RGBA8)
	_rideau = RideauSape.creer(_verrou, ImageTexture.create_from_image(image))
	add_child_autofree(_rideau)


func after_all() -> void:
	GameState.reinitialiser()


func test_pose_sur_le_verrou_en_6_images() -> void:
	assert_eq(_rideau.position, Vector2(1580, 675))
	assert_eq(_rideau.dessin.hframes, 6)
	assert_eq(_rideau.dessin.frame, 0)


func test_sans_verrou_ou_sans_planche() -> void:
	assert_null(RideauSape.creer(null, ImageTexture.new()))


func test_verrou_ferme_la_couverture_ne_bouge_pas() -> void:
	assert_false(_rideau.soulever())
	assert_false(_rideau.en_cours)


func test_ouverte_elle_se_souleve_et_retombe() -> void:
	GameState.marquer_rencontre_vue(&"e1_adieu")
	assert_true(_rideau.visible, "la couverture reste en place quand le verrou s'efface")
	assert_true(_rideau.soulever())
	assert_false(_rideau.soulever(), "pas de reprise pendant qu'elle se balance")
	_rideau._process(0.25)
	assert_eq(_rideau.dessin.frame, 2, "soulevée")
	_rideau._process(0.3)
	assert_eq(_rideau.dessin.frame, 5)
	_rideau._process(0.1)
	assert_eq(_rideau.dessin.frame, 0, "tendue de nouveau")
	assert_false(_rideau.en_cours)
	assert_true(_rideau.soulever(), "Tobie peut repasser")
