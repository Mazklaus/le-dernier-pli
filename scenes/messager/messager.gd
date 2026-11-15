class_name Messager
extends CharacterBody2D
## Le messager : marche latérale (pas de course à l'étape 1) et interactions.
## Il détecte les Interactif (dialogues, passages) dans son rayon d'interaction (96 px), garde le plus
## proche comme cible et le déclenche sur l'action « interagir ». Immobile pendant un dialogue.

signal cible_changee(cible: Interactif)  # null quand plus rien n'est à portée
## Émis après un déplacement instantané (passage entre la surface et un lieu).
signal teleporte(position_globale: Vector2)

const GROUPE: StringName = &"messager"
const VITESSE_MARCHE := 160.0
const RAYON_INTERACTION := 96.0
## Distance à laquelle le saut de débogage pose le messager devant un déclencheur.
const ECART_PLACEMENT := 64.0
## Pente la plus raide encore marchable (au-delà, c'est un mur).
const PENTE_MAX_DEGRES := 40.0
## Distance d'accroche au sol : garde le messager collé en descente de pente ou de marche.
const ACCROCHE_SOL := 24.0

@export var vitesse: float = VITESSE_MARCHE
@export var gravite: float = 2400.0

var bloque: bool = false
## 1 vers la droite, -1 vers la gauche.
var regard: int = 1
var cible: Interactif = null

var _a_portee: Array[Interactif] = []
var _en_dialogue: bool = false

@onready var _detecteur: Area2D = %Detecteur
@onready var _silhouette: SilhouetteTobie = %Silhouette
@onready var _camera: Camera2D = %Camera


func _ready() -> void:
	add_to_group(GROUPE)
	# Sols en pente (étape 2, 30° au plus) : vitesse constante, collé au sol en descente,
	# immobile à l'arrêt.
	floor_max_angle = deg_to_rad(PENTE_MAX_DEGRES)
	floor_constant_speed = true
	floor_snap_length = ACCROCHE_SOL
	floor_stop_on_slope = true
	_detecteur.area_entered.connect(_sur_zone_entree)
	_detecteur.area_exited.connect(_sur_zone_sortie)
	DialogueManager.dialogue_started.connect(_sur_dialogue_commence)
	DialogueManager.dialogue_ended.connect(_sur_dialogue_fini)


func _physics_process(delta: float) -> void:
	var direction: float = 0.0 if bloque else Input.get_axis(&"deplacer_gauche", &"deplacer_droite")
	velocity.x = direction * vitesse
	if is_on_floor():
		velocity.y = 0.0
	else:
		velocity.y += gravite * delta
	move_and_slide()
	if direction != 0.0:
		regard = 1 if direction > 0.0 else -1
		_silhouette.scale.x = regard
	_silhouette.jouer(animation_voulue(direction))
	_mettre_a_jour_cible()


## Interagir pendant un dialogue (main au pli), marche quand il avance vraiment, repos sinon
## (bloqué par un mur, en fondu de passage, à l'arrêt).
func animation_voulue(direction: float) -> StringName:
	if _en_dialogue:
		return SilhouetteTobie.INTERAGIR
	if direction != 0.0 and absf(get_real_velocity().x) > 1.0:
		return SilhouetteTobie.MARCHE
	return SilhouetteTobie.REPOS


func _unhandled_input(event: InputEvent) -> void:
	if bloque or cible == null:
		return
	if event.is_action_pressed(&"interagir"):
		get_viewport().set_input_as_handled()
		cible.interagir(self)


## Pose le messager devant un déclencheur, tourné vers lui (saut de débogage).
func placer_devant(declencheur: Node2D) -> void:
	teleporter(Vector2(declencheur.global_position.x - ECART_PLACEMENT, declencheur.global_position.y))
	regard = 1
	_silhouette.scale.x = regard


## Bornes horizontales de la caméra (surface d'une étape, pour le décor parallaxe).
func borner_camera(gauche: int, droite: int) -> void:
	_camera.limit_left = gauche
	_camera.limit_right = droite
	_camera.reset_smoothing()


func liberer_camera() -> void:
	_camera.limit_left = -10000000
	_camera.limit_right = 10000000
	_camera.reset_smoothing()


## Déplacement instantané (passages, saut de débogage) : la caméra suit sans glisser.
func teleporter(position_globale: Vector2) -> void:
	global_position = position_globale
	velocity = Vector2.ZERO
	_camera.reset_smoothing()
	teleporte.emit(position_globale)


## Le déclencheur disponible le plus proche parmi ceux à portée, ou null.
func choisir_cible() -> Interactif:
	var meilleur: Interactif = null
	var meilleure_distance := INF
	for d in _a_portee:
		if not is_instance_valid(d) or not d.est_disponible():
			continue
		var distance := global_position.distance_squared_to(d.global_position)
		if distance < meilleure_distance:
			meilleure_distance = distance
			meilleur = d
	return meilleur


func _mettre_a_jour_cible() -> void:
	var nouvelle: Interactif = null if bloque else choisir_cible()
	if nouvelle != cible:
		cible = nouvelle
		cible_changee.emit(cible)


func _sur_zone_entree(zone: Area2D) -> void:
	if zone is Interactif and zone not in _a_portee:
		_a_portee.append(zone as Interactif)


func _sur_zone_sortie(zone: Area2D) -> void:
	if zone is Interactif:
		_a_portee.erase(zone)


func _sur_dialogue_commence(_ressource: Resource) -> void:
	bloque = true
	_en_dialogue = true
	_mettre_a_jour_cible()


func _sur_dialogue_fini(_ressource: Resource) -> void:
	# On attend une frame : la touche qui ferme la dernière réplique ne doit pas
	# relancer aussitôt le même dialogue.
	_en_dialogue = false
	await get_tree().process_frame
	bloque = false
