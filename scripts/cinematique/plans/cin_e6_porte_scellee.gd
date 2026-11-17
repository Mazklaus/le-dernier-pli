extends CinematiquePlans
## e6_porte_scellee (lot 1, planche validée par le GD le 17/11) : 10 s, au début de e6_seuil.
## Planches de tools/gen_cin_e6_porte.py (l'écran de l'étape 6 les inverse).
## P1, 0 à 3 s : contre-plongée sur la porte, couche de cire sur couche de cire ; lent
##    panoramique du seuil vers l'arc (plan fixe en effets atténués).
## P2, 3 à 7 s : devant la porte (décor du seuil réemployé, rapproché), Éloi pose son bocal
##    (geste poser-bocal réemployé) devant Tobie.
## P3, 7 à 10 s : Éloi recule dans l'ombre sans se retourner et s'efface ; le bocal reste seul
##    devant la porte. Rien de ce qu'il y a derrière.

const CIN := "res://assets/graphics/cin/%s.png"
const CHR := "res://assets/graphics/chr/%s.png"
const DECOR := "res://assets/graphics/env/e6/env_e6_plan3_seuil_01.png"
const SON := "sfx_porte_scellee"
const DUREE := 10.0
const P2 := 3.0
const P3 := 7.0
## P1 : la porte (1920 × 2160), du seuil (en bas) à l'arc (en haut).
const CIRE_BAS := Vector2(0, -1080)
const CIRE_HAUT := Vector2.ZERO
const DEBUT_PANORAMIQUE := 0.2
## P2 et P3 : le seuil rapproché autour du pied de la porte.
const ECHELLE_SEUIL := 1.25
const FOYER := Vector2(900, 760)
const PIEDS := Vector2(100, 316)
const TOBIE := Vector2(740, 900)
const ELOI := Vector2(1040, 900)
const BOCAL := Vector2(40, 268)          # coin du bocal dans l'image d'Éloi (CADRE_BOCAL)
const POSE := [[3.6, 1], [3.85, 2], [4.1, 3], [4.4, 4], [4.7, 5]]
const DEBUT_RECUL := 7.2
const FIN_RECUL := 9.4
const RECUL := Vector2(520, -30)
const RESPIRATION := 0.5

var couche: CanvasLayer


func construire() -> Animation:
	var tex := {}
	for nom in ["cire", "eloi", "bocal"]:
		tex[nom] = planche(CIN % ("cin_e6-porte-" + nom))
	for nom in ["chr_eloi_poser-bocal_01", "chr_tobie_repos_01"]:
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

	# P1 : la cire, du seuil vers l'arc
	couche.add_child(sprite("Cire", tex["cire"], CIRE_BAS))
	cle(anim, "Plans/Cire:visible", 0.0, true)
	if attenues:
		cle(anim, "Plans/Cire:position", 0.0, CIRE_BAS.lerp(CIRE_HAUT, 0.5))
	else:
		cle(anim, "Plans/Cire:position", 0.0, CIRE_BAS)
		glisser(anim, "Plans/Cire:position", DEBUT_PANORAMIQUE, P2, CIRE_BAS, CIRE_HAUT)
	cle(anim, "Plans/Cire:visible", P2, false)

	# P2 et P3 : devant la porte
	var seuil := Node2D.new()
	seuil.name = "Seuil"
	seuil.scale = Vector2.ONE * ECHELLE_SEUIL
	seuil.position = FOYER - FOYER * ECHELLE_SEUIL
	seuil.add_child(sprite("Decor", tex["decor"], Vector2.ZERO))
	var tobie := sprite("Tobie", tex["chr_tobie_repos_01"], TOBIE, 4)
	tobie.offset = -PIEDS
	seuil.add_child(tobie)
	var bocal := sprite("Bocal", tex["bocal"], ELOI - PIEDS + BOCAL)
	seuil.add_child(bocal)
	var geste := sprite("Geste", tex["chr_eloi_poser-bocal_01"], ELOI, 6)
	geste.offset = -PIEDS
	seuil.add_child(geste)
	var eloi := sprite("Eloi", tex["eloi"], ELOI)
	eloi.offset = -PIEDS
	seuil.add_child(eloi)
	couche.add_child(seuil)
	cle(anim, "Plans/Seuil:visible", 0.0, false)
	cle(anim, "Plans/Seuil:visible", P2, true)
	boucle(anim, "Plans/Seuil/Tobie", P2, DUREE, [0, 1, 2, 3, 2, 1], RESPIRATION)
	# le geste : Éloi tient son bocal, se penche, le pose, se redresse
	cle(anim, "Plans/Seuil/Geste:visible", 0.0, true)
	cle(anim, "Plans/Seuil/Geste:frame", P2, 0)
	for c: Array in POSE:
		cle(anim, "Plans/Seuil/Geste:frame", c[0], c[1])
	# puis il recule sans le bocal, qui reste à sa place
	cle(anim, "Plans/Seuil/Bocal:visible", 0.0, false)
	cle(anim, "Plans/Seuil/Eloi:visible", 0.0, false)
	cle(anim, "Plans/Seuil/Geste:visible", P3, false)
	cle(anim, "Plans/Seuil/Bocal:visible", P3, true)
	cle(anim, "Plans/Seuil/Eloi:visible", P3, true)
	cle(anim, "Plans/Seuil/Eloi:position", 0.0, ELOI)
	cle(anim, "Plans/Seuil/Eloi:modulate", 0.0, Color.WHITE)
	var n := roundi((FIN_RECUL - DEBUT_RECUL) / Cinematique.PAS)
	for k in n + 1:
		var u := float(k) / n
		var t := DEBUT_RECUL + k * Cinematique.PAS
		var pas := -4.0 * absf(sin(u * 6.0 * PI))
		cle(anim, "Plans/Seuil/Eloi:position", t, (ELOI + RECUL * u + Vector2(0, pas)).round())
		cle(anim, "Plans/Seuil/Eloi:modulate", t, Color(1, 1, 1, clampf(1.4 - 1.4 * u, 0.0, 1.0)))
	cle(anim, "Plans:visible", DUREE, false)
	return anim


func apres() -> void:
	if couche != null:
		couche.visible = false


static func glisser(anim: Animation, chemin: String, t0: float, t1: float, v0: Vector2, v1: Vector2) -> void:
	var n := maxi(1, roundi((t1 - t0) / Cinematique.PAS))
	for k in n + 1:
		var u := float(k) / n
		cle(anim, chemin, snappedf(t0 + k * Cinematique.PAS, Cinematique.PAS), v0.lerp(v1, u * u * (3.0 - 2.0 * u)).round())


static func boucle(anim: Animation, chemin: String, debut: float, fin: float, suite: Array, duree_image: float) -> void:
	var t := debut
	var k := 0
	while t < fin - 0.001:
		cle(anim, chemin + ":frame", snappedf(t, Cinematique.PAS), int(suite[k % suite.size()]))
		t += duree_image
		k += 1
