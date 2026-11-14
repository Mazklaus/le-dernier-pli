extends EtapeBase
## Étape 2 : le No Man's Land.
## Maquette grise du Level Designer : une seule surface continue, sans retour, sur un sol à
## trois hauteurs (crête du poste, fond des trous d'obus), et un lieu souterrain facultatif,
## le vieux boyau sous le poste (scenes/etapes/etape_02/lieux/).
## Plan de référence : https://claude.ai/artifact/35soMAhr4mFiMqi6th6P1F
##
## Les rencontres sont des DeclencheurDialogue nommés par leur identifiant (&"e2_poste"…).
## Les verrous du chemin s'ouvrent sur des rencontres marquées par les dialogues :
## e2_poste_passe (chicane), e2_barbeles et e2_barbeles_ceinture2 (les deux ceintures).

## Le messager débouche de l'échelle sur le parapet.
const POINT_DE_DEPART: StringName = &"entree_parapet"


func _ready() -> void:
	super()
	var messager := trouver_messager()
	var depart := find_child(String(POINT_DE_DEPART), true, false) as Marker2D
	if messager != null and depart != null:
		messager.global_position = depart.global_position
