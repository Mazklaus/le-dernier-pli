extends CinematiquePlans
## e7_moule_brise (planche « Le Dernier Pli » de la DA, tools/gen_cin_e7_fin.py) : choix « Être
## le dernier » de e7_mere_cloche. Un gros plan sur la table de pierre : le moule à sceaux se fend,
## les mâchoires s'écartent, la cire noire coule et se fige. Fond cin_moule_01 (la table, la main
## ouverte de Tobie, le ruban), puis 6 images de 860×480 (cin_moule_02, grille 3 × 2) en (560, 480).
## Rien d'autre ne bouge, pas de caméra : la même en effets atténués. 8 s.

const FOND := "res://assets/graphics/cin/cin_moule_01.png"
const IMAGES := "res://assets/graphics/cin/cin_moule_02.png"
const ZONE := Vector2(560, 480)
## Durée de chaque image : fermé, fendu, écarté, la cire sort, coule, figée (tenue jusqu'à la fin).
const DUREES := [1.5, 0.8, 0.7, 0.6, 0.8, 3.6]
const SON_FENTE := "sfx_sceau_abimer"
const IMAGE_FENTE := 1

var couche: CanvasLayer


func construire() -> Animation:
	var fond := planche(FOND)
	var images_moule := planche(IMAGES)
	if fond == null or images_moule == null:
		return null
	couche = couche_plein_ecran()
	couche.add_child(sprite("Fond", fond, Vector2.ZERO))
	couche.add_child(sprite("Moule", images_moule, ZONE, 3, 2))

	var anim := Animation.new()
	cle(anim, "Plans:visible", 0.0, true)
	var t := 0.0
	for i in DUREES.size():
		cle(anim, "Plans/Moule:frame", t, i)
		if i == IMAGE_FENTE:
			son(anim, t, SON_FENTE)
		t += float(DUREES[i])
	anim.length = snappedf(t, Cinematique.PAS)
	cle(anim, "Plans:visible", anim.length, false)
	return anim


func apres() -> void:
	if couche != null:
		couche.visible = false
