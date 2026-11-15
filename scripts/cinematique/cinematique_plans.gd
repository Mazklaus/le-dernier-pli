class_name CinematiquePlans
extends Cinematique
## Cinématique dont l'animation est construite en code à partir des planches de la DA, au
## lieu d'un AnimationPlayer saisi à la main (pistes longues et fragiles en .tscn). Une
## sous-classe par cinématique remplace le script du nœud Cinematique placé par le Level
## Designer et décrit ses plans dans `construire()`, qui renvoie l'Animation `jouer`.
## Les clés sont posées au pas de 1/10 s, en mode discret (pas d'interpolation molle).

## Au-dessus du jeu et de l'interface (masquée de toute façon pendant la cinématique).
const COUCHE_PLEIN_ECRAN := 60


func _ready() -> void:
	if get_node_or_null("Animation") == null:
		var anim := construire()
		if anim != null:
			var biblio := AnimationLibrary.new()
			biblio.add_animation(animation, anim)
			var lecteur := AnimationPlayer.new()
			lecteur.name = "Animation"
			lecteur.add_animation_library(&"", biblio)
			add_child(lecteur)
	finie.connect(func(_sautee: bool) -> void: apres())
	super()


## À redéfinir : l'animation de la cinématique, ou null si ses planches manquent (la
## cinématique ne fait alors rien, comme une cinématique pas encore placée).
func construire() -> Animation:
	return null


## À redéfinir : remise en ordre à la fin, jouée ou sautée (ex. masquer les plans).
func apres() -> void:
	pass


static func planche(chemin: String) -> Texture2D:
	return load(chemin) as Texture2D if ResourceLoader.exists(chemin) else null


## Sprite d'une planche en grille, coin haut-gauche en `position`.
static func sprite(nom: String, texture: Texture2D, position_haut_gauche: Vector2, colonnes: int = 1, lignes: int = 1) -> Sprite2D:
	var s := Sprite2D.new()
	s.name = nom
	s.texture = texture
	s.centered = false
	s.position = position_haut_gauche
	s.hframes = colonnes
	s.vframes = lignes
	s.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	return s


## Couche plein écran (repère 1920×1080), masquée hors de la cinématique.
func couche_plein_ecran() -> CanvasLayer:
	var couche := CanvasLayer.new()
	couche.name = "Plans"
	couche.layer = COUCHE_PLEIN_ECRAN
	couche.visible = false
	add_child(couche)
	return couche


## Pose une clé discrète (la piste est créée au besoin), chemin relatif à la cinématique.
static func cle(anim: Animation, chemin: String, temps: float, valeur: Variant) -> void:
	var piste := anim.find_track(NodePath(chemin), Animation.TYPE_VALUE)
	if piste == -1:
		piste = anim.add_track(Animation.TYPE_VALUE)
		anim.track_set_path(piste, NodePath(chemin))
		anim.value_track_set_update_mode(piste, Animation.UPDATE_DISCRETE)
		anim.track_set_interpolation_type(piste, Animation.INTERPOLATION_NEAREST)
	anim.track_insert_key(piste, snappedf(temps, Cinematique.PAS), valeur)


## Joue les images `premiere`..`derniere` d'un sprite, une par pas de `duree_image`, à
## partir de `debut`. Renvoie l'instant qui suit la dernière image.
static func images(anim: Animation, chemin: String, debut: float, premiere: int, derniere: int, duree_image: float = Cinematique.PAS) -> float:
	var t := debut
	for i in range(premiere, derniere + 1):
		cle(anim, chemin + ":frame", t, i)
		t += duree_image
	return t


## Un son à l'instant donné (piste de méthode vers l'AudioDirector ; sautée par un saut).
static func son(anim: Animation, temps: float, nom: String) -> void:
	var piste := anim.find_track(NodePath("/root/AudioDirector"), Animation.TYPE_METHOD)
	if piste == -1:
		piste = anim.add_track(Animation.TYPE_METHOD)
		anim.track_set_path(piste, NodePath("/root/AudioDirector"))
	anim.track_insert_key(piste, snappedf(temps, Cinematique.PAS), {"method": &"jouer_variante", "args": [nom]})
