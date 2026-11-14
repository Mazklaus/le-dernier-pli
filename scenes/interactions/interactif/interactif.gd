class_name Interactif
extends Area2D
## Base de tout ce que le messager peut déclencher avec « interagir » : dialogues, passages…
## Calque de collision 3 (« interactions ») : seul le détecteur du messager le voit.
## Les sous-classes redéfinissent est_disponible() et interagir().

const GROUPE: StringName = &"interactifs"

## Texte d'invite pour l'UI (24 caractères au plus, ex. « Parler à Jacquot »).
@export var libelle: String = ""


func _ready() -> void:
	add_to_group(GROUPE)


func est_disponible() -> bool:
	return true


func interagir(_messager: Messager) -> void:
	pass
