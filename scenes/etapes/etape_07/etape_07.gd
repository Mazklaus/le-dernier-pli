extends EtapeBase
## Étape 7 : le Destinataire.
## Maquette grise du Level Designer : la descente finale en spirale le long de la plus grande
## cloche. En vue de côté, des anneaux superposés : au bout de chacun, Tobie passe derrière la
## cloche (Passage sans fondu) vers l'anneau du dessous, et le sens de marche s'inverse.
## Galerie → cloches tues (e7_cloches) → Lise (e7_lise) → dernière porte (e7_sceau) → sous la
## Mère-Cloche (e7_mere_cloche, fin d'étape, 4 fins). Aucun retour vers le haut.
## Plan de référence : https://claude.ai/artifact/SKhvHgc3VA9zJK9gbnNjQL

## Le messager arrive par la porte de la Mère-Cloche, en haut de la grande salle.
const POINT_DE_DEPART: StringName = &"entree_galerie"


func _ready() -> void:
	super()
	var messager := trouver_messager()
	var depart := find_child(String(POINT_DE_DEPART), true, false) as Marker2D
	if messager != null and depart != null:
		messager.global_position = depart.global_position
