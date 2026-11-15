class_name DecorE3
extends DecorParallaxe
## Décor de surface de l'étape 3, le Village aux cloches muettes (planche du DA) : cinq plans
## parallaxes pour la lisière et la rue (7680 px), sol à y 900. Un village trop intact :
## les deux fausses notes (lampions pendus à l'envers, baie du clocher vide) sont peintes dans
## le plan 3. La nuit vient de la teinte d'EtapeBase : aucun modulate ici.
## Masque les fonds, sols et murs gris de la maquette (Surface/*/Fond, Sol, Mur*).
## Les lieux (maison d'Ilde, clocher, chambre, chemins) gardent leur gris pour l'instant.

const DOSSIER := "res://assets/graphics/env/e3/env_e3_"
## [nom du plan, vitesse, couche] du plus lointain au plus proche.
const PLANS := [
	["plan0_ciel", 0.05, -50],
	["plan1_lointain", 0.2, -40],
	["plan2_milieu", 0.5, -30],
	["plan3_surface", 1.0, -20],
	["plan4_premier-plan", 1.4, 20],
]

@export var masquer_fonds_maquette: bool = true

var plans: Array[Parallax2D] = []


func _ready() -> void:
	for p: Array in PLANS:
		var plan := creer_plan(DOSSIER + String(p[0]), float(p[1]), int(p[2]))
		if plan != null:
			add_child(plan)
			plans.append(plan)
	if masquer_fonds_maquette and not plans.is_empty():
		masquer_fonds_gris()
