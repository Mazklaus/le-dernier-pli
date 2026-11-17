extends CinematiquePlans
## e7_mere_cloche (lot 1, planche validée par le GD le 17/11) : 10 s, au début de
## e7_mere_cloche. Planches de tools/gen_cin_e7_mere.py.
## P1, 0 à 3 s : la salle ronde sous la grande cloche (décor réemployé), Tobie entre ; travelling
##    avant vers elle (plan fixe en effets atténués).
## P2, 3 à 7 s : de près, la Mère-Cloche lève la tête vers lui, les yeux clos (3 images).
## P3, 7 à 10 s : contrechamp, Tobie, petit, sous la bouche noire de la cloche. Rien dedans.
## Tobie porte son ruban (calque _red de ses planches, comme en jeu).

const CIN := "res://assets/graphics/cin/%s.png"
const CHR := "res://assets/graphics/chr/%s.png"
const DECOR := "res://assets/graphics/env/e7/env_e7_plan3_mere-cloche_01.png"
const SON := "sfx_mere_cloche"
const DUREE := 10.0
const P2 := 3.0
const P3 := 7.0
const PIEDS := Vector2(100, 316)
## P1 : la salle ; elle assise au centre, lui qui entre par la gauche.
const MERE := Vector2(960, 900)
const ENTREE := Vector2(240, 900)
const ARRET := Vector2(660, 900)
const FIN_MARCHE := 2.4
const FOYER_SALLE := Vector2(960, 760)
const ZOOM_SALLE := 1.2
const ZOOM_ATTENUE := 1.1
## P2 : la tête (ZONE_TETE du générateur), le cadre rapproché autour du visage.
const ZONE_TETE := Vector2(700, 140)
const VISAGE := Vector2(960, 400)
const ZOOM_GROS := [1.3, 1.38]
## Le visage cadré à CADRE_VISAGE (pas plus bas : le haut de la planche ne doit pas se découvrir).
const CADRE_VISAGE := Vector2(960, 500)
const TETE := [[3.0, 0], [4.4, 1], [5.2, 2]]
## P3 : Tobie sous la bouche.
const PIEDS_TOBIE := Vector2(960, 960)
const RESPIRATION := 0.5

var couche: CanvasLayer


func construire() -> Animation:
	var tex := {}
	for nom in ["gros", "tete", "bouche"]:
		tex[nom] = planche(CIN % ("cin_e7-mere-" + nom))
	for nom in ["chr_mere-cloche_repos_01", "chr_tobie_marche_01", "chr_tobie_marche_01_red",
			"chr_tobie_repos_01", "chr_tobie_repos_01_red"]:
		tex[nom] = planche(CHR % nom)
	tex["decor"] = planche(DECOR)
	for t: Variant in tex.values():
		if t == null:
			return null
	var attenues := bool(Reglages.valeur(&"effets_attenues"))
	couche = couche_plein_ecran()
	var anim := Animation.new()
	anim.length = DUREE
	cle(anim, "Plans:visible", 0.0, true)
	if not AudioDirector.variantes_de(SON).is_empty():
		son(anim, 0.0, SON)

	# P1 : la salle ronde, il entre
	var salle := Node2D.new()
	salle.name = "Salle"
	salle.add_child(sprite("Decor", tex["decor"], Vector2.ZERO))
	var mere := sprite("Mere", tex["chr_mere-cloche_repos_01"], MERE, 4)
	mere.offset = -PIEDS
	salle.add_child(mere)
	salle.add_child(_tobie("Tobie", tex["chr_tobie_marche_01"], tex["chr_tobie_marche_01_red"], 8))
	couche.add_child(salle)
	cle(anim, "Plans/Salle:visible", 0.0, true)
	var n := roundi(P2 / Cinematique.PAS)
	for k in n + 1:
		var t := k * Cinematique.PAS
		var u := float(k) / n
		var z := ZOOM_ATTENUE if attenues else lerpf(1.0, ZOOM_SALLE, u * u * (3.0 - 2.0 * u))
		if k == 0 or not attenues:
			cle(anim, "Plans/Salle:scale", t, Vector2.ONE * z)
			cle(anim, "Plans/Salle:position", t, (FOYER_SALLE - FOYER_SALLE * z).round())
		var m := clampf(t / FIN_MARCHE, 0.0, 1.0)
		cle(anim, "Plans/Salle/Tobie:position", t, ENTREE.lerp(ARRET, m).round())
		_image_tobie(anim, "Plans/Salle/Tobie", t, k % 8 if t < FIN_MARCHE else 0)
	boucle(anim, "Plans/Salle/Mere", 0.0, P2, [0, 1, 2, 3, 2, 1], RESPIRATION)
	cle(anim, "Plans/Salle:visible", P2, false)

	# P2 : elle lève la tête, les yeux clos
	var gros := Node2D.new()
	gros.name = "Gros"
	gros.add_child(sprite("Fond", tex["gros"], Vector2.ZERO))
	gros.add_child(sprite("Tete", tex["tete"], ZONE_TETE, 3))
	couche.add_child(gros)
	cle(anim, "Plans/Gros:visible", 0.0, false)
	cle(anim, "Plans/Gros:visible", P2, true)
	for c: Array in TETE:
		cle(anim, "Plans/Gros/Tete:frame", c[0], c[1])
	var z0: float = ZOOM_GROS[0]
	var z1: float = ZOOM_GROS[1]
	n = roundi((P3 - P2) / Cinematique.PAS)
	for k in n + 1:
		var z := z0 if attenues else lerpf(z0, z1, float(k) / n)
		if k == 0 or not attenues:
			cle(anim, "Plans/Gros:scale", P2 + k * Cinematique.PAS, Vector2.ONE * z)
			cle(anim, "Plans/Gros:position", P2 + k * Cinematique.PAS, (CADRE_VISAGE - VISAGE * z).round())
	cle(anim, "Plans/Gros:visible", P3, false)

	# P3 : contrechamp, Tobie sous la bouche noire
	var contre := Node2D.new()
	contre.name = "Bouche"
	contre.add_child(sprite("Fond", tex["bouche"], Vector2.ZERO))
	var tobie := _tobie("Tobie", tex["chr_tobie_repos_01"], tex["chr_tobie_repos_01_red"], 4)
	tobie.position = PIEDS_TOBIE
	contre.add_child(tobie)
	couche.add_child(contre)
	cle(anim, "Plans/Bouche:visible", 0.0, false)
	cle(anim, "Plans/Bouche:visible", P3, true)
	var t := P3
	var suite := [0, 1, 2, 3, 2, 1]
	var i := 0
	while t < DUREE - 0.001:
		_image_tobie(anim, "Plans/Bouche/Tobie", t, suite[i % suite.size()])
		t += RESPIRATION
		i += 1
	cle(anim, "Plans:visible", DUREE, false)
	return anim


## Tobie et son ruban : le calque _red posé sur la planche de base, mêmes images.
func _tobie(nom: String, base: Texture2D, ruban: Texture2D, images: int) -> Sprite2D:
	var s := sprite(nom, base, Vector2.ZERO, images)
	s.offset = -PIEDS
	var r := sprite("Ruban", ruban, Vector2.ZERO, images)
	r.offset = -PIEDS
	s.add_child(r)
	return s


static func _image_tobie(anim: Animation, chemin: String, t: float, image: int) -> void:
	cle(anim, chemin + ":frame", t, image)
	cle(anim, chemin + "/Ruban:frame", t, image)


func apres() -> void:
	if couche != null:
		couche.visible = false


static func boucle(anim: Animation, chemin: String, debut: float, fin: float, suite: Array, duree_image: float) -> void:
	var t := debut
	var k := 0
	while t < fin - 0.001:
		cle(anim, chemin + ":frame", snappedf(t, Cinematique.PAS), int(suite[k % suite.size()]))
		t += duree_image
		k += 1
