extends CinematiquePlans
## e1_adieu_jacquot (lot 2, planche validée par le GD le 17/11) : 8 s, à la fin de e1_adieu,
## après « Tu le siffleras là-bas. ». Planches de tools/gen_cin_e1_adieu.py.
## P1, 0 à 3 s : dans le boyau (décor de la sape réemployé), Jacquot siffle (geste réemployé)
##    devant l'abri ; Tobie s'en va vers la droite.
## P2, 3 à 6 s : travelling arrière : Tobie au premier plan, Jacquot qui lève la main
##    rapetisse au fond (plan fixe en effets atténués).
## P3, 6 à 8 s : gros plan sur la porte de l'abri : la main tient la couverture anti-gaz,
##    salue, la lâche ; la couverture retombe.

const CIN := "res://assets/graphics/cin/%s.png"
const CHR := "res://assets/graphics/chr/%s.png"
const DECOR := "res://assets/graphics/env/e1/env_e1_plan3_sape-sortie_01.png"
const SON := "sfx_adieu_jacquot"
const DUREE := 8.0
const P2 := 3.0
const P3 := 6.0
const PIEDS := Vector2(100, 316)
## P1 : le boyau tel qu'en jeu ; Jacquot devant l'abri, Tobie qui s'éloigne.
const JACQUOT := Vector2(420, 900)
const TOBIE_DEBUT := Vector2(720, 900)
const TOBIE_FIN := Vector2(1260, 900)
## P2 : le boyau cadré serré sur Jacquot, qui s'élargit ; Tobie grand, au premier plan.
const ZOOM_DEBUT := 1.6
const BOYAU_DEBUT := Vector2(-152, -520)
const TOBIE_DEVANT := Vector2(1460, 1210)
const ECHELLE_DEVANT := 2.6
## P3 : la main (ZONE_MAIN du générateur).
const ZONE_MAIN := Vector2(560, 60)
const MAIN := [[6.0, 0], [6.4, 1], [6.9, 0], [7.2, 2], [7.5, 3]]

var couche: CanvasLayer


func construire() -> Animation:
	var tex := {}
	for nom in ["porte", "main"]:
		tex[nom] = planche(CIN % ("cin_e1-adieu-" + nom))
	for nom in ["chr_jacquot_siffler_01", "chr_jacquot_lever-main_01", "chr_tobie_marche_01"]:
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

	# le boyau, pour P1 et P2
	var boyau := Node2D.new()
	boyau.name = "Boyau"
	boyau.add_child(sprite("Decor", tex["decor"], Vector2.ZERO))
	var jacquot := sprite("Jacquot", tex["chr_jacquot_siffler_01"], JACQUOT, 6)
	jacquot.offset = -PIEDS
	boyau.add_child(jacquot)
	var tobie := sprite("Tobie", tex["chr_tobie_marche_01"], TOBIE_DEBUT, 8)
	tobie.offset = -PIEDS
	boyau.add_child(tobie)
	CalqueRuban.poser(tobie)
	couche.add_child(boyau)
	var devant := sprite("Devant", tex["chr_tobie_marche_01"], TOBIE_DEVANT, 8)
	devant.offset = -PIEDS
	devant.scale = Vector2.ONE * ECHELLE_DEVANT
	couche.add_child(devant)
	CalqueRuban.poser(devant)

	# P1 : il siffle, Tobie s'en va
	cle(anim, "Plans/Boyau:visible", 0.0, true)
	cle(anim, "Plans/Devant:visible", 0.0, false)
	cle(anim, "Plans/Boyau:scale", 0.0, Vector2.ONE)
	cle(anim, "Plans/Boyau:position", 0.0, Vector2.ZERO)
	cle(anim, "Plans/Boyau/Jacquot:texture", 0.0, tex["chr_jacquot_siffler_01"])
	cle(anim, "Plans/Boyau/Tobie:visible", 0.0, true)
	boucle(anim, "Plans/Boyau/Jacquot", 0.0, P2, [0, 1, 2, 3, 4, 5], 0.2)
	var n := roundi(P2 / Cinematique.PAS)
	for k in n + 1:
		cle(anim, "Plans/Boyau/Tobie:position", k * Cinematique.PAS, TOBIE_DEBUT.lerp(TOBIE_FIN, float(k) / n).round())
	boucle(anim, "Plans/Boyau/Tobie", 0.0, P2, [0, 1, 2, 3, 4, 5, 6, 7], Cinematique.PAS)

	# P2 : travelling arrière, Jacquot lève la main et rapetisse
	cle(anim, "Plans/Boyau/Tobie:visible", P2, false)
	cle(anim, "Plans/Devant:visible", P2, true)
	cle(anim, "Plans/Boyau/Jacquot:texture", P2, tex["chr_jacquot_lever-main_01"])
	boucle(anim, "Plans/Boyau/Jacquot", P2, P3, [0, 1, 2, 3, 4, 3, 2, 3, 4, 5], 0.3)
	boucle(anim, "Plans/Devant", P2, P3, [0, 1, 2, 3, 4, 5, 6, 7], Cinematique.PAS)
	n = roundi((P3 - P2) / Cinematique.PAS)
	for k in n + 1:
		var u := 0.5 if attenues else float(k) / n
		u = u * u * (3.0 - 2.0 * u)
		if k == 0 or not attenues:
			var t := P2 + k * Cinematique.PAS
			cle(anim, "Plans/Boyau:scale", t, Vector2.ONE * lerpf(ZOOM_DEBUT, 1.0, u))
			cle(anim, "Plans/Boyau:position", t, BOYAU_DEBUT.lerp(Vector2.ZERO, u).round())

	# P3 : la main, la couverture qui retombe
	cle(anim, "Plans/Boyau:visible", P3, false)
	cle(anim, "Plans/Devant:visible", P3, false)
	var porte := Node2D.new()
	porte.name = "Porte"
	porte.add_child(sprite("Fond", tex["porte"], Vector2.ZERO))
	porte.add_child(sprite("Main", tex["main"], ZONE_MAIN, 2, 2))
	couche.add_child(porte)
	cle(anim, "Plans/Porte:visible", 0.0, false)
	cle(anim, "Plans/Porte:visible", P3, true)
	for c: Array in MAIN:
		cle(anim, "Plans/Porte/Main:frame", c[0], c[1])
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
