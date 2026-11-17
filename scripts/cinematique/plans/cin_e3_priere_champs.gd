extends CinematiquePlans
## e3_priere_champs (lot 1, planche de la DA validée par le GD le 17/11 ; tools/gen_cin_e3_priere.py) :
## début de « champs » dans e3_procession. La nuit, dans le champ labouré, le village est à genoux
## en cercle, front contre terre, les cierges plantés devant eux ; il reste une place vide, avec un
## cierge éteint. La ciné s'arrête dessus : c'est le joueur qui choisit ensuite de s'y mettre.
##   P1, 0 à 4 s : de profil, au ras des sillons, deux rangs de dos ronds qui respirent ; le cercle
##       sort du cadre des deux côtés, la caméra glisse.
##   P2, 4 à 8 s : en plongée, le cercle déborde du cadre (rien ne se compte).
##   P3, 8 à 12 s : poussée lente vers la place vide ; le vent couche les flammes.
## Peint de nuit, comme e3_procession_nuit : l'écran gravure garde la teinte du chemin de nuit.
## En effets atténués, le glissement et la poussée deviennent des plans fixes.

const CIN := "res://assets/graphics/cin/%s.png"
const DUREE := 12.0
const P2 := 4.0
const P3 := 8.0
## P1 : sprites de profil 300 × 220, le sol à (150, 210) ; image = silhouette × 2 + souffle.
const PIED_PROFIL := Vector2(150, 210)
const RANG_FOND := {"y": 640.0, "echelle": 0.72, "pas": 215.0, "x0": -120.0}
const RANG_DEVANT := {"y": 1000.0, "echelle": 1.3, "pas": 400.0, "x0": -260.0}
## le cierge devant la tête : à droite des pieds de la silhouette (repère du sprite de profil)
const CIERGE_PROFIL := Vector2(158, 0)
const PIED_CIERGE := Vector2(30, 116)
const GLISSEMENT := -160.0
const SOUFFLE := 1.0
const IMAGE_FLAMME := 0.3
## P2-P3 : le cercle, vu d'en haut ; sprites 300 × 390 tournés tête vers le centre.
const CENTRE := Vector2(960, 330)
const RAYON := 690.0
const NB_PLACES := 30
const PLACE_VIDE := 3          # la place à 3 × 360/30 = 36° : en bas à droite de l'écran
const CENTRE_DESSUS := Vector2(150, 200)
const ECHELLE_DESSUS := 0.62
const RAYON_CIERGES := 560.0
const CENTRE_LUEUR := Vector2(45, 45)
const SILLONS := Vector2(-240, -160)
const ZOOM := 1.8
const VENT := 9.5
## Le fond sonore du Sound Designer (un seul son de 12 s : souffles, mèches, le Cantique fredonné,
## la rafale à 9,5 s), s'il est là.
const SON := "sfx_priere_murmurer"
## Les silhouettes, sans motif qui se répète : 0 femme au fichu, 1 homme au bonnet, 2 enfant,
## 3 vieux tassé.
const SILHOUETTES := [0, 1, 0, 3, 1, 0, 2, 1, 0, 1, 3, 0, 2, 1, 0, 0, 1, 3, 0, 1, 2, 0, 1]

var couche: CanvasLayer


func construire() -> Animation:
	var tex := {}
	for nom in ["cin_e3-priere-champ", "cin_e3-priere-profil", "cin_e3-priere-sillons", "cin_e3-priere-dessus",
			"cin_e3-priere-cierge", "cin_e3-priere-lueur"]:
		tex[nom] = planche(CIN % nom)
		if tex[nom] == null:
			return null
	var attenues := bool(Reglages.valeur(&"effets_attenues"))
	couche = couche_plein_ecran()
	var anim := Animation.new()
	anim.length = DUREE
	cle(anim, "Plans:visible", 0.0, true)
	if not AudioDirector.variantes_de(SON).is_empty():
		son(anim, 0.0, SON)

	# P1 : de profil
	var p1 := Node2D.new()
	p1.name = "P1"
	couche.add_child(p1)
	p1.add_child(sprite("Champ", tex["cin_e3-priere-champ"], Vector2.ZERO))
	var i := 0
	for rang: Dictionary in [RANG_FOND, RANG_DEVANT]:
		var e: float = rang["echelle"]
		var x: float = rang["x0"]
		while x < 1920.0 - GLISSEMENT + 300.0:
			var v: int = SILHOUETTES[i % SILHOUETTES.size()]
			var nom := "Prie%d" % i
			var s := sprite(nom, tex["cin_e3-priere-profil"], Vector2.ZERO, 2, 4)
			s.offset = -PIED_PROFIL
			s.scale = Vector2(e, e)
			s.position = Vector2(roundf(x), rang["y"])
			p1.add_child(s)
			var c := sprite("Cierge%d" % i, tex["cin_e3-priere-cierge"], Vector2.ZERO, 3)
			c.offset = -PIED_CIERGE
			c.scale = Vector2(e, e)
			c.position = s.position + CIERGE_PROFIL * e
			p1.add_child(c)
			# ils respirent, chacun à son rythme ; les flammes vacillent
			var t := 0.0
			var k := 0
			while t < P2 - 0.001:
				cle(anim, "Plans/P1/%s:frame" % nom, snappedf(t, PAS), v * 2 + (k + i) % 2)
				t += SOUFFLE + 0.1 * (i % 3)
				k += 1
			boucle(anim, "Plans/P1/Cierge%d" % i, 0.0, P2, [0, 1] if i % 2 == 0 else [1, 0], IMAGE_FLAMME)
			x += rang["pas"]
			i += 1
	cle(anim, "Plans/P1:visible", 0.0, true)
	cle(anim, "Plans/P1:visible", P2, false)
	if attenues:
		cle(anim, "Plans/P1:position", 0.0, Vector2.ZERO)
	else:
		glisser(anim, "Plans/P1:position", 0.0, P2, Vector2.ZERO, Vector2(GLISSEMENT, 0.0))

	# P2 et P3 : le cercle, d'en haut
	var cercle := Node2D.new()
	cercle.name = "Cercle"
	cercle.visible = false
	couche.add_child(cercle)
	cercle.add_child(sprite("Sillons", tex["cin_e3-priere-sillons"], SILLONS))
	var vide := Vector2.ZERO
	for p in NB_PLACES:
		var a := TAU * p / NB_PLACES
		var dir := Vector2(cos(a), sin(a))
		var l := sprite("Lueur%d" % p, tex["cin_e3-priere-lueur"], Vector2.ZERO, 4)
		l.offset = -CENTRE_LUEUR
		l.position = (CENTRE + dir * RAYON_CIERGES).round()
		cercle.add_child(l)
		if p == PLACE_VIDE:
			cle(anim, "Plans/Cercle/Lueur%d:frame" % p, P2, 3)
			vide = CENTRE + dir * (RAYON + RAYON_CIERGES) / 2.0
			continue
		var d := sprite("Dos%d" % p, tex["cin_e3-priere-dessus"], Vector2.ZERO, 4)
		d.offset = -CENTRE_DESSUS
		d.frame = SILHOUETTES[p % SILHOUETTES.size()]
		d.rotation = a - PI / 2.0
		d.scale = Vector2(ECHELLE_DESSUS, ECHELLE_DESSUS)
		d.position = (CENTRE + dir * RAYON).round()
		cercle.add_child(d)
		boucle(anim, "Plans/Cercle/Lueur%d" % p, P2, VENT, [0, 1] if p % 2 == 0 else [1, 0], IMAGE_FLAMME)
		boucle(anim, "Plans/Cercle/Lueur%d" % p, VENT, DUREE, [2, 1, 2, 2] if p % 2 == 0 else [2, 2, 1, 2], IMAGE_FLAMME)
	cle(anim, "Plans/Cercle:visible", 0.0, false)
	cle(anim, "Plans/Cercle:visible", P2, true)
	# la poussée vers la place vide : elle vient au centre de l'écran (position = écran − vide × zoom)
	var arrivee := Vector2(960, 540) - vide * ZOOM
	cle(anim, "Plans/Cercle:scale", P2, Vector2.ONE)
	cle(anim, "Plans/Cercle:position", P2, Vector2.ZERO)
	if attenues:
		cle(anim, "Plans/Cercle:scale", 10.0, Vector2(ZOOM, ZOOM))
		cle(anim, "Plans/Cercle:position", 10.0, arrivee.round())
	else:
		glisser(anim, "Plans/Cercle:scale", P3, DUREE - 0.5, Vector2.ONE, Vector2(ZOOM, ZOOM))
		glisser(anim, "Plans/Cercle:position", P3, DUREE - 0.5, Vector2.ZERO, arrivee)
	cle(anim, "Plans:visible", DUREE, false)
	return anim


func apres() -> void:
	if couche != null:
		couche.visible = false


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
