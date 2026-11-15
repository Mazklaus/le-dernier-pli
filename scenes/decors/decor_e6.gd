class_name DecorE6
extends DecorParallaxe
## Décor de l'étape 6, la Cathédrale enterrée (tools/gen_decors_e6.py) : la surface (la fissure)
## et chaque lieu souterrain reçoivent un fond fixe env_e6_plan3_<nom>_NN, posé en (0, 0) dans
## leur repère, derrière le jeu ; les gris de la maquette sont masqués. L'écran inverse tout :
## les fonds sont dessinés pour ça (le vide en papier, la lumière en hachures serrées).
## Le village garde ouverte la galerie d'où vient Tobie : l'éboulement (fx_eboule-village) est un
## calque qui n'apparaît qu'après la ciné e6_eboulement.

const DOSSIER := "res://assets/graphics/env/e6/env_e6_"
## [chemin du nœud sous l'étape, nom du fond].
const LIEUX := [
	["Surface/Fissure", "fissure"],
	["Lieux/Nef", "nef"],
	["Lieux/Village", "village"],
	["Lieux/NicheVeilleur", "niche"],
	["Lieux/Seuil", "seuil"],
]
const Z_LIEU := -20
## Calque au-dessus du fond, toujours derrière le jeu.
const Z_CALQUE := -19
const FX_EBOULE := "res://assets/graphics/fx/fx_eboule-village.png"
const VILLAGE := "Lieux/Village"
## Coin haut-gauche du calque dans le repère du village (EBOULE_X, EBOULE_Y de gen_decors_e6.py).
const ANCRE_EBOULE := Vector2(790, 330)
const CINE_EBOULEMENT: StringName = &"e6_eboulement"

@export var masquer_fonds_maquette: bool = true

var _eboule: Sprite2D


func _ready() -> void:
	var etape := get_parent()
	if etape == null:
		return
	for l: Array in LIEUX:
		var lieu := etape.get_node_or_null(String(l[0])) as Node2D
		if lieu == null:
			continue
		var fond := dessin_lieu("%splan3_%s" % [DOSSIER, String(l[1])], "Dessin", Z_LIEU)
		if fond == null:
			continue
		lieu.add_child(fond)
		lieu.move_child(fond, 0)
		if masquer_fonds_maquette:
			masquer_gris_lieu(lieu)
	var village := etape.get_node_or_null(VILLAGE) as Node2D
	if village != null:
		_eboule = Sprite2D.new()
		_eboule.name = "Eboulement"
		_eboule.texture = charger_tuile(FX_EBOULE)
		_eboule.centered = false
		_eboule.position = ANCRE_EBOULE
		_eboule.z_as_relative = false
		_eboule.z_index = Z_CALQUE
		village.add_child(_eboule)
	GameState.rencontre_vue_marquee.connect(_sur_rencontre_vue)
	maj_calques()


func _exit_tree() -> void:
	if GameState.rencontre_vue_marquee.is_connected(_sur_rencontre_vue):
		GameState.rencontre_vue_marquee.disconnect(_sur_rencontre_vue)


func _sur_rencontre_vue(id: StringName) -> void:
	if id == Cinematique.drapeau(CINE_EBOULEMENT):
		maj_calques()


func maj_calques() -> void:
	if _eboule != null:
		_eboule.visible = GameState.rencontre_vue(Cinematique.drapeau(CINE_EBOULEMENT))
