extends CinematiquePlans
## e1_sortie_tranchee : Tobie monte l'échelle, la caméra reste en bas (cadrage Depart →
## Arrivee du Level Designer) et le perd au-dessus du parapet.
## Planche chr_tobie_grimper_01 (DA) : 4 images de 200×320, pieds à (100, 316) ; à l'image 0
## les pieds sont sur un barreau, et chaque image fait monter Tobie de 32 px (deux barreaux
## par cycle). 5 i/s, pour tomber juste sur le pas de 1/10 s du lecteur (6 i/s conseillé).
## Le vrai messager est masqué : la scène passe à l'étape suivante juste après.

const PLANCHE := "res://assets/graphics/chr/chr_tobie_grimper_01.png"
const SON := "sfx_echelle_monter"
## Pieds de Tobie sur le barreau du bas de fx_echelle (centrée en (820, 550) dans le pied de
## l'échelle, 720 px de haut, barreaux à y 39,5 + 64 k de la planche).
const DEPART := Vector2(820.0, 869.5)
const MONTEE_PAR_IMAGE := 32.0
const DUREE_IMAGE := 0.2
const DEBUT := 0.5
## Assez d'images pour que Tobie sorte du cadre par le haut.
const NB_IMAGES := 17
const DUREE := 6.0

var grimpeur: Sprite2D


func construire() -> Animation:
	var texture := planche(PLANCHE)
	if texture == null:
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

	var anim := Animation.new()
	anim.length = DUREE
	var depart := get_node_or_null("Depart") as Marker2D
	var arrivee := get_node_or_null("Arrivee") as Marker2D
	if depart != null:
		if arrivee == null:
			arrivee = depart
		for p in [["position", depart.position, arrivee.position], ["zoom", depart.scale, arrivee.scale]]:
			var piste := anim.add_track(Animation.TYPE_VALUE)
			anim.track_set_path(piste, NodePath("Camera:%s" % p[0]))
			anim.track_insert_key(piste, 0.0, p[1])
			anim.track_insert_key(piste, DUREE, p[2])
	cle(anim, "Grimpeur:visible", 0.0, true)
	for n in NB_IMAGES:
		var t := DEBUT + n * DUREE_IMAGE
		cle(anim, "Grimpeur:frame", t, n % 4)
		cle(anim, "Grimpeur:position", t, DEPART - Vector2(0.0, MONTEE_PAR_IMAGE * n))
	son(anim, DEBUT, SON)
	cle(anim, "Grimpeur:visible", DEBUT + NB_IMAGES * DUREE_IMAGE, false)
	return anim


func _prendre_controle() -> void:
	super()
	var messager := _trouver_messager()
	if messager != null:
		messager.visible = false


func apres() -> void:
	if grimpeur != null:
		grimpeur.visible = false
