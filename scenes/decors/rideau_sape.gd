class_name RideauSape
extends Node2D
## La couverture anti-gaz de la sape de sortie (étape 1, directive animation du GD) : tendue
## en travers tant que le VerrouCendre est fermé ; une fois e1_adieu jouée, Tobie la soulève en
## passant et elle retombe derrière lui (fx_rideau-sape-tombe, 6 images de 140×460, 10 i/s).
## Posée à côté du verrou et non dedans, pour rester visible quand le verrou s'efface.

const PLANCHE := "res://assets/graphics/fx/fx_rideau-sape-tombe.png"
const IMAGES := 6
const LARGEUR := 140.0
const HAUTEUR := 460.0
const IMAGES_PAR_SECONDE := 10.0

var verrou: Verrou
var dessin: Sprite2D
var zone: Area2D
var en_cours: bool = false
var _temps: float = 0.0


## Construit le rideau sur la position du verrou, ou null sans planche.
static func creer(v: Verrou, planche: Texture2D = null) -> RideauSape:
	if planche == null and ResourceLoader.exists(PLANCHE):
		planche = load(PLANCHE) as Texture2D
	if v == null or planche == null:
		return null
	var r := RideauSape.new()
	r.name = "RideauSape"
	r.verrou = v
	r.position = v.position
	r.dessin = Sprite2D.new()
	r.dessin.name = "Dessin"
	r.dessin.texture = planche
	r.dessin.hframes = IMAGES
	r.dessin.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	r.add_child(r.dessin)
	r.zone = Area2D.new()
	r.zone.name = "Passage"
	r.zone.monitorable = false
	r.zone.collision_layer = 0
	r.zone.collision_mask = 1
	var forme := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(LARGEUR, HAUTEUR)
	forme.shape = rect
	r.zone.add_child(forme)
	r.add_child(r.zone)
	return r


func _ready() -> void:
	zone.body_entered.connect(_sur_corps_entre)
	set_process(false)


func _sur_corps_entre(corps: Node2D) -> void:
	if corps.is_in_group(Messager.GROUPE):
		soulever()


## Tobie passe : la couverture se soulève et retombe. Rien tant que le verrou est fermé, ni
## pendant qu'elle se balance encore.
func soulever() -> bool:
	if en_cours or verrou == null or not verrou.est_ouvert():
		return false
	en_cours = true
	_temps = 0.0
	dessin.frame = 0
	set_process(true)
	return true


func _process(delta: float) -> void:
	_temps += delta
	var image := int(_temps * IMAGES_PAR_SECONDE)
	if image >= IMAGES:
		dessin.frame = 0
		en_cours = false
		set_process(false)
		return
	dessin.frame = image
