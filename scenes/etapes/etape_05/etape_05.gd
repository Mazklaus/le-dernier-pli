extends EtapeBase
## Étape 5 : la Forêt de Croix.
## Maquette grise du Level Designer : une boucle. Le bout du sentier ramène, sans fondu, devant
## la même croix-repère (e5_sentier : premier_passage pose e5_entaille, debut au second
## passage). « Quitter le sentier » s'ouvre sur e5_sentier, puis campement, cimetière des
## coureurs (le pic) et clairière (fin d'étape), en ligne. Pas de zone sombre.
## Plan de référence : https://claude.ai/artifact/H1ng4JRzZ6SSBGZNLrTp6v

## Le messager entre dans la forêt par l'orée.
const POINT_DE_DEPART: StringName = &"entree_oree"


func _ready() -> void:
	super()
	var messager := trouver_messager()
	var depart := find_child(String(POINT_DE_DEPART), true, false) as Marker2D
	if messager != null and depart != null:
		messager.global_position = depart.global_position
