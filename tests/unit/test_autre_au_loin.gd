extends GutTest
## L'Autre en jeu à l'étape 5 : il apparaît avec e5_autre et reste hors d'atteinte.

const SceneDeclencheur := preload("res://scenes/interactions/declencheur_dialogue/declencheur_dialogue.tscn")


func test_il_garde_ses_distances_jusqu_au_bout_du_sentier() -> void:
	assert_eq(AutreAuLoin.position_suivie(1000.0, 550.0, 3820.0), 1550.0)
	assert_eq(AutreAuLoin.position_suivie(3500.0, 550.0, 3820.0), 3820.0, "acculé")


func test_accule_il_se_dissout_si_tobie_approche() -> void:
	assert_false(AutreAuLoin.doit_se_dissiper(3700.0, 3300.0, 3820.0, 300.0), "pas acculé")
	assert_false(AutreAuLoin.doit_se_dissiper(3820.0, 3300.0, 3820.0, 300.0), "encore loin")
	assert_true(AutreAuLoin.doit_se_dissiper(3820.0, 3600.0, 3820.0, 300.0))


func test_il_apparait_quand_la_rencontre_commence() -> void:
	var lieu := Node2D.new()
	add_child_autofree(lieu)
	var d: DeclencheurDialogue = SceneDeclencheur.instantiate()
	d.name = "e5_autre"
	lieu.add_child(d)
	var autre := AutreAuLoin.new()
	autre.declencheur = NodePath("../e5_autre")
	lieu.add_child(autre)
	assert_false(autre.visible)
	d.dialogue_commence.emit(d)
	if autre.dessin == null:
		assert_eq(autre.etat, AutreAuLoin.Etat.CACHE, "sans planche, rien ne se montre")
		pending("planche chr_autre_marche_01 pas encore livrée par la DA")
		return
	assert_true(autre.visible)
	assert_eq(autre.etat, AutreAuLoin.Etat.PRESENT)
	autre.dissiper()
	assert_eq(autre.etat, AutreAuLoin.Etat.DISSIPE)


func test_il_est_place_au_bout_de_la_boucle() -> void:
	var etape := (load("res://scenes/etapes/etape_05/etape_05.tscn") as PackedScene).instantiate()
	autofree(etape)
	var autre := etape.get_node_or_null("Surface/Boucle/AutreAuLoin") as AutreAuLoin
	assert_not_null(autre)
	if autre != null:
		assert_eq(autre.declencheur, NodePath("../e5_autre"))
