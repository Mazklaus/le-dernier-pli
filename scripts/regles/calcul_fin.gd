class_name CalculFin
extends RefCounted
## Calcul de la fin : fonction pure de `marques` et `sceau_ouvert` (spec jauges v0.1, § Calcul de la fin).
## Aucune dépendance à l'arbre de scènes ni à GameState : testable seule.

const FIN_PORTEUR: StringName = &"porteur"
const FIN_ORDRE: StringName = &"ordre"
const FIN_DERNIER_PLI: StringName = &"dernier_pli"
const FIN_RECOUSU: StringName = &"recousu"


## Ombre = Cicatrices + Reliques + Promesses trahies.
static func score_ombre(marques: Array) -> int:
	var total := 0
	for m: Dictionary in marques:
		var famille: StringName = StringName(m.get("famille", ""))
		var etat: StringName = StringName(m.get("etat", ""))
		if famille == Marques.CICATRICE or famille == Marques.RELIQUE:
			total += 1
		elif famille == Marques.PROMESSE and etat == Marques.TRAHIE:
			total += 1
	return total


## Visage = Noms retenus + Promesses tenues (une Promesse ouverte compte 0).
static func score_visage(marques: Array) -> int:
	var total := 0
	for m: Dictionary in marques:
		var famille: StringName = StringName(m.get("famille", ""))
		var etat: StringName = StringName(m.get("etat", ""))
		if famille == Marques.NOM_RETENU:
			total += 1
		elif famille == Marques.PROMESSE and etat == Marques.TENUE:
			total += 1
	return total


## L'égalité penche vers le Visage.
static func garde_un_visage(marques: Array) -> bool:
	return score_visage(marques) >= score_ombre(marques)


static func calculer(marques: Array, sceau_ouvert: bool) -> StringName:
	var visage := garde_un_visage(marques)
	if sceau_ouvert:
		return FIN_DERNIER_PLI if visage else FIN_RECOUSU
	return FIN_PORTEUR if visage else FIN_ORDRE
