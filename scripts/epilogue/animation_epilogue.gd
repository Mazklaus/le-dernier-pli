class_name AnimationEpilogue
extends Control
## Épilogue animé (planches de la DA) : remplace la gravure fixe du carton d'épilogue. Une
## sous-classe par lettre (anim_epilogue_<lettre>.gd) décrit ses plans dans construire(), comme
## une CinematiquePlans : des calques plein écran dans le repère 1920 × 1080 (sous le nœud Cadre),
## des clés au pas de 1/10 s. epilogue.gd pose les lignes de texte aux instants temps_lignes, sur
## un bandeau papier en bas : rien d'important ne se passe sous y 780.
## En effets atténués, les mouvements de « caméra » (poussées, panoramiques) deviennent des plans
## fixes ; les objets qui bougent (cloche, corde) bougent toujours.

signal finie

const PAS := Cinematique.PAS
const NOM_ANIMATION := &"jouer"

## Instant (s) où chaque ligne du titre epilogue_<clé> doit paraître.
var temps_lignes: Array[float] = []
var duree: float = 0.0
var cadre: Node2D
var _lecteur: AnimationPlayer
var _finie_emise := false


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	cadre = Node2D.new()
	cadre.name = "Cadre"
	add_child(cadre)
	var anim := construire()
	if anim == null:
		return
	duree = anim.length
	var biblio := AnimationLibrary.new()
	biblio.add_animation(NOM_ANIMATION, anim)
	_lecteur = AnimationPlayer.new()
	_lecteur.name = "Animation"
	_lecteur.add_animation_library(&"", biblio)
	add_child(_lecteur)
	_lecteur.animation_finished.connect(func(_n: StringName) -> void: _emettre_finie())
	# l'état de départ, avant jouer()
	_lecteur.play(NOM_ANIMATION)
	_lecteur.seek(0.0, true)
	_lecteur.pause()


## À redéfinir : l'animation (clés relatives à ce nœud, ex. "Cadre/P1:visible"), ou null.
func construire() -> Animation:
	return null


func jouer() -> void:
	if _lecteur == null:
		_emettre_finie()
		return
	_lecteur.play(NOM_ANIMATION)


## Saute à la dernière image (comme « annuler » dans les cinés).
func passer() -> void:
	if _lecteur != null:
		_lecteur.play(NOM_ANIMATION)
		_lecteur.seek(duree, true)
		_lecteur.pause()
	_emettre_finie()


func _emettre_finie() -> void:
	if not _finie_emise:
		_finie_emise = true
		finie.emit()


# --- aides de construction ----------------------------------------------------------------------

## Un plan : un Node2D sous le Cadre, caché hors de [debut, fin[.
func plan(anim: Animation, nom: String, debut: float, fin: float) -> Node2D:
	var p := Node2D.new()
	p.name = nom
	p.visible = false
	cadre.add_child(p)
	cle(anim, "Cadre/%s:visible" % nom, 0.0, debut <= 0.0)
	if debut > 0.0:
		cle(anim, "Cadre/%s:visible" % nom, debut, true)
	if fin < anim.length:
		cle(anim, "Cadre/%s:visible" % nom, fin, false)
	return p


static func cle(anim: Animation, chemin: String, temps: float, valeur: Variant) -> void:
	CinematiquePlans.cle(anim, chemin, temps, valeur)


static func planche(chemin: String) -> Texture2D:
	return CinematiquePlans.planche(chemin)


static func sprite(nom: String, texture: Texture2D, position_haut_gauche: Vector2, colonnes: int = 1, lignes: int = 1) -> Sprite2D:
	return CinematiquePlans.sprite(nom, texture, position_haut_gauche, colonnes, lignes)


## Un mouvement de caméra (poussée, panoramique) de v0 à v1 entre t0 et t1, une clé tous les
## dixièmes, adouci aux deux bouts. En effets atténués : deux plans fixes (v0, puis v1 à mi-course).
static func mouvement(anim: Animation, chemin: String, t0: float, t1: float, v0: Variant, v1: Variant) -> void:
	if Reglages.valeur(&"effets_attenues"):
		cle(anim, chemin, t0, v0)
		cle(anim, chemin, snappedf((t0 + t1) / 2.0, PAS), v1)
		return
	var n := maxi(1, roundi((t1 - t0) / PAS))
	for k in n + 1:
		var u := float(k) / n
		var v: Variant = lerp(v0, v1, u * u * (3.0 - 2.0 * u))
		if v is Vector2:
			v = (v as Vector2).round() if chemin.ends_with(":position") else v
		cle(anim, chemin, t0 + k * PAS, v)


## Une poussée vers le point centre (repère écran) : échelle et position du nœud, de z0 à z1.
static func pousser(anim: Animation, chemin: String, t0: float, t1: float, centre: Vector2, z0: float, z1: float) -> void:
	mouvement(anim, chemin + ":scale", t0, t1, Vector2(z0, z0), Vector2(z1, z1))
	mouvement(anim, chemin + ":position", t0, t1, centre - centre * z0, centre - centre * z1)


## Des images en boucle (frame) de debut à fin, chacune tenue duree_image.
static func boucle(anim: Animation, chemin: String, debut: float, fin: float, images: Array, duree_image: float) -> void:
	var t := debut
	var i := 0
	while t < fin - 0.001:
		cle(anim, chemin + ":frame", snappedf(t, PAS), int(images[i % images.size()]))
		t += duree_image
		i += 1
