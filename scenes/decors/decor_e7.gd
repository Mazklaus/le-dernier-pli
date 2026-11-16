class_name DecorE7
extends DecorParallaxe
## Décor de l'étape 7, le Destinataire (tools/gen_decors_e7.py) : la galerie du haut du puits et
## chaque lieu de la descente reçoivent un fond fixe env_e7_plan3_<nom>_NN, posé en (0, 0) dans
## leur repère, derrière le jeu ; les gris de la maquette sont masqués. Écran clair, sans accent :
## le flanc de la grande cloche derrière chaque anneau, des cloches cirées dans le vide.

const DOSSIER := "res://assets/graphics/env/e7/env_e7_"
## [chemin du nœud sous l'étape, nom du fond].
const LIEUX := [
	["Surface/Galerie", "galerie"],
	["Lieux/AnneauCloches", "anneau-cloches"],
	["Lieux/AnneauLise", "anneau-lise"],
	["Lieux/AnneauPorte", "anneau-porte"],
	["Lieux/MereCloche", "mere-cloche"],
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
