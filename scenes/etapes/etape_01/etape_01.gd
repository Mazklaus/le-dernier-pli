extends Node2D
## Étape 1 : La Tranchée-Mère (tranche verticale du jalon 1).
## Maquette grise du Level Designer : surface continue (boyau arrière, carrefour,
## pied de l'échelle) et lieux souterrains en sous-scènes (scenes/etapes/etape_01/lieux/).
## Plan de référence : https://claude.ai/artifact/4avYedGZ1zMuy78hUwjhAb
##
## Chaque rencontre est une Area2D du groupe « declencheurs_rencontre », nommée par son
## identifiant (&"e1_ordre"…) et portant la métadonnée dialogue_id. Chaque lieu
## souterrain expose des Marker2D entree_<lieu> / sortie_<lieu>.
## Tant que le messager n'existe pas, la caméra de maquette se déplace avec
## deplacer_gauche / deplacer_droite pour parcourir la surface.

const DIALOGUE := preload("res://dialogue/etape_01/exemple.dialogue")
const GROUPE_RENCONTRES: StringName = &"declencheurs_rencontre"
const GROUPE_MESSAGER: StringName = &"messager"
const VITESSE_CAMERA := 960.0

@onready var _camera: Camera2D = $CameraBlockout


func _process(delta: float) -> void:
	if _messager() != null:
		return
	var direction := Input.get_axis(&"deplacer_gauche", &"deplacer_droite")
	_camera.position.x += direction * VITESSE_CAMERA * delta


## Saut de débogage : place le messager (ou, à défaut, la caméra) devant la rencontre.
func aller_rencontre(id: StringName) -> void:
	var cible := declencheur(id)
	if cible == null:
		push_warning("Étape 1 : rencontre %s introuvable dans la maquette" % id)
		return
	var messager := _messager()
	if messager != null:
		messager.global_position = Vector2(cible.global_position.x - 160.0, cible.global_position.y + 150.0)
	else:
		_camera.global_position = cible.global_position


## Renvoie le déclencheur d'une rencontre, ou null.
func declencheur(id: StringName) -> Area2D:
	for noeud in get_tree().get_nodes_in_group(GROUPE_RENCONTRES):
		if is_ancestor_of(noeud) and noeud.get_meta(&"dialogue_id", &"") == id:
			return noeud as Area2D
	return null


func _messager() -> Node2D:
	return get_tree().get_first_node_in_group(GROUPE_MESSAGER) as Node2D
