extends CinematiquePlans
## e2_brouillard_dechire (lot 2, planche validée par le GD le 17/11) : 10 s, au début de
## e2_cantique. Planches de tools/gen_cin_e2_brouillard.py.
## P1, 0 à 3 s : le brouillard plein cadre, il roule (3 images en boucle).
## P2, 3 à 7 s : il se déchire d'un coup autour de la souche brûlée (4 images en une seconde),
##    puis la souche reste seule debout ; lente avancée (plan fixe en effets atténués).
## P3, 7 à 10 s : très loin, le village et son clocher vide ; lent zoom vers la baie, où rien
##    ne pend.

const CIN := "res://assets/graphics/cin/%s.png"
const SON := "sfx_brouillard_dechire"
const DUREE := 10.0
const P2 := 3.0
const P3 := 7.0
## La brume est dessinée en demi-définition (960 x 540), 7 images en grille 4 x 2 : affichée ×2.
const ECHELLE_BRUME := 2.0
const ROULE := [0, 1, 2]
const IMAGE_ROULE := 0.3
const DECHIRE := [[3.0, 3], [3.3, 4], [3.6, 5], [4.0, 6]]
const FOYER_SOUCHE := Vector2(820, 700)
const ZOOM_SOUCHE := 1.08
const FOYER_CLOCHER := Vector2(1180, 470)
const ZOOM_CLOCHER := 1.25

var couche: CanvasLayer


func construire() -> Animation:
	var tex := {}
	for nom in ["souche", "brume", "village"]:
		tex[nom] = planche(CIN % ("cin_e2-brouillard-" + nom))
		if tex[nom] == null:
			return null
	var attenues := bool(Reglages.valeur(&"effets_attenues"))
	couche = couche_plein_ecran()
	var champ := Node2D.new()
	champ.name = "Champ"
	champ.add_child(sprite("Fond", tex["souche"], Vector2.ZERO))
	var brume := sprite("Brume", tex["brume"], Vector2.ZERO, 4, 2)
	brume.scale = Vector2.ONE * ECHELLE_BRUME
	champ.add_child(brume)
	couche.add_child(champ)
	var loin := Node2D.new()
	loin.name = "Village"
	loin.add_child(sprite("Fond", tex["village"], Vector2.ZERO))
	couche.add_child(loin)

	var anim := Animation.new()
	anim.length = DUREE
	cle(anim, "Plans:visible", 0.0, true)
	if not AudioDirector.variantes_de(SON).is_empty():
		son(anim, 0.0, SON)

	# P1 : le brouillard roule
	cle(anim, "Plans/Champ:visible", 0.0, true)
	cle(anim, "Plans/Village:visible", 0.0, false)
	cle(anim, "Plans/Champ:scale", 0.0, Vector2.ONE)
	cle(anim, "Plans/Champ:position", 0.0, Vector2.ZERO)
	var t := 0.0
	var k := 0
	while t < P2 - 0.001:
		cle(anim, "Plans/Champ/Brume:frame", snappedf(t, Cinematique.PAS), ROULE[k % ROULE.size()])
		t += IMAGE_ROULE
		k += 1

	# P2 : il se déchire sur la souche
	for c: Array in DECHIRE:
		cle(anim, "Plans/Champ/Brume:frame", c[0], c[1])
	avancee(anim, "Plans/Champ", P2, P3, FOYER_SOUCHE, ZOOM_SOUCHE, attenues)
	cle(anim, "Plans/Champ:visible", P3, false)

	# P3 : le village, le clocher vide
	cle(anim, "Plans/Village:visible", P3, true)
	avancee(anim, "Plans/Village", P3, DUREE, FOYER_CLOCHER, ZOOM_CLOCHER, attenues)
	cle(anim, "Plans:visible", DUREE, false)
	return anim


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


func apres() -> void:
	if couche != null:
		couche.visible = false
