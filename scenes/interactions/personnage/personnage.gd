class_name Personnage
extends AnimatedSprite2D
## Personnage d'une rencontre (planches de la DA, #68, #72, #84) : chr_<nom>_repos_01.png (ou
## chr_<nom>_fige_01.png pour une image fixe, comme le mort de l'étape 2, ou
## chr_<nom>_marche_01.png pour une marche sur place, comme la procession), images de 200×320,
## pieds à (100, 316) sur l'origine, de face (jamais retourné). La respiration tient chaque
## image 3 tics de 10 i/s, plus lente que la marche de Tobie.

const DOSSIER := "res://assets/graphics/chr/"
const IMAGES_PAR_SECONDE := SilhouetteTobie.IMAGES_PAR_SECONDE / 3.0

var nom: StringName
## Image de départ de la boucle (déphase les silhouettes d'un même cortège).
var dephasage: int = 0
## Le geste en cours garde sa dernière image au lieu de revenir à la respiration.
var _tenu: bool = false


## Planches essayées, dans l'ordre : respiration, image figée, marche sur place.
const ANIMATIONS: Array[String] = ["repos", "fige", "marche"]


static func chemin_planche(nom_personnage: StringName) -> String:
	for animation in ANIMATIONS:
		var chemin := DOSSIER + "chr_%s_%s_01.png" % [nom_personnage, animation]
		if ResourceLoader.exists(chemin):
			return chemin
	return ""


## Construit le personnage, ou null si sa planche n'existe pas encore.
static func creer(nom_personnage: StringName) -> Personnage:
	var chemin := chemin_planche(nom_personnage)
	if nom_personnage == &"" or chemin == "":
		return null
	var images := SpriteFrames.new()
	images.remove_animation(&"default")
	SilhouetteTobie.ajouter_planche(images, SilhouetteTobie.REPOS, load(chemin) as Texture2D, true)
	images.set_animation_speed(SilhouetteTobie.REPOS, IMAGES_PAR_SECONDE)
	var p := Personnage.new()
	p.name = "Personnage"
	p.nom = nom_personnage
	p.sprite_frames = images
	p.centered = false
	p.offset = -SilhouetteTobie.PIEDS
	p.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	return p


## Planche d'un geste (directive animation) : chr_<nom>_<geste>_01.png, ou "" si pas encore
## dessinée.
static func chemin_geste(nom_personnage: StringName, geste: StringName) -> String:
	if nom_personnage == &"" or geste == &"" or String(geste) in ANIMATIONS:
		return ""
	var chemin := DOSSIER + "chr_%s_%s_01.png" % [nom_personnage, geste]
	return chemin if ResourceLoader.exists(chemin) else ""


## Joue un geste une fois à 10 i/s, puis revient à la respiration, ou garde sa dernière image
## avec `tenir` (jusqu'au geste suivant). Faux (et rien ne bouge) tant que la planche du geste
## n'existe pas : les dialogues se balisent avant les dessins.
func jouer_geste(geste: StringName, tenir: bool = false) -> bool:
	if not _charger_geste(geste):
		return false
	_tenu = tenir
	play(geste)
	return true


## Montre la première image d'un geste, immobile (ex. le mort bras pendant, avant qu'il ne
## le lève). Faux sans planche.
func poser_debut_geste(geste: StringName) -> bool:
	if not _charger_geste(geste):
		return false
	_tenu = true
	animation = geste
	frame = 0
	stop()
	return true


func _charger_geste(geste: StringName) -> bool:
	if sprite_frames == null:
		return false
	if not sprite_frames.has_animation(geste):
		var chemin := chemin_geste(nom, geste)
		if chemin == "":
			return false
		SilhouetteTobie.ajouter_planche(sprite_frames, geste, load(chemin) as Texture2D, false)
	return true


func _ready() -> void:
	animation_finished.connect(_sur_animation_finie)
	play(SilhouetteTobie.REPOS)
	frame = dephasage % maxi(1, sprite_frames.get_frame_count(SilhouetteTobie.REPOS))


func _sur_animation_finie() -> void:
	if animation != SilhouetteTobie.REPOS and not _tenu:
		play(SilhouetteTobie.REPOS)
