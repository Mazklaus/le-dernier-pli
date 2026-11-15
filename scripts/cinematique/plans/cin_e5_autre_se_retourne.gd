extends CinematiquePlans
## e5_autre_se_retourne (planches de la DA, tools/gen_cin_e5.py) : au bout de la boucle, l'Autre
## s'arrête, sa tête tourne à moitié (jamais jusqu'au visage), revient, et il repart du même pas.
## Un plan plein écran à 10 i/s : fond cin_autre_01, 6 images de 200×170 (cin_autre_02, grille
## 3 × 2) en (880, 500) : 0 il marche, 1 il s'arrête, 2 et 3 la tête tourne, 4 elle revient,
## 5 il repart. Un temps sur 0, puis 1 à 3, une tenue sur 3, puis 4 et 5, une tenue sur 5.

const FOND := "res://assets/graphics/cin/cin_autre_01.png"
const GESTE := "res://assets/graphics/cin/cin_autre_02.png"
const TENUE_DEBUT := 1.0
const TENUE_TETE := 0.8
const TENUE_FIN := 1.0

var couche: CanvasLayer


func construire() -> Animation:
	var fond := planche(FOND)
	var geste := planche(GESTE)
	if fond == null or geste == null:
		return null
	couche = couche_plein_ecran()
	couche.add_child(sprite("Fond", fond, Vector2.ZERO))
	couche.add_child(sprite("Autre", geste, Vector2(880, 500), 3, 2))

	var anim := Animation.new()
	cle(anim, "Plans:visible", 0.0, true)
	cle(anim, "Plans/Autre:frame", 0.0, 0)
	var t := images(anim, "Plans/Autre", TENUE_DEBUT, 1, 3) - Cinematique.PAS + TENUE_TETE
	t = images(anim, "Plans/Autre", t, 4, 5) - Cinematique.PAS + TENUE_FIN
	anim.length = snappedf(t, Cinematique.PAS)
	cle(anim, "Plans:visible", anim.length, false)
	return anim


func apres() -> void:
	if couche != null:
		couche.visible = false
