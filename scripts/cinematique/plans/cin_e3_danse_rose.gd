extends CinematiquePlans
## e3_danse_rose (lot 1, planche de la DA validée par le GD le 17/11 ; tools/gen_cin_e3_danse.py) :
## « Demander son nom à la mariée » dans e3_noce, sur « Alors danse, Tobie. Un seul tour. »
##   P1, 0 à 3 s : la place de la noce, le violon reprend ; Rose se tourne vers Tobie.
##   P2, 3 à 7 s : un seul tour à deux, la main dans la main ; il trébuche, les rubans de papier
##       tournent avec elle.
##   P3, 7 à 10 s : le gros plan, elle rit (un vrai visage, retouche du GD : le seul moment de
##       joie du jeu).
## En effets atténués, la poussée du gros plan devient un plan fixe ; la danse reste (ce sont les
## personnages qui bougent, pas la caméra).

const CIN := "res://assets/graphics/cin/%s.png"
const CHR := "res://assets/graphics/chr/%s.png"
const DUREE := 10.0
const P2 := 3.0
const P3 := 7.0
## Le décor de la place (env_e3_plan3_surface_03, 2048 × 712), agrandi pour remplir l'écran.
const ECHELLE_DECOR := 1.52
const DECALAGE_DECOR := Vector2(-1186, 0)
const SOL := 975.0
const ECHELLE := 1.5
const PIEDS := Vector2(100, 316)
const X_TOBIE := 640.0
const X_ROSE := 960.0
const X_VIOLON := 1460.0
const SE_TOURNE := 1.8
## Le tour : autour de CENTRE, l'un en face de l'autre, d'un seul tour en 4 s.
const CENTRE := Vector2(800, SOL)
const RAYON := Vector2(160, 22)
const TREBUCHE := 5.2
## Le bouquet de Rose et la main de Tobie, depuis les pieds (repère des sprites, échelle 1).
const BOUQUET := Vector2(-4, -119)
const MAIN_TOBIE := Vector2(30, -126)
const ATTACHE_RUBANS := Vector2(80, 20)
## P3 : le visage, et ses deux images (ZONE_RIRE) : le rire éclate, la tête part en arrière.
const ZONE_RIRE := Vector2(560, 80)
const RIRE := [[7.0, 0], [7.7, 1], [8.3, 0], [8.9, 1], [9.4, 0]]
const VISAGE := Vector2(960, 500)

var couche: CanvasLayer


func construire() -> Animation:
	var tex := {}
	for nom in ["cin_e3-danse-rubans", "cin_e3-danse-rire", "cin_e3-danse-rires"]:
		tex[nom] = planche(CIN % nom)
	for nom in ["chr_rose_repos_01", "chr_rose_danser_01", "chr_tobie_repos_01", "chr_tobie_marche_01", "chr_violoneux_repos_01"]:
		tex[nom] = planche(CHR % nom)
	tex["decor"] = planche("res://assets/graphics/env/e3/env_e3_plan3_surface_03.png")
	for t: Variant in tex.values():
		if t == null:
			return null
	var attenues := bool(Reglages.valeur(&"effets_attenues"))
	couche = couche_plein_ecran()
	var anim := Animation.new()
	anim.length = DUREE
	cle(anim, "Plans:visible", 0.0, true)

	# P1 et P2 : la place
	var place := Node2D.new()
	place.name = "Place"
	couche.add_child(place)
	var ciel := ColorRect.new()
	ciel.color = StylePapier.PAPIER
	ciel.size = TAILLE_PLEIN_ECRAN
	ciel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	place.add_child(ciel)
	var decor := sprite("Decor", tex["decor"], DECALAGE_DECOR)
	decor.scale = Vector2(ECHELLE_DECOR, ECHELLE_DECOR)
	place.add_child(decor)
	var violon := personnage("Violon", tex["chr_violoneux_repos_01"], 4, Vector2(X_VIOLON, SOL))
	place.add_child(violon)
	var tobie := personnage("Tobie", tex["chr_tobie_repos_01"], 4, Vector2(X_TOBIE, SOL))
	place.add_child(tobie)
	var rose := personnage("Rose", tex["chr_rose_repos_01"], 4, Vector2(X_ROSE, SOL))
	place.add_child(rose)
	var bras := Node2D.new()
	bras.name = "Bras"
	place.add_child(bras)
	for couche_bras in [[Color(StylePapier.ENCRE), 13.0], [Color(StylePapier.PAPIER), 7.0]]:
		var l := Line2D.new()
		l.name = "Trait%d" % bras.get_child_count()
		l.default_color = couche_bras[0]
		l.width = couche_bras[1]
		l.begin_cap_mode = Line2D.LINE_CAP_ROUND
		l.end_cap_mode = Line2D.LINE_CAP_ROUND
		l.points = PackedVector2Array([Vector2.ZERO, Vector2.ZERO])
		bras.add_child(l)
	var rubans := sprite("Rubans", tex["cin_e3-danse-rubans"], Vector2.ZERO, 4)
	rubans.offset = -ATTACHE_RUBANS
	place.add_child(rubans)

	# P1 : le violon (l'archet va et vient), Tobie et Rose au repos ; elle se tourne vers lui
	boucle(anim, "Plans/Place/Violon", 0.0, P3, [0, 1, 2, 3], 0.3)
	boucle(anim, "Plans/Place/Tobie", 0.0, P2, [0, 1, 2, 1], 0.3)
	boucle(anim, "Plans/Place/Rose", 0.0, SE_TOURNE, [0, 1, 2, 1], 0.3)
	cle(anim, "Plans/Place/Rose:texture", 0.0, tex["chr_rose_repos_01"])
	cle(anim, "Plans/Place/Rose:hframes", 0.0, 4)
	cle(anim, "Plans/Place/Rose:texture", SE_TOURNE, tex["chr_rose_danser_01"])
	cle(anim, "Plans/Place/Rose:hframes", SE_TOURNE, 6)
	cle(anim, "Plans/Place/Rose:frame", SE_TOURNE, 4)
	cle(anim, "Plans/Place/Rose:frame", SE_TOURNE + 0.5, 5)
	cle(anim, "Plans/Place/Rose:position", 0.0, Vector2(X_ROSE, SOL))
	cle(anim, "Plans/Place/Tobie:position", 0.0, Vector2(X_TOBIE, SOL))
	cle(anim, "Plans/Place/Tobie:flip_h", 0.0, false)
	cle(anim, "Plans/Place/Bras:visible", 0.0, false)
	cle(anim, "Plans/Place/Rubans:position", 0.0, Vector2(X_ROSE, SOL) + BOUQUET * ECHELLE)
	cle(anim, "Plans/Place/Rubans:frame", 0.0, 0)

	# P2 : le tour, d'un seul élan ; Rose devant quand elle passe vers nous
	cle(anim, "Plans/Place/Tobie:texture", 0.0, tex["chr_tobie_repos_01"])
	cle(anim, "Plans/Place/Tobie:hframes", 0.0, 4)
	cle(anim, "Plans/Place/Tobie:texture", P2, tex["chr_tobie_marche_01"])
	cle(anim, "Plans/Place/Tobie:hframes", P2, 8)
	cle(anim, "Plans/Place/Bras:visible", P2, true)
	var n := roundi((P3 - P2) / PAS)
	for k in n + 1:
		var t := P2 + k * PAS
		var u := float(k) / n
		var a := TAU * (u * u * (3.0 - 2.0 * u))
		var off := Vector2(cos(a) * RAYON.x, sin(a) * RAYON.y)
		var pr := (CENTRE + off).round()
		var pt := (CENTRE - off).round()
		if t >= TREBUCHE and t < TREBUCHE + 0.3:
			pt += Vector2(0, 8)   # il marche sur la traîne : il trébuche
		var tobie_a_gauche := pt.x < pr.x
		cle(anim, "Plans/Place/Rose:position", snappedf(t, PAS), pr)
		cle(anim, "Plans/Place/Tobie:position", snappedf(t, PAS), pt)
		cle(anim, "Plans/Place/Tobie:flip_h", snappedf(t, PAS), not tobie_a_gauche)
		cle(anim, "Plans/Place/Rose:z_index", snappedf(t, PAS), 1 if off.y > 0 else 0)
		cle(anim, "Plans/Place/Rose:frame", snappedf(t, PAS), [1, 2, 3, 4, 5, 0][k / 2 % 6])
		if not (t >= TREBUCHE and t < TREBUCHE + 0.3):
			cle(anim, "Plans/Place/Tobie:frame", snappedf(t, PAS), (k / 2) % 8)
		var main_t := pt + Vector2(MAIN_TOBIE.x * (1 if tobie_a_gauche else -1), MAIN_TOBIE.y) * ECHELLE
		var main_r := pr + BOUQUET * ECHELLE
		for b in 2:
			cle(anim, "Plans/Place/Bras/Trait%d:points" % b, snappedf(t, PAS), PackedVector2Array([main_r, main_t]))
		cle(anim, "Plans/Place/Rubans:position", snappedf(t, PAS), main_r)
		cle(anim, "Plans/Place/Rubans:z_index", snappedf(t, PAS), 1 if off.y > 0 else 0)
		cle(anim, "Plans/Place/Rubans:frame", snappedf(t, PAS), (k / 2) % 4)
	cle(anim, "Plans/Place:visible", 0.0, true)
	cle(anim, "Plans/Place:visible", P3, false)

	# P3 : le gros plan, elle rit
	var gros := Node2D.new()
	gros.name = "Rire"
	gros.visible = false
	couche.add_child(gros)
	gros.add_child(sprite("Fond", tex["cin_e3-danse-rire"], Vector2.ZERO))
	gros.add_child(sprite("Tete", tex["cin_e3-danse-rires"], ZONE_RIRE, 2))
	for r: Array in RIRE:
		cle(anim, "Plans/Rire/Tete:frame", r[0], r[1])
	cle(anim, "Plans/Rire:visible", 0.0, false)
	cle(anim, "Plans/Rire:visible", P3, true)
	if attenues:
		cle(anim, "Plans/Rire:scale", P3, Vector2.ONE)
		cle(anim, "Plans/Rire:position", P3, Vector2.ZERO)
	else:
		glisser(anim, "Plans/Rire:scale", P3, DUREE, Vector2.ONE, Vector2(1.05, 1.05))
		glisser(anim, "Plans/Rire:position", P3, DUREE, Vector2.ZERO, VISAGE - VISAGE * 1.05)
	cle(anim, "Plans:visible", DUREE, false)
	return anim


func apres() -> void:
	if couche != null:
		couche.visible = false


func personnage(nom: String, texture: Texture2D, images: int, pieds: Vector2) -> Sprite2D:
	var s := sprite(nom, texture, Vector2.ZERO, images)
	s.offset = -PIEDS
	s.scale = Vector2(ECHELLE, ECHELLE)
	s.position = pieds
	return s


## Un mouvement de caméra adouci aux deux bouts, une clé par dixième de seconde.
static func glisser(anim: Animation, chemin: String, t0: float, t1: float, v0: Vector2, v1: Vector2) -> void:
	var n := maxi(1, roundi((t1 - t0) / PAS))
	for k in n + 1:
		var u := float(k) / n
		var v: Vector2 = v0.lerp(v1, u * u * (3.0 - 2.0 * u))
		cle(anim, chemin, snappedf(t0 + k * PAS, PAS), v.round() if chemin.ends_with(":position") else v)


## Des images en boucle (frame) de debut à fin, chacune tenue duree_image.
static func boucle(anim: Animation, chemin: String, debut: float, fin: float, suite: Array, duree_image: float) -> void:
	var t := debut
	var k := 0
	while t < fin - 0.001:
		cle(anim, chemin + ":frame", snappedf(t, PAS), int(suite[k % suite.size()]))
		t += duree_image
		k += 1
