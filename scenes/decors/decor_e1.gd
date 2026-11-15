class_name DecorE1
extends DecorParallaxe
## Décor de surface de l'étape 1 (planche du DA, PR #39) : cinq plans parallaxes pour un
## niveau de 10624 px, la cendre qui tombe entre le plan 2 et le plan 3. La tombée du jour
## est peinte dans les tuiles (crans à x 6600 et 9000) : aucun modulate.
## Masque les fonds, sols et murs gris de la maquette (Surface/*/Fond, Sol, Mur*) quand le décor est posé, et habille
## la Chicane (fx_chicane), la banquette du périscope (fx_banquette) et l'échelle de sortie (ombre, puis claire après e1_adieu).

const DOSSIER := "res://assets/graphics/env/e1/env_e1_"
const CENDRE := "res://assets/graphics/fx/fx_cendre.png"
const CHICANE := "res://assets/graphics/fx/fx_chicane.png"
const BANQUETTE := "res://assets/graphics/fx/fx_banquette.png"
const ECHELLE_OMBRE := "res://assets/graphics/fx/fx_echelle-ombre.png"
const ECHELLE_CLAIRE := "res://assets/graphics/fx/fx_echelle-claire.png"
## L'échelle de sortie passe au clair quand l'adieu de Jacquot a été fait (Level Designer).
const RENCONTRE_ECHELLE: StringName = &"e1_adieu"
## [nom du plan, vitesse, couche] du plus lointain au plus proche.
const PLANS := [
	["plan0_ciel", 0.05, -50],
	["plan1_lointain", 0.2, -40],
	["plan2_milieu", 0.5, -30],
	["plan3_surface", 1.0, -20],
	["plan4_premier-plan", 1.4, 20],
]
const Z_CENDRE := -25
## Voiles de la tombée du jour (DA, #53) : calques plein écran entre le plan 2 et le plan 3,
## affichés en tout-ou-rien quand le messager dépasse leur abscisse.
const VOILES := [
	["fx_voile-hachure", 6600.0, -27],
	["fx_voile-contre-hachure", 9000.0, -26],
]
const DOSSIER_FX := "res://assets/graphics/fx/"
const FONDU_VOILE := 0.1
## Vitesse de chute de la cendre, en pixels par seconde.
const CHUTE_CENDRE := 40.0

@export var masquer_fonds_maquette: bool = true

var plans: Array[Parallax2D] = []
var cendre: Sprite2D
var echelle: Sprite2D
## [Sprite2D, seuil x] par voile.
var voiles: Array = []

var _defilement: float = 0.0


func _ready() -> void:
	for p: Array in PLANS:
		var plan := creer_plan(DOSSIER + String(p[0]), float(p[1]), int(p[2]))
		if plan != null:
			add_child(plan)
			plans.append(plan)
	_creer_cendre()
	_creer_voiles()
	if masquer_fonds_maquette:
		masquer_fonds_gris()
	_habiller_chicane()
	_habiller_banquette()
	_habiller_echelle()


func _process(delta: float) -> void:
	_maj_voiles()
	_couvrir_ecran()
	if cendre == null:
		return
	var attenue: bool = Reglages.valeur(&"effets_attenues")
	_defilement = fmod(_defilement + CHUTE_CENDRE * (0.4 if attenue else 1.0) * delta, 1080.0)
	cendre.region_rect.position.y = -_defilement


## Cendre et voiles couvrent tout l'écran, même plus large que 16/9 (stretch expand) : leur
## région (texture répétée) prend la taille de la vue.
func _couvrir_ecran() -> void:
	var taille := get_viewport_rect().size.max(Vector2(1920.0, 1080.0))
	if cendre != null:
		cendre.region_rect.size = taille
	for paire: Array in voiles:
		(paire[0] as Sprite2D).region_rect.size = taille


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


func _creer_voiles() -> void:
	for v: Array in VOILES:
		var chemin := DOSSIER_FX + String(v[0]) + ".png"
		if not ResourceLoader.exists(chemin):
			continue
		var couche := Parallax2D.new()
		couche.name = String(v[0])
		couche.scroll_scale = Vector2(0.0, 1.0)
		couche.z_index = int(v[2])
		add_child(couche)
		var voile := Sprite2D.new()
		voile.texture = load(chemin) as Texture2D
		voile.centered = false
		# La texture est une petite tuile qui se raccorde (DA) : on la répète sur tout l'écran.
		voile.region_enabled = true
		voile.region_rect = Rect2(0, 0, 1920, 1080)
		voile.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
		voile.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		voile.modulate.a = 0.0
		voile.visible = false
		couche.add_child(voile)
		voiles.append([voile, float(v[1])])


## Tout-ou-rien selon l'abscisse du messager (fondu de FONDU_VOILE s au plus).
func _maj_voiles() -> void:
	if voiles.is_empty():
		return
	var messager := get_tree().get_first_node_in_group(Messager.GROUPE) as Node2D
	if messager == null:
		return
	for paire: Array in voiles:
		var voile: Sprite2D = paire[0]
		var actif: bool = messager.global_position.x >= float(paire[1])
		var cible := 1.0 if actif else 0.0
		if is_equal_approx(voile.modulate.a, cible) and voile.visible == actif:
			continue
		voile.visible = true
		voile.modulate.a = move_toward(voile.modulate.a, cible, get_process_delta_time() / FONDU_VOILE)
		if voile.modulate.a <= 0.0:
			voile.visible = false


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


## La banquette du périscope prend le dessin du DA (caillebotis sur sacs, déjà sous le voile)
## à la place du rectangle gris.
func _habiller_banquette() -> void:
	var banquette := get_parent().get_node_or_null("Surface/Carrefour/BanquettePeriscope") if get_parent() else null
	if banquette == null or not ResourceLoader.exists(BANQUETTE):
		return
	var visuel := banquette.get_node_or_null("Visuel") as CanvasItem
	if visuel != null:
		visuel.visible = false
	var dessin := Sprite2D.new()
	dessin.name = "Dessin"
	dessin.texture = load(BANQUETTE) as Texture2D
	dessin.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	banquette.add_child(dessin)


## L'échelle de sortie : dans l'ombre tant que l'adieu de Jacquot n'est pas fait, claire ensuite.
func _habiller_echelle() -> void:
	var support := get_parent().get_node_or_null("Surface/PiedEchelle/Echelle") if get_parent() else null
	if support == null or not ResourceLoader.exists(ECHELLE_OMBRE):
		return
	var visuel := support.get_node_or_null("Visuel") as CanvasItem
	if visuel != null:
		visuel.visible = false
	echelle = Sprite2D.new()
	echelle.name = "Dessin"
	echelle.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	support.add_child(echelle)
	GameState.rencontre_vue_marquee.connect(func(_id: StringName) -> void: actualiser_echelle())
	GameState.etat_charge.connect(actualiser_echelle)
	actualiser_echelle()


func actualiser_echelle() -> void:
	if echelle == null:
		return
	var claire := GameState.rencontre_vue(RENCONTRE_ECHELLE)
	echelle.texture = load(ECHELLE_CLAIRE if claire else ECHELLE_OMBRE) as Texture2D
