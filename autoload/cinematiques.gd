extends Node
## Lance les cinématiques (nœuds Cinematique de la scène courante) par leur identifiant.
## Depuis un .dialogue : `do Cinematiques.jouer(&"e1_remise_pli")` ; le dialogue reprend à la fin.
## Une cinématique pas encore placée par le Level Designer ne fait rien (avertissement en
## debug) : les dialogues peuvent être balisés avant les plans.

signal commencee(id: StringName)
signal terminee(id: StringName, sautee: bool)

## Les nœuds de ce groupe (bulle, interface en jeu) sont masqués pendant une cinématique.
const GROUPE_MASQUE := &"masque_en_cinematique"

var en_cours: StringName = &""
var _masques: Array[Node] = []


func trouver(id: StringName) -> Cinematique:
	for n in get_tree().get_nodes_in_group(Cinematique.GROUPE):
		if n is Cinematique and (n as Cinematique).id == id:
			return n as Cinematique
	return null


## Joue la cinématique `id` et attend sa fin. Renvoie true si elle a été sautée.
func jouer(id: StringName) -> bool:
	var cine := trouver(id)
	if cine == null:
		if OS.has_feature("debug"):
			push_warning("Cinematiques : « %s » n'est pas placée dans cette scène" % id)
		return false
	if cine.une_seule_fois and cine.deja_vue():
		return false
	en_cours = id
	commencee.emit(id)
	var sautee: bool = await cine.jouer()
	en_cours = &""
	terminee.emit(id, sautee)
	return sautee


func masquer_interface(masquer: bool) -> void:
	if masquer:
		_masques.clear()
		for n in get_tree().get_nodes_in_group(GROUPE_MASQUE):
			if n is CanvasItem and (n as CanvasItem).visible:
				(n as CanvasItem).visible = false
				_masques.append(n)
			elif n is CanvasLayer and (n as CanvasLayer).visible:
				(n as CanvasLayer).visible = false
				_masques.append(n)
	else:
		for n in _masques:
			if is_instance_valid(n):
				n.set(&"visible", true)
		_masques.clear()
