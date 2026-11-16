extends CinematiquePlans
## e1_sortie_tranchee (retouche du GD) : trois temps, 5,8 s.
## A, dans le décor : Tobie monte l'échelle (planche chr_tobie_grimper_01 : 4 images de 200×320,
##    pieds à (100, 316), chaque image le monte de 32 px) et la caméra le suit vers le haut,
##    jusqu'au parapet. En effets atténués, elle reste sur l'échelle (plan fixe).
## B, plein écran (tools/gen_cin_e1_sortie.py) : le parapet vu d'en bas, à contre-jour sur une
##    aube pâle ; Tobie le franchit (cin_sortie_02 : 4 images, grille 2 × 2, en ZONE_B) et
##    disparaît de l'autre côté ; le parapet vide reste (cin_sortie_01).
## C, plein écran : retour bref sur Lamarre (cin_sortie_03), qui baisse la tête (cin_sortie_04,
##    2 images en ligne, en ZONE_C).
## Le vrai messager est masqué : la scène passe à l'étape suivante juste après.

const PLANCHE := "res://assets/graphics/chr/chr_tobie_grimper_01.png"
const DOSSIER := "res://assets/graphics/cin/cin_sortie_%02d.png"
const SON := "sfx_echelle_monter"
## Pieds de Tobie sur le barreau du bas de fx_echelle (centrée en (820, 550) dans le pied de
## l'échelle, 720 px de haut, barreaux à y 39,5 + 64 k de la planche).
const DEPART := Vector2(820.0, 869.5)
const MONTEE_PAR_IMAGE := 32.0
const DUREE_IMAGE := 0.2
const DEBUT := 0.3
const NB_IMAGES := 11
## La caméra suit la montée, du pied au haut de l'échelle (zoom de Depart), sans jamais
## sortir du décor peint : de 0 à 1080 en hauteur (demi-hauteur 360 au zoom 1,5), et pas
## au-delà de x 1330 à droite, où s'arrête la tranchée (demi-largeur 640).
const CAMERA_BAS := Vector2(680.0, 720.0)
const CAMERA_HAUT := Vector2(680.0, 380.0)
const FIN_A := 2.4
const ZONE_B := Vector2(780, 360)
const IMAGE_B := 0.3
const FIN_B := 4.4
const ZONE_C := Vector2(640, 60)
const REGARD_C := 0.5
const DUREE := 5.8

var grimpeur: Sprite2D
var couche: CanvasLayer


func construire() -> Animation:
	var texture := planche(PLANCHE)
	var t: Array[Texture2D] = []
	for i in range(1, 5):
		t.append(planche(DOSSIER % i))
	if texture == null or t.has(null):
		return null
	grimpeur = Sprite2D.new()
	grimpeur.name = "Grimpeur"
	grimpeur.texture = texture
	grimpeur.hframes = 4
	grimpeur.centered = false
	grimpeur.offset = -SilhouetteTobie.PIEDS
	grimpeur.position = DEPART
	grimpeur.visible = false
	grimpeur.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	add_child(grimpeur)

	couche = couche_plein_ecran()
	var b := Node2D.new()
	b.name = "B"
	b.add_child(sprite("Fond", t[0], Vector2.ZERO))
	b.add_child(sprite("Tobie", t[1], ZONE_B, 2, 2))
	var c := Node2D.new()
	c.name = "C"
	c.add_child(sprite("Fond", t[2], Vector2.ZERO))
	c.add_child(sprite("Lamarre", t[3], ZONE_C, 2, 1))
	couche.add_child(b)
	couche.add_child(c)

	var anim := Animation.new()
	anim.length = DUREE
	# A : la montée, la caméra qui suit
	var depart := get_node_or_null("Depart") as Marker2D
	if depart != null:
		cle(anim, "Camera:zoom", 0.0, depart.scale)
		if Reglages.valeur(&"effets_attenues"):
			cle(anim, "Camera:position", 0.0, CAMERA_BAS)
		else:
			var n := roundi(FIN_A / Cinematique.PAS)
			for k in n + 1:
				var u := float(k) / n
				cle(anim, "Camera:position", k * Cinematique.PAS, CAMERA_BAS.lerp(CAMERA_HAUT, u * u * (3.0 - 2.0 * u)))
	cle(anim, "Grimpeur:visible", 0.0, true)
	for n in NB_IMAGES:
		var ti := DEBUT + n * DUREE_IMAGE
		cle(anim, "Grimpeur:frame", ti, n % 4)
		cle(anim, "Grimpeur:position", ti, DEPART - Vector2(0.0, MONTEE_PAR_IMAGE * n))
	son(anim, DEBUT, SON)
	# B : le parapet, il passe de l'autre côté, puis le parapet vide
	cle(anim, "Plans:visible", 0.0, false)
	cle(anim, "Plans:visible", FIN_A, true)
	cle(anim, "Grimpeur:visible", FIN_A, false)
	cle(anim, "Plans/B:visible", 0.0, true)
	cle(anim, "Plans/C:visible", 0.0, false)
	cle(anim, "Plans/B/Tobie:visible", 0.0, true)
	var tb := images(anim, "Plans/B/Tobie", FIN_A, 0, 3, IMAGE_B)
	cle(anim, "Plans/B/Tobie:visible", tb, false)
	# C : Lamarre regarde en haut, puis baisse la tête
	cle(anim, "Plans/B:visible", FIN_B, false)
	cle(anim, "Plans/C:visible", FIN_B, true)
	images(anim, "Plans/C/Lamarre", FIN_B, 0, 1, REGARD_C)
	cle(anim, "Plans:visible", DUREE, false)
	return anim


func _prendre_controle() -> void:
	super()
	var messager := _trouver_messager()
	if messager != null:
		messager.visible = false


func apres() -> void:
	if grimpeur != null:
		grimpeur.visible = false
	if couche != null:
		couche.visible = false
