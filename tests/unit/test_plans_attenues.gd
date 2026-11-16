extends GutTest
## CinematiquePlans : une ciné qui lit « effets atténués » dans construire() (au chargement de
## l'étape) est reconstruite au moment de jouer si le réglage a changé entre-temps.


class CineReglee extends CinematiquePlans:
	var constructions := 0

	func construire() -> Animation:
		constructions += 1
		var couche := couche_plein_ecran()
		var marque := Node2D.new()
		marque.name = "Fixe" if Reglages.valeur(&"effets_attenues") else "Mouvement"
		couche.add_child(marque)
		var anim := Animation.new()
		anim.length = 0.2
		cle(anim, "Plans:visible", 0.0, true)
		cle(anim, "Plans:visible", 0.2, false)
		return anim


func after_each() -> void:
	Reglages.changer(&"effets_attenues", false)
	GameState.reinitialiser()


func _cine() -> CineReglee:
	var c := CineReglee.new()
	c.id = &"test_plans_attenues"
	c.une_seule_fois = false
	return add_child_autofree(c)


func test_reconstruite_si_le_reglage_a_change() -> void:
	Reglages.changer(&"effets_attenues", false)
	var c := _cine()
	assert_eq(c.constructions, 1)
	assert_not_null(c.get_node_or_null("Plans/Mouvement"))
	Reglages.changer(&"effets_attenues", true)
	c.jouer()
	assert_eq(c.constructions, 2, "refaite avant de jouer")
	assert_not_null(c.get_node_or_null("Plans/Fixe"))
	assert_null(c.get_node_or_null("Plans/Mouvement"), "l'ancienne construction est retirée")
	assert_eq(c.get_children().filter(func(n: Node) -> bool: return n is CanvasLayer).size(), 1)
	c.sauter()


func test_pas_reconstruite_si_le_reglage_n_a_pas_change() -> void:
	var c := _cine()
	c.jouer()
	assert_eq(c.constructions, 1)
	c.sauter()
