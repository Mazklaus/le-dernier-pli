extends CinematiquePlans
## e4_sortie_hopital (lot 2, planche validée par le GD le 17/11, retouche comprise) : 6 s, dans
## e4_benediction, sur « La porte se referme derrière moi ». Planches de tools/gen_cin_e4_sortie.py.
## P1, 0 à 2 s : la porte de la rue latérale, de près ; le battant se referme derrière Tobie
##    (3 images).
## P2, 2 à 4 s : dehors, la lumière est blanche : le mur pâlit, il est seul sur la marche ;
##    lente avancée vers lui (plan fixe en effets atténués).
## P3, 4 à 6 s : plan large, la route ; au loin la forêt de croix, plusieurs plans de profondeur
##    mangés par la brume ; Tobie, petit, face à elle.
## Tobie porte son ruban (CalqueRuban).

const CIN := "res://assets/graphics/cin/%s.png"
const CHR := "res://assets/graphics/chr/chr_tobie_repos_01.png"
const SON := "sfx_sortie_hopital"
const DUREE := 6.0
const P2 := 2.0
const P3 := 4.0
const PIEDS := Vector2(100, 316)
## P1 et P2 : le battant (ZONE_BATTANT du générateur), Tobie sur la marche, à droite de la porte.
const ZONE_BATTANT := Vector2(480, 260)
const BATTANT := [[0.0, 0], [0.6, 1], [1.2, 2]]
const TOBIE_PORTE := Vector2(1130, 970)
const ECHELLE_PORTE := 2.2
const RESPIRATION := 0.5
## P2 : la lumière blanche, un voile de papier sur le décor (pas sur Tobie).
const BLANC := Color(0.91, 0.898, 0.855, 0.6)
const FOYER_MARCHE := Vector2(1130, 700)
const ZOOM_MARCHE := 1.1
## P3 : Tobie, petit, au bas de la route.
const TOBIE_ROUTE := Vector2(500, 990)
const ECHELLE_ROUTE := 0.8
const FOYER_FORET := Vector2(1100, 600)
const ZOOM_FORET := 1.08

var couche: CanvasLayer


func construire() -> Animation:
	var tex := {}
	for nom in ["porte", "battant", "foret"]:
		tex[nom] = planche(CIN % ("cin_e4-sortie-" + nom))
	tex["tobie"] = planche(CHR)
	for t: Variant in tex.values():
		if t == null:
			return null
	var attenues := bool(Reglages.valeur(&"effets_attenues"))
	couche = couche_plein_ecran()

	var porte := Node2D.new()
	porte.name = "Porte"
	porte.add_child(sprite("Fond", tex["porte"], Vector2.ZERO))
	porte.add_child(sprite("Battant", tex["battant"], ZONE_BATTANT, 3))
	var voile := ColorRect.new()
	voile.name = "Blanc"
	voile.size = Vector2(1920, 1080)
	voile.color = BLANC
	voile.mouse_filter = Control.MOUSE_FILTER_IGNORE
	porte.add_child(voile)
	porte.add_child(_tobie("Tobie", tex["tobie"], TOBIE_PORTE, ECHELLE_PORTE))
	couche.add_child(porte)

	var route := Node2D.new()
	route.name = "Route"
	route.add_child(sprite("Fond", tex["foret"], Vector2.ZERO))
	route.add_child(_tobie("Tobie", tex["tobie"], TOBIE_ROUTE, ECHELLE_ROUTE))
	couche.add_child(route)

	var anim := Animation.new()
	anim.length = DUREE
	cle(anim, "Plans:visible", 0.0, true)
	if not AudioDirector.variantes_de(SON).is_empty():
		son(anim, 0.0, SON)

	# P1 : le battant se referme derrière lui
	cle(anim, "Plans/Porte:visible", 0.0, true)
	cle(anim, "Plans/Route:visible", 0.0, false)
	cle(anim, "Plans/Porte/Blanc:visible", 0.0, false)
	for c: Array in BATTANT:
		cle(anim, "Plans/Porte/Battant:frame", c[0], c[1])
	boucle(anim, "Plans/Porte/Tobie", 0.0, P3, [0, 1, 2, 3, 2, 1], RESPIRATION)

	# P2 : la lumière blanche, seul sur la marche
	cle(anim, "Plans/Porte/Blanc:visible", P2, true)
	cle(anim, "Plans/Porte:scale", 0.0, Vector2.ONE)
	cle(anim, "Plans/Porte:position", 0.0, Vector2.ZERO)
	avancee(anim, "Plans/Porte", P2, P3, FOYER_MARCHE, ZOOM_MARCHE, attenues)
	cle(anim, "Plans/Porte:visible", P3, false)

	# P3 : la forêt de croix au loin
	cle(anim, "Plans/Route:visible", P3, true)
	boucle(anim, "Plans/Route/Tobie", P3, DUREE, [0, 1, 2, 3, 2, 1], RESPIRATION)
	avancee(anim, "Plans/Route", P3, DUREE, FOYER_FORET, ZOOM_FORET, attenues)
	cle(anim, "Plans:visible", DUREE, false)
	return anim


func _tobie(nom: String, base: Texture2D, pieds: Vector2, echelle: float) -> Sprite2D:
	var s := sprite(nom, base, pieds, 4)
	s.offset = -PIEDS
	s.scale = Vector2.ONE * echelle
	CalqueRuban.poser(s)
	return s


## Lente avancée vers le foyer, de 1 à zoom ; un seul cadrage fixe en effets atténués.
static func avancee(anim: Animation, chemin: String, debut: float, fin: float, foyer: Vector2, zoom: float, attenues: bool) -> void:
	var n := roundi((fin - debut) / Cinematique.PAS)
	for k in n + 1:
		var u := float(k) / n
		var z := 1.0 if attenues else lerpf(1.0, zoom, u * u * (3.0 - 2.0 * u))
		cle(anim, chemin + ":scale", debut + k * Cinematique.PAS, Vector2.ONE * z)
		cle(anim, chemin + ":position", debut + k * Cinematique.PAS, (foyer - foyer * z).round())
		if attenues:
			return


static func boucle(anim: Animation, chemin: String, debut: float, fin: float, suite: Array, duree_image: float) -> void:
	var t := debut
	var k := 0
	while t < fin - 0.001:
		cle(anim, chemin + ":frame", snappedf(t, Cinematique.PAS), int(suite[k % suite.size()]))
		t += duree_image
		k += 1


func apres() -> void:
	if couche != null:
		couche.visible = false
