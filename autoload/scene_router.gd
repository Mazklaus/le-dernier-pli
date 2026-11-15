extends Node
## Autoload SceneRouter : enchaîne l'écran titre et les sept étapes.
## Chaque étape est une scène res://scenes/etapes/etape_NN/etape_NN.tscn.
## La racine d'une étape peut exposer aller_rencontre(id) pour le saut de débogage.

signal etape_chargee(numero: int)
## Émis par l'étape elle-même à la fin de son _ready (EtapeBase) : la scène est dans l'arbre,
## on peut s'abonner à ses signaux (ex. phase_changee). etape_chargee part avant le
## changement de scène effectif.
signal etape_prete(etape: Node)

const ECRAN_TITRE := "res://scenes/titre/titre.tscn"
const NB_ETAPES := 7
## Carton d'épilogue, après la dernière étape (fin de la Mère-Cloche).
const ECRAN_EPILOGUE := "res://scenes/epilogue/epilogue.tscn"

var etape_courante: int = 0


func chemin_etape(numero: int) -> String:
	return "res://scenes/etapes/etape_%02d/etape_%02d.tscn" % [numero, numero]


func etape_existe(numero: int) -> bool:
	return numero >= 1 and numero <= NB_ETAPES and ResourceLoader.exists(chemin_etape(numero))


## Charge l'étape demandée. Prévient AudioDirector, puis émet etape_chargee.
func aller_etape(numero: int) -> void:
	if not etape_existe(numero):
		push_error("SceneRouter : étape %d introuvable" % numero)
		return
	etape_courante = numero
	var erreur := get_tree().change_scene_to_file(chemin_etape(numero))
	if erreur != OK:
		push_error("SceneRouter : échec du chargement de l'étape %d (%s)" % [numero, error_string(erreur)])
		return
	AudioDirector.jouer_etape(numero)
	etape_chargee.emit(numero)


## Quitte l'étape courante (coût de la marche dans GameState) et charge la suivante.
## Après la dernière étape : pas de marche, le carton d'épilogue (puis retour au titre).
func etape_suivante() -> void:
	if est_derniere_etape(etape_courante):
		aller_epilogue()
		return
	GameState.passer_etape()
	aller_etape(etape_courante + 1)


## La fin de cette étape mène-t-elle au carton d'épilogue plutôt qu'à une autre étape ?
static func est_derniere_etape(numero: int) -> bool:
	return numero >= NB_ETAPES


func aller_epilogue() -> void:
	get_tree().change_scene_to_file(ECRAN_EPILOGUE)


func retour_titre() -> void:
	etape_courante = 0
	get_tree().change_scene_to_file(ECRAN_TITRE)


## Saut direct vers une rencontre (menu de débogage). Identifiant : &"eN_nom".
func aller_rencontre(id: StringName) -> void:
	var numero := numero_etape_de(id)
	if numero == 0:
		push_error("SceneRouter : identifiant de rencontre invalide %s" % id)
		return
	if numero != etape_courante:
		aller_etape(numero)
		await get_tree().process_frame
		await get_tree().process_frame
	var racine := get_tree().current_scene
	if racine and racine.has_method(&"aller_rencontre"):
		racine.call(&"aller_rencontre", id)
	else:
		push_warning("SceneRouter : l'étape %d ne gère pas aller_rencontre" % numero)


static func numero_etape_de(id: StringName) -> int:
	var texte := String(id)
	if not texte.begins_with("e"):
		return 0
	var prefixe := texte.substr(1).get_slice("_", 0)
	return int(prefixe) if prefixe.is_valid_int() else 0
