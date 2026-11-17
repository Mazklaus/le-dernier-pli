extends AnimationEpilogue
## Épilogue « Le Quatorzième » (lettre d, ordre). Planche de la DA validée par le GD le 17/11, avec
## ses corrections (rien ne se compte) : 32 s, quatre plans, une ligne par plan. Images faites pour
## la ciné (tools/gen_cin_epilogue_quatorzieme.py) ; le dernier plan réemploie exprès la tranchée de
## l'étape 1 et la marche de Tobie : un autre garçon, le même pas, le jeu recommence.

const CIN := "res://assets/graphics/cin/%s.png"
const TRANCHEE := "res://assets/graphics/env/e1/env_e1_plan3_surface_01.png"
const MARCHE := "res://assets/graphics/chr/chr_tobie_marche_01.png"
const DUREE := 32.0
const LIGNES: Array[float] = [0.5, 8.5, 14.5, 24.5]
## P1 : le rayon ; la main pose le pli (ZONE_RANGER, 3 images) sur le tas le plus proche.
const ZONE_RANGER := Vector2(1180, 0)
const RANGER := [[0.0, -1], [2.0, 0], [3.4, 1], [4.6, 2]]
const TAS := Vector2(1400, 250)
## P2 : la plaque vierge, la poussière qui tombe (cin_epi-c-poussiere, 900 × 900, 3 images).
const POUSSIERE := Vector2(510, -60)
## P3 : la remise ; les mains du garçon (ZONE_MAINS, 3 images).
const ZONE_MAINS := Vector2(0, 380)
const MAINS := [[14.0, -1], [16.0, 0], [17.5, 1], [19.0, 2]]
const OBJETS := Vector2(1000, 520)
## P4 : la tranchée de l'étape 1 à l'échelle 1,4 ; il marche vers la droite et s'éloigne.
const ECHELLE_TRANCHEE := 1.4
const SOL := 616.0
const PIEDS := Vector2(100, 316)
const DEPART := 420.0
const ARRIVEE := 1640.0
const MARCHE_DEBUT := 24.5
const MARCHE_FIN := 30.5
const IMAGE_MARCHE := 0.1
const FONDU := 30.0


func construire() -> Animation:
	var tex := {}
	for nom in ["cin_epi-d-rayon", "cin_epi-d-ranger", "cin_epi-d-plaque", "cin_epi-c-poussiere", "cin_epi-d-remise", "cin_epi-d-mains"]:
		tex[nom] = planche(CIN % nom)
	tex["tranchee"] = planche(TRANCHEE)
	tex["marche"] = planche(MARCHE)
	for t: Variant in tex.values():
		if t == null:
			return null
	temps_lignes = LIGNES
	var anim := Animation.new()
	anim.length = DUREE

	# P1, 0 à 8 s : « Le pli fut rangé avec les autres. » Le rayon profond, la main qui pose le
	# pli de Tobie sur le dessus, puis la poussée lente vers lui.
	var p1 := plan(anim, "P1", 0.0, 8.0)
	var rayon := Node2D.new()
	rayon.name = "Rayon"
	p1.add_child(rayon)
	rayon.add_child(sprite("Fond", tex["cin_epi-d-rayon"], Vector2.ZERO))
	rayon.add_child(sprite("Ranger", tex["cin_epi-d-ranger"], ZONE_RANGER, 3, 1))
	images_cachees(anim, "Cadre/P1/Rayon/Ranger", RANGER)
	pousser(anim, "Cadre/P1/Rayon", 0.0, 8.0, TAS, 1.0, 1.1)

	# P2, 8 à 14 s : « Personne ne grava rien. » La plaque vierge, la poussière.
	var p2 := plan(anim, "P2", 8.0, 14.0)
	p2.add_child(sprite("Fond", tex["cin_epi-d-plaque"], Vector2.ZERO))
	p2.add_child(sprite("Poussiere", tex["cin_epi-c-poussiere"], POUSSIERE, 3, 1))
	boucle(anim, "Cadre/P2/Poussiere", 8.0, 14.0, [0, 1, 2], 0.3)

	# P3, 14 à 24 s : « un garçon reçut une sacoche, une cloche sans battant et un ordre. »
	var p3 := plan(anim, "P3", 14.0, 24.0)
	var remise := Node2D.new()
	remise.name = "Remise"
	p3.add_child(remise)
	remise.add_child(sprite("Fond", tex["cin_epi-d-remise"], Vector2.ZERO))
	remise.add_child(sprite("Mains", tex["cin_epi-d-mains"], ZONE_MAINS, 3, 1))
	images_cachees(anim, "Cadre/P3/Remise/Mains", MAINS)
	pousser(anim, "Cadre/P3/Remise", 14.0, 24.0, OBJETS, 1.0, 1.08)

	# P4, 24 à 32 s : « Il avait le même pas. » La tranchée de l'étape 1, il s'éloigne, puis le
	# papier revient.
	var p4 := plan(anim, "P4", 24.0, DUREE)
	var decor := sprite("Tranchee", tex["tranchee"], Vector2.ZERO)
	decor.scale = Vector2.ONE * ECHELLE_TRANCHEE
	p4.add_child(decor)
	var garcon := Sprite2D.new()
	garcon.name = "Garcon"
	garcon.texture = tex["marche"]
	garcon.hframes = 8
	garcon.centered = false
	garcon.offset = -PIEDS
	garcon.scale = Vector2.ONE * ECHELLE_TRANCHEE
	garcon.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	p4.add_child(garcon)
	var n := roundi((MARCHE_FIN - MARCHE_DEBUT) / IMAGE_MARCHE)
	cle(anim, "Cadre/P4/Garcon:position", 24.0, Vector2(DEPART, SOL))
	for k in n + 1:
		var t := MARCHE_DEBUT + k * IMAGE_MARCHE
		cle(anim, "Cadre/P4/Garcon:frame", snappedf(t, PAS), k % 8)
		cle(anim, "Cadre/P4/Garcon:position", snappedf(t, PAS), Vector2(roundf(lerpf(DEPART, ARRIVEE, float(k) / n)), SOL))
	var papier := ColorRect.new()
	papier.name = "Papier"
	papier.color = StylePapier.PAPIER
	papier.size = Vector2(1920, 1080)
	papier.mouse_filter = Control.MOUSE_FILTER_IGNORE
	p4.add_child(papier)
	cle(anim, "Cadre/P4/Papier:modulate", 24.0, Color(1, 1, 1, 0))
	for k in 21:
		cle(anim, "Cadre/P4/Papier:modulate", FONDU + k * PAS, Color(1, 1, 1, clampf((k - 1) / 18.0, 0.0, 1.0)))
	return anim


## Des images tenues à des instants donnés ([temps, image]) ; l'image -1 cache le sprite.
static func images_cachees(anim: Animation, chemin: String, cles: Array) -> void:
	for c: Array in cles:
		cle(anim, chemin + ":visible", c[0], c[1] >= 0)
		if c[1] >= 0:
			cle(anim, chemin + ":frame", c[0], c[1])
