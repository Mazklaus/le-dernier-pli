class_name EtapeBase
extends Node2D
## Base des scènes d'étape. Fournit le saut de débogage attendu par SceneRouter :
## aller_rencontre(id) pose le messager devant le DeclencheurDialogue de cette rencontre.
## Ajoute aussi l'interface en jeu (InterfaceJeu) si l'étape n'en a pas.
## Voix de surface : si l'étape a un nœud « ReperesVoix » (Marker2D boyau_arriere, carrefour,
## periscope, pied_echelle), le gain des voix suit le messager tant qu'il est à la surface
## (y ≤ limite_surface_y), et revient plein sous terre. Mis à jour à chaque téléportation.
## Une étape qui redéfinit _ready() doit appeler super().

const NOEUD_REPERES_VOIX := "ReperesVoix"

## Ordonnée (globale) sous laquelle le messager est sous terre (lieux souterrains).
@export var limite_surface_y: float = INF
## Numéro de l'étape (musiques AudioDirector.jouer_musique).
@export var numero_etape: int = 0
## Musique par lieu : franchir un Passage vers un de ces lieux lance la musique du moment
## associé (fondu entrant) ; vers tout autre lieu, elle s'arrête (fondu sortant).
## Ex. étape 1 : {&"abri_sergent": "theme", &"chapelle": "theme"}.
@export var lieux_musique: Dictionary = {}


func _ready() -> void:
	ajouter_interface()
	brancher_suivi_voix()
	brancher_musique_lieux()


## Relie les Passages de l'étape à la musique par lieu (lieux_musique).
func brancher_musique_lieux() -> void:
	if lieux_musique.is_empty():
		return
	for n in get_tree().get_nodes_in_group(&"passages"):
		if n is Passage and is_ancestor_of(n):
			var passage := n as Passage
			if not passage.franchi.is_connected(_sur_passage_franchi):
				passage.franchi.connect(_sur_passage_franchi)


func _sur_passage_franchi(_passage: Passage, vers: StringName) -> void:
	if lieux_musique.has(vers):
		AudioDirector.jouer_musique(numero_etape, String(lieux_musique[vers]))
	else:
		AudioDirector.arreter_musique()


## Relie le gain des voix de surface (AudioDirector) à la position du messager.
func brancher_suivi_voix() -> void:
	var messager := trouver_messager()
	if messager == null or reperes_voix().is_empty():
		return
	if not messager.teleporte.is_connected(_sur_teleporte):
		messager.teleporte.connect(_sur_teleporte)
	# Différé : l'étape place encore le messager au départ après super()._ready().
	maj_suivi_voix.call_deferred()


func reperes_voix() -> Array[Marker2D]:
	var reperes: Array[Marker2D] = []
	var noeud := get_node_or_null(NOEUD_REPERES_VOIX)
	if noeud != null:
		for enfant in noeud.get_children():
			if enfant is Marker2D:
				reperes.append(enfant as Marker2D)
	return reperes


func est_en_surface(position_globale: Vector2) -> bool:
	return position_globale.y <= limite_surface_y


func maj_suivi_voix() -> void:
	var messager := trouver_messager()
	if messager == null:
		return
	if est_en_surface(messager.global_position):
		AudioDirector.definir_suivi_voix(messager, reperes_voix())
	else:
		AudioDirector.arreter_suivi_voix()


func _sur_teleporte(_position_globale: Vector2) -> void:
	maj_suivi_voix()


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
