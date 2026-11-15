class_name VerrouRetour
extends StaticBody2D
## Verrou de retour : l'inverse d'un Verrou. Ouvert (invisible, sans collision) au départ, il
## se ferme derrière le messager une fois la rencontre vue et le verrou franchi vers la droite
## de `marge` px, et ne se rouvre plus (ex. le fil qui retombe derrière Tobie à la sortie du
## brouillard, étape 2). Ses formes de collision sont activées et il devient visible.

signal ferme(verrou: VerrouRetour)

@export var rencontre: StringName
## Distance à franchir au-delà du verrou avant qu'il ne retombe.
@export var marge: float = 80.0

var est_ferme: bool = false


func _ready() -> void:
	_appliquer()


func _physics_process(_delta: float) -> void:
	if est_ferme:
		return
	var messager := get_tree().get_first_node_in_group(Messager.GROUPE) as Node2D
	if messager != null and doit_se_fermer(messager.global_position.x):
		fermer()


func doit_se_fermer(x_messager: float) -> bool:
	if rencontre != &"" and not GameState.rencontre_vue(rencontre):
		return false
	return x_messager > global_position.x + marge


func fermer() -> void:
	if est_ferme:
		return
	est_ferme = true
	_appliquer()
	ferme.emit(self)


func _appliquer() -> void:
	visible = est_ferme
	for enfant in get_children():
		if enfant is CollisionShape2D or enfant is CollisionPolygon2D:
			enfant.set_deferred(&"disabled", not est_ferme)
