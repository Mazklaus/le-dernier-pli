extends CinematiquePlans
## e6_village_sous_terre (lot 1, planche validée par le GD le 17/11) : 12 s, au début de
## e6_tablee. Planches de tools/gen_cin_e6_village.py (l'écran de l'étape 6 les inverse).
## P1, 0 à 4 s : le village dans l'argile (décor village_01 réemployé, agrandi), les fumées
##    qui montent des toits et s'écrasent sous la terre ; le décor glisse.
## P2, 4 à 8 s : la longue table, les convives assis lèvent leurs cuillères (gestes
##    lever-cuillere réemployés, décalés : la musique, ce sont les cuillères) ; une place vide
##    au bout ; la table glisse vers elle.
## P3, 8 à 12 s : la chaise vide, l'écuelle servie qui fume ; lente poussée vers l'écuelle.
## En effets atténués, plus de glissement ni de poussée : trois plans fixes.

const CIN := "res://assets/graphics/cin/%s.png"
const CHR := "res://assets/graphics/chr/chr_%s_lever-cuillere_01.png"
const DECOR := "res://assets/graphics/env/e6/env_e6_plan3_village_01.png"
const SON := "sfx_village_tablee"
## La musique de la tablée (émetteur posé dans etape_06.tscn sous le village), mise en pause le
## temps de la ciné : son air et celui des cuillères se chevaucheraient.
const EMETTEUR := "MusiqueTablee"
const DUREE := 12.0
const P2 := 4.0
const P3 := 8.0
## P1 : le décor (2048 × 1080) agrandi, qui glisse ; les fumées sur les deux toits.
const ECHELLE_VILLAGE := 1.25
const VILLAGE_DEBUT := Vector2(0, -135)
const VILLAGE_FIN := Vector2(-640, -135)
const TOITS := [Vector2(1210, 600), Vector2(1527, 562)]
const BASE_FUMEE := Vector2(160, 290)
const IMAGE_FUMEE := 0.3
## P2 : la table (2400 px) ; le dessus de table à y 700 (ligne 80 du plateau).
const PLATEAU := Vector2(0, 620)
const TABLE_FIN := Vector2(-480, 0)
const DESSUS_TABLE := 700.0
const ECHELLE_CONVIVE := 1.6
const GENOUX := 215.0             # hauteur du dessus de table dans l'image d'un convive
const CONVIVES := ["femme", "mere", "enfant", "fillette"]
const PAS_CONVIVE := 270.0
const PREMIER := 40.0
const PLACE_VIDE := 2150.0        # le bout de la table, où personne n'est assis
## P3 : la chaise, l'écuelle (BOL du générateur) et sa vapeur.
const BOL := Vector2(960, 740)
const BASE_VAPEUR := Vector2(100, 270)
const POUSSEE := 1.18

var couche: CanvasLayer
var emetteur: AudioStreamPlayer2D


func construire() -> Animation:
	var tex := {}
	for nom in ["fumee", "table", "plateau", "chaise", "vapeur"]:
		tex[nom] = planche(CIN % ("cin_e6-village-" + nom))
	for nom: String in CONVIVES:
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

	# P1 : le village et ses fumées
	var village := Node2D.new()
	village.name = "Village"
	village.scale = Vector2.ONE * ECHELLE_VILLAGE
	village.add_child(sprite("Decor", tex["decor"], Vector2.ZERO))
	for i in TOITS.size():
		var f := sprite("Fumee%d" % i, tex["fumee"], TOITS[i] - BASE_FUMEE, 3)
		village.add_child(f)
		boucle(anim, "Plans/Village/Fumee%d" % i, 0.0, P2, [i % 3, (i + 1) % 3, (i + 2) % 3], IMAGE_FUMEE)
	couche.add_child(village)
	cle(anim, "Plans/Village:visible", 0.0, true)
	if attenues:
		cle(anim, "Plans/Village:position", 0.0, VILLAGE_DEBUT.lerp(VILLAGE_FIN, 0.5).round())
	else:
		glisser(anim, "Plans/Village:position", 0.0, P2, VILLAGE_DEBUT, VILLAGE_FIN)
	cle(anim, "Plans/Village:visible", P2, false)

	# P2 : la longue table
	var tablee := Node2D.new()
	tablee.name = "Table"
	tablee.add_child(sprite("Fond", tex["table"], Vector2.ZERO))
	var x := PREMIER
	var i := 0
	while x < 2400.0:
		if absf(x - PLACE_VIDE) > PAS_CONVIVE * 0.6:
			var nom: String = CONVIVES[i % CONVIVES.size()]
			var c := sprite("Convive%d" % i, tex[nom], Vector2.ZERO, 6)
			c.centered = false
			c.scale = Vector2.ONE * ECHELLE_CONVIVE
			c.flip_h = i % 2 == 1
			c.position = Vector2(x, DESSUS_TABLE - GENOUX * ECHELLE_CONVIVE)
			tablee.add_child(c)
			var depart := (i * 2) % 6
			var suite: Array = []
			for k in 6:
				suite.append((depart + k) % 6)
			boucle(anim, "Plans/Table/Convive%d" % i, P2, P3, suite, Cinematique.PAS)
			i += 1
		x += PAS_CONVIVE
	tablee.add_child(sprite("Plateau", tex["plateau"], PLATEAU))
	couche.add_child(tablee)
	cle(anim, "Plans/Table:visible", 0.0, false)
	cle(anim, "Plans/Table:visible", P2, true)
	if attenues:
		cle(anim, "Plans/Table:position", 0.0, TABLE_FIN * 0.5)
	else:
		cle(anim, "Plans/Table:position", 0.0, Vector2.ZERO)
		glisser(anim, "Plans/Table:position", P2, P3, Vector2.ZERO, TABLE_FIN)
	cle(anim, "Plans/Table:visible", P3, false)

	# P3 : la chaise vide, l'écuelle qui fume
	var chaise := Node2D.new()
	chaise.name = "Chaise"
	chaise.add_child(sprite("Fond", tex["chaise"], Vector2.ZERO))
	chaise.add_child(sprite("Vapeur", tex["vapeur"], BOL - BASE_VAPEUR, 3))
	couche.add_child(chaise)
	cle(anim, "Plans/Chaise:visible", 0.0, false)
	cle(anim, "Plans/Chaise:visible", P3, true)
	boucle(anim, "Plans/Chaise/Vapeur", P3, DUREE, [0, 1, 2], IMAGE_FUMEE)
	cle(anim, "Plans/Chaise:scale", 0.0, Vector2.ONE)
	cle(anim, "Plans/Chaise:position", 0.0, Vector2.ZERO)
	if not attenues:
		var n := roundi((DUREE - P3) / Cinematique.PAS)
		for k in n + 1:
			var u := float(k) / n
			var s := lerpf(1.0, POUSSEE, u * u * (3.0 - 2.0 * u))
			cle(anim, "Plans/Chaise:scale", P3 + k * Cinematique.PAS, Vector2.ONE * s)
			cle(anim, "Plans/Chaise:position", P3 + k * Cinematique.PAS, (BOL - BOL * s).round())
	cle(anim, "Plans:visible", DUREE, false)
	return anim


func _prendre_controle() -> void:
	super()
	var lieu := get_parent()
	emetteur = lieu.find_child(EMETTEUR, true, false) as AudioStreamPlayer2D if lieu != null else null
	if emetteur != null:
		emetteur.stream_paused = true


func apres() -> void:
	if couche != null:
		couche.visible = false
	if emetteur != null and is_instance_valid(emetteur):
		emetteur.stream_paused = false


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
