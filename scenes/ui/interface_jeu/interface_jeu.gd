class_name InterfaceJeu
extends CanvasLayer
## Interface en jeu : l'invite d'interaction, et plus tard le HUD des jauges.
## Instanciée par EtapeBase quand l'étape n'en a pas (zéro câblage par étape).

const SCENE := "res://scenes/ui/interface_jeu/interface_jeu.tscn"

@onready var invite: InviteInteraction = %InviteInteraction


## Branche l'interface sur le messager de l'étape.
func brancher(messager: Messager) -> void:
	invite.suivre(messager)
