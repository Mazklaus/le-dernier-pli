extends Node2D
## Étape 1 : La Tranchée-Mère (tranche verticale du jalon 1).
## Squelette : zone vide. Le Level Designer fournit le plan, le Gameplay Prog
## le messager et les interactions, le Narrative Designer les dialogues.

const DIALOGUE := preload("res://dialogue/etape_01/exemple.dialogue")


## Saut de débogage : place le messager devant la rencontre demandée.
func aller_rencontre(id: StringName) -> void:
	push_warning("Étape 1 : rencontre %s pas encore placée" % id)
