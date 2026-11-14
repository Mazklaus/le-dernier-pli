class_name SilhouetteTobie
extends Node2D
## Tobie dessiné (planche de la DA, #65) : trois AnimatedSprite2D superposés, synchronisés
## image par image : le dessin de base, le ruban rouge du pli (calque _red, qui bat avec la
## Lucidité basse, voir Battement) et la cendre au front (calque chr_tobie-cendre, visible
## après e1_cendre, où Cassien cendre Tobie même s'il refuse).
## Planches horizontales d'images de 200×320, Tobie tourné vers la droite, pieds sur le sol à
## y 316, hanches à x 100 : l'origine du nœud est aux pieds. Le Messager retourne ce nœud
## (scale.x) pour la gauche. 10 i/s pile : la marche (8 images) ne glisse pas à 160 px/s.

const DOSSIER := "res://assets/graphics/chr/"
const LARGEUR_IMAGE := 200
const HAUTEUR_IMAGE := 320
const PIEDS := Vector2(100.0, 316.0)
const IMAGES_PAR_SECONDE := 10.0
const REPOS: StringName = &"repos"
const MARCHE: StringName = &"marche"
const INTERAGIR: StringName = &"interagir"
## [animation, en boucle]. Interagir se joue une fois et reste sur la main au pli.
const ANIMATIONS := [[REPOS, true], [MARCHE, true], [INTERAGIR, false]]
## Rencontre qui laisse la cendre au front.
const RENCONTRE_CENDRE: StringName = &"e1_cendre"

var base: AnimatedSprite2D
var ruban: AnimatedSprite2D
var cendre: AnimatedSprite2D
var animation: StringName = REPOS


func _ready() -> void:
	base = _calque("Base", "chr_tobie_%s_01.png")
	ruban = _calque("Ruban", "chr_tobie_%s_01_red.png")
	cendre = _calque("Cendre", "chr_tobie-cendre_%s_01.png")
	jouer(REPOS)
	GameState.rencontre_vue_marquee.connect(func(_id: StringName) -> void: actualiser_cendre())
	GameState.etat_charge.connect(actualiser_cendre)
	actualiser_cendre()


## Le dessin est-il chargé (planches présentes) ?
func _process(_delta: float) -> void:
	if ruban != null:
		ruban.modulate.a = Battement.opacite(Battement.maintenant(), GameState.palier,
			Reglages.valeur(&"effets_attenues"))


func est_dessine() -> bool:
	return base != null


func jouer(nom: StringName) -> void:
	if base == null or not base.sprite_frames.has_animation(nom):
		return
	# Déjà en cours (ou interagir fini, qui reste sur sa dernière image) : ne pas relancer.
	if nom == animation and base.animation == nom:
		return
	animation = nom
	for calque in calques():
		calque.play(nom)


func calques() -> Array[AnimatedSprite2D]:
	var liste: Array[AnimatedSprite2D] = []
	for c in [base, ruban, cendre]:
		if c != null:
			liste.append(c)
	return liste


func actualiser_cendre() -> void:
	if cendre != null:
		cendre.visible = GameState.rencontre_vue(RENCONTRE_CENDRE)


## Un calque : un AnimatedSprite2D dont chaque animation vient d'une planche horizontale.
func _calque(nom: String, motif: String) -> AnimatedSprite2D:
	var images := SpriteFrames.new()
	images.remove_animation(&"default")
	for a: Array in ANIMATIONS:
		var chemin := DOSSIER + motif % String(a[0])
		if not ResourceLoader.exists(chemin):
			continue
		ajouter_planche(images, StringName(a[0]), load(chemin) as Texture2D, bool(a[1]))
	if images.get_animation_names().is_empty():
		return null
	var sprite := AnimatedSprite2D.new()
	sprite.name = nom
	sprite.sprite_frames = images
	sprite.centered = false
	sprite.offset = -PIEDS
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	add_child(sprite)
	return sprite


## Découpe une planche en images de LARGEUR_IMAGE (leur nombre vient de la largeur).
static func ajouter_planche(images: SpriteFrames, nom: StringName, planche: Texture2D, boucle: bool) -> void:
	images.add_animation(nom)
	images.set_animation_speed(nom, IMAGES_PAR_SECONDE)
	images.set_animation_loop(nom, boucle)
	for i in planche.get_width() / LARGEUR_IMAGE:
		var image := AtlasTexture.new()
		image.atlas = planche
		image.region = Rect2(i * LARGEUR_IMAGE, 0, LARGEUR_IMAGE, HAUTEUR_IMAGE)
		images.add_frame(nom, image)
