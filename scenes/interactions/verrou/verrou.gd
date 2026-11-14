class_name Verrou
extends StaticBody2D
## Obstacle qui s'efface quand une rencontre a été vue (ex. la Chicane après e1_ordre,
## le VerrouCendre après e1_cendre). On peut poser ce script directement sur un
## StaticBody2D existant de la maquette : ses formes de collision sont désactivées
## et il est masqué une fois ouvert.

signal ouvert(verrou: Verrou)

@export var rencontre: StringName


func _ready() -> void:
	GameState.rencontre_vue_marquee.connect(_sur_rencontre_vue)
	GameState.etat_charge.connect(actualiser)
	actualiser()


func est_ouvert() -> bool:
	return rencontre != &"" and GameState.rencontre_vue(rencontre)


func actualiser() -> void:
	var o := est_ouvert()
	visible = not o
	for enfant in get_children():
		if enfant is CollisionShape2D or enfant is CollisionPolygon2D:
			enfant.set_deferred(&"disabled", o)


func _sur_rencontre_vue(id: StringName) -> void:
	if id == rencontre:
		actualiser()
		ouvert.emit(self)
