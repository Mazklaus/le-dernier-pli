class_name EtapeBase
extends Node2D
## Base des scènes d'étape. Fournit le saut de débogage attendu par SceneRouter :
## aller_rencontre(id) pose le messager devant le DeclencheurDialogue de cette rencontre.


func aller_rencontre(id: StringName) -> void:
	var messager := trouver_messager()
	var declencheur := trouver_declencheur(id)
	if messager == null or declencheur == null:
		push_warning("%s : rencontre %s introuvable (messager ou déclencheur absent)" % [name, id])
		return
	messager.placer_devant(declencheur)


func trouver_messager() -> Messager:
	for n in get_tree().get_nodes_in_group(Messager.GROUPE):
		if n is Messager and is_ancestor_of(n):
			return n as Messager
	return null


func trouver_declencheur(id: StringName) -> DeclencheurDialogue:
	for n in get_tree().get_nodes_in_group(Interactif.GROUPE):
		if n is DeclencheurDialogue and is_ancestor_of(n) and (n as DeclencheurDialogue).rencontre_id == id:
			return n as DeclencheurDialogue
	return null
