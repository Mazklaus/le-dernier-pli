class_name EtapeBase
extends Node2D
## Base des scènes d'étape. Fournit le saut de débogage attendu par SceneRouter :
## aller_rencontre(id) pose le messager devant le DeclencheurDialogue de cette rencontre.
## Ajoute aussi l'interface en jeu (InterfaceJeu) si l'étape n'en a pas.
## Une étape qui redéfinit _ready() doit appeler super().


func _ready() -> void:
	ajouter_interface()


## Instancie InterfaceJeu et la branche sur le messager, sauf si l'étape en a déjà une.
func ajouter_interface() -> InterfaceJeu:
	for enfant in get_children():
		if enfant is InterfaceJeu:
			return enfant as InterfaceJeu
	var messager := trouver_messager()
	if messager == null:
		return null
	var interface: InterfaceJeu = (load(InterfaceJeu.SCENE) as PackedScene).instantiate()
	add_child(interface)
	interface.brancher(messager)
	return interface


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
