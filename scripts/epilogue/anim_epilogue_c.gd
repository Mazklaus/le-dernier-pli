extends AnimationEpilogue
## Épilogue « Le Dernier Pli », les cloches (lettre c). Planche de la DA validée par le GD le 17/11 :
## 36 s, quatre plans. C'est la seule sonnerie du jeu : la règle « aucune cloche ne bouge » est
## payée ici (GD). P1 : la grande cloche se balance (3 positions en aller-retour), la poussière
## tombe de la couronne, les ondes ; trois petites cloches perdent leur bouchon de cire et frémissent.
## P2 : le son monte, un travelling vertical sur quatre décors (galeries, forêt, le village d'Ilde
## avec son clocher vide, la tranchée). P3 : la main reste serrée, la corde va et vient seule.
## P4 : Lamarre lève la tête (réemploi de e1_sortie_tranchee : le jeu se referme sur sa première
## ciné). Nouveau : tools/gen_cin_epilogues_anim.py ; corde et main : tools/gen_cin_e7_fin.py.

const CIN := "res://assets/graphics/cin/%s.png"
const ENV := "res://assets/graphics/env/%s.png"
const DUREE := 36.0
const LIGNES: Array[float] = [0.5, 8.5, 18.5, 26.5]
## P1. La grande cloche (calque 900 de large, couronne en (450, 140)), pendue en PIVOT, à 0,75.
const PIVOT := Vector2(960, -40)
const ECHELLE_GRANDE := 0.75
const ORIGINE_GRANDE := Vector2(450, 0)
## Le balancement : 3 positions ; la grande cloche frappe à chaque extrémité (grille du Sound
## Designer : 0,0 / 1,8 / 3,6 / 5,4 / 7,2 s), l'image d'extrémité est tenue autour du choc.
const BALANCE := 5.0
const DEMI_PERIODE := 1.8
const LEVRE_Y := 725.0
## Les petites cloches libérées (gen_cin_epilogues_anim.PETITES : x, y du haut) et l'instant où
## leur bouchon tombe ; case de 240 × 300, la corde à (120, 0).
const PETITES := [Vector2(300, 300), Vector2(1560, 220), Vector2(1700, 520)]
## Grille du Sound Designer : le bouchon claque (CLAQUE), tombe 0,4 s plus tard, la petite cloche
## sonne 0,3 s après (elle frémit alors).
const CLAQUE := [2.6, 4.4, 6.0]
const LEVRE_PETITE := [183.0, 165.0, 201.0]
## P2. Les décors, de haut en bas, et la bande de terre entre eux.
const TERRE := 120.0
## Ce qu'on montre de chaque bloc (décalage sous son haut, pour une vue de 790 px) : la tranchée
## et ses sacs en bas, le clocher vide, les croix, les cloches de la galerie.
const CADRAGE := [290.0, 60.0, 200.0, 0.0]
## Départs des trois montées (s).
const PALIERS := [10.0, 12.5, 15.0]
## P3. La corde (gen_cin_e7_fin) : prise à l'écran et angle, remontée sous le bandeau.
const PRISE := Vector2(598, 876)
const ANGLE := 54.70
const ORIGINE_MAIN := Vector2(1350, 240)
const MONTEE_CORDE := -300.0
## La corde tire au plus bas à chaque coup de la cloche (piste du Sound Designer, #212) : les
## allers-retours ralentissent ; après le dernier, un aller-retour de plus, qui s'éteint.
const COUPS_CORDE := [18.0, 19.9, 22.0, 24.4, 27.0]


func construire() -> Animation:
	var noms := ["cin_epi-c-campanile", "cin_epi-c-grande", "cin_epi-c-petites", "cin_epi-c-bouchon",
			"cin_epi-c-poussiere", "cin_epi-c-ondes", "cin_corde_01", "cin_corde_02", "cin_corde_03",
			"cin_moule_02", "cin_sortie_03", "cin_sortie_04"]
	var tex := {}
	for nom: String in noms:
		tex[nom] = planche(CIN % nom)
	for nom: String in ["e1/env_e1_plan3_surface_01", "e3/env_e3_plan3_surface_04", "e5/env_e5_plan3_cimetiere_01", "e7/env_e7_plan3_galerie_01"]:
		tex[nom] = planche(ENV % nom)
	for t: Variant in tex.values():
		if t == null:
			return null
	temps_lignes = LIGNES
	var anim := Animation.new()
	anim.length = DUREE
	_plan_cloche(anim, tex)
	_plan_montee(anim, tex)
	_plan_corde(anim, tex)
	_plan_lamarre(anim, tex)
	return anim


## P1, 0 à 8 s : « Toutes les cloches sonnèrent à la fois… »
func _plan_cloche(anim: Animation, tex: Dictionary) -> void:
	var p := plan(anim, "P1", 0.0, 8.0)
	p.add_child(sprite("Fond", tex["cin_epi-c-campanile"], Vector2.ZERO))
	for i in PETITES.size():
		var pivot := Node2D.new()
		pivot.name = "Petite%d" % i
		pivot.position = PETITES[i] + Vector2(0, -30)
		p.add_child(pivot)
		var s := sprite("Cloche", tex["cin_epi-c-petites"], Vector2(-120, 0), 2, 3)
		s.frame = i * 2
		pivot.add_child(s)
		var b := sprite("Bouchon", tex["cin_epi-c-bouchon"], PETITES[i] + Vector2(-45, LEVRE_PETITE[i] - 30))
		b.visible = false
		p.add_child(b)
		var claque: float = CLAQUE[i]
		var t0 := claque + 0.4
		cle(anim, "Cadre/P1/Petite%d:rotation_degrees" % i, 0.0, 0.0)
		cle(anim, "Cadre/P1/Petite%d:rotation_degrees" % i, claque, 1.0)
		cle(anim, "Cadre/P1/Petite%d:rotation_degrees" % i, claque + PAS, 0.0)
		cle(anim, "Cadre/P1/Petite%d/Cloche:frame" % i, 0.0, i * 2)
		cle(anim, "Cadre/P1/Petite%d/Cloche:frame" % i, t0, i * 2 + 1)
		# le bouchon tombe, de plus en plus vite, et sort de l'écran
		b.name = "Bouchon%d" % i
		var depart: Vector2 = b.position
		cle(anim, "Cadre/P1/Bouchon%d:visible" % i, 0.0, false)
		cle(anim, "Cadre/P1/Bouchon%d:visible" % i, t0, true)
		for k in 12:
			cle(anim, "Cadre/P1/Bouchon%d:position" % i, t0 + k * PAS, (depart + Vector2(k * 2.0, 9.0 * k * k)).round())
		cle(anim, "Cadre/P1/Bouchon%d:visible" % i, t0 + 1.2, false)
		# elle frémit, sans balancer
		var t := t0 + 0.3
		var sens := 1.0
		while t < 8.0:
			cle(anim, "Cadre/P1/Petite%d:rotation_degrees" % i, snappedf(t, PAS), 1.5 * sens)
			sens = -sens
			t += 0.2
	var grande := Node2D.new()
	grande.name = "Grande"
	grande.position = PIVOT
	grande.scale = Vector2(ECHELLE_GRANDE, ECHELLE_GRANDE)
	p.add_child(grande)
	grande.add_child(sprite("Cloche", tex["cin_epi-c-grande"], -ORIGINE_GRANDE))
	var choc := 0.0
	var cote := 1.0
	while choc < 8.0:
		cle(anim, "Cadre/P1/Grande:rotation_degrees", maxf(0.0, choc - 0.6), BALANCE * cote)
		cle(anim, "Cadre/P1/Grande:rotation_degrees", choc + 0.6, 0.0)
		choc += DEMI_PERIODE
		cote = -cote
	var poussiere := sprite("Poussiere", tex["cin_epi-c-poussiere"], Vector2(960 - 450, 40), 3, 1)
	p.add_child(poussiere)
	boucle(anim, "Cadre/P1/Poussiere", 0.0, 8.0, [0, 1, 2], 0.2)
	var ondes := sprite("Ondes", tex["cin_epi-c-ondes"], Vector2(0, LEVRE_Y - 840.0), 1, 2)
	ondes.scale = Vector2(2, 2)
	p.add_child(ondes)
	boucle(anim, "Cadre/P1/Ondes", 0.0, 8.0, [0, 1], 0.3)


## P2, 8 à 18 s : « Le son monta par les galeries, par la forêt, par les champs d'Ilde, jusqu'à
## la tranchée. » De bas en haut ; les ondes restent à l'écran.
func _plan_montee(anim: Animation, tex: Dictionary) -> void:
	var p := plan(anim, "P2", 8.0, 18.0)
	var colonne := Node2D.new()
	colonne.name = "Colonne"
	p.add_child(colonne)
	# du haut (la tranchée) au bas (les galeries), chacun à la largeur de l'écran
	var blocs := [["e1/env_e1_plan3_surface_01", 1080.0], ["e3/env_e3_plan3_surface_04", 0.0],
			["e5/env_e5_plan3_cimetiere_01", 0.0], ["e7/env_e7_plan3_galerie_01", 0.0]]
	var y := 0.0
	var hauts: Array[float] = []
	for i in blocs.size():
		var t: Texture2D = tex[blocs[i][0]]
		var echelle := 1920.0 / t.get_width() if t.get_width() < 1920 else 1.0
		var haut := t.get_height() * echelle
		var bloc_h: float = maxf(float(blocs[i][1]), haut)
		hauts.append(y)
		var fond := ColorRect.new()
		fond.color = StylePapier.PAPIER
		fond.position = Vector2(0, y)
		fond.size = Vector2(1920, bloc_h)
		fond.mouse_filter = Control.MOUSE_FILTER_IGNORE
		colonne.add_child(fond)
		var s := sprite("Decor%d" % i, t, Vector2(0, y + bloc_h - haut))
		s.scale = Vector2(echelle, echelle)
		colonne.add_child(s)
		y += bloc_h
		if i < blocs.size() - 1:
			var terre := ColorRect.new()
			terre.color = StylePapier.LAVIS
			terre.position = Vector2(0, y)
			terre.size = Vector2(1920, TERRE)
			terre.mouse_filter = Control.MOUSE_FILTER_IGNORE
			colonne.add_child(terre)
			y += TERRE
	# un palier par décor, calé sur la grille du son (galeries 8 à 10,5 s, forêt à 13, champs
	# d'Ilde à 15,5, tranchée à 18) ; on monte d'un décor à l'autre en 1 s
	var vues := []   # position de la colonne qui montre chaque bloc, du bas vers le haut
	for i in [3, 2, 1, 0]:
		vues.append(Vector2(0, -(hauts[i] + float(CADRAGE[i]))))
	var t := 8.0
	cle(anim, "Cadre/P2/Colonne:position", t, vues[0])
	for i in range(1, vues.size()):
		mouvement(anim, "Cadre/P2/Colonne:position", PALIERS[i - 1], PALIERS[i - 1] + 1.0, vues[i - 1], vues[i])
	var ondes := sprite("Ondes", tex["cin_epi-c-ondes"], Vector2(0, 0), 1, 2)
	ondes.scale = Vector2(2, 2)
	p.add_child(ondes)
	boucle(anim, "Cadre/P2/Ondes", 8.0, 18.0, [0, 1], 0.3)


## Où en est la corde à l'instant t : 1 au plus bas (un coup), -1 au plus haut, entre deux coups.
static func tirage(t: float) -> float:
	for i in COUPS_CORDE.size() - 1:
		var a: float = COUPS_CORDE[i]
		var b: float = COUPS_CORDE[i + 1]
		if t <= b:
			return cos(TAU * clampf((t - a) / (b - a), 0.0, 1.0))
	return 1.0


## P3, 18 à 26 s : « Il mourut dessous, la corde dans les mains. » La corde va et vient seule.
func _plan_corde(anim: Animation, tex: Dictionary) -> void:
	var p := plan(anim, "P3", 18.0, 26.0)
	p.position = Vector2(0, MONTEE_CORDE)
	p.add_child(sprite("Fond", tex["cin_corde_01"], Vector2.ZERO))
	var m := sprite("Moule", tex["cin_moule_02"], Vector2(560, 480), 3, 2)
	m.frame = 0
	p.add_child(m)
	var prise := Node2D.new()
	prise.name = "Prise"
	prise.position = PRISE
	prise.rotation_degrees = ANGLE
	p.add_child(prise)
	var corde := Sprite2D.new()
	corde.name = "Corde"
	corde.texture = tex["cin_corde_02"]
	corde.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	prise.add_child(corde)
	prise.add_child(sprite("Main", tex["cin_corde_03"], -ORIGINE_MAIN))
	var le_long := Vector2.DOWN.rotated(deg_to_rad(ANGLE))
	var n := roundi(8.0 / PAS)
	for k in n + 1:
		var t := 18.0 + k * PAS
		cle(anim, "Cadre/P3/Prise:position", t, (PRISE + le_long * lerpf(18.0, 3.0, (t - 18.0) / 8.0) * tirage(t)).round())
	var poussiere := sprite("Poussiere", tex["cin_epi-c-poussiere"], Vector2(1100, 300), 3, 1)
	p.add_child(poussiere)
	boucle(anim, "Cadre/P3/Poussiere", 18.0, 26.0, [0, 1, 2], 0.2)


## P4, 26 à 36 s : « Là-haut, on leva la tête. » Lamarre, tête basse, puis il la lève.
func _plan_lamarre(anim: Animation, tex: Dictionary) -> void:
	var p := plan(anim, "P4", 26.0, DUREE)
	p.add_child(sprite("Fond", tex["cin_sortie_03"], Vector2.ZERO))
	p.add_child(sprite("Lamarre", tex["cin_sortie_04"], Vector2(640, 60), 2, 1))
	cle(anim, "Cadre/P4/Lamarre:frame", 0.0, 1)
	cle(anim, "Cadre/P4/Lamarre:frame", 28.0, 0)
