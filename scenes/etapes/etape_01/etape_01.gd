extends EtapeBase
## Étape 1 : La Tranchée-Mère (tranche verticale du jalon 1).
## Maquette grise du Level Designer : surface continue (boyau arrière, carrefour,
## pied de l'échelle) et lieux souterrains en sous-scènes (scenes/etapes/etape_01/lieux/).
## Plan de référence : https://claude.ai/artifact/4avYedGZ1zMuy78hUwjhAb
##
## Chaque rencontre est un DeclencheurDialogue nommé par son identifiant (&"e1_ordre"…).
## Chaque lieu souterrain expose des Marker2D entree_<lieu> / sortie_<lieu>, et la surface
## des Marker2D porte_<lieu> pour l'arrivée au retour. Le saut de débogage vient d'EtapeBase.

const DIALOGUE := preload("res://dialogue/etape_01/exemple.dialogue")
## Le réveil se joue dans la couchette : le messager y démarre.
const POINT_DE_DEPART: StringName = &"entree_couchette"


func _ready() -> void:
	super()
	var messager := trouver_messager()
	var depart := find_child(String(POINT_DE_DEPART), true, false) as Marker2D
	if messager != null and depart != null:
		messager.global_position = depart.global_position
