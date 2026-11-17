extends CinematiquePlans
## e6_fuite_noir (lot 2, planche validée par le GD le 17/11) : 8 s, option « Fuir » de e6_eloi.
## L'écran de l'étape 6 inverse l'image. Planches de tools/gen_cin_e6_fuite.py.
## P1, 0 à 3 s : la course dans le noir, sa silhouette à peine visible (3 images) qui traverse.
## P2, 3 à 5 s : la chute ; de tout près, les mains qui arrivent puis à plat sur la pierre
##    (2 images), le choc secoue le cadre.
## P3, 5 à 8 s : longtemps après, le noir ; la petite lumière verte revient, au loin, immobile.
## Effets atténués : plans fixes, sans secousse ni vacillement. Le pli et son ruban restent hors
## champ (silhouette de profil, puis les mains seules).

const CIN := "res://assets/graphics/cin/%s.png"
const SON := "sfx_fuite_noir"
const DUREE := 8.0
const P2 := 3.0
const P3 := 5.0
## P1 : la silhouette (360 × 600), ses pieds sur le sol (y 900), de x 100 à 1700.
const COURSE_Y := 360.0
const COURSE_X := [100.0, 1700.0]
const IMAGES_COURSE := [0, 1, 2, 1]
const IMAGE_COURSE := 0.1
## P2 : les mains (ZONE_MAINS), qui arrivent puis tombent à plat ; la secousse du choc.
const ZONE_MAINS := Vector2(360, 280)
const MAINS := [[3.0, 0], [3.25, 1]]
const SECOUSSE := [[3.25, Vector2(0, 10)], [3.32, Vector2(-6, -4)], [3.4, Vector2(4, 2)], [3.48, Vector2.ZERO]]
## P3 : la lueur (ZONE_LUEUR) : rien, puis elle vacille et reste.
const ZONE_LUEUR := Vector2(1240, 560)
const LUEUR := [[5.0, false], [5.8, true], [5.95, false], [6.1, true]]

var couche: CanvasLayer


func construire() -> Animation:
	var tex := {}
	for nom in ["noir", "course", "dalles", "mains", "loin", "lueur"]:
		tex[nom] = planche(CIN % ("cin_e6-fuite-" + nom))
		if tex[nom] == null:
			return null
	var attenues := bool(Reglages.valeur(&"effets_attenues"))
	couche = couche_plein_ecran()

	var nef := Node2D.new()
	nef.name = "Nef"
	nef.add_child(sprite("Fond", tex["noir"], Vector2.ZERO))
	nef.add_child(sprite("Course", tex["course"], Vector2(COURSE_X[0], COURSE_Y), 3))
	couche.add_child(nef)
	var chute := Node2D.new()
	chute.name = "Chute"
	chute.add_child(sprite("Fond", tex["dalles"], Vector2.ZERO))
	chute.add_child(sprite("Mains", tex["mains"], ZONE_MAINS, 2))
	couche.add_child(chute)
	var loin := Node2D.new()
	loin.name = "Loin"
	loin.add_child(sprite("Fond", tex["loin"], Vector2.ZERO))
	loin.add_child(sprite("Lueur", tex["lueur"], ZONE_LUEUR))
	couche.add_child(loin)

	var anim := Animation.new()
	anim.length = DUREE
	cle(anim, "Plans:visible", 0.0, true)
	if not AudioDirector.variantes_de(SON).is_empty():
		son(anim, 0.0, SON)
	cle(anim, "Plans/Nef:visible", 0.0, true)
	cle(anim, "Plans/Nef:visible", P2, false)
	cle(anim, "Plans/Chute:visible", 0.0, false)
	cle(anim, "Plans/Chute:visible", P2, true)
	cle(anim, "Plans/Chute:visible", P3, false)
	cle(anim, "Plans/Loin:visible", 0.0, false)
	cle(anim, "Plans/Loin:visible", P3, true)

	# P1 : la course
	var n := roundi(P2 / Cinematique.PAS)
	for i in n + 1:
		var x := (COURSE_X[0] + COURSE_X[1]) / 2.0 if attenues else lerpf(COURSE_X[0], COURSE_X[1], float(i) / n)
		cle(anim, "Plans/Nef/Course:position", i * Cinematique.PAS, Vector2(roundf(x), COURSE_Y))
		if attenues:
			break
	var t := 0.0
	var k := 0
	while t < P2 - 0.001:
		cle(anim, "Plans/Nef/Course:frame", snappedf(t, Cinematique.PAS), IMAGES_COURSE[k % IMAGES_COURSE.size()])
		t += IMAGE_COURSE
		k += 1

	# P2 : les mains sur la pierre
	for c: Array in MAINS:
		cle(anim, "Plans/Chute/Mains:frame", c[0], c[1])
	cle(anim, "Plans/Chute:position", P2, Vector2.ZERO)
	if not attenues:
		for c: Array in SECOUSSE:
			cle(anim, "Plans/Chute:position", c[0], c[1])

	# P3 : la lumière verte revient
	if attenues:
		cle(anim, "Plans/Loin/Lueur:visible", 0.0, false)
		cle(anim, "Plans/Loin/Lueur:visible", LUEUR[1][0], true)
	else:
		cle(anim, "Plans/Loin/Lueur:visible", 0.0, false)
		for c: Array in LUEUR:
			cle(anim, "Plans/Loin/Lueur:visible", c[0], c[1])
	cle(anim, "Plans:visible", DUREE, false)
	return anim


func apres() -> void:
	if couche != null:
		couche.visible = false
