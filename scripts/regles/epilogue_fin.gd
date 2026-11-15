class_name EpilogueFin
extends RefCounted
## Carton d'épilogue : de la fin calculée (CalculFin) au titre de e7_epilogues.dialogue, à la
## gravure cin_epilogue-<lettre> du DA et au Cantique mus_destinataire_fin-<lettre> du Sound
## Designer. La table lettre → fin vit ici et dans tools/son/README.md, jamais dans un nom de
## fichier (règle du Game Director). Fonctions pures, testables sans scène.

const DIALOGUE := "res://dialogue/etape_07/e7_epilogues.dialogue"
const GRAVURE := "res://assets/graphics/cin/cin_epilogue-%s.png"

const PORTEUR := "porteur"
const ORDRE := "ordre"
const DERNIER_PLI_TRIBUT := "dernier_pli_tribut"
const DERNIER_PLI_CLOCHES := "dernier_pli_cloches"
const RECOUSU := "recousu"

## Clé d'épilogue → lettre (tools/son/README.md : a Le Battant, b Le Dernier Pli sacrifice,
## c Le Dernier Pli refus, d Le Quatorzième, e La Remontée).
const LETTRES := {
	PORTEUR: "a",
	DERNIER_PLI_TRIBUT: "b",
	DERNIER_PLI_CLOCHES: "c",
	ORDRE: "d",
	RECOUSU: "e",
}

## Drapeau posé par le choix de Tobie dans e7_mere_cloche (fin dernier_pli).
const DRAPEAU_CLOCHES: StringName = &"fin_dernier_pli_cloches"

## Libellés des Noms retenus et des Promesses sur le carton (Narrative Designer).
## Une marque absente de la table est affichée d'après son identifiant.
const LIBELLES := {
	&"jacquot": "Jacquot",
	&"hugues_lamarre": "Hugues",
	&"il_s_appelait_aurele": "Aurèle",
	&"il_s_appelait_gaspard": "Gaspard",
	&"il_s_appelait_matthieu": "Matthieu",
	&"elle_s_appelait_rose": "Rose",
	&"il_s_appelait_fernand": "Fernand",
	&"il_s_appelait_aubin": "Aubin",
	&"il_s_appelait_mathurin": "Mathurin",
	&"ceux_d_avant": "Ceux d'avant",
	&"la_langue_d_en_dessous": "La langue d'en dessous",
	&"promis_a_jacquot": "Du pain blanc pour Jacquot",
	&"promis_a_ilde": "Rester chez Ilde, volets clos",
	&"la_lettre_de_matthieu": "La lettre de Matthieu",
}


## Clé de l'épilogue : la fin, et pour dernier_pli le choix fait sous la cloche
## (sans drapeau des cloches, le tribut).
static func cle(fin: StringName, cloches_sonnees: bool) -> String:
	if fin == CalculFin.FIN_DERNIER_PLI:
		return DERNIER_PLI_CLOCHES if cloches_sonnees else DERNIER_PLI_TRIBUT
	return String(fin) if LETTRES.has(String(fin)) else PORTEUR


static func lettre(cle_epilogue: String) -> String:
	return String(LETTRES.get(cle_epilogue, "a"))


static func titre(cle_epilogue: String) -> String:
	return "epilogue_" + cle_epilogue


static func gravure(cle_epilogue: String) -> String:
	return GRAVURE % lettre(cle_epilogue)


## Moment du Cantique pour AudioDirector.jouer_epilogue.
static func moment(cle_epilogue: String) -> String:
	return "fin-" + lettre(cle_epilogue)


static func libelle(id: StringName) -> String:
	if LIBELLES.has(id):
		return String(LIBELLES[id])
	var texte := String(id).replace("_", " ").strip_edges()
	return texte.substr(0, 1).to_upper() + texte.substr(1)


## Noms retenus, dans l'ordre où Tobie les a reçus.
static func noms_retenus(marques: Array) -> PackedStringArray:
	var noms := PackedStringArray()
	for m: Dictionary in marques:
		if StringName(m.get("famille", "")) == Marques.NOM_RETENU:
			noms.append(libelle(StringName(m.get("id", ""))))
	return noms


## Promesses encore ouvertes au moment du carton.
static func promesses_ouvertes(marques: Array) -> PackedStringArray:
	var promesses := PackedStringArray()
	for m: Dictionary in marques:
		if StringName(m.get("famille", "")) == Marques.PROMESSE \
				and StringName(m.get("etat", "")) == Marques.OUVERTE:
			promesses.append(libelle(StringName(m.get("id", ""))))
	return promesses
