extends CinematiquePlans
## e7_corde_tiree (planche « Le Dernier Pli » de la DA, tools/gen_cin_e7_fin.py) : « Je tire. »
## dans e7_mere_cloche. Le même gros plan que e7_moule_brise, sans la main ouverte (fond
## cin_corde_01), le moule encore fermé (image 0 de cin_moule_02) : la corde de la grande cloche tombe en diagonale ; la main de
## Tobie la prend, tire deux fois ; noir sec AVANT le son (la première sonnerie du jeu appartient à
## l'épilogue « cloches », décision du GD). 6 s.
## La corde (cin_corde_02) et la main (cin_corde_03) sont dans le repère de la corde : axe y le long
## de la corde, prise en (0, 0) ; le nœud Prise les pose et les tourne. Tirer = faire glisser la
## Prise le long de la corde, vers le bas : un mouvement d'objet, pas de caméra (même en atténué).

const FOND := "res://assets/graphics/cin/cin_corde_01.png"
const MOULE := "res://assets/graphics/cin/cin_moule_02.png"
const CORDE := "res://assets/graphics/cin/cin_corde_02.png"
const MAIN := "res://assets/graphics/cin/cin_corde_03.png"
const ZONE_MOULE := Vector2(560, 480)
## La prise à l'écran et l'angle de la corde (gen_cin_e7_fin.py l'affiche à la génération).
const PRISE := Vector2(598, 876)
const ANGLE := 54.70
## L'origine du repère de la corde dans la planche de la main (boîte -900, -160 à l'échelle 1,5).
const ORIGINE_MAIN := Vector2(1350, 240)
## La main entre par la gauche (le long de son bras), en trois images.
const ENTREE := [Vector2(-150, 0), Vector2(-70, 0), Vector2(-20, 0), Vector2.ZERO]
const T_ENTREE := 0.6
## Deux tractions : la prise descend le long de la corde, image par image (px), puis tient.
const TRACTIONS := [[2.0, [14.0, 30.0, 42.0]], [3.2, [56.0, 74.0, 84.0]]]
const T_NOIR := 4.5
const DUREE := 6.0
const SON_CORDE := "sfx_corde_tirer"

var couche: CanvasLayer


func construire() -> Animation:
	var fond := planche(FOND)
	var moule := planche(MOULE)
	var corde := planche(CORDE)
	var main := planche(MAIN)
	if fond == null or moule == null or corde == null or main == null:
		return null
	couche = couche_plein_ecran()
	couche.add_child(sprite("Fond", fond, Vector2.ZERO))
	var m := sprite("Moule", moule, ZONE_MOULE, 3, 2)
	m.frame = 0
	couche.add_child(m)
	var prise := Node2D.new()
	prise.name = "Prise"
	prise.position = PRISE
	prise.rotation_degrees = ANGLE
	couche.add_child(prise)
	var s_corde := Sprite2D.new()
	s_corde.name = "Corde"
	s_corde.texture = corde
	s_corde.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	prise.add_child(s_corde)
	var s_main := sprite("Main", main, -ORIGINE_MAIN)
	prise.add_child(s_main)
	var noir := ColorRect.new()
	noir.name = "Noir"
	noir.color = StylePapier.ENCRE
	# déborde largement : en aspect « expand », l'écran peut être plus large que 1920
	noir.position = Vector2(-2000, -1000)
	noir.size = Vector2(5920, 3080)
	noir.mouse_filter = Control.MOUSE_FILTER_IGNORE
	couche.add_child(noir)

	var anim := Animation.new()
	anim.length = DUREE
	cle(anim, "Plans:visible", 0.0, true)
	cle(anim, "Plans/Noir:visible", 0.0, false)
	cle(anim, "Plans/Prise:position", 0.0, PRISE)
	cle(anim, "Plans/Prise/Main:visible", 0.0, false)
	cle(anim, "Plans/Prise/Main:visible", T_ENTREE, true)
	for i in ENTREE.size():
		cle(anim, "Plans/Prise/Main:position", T_ENTREE + i * Cinematique.PAS, -ORIGINE_MAIN + ENTREE[i])
	var le_long := Vector2.DOWN.rotated(deg_to_rad(ANGLE))
	for traction: Array in TRACTIONS:
		var t0: float = traction[0]
		son(anim, t0, SON_CORDE)
		var pas: Array = traction[1]
		for i in pas.size():
			cle(anim, "Plans/Prise:position", t0 + i * Cinematique.PAS, (PRISE + le_long * float(pas[i])).round())
	cle(anim, "Plans/Noir:visible", T_NOIR, true)
	cle(anim, "Plans:visible", DUREE, false)
	return anim


func apres() -> void:
	if couche != null:
		couche.visible = false
