class_name Messager
extends CharacterBody2D
## Le messager : marche latérale (pas de course à l'étape 1) et interactions.
## Il détecte les DeclencheurDialogue dans son rayon d'interaction (96 px), garde le plus
## proche comme cible et le déclenche sur l'action « interagir ». Immobile pendant un dialogue.

signal cible_changee(cible: DeclencheurDialogue)  # null quand plus rien n'est à portée

const GROUPE: StringName = &"messager"
const VITESSE_MARCHE := 160.0
const RAYON_INTERACTION := 96.0
## Distance à laquelle le saut de débogage pose le messager devant un déclencheur.
const ECART_PLACEMENT := 64.0

@export var vitesse: float = VITESSE_MARCHE
@export var gravite: float = 2400.0

var bloque: bool = false
## 1 vers la droite, -1 vers la gauche.
var regard: int = 1
var cible: DeclencheurDialogue = null

var _a_portee: Array[DeclencheurDialogue] = []

@onready var _detecteur: Area2D = %Detecteur
@onready var _silhouette: Node2D = %Silhouette


func _ready() -> void:
	add_to_group(GROUPE)
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
	_mettre_a_jour_cible()


func _unhandled_input(event: InputEvent) -> void:
	if bloque or cible == null:
		return
	if event.is_action_pressed(&"interagir"):
		get_viewport().set_input_as_handled()
		cible.interagir(self)


## Pose le messager devant un déclencheur, tourné vers lui (saut de débogage).
func placer_devant(declencheur: Node2D) -> void:
	global_position = Vector2(declencheur.global_position.x - ECART_PLACEMENT, global_position.y)
	velocity = Vector2.ZERO
	regard = 1
	_silhouette.scale.x = regard


## Le déclencheur disponible le plus proche parmi ceux à portée, ou null.
func choisir_cible() -> DeclencheurDialogue:
	var meilleur: DeclencheurDialogue = null
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
	var nouvelle: DeclencheurDialogue = null if bloque else choisir_cible()
	if nouvelle != cible:
		cible = nouvelle
		cible_changee.emit(cible)


func _sur_zone_entree(zone: Area2D) -> void:
	if zone is DeclencheurDialogue and zone not in _a_portee:
		_a_portee.append(zone as DeclencheurDialogue)


func _sur_zone_sortie(zone: Area2D) -> void:
	if zone is DeclencheurDialogue:
		_a_portee.erase(zone)


func _sur_dialogue_commence(_ressource: Resource) -> void:
	bloque = true
	_mettre_a_jour_cible()


func _sur_dialogue_fini(_ressource: Resource) -> void:
	# On attend une frame : la touche qui ferme la dernière réplique ne doit pas
	# relancer aussitôt le même dialogue.
	await get_tree().process_frame
	bloque = false
