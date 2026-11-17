extends AnimationEpilogue
## Épilogue « La Remontée » (lettre e, recousu). Planche de la DA validée par le GD le 17/11 : 32 s,
## quatre plans, une ligne par plan. Images faites pour la ciné (tools/gen_cin_epilogue_remontee.py),
## seule la gravure e est réemployée. Décision du GD : le noir tombe pendant le sifflement, sur la
## dernière note, avant tout coup de feu ; rien ne montre le coup.

const CIN := "res://assets/graphics/cin/%s.png"
const DUREE := 32.0
const LIGNES: Array[float] = [0.5, 8.5, 16.5, 24.5]
## P1 : la galerie (1920 × 1300) monte le long de la rampe y = RAMPE0 + PENTE × x ; la caméra
## remonte avec la colonne (Vue de y -500 à 0). Les Enfouis sortent du noir à gauche et passent
## par le haut : on ne les compte pas. Tobie (la rangée 2 de la planche, le ruban) est le quatrième.
const RAMPE0 := 1180.0
const PENTE := -0.5
const MONTEE := -500.0
const DEPARTS := [-150.0, 90.0, 330.0, 570.0, 810.0, 1050.0, 1290.0, 1530.0, 1770.0]
const TOBIE := 3
const PAS_COLONNE := 300.0
const PIED := Vector2(120, 340)
const ECHELLE_ENFOUI := 1.2
const IMAGE_ENFOUI := 0.3
## P2 : les mains recousues (ZONE_MAINS, 2 images) : elles se ferment à demi, se rouvrent.
const ZONE_MAINS := Vector2(240, 0)
const FERMER := [[8.0, 0], [10.4, 1], [11.6, 0], [13.6, 1], [14.6, 0]]
## P3 : la gravure e, la terre qui glisse de la butte (ZONE_TERRE, 3 images).
const ZONE_TERRE := Vector2(640, 240)
const SILHOUETTE := Vector2(1040, 260)
## P4 : le soldat de face (ZONE_EPAULER, grille 3 × 2 : image = pose × 2 + lèvres). Il épaule à
## POSES, siffle (les lèvres changent tous les LEVRES_PAS), et le noir tombe à NOIR, net.
const ZONE_EPAULER := Vector2(540, 40)
const POSES := [24.0, 26.4, 28.0]
const LEVRES_PAS := 0.4
const NOIR := 30.0
const VISAGE := Vector2(960, 330)


func construire() -> Animation:
	var tex := {}
	for nom in ["cin_epi-e-galerie", "cin_epi-e-enfoui", "cin_epi-e-mains", "cin_epi-e-fermer", "cin_epilogue-e",
			"cin_epi-e-terre", "cin_epi-e-matin", "cin_epi-e-epauler"]:
		tex[nom] = planche(CIN % nom)
	for t: Variant in tex.values():
		if t == null:
			return null
	temps_lignes = LIGNES
	var anim := Animation.new()
	anim.length = DUREE

	# P1, 0 à 8 s : « Il remonta. Lentement, par les galeries, avec les autres. »
	var p1 := plan(anim, "P1", 0.0, 8.0)
	var vue := Node2D.new()
	vue.name = "Vue"
	p1.add_child(vue)
	vue.add_child(sprite("Fond", tex["cin_epi-e-galerie"], Vector2.ZERO))
	var n := roundi(8.0 / PAS)
	for i in DEPARTS.size():
		var e := Sprite2D.new()
		e.name = "Enfoui%d" % i
		e.texture = tex["cin_epi-e-enfoui"]
		e.hframes = 4
		e.vframes = 2
		e.centered = false
		e.offset = -PIED
		e.scale = Vector2.ONE * ECHELLE_ENFOUI
		e.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		vue.add_child(e)
		var rangee := 4 if i == TOBIE else 0
		for k in n + 1:
			var t := k * PAS
			var x: float = DEPARTS[i] + PAS_COLONNE * float(k) / n
			var chemin := "Cadre/P1/Vue/Enfoui%d" % i
			cle(anim, chemin + ":position", snappedf(t, PAS), Vector2(roundf(x), roundf(RAMPE0 + PENTE * x)))
			cle(anim, chemin + ":frame", snappedf(t, PAS), rangee + (floori(t / IMAGE_ENFOUI + 0.001) + i * 3) % 4)
	mouvement(anim, "Cadre/P1/Vue:position", 0.0, 8.0, Vector2(0.0, MONTEE), Vector2.ZERO)
	# la galerie est plus haute que l'écran : sous le bandeau, le papier (comme les autres fonds)
	var bas := ColorRect.new()
	bas.name = "Bas"
	bas.color = StylePapier.PAPIER
	bas.position = Vector2(0, 800)
	bas.size = Vector2(1920, 280)
	bas.mouse_filter = Control.MOUSE_FILTER_IGNORE
	p1.add_child(bas)

	# P2, 8 à 16 s : « Il ne se souvenait d'aucun nom. Ses mains ne faisaient plus mal. »
	var p2 := plan(anim, "P2", 8.0, 16.0)
	var mains := Node2D.new()
	mains.name = "Mains"
	p2.add_child(mains)
	mains.add_child(sprite("Fond", tex["cin_epi-e-mains"], Vector2.ZERO))
	mains.add_child(sprite("Fermer", tex["cin_epi-e-fermer"], ZONE_MAINS, 2, 1))
	for f: Array in FERMER:
		cle(anim, "Cadre/P2/Mains/Fermer:frame", f[0], f[1])
	pousser(anim, "Cadre/P2/Mains", 8.0, 16.0, Vector2(960, 360), 1.0, 1.06)

	# P3, 16 à 24 s : « Un matin, il sortit de terre devant une tranchée qu'il croyait reconnaître. »
	var p3 := plan(anim, "P3", 16.0, 24.0)
	var gravure := Node2D.new()
	gravure.name = "Gravure"
	p3.add_child(gravure)
	gravure.add_child(sprite("Fond", tex["cin_epilogue-e"], Vector2.ZERO))
	gravure.add_child(sprite("Terre", tex["cin_epi-e-terre"], ZONE_TERRE, 3, 1))
	boucle(anim, "Cadre/P3/Gravure/Terre", 16.0, 24.0, [0, 1, 2], 0.3)
	pousser(anim, "Cadre/P3/Gravure", 16.0, 24.0, SILHOUETTE, 1.0, 1.12)

	# P4, 24 à 32 s : « Un soldat leva son fusil. Il sifflait un air, entre ses dents. » Il épaule,
	# vise, siffle ; le noir tombe d'un coup sur la dernière note, et reste.
	var p4 := plan(anim, "P4", 24.0, DUREE)
	var face := Node2D.new()
	face.name = "Face"
	p4.add_child(face)
	face.add_child(sprite("Fond", tex["cin_epi-e-matin"], Vector2.ZERO))
	face.add_child(sprite("Soldat", tex["cin_epi-e-epauler"], ZONE_EPAULER, 3, 2))
	var t := POSES[0] as float
	while t < NOIR - 0.001:
		var pose := 0
		for p in POSES.size():
			if t >= POSES[p] - 0.001:
				pose = p
		var levres := roundi((t - POSES[0]) / LEVRES_PAS) % 2
		cle(anim, "Cadre/P4/Face/Soldat:frame", snappedf(t, PAS), pose * 2 + levres)
		t += LEVRES_PAS
	pousser(anim, "Cadre/P4/Face", 24.0, NOIR, VISAGE, 1.0, 1.1)
	var noir := ColorRect.new()
	noir.name = "Noir"
	noir.color = StylePapier.ENCRE
	noir.size = Vector2(1920, 1080)
	noir.mouse_filter = Control.MOUSE_FILTER_IGNORE
	noir.visible = false
	p4.add_child(noir)
	cle(anim, "Cadre/P4/Noir:visible", 24.0, false)
	cle(anim, "Cadre/P4/Noir:visible", NOIR, true)
	return anim
