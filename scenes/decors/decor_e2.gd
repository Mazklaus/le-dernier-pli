class_name DecorE2
extends DecorParallaxe
## Décor de surface de l'étape 2, le No Man's Land (planche du DA, PR #56) : cinq plans
## parallaxes de 1300 px de haut pour un niveau de 16320 px.
## - Brouillard : trois bandes gravées qui bouclent sur x, affichées en tout-ou-rien tant que le
##   messager est entre x 4800 et 10100 (de la première ceinture à la sortie de la seconde).
##   La bande lointaine passe derrière le plan 2, la moyenne derrière le plan 3, la proche
##   devant le plan 3 mais derrière le messager et les personnages (DA : les silhouettes
##   restent entières), à la vitesse du sol.
## - Cheval de frise : ferme la chicane de Brisse, part avec le Verrou (e2_poste_passe).
## - Fil qui retombe : une fois la seconde ceinture ouverte et franchie, le fil se referme
##   derrière Tobie et bloque le retour (verrou de retour).
## - La sacoche de Matthieu au fond du grand trou.
## Masque aussi les gris de la maquette (fonds, sol, murs, bandes de brouillard, souche).

const DOSSIER := "res://assets/graphics/env/e2/env_e2_"
const DOSSIER_FX := "res://assets/graphics/fx/"
## [nom du plan, vitesse, couche] du plus lointain au plus proche.
const PLANS := [
	["plan0_ciel", 0.05, -50],
	["plan1_lointain", 0.2, -40],
	["plan2_milieu", 0.5, -30],
	["plan3_surface", 1.0, -20],
	["plan4_premier-plan", 1.4, 20],
]
## [fichier, vitesse, couche] des bandes de brouillard, de la plus lointaine à la plus proche.
const BANDES := [
	["fx_brouillard_01", 0.35, -35],
	["fx_brouillard_02", 0.75, -25],
	["fx_brouillard_03", 1.0, -10],
]
const LARGEUR_BANDE := 1920.0
const BROUILLARD := Vector2(4800.0, 10100.0)
const FONDU_BROUILLARD := 0.1

const CHEVAL_FRISE := "fx_cheval-frise"
const CHEMIN_CHICANE := "Surface/Poste/Chicane"
## Le dessin de la planche centre la chicane à x 3260 (le Verrou est à 3230).
const X_CHEVAL_FRISE := 3260.0

const FIL_RETOMBE := "fx_fil-retombe"
const CHEMIN_CEINTURE_DEUX := "Surface/Brouillard/CeintureDeux"
const RENCONTRE_CEINTURE_DEUX: StringName = &"e2_barbeles_ceinture2"
## Le fil retombe quand le messager a dépassé la seconde ceinture de cette distance.
const MARGE_FIL := 80.0

const SACOCHE := "fx_sacoche-matthieu"
const POSITION_SACOCHE := Vector2(12900.0, 1060.0)

## Gris de la maquette que le décor remplace, en plus des fonds, du sol et des murs.
const GRIS_MAQUETTE := [
	"Surface/Brouillard/ZoneSombre/BandeBrouillard1",
	"Surface/Brouillard/ZoneSombre/BandeBrouillard2",
	"Surface/Brouillard/ZoneSombre/BandeBrouillard3",
	"Surface/Souche/SoucheVisuel",
]

@export var masquer_fonds_maquette: bool = true

var plans: Array[Parallax2D] = []
var bandes: Array[Parallax2D] = []
var cheval_frise: Sprite2D
var fil_retombe: StaticBody2D
var sacoche: Sprite2D
var fil_tombe: bool = false

var _alpha_brouillard: float = 0.0


func _ready() -> void:
	for p: Array in PLANS:
		var plan := creer_plan(DOSSIER + String(p[0]), float(p[1]), int(p[2]))
		if plan != null:
			add_child(plan)
			plans.append(plan)
	_creer_brouillard()
	if masquer_fonds_maquette:
		masquer_fonds_gris()
		for chemin: String in GRIS_MAQUETTE:
			var gris: CanvasItem = get_parent().get_node_or_null(chemin) as CanvasItem if get_parent() else null
			if gris != null:
				gris.visible = false
	_habiller_chicane()
	_creer_fil_retombe()
	_poser_sacoche()


func _process(delta: float) -> void:
	var messager := get_tree().get_first_node_in_group(Messager.GROUPE) as Node2D
	if messager == null:
		return
	_maj_brouillard(messager.global_position.x, delta)
	if not fil_tombe:
		_maj_fil(messager.global_position.x)


static func dans_le_brouillard(x: float) -> bool:
	return x >= BROUILLARD.x and x <= BROUILLARD.y


func _sprite_fx(nom: String) -> Sprite2D:
	var chemin := DOSSIER_FX + nom + ".png"
	if not ResourceLoader.exists(chemin):
		return null
	var sprite := Sprite2D.new()
	sprite.name = "Dessin"
	sprite.texture = load(chemin) as Texture2D
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	return sprite


## Trois bandes qui bouclent sur x (Parallax2D répété), à l'échelle du monde verticalement.
func _creer_brouillard() -> void:
	for b: Array in BANDES:
		var chemin := DOSSIER_FX + String(b[0]) + ".png"
		if not ResourceLoader.exists(chemin):
			continue
		var bande := Parallax2D.new()
		bande.name = String(b[0])
		bande.scroll_scale = Vector2(float(b[1]), 1.0)
		bande.repeat_size = Vector2(LARGEUR_BANDE, 0.0)
		bande.repeat_times = 2
		bande.z_index = int(b[2])
		bande.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		bande.visible = false
		bande.modulate.a = 0.0
		var sprite := Sprite2D.new()
		sprite.texture = load(chemin) as Texture2D
		sprite.centered = false
		bande.add_child(sprite)
		add_child(bande)
		bandes.append(bande)


## Tout-ou-rien selon l'abscisse du messager (fondu de FONDU_BROUILLARD s au plus).
func _maj_brouillard(x: float, delta: float) -> void:
	if bandes.is_empty():
		return
	var cible := 1.0 if dans_le_brouillard(x) else 0.0
	if is_equal_approx(_alpha_brouillard, cible):
		return
	_alpha_brouillard = move_toward(_alpha_brouillard, cible, delta / FONDU_BROUILLARD)
	for bande in bandes:
		bande.modulate.a = _alpha_brouillard
		bande.visible = _alpha_brouillard > 0.0


## Le cheval de frise prend la place du rectangle gris de la Chicane ; il part avec le Verrou.
func _habiller_chicane() -> void:
	var chicane: Node2D = get_parent().get_node_or_null(CHEMIN_CHICANE) as Node2D if get_parent() else null
	if chicane == null:
		return
	cheval_frise = _sprite_fx(CHEVAL_FRISE)
	if cheval_frise == null:
		return
	var visuel := chicane.get_node_or_null("Visuel") as CanvasItem
	if visuel != null:
		visuel.visible = false
	chicane.add_child(cheval_frise)
	_poser_au_sol(cheval_frise, Vector2(X_CHEVAL_FRISE, _sol_sous(chicane)))


## Le verrou de retour : invisible et sans collision jusqu'à ce que le fil retombe.
func _creer_fil_retombe() -> void:
	var ceinture: Node2D = get_parent().get_node_or_null(CHEMIN_CEINTURE_DEUX) as Node2D if get_parent() else null
	if ceinture == null:
		return
	var dessin := _sprite_fx(FIL_RETOMBE)
	if dessin == null:
		return
	fil_retombe = StaticBody2D.new()
	fil_retombe.name = "FilRetombe"
	var forme := CollisionShape2D.new()
	forme.name = "Forme"
	var rect := RectangleShape2D.new()
	rect.size = Vector2(60.0, 300.0)
	forme.shape = rect
	forme.disabled = true
	fil_retombe.add_child(forme)
	fil_retombe.add_child(dessin)
	fil_retombe.visible = false
	add_child(fil_retombe)
	fil_retombe.global_position = ceinture.global_position
	_poser_au_sol(dessin, Vector2(ceinture.global_position.x, _sol_sous(ceinture)))


func _maj_fil(x: float) -> void:
	if fil_retombe == null or not GameState.rencontre_vue(RENCONTRE_CEINTURE_DEUX):
		return
	if x > fil_retombe.global_position.x + MARGE_FIL:
		faire_tomber_fil()


func faire_tomber_fil() -> void:
	if fil_retombe == null or fil_tombe:
		return
	fil_tombe = true
	fil_retombe.visible = true
	(fil_retombe.get_node("Forme") as CollisionShape2D).set_deferred(&"disabled", false)


func _poser_sacoche() -> void:
	sacoche = _sprite_fx(SACOCHE)
	if sacoche == null:
		return
	sacoche.name = "Sacoche"
	add_child(sacoche)
	_poser_au_sol(sacoche, POSITION_SACOCHE)


## Place un sprite centré pour que le bas de sa texture touche le sol en (x, y_sol).
func _poser_au_sol(sprite: Sprite2D, pied: Vector2) -> void:
	sprite.global_position = pied - Vector2(0.0, sprite.texture.get_height() / 2.0)


## Bas du rectangle gris d'un Verrou de la maquette (300 px de haut, centré) : le sol.
func _sol_sous(verrou: Node2D) -> float:
	return verrou.global_position.y + 150.0
