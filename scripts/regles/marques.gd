class_name Marques
extends RefCounted
## Constantes partagées des marques (familles et états de Promesse).

const CICATRICE: StringName = &"cicatrice"
const RELIQUE: StringName = &"relique"
const PROMESSE: StringName = &"promesse"
const NOM_RETENU: StringName = &"nom_retenu"
const FAMILLES: Array[StringName] = [CICATRICE, RELIQUE, PROMESSE, NOM_RETENU]

const OUVERTE: StringName = &"ouverte"
const TENUE: StringName = &"tenue"
const TRAHIE: StringName = &"trahie"

## Marques déclenchées automatiquement par les jauges (première fois).
const LA_FAIM: StringName = &"la_faim"
const CE_QUI_A_ETE_VU: StringName = &"ce_qui_a_ete_vu"


static func creer(id: StringName, famille: StringName) -> Dictionary:
	assert(famille in FAMILLES, "Famille de marque inconnue : %s" % famille)
	var etat: StringName = OUVERTE if famille == PROMESSE else &""
	return {"id": id, "famille": famille, "etat": etat}
