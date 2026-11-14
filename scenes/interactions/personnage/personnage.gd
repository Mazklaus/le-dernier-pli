class_name Personnage
extends AnimatedSprite2D
## Personnage d'une rencontre (planches de la DA, ex. #68) : chr_<nom>_repos_01.png, images
## de 200×320, pieds à (100, 316) sur l'origine, de face (jamais retourné). La respiration
## tient chaque image 3 tics de 10 i/s, plus lente que la marche de Tobie.

const DOSSIER := "res://assets/graphics/chr/"
const IMAGES_PAR_SECONDE := SilhouetteTobie.IMAGES_PAR_SECONDE / 3.0

var nom: StringName


static func chemin_planche(nom_personnage: StringName) -> String:
	return DOSSIER + "chr_%s_repos_01.png" % nom_personnage


## Construit le personnage, ou null si sa planche n'existe pas encore.
static func creer(nom_personnage: StringName) -> Personnage:
	var chemin := chemin_planche(nom_personnage)
	if nom_personnage == &"" or not ResourceLoader.exists(chemin):
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
	p.autoplay = String(SilhouetteTobie.REPOS)
	return p
