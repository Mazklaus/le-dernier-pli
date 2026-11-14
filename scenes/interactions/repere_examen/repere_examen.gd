class_name RepereExamen
extends Node2D
## Repère au-dessus d'un détail pas encore examiné (spec UI/UX v2) : le sprite du DA
## ui_repere-detail (astérisque à la plume sur papier déchiré, 40×40 à 1080), lisible sur tout
## fond, immobile, visible dès que le détail est à l'écran (UI/UX : la règle la plus simple pour
## un joueur curieux). Disparaît une fois examiné.

const SPRITE := "res://assets/graphics/ui/ui_repere-detail.png"
const TAILLE := 40.0
## Hauteur au-dessus de l'origine du détail.
const HAUTEUR := 190.0
const DUREE_FONDU := 0.25

var rencontre_id: StringName

var _cible_alpha: float = 0.0


func _ready() -> void:
	position = Vector2(0.0, -HAUTEUR)
	z_index = 5
	modulate.a = 0.0
	var dessin := Sprite2D.new()
	dessin.name = "Dessin"
	dessin.texture = load(SPRITE) as Texture2D
	dessin.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	add_child(dessin)


func _process(delta: float) -> void:
	_cible_alpha = 1.0 if doit_paraitre() else 0.0
	modulate.a = move_toward(modulate.a, _cible_alpha, delta / DUREE_FONDU)


func est_examine() -> bool:
	return rencontre_id != &"" and GameState.rencontre_vue(rencontre_id)


func doit_paraitre() -> bool:
	if est_examine() or not is_inside_tree():
		return false
	return est_a_l_ecran(global_position, ecran_monde())


## Le rectangle visible de la vue, en coordonnées du monde (caméra comprise).
func ecran_monde() -> Rect2:
	var vue := get_viewport()
	return vue.get_canvas_transform().affine_inverse() * vue.get_visible_rect()


## Le repère compte comme à l'écran si son dessin y entre, même en partie.
static func est_a_l_ecran(point: Vector2, ecran: Rect2) -> bool:
	return ecran.grow(TAILLE / 2.0).has_point(point)
