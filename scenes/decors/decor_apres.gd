class_name DecorApres
extends Sprite2D
## Objet de décor qui n'apparaît qu'une fois un drapeau marqué, et reste là au rechargement
## (ex. le bocal d'Éloi, posé devant la porte du seuil à la fin de la ciné e6_porte_scellee).
## La position est le coin haut-gauche de l'image.

@export var drapeau: StringName


func _ready() -> void:
	centered = false
	GameState.rencontre_vue_marquee.connect(_sur_rencontre_vue_marquee)
	GameState.etat_charge.connect(maj)
	maj()


func _sur_rencontre_vue_marquee(_id: StringName) -> void:
	maj()


func maj() -> void:
	visible = drapeau != &"" and GameState.rencontre_vue(drapeau)
