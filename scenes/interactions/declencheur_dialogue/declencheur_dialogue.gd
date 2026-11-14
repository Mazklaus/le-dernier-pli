class_name DeclencheurDialogue
extends Area2D
## Point d'interaction : lance un dialogue quand le messager appuie sur « interagir ».
## Tout se règle dans l'inspecteur, sans code par rencontre :
## - un verrou (`rencontre_requise`) joue un autre titre tant qu'une rencontre n'a pas été vue
##   (ex. Jacquot : `refus_sans_cendre` tant que `e1_cendre` n'est pas vue, puis `debut`) ;
## - `fin_etape` appelle SceneRouter.etape_suivante() à la fin du dialogue (ex. le parapet).
## Calque de collision 3 (« interactions ») : seul le détecteur du messager le voit.

signal dialogue_commence(declencheur: DeclencheurDialogue)
signal dialogue_termine(declencheur: DeclencheurDialogue)

const GROUPE: StringName = &"declencheurs"

## Identifiant de rencontre du plan (ex. &"e1_adieu").
@export var rencontre_id: StringName
@export var dialogue: DialogueResource
@export var titre: String = "debut"
## Texte d'invite pour l'UI (ex. « Parler à Jacquot »).
@export var libelle: String = ""

@export_group("Verrou")
## Tant que cette rencontre n'est pas vue, on joue `titre_si_verrouille`.
@export var rencontre_requise: StringName
@export var titre_si_verrouille: String = ""

@export_group("Comportement")
## Le déclencheur s'éteint une fois sa rencontre jouée (titre principal).
@export var une_seule_fois: bool = false
## À la fin du dialogue principal, passe à l'étape suivante.
@export var fin_etape: bool = false

var en_cours: bool = false


func _ready() -> void:
	add_to_group(GROUPE)


func est_verrouille() -> bool:
	return rencontre_requise != &"" and titre_si_verrouille != "" \
		and not GameState.rencontre_vue(rencontre_requise)


func titre_a_jouer() -> String:
	return titre_si_verrouille if est_verrouille() else titre


func est_disponible() -> bool:
	if dialogue == null or en_cours:
		return false
	if une_seule_fois and not est_verrouille() and GameState.rencontre_vue(rencontre_id):
		return false
	return true


func interagir(_messager: Node) -> void:
	if not est_disponible():
		return
	var verrouille := est_verrouille()
	en_cours = true
	dialogue_commence.emit(self)
	DialogueManager.show_dialogue_balloon(dialogue, titre_a_jouer())
	await DialogueManager.dialogue_ended
	terminer(verrouille)


## Fin du dialogue : la rencontre n'est comptée comme vue que si son titre principal a été joué.
func terminer(etait_verrouille: bool) -> void:
	en_cours = false
	if not etait_verrouille:
		GameState.marquer_rencontre_vue(rencontre_id)
	dialogue_termine.emit(self)
	if fin_etape and not etait_verrouille:
		SceneRouter.etape_suivante()
