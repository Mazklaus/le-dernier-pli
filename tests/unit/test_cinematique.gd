extends GutTest
## Lecteur de cinématique (directive animation du GD) : 10 i/s, saut, effets atténués,
## prise et rendu du contrôle, une seule fois par partie.

const SceneMessager := preload("res://scenes/messager/messager.tscn")

var cine: Cinematique
var messager: Messager


func before_each() -> void:
	GameState.reinitialiser()
	Reglages.changer(&"effets_attenues", false)
	messager = add_child_autofree(SceneMessager.instantiate())
	cine = add_child_autofree(_fabriquer(&"test_cine"))


func after_each() -> void:
	Reglages.changer(&"effets_attenues", false)


## Une cinématique d'une seconde : la caméra glisse de x 0 à x 100.
func _fabriquer(id: StringName) -> Cinematique:
	var c := Cinematique.new()
	c.id = id
	var camera := Camera2D.new()
	camera.name = "Camera"
	c.add_child(camera)
	var lecteur := AnimationPlayer.new()
	lecteur.name = "Animation"
	var anim := Animation.new()
	anim.length = 1.0
	var piste := anim.add_track(Animation.TYPE_VALUE)
	anim.track_set_path(piste, ^"Camera:position")
	anim.track_insert_key(piste, 0.0, Vector2(0, 0))
	anim.track_insert_key(piste, 1.0, Vector2(100, 0))
	var biblio := AnimationLibrary.new()
	biblio.add_animation(Cinematique.ANIMATION_PAR_DEFAUT, anim)
	lecteur.add_animation_library(&"", biblio)
	c.add_child(lecteur)
	return c


func _camera() -> Camera2D:
	return cine.get_node("Camera") as Camera2D


func test_avance_par_pas_de_un_dixieme() -> void:
	cine.jouer()
	assert_true(cine.en_cours)
	cine._process(0.05)
	assert_almost_eq(_camera().position.x, 0.0, 0.01, "pas encore une image")
	cine._process(0.05)
	assert_almost_eq(_camera().position.x, 10.0, 0.01, "une image de 1/10 s")
	cine._process(0.25)
	assert_almost_eq(_camera().position.x, 30.0, 0.01, "deux images de plus, le reste attend")


func test_prend_puis_rend_le_controle() -> void:
	var camera_jeu := get_viewport().get_camera_2d()
	cine.jouer()
	assert_true(messager.bloque, "messager bloqué")
	assert_true(_camera().is_current(), "caméra de la cinématique")
	for i in 12:
		cine._process(0.1)
	assert_false(cine.en_cours)
	assert_false(messager.bloque, "contrôle rendu")
	assert_eq(get_viewport().get_camera_2d(), camera_jeu, "caméra du jeu rendue")
	assert_almost_eq(_camera().position.x, 100.0, 0.01, "état final gardé")


func test_saut_va_a_la_fin_et_rend_la_main() -> void:
	watch_signals(cine)
	cine.jouer()
	cine._process(0.1)
	cine.sauter()
	assert_false(cine.en_cours)
	assert_almost_eq(_camera().position.x, 100.0, 0.01, "état final appliqué")
	assert_signal_emitted_with_parameters(cine, "finie", [true])
	assert_false(messager.bloque)


func test_la_touche_annuler_saute() -> void:
	cine.jouer()
	var evt := InputEventAction.new()
	evt.action = &"annuler"
	evt.pressed = true
	var touche := InputEventKey.new()
	touche.pressed = true
	for e in InputMap.action_get_events(&"annuler"):
		if e is InputEventKey:
			touche.keycode = (e as InputEventKey).keycode
			touche.physical_keycode = (e as InputEventKey).physical_keycode
	cine._input(touche)
	assert_false(cine.en_cours, "annuler saute la cinématique")


func test_une_seule_fois_par_partie() -> void:
	cine.jouer()
	cine.sauter()
	assert_true(GameState.rencontre_vue(Cinematique.drapeau(&"test_cine")))
	var sautee: bool = await cine.jouer()
	assert_false(sautee)
	assert_false(cine.en_cours, "déjà vue : ne se rejoue pas")


func test_effets_attenues_la_camera_coupe() -> void:
	Reglages.changer(&"effets_attenues", true)
	cine.jouer()
	for i in 9:
		cine._process(0.1)
	assert_almost_eq(_camera().position.x, 0.0, 0.01, "pas de glissement : plan de départ tenu")
	cine._process(0.1)
	assert_almost_eq(_camera().position.x, 100.0, 0.01, "coupe sur le plan d'arrivée")
	var originale := cine.get_node("Animation").get_animation(Cinematique.ANIMATION_PAR_DEFAUT) as Animation
	assert_eq(originale.track_get_interpolation_type(0), Animation.INTERPOLATION_LINEAR, "l'originale reste intacte")


func test_cinematiques_masque_l_interface_et_ignore_un_id_inconnu() -> void:
	var interface := CanvasLayer.new()
	interface.add_to_group(Cinematiques.GROUPE_MASQUE)
	add_child_autofree(interface)
	assert_false(await Cinematiques.jouer(&"absente"), "pas placée : rien")
	Cinematiques.jouer(&"test_cine")
	assert_eq(Cinematiques.en_cours, &"test_cine")
	assert_false(interface.visible, "interface masquée")
	cine.sauter()
	await wait_process_frames(1)
	assert_true(interface.visible, "interface rendue")
	assert_eq(Cinematiques.en_cours, &"")


func test_cadrage_par_marqueurs_sans_animation() -> void:
	var c := Cinematique.new()
	c.id = &"test_marqueurs"
	c.duree = 2.0
	var camera := Camera2D.new()
	camera.name = "Camera"
	c.add_child(camera)
	var depart := Marker2D.new()
	depart.name = "Depart"
	depart.position = Vector2(0, 0)
	c.add_child(depart)
	var arrivee := Marker2D.new()
	arrivee.name = "Arrivee"
	arrivee.position = Vector2(200, 0)
	arrivee.scale = Vector2(2, 2)
	c.add_child(arrivee)
	add_child_autofree(c)
	c.jouer()
	for i in 10:
		c._process(0.1)
	assert_almost_eq(camera.position.x, 100.0, 0.01, "à mi-parcours")
	assert_almost_eq(camera.zoom.x, 1.5, 0.01, "zoom à mi-parcours")
	for i in 10:
		c._process(0.1)
	assert_false(c.en_cours)
	assert_almost_eq(camera.zoom.x, 2.0, 0.01)


func test_retiree_en_cours_de_lecture_rend_la_main() -> void:
	watch_signals(cine)
	cine.jouer()
	remove_child(cine)
	assert_false(cine.en_cours)
	assert_false(messager.bloque, "contrôle rendu")
	assert_signal_emitted_with_parameters(cine, "finie", [true])
	add_child(cine)


func test_au_debut_etape_ignore_une_etape_qui_n_est_pas_la_scene_courante() -> void:
	var etape := Node2D.new()
	add_child_autofree(etape)
	var c := _fabriquer(&"test_arrivee")
	c.au_debut_etape = true
	etape.add_child(c)
	SceneRouter.etape_prete.emit(etape)
	await wait_process_frames(2)
	assert_false(c.en_cours, "étape de test : pas de cinématique d'arrivée")


func test_la_camera_du_plan_ne_prend_pas_la_vue_hors_lecture() -> void:
	# #164 : une Camera2D active prenait la vue dès son entrée dans l'arbre.
	await wait_process_frames(1)
	assert_false(_camera().enabled, "éteinte hors lecture")
	assert_ne(get_viewport().get_camera_2d(), _camera())
	cine.jouer()
	assert_true(_camera().enabled)
	assert_true(_camera().is_current())
	cine.sauter()
	assert_false(_camera().enabled, "éteinte après la lecture")
	assert_ne(get_viewport().get_camera_2d(), _camera())
