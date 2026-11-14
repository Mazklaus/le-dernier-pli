class_name InterfaceJeu
extends CanvasLayer
## Interface en jeu : le HUD des jauges (lit GameState seul) et l'invite d'interaction.
## Instanciée par EtapeBase quand l'étape n'en a pas (zéro câblage par étape).

const SCENE := "res://scenes/ui/interface_jeu/interface_jeu.tscn"

@onready var hud: HudJauges = %HudJauges
@onready var invite: InviteInteraction = %InviteInteraction


func _process(_delta: float) -> void:
	invite.zones_interdites = hud.zones_plaques()


## Branche l'interface sur le messager de l'étape.
func brancher(messager: Messager) -> void:
	invite.suivre(messager)
