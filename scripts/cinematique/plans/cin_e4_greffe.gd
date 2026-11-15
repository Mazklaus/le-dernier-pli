extends CinematiquePlans
## e4_greffe (planches de la DA, tools/gen_cin_e4.py) : en ombre, hors champ, jamais l'œil ni la
## plaie. Deux plans plein écran à 10 i/s, séparés par un noir franc, sans texte.
## Plan A : les mains d'Anselme, la lampe (fond cin_greffe_01, 6 images de 1280×840 en
##          (320, 120)) : un temps sur l'image 0, puis 1 à 5, tenue sur la 5.
## Noir :   0,6 s, coupe franche (la fausse note du Sound Designer s'y cale).
## Plan B : la lampe qui s'éteint (fond cin_greffe_03, 4 images de 800×800 en (560, 140)) :
##          un temps sur l'image 0, puis 1 à 3, et un temps sur la lampe éteinte, le fil de
##          fumée, avant de rendre la main au dialogue.

const DOSSIER := "res://assets/graphics/cin/cin_greffe_%02d.png"
## Son calé sur le noir, s'il existe (bruitage du Sound Designer).
const SON_NOIR := "sfx_greffe_fausse-note"
const DEBUT_GESTE_A := 0.8
const TENUE_A := 0.4
const DUREE_NOIR := 0.6
const TENUE_DEBUT_B := 0.5
const TENUE_FIN_B := 2.1

var couche: CanvasLayer


func construire() -> Animation:
	var t: Array[Texture2D] = []
	for i in range(1, 5):
		t.append(planche(DOSSIER % i))
	if t.has(null):
		return null
	couche = couche_plein_ecran()
	var a := Node2D.new()
	a.name = "A"
	a.add_child(sprite("Fond", t[0], Vector2.ZERO))
	a.add_child(sprite("Geste", t[1], Vector2(320, 120), 2, 3))
	var noir := ColorRect.new()
	noir.name = "Noir"
	noir.color = StylePapier.ENCRE
	noir.position = Vector2(-1920, -1080)
	noir.size = Vector2(1920 * 3, 1080 * 3)  # couvre aussi un écran plus large que 16/9
	noir.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var b := Node2D.new()
	b.name = "B"
	b.add_child(sprite("Fond", t[2], Vector2.ZERO))
	b.add_child(sprite("Geste", t[3], Vector2(560, 140), 2, 2))
	couche.add_child(a)
	couche.add_child(noir)
	couche.add_child(b)

	var anim := Animation.new()
	cle(anim, "Plans:visible", 0.0, true)
	cle(anim, "Plans/A:visible", 0.0, true)
	cle(anim, "Plans/Noir:visible", 0.0, false)
	cle(anim, "Plans/B:visible", 0.0, false)
	cle(anim, "Plans/A/Geste:frame", 0.0, 0)
	var t_noir := images(anim, "Plans/A/Geste", DEBUT_GESTE_A, 1, 5) - Cinematique.PAS + TENUE_A
	cle(anim, "Plans/A:visible", t_noir, false)
	cle(anim, "Plans/Noir:visible", t_noir, true)
	if not AudioDirector.variantes_de(SON_NOIR).is_empty():
		son(anim, t_noir, SON_NOIR)
	var t_b := t_noir + DUREE_NOIR
	cle(anim, "Plans/Noir:visible", t_b, false)
	cle(anim, "Plans/B:visible", t_b, true)
	cle(anim, "Plans/B/Geste:frame", t_b, 0)
	var fin := images(anim, "Plans/B/Geste", t_b + TENUE_DEBUT_B, 1, 3) - Cinematique.PAS + TENUE_FIN_B
	anim.length = snappedf(fin, Cinematique.PAS)
	cle(anim, "Plans:visible", anim.length, false)
	return anim


func apres() -> void:
	if couche != null:
		couche.visible = false
