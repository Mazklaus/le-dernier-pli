class_name InterfaceJeu
extends CanvasLayer
## Interface en jeu, portée par le messager (une par étape, sans câblage du Level Designer) :
## l'invite d'interaction, et plus tard le HUD des jauges.

@onready var invite: InviteInteraction = %InviteInteraction


func _ready() -> void:
	var messager := get_parent() as Messager
	if messager != null:
		invite.suivre(messager)
