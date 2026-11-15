extends CinematiquePlans
## e5_autre_se_retourne (planches de la DA, tools/gen_cin_e5.py) : au bout de la boucle, l'Autre
## marche sur place au loin (« il ne s'approche pas, il ne s'éloigne pas »), s'arrête, sa tête
## tourne à moitié (jamais jusqu'au visage), revient, et il repart du même pas.
## Un plan plein écran : fond cin_autre_01, 6 images de 200×170 (cin_autre_02, grille 3 × 2) en
## (880, 500). 0 et 5 sont les deux appuis de la marche : alternés à 3 i/s, il marche sur place.
## 1 il s'arrête, 2 et 3 la tête tourne (10 i/s), tenue sur 3, 4 elle revient, puis la marche
## reprend et une tenue finale. Le sprite ne bouge jamais : fond et images opaques, alignés au pixel.

const FOND := "res://assets/graphics/cin/cin_autre_01.png"
const GESTE := "res://assets/graphics/cin/cin_autre_02.png"
const MARCHE := 2.0
const CADENCE_MARCHE := 1.0 / 3.0
const TENUE_TETE := 1.2
const TENUE_FIN := 0.5

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
	var t := marcher(anim, 0.0)
	t = images(anim, "Plans/Autre", t, 1, 3) - Cinematique.PAS + TENUE_TETE
	t = images(anim, "Plans/Autre", t, 4, 4)
	t = marcher(anim, t) + TENUE_FIN
	anim.length = snappedf(t, Cinematique.PAS)
	cle(anim, "Plans:visible", anim.length, false)
	return anim


## Les appuis 0 et 5 en alternance pendant MARCHE secondes, à partir de debut ; rend la fin.
func marcher(anim: Animation, debut: float) -> float:
	var pas := roundi(MARCHE / CADENCE_MARCHE)
	for k in pas:
		cle(anim, "Plans/Autre:frame", debut + k * CADENCE_MARCHE, 0 if k % 2 == 0 else 5)
	return debut + MARCHE


func apres() -> void:
	if couche != null:
		couche.visible = false
