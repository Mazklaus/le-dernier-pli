class_name DecorE5
extends DecorParallaxe
## Décor de l'étape 5, la Forêt de Croix (tools/gen_decors_e5.py) : chaque section reçoit un fond
## fixe env_e5_plan3_<nom>_NN, posé en (0, 0) dans son repère, derrière le jeu ; les gris de la
## maquette sont masqués. Trois petits calques montrent ce que Tobie a fait, sans un mot :
## l'entaille sur la croix-repère (sous le nœud « Entaille » que l'étape montre ou cache),
## la cloche d'Aubin raccrochée à son clou (insigne_rendu) et TOBIE gravé sur la croix sans nom
## (nom_grave).

const DOSSIER := "res://assets/graphics/env/e5/env_e5_"
const FX := "res://assets/graphics/fx/fx_%s.png"
const SECTIONS := [
	["Surface/Oree", "oree"],
	["Surface/Boucle", "boucle"],
	["Surface/Campement", "campement"],
	["Surface/Cimetiere", "cimetiere"],
	["Surface/Clairiere", "clairiere"],
]
const Z_LIEU := -20
## Les calques sont peints sur le bois, juste devant le fond et derrière les personnages.
const Z_CALQUE := -19

const ENTAILLE := "Surface/Boucle/e5_sentier/Entaille"
const CROIX_AUBIN := "Surface/Cimetiere/e5_croix"
## Coin haut-gauche de chaque calque dans le repère du déclencheur (gen_decors_e5.py, ANCRES).
const ANCRE_ENTAILLE := Vector2(-32, -308)
const ANCRE_CLOCHE := Vector2(-38, -276)
## La croix sans nom est 140 px à droite de celle d'Aubin (le déclencheur).
const ANCRE_NOM := Vector2(140 - 32, -231)
const CLOCHE_RENDUE: StringName = &"insigne_rendu"
const NOM_GRAVE: StringName = &"nom_grave"

@export var masquer_fonds_maquette: bool = true

var _cloche: Sprite2D
var _nom: Sprite2D


func _ready() -> void:
	var etape := get_parent()
	if etape == null:
		return
	for s: Array in SECTIONS:
		var lieu := etape.get_node_or_null(String(s[0])) as Node2D
		if lieu == null:
			continue
		var fond := dessin_lieu("%splan3_%s" % [DOSSIER, String(s[1])], "Dessin", Z_LIEU)
		if fond == null:
			continue
		lieu.add_child(fond)
		lieu.move_child(fond, 0)
		if masquer_fonds_maquette:
			masquer_gris_lieu(lieu)
	_poser_entaille(etape.get_node_or_null(ENTAILLE) as ColorRect)
	var croix := etape.get_node_or_null(CROIX_AUBIN) as Node2D
	if croix != null:
		_cloche = _calque("cloche-aubin", "Cloche", ANCRE_CLOCHE)
		_nom = _calque("nom-grave", "NomGrave", ANCRE_NOM)
		croix.add_child(_cloche)
		croix.add_child(_nom)
	GameState.rencontre_vue_marquee.connect(_sur_rencontre_vue)
	maj_calques()


func _exit_tree() -> void:
	if GameState.rencontre_vue_marquee.is_connected(_sur_rencontre_vue):
		GameState.rencontre_vue_marquee.disconnect(_sur_rencontre_vue)


func _sur_rencontre_vue(id: StringName) -> void:
	if id == CLOCHE_RENDUE or id == NOM_GRAVE:
		maj_calques()


func maj_calques() -> void:
	if _cloche != null:
		_cloche.visible = GameState.rencontre_vue(CLOCHE_RENDUE)
	if _nom != null:
		_nom.visible = GameState.rencontre_vue(NOM_GRAVE)


## L'étape montre ou cache le nœud « Entaille » : son gris devient transparent et le dessin des
## encoches s'y accroche, il suit donc sa visibilité.
func _poser_entaille(entaille: ColorRect) -> void:
	if entaille == null:
		return
	entaille.color = Color(0, 0, 0, 0)
	entaille.add_child(_calque("entaille-croix", "Dessin", ANCRE_ENTAILLE - entaille.position))


static func _calque(nom: String, nom_noeud: String, position: Vector2) -> Sprite2D:
	var s := Sprite2D.new()
	s.name = nom_noeud
	s.texture = charger_tuile(FX % nom)
	s.centered = false
	s.position = position
	s.z_as_relative = false
	s.z_index = Z_CALQUE
	return s
