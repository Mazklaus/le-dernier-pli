extends EtapeBase
## Étape 3 : le Village aux cloches muettes.
## Maquette grise du Level Designer : de jour, une lisière linéaire puis un hub libre autour de
## la place (maison d'Ilde, clocher) ; le lit chez Ilde (Passage en fondu au noir) bascule
## l'étape en nuit, sans retour. La nuit et l'aube sont deux lieux distincts (chemin_nuit,
## chemin_aube), ouverts par e3_suivre ou e3_rester, que marque la procession à la fenêtre.
## La teinte de nuit vient d'EtapeBase (lieux_nuit).
## Plan de référence : https://claude.ai/artifact/FPwPDussWcnijshgu2QbLB

## Le messager arrive du No Man's Land par la lisière.
const POINT_DE_DEPART: StringName = &"entree_lisiere"


func _ready() -> void:
	super()
	var messager := trouver_messager()
	var depart := find_child(String(POINT_DE_DEPART), true, false) as Marker2D
	if messager != null and depart != null:
		messager.global_position = depart.global_position
