class_name DecorE1
extends DecorParallaxe
## Décor de surface de l'étape 1 (planche du DA, PR #39) : cinq plans parallaxes pour un
## niveau de 10624 px, la cendre qui tombe entre le plan 2 et le plan 3. La tombée du jour
## est peinte dans les tuiles (crans à x 6600 et 9000) : aucun modulate.
## Masque les fonds gris de la maquette (Surface/*/Fond) quand le décor est posé, et habille
## la Chicane (fx_chicane).

const DOSSIER := "res://assets/graphics/env/e1/env_e1_"
const CENDRE := "res://assets/graphics/fx/fx_cendre.png"
const CHICANE := "res://assets/graphics/fx/fx_chicane.png"
## [nom du plan, vitesse, couche] du plus lointain au plus proche.
const PLANS := [
	["plan0_ciel", 0.05, -50],
	["plan1_lointain", 0.2, -40],
	["plan2_milieu", 0.5, -30],
	["plan3_surface", 1.0, -20],
	["plan4_premier-plan", 1.4, 20],
]
const Z_CENDRE := -25
## Vitesse de chute de la cendre, en pixels par seconde.
const CHUTE_CENDRE := 40.0

@export var masquer_fonds_maquette: bool = true

var plans: Array[Parallax2D] = []
var cendre: Sprite2D

var _defilement: float = 0.0


func _ready() -> void:
	for p: Array in PLANS:
		var plan := creer_plan(DOSSIER + String(p[0]), float(p[1]), int(p[2]))
		if plan != null:
			add_child(plan)
			plans.append(plan)
	_creer_cendre()
	if masquer_fonds_maquette:
		_masquer_fonds()
	_habiller_chicane()


func _process(delta: float) -> void:
	if cendre == null:
		return
	var attenue: bool = Reglages.valeur(&"effets_attenues")
	_defilement = fmod(_defilement + CHUTE_CENDRE * (0.4 if attenue else 1.0) * delta, 1080.0)
	cendre.region_rect.position.y = -_defilement


## Cendre plein écran qui défile en boucle verticale (texture répétée dans une région fixe),
## fixée à l'écran horizontalement, au monde verticalement (absente sous terre).
func _creer_cendre() -> void:
	if not ResourceLoader.exists(CENDRE):
		return
	var couche := Parallax2D.new()
	couche.name = "Cendre"
	couche.scroll_scale = Vector2(0.0, 1.0)
	couche.z_index = Z_CENDRE
	add_child(couche)
	cendre = Sprite2D.new()
	cendre.texture = load(CENDRE) as Texture2D
	cendre.centered = false
	cendre.region_enabled = true
	cendre.region_rect = Rect2(0, 0, 1920, 1080)
	cendre.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	cendre.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	couche.add_child(cendre)


func _masquer_fonds() -> void:
	var surface := get_parent().get_node_or_null("Surface") if get_parent() else null
	if surface == null:
		return
	for section in surface.get_children():
		var fond := section.get_node_or_null("Fond") as CanvasItem
		if fond != null:
			fond.visible = false


## La Chicane (Verrou levé après e1_ordre) prend le dessin du DA à la place du rectangle gris ;
## elle disparaît avec le Verrou.
func _habiller_chicane() -> void:
	var chicane := get_parent().get_node_or_null("Surface/BoyauArriere/Chicane") if get_parent() else null
	if chicane == null or not ResourceLoader.exists(CHICANE):
		return
	var visuel := chicane.get_node_or_null("Visuel") as CanvasItem
	if visuel != null:
		visuel.visible = false
	var dessin := Sprite2D.new()
	dessin.name = "Dessin"
	dessin.texture = load(CHICANE) as Texture2D
	dessin.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	chicane.add_child(dessin)
