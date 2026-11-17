extends GutTest
## Étape 6 : après la ciné e6_porte_scellee, Éloi n'est plus devant la porte ; son bocal y reste.

const SceneDeclencheur := preload("res://scenes/interactions/declencheur_dialogue/declencheur_dialogue.tscn")
const DRAPEAU := &"cine_e6_porte_scellee"


func before_each() -> void:
	GameState.reinitialiser()


func after_all() -> void:
	GameState.reinitialiser()


func test_eloi_quitte_la_scene_a_la_fin_de_la_cine() -> void:
	var d: DeclencheurDialogue = SceneDeclencheur.instantiate()
	d.personnage = &"eloi"
	d.absent_apres = DRAPEAU
	add_child_autofree(d)
	assert_true(d.dessin.visible)
	GameState.marquer_rencontre_vue(DRAPEAU)
	assert_false(d.dessin.visible)


func test_eloi_reste_absent_au_rechargement() -> void:
	GameState.marquer_rencontre_vue(DRAPEAU)
	var d: DeclencheurDialogue = SceneDeclencheur.instantiate()
	d.personnage = &"eloi"
	d.absent_apres = DRAPEAU
	add_child_autofree(d)
	assert_false(d.dessin.visible)


func test_le_bocal_apparait_avec_le_drapeau() -> void:
	var b := DecorApres.new()
	b.drapeau = DRAPEAU
	add_child_autofree(b)
	assert_false(b.visible)
	GameState.marquer_rencontre_vue(DRAPEAU)
	assert_true(b.visible)


func test_le_seuil_est_regle() -> void:
	var seuil := (load("res://scenes/etapes/etape_06/lieux/seuil.tscn") as PackedScene).instantiate()
	autofree(seuil)
	var d := seuil.get_node("Rencontres/e6_seuil") as DeclencheurDialogue
	assert_eq(d.absent_apres, DRAPEAU)
	var b := seuil.get_node_or_null("BocalEloi") as DecorApres
	assert_not_null(b)
	if b != null:
		assert_eq(b.drapeau, DRAPEAU)
		assert_not_null(b.texture)
