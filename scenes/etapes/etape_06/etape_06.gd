extends EtapeBase
## Étape 6 : la Cathédrale enterrée.
## Maquette grise du Level Designer : une plongée puis un renversement. La fissure (surface)
## mène à la nef engloutie (zone sombre ouverte par e6_nef, fermée par e6_eloi), puis au
## village enfoui, chaud, reflet inversé de la place de l'étape 3 (tablée au centre, niche du
## veilleur à la place du clocher), et au seuil de la Mère-Cloche (e6_seuil, fin d'étape).
## Pas de retour vers la nef ; seule la niche fait un aller-retour.
## Plan de référence : https://claude.ai/artifact/4ZXpkJraK9xWfuj5o6fYFq

## Le messager arrive de la clairière de la forêt par la fissure.
const POINT_DE_DEPART: StringName = &"entree_fissure"


func _ready() -> void:
	super()
	var messager := trouver_messager()
	var depart := find_child(String(POINT_DE_DEPART), true, false) as Marker2D
	if messager != null and depart != null:
		messager.global_position = depart.global_position
