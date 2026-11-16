extends CinematiquePlans
## e6_eboulement (retouche du GD) : à l'entrée du village, la voûte de la galerie d'où vient
## Tobie cède derrière lui. Un seul plan plein écran, dessiné (tools/gen_cin_e6_eboulement.py) :
## le village à l'échelle du jeu (cin_eboulement_01), et 8 images de la zone de la galerie
## (cin_eboulement_02, grille 3 × 3, rendues à l'échelle 0,75) : des graviers tombent, Tobie
## lève la tête ; la voûte se fend, l'étai plie ; elle cède, Tobie se jette en avant ; la
## poussière couvre tout, retombe lentement, et laisse l'éboulis (celui du calque
## fx_eboule-village, qui reste ensuite dans le décor). Environ 6 s.
## Pas de mouvement de caméra : la ciné est la même en effets atténués. Le plan cache aussi la
## caméra du jeu (ni la bande grise sous le sol, ni la maquette ne peuvent se voir).

const DOSSIER := "res://assets/graphics/cin/cin_eboulement_%02d.png"
## Coin haut-gauche de la zone dessinée dans l'écran, et l'échelle du rendu des images.
const ZONE := Vector2(360, 260)
const ECHELLE := 0.75
## Durée de chaque image (gen_cin_e6_eboulement.TEMPS).
const TEMPS: Array[float] = [0.6, 0.8, 0.3, 0.2, 0.3, 1.2, 1.2, 1.4]
const SON_GRAVIERS := "sfx_terre_ebouler"
const SON_VOUTE := "sfx_voute_effondrer"
## L'image où la voûte cède.
const IMAGE_CHUTE := 3

var couche: CanvasLayer


func construire() -> Animation:
	var fond := planche(DOSSIER % 1)
	var bande := planche(DOSSIER % 2)
	if fond == null or bande == null:
		return null
	couche = couche_plein_ecran()
	couche.add_child(sprite("Fond", fond, Vector2.ZERO))
	var voute := sprite("Voute", bande, ZONE, 3, 3)
	voute.scale = Vector2.ONE / ECHELLE
	couche.add_child(voute)

	var anim := Animation.new()
	cle(anim, "Plans:visible", 0.0, true)
	var t := 0.0
	for k in TEMPS.size():
		cle(anim, "Plans/Voute:frame", t, k)
		if k == 0:
			son(anim, t, SON_GRAVIERS)
		elif k == IMAGE_CHUTE:
			son(anim, t, SON_VOUTE)
		t += TEMPS[k]
	anim.length = snappedf(t, Cinematique.PAS)
	cle(anim, "Plans:visible", anim.length, false)
	return anim


func apres() -> void:
	if couche != null:
		couche.visible = false
