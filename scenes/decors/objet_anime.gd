class_name ObjetAnime
extends AnimatedSprite2D
## Objet animé d'un décor (relevé de la QA du 17/11 : la buée de la crypte, la gamelle qui fume,
## la cloche qui frémit). Planches fx de la DA : images de `largeur_image` côte à côte, toute la
## hauteur de la planche.
## - `boucle` : tourne tout le temps (la fumée de la gamelle, la buée). Vide : l'objet reste
##   sur la première image de son premier geste, immobile.
## - `gestes` : {nom: planche} joués une fois sur la balise [#geste=<nom_objet>:<nom>] d'une
##   réplique des `declencheurs`, puis retour à la boucle (ou à l'immobilité). Le geste
##   « accelerer » n'a pas de planche : la boucle va `acceleration` fois plus vite, pour de bon
##   (« Derrière moi, la buée va plus vite »).
## Muet : un objet animé ne joue aucun son (la cloche ne sonne jamais avant l'épilogue).

const BOUCLE := &"boucle"
const ACCELERER := &"accelerer"

## Nom visé par les balises [#geste=<nom_objet>:…] (ex. &"cloche").
@export var nom_objet: StringName
@export var boucle: Texture2D
@export var gestes: Dictionary = {}
@export var largeur_image: int = 200
@export var images_par_seconde: float = 6.0
@export var acceleration: float = 2.0
## Rencontres dont les répliques peuvent animer l'objet.
@export var declencheurs: Array[NodePath] = []

var _repos: StringName = &""


func _ready() -> void:
	construire()
	for chemin in declencheurs:
		var d := get_node_or_null(chemin) as DeclencheurDialogue
		if d != null:
			d.geste_demande.connect(_sur_geste_demande)
	animation_finished.connect(_revenir)


## Monte les animations depuis les planches ; démarre la boucle s'il y en a une.
func construire() -> void:
	var images := SpriteFrames.new()
	images.remove_animation(&"default")
	if boucle != null:
		_ajouter(images, BOUCLE, boucle, true)
	for nom: StringName in gestes:
		var t := gestes[nom] as Texture2D
		if t != null:
			_ajouter(images, nom, t, false)
	sprite_frames = images
	_revenir()


func _ajouter(images: SpriteFrames, nom: StringName, planche: Texture2D, en_boucle: bool) -> void:
	images.add_animation(nom)
	images.set_animation_speed(nom, images_par_seconde)
	images.set_animation_loop(nom, en_boucle)
	var largeur := mini(largeur_image, planche.get_width()) if largeur_image > 0 else planche.get_width()
	for i in planche.get_width() / largeur:
		var image := AtlasTexture.new()
		image.atlas = planche
		image.region = Rect2(i * largeur, 0, largeur, planche.get_height())
		images.add_frame(nom, image)


func _sur_geste_demande(cible: StringName, geste: StringName) -> void:
	if cible == nom_objet:
		jouer_geste(geste)


## Joue un geste une fois (ou accélère la boucle). Faux sans planche : rien ne bouge.
func jouer_geste(geste: StringName) -> bool:
	if geste == ACCELERER:
		if not sprite_frames.has_animation(BOUCLE):
			return false
		speed_scale = acceleration
		return true
	if not sprite_frames.has_animation(geste):
		return false
	play(geste)
	return true


func _revenir() -> void:
	if sprite_frames.has_animation(BOUCLE):
		play(BOUCLE)
		return
	stop()
	var noms := sprite_frames.get_animation_names()
	if noms.is_empty():
		return
	if _repos == &"":
		_repos = noms[0]
	animation = _repos
	frame = 0
