extends CinematiquePlans
## e7_ouverture_sceau (planches de la DA, tools/gen_cin_e7.py) : branche « Briser le sceau » de
## e7_sceau. Un seul gros plan, rien d'autre ne bouge : fond cin_sceau_01, puis 10 images de
## 1320×940 (cin_sceau_02, grille 3 × 4) en (300, 140) : le pli fermé, la cire se fend, éclate,
## le ruban glisse et sort du cadre, le pli s'ouvre, l'index glisse sous la première ligne.

const FOND := "res://assets/graphics/cin/cin_sceau_01.png"
const IMAGES := "res://assets/graphics/cin/cin_sceau_02.png"
## Durée de chaque image, 0 à 9 (TEMPS_SCEAU de la DA) : 8 s en tout.
const DUREES := [1.5, 0.8, 0.3, 0.3, 0.3, 0.4, 0.8, 0.8, 0.3, 2.5]

var couche: CanvasLayer


func construire() -> Animation:
	var fond := planche(FOND)
	var images_sceau := planche(IMAGES)
	if fond == null or images_sceau == null:
		return null
	couche = couche_plein_ecran()
	couche.add_child(sprite("Fond", fond, Vector2.ZERO))
	couche.add_child(sprite("Sceau", images_sceau, Vector2(300, 140), 3, 4))

	var anim := Animation.new()
	cle(anim, "Plans:visible", 0.0, true)
	var t := 0.0
	for i in DUREES.size():
		cle(anim, "Plans/Sceau:frame", t, i)
		t += float(DUREES[i])
	anim.length = snappedf(t, Cinematique.PAS)
	cle(anim, "Plans:visible", anim.length, false)
	return anim


func apres() -> void:
	if couche != null:
		couche.visible = false
