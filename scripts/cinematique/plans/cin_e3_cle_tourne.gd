extends CinematiquePlans
## e3_cle_tourne (lot 2, planche validée par le GD le 17/11) : 6 s, jouée par le passage « Accepter
## le lit » de la maison d'Ilde, avant d'arriver dans la chambre (la nuit tombe à la fin du plan).
## Planches de tools/gen_cin_e3_cle.py.
## P1, 0 à 2 s : Ilde, de dos, rabat elle-même les volets (3 images) ; la lumière s'en va.
## P2, 2 à 4 s : vue du lit, la porte se ferme sur nous ; Ilde en ombre, son cierge (2 images).
## P3, 4 à 6 s : de près, vu de dedans, la clé entre dans la serrure, tourne une fois, deux fois
##    (4 images).

const CIN := "res://assets/graphics/cin/%s.png"
const SON := "sfx_cle_tourne"
const DUREE := 6.0
const P2 := 2.0
const P3 := 4.0
## Les vignettes animées (ZONE_* du générateur) et leurs images.
const ZONE_VOLETS := Vector2(420, 100)
const VOLETS := [[0.0, 0], [0.7, 1], [1.3, 2]]
## La chambre s'assombrit quand le second volet est clos.
const SOMBRE := Color(0.72, 0.72, 0.74)
const ZONE_BATTANT := Vector2(560, 100)
const BATTANT := [[2.0, 0], [3.1, 1]]
const ZONE_PENE := Vector2(700, 300)
const PENE := [[4.0, 0], [4.4, 1], [4.9, 2], [5.5, 3]]

var couche: CanvasLayer


func construire() -> Animation:
	var tex := {}
	for nom in ["fenetre", "volets", "porte", "battant", "serrure", "pene"]:
		tex[nom] = planche(CIN % ("cin_e3-cle-" + nom))
		if tex[nom] == null:
			return null
	couche = couche_plein_ecran()
	var anim := Animation.new()
	anim.length = DUREE
	cle(anim, "Plans:visible", 0.0, true)
	if not AudioDirector.variantes_de(SON).is_empty():
		son(anim, 0.0, SON)

	var plans := [
		["Fenetre", "fenetre", "Volets", "volets", ZONE_VOLETS, 3, VOLETS, 0.0, P2],
		["Porte", "porte", "Battant", "battant", ZONE_BATTANT, 2, BATTANT, P2, P3],
		["Serrure", "serrure", "Pene", "pene", ZONE_PENE, 4, PENE, P3, DUREE],
	]
	for p: Array in plans:
		var noeud := Node2D.new()
		noeud.name = p[0]
		noeud.add_child(sprite("Fond", tex[p[1]], Vector2.ZERO))
		noeud.add_child(sprite(p[2], tex[p[3]], p[4], p[5]))
		couche.add_child(noeud)
		var chemin := "Plans/" + String(p[0])
		var debut: float = p[7]
		var fin: float = p[8]
		cle(anim, chemin + ":visible", 0.0, debut == 0.0)
		if debut > 0.0:
			cle(anim, chemin + ":visible", debut, true)
		if fin < DUREE:
			cle(anim, chemin + ":visible", fin, false)
		for c: Array in p[6]:
			cle(anim, chemin + "/" + String(p[2]) + ":frame", c[0], c[1])
	cle(anim, "Plans/Fenetre:modulate", 0.0, Color.WHITE)
	cle(anim, "Plans/Fenetre:modulate", VOLETS[2][0], SOMBRE)
	cle(anim, "Plans:visible", DUREE, false)
	return anim


func apres() -> void:
	if couche != null:
		couche.visible = false
