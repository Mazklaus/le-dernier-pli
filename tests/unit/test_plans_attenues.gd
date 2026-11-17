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


## Écran plus large que 16:9 (stretch expand) : plans centrés, bandeau sombre sur toute la vue,
## et le bandeau ne compte pas parmi les plans (QA, procession e3 en 2560 × 1080).
func test_ecran_large_plans_centres_sur_un_bandeau() -> void:
	var vue := SubViewport.new()
	vue.size = Vector2i(2560, 1200)
	add_child_autofree(vue)
	var c := CineReglee.new()
	c.id = &"test_plans_large"
	c.une_seule_fois = false
	vue.add_child(c)
	var couche := c.get_node("Plans") as CanvasLayer
	assert_eq(couche.offset, Vector2(320, 60), "repère 1920×1080 centré")
	assert_eq(couche.get_child_count(), 1, "seul le plan compte, pas le bandeau")
	var bandeau := couche.get_node("Bandeau") as ColorRect
	assert_eq(bandeau.size, Vector2(2560, 1200), "bandeau sur toute la vue")
	assert_eq(bandeau.position, Vector2(-320, -60))
	vue.size = Vector2i(1920, 1080)
	c.jouer()
	assert_eq(couche.offset, Vector2.ZERO, "recadré à la lecture")
	c.sauter()
