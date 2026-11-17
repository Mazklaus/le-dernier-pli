class_name Passage
extends Interactif
## Escalier, trou d'étais, niche : sur « interagir », déplace le messager vers un autre lieu
## de l'étape (surface ↔ lieux souterrains). Destination : le Marker2D `arrivee` s'il est
## renseigné, sinon le Marker2D nommé `entree_<vers>` n'importe où dans la scène d'étape
## (ex. vers = &"couchette" → entree_couchette, vers = &"boyau_arriere" → entree_boyau_arriere).
## On peut poser ce script directement sur une Area2D existante de la maquette.
## `fondu_noir` > 0 : fondu au noir, téléportation et signal `franchi` dans le noir (l'étape
## peut y basculer jour/nuit, éclairage, ambiances), puis retour de l'image.
## `cinematique` : jouée avant le déplacement (ex. la chute dans la fissure de l'étape 6, qui
## suit directement le choix « se laisser tomber ») ; le messager arrive à la fin du plan.

signal franchi(passage: Passage, vers: StringName)

@export var vers: StringName
## Optionnel : force le point d'arrivée.
@export var arrivee: NodePath
## Optionnel : le passage reste fermé tant que cette rencontre n'a pas été vue.
@export var rencontre_requise: StringName
## Durée (s) de chaque moitié du fondu au noir ; 0 = passage instantané.
@export var fondu_noir: float = 0.0
## Bruitage du passage (ex. sfx_echelle_monter pour une échelle) ; vide : l'étape choisit
## l'escalier ou la toile selon le changement de niveau (EtapeBase.son_passage).
@export var son: String = ""
## Optionnel : identifiant de la cinématique jouée avant le déplacement.
@export var cinematique: StringName = &""

const COUCHE_FONDU := 20

var _en_fondu: bool = false


func _ready() -> void:
	super()
	# Toujours dans le groupe, même posé à la main sans groups=["passages"] dans la scène :
	# EtapeBase s'y abonne pour la musique et la bascule jour/nuit.
	add_to_group(&"passages")
	collision_layer = 4
	collision_mask = 0
	monitoring = false
	if vers == &"" and has_meta(&"vers"):
		vers = StringName(get_meta(&"vers"))


func est_disponible() -> bool:
	if _en_fondu:
		return false
	if rencontre_requise != &"" and not GameState.rencontre_vue(rencontre_requise):
		return false
	return trouver_arrivee() != null


func trouver_arrivee() -> Marker2D:
	if not arrivee.is_empty():
		return get_node_or_null(arrivee) as Marker2D
	if vers == &"":
		return null
	var racine := _racine_etape()
	if racine == null:
		return null
	return racine.find_child("entree_%s" % vers, true, false) as Marker2D


func interagir(messager: Messager) -> void:
	var cible := trouver_arrivee()
	if cible == null or not est_disponible():
		return
	if cinematique != &"":
		_en_fondu = true
		await Cinematiques.jouer(cinematique)
		_en_fondu = false
		if not is_instance_valid(messager) or not is_inside_tree():
			return
		# La ciné cache tout l'écran jusqu'à sa dernière image : le messager arrive dans la
		# même image, sans retour visible au lieu de départ.
		messager.teleporter(cible.global_position)
		# Raccord : si le plan a laissé Tobie ailleurs (repère PlaceTobie), il reprend là.
		var cine := Cinematiques.trouver(cinematique)
		if cine != null:
			cine.replacer_messager()
		franchi.emit(self, vers)
		return
	if fondu_noir <= 0.0:
		messager.teleporter(cible.global_position)
		franchi.emit(self, vers)
		return
	_en_fondu = true
	messager.bloque = true
	var couche := CanvasLayer.new()
	couche.layer = COUCHE_FONDU
	var noir := ColorRect.new()
	noir.name = "Noir"
	noir.color = Color(0, 0, 0, 0)
	noir.mouse_filter = Control.MOUSE_FILTER_IGNORE
	noir.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	couche.add_child(noir)
	# Enfant du Passage : si l'étape est déchargée pendant le fondu (saut de débogage,
	# retour au titre), le voile part avec elle au lieu de rester noir sur la racine.
	add_child(couche)
	var aller := create_tween()
	aller.tween_property(noir, "color:a", 1.0, fondu_noir)
	await aller.finished
	messager.teleporter(cible.global_position)
	franchi.emit(self, vers)
	var retour := couche.create_tween()
	retour.tween_property(noir, "color:a", 0.0, fondu_noir)
	await retour.finished
	couche.queue_free()
	if is_instance_valid(messager):
		messager.bloque = false
	_en_fondu = false


func _racine_etape() -> Node:
	var noeud: Node = get_parent()
	while noeud != null:
		if noeud is EtapeBase:
			return noeud
		noeud = noeud.get_parent()
	return get_tree().current_scene if is_inside_tree() else null
