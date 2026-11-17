extends CinematiquePlans
## e3_procession_nuit (planches de la DA, tools/gen_cin_e3.py) : depuis la chambre, entre les
## lames du volet, la procession passe dans la rue noire, cierges à deux mains, Ilde en tête.
## Trois calques plein écran, de l'arrière vers l'avant : la rue (cin_procession-nuit_01),
## la file qui marche vers la droite (pieds à y 820, échelle 1,3 ; Ilde puis les silhouettes
## de la procession, déphasées), le volet aux jours transparents (cin_procession-nuit_02).
## Tout est peint de nuit : l'écran gravure prend la teinte du chemin de nuit le temps de la
## cinématique (celle de la chambre éteindrait les flammes), puis reprend la sienne.

const RUE := "res://assets/graphics/cin/cin_procession-nuit_01.png"
const VOLET := "res://assets/graphics/cin/cin_procession-nuit_02.png"
const ILDE := "res://assets/graphics/chr/chr_ilde-cierge_marche_01.png"
const FILE := "res://assets/graphics/chr/chr_procession_marche_01.png"
const SOL := 820.0
const ECHELLE := 1.3
const NB_SUIVANTS := 5
const ECART := 200.0
## Ilde part derrière le mur, à gauche de l'embrasure (x 360 à 1560), et sort à droite.
const X_DEPART := 160.0
## Un marcheur n'existe qu'entre les lames : caché dès qu'il est entièrement derrière le mur
## (demi-largeur 100 × ECHELLE de part et d'autre des pieds). Sinon, sur un écran plus large
## que 16:9 (aspect « expand »), la file déborderait à droite et à gauche du cadre du volet.
const EMBRASURE := Vector2(360.0, 1560.0)
const VITESSE := 200.0
## Une image de marche toutes les 3 tics, comme la respiration des personnages.
const DUREE_IMAGE := 0.3
const DUREE := 10.0
const TEINTE_RUE := Color(0.85, 0.88, 1.0)

var couche: CanvasLayer
var marcheurs: Array[Sprite2D] = []
var _teinte_avant: Color = Color.WHITE
var _etape: EtapeBase


func construire() -> Animation:
	var rue := planche(RUE)
	var volet := planche(VOLET)
	var ilde := planche(ILDE)
	var file := planche(FILE)
	if rue == null or volet == null or ilde == null or file == null:
		return null
	couche = couche_plein_ecran()
	couche.add_child(sprite("Rue", rue, Vector2.ZERO))
	for i in NB_SUIVANTS + 1:
		var s := sprite("Marcheur%d" % i, ilde if i == 0 else file, Vector2.ZERO, 4)
		s.offset = -SilhouetteTobie.PIEDS
		s.scale = Vector2(ECHELLE, ECHELLE)
		couche.add_child(s)
		marcheurs.append(s)
	couche.add_child(sprite("Volet", volet, Vector2.ZERO))

	var anim := Animation.new()
	anim.length = DUREE
	cle(anim, "Plans:visible", 0.0, true)
	var nb_pas := int(roundf(DUREE / Cinematique.PAS))
	for i in marcheurs.size():
		var chemin := "Plans/Marcheur%d" % i
		var x0 := X_DEPART - ECART * i
		var demi := SilhouetteTobie.PIEDS.x * ECHELLE
		var vu := -1
		for p in nb_pas + 1:
			var t := p * Cinematique.PAS
			var x := roundf(x0 + VITESSE * t)
			cle(anim, chemin + ":position", t, Vector2(x, SOL))
			var dedans := 1 if x + demi > EMBRASURE.x and x - demi < EMBRASURE.y else 0
			if dedans != vu:
				cle(anim, chemin + ":visible", t, dedans == 1)
				vu = dedans
			if p % int(roundf(DUREE_IMAGE / Cinematique.PAS)) == 0:
				cle(anim, chemin + ":frame", t, (i + int(roundf(t / DUREE_IMAGE))) % 4)
	cle(anim, "Plans:visible", DUREE, false)
	return anim


func _prendre_controle() -> void:
	super()
	_etape = _etape_parente()
	if _etape != null:
		_teinte_avant = _etape.teinte_actuelle()
		_etape.definir_teinte(Color(_etape.teintes_lieux.get(&"chemin_nuit", TEINTE_RUE)))


func apres() -> void:
	if couche != null:
		couche.visible = false
	if _etape != null and is_instance_valid(_etape):
		_etape.definir_teinte(_teinte_avant)
	_etape = null


func _etape_parente() -> EtapeBase:
	var n := get_parent()
	while n != null and not n is EtapeBase:
		n = n.get_parent()
	return n as EtapeBase
