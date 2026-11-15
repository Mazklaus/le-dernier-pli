extends CinematiquePlans
## e1_remise_pli (planches de la DA, tools/gen_cin_e1.py) : deux plans plein écran à 10 i/s,
## coupe franche entre les deux.
## Plan A : la main de Lamarre tend le pli, celle de Tobie le saisit, Lamarre lâche
##          (fond cin_remise-pli_01, 6 images de 1440×840 en (0, 240)).
## Plan B : le pli monte et se glisse sous la bandoulière, la main se pose dessus
##          (fond cin_remise-pli_03, 4 images de 1200×780 en (300, 300)).

const DOSSIER := "res://assets/graphics/cin/cin_remise-pli_%02d.png"
## [début, première image animée, fin du plan] : un temps sur la première image, le geste,
## puis un temps sur la dernière.
const PLAN_A := [0.0, 1.0, 2.8]
const PLAN_B := [2.8, 3.6, 5.4]

var couche: CanvasLayer


func construire() -> Animation:
	var t: Array[Texture2D] = []
	for i in range(1, 5):
		t.append(planche(DOSSIER % i))
	if t.has(null):
		return null
	couche = couche_plein_ecran()
	var a := Node2D.new()
	a.name = "A"
	a.add_child(sprite("Fond", t[0], Vector2.ZERO))
	a.add_child(sprite("Geste", t[1], Vector2(0, 240), 2, 3))
	var b := Node2D.new()
	b.name = "B"
	b.add_child(sprite("Fond", t[2], Vector2.ZERO))
	b.add_child(sprite("Geste", t[3], Vector2(300, 300), 2, 2))
	couche.add_child(a)
	couche.add_child(b)

	var anim := Animation.new()
	anim.length = PLAN_B[2]
	cle(anim, "Plans:visible", 0.0, true)
	cle(anim, "Plans/A:visible", PLAN_A[0], true)
	cle(anim, "Plans/B:visible", PLAN_A[0], false)
	cle(anim, "Plans/A/Geste:frame", PLAN_A[0], 0)
	images(anim, "Plans/A/Geste", PLAN_A[1], 1, 5)
	cle(anim, "Plans/A:visible", PLAN_B[0], false)
	cle(anim, "Plans/B:visible", PLAN_B[0], true)
	cle(anim, "Plans/B/Geste:frame", PLAN_B[0], 0)
	images(anim, "Plans/B/Geste", PLAN_B[1], 1, 3)
	cle(anim, "Plans:visible", anim.length, false)
	return anim


func apres() -> void:
	if couche != null:
		couche.visible = false
