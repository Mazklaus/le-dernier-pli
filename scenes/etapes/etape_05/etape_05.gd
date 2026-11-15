extends EtapeBase
## Étape 5 : la Forêt de Croix.
## Maquette grise du Level Designer : une boucle. Le bout du sentier (Passage « Continuer »,
## sans fondu) ramène devant la même croix-repère. Le tour n'est complet qu'après e5_autre
## (verrou « Fourre » avant le bout) : la croix joue premier_passage jusque-là, puis debut.
## Décisions du Game Director pour que la boucle ne passe jamais pour un bug : l'entaille est
## visible sur la croix dès que Tobie l'a faite, et debut se lance tout seul au retour.
## Ensuite « Quitter le sentier » (e5_sentier), campement, cimetière, clairière (fin d'étape).
## Plan de référence : https://claude.ai/artifact/H1ng4JRzZ6SSBGZNLrTp6v

## Le messager entre dans la forêt par l'orée.
const POINT_DE_DEPART: StringName = &"entree_oree"
const CROIX: StringName = &"e5_sentier"
## Posée par premier_passage si Tobie entaille la croix (dialogue de la Narrative).
const ENTAILLE_FAITE: StringName = &"e5_entaille_faite"


func _ready() -> void:
	super()
	var messager := trouver_messager()
	var depart := find_child(String(POINT_DE_DEPART), true, false) as Marker2D
	if messager != null and depart != null:
		messager.global_position = depart.global_position
	var boucle := find_child("Continuer", true, false) as Passage
	if boucle != null:
		boucle.franchi.connect(_sur_retour_de_boucle)
	GameState.rencontre_vue_marquee.connect(_sur_rencontre_vue)
	maj_entaille()


func _exit_tree() -> void:
	if GameState.rencontre_vue_marquee.is_connected(_sur_rencontre_vue):
		GameState.rencontre_vue_marquee.disconnect(_sur_rencontre_vue)


func _sur_rencontre_vue(id: StringName) -> void:
	if id == ENTAILLE_FAITE:
		maj_entaille()


func maj_entaille() -> void:
	var croix := trouver_declencheur(CROIX)
	var entaille := croix.get_node_or_null("Entaille") as CanvasItem if croix != null else null
	if entaille != null:
		entaille.visible = GameState.rencontre_vue(ENTAILLE_FAITE)


## Au retour devant la croix, Tobie reconnaît l'endroit sans que le joueur ait à appuyer.
func _sur_retour_de_boucle(_passage: Passage, _vers: StringName) -> void:
	var croix := trouver_declencheur(CROIX)
	if croix != null and croix.est_disponible() and not croix.est_verrouille():
		croix.interagir.call_deferred(trouver_messager())
