extends CinematiquePlans
## e5_clairiere_ciel (lot 2, planche validée par le GD le 17/11) : 10 s, au début de
## e5_clairiere. L'écran de l'étape 5 inverse l'image. Planches de tools/gen_cin_e5_clairiere.py.
## P1, 0 à 3 s : les dernières croix ; Tobie en sort (travelling latéral, décor du cimetière et
##    de la clairière réemployé et rapproché).
## P2, 3 à 7 s : tilt vers le haut, des deux dernières croix au ciel ouvert, immense ; de longs
##    nuages dérivent.
## P3, 7 à 10 s : plongée, en contrebas, le toit d'église à moitié enterré ; l'herbe de la crête
##    sous le vent (2 images) ; lente avancée.
## Effets atténués : plans fixes. Tobie porte son ruban (CalqueRuban).

const CIN := "res://assets/graphics/cin/%s.png"
const ENV := "res://assets/graphics/env/e5/env_e5_plan3_%s.png"
const CHR := "res://assets/graphics/chr/%s.png"
const SON := "sfx_clairiere_ciel"
const DUREE := 10.0
const P2 := 3.0
const P3 := 7.0
const PIEDS := Vector2(100, 316)
## La fin du cimetière (832 px) puis la clairière ; rapprochées ×1,5, le sol (y 900) en y 980.
const ECHELLE := 1.5
const BANDE_Y := -370.0
const TUILES := [["cimetiere_02", 0.0], ["clairiere_01", 832.0]]
const TOBIE := Vector2(860, 980)
const IMAGE_MARCHE := 0.1
## Tobie passe des dernières croix (x 700 de la bande) à l'herbe nue (x 1180) : 240 px/s.
const P1_X := [-190.0, -910.0]
## P2 : la planche du ciel (2160 px de haut) monte d'un écran ; les nuages (ZONE_NUAGES).
const CIEL_Y := [-1080.0, 0.0]
const ZONE_NUAGES := Vector2(0, 80)
const DERIVE := 60.0
## P3 : l'herbe (ZONE_HERBE), couchée et relevée par le vent, à un rythme irrégulier.
const ZONE_HERBE := Vector2(0, 900)
const HERBE := [[7.0, 0], [7.5, 1], [8.1, 0], [8.4, 1], [9.0, 0], [9.6, 1]]
const FOYER_TOIT := Vector2(960, 560)
const ZOOM_TOIT := 1.1

var couche: CanvasLayer


func construire() -> Animation:
	var tex := {}
	for nom in ["cimetiere_02", "clairiere_01"]:
		tex[nom] = planche(ENV % nom)
	for nom in ["ciel", "nuages", "eglise", "herbe"]:
		tex[nom] = planche(CIN % ("cin_e5-clairiere-" + nom))
	tex["marche"] = planche(CHR % "chr_tobie_marche_01")
	for t: Variant in tex.values():
		if t == null:
			return null
	var attenues := bool(Reglages.valeur(&"effets_attenues"))
	couche = couche_plein_ecran()

	var sentier := Node2D.new()
	sentier.name = "Sentier"
	var bande := Node2D.new()
	bande.name = "Bande"
	bande.scale = Vector2.ONE * ECHELLE
	for t: Array in TUILES:
		bande.add_child(sprite(String(t[0]), tex[t[0]], Vector2(t[1], 0)))
	sentier.add_child(bande)
	var tobie := sprite("Marche", tex["marche"], TOBIE, 8)
	tobie.offset = -PIEDS
	tobie.scale = Vector2.ONE * ECHELLE
	CalqueRuban.poser(tobie)
	sentier.add_child(tobie)
	couche.add_child(sentier)

	var ciel := Node2D.new()
	ciel.name = "Ciel"
	ciel.add_child(sprite("Fond", tex["ciel"], Vector2.ZERO))
	ciel.add_child(sprite("Nuages", tex["nuages"], ZONE_NUAGES))
	couche.add_child(ciel)

	var eglise := Node2D.new()
	eglise.name = "Eglise"
	eglise.add_child(sprite("Fond", tex["eglise"], Vector2.ZERO))
	eglise.add_child(sprite("Herbe", tex["herbe"], ZONE_HERBE, 2))
	couche.add_child(eglise)

	var anim := Animation.new()
	anim.length = DUREE
	cle(anim, "Plans:visible", 0.0, true)
	if not AudioDirector.variantes_de(SON).is_empty():
		son(anim, 0.0, SON)

	# P1 : il sort des dernières croix
	cle(anim, "Plans/Sentier:visible", 0.0, true)
	cle(anim, "Plans/Ciel:visible", 0.0, false)
	cle(anim, "Plans/Eglise:visible", 0.0, false)
	var n := roundi(P2 / Cinematique.PAS)
	for i in n + 1:
		var x := lerpf(P1_X[0], P1_X[1], float(i) / n)
		if attenues:
			x = (P1_X[0] + P1_X[1]) / 2.0
		cle(anim, "Plans/Sentier/Bande:position", i * Cinematique.PAS, Vector2(roundf(x), BANDE_Y))
		if attenues:
			break
	var t := 0.0
	var k := 0
	while t < P2 - 0.001:
		cle(anim, "Plans/Sentier/Marche:frame", snappedf(t, Cinematique.PAS), k % 8)
		t += IMAGE_MARCHE
		k += 1
	cle(anim, "Plans/Sentier:visible", P2, false)

	# P2 : le ciel s'ouvre
	cle(anim, "Plans/Ciel:visible", P2, true)
	cle(anim, "Plans/Ciel:visible", P3, false)
	n = roundi((P3 - P2) / Cinematique.PAS)
	for i in n + 1:
		var u := float(i) / n
		var e := u * u * (3.0 - 2.0 * u)
		var y := lerpf(CIEL_Y[0], CIEL_Y[1], e)
		var d := DERIVE * u
		if attenues:
			y = (CIEL_Y[0] + CIEL_Y[1]) / 2.0
			d = 0.0
		cle(anim, "Plans/Ciel:position", P2 + i * Cinematique.PAS, Vector2(0, roundf(y)))
		cle(anim, "Plans/Ciel/Nuages:position", P2 + i * Cinematique.PAS, ZONE_NUAGES + Vector2(roundf(d), 0))
		if attenues:
			break

	# P3 : le toit enterré
	cle(anim, "Plans/Eglise:visible", P3, true)
	for c: Array in HERBE:
		cle(anim, "Plans/Eglise/Herbe:frame", c[0], c[1])
	n = roundi((DUREE - P3) / Cinematique.PAS)
	for i in n + 1:
		var u := float(i) / n
		var z := 1.0 if attenues else lerpf(1.0, ZOOM_TOIT, u * u * (3.0 - 2.0 * u))
		cle(anim, "Plans/Eglise:scale", P3 + i * Cinematique.PAS, Vector2.ONE * z)
		cle(anim, "Plans/Eglise:position", P3 + i * Cinematique.PAS, (FOYER_TOIT - FOYER_TOIT * z).round())
		if attenues:
			break
	cle(anim, "Plans:visible", DUREE, false)
	return anim


func apres() -> void:
	if couche != null:
		couche.visible = false
