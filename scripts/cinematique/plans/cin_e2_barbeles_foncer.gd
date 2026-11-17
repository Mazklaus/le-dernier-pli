extends CinematiquePlans
## e2_barbeles_foncer (lot 1, planche validée par le GD le 17/11) : 7 s, option « Foncer » de
## e2_barbeles, dans le noir. Planches de tools/gen_cin_e2_barbeles.py.
## P1, 0 à 2,5 s : de profil dans le brouillard, Tobie court vers la ceinture de barbelés ; le
##    fond glisse (plan fixe en effets atténués).
## P2, 2,5 à 5 s : gros plan, la pointe prend la manche, une goutte de sang perle (3 images) ;
##    il tire d'un coup sec (secousse, supprimée en effets atténués).
## P3, 5 à 7 s : de profil, il s'est arraché et repart ; le lambeau de capote reste sur le fil
##    et bat au vent.

const CIN := "res://assets/graphics/cin/%s.png"
const SON := "sfx_barbeles_foncer"
const DUREE := 7.0
const P2 := 2.5
const P3 := 5.0
## P1 : le fond (2400 px) glisse de 480 px ; Tobie court, pieds au sol de la planche (y 860).
const GLISSEMENT := Vector2(-480, 0)
const PIEDS := Vector2(160, 420)
const SOL := 860.0
const COURSE_DEBUT := 160.0
const COURSE_FIN := 1000.0
const FOULEE := [0, 1, 2, 1]
const IMAGE_COURSE := 0.1
## P2 : la manche (ZONE_MANCHE du générateur), ses trois images, la secousse.
const ZONE_MANCHE := Vector2(480, 240)
const IMAGES_MANCHE := [[2.5, 0], [3.3, 1], [4.1, 2]]
## Le gros plan est agrandi de 4 % pendant P2, pour que la secousse ne découvre aucun bord.
const MARGE := 1.04
const SECOUSSE := [[4.5, Vector2.ZERO], [4.6, Vector2(10, 6)], [4.7, Vector2(-6, -3)], [4.8, Vector2(12, 8)], [4.9, Vector2.ZERO]]
## P3 : le lambeau pendu à la pointe du fil tendu (1640, 640 dans le fond, attache à (100, 20)).
const ECHELLE_LAMBEAU := 1.3
const LAMBEAU := Vector2(1640, 640) + GLISSEMENT - Vector2(100, 20) * ECHELLE_LAMBEAU
const BAT := 0.3
const DEPART_P3 := 1320.0
const SORTIE_P3 := 1880.0
const ECHELLE_P3 := 0.9

var couche: CanvasLayer


func construire() -> Animation:
	var tex := {}
	for nom in ["brume", "course", "gros", "manche", "lambeau"]:
		tex[nom] = planche(CIN % ("cin_e2-barbeles-" + nom))
		if tex[nom] == null:
			return null
	var attenues := bool(Reglages.valeur(&"effets_attenues"))
	couche = couche_plein_ecran()
	var profil := Node2D.new()
	profil.name = "Profil"
	profil.add_child(sprite("Brume", tex["brume"], Vector2.ZERO))
	var lambeau := sprite("Lambeau", tex["lambeau"], LAMBEAU, 2)
	lambeau.scale = Vector2.ONE * ECHELLE_LAMBEAU
	profil.add_child(lambeau)
	var tobie := sprite("Tobie", tex["course"], Vector2.ZERO, 3)
	tobie.offset = -PIEDS
	profil.add_child(tobie)
	var gros := Node2D.new()
	gros.name = "Gros"
	gros.scale = Vector2.ONE * MARGE
	gros.add_child(sprite("Fond", tex["gros"], Vector2.ZERO))
	gros.add_child(sprite("Manche", tex["manche"], ZONE_MANCHE, 3))
	couche.add_child(profil)
	couche.add_child(gros)

	var anim := Animation.new()
	anim.length = DUREE
	cle(anim, "Plans:visible", 0.0, true)
	if not AudioDirector.variantes_de(SON).is_empty():
		son(anim, 0.0, SON)

	# P1 : la course vers les fils
	cle(anim, "Plans/Profil:visible", 0.0, true)
	cle(anim, "Plans/Gros:visible", 0.0, false)
	cle(anim, "Plans/Profil/Lambeau:visible", 0.0, false)
	cle(anim, "Plans/Profil/Tobie:scale", 0.0, Vector2.ONE)
	cle(anim, "Plans/Profil/Tobie:modulate", 0.0, Color.WHITE)
	if attenues:
		cle(anim, "Plans/Profil/Brume:position", 0.0, GLISSEMENT)
	else:
		glisser(anim, "Plans/Profil/Brume:position", 0.0, P2, Vector2.ZERO, GLISSEMENT)
	_courir(anim, 0.0, P2, Vector2(COURSE_DEBUT, SOL), Vector2(COURSE_FIN, SOL))

	# P2 : la manche prise, la goutte, la secousse
	cle(anim, "Plans/Profil:visible", P2, false)
	cle(anim, "Plans/Gros:visible", P2, true)
	var centre := -TAILLE_PLEIN_ECRAN * (MARGE - 1.0) / 2.0
	cle(anim, "Plans/Gros:position", 0.0, centre)
	for c: Array in IMAGES_MANCHE:
		cle(anim, "Plans/Gros/Manche:frame", c[0], c[1])
	if not attenues:
		for c: Array in SECOUSSE:
			cle(anim, "Plans/Gros:position", c[0], centre + c[1])

	# P3 : il repart, le lambeau reste sur le fil
	cle(anim, "Plans/Gros:visible", P3, false)
	cle(anim, "Plans/Profil:visible", P3, true)
	if not attenues:
		cle(anim, "Plans/Profil/Brume:position", P3, GLISSEMENT)
	cle(anim, "Plans/Profil/Lambeau:visible", P3, true)
	boucle(anim, "Plans/Profil/Lambeau", P3, DUREE, [0, 1], BAT)
	cle(anim, "Plans/Profil/Tobie:scale", P3, Vector2.ONE * ECHELLE_P3)
	_courir(anim, P3, DUREE - 0.3, Vector2(DEPART_P3, SOL), Vector2(SORTIE_P3, SOL))
	# il se perd dans le brouillard : il pâlit sur la dernière seconde
	for k in 11:
		cle(anim, "Plans/Profil/Tobie:modulate", DUREE - 1.0 + k * Cinematique.PAS, Color(1, 1, 1, 1.0 - 0.07 * k))
	cle(anim, "Plans:visible", DUREE, false)
	return anim


func _courir(anim: Animation, t0: float, t1: float, de: Vector2, a: Vector2) -> void:
	var n := maxi(1, roundi((t1 - t0) / Cinematique.PAS))
	for k in n + 1:
		cle(anim, "Plans/Profil/Tobie:position", snappedf(t0 + k * Cinematique.PAS, Cinematique.PAS), de.lerp(a, float(k) / n).round())
	boucle(anim, "Plans/Profil/Tobie", t0, t1, FOULEE, IMAGE_COURSE)


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
