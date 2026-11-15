class_name DecorE4
extends DecorParallaxe
## Décor de l'étape 4, l'Hôpital des Recousus (tools/gen_decors_e4.py) : toute l'étape est faite
## de pièces fermées, sans parallaxe. Chaque section (le porche et la rue latérale, à ciel
## ouvert) et chaque lieu reçoit un fond fixe env_e4_plan3_<nom>_NN, posé en (0, 0) dans son
## repère, derrière le jeu ; les gris de la maquette (Fond, Sol, Plafond, Mur*) sont masqués.

const DOSSIER := "res://assets/graphics/env/e4/env_e4_"
## [chemin du nœud sous l'étape, nom du fond].
const LIEUX := [
	["Surface/Porche", "porche"],
	["Lieux/Salle", "salle"],
	["Lieux/Lingerie", "lingerie"],
	["Lieux/Atelier", "atelier"],
	["Lieux/Escalier", "escalier"],
	["Lieux/Crypte", "crypte"],
	["Lieux/EscalierService", "escalier-service"],
	["Surface/RueLaterale", "rue-laterale"],
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
