class_name DecorE6
extends DecorParallaxe
## Décor de l'étape 6, la Cathédrale enterrée (tools/gen_decors_e6.py) : la surface (la fissure)
## et chaque lieu souterrain reçoivent un fond fixe env_e6_plan3_<nom>_NN, posé en (0, 0) dans
## leur repère, derrière le jeu ; les gris de la maquette sont masqués. L'écran inverse tout :
## les fonds sont dessinés pour ça (le vide en papier, la lumière en hachures serrées).

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

@export var masquer_fonds_maquette: bool = true


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
