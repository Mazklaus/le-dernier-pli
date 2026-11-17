extends CinematiquePlans
## e4_descente_crypte (lot 1, planche validée par le GD le 17/11) : 10 s, au début de e4_crypte,
## avant le choix de la lanterne. Planches de tools/gen_cin_e4_crypte.py.
## P1, 0 à 4 s : plongée dans la vis ; elle tourne et s'agrandit d'un palier (elle « descend »),
##    Tobie, vu d'en haut, suit les marches (plan fixe en effets atténués).
## P2, 4 à 8 s : dans la cage, de côté, Tobie descend ; la lumière de la porte d'en haut
##    rétrécit (4 images) pendant que le noir monte.
## P3, 8 à 10 s : noir complet. On ne voit pas encore les saints.

const CIN := "res://assets/graphics/cin/%s.png"
const MARCHE := "res://assets/graphics/chr/chr_tobie_marche_01.png"
const SON := "sfx_crypte_descendre"
const DUREE := 10.0
const P2 := 4.0
const P3 := 8.0
const CENTRE := Vector2(960, 540)
## La vis : dessinée sur 2240 px, rendue en 1400 (affichée à 1,6). Un palier plus bas est vu
## RAPPORT fois plus petit et tourné de DECALAGE : en 4 s on gagne un palier, sans couture.
const ECHELLE_VIS := 1.6
const RAPPORT := 0.6
const DECALAGE := 67.5
const ZOOM_ATTENUE := 1.25
## Tobie vu d'en haut, sur les marches du palier 2 (rayons 343 à 492 dans le repère de la vis),
## à gauche du cadre : même agrandi et tourné, il reste dans l'image.
const RAYON_DEBUT := 450.0
const RAYON_FIN := 400.0
const ANGLE_DEBUT := 150.0
const ANGLE_FIN := 210.0
const ECHELLE_DESSUS := 1.1
const FOULEE_DESSUS := 0.25
## P2 : les marches de la cage (nez de la marche m en (200 + 118 m, 420 + 54 m)), pieds au milieu.
const PIEDS := Vector2(100, 316)
const PIED_DEBUT := Vector2(377, 474)
const PAS_MARCHE := Vector2(118, 54)
const MARCHES := 9.0
const DESCENTE := [4.2, 7.6]
const LUMIERE := [[4.0, 0], [5.2, 1], [6.3, 2], [7.3, 3]]
const LUMIERE_ETEINTE := 7.8
const NOIR_DEBUT := 0.25
const NOIR_FIN := 0.92

var couche: CanvasLayer


func construire() -> Animation:
	var tex := {}
	for nom in ["vis", "dessus", "cage", "lumiere"]:
		tex[nom] = planche(CIN % ("cin_e4-crypte-" + nom))
	tex["marche"] = planche(MARCHE)
	for t: Variant in tex.values():
		if t == null:
			return null
	var attenues := bool(Reglages.valeur(&"effets_attenues"))
	couche = couche_plein_ecran()

	# P1 : la vis
	var pivot := Node2D.new()
	pivot.name = "Vis"
	pivot.position = CENTRE
	var vis := sprite("Fond", tex["vis"], Vector2.ZERO)
	vis.centered = true
	vis.scale = Vector2.ONE * ECHELLE_VIS
	pivot.add_child(vis)
	var dessus := sprite("Tobie", tex["dessus"], Vector2.ZERO, 2)
	dessus.centered = true
	dessus.scale = Vector2.ONE * ECHELLE_DESSUS
	pivot.add_child(dessus)
	couche.add_child(pivot)

	# P2 : la cage
	var cage := Node2D.new()
	cage.name = "Cage"
	cage.add_child(sprite("Fond", tex["cage"], Vector2.ZERO))
	var tobie := sprite("Tobie", tex["marche"], Vector2.ZERO, 8)
	tobie.offset = -PIEDS
	cage.add_child(tobie)
	CalqueRuban.poser(tobie)
	var nuit := ColorRect.new()
	nuit.name = "Nuit"
	nuit.size = TAILLE_PLEIN_ECRAN
	nuit.color = Color.BLACK
	nuit.mouse_filter = Control.MOUSE_FILTER_IGNORE
	cage.add_child(nuit)
	cage.add_child(sprite("Lumiere", tex["lumiere"], Vector2.ZERO, 2, 2))
	couche.add_child(cage)

	# P3 : le noir
	var noir := ColorRect.new()
	noir.name = "Noir"
	noir.size = TAILLE_PLEIN_ECRAN
	noir.color = Color.BLACK
	noir.mouse_filter = Control.MOUSE_FILTER_IGNORE
	couche.add_child(noir)

	var anim := Animation.new()
	anim.length = DUREE
	cle(anim, "Plans:visible", 0.0, true)
	if not AudioDirector.variantes_de(SON).is_empty():
		son(anim, 0.0, SON)
	cle(anim, "Plans/Vis:visible", 0.0, true)
	cle(anim, "Plans/Cage:visible", 0.0, false)
	cle(anim, "Plans/Noir:visible", 0.0, false)

	# P1 : la vis tourne et descend d'un palier ; Tobie suit les marches
	var n := roundi(P2 / Cinematique.PAS)
	for k in n + 1:
		var t := k * Cinematique.PAS
		var u := float(k) / n
		if attenues:
			if k == 0:
				cle(anim, "Plans/Vis:scale", t, Vector2.ONE * ZOOM_ATTENUE)
				cle(anim, "Plans/Vis:rotation", t, 0.0)
		else:
			cle(anim, "Plans/Vis:scale", t, Vector2.ONE * lerpf(1.0, 1.0 / RAPPORT, u))
			cle(anim, "Plans/Vis:rotation", t, deg_to_rad(-DECALAGE * u))
		var a := deg_to_rad(lerpf(ANGLE_DEBUT, ANGLE_FIN, u))
		var r := lerpf(RAYON_DEBUT, RAYON_FIN, u)
		cle(anim, "Plans/Vis/Tobie:position", t, (Vector2(cos(a), sin(a)) * r).round())
		cle(anim, "Plans/Vis/Tobie:rotation", t, a + PI)
		cle(anim, "Plans/Vis/Tobie:modulate", t, Color(1, 1, 1).darkened(0.35 * u))
	boucle(anim, "Plans/Vis/Tobie", 0.0, P2, [0, 1], FOULEE_DESSUS)

	# P2 : la descente, la lumière qui rétrécit, le noir qui monte
	cle(anim, "Plans/Vis:visible", P2, false)
	cle(anim, "Plans/Cage:visible", P2, true)
	var d0: float = DESCENTE[0]
	var d1: float = DESCENTE[1]
	n = roundi((d1 - d0) / Cinematique.PAS)
	cle(anim, "Plans/Cage/Tobie:position", P2, PIED_DEBUT)
	for k in n + 1:
		var u := float(k) / n
		var bond := -6.0 * absf(sin(u * MARCHES * PI))
		cle(anim, "Plans/Cage/Tobie:position", d0 + k * Cinematique.PAS, (PIED_DEBUT + PAS_MARCHE * MARCHES * u + Vector2(0, bond)).round())
	cle(anim, "Plans/Cage/Tobie:frame", P2, 0)
	boucle(anim, "Plans/Cage/Tobie", d0, d1, [0, 1, 2, 3, 4, 5, 6, 7], Cinematique.PAS)
	cle(anim, "Plans/Cage/Tobie:frame", d1, 0)
	n = roundi((P3 - P2) / Cinematique.PAS)
	for k in n + 1:
		var u := float(k) / n
		cle(anim, "Plans/Cage/Nuit:color", P2 + k * Cinematique.PAS, Color(0, 0, 0, lerpf(NOIR_DEBUT, NOIR_FIN, u * u)))
	cle(anim, "Plans/Cage/Lumiere:visible", 0.0, true)
	for c: Array in LUMIERE:
		cle(anim, "Plans/Cage/Lumiere:frame", c[0], c[1])
	cle(anim, "Plans/Cage/Lumiere:visible", LUMIERE_ETEINTE, false)

	# P3 : noir complet
	cle(anim, "Plans/Cage:visible", P3, false)
	cle(anim, "Plans/Noir:visible", P3, true)
	cle(anim, "Plans:visible", DUREE, false)
	return anim


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
