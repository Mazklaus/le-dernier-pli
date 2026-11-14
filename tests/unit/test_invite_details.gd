extends GutTest
## Invite v2 (spec UI/UX, demande du Game Director) : taille, persistance à la sortie de
## zone, placement dans les marges et hors des plaques du HUD ; repère des détails.

const SceneMessager := preload("res://scenes/messager/messager.tscn")
const SceneDeclencheur := preload("res://scenes/interactions/declencheur_dialogue/declencheur_dialogue.tscn")
const Dialogue := preload("res://scenes/bac_a_sable/bac_a_sable.dialogue")


func before_each() -> void:
	GameState.reinitialiser()


func after_all() -> void:
	GameState.reinitialiser()


func _invite() -> InviteInteraction:
	var invite := InviteInteraction.new()
	add_child_autofree(invite)
	return invite


func _declencheur(id: StringName, x: float) -> DeclencheurDialogue:
	var d: DeclencheurDialogue = SceneDeclencheur.instantiate()
	d.rencontre_id = id
	d.dialogue = Dialogue
	d.libelle = "Examiner l'écriteau"
	d.position = Vector2(x, 500)
	add_child_autofree(d)
	return d


func test_constantes_de_la_spec() -> void:
	assert_eq(InviteInteraction.TAILLE_TEXTE, 28)
	assert_almost_eq(InviteInteraction.RAPPORT_TOUCHE, 1.1, 0.001)
	assert_eq(InviteInteraction.MARGE_PLAQUE, 10.0)
	assert_eq(InviteInteraction.PERSISTANCE, 0.6)
	assert_eq(InviteInteraction.DUREE_EFFACEMENT, 0.4)
	assert_eq(InviteInteraction.MARGE_ECRAN, 24.0)
	assert_eq(RepereExamen.TAILLE, 40.0)


func test_touche_en_carre_d_encre_et_libelle_a_28() -> void:
	var invite := _invite()
	invite.definir_cible(_declencheur(&"e9_detail_test", 100))
	assert_eq(invite._etiquette.get_theme_font_size(&"font_size"), 28)
	assert_eq(invite._etiquette.text, "Examiner l'écriteau")
	assert_eq(invite._lettre.text, "E")
	assert_eq(invite._lettre.get_theme_color(&"font_color"), StylePapier.PAPIER)
	assert_almost_eq(invite._touche.custom_minimum_size.y, roundf(28 * 1.1), 0.5)


func test_persiste_puis_s_efface_et_revenir_annule() -> void:
	var invite := _invite()
	var d := _declencheur(&"e9_detail_test", 100)
	invite.definir_cible(d)
	await wait_seconds(0.3)
	invite.definir_cible(null)
	await wait_seconds(0.4)
	assert_almost_eq(invite.modulate.a, 1.0, 0.01, "encore pleinement visible à 0,4 s")
	invite.definir_cible(d)
	await wait_seconds(0.8)
	assert_almost_eq(invite.modulate.a, 1.0, 0.01, "revenir annule l'effacement")
	invite.definir_cible(null)
	await wait_seconds(1.2)
	assert_false(invite.visible, "effacée après 0,6 + 0,4 s")


func test_placement_dans_les_marges_et_sous_les_plaques() -> void:
	var ecran := Vector2(1920, 1080)
	var taille := Vector2(300, 60)
	var aucune: Array[Rect2] = []
	var p := InviteInteraction.placer(Vector2(-50, -50), taille, ecran, aucune)
	assert_eq(p, Vector2(24, 24))
	p = InviteInteraction.placer(Vector2(1800, 1050), taille, ecran, aucune)
	assert_eq(p, Vector2(1920 - 24 - 300, 1080 - 24 - 60))
	var plaque := Rect2(38, 38, 340, 180)
	var plaques: Array[Rect2] = [plaque]
	p = InviteInteraction.placer(Vector2(100, 100), taille, ecran, plaques)
	assert_eq(p.y, plaque.end.y + 24, "jamais sous la plaque du HUD")


func test_repere_sur_les_details_seulement() -> void:
	var detail := _declencheur(&"e9_detail_test", 100)
	var rencontre := _declencheur(&"e9_ordre", 800)
	assert_not_null(detail.repere)
	assert_null(rencontre.repere)


func test_repere_visible_des_que_le_detail_est_a_l_ecran() -> void:
	var ecran := Rect2(1000, 0, 1920, 1080)
	assert_true(RepereExamen.est_a_l_ecran(Vector2(1010, 500), ecran))
	assert_true(RepereExamen.est_a_l_ecran(Vector2(990, 500), ecran), "en partie à l'écran")
	assert_false(RepereExamen.est_a_l_ecran(Vector2(900, 500), ecran))
	assert_false(RepereExamen.est_a_l_ecran(Vector2(3000, 500), ecran))


func test_repere_visible_de_loin_et_efface_une_fois_examine() -> void:
	var detail := _declencheur(&"e9_detail_test", 500)
	var m: Messager = add_child_autofree(SceneMessager.instantiate())
	m.gravite = 0.0
	m.teleporter(Vector2(500 + 450, 500))
	await wait_process_frames(3)
	assert_true(detail.repere.doit_paraitre(), "à 450 px, à l'écran : bien plus loin que l'invite")
	m.teleporter(Vector2(500 + 6000, 500))
	await wait_process_frames(3)
	assert_false(detail.repere.doit_paraitre(), "hors de l'écran")
	m.teleporter(Vector2(500 + 50, 500))
	await wait_process_frames(3)
	GameState.marquer_rencontre_vue(&"e9_detail_test")
	assert_false(detail.repere.doit_paraitre(), "examiné : plus de repère")


func test_les_douze_details_de_l_etape_1_ont_leur_repere() -> void:
	# Garde-fou : un renommage d'id ne doit pas faire disparaître un astérisque sans prévenir.
	var etape: EtapeBase = add_child_autofree(load("res://scenes/etapes/etape_01/etape_01.tscn").instantiate())
	var avec_repere := 0
	for n in get_tree().get_nodes_in_group(Interactif.GROUPE):
		if n is DeclencheurDialogue and etape.is_ancestor_of(n) and (n as DeclencheurDialogue).repere != null:
			avec_repere += 1
	assert_eq(avec_repere, 12, "12 détails à examiner (Level Designer, #29)")


func test_est_detail_force_le_repere() -> void:
	var d: DeclencheurDialogue = SceneDeclencheur.instantiate()
	d.rencontre_id = &"e9_ecriteau"
	d.est_detail = true
	add_child_autofree(d)
	assert_not_null(d.repere)



func test_repere_dessine_par_le_sprite_du_da() -> void:
	var detail := _declencheur(&"e9_detail_test", 100)
	var dessin := detail.repere.get_node("Dessin") as Sprite2D
	assert_not_null(dessin.texture)
	assert_eq(dessin.texture.get_size(), Vector2(RepereExamen.TAILLE, RepereExamen.TAILLE))
