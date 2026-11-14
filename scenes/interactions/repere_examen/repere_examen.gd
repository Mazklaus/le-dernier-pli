class_name RepereExamen
extends Node2D
## Repère gravé au-dessus d'un détail pas encore examiné (spec UI/UX v2) : astérisque à la
## plume, immobile, en lavis, visible de plus loin que l'invite (deux fois le rayon
## d'interaction) pour qu'on ne rate pas le détail en marchant. Disparaît une fois examiné.

const TAILLE := 16.0
const PORTEE := Messager.RAYON_INTERACTION * 2.0
## Hauteur au-dessus de l'origine du détail.
const HAUTEUR := 190.0
const COULEUR := StylePapier.LAVIS
const DUREE_FONDU := 0.25

var rencontre_id: StringName

var _cible_alpha: float = 0.0


func _ready() -> void:
	position = Vector2(0.0, -HAUTEUR)
	z_index = 5
	modulate.a = 0.0


func _process(delta: float) -> void:
	_cible_alpha = 1.0 if doit_paraitre() else 0.0
	modulate.a = move_toward(modulate.a, _cible_alpha, delta / DUREE_FONDU)


func est_examine() -> bool:
	return rencontre_id != &"" and GameState.rencontre_vue(rencontre_id)


func doit_paraitre() -> bool:
	if est_examine():
		return false
	var messager := get_tree().get_first_node_in_group(Messager.GROUPE) as Node2D
	if messager == null:
		return false
	return messager.global_position.distance_to(get_parent().global_position) <= PORTEE


func _draw() -> void:
	# Trois traits de plume croisés, légèrement inégaux.
	var r := TAILLE / 2.0
	for i in 3:
		var angle := PI / 2.0 + i * PI / 3.0 + (0.06 if i == 1 else 0.0)
		var d := Vector2.from_angle(angle) * r
		draw_line(-d, d, COULEUR, 2.0 if i == 0 else 1.6, true)
