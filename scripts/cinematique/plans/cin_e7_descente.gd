extends CinematiquePlans
## e7_descente (planches de la DA, tools/gen_cin_e7.py) : au début de e7_cloches, Tobie descend
## l'escalier qui tourne autour de la plus grande cloche. Aucune cloche ne bouge. Quatre plans :
## 1 (0 à 2,4 s)   en haut, la couronne de la grande cloche (cin_descente_01) ;
## 2 (2,4 à 5,4 s) le flanc, plus près : la caméra descend avec Tobie, le fond (cin_descente_02)
##                 monte de PAN px, l'avant-plan transparent (cin_descente_03) deux fois plus ;
##                 Tobie est dessiné entre les deux (il passe derrière les cloches proches) ;
## 3 (5,4 à 7,4 s) gros plan immobile sur la cire figée (cin_descente_04) ;
## 4 (7,4 à 10 s)  en bas, l'escalier mangé par le blanc (cin_descente_05).
## Tobie : cin_descente_06, 4 images de 120×200 en ligne, pieds en (60, 196), de profil vers la
## droite, sans retournement ; mis à l'échelle par plan et posé par ses pieds sur les clés de la
## DA (image -1 : caché derrière la grande cloche). Caché avant sa première clé.

const DOSSIER := "res://assets/graphics/cin/cin_descente_%02d.png"
const PIEDS := Vector2(60, 196)
const DEBUTS := {1: 0.0, 2: 2.4, 3: 5.4, 4: 7.4}
const FIN := 10.0
const ECHELLES := {1: 0.55, 2: 1.0, 4: 0.35}
const PAN := 410.0
const PAN_DEBUT := 0.1
const PAN_FIN := 2.7
## Clés de Tobie par plan : (instant depuis le début du plan, image, pieds x, pieds y). Plan 2 :
## en coordonnées du fond qui monte (Tobie y est accroché).
const CHEMINS := {
	1: [
		[0.6, 0, 980, 400], [0.8, 1, 1085, 413], [1.0, 2, 1184, 425], [1.2, 3, 1274, 438],
		[1.4, 0, 1350, 450], [1.6, 1, 1408, 463], [1.8, 2, 1445, 476], [2.0, 3, 1460, 488],
		[2.2, -1, 0, 0],
	],
	2: [
		[0.1, 0, 305, 560], [0.3, 1, 339, 592], [0.5, 2, 403, 623], [0.7, 3, 494, 655],
		[0.9, 0, 608, 686], [1.1, 1, 738, 718], [1.3, 2, 879, 749], [1.5, 3, 1024, 781],
		[1.7, 0, 1166, 812], [1.9, 1, 1298, 844], [2.1, 2, 1413, 875], [2.3, 3, 1507, 907],
		[2.5, 0, 1574, 938], [2.7, 1, 1612, 970],
	],
	4: [
		[0.3, 0, 662, 585], [0.5, 1, 678, 593], [0.7, 2, 707, 602], [0.9, 3, 748, 610],
		[1.1, 0, 800, 618], [1.3, 1, 859, 627], [1.5, 2, 923, 635], [1.7, 3, 989, 644],
		[1.9, 0, 1053, 652], [2.1, 1, 1113, 661], [2.3, 2, 1166, 669], [2.5, 3, 1209, 677],
	],
}

var couche: CanvasLayer


func construire() -> Animation:
	var t: Array[Texture2D] = []
	for i in range(1, 7):
		t.append(planche(DOSSIER % i))
	if t.has(null):
		return null
	couche = couche_plein_ecran()
	for p in [1, 2, 3, 4]:
		var plan := Node2D.new()
		plan.name = "P%d" % p
		couche.add_child(plan)
	var fonds := {1: t[0], 2: t[1], 3: t[3], 4: t[4]}
	for p: int in fonds:
		couche.get_node("P%d" % p).add_child(sprite("Fond", fonds[p], Vector2.ZERO))
	# Tobie du plan 2 accroché au fond qui monte ; l'avant-plan par-dessus.
	couche.get_node("P1").add_child(tobie(t[5], ECHELLES[1]))
	couche.get_node("P2/Fond").add_child(tobie(t[5], ECHELLES[2]))
	couche.get_node("P2").add_child(sprite("AvantPlan", t[2], Vector2.ZERO))
	couche.get_node("P4").add_child(tobie(t[5], ECHELLES[4]))

	var anim := Animation.new()
	cle(anim, "Plans:visible", 0.0, true)
	for p: int in DEBUTS:
		for q: int in DEBUTS:
			cle(anim, "Plans/P%d:visible" % q, DEBUTS[p], q == p)
	_pan(anim)
	_chemin(anim, "Plans/P1/Tobie", 1)
	_chemin(anim, "Plans/P2/Fond/Tobie", 2)
	_chemin(anim, "Plans/P4/Tobie", 4)
	anim.length = FIN
	cle(anim, "Plans:visible", FIN, false)
	return anim


## Sprite de Tobie posé par ses pieds (l'échelle se fait autour d'eux), caché au départ.
static func tobie(texture: Texture2D, echelle: float) -> Sprite2D:
	var s := sprite("Tobie", texture, Vector2.ZERO, 4, 1)
	s.offset = -PIEDS
	s.scale = Vector2.ONE * echelle
	s.visible = false
	return s


## Le pan du plan 2 : le fond monte de PAN px et l'avant-plan de 2 × PAN, linéairement de
## PAN_DEBUT à PAN_FIN, une clé par pas.
func _pan(anim: Animation) -> void:
	var debut: float = DEBUTS[2]
	var pas := roundi((PAN_FIN - PAN_DEBUT) / Cinematique.PAS)
	for k in pas + 1:
		var avance := float(k) / pas
		var instant := debut + PAN_DEBUT + k * Cinematique.PAS
		cle(anim, "Plans/P2/Fond:position", instant, Vector2(0, roundf(-PAN * avance)))
		cle(anim, "Plans/P2/AvantPlan:position", instant, Vector2(0, roundf(-2.0 * PAN * avance)))
	cle(anim, "Plans/P2/Fond:position", debut, Vector2.ZERO)
	cle(anim, "Plans/P2/AvantPlan:position", debut, Vector2.ZERO)


## Les clés de Tobie dans un plan : caché au début du plan, puis image et pieds à chaque clé.
func _chemin(anim: Animation, chemin: String, plan: int) -> void:
	var debut: float = DEBUTS[plan]
	cle(anim, chemin + ":visible", debut, false)
	for etape: Array in CHEMINS[plan]:
		var instant: float = debut + float(etape[0])
		var image: int = etape[1]
		cle(anim, chemin + ":visible", instant, image >= 0)
		if image >= 0:
			cle(anim, chemin + ":frame", instant, image)
			cle(anim, chemin + ":position", instant, Vector2(etape[2], etape[3]))


func apres() -> void:
	if couche != null:
		couche.visible = false
