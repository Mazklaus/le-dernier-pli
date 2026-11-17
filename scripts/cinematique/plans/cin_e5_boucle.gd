extends CinematiquePlans
## e5_boucle (lot 2, planche validée par le GD le 17/11) : 10 s, au second passage à la
## croix-repère (e5_sentier, titre debut). L'écran de l'étape 5 inverse l'image.
## P1, 0 à 4 s : Tobie marche entre les croix toutes pareilles ; il dépasse la croix-repère
##    (travelling latéral, décor de la boucle réemployé et rapproché).
## P2, 4 à 7 s : plus tard, la même croix revient dans le cadre ; il s'arrête devant elle.
## P3, 7 à 10 s : de près, le poteau : l'encoche ancienne, noircie (et au-dessus son entaille
##    fraîche, s'il l'a faite au premier passage). Jamais une main. Lente avancée.
## Effets atténués : plans fixes. Tobie porte son ruban (CalqueRuban).

const CIN := "res://assets/graphics/cin/%s.png"
const ENV := "res://assets/graphics/env/e5/env_e5_plan3_%s.png"
const CHR := "res://assets/graphics/chr/%s.png"
const SON := "sfx_boucle_revenir"
const DUREE := 10.0
const P2 := 4.0
const P3 := 7.0
const PIEDS := Vector2(100, 316)
## La boucle (3840 px, en deux tuiles) bouclée sur elle-même : la fin de la boucle avant, une
## seconde fois le début après. Rapprochée ×1,5, le sol (y 900) à l'écran en y 980.
const ECHELLE := 1.5
const BANDE_Y := -370.0
const TUILES := [["boucle_02", -1792.0], ["boucle_01", 0.0], ["boucle_02", 2048.0], ["boucle_01", 3840.0]]
const TOBIE := Vector2(860, 980)
const IMAGE_MARCHE := 0.1
## Position x de la bande : la croix-repère (x 600, puis 4440 au second tour) devant, puis
## derrière lui (P1) ; revenue à droite, puis juste devant lui (P2). 240 px/s : son pas.
const P1_X := [400.0, -560.0]
const P2_X := [-5000.0, -5600.0]
const ARRET := 6.5
## Son entaille sur la croix-repère (fx du décor, ANCRES de gen_decors_e5), aux deux tours de
## la boucle, s'il l'a faite ; sinon rien ne distingue la croix (« celle-ci, ou une autre »).
const FX_ENTAILLE := "res://assets/graphics/fx/fx_entaille-croix.png"
const ENTAILLES := [Vector2(568, 592), Vector2(4408, 592)]
## P3 : le poteau, l'entaille fraîche (ZONE_ENTAILLE du générateur).
const ZONE_ENTAILLE := Vector2(780, 300)
const FOYER_ENCOCHE := Vector2(960, 640)
const ZOOM_ENCOCHE := 1.12

var couche: CanvasLayer


func construire() -> Animation:
	var tex := {}
	for nom in ["boucle_01", "boucle_02"]:
		tex[nom] = planche(ENV % nom)
	for nom in ["poteau", "entaille"]:
		tex[nom] = planche(CIN % ("cin_e5-boucle-" + nom))
	for nom in ["chr_tobie_marche_01", "chr_tobie_repos_01"]:
		tex[nom] = planche(CHR % nom)
	for t: Variant in tex.values():
		if t == null:
			return null
	var attenues := bool(Reglages.valeur(&"effets_attenues"))
	var entaille_faite := GameState.rencontre_vue(&"e5_entaille_faite")
	couche = couche_plein_ecran()

	var sentier := Node2D.new()
	sentier.name = "Sentier"
	var bande := Node2D.new()
	bande.name = "Bande"
	bande.scale = Vector2.ONE * ECHELLE
	for t: Array in TUILES:
		bande.add_child(sprite(String(t[0]) + "_" + str(int(t[1])), tex[t[0]], Vector2(t[1], 0)))
	var fx := planche(FX_ENTAILLE)
	if entaille_faite and fx != null:
		for i in ENTAILLES.size():
			bande.add_child(sprite("Entaille%d" % i, fx, ENTAILLES[i]))
	sentier.add_child(bande)
	sentier.add_child(_tobie("Marche", tex["chr_tobie_marche_01"], 8))
	sentier.add_child(_tobie("Repos", tex["chr_tobie_repos_01"], 4))
	couche.add_child(sentier)

	var gros := Node2D.new()
	gros.name = "Poteau"
	gros.add_child(sprite("Fond", tex["poteau"], Vector2.ZERO))
	var fraiche := sprite("Entaille", tex["entaille"], ZONE_ENTAILLE)
	fraiche.visible = entaille_faite
	gros.add_child(fraiche)
	couche.add_child(gros)

	var anim := Animation.new()
	anim.length = DUREE
	cle(anim, "Plans:visible", 0.0, true)
	if not AudioDirector.variantes_de(SON).is_empty():
		son(anim, 0.0, SON)

	# P1 et P2 : la marche, la même croix revient
	cle(anim, "Plans/Sentier:visible", 0.0, true)
	cle(anim, "Plans/Poteau:visible", 0.0, false)
	cle(anim, "Plans/Sentier/Marche:visible", 0.0, true)
	cle(anim, "Plans/Sentier/Repos:visible", 0.0, false)
	glisser(anim, "Plans/Sentier/Bande:position", 0.0, P2, P1_X, attenues)
	glisser(anim, "Plans/Sentier/Bande:position", P2, ARRET, P2_X, attenues)
	var t := 0.0
	var k := 0
	while t < ARRET - 0.001:
		cle(anim, "Plans/Sentier/Marche:frame", snappedf(t, Cinematique.PAS), k % 8)
		t += IMAGE_MARCHE
		k += 1
	cle(anim, "Plans/Sentier/Marche:visible", ARRET, false)
	cle(anim, "Plans/Sentier/Repos:visible", ARRET, true)
	cle(anim, "Plans/Sentier/Repos:frame", ARRET, 0)
	cle(anim, "Plans/Sentier:visible", P3, false)

	# P3 : l'encoche ancienne, noircie
	cle(anim, "Plans/Poteau:visible", P3, true)
	var n := roundi((DUREE - P3) / Cinematique.PAS)
	for i in n + 1:
		var u := float(i) / n
		var z := 1.0 if attenues else lerpf(1.0, ZOOM_ENCOCHE, u * u * (3.0 - 2.0 * u))
		cle(anim, "Plans/Poteau:scale", P3 + i * Cinematique.PAS, Vector2.ONE * z)
		cle(anim, "Plans/Poteau:position", P3 + i * Cinematique.PAS, (FOYER_ENCOCHE - FOYER_ENCOCHE * z).round())
		if attenues:
			break
	cle(anim, "Plans:visible", DUREE, false)
	return anim


func _tobie(nom: String, base: Texture2D, images: int) -> Sprite2D:
	var s := sprite(nom, base, TOBIE, images)
	s.offset = -PIEDS
	s.scale = Vector2.ONE * ECHELLE
	CalqueRuban.poser(s)
	return s


## Le travelling de la bande, de x0 à x1 à vitesse constante (le pas de Tobie) ; plan fixe au
## milieu en effets atténués.
static func glisser(anim: Animation, chemin: String, t0: float, t1: float, xs: Array, attenues: bool) -> void:
	var x0: float = xs[0]
	var x1: float = xs[1]
	if attenues:
		cle(anim, chemin, t0, Vector2(roundf((x0 + x1) / 2.0), BANDE_Y))
		return
	var n := maxi(1, roundi((t1 - t0) / Cinematique.PAS))
	for i in n + 1:
		cle(anim, chemin, t0 + i * Cinematique.PAS, Vector2(roundf(lerpf(x0, x1, float(i) / n)), BANDE_Y))


func apres() -> void:
	if couche != null:
		couche.visible = false
