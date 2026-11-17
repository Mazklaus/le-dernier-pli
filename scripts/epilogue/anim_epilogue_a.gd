extends AnimationEpilogue
## Épilogue « Le Battant » (lettre a, porteur). Planche de la DA validée par le GD le 17/11
## (direction-artistique/epilogues/planche_trois_fins.png) : 32 s, quatre plans, une ligne par
## plan. Images faites pour la ciné (tools/gen_cin_epilogue_battant.py), seule la gravure a est
## réemployée. Les fonds s'arrêtent à y 800, sous le bandeau du texte.

const CIN := "res://assets/graphics/cin/%s.png"
const DUREE := 32.0
const LIGNES: Array[float] = [0.5, 8.5, 16.5, 24.5]
## P1 : la corde pend de la bouche noire de la grande cloche (gravure a : bouche centrée en
## (960, 408)) ; son haut reste dans le noir, le jeu la balance à peine autour de ce point.
const CORDE_HAUT := Vector2(1010, 440)
const CORDE_LARGEUR := 40.0
const BALANCE_CORDE := 1.2
const PERIODE_CORDE := 3.2
const BOUCHE := Vector2(960, 420)
## P2 : la Longue Tranchée (2600 de large), panoramique ; une pelletée au-dessus de chaque casque
## (gen_cin_epilogue_battant.CASQUES), le pied de l'image (120, 250) au ras du parapet.
const PANORAMIQUE := -680.0
const CASQUES := [Vector2(420, 556), Vector2(1180, 548), Vector2(1900, 560), Vector2(2380, 552)]
const PIED_PELLETEE := Vector2(80, 250)
const IMAGE_PELLETEE := 0.3
## P3 : la tête du soldat (ZONE_SIFFLE), 3 images : il siffle, la larme vient, elle descend.
const ZONE_SIFFLE := Vector2(760, 160)
const VISAGE := Vector2(960, 330)
const LARME := 19.5
const LARME_JOUE := 21.5
## P4 : la Mère-Cloche, tête et mains (ZONE_LIRE, grille 3 × 2 : image = mains × 2 + lèvres) ;
## la lampe (ZONE_LAMPE, 3 images) se rallume.
const ZONE_LIRE := Vector2(700, 90)
const MAINS := [24.0, 26.0, 28.5]
const LEVRES_DEBUT := 24.6
const LEVRES_FIN := 30.0
const LEVRES_PAS := 0.4
const ZONE_LAMPE := Vector2(460, 370)
const LAMPE := [[24.0, 0], [26.5, 1], [26.8, 2], [28.0, 1], [28.2, 2]]
const FONDU := 30.0


func construire() -> Animation:
	var tex := {}
	for nom in ["cin_epilogue-a", "cin_epi-a-corde", "cin_epi-a-tranchee", "cin_epi-a-pelletee", "cin_epi-a-soldat",
			"cin_epi-a-siffle", "cin_epi-a-mere", "cin_epi-a-lire", "cin_epi-a-lampe"]:
		tex[nom] = planche(CIN % nom)
	for t: Variant in tex.values():
		if t == null:
			return null
	temps_lignes = LIGNES
	var anim := Animation.new()
	anim.length = DUREE

	# P1, 0 à 8 s : « On l'attacha dans la grande cloche… » La corde pend de la bouche noire ;
	# poussée lente vers elle.
	var p1 := plan(anim, "P1", 0.0, 8.0)
	var gravure := Node2D.new()
	gravure.name = "Gravure"
	p1.add_child(gravure)
	gravure.add_child(sprite("Fond", tex["cin_epilogue-a"], Vector2.ZERO))
	var corde := Node2D.new()
	corde.name = "Corde"
	corde.position = CORDE_HAUT
	gravure.add_child(corde)
	corde.add_child(sprite("Brin", tex["cin_epi-a-corde"], Vector2(-CORDE_LARGEUR / 2.0, 0.0)))
	pousser(anim, "Cadre/P1/Gravure", 0.0, 8.0, BOUCHE, 1.0, 1.15)
	if Reglages.valeur(&"effets_attenues"):
		cle(anim, "Cadre/P1/Gravure/Corde:rotation_degrees", 0.0, 0.0)
	else:
		var n := roundi(8.0 / PAS)
		for k in n + 1:
			var t := k * PAS
			cle(anim, "Cadre/P1/Gravure/Corde:rotation_degrees", t, snappedf(BALANCE_CORDE * sin(TAU * t / PERIODE_CORDE), 0.01))

	# P2, 8 à 16 s : « la Longue Tranchée continua de creuser. » Panoramique sur les parapets, la
	# terre jetée par-dessus, chacune à son rythme.
	var p2 := plan(anim, "P2", 8.0, 16.0)
	var vue := Node2D.new()
	vue.name = "Vue"
	p2.add_child(vue)
	vue.add_child(sprite("Fond", tex["cin_epi-a-tranchee"], Vector2.ZERO))
	for i in CASQUES.size():
		var c: Vector2 = CASQUES[i]
		vue.add_child(sprite("Pelletee%d" % i, tex["cin_epi-a-pelletee"], c - PIED_PELLETEE, 3, 1))
		var images := [0, 1, 2, -1, -1]
		for _r in i:
			images.push_front(images.pop_back())
		boucle_visible(anim, "Cadre/P2/Vue/Pelletee%d" % i, 8.0, 16.0, images, IMAGE_PELLETEE)
	mouvement(anim, "Cadre/P2/Vue:position", 8.0, 16.0, Vector2.ZERO, Vector2(PANORAMIQUE, 0.0))

	# P3, 16 à 24 s : « un soldat siffla l'air du dépôt, et ne sut pas pourquoi il pleurait. »
	var p3 := plan(anim, "P3", 16.0, 24.0)
	var soldat := Node2D.new()
	soldat.name = "Soldat"
	p3.add_child(soldat)
	soldat.add_child(sprite("Fond", tex["cin_epi-a-soldat"], Vector2.ZERO))
	soldat.add_child(sprite("Tete", tex["cin_epi-a-siffle"], ZONE_SIFFLE, 3, 1))
	cle(anim, "Cadre/P3/Soldat/Tete:frame", 16.0, 0)
	cle(anim, "Cadre/P3/Soldat/Tete:frame", LARME, 1)
	cle(anim, "Cadre/P3/Soldat/Tete:frame", LARME_JOUE, 2)
	pousser(anim, "Cadre/P3/Soldat", 16.0, 24.0, VISAGE, 1.0, 1.08)

	# P4, 24 à 32 s : « une vieille femme répétait des noms… » La Mère-Cloche, les yeux clos ; ses
	# doigts parcourent l'éclat et s'arrêtent sur le nom frais, ses lèvres bougent ; la lampe se
	# rallume ; puis le papier revient.
	var p4 := plan(anim, "P4", 24.0, DUREE)
	p4.add_child(sprite("Fond", tex["cin_epi-a-mere"], Vector2.ZERO))
	p4.add_child(sprite("Lire", tex["cin_epi-a-lire"], ZONE_LIRE, 3, 2))
	p4.add_child(sprite("Lampe", tex["cin_epi-a-lampe"], ZONE_LAMPE, 3, 1))
	var t := MAINS[0] as float
	while t < DUREE - 0.001:
		var mains := 0
		for m in MAINS.size():
			if t >= MAINS[m] - 0.001:
				mains = m
		var levres := 0
		if t >= LEVRES_DEBUT - 0.001 and t < LEVRES_FIN - 0.001:
			levres = 1 if roundi((t - LEVRES_DEBUT) / LEVRES_PAS) % 2 == 0 else 0
		cle(anim, "Cadre/P4/Lire:frame", snappedf(t, PAS), mains * 2 + levres)
		t += PAS * 2
	for l: Array in LAMPE:
		cle(anim, "Cadre/P4/Lampe:frame", l[0], l[1])
	var papier := ColorRect.new()
	papier.name = "Papier"
	papier.color = StylePapier.PAPIER
	papier.size = Vector2(1920, 1080)
	papier.mouse_filter = Control.MOUSE_FILTER_IGNORE
	p4.add_child(papier)
	cle(anim, "Cadre/P4/Papier:modulate", 24.0, Color(1, 1, 1, 0))
	for k in 21:
		cle(anim, "Cadre/P4/Papier:modulate", FONDU + k * PAS, Color(1, 1, 1, clampf((k - 1) / 18.0, 0.0, 1.0)))
	return anim


## Une boucle d'images où -1 cache le sprite (un temps de repos entre deux pelletées).
static func boucle_visible(anim: Animation, chemin: String, debut: float, fin: float, images: Array, duree_image: float) -> void:
	var t := debut
	var i := 0
	while t < fin - 0.001:
		var im: int = images[i % images.size()]
		cle(anim, chemin + ":visible", snappedf(t, PAS), im >= 0)
		if im >= 0:
			cle(anim, chemin + ":frame", snappedf(t, PAS), im)
		t += duree_image
		i += 1
