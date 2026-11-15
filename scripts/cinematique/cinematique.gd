class_name Cinematique
extends Node2D
## Cinématique courte jouée dans le moteur (directive animation du Game Director).
##
## Le Level Designer place ce nœud dans une étape, avec ses enfants :
## - `Camera` (Camera2D) : la caméra du plan, rendue courante le temps de la cinématique ;
## - soit des Marker2D `Depart` (et `Arrivee`, facultatif) : cadrage sans animer. La caméra
##   va de Depart à Arrivee en `duree` secondes, en ligne droite ; le zoom est l'échelle du
##   marqueur (scale 2 = deux fois plus près) ;
## - soit un AnimationPlayer `Animation` avec une animation `jouer` (5 à 15 s), pour tout le
##   reste (sprites, visibilités, sons). L'état final doit venir de pistes de propriétés : un
##   saut place l'animation à sa fin sans jouer les clés intermédiaires. Un son se pose par
##   une piste de méthode vers `/root/AudioDirector`, `jouer_variante("sfx_…")`.
##
## Lancement, au choix :
## - depuis un .dialogue : `do Cinematiques.jouer(&"e1_remise_pli")` (le dialogue attend) ;
## - à l'entrée du messager dans un enfant `Zone` (Area2D) ;
## - au début de l'étape : `au_debut_etape` coché.
## Pendant la lecture, le messager est bloqué et l'interface masquée ; `annuler` saute.
## L'animation avance par pas de 1/10 s (10 images par seconde, pas d'interpolation molle).
## En effets atténués, les pistes de la caméra passent en interpolation « au plus proche » :
## la caméra coupe d'un cadrage au suivant au lieu de glisser.

signal finie(sautee: bool)

const GROUPE := &"cinematiques"
const ANIMATION_PAR_DEFAUT := &"jouer"
const PAS := 0.1  # 10 images par seconde

## Identifiant, préfixé par l'étape : e1_remise_pli, e3_procession…
@export var id: StringName
@export var animation: StringName = ANIMATION_PAR_DEFAUT
## Ne se joue qu'une fois par partie (drapeau de rencontre cine_<id>).
@export var une_seule_fois: bool = true
## Se lance dès que l'étape est prête (arrivée par un Passage d'étape : la chute, la spirale).
@export var au_debut_etape: bool = false
## Durée du cadrage Depart → Arrivee, quand il n'y a pas d'AnimationPlayer.
@export_range(1.0, 15.0, 0.1) var duree: float = 6.0

var en_cours: bool = false
var _lecteur: AnimationPlayer
var _camera: Camera2D
var _camera_precedente: Camera2D
var _messager_bloque_avant: bool = false
var _messager: Messager
var _cumul: float = 0.0
var _reste: float = 0.0


func _ready() -> void:
	add_to_group(GROUPE)
	_lecteur = get_node_or_null("Animation") as AnimationPlayer
	_camera = get_node_or_null("Camera") as Camera2D
	if _camera != null:
		# Une Camera2D active prend la vue en entrant dans l'arbre (#164) : celle du plan ne
		# s'allume que pendant la lecture, et la vue revient au messager.
		_camera.enabled = false
		_rendre_vue_au_messager.call_deferred()
	if _lecteur == null and get_node_or_null("Depart") is Marker2D:
		_lecteur = _lecteur_depuis_marqueurs()
	if au_debut_etape:
		SceneRouter.etape_prete.connect(_sur_etape_prete, CONNECT_ONE_SHOT)
	if _lecteur != null:
		_lecteur.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	var zone := get_node_or_null("Zone") as Area2D
	if zone != null:
		zone.body_entered.connect(_sur_entree_zone)
	set_process(false)


## Seulement pour l'étape réellement chargée (scène courante) : une étape instanciée par un
## test ne lance pas sa cinématique d'arrivée (le messager resterait bloqué).
func _sur_etape_prete(etape: Node) -> void:
	if etape.is_ancestor_of(self) and etape == get_tree().current_scene:
		Cinematiques.jouer.call_deferred(id)


## Retirée en pleine lecture (changement de scène, test) : on rend la main et on prévient
## ceux qui attendent la fin, pour qu'aucun dialogue ne reste suspendu.
func _exit_tree() -> void:
	if en_cours:
		_terminer(true)


## Cadrage sans animation : la caméra va de Depart à Arrivee (position et zoom) en `duree`.
func _lecteur_depuis_marqueurs() -> AnimationPlayer:
	var depart := get_node("Depart") as Marker2D
	var arrivee := get_node_or_null("Arrivee") as Marker2D
	if arrivee == null:
		arrivee = depart
	var anim := Animation.new()
	anim.length = duree
	for propriete in [["position", depart.position, arrivee.position], ["zoom", depart.scale, arrivee.scale]]:
		var piste := anim.add_track(Animation.TYPE_VALUE)
		anim.track_set_path(piste, NodePath("Camera:%s" % propriete[0]))
		anim.track_insert_key(piste, 0.0, propriete[1])
		anim.track_insert_key(piste, duree, propriete[2])
	var biblio := AnimationLibrary.new()
	biblio.add_animation(animation, anim)
	var lecteur := AnimationPlayer.new()
	lecteur.name = "Animation"
	lecteur.add_animation_library(&"", biblio)
	add_child(lecteur)
	return lecteur


func _sur_entree_zone(corps: Node2D) -> void:
	if corps is Messager and not en_cours:
		Cinematiques.jouer(id)


static func drapeau(id_cine: StringName) -> StringName:
	return StringName("cine_%s" % id_cine)


func deja_vue() -> bool:
	return GameState.rencontre_vue(drapeau(id))


## Joue la cinématique et attend sa fin. Renvoie true si elle a été sautée.
## Ne fait rien (renvoie false aussitôt) si elle est déjà en cours ou déjà vue.
func jouer() -> bool:
	if en_cours or _lecteur == null or not _lecteur.has_animation(animation):
		return false
	if une_seule_fois and deja_vue():
		return false
	en_cours = true
	_prendre_controle()
	_lecteur.play(_preparer_animation())
	_lecteur.advance(0.0)
	_reste = _lecteur.current_animation_length
	_cumul = 0.0
	set_process(true)
	var sautee: bool = await finie
	return sautee


## Va directement à la fin (touche annuler).
func sauter() -> void:
	if not en_cours:
		return
	# seek (et non advance) : les clés de méthode sautées (sons) ne sont pas jouées.
	_lecteur.seek(_lecteur.current_animation_length, true)
	_terminer(true)


func _process(delta: float) -> void:
	_cumul += delta
	while _cumul >= PAS and en_cours:
		_cumul -= PAS
		var pas := minf(PAS, _reste)
		_lecteur.advance(pas)
		_reste -= pas
		if _reste <= 0.0:
			_terminer(false)


func _input(event: InputEvent) -> void:
	if not en_cours:
		return
	# Rien d'autre ne reçoit d'entrée pendant la cinématique (ni la bulle, ni le messager).
	if event is InputEventKey or event is InputEventMouseButton or event is InputEventJoypadButton:
		get_viewport().set_input_as_handled()
		if event.is_action_pressed(&"annuler"):
			sauter()


## L'animation jouée : une copie dont les pistes de caméra coupent en effets atténués.
func _preparer_animation() -> StringName:
	if not Reglages.valeur(&"effets_attenues"):
		return animation
	var copie := _lecteur.get_animation(animation).duplicate(true) as Animation
	for i in copie.get_track_count():
		if String(copie.track_get_path(i)).begins_with("Camera"):
			copie.track_set_interpolation_type(i, Animation.INTERPOLATION_NEAREST)
	var biblio := _lecteur.get_animation_library(&"")
	var nom := StringName("%s_coupe" % animation)
	if biblio.has_animation(nom):
		biblio.remove_animation(nom)
	biblio.add_animation(nom, copie)
	return nom


func _prendre_controle() -> void:
	_messager = _trouver_messager()
	if _messager != null:
		_messager_bloque_avant = _messager.bloque
		_messager.bloque = true
		_messager.velocity = Vector2.ZERO
	_camera_precedente = get_viewport().get_camera_2d()
	if _camera != null:
		_camera.enabled = true
		_camera.make_current()
	Cinematiques.masquer_interface(true)


func _rendre_controle() -> void:
	if _camera != null:
		if is_instance_valid(_camera_precedente) and _camera_precedente != _camera and _camera_precedente.enabled:
			_camera_precedente.make_current()
		_camera.enabled = false
		_rendre_vue_au_messager()
	if _messager != null and is_instance_valid(_messager):
		_messager.bloque = _messager_bloque_avant
	Cinematiques.masquer_interface(false)


## Hors lecture, si aucune caméra active ne tient la vue, elle revient à celle du messager.
func _rendre_vue_au_messager() -> void:
	if en_cours or not is_inside_tree():
		return
	var courante := get_viewport().get_camera_2d()
	if courante != null and courante.enabled and courante != _camera:
		return
	var messager := _trouver_messager()
	if messager != null:
		messager.activer_camera()


func _terminer(sautee: bool) -> void:
	if not en_cours:
		return
	en_cours = false
	set_process(false)
	if is_instance_valid(_lecteur) and _lecteur.is_inside_tree():
		_lecteur.stop(true)  # garde l'état final
	_rendre_controle()
	if une_seule_fois:
		GameState.marquer_rencontre_vue(drapeau(id))
	finie.emit(sautee)


func _trouver_messager() -> Messager:
	for n in get_tree().get_nodes_in_group(Messager.GROUPE):
		if n is Messager:
			return n as Messager
	return null
