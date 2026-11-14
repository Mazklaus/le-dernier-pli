class_name RepereExamen
extends Node2D
## Repère gravé au-dessus d'un détail pas encore examiné (spec UI/UX v2) : astérisque à la
## plume en encre pleine sur une pastille de papier au bord déchiré (lisible sur tout fond),
## immobile, visible de plus loin que l'invite (deux fois le rayon
## d'interaction) pour qu'on ne rate pas le détail en marchant. Disparaît une fois examiné.

const TAILLE := 24.0
## Diamètre de la pastille de papier : 1,5 fois l'astérisque.
const RAPPORT_PASTILLE := 1.5
const PORTEE := Messager.RAYON_INTERACTION * 2.0
## Hauteur au-dessus de l'origine du détail.
const HAUTEUR := 190.0
const COULEUR := StylePapier.ENCRE
const COULEUR_PASTILLE := StylePapier.PAPIER
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


## Contour déchiré de la pastille : cercle aux rayons irréguliers, toujours le même pour un
## détail donné (graine tirée de son identifiant).
func contour_pastille() -> PackedVector2Array:
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(rencontre_id)
	var rayon := TAILLE * RAPPORT_PASTILLE / 2.0
	var points := PackedVector2Array()
	for i in 20:
		var angle := TAU * i / 20.0
		points.append(Vector2.from_angle(angle) * rayon * rng.randf_range(0.88, 1.04))
	return points


func _draw() -> void:
	draw_colored_polygon(contour_pastille(), COULEUR_PASTILLE)
	# Trois traits de plume croisés, légèrement inégaux.
	var r := TAILLE / 2.0
	for i in 3:
		var angle := PI / 2.0 + i * PI / 3.0 + (0.06 if i == 1 else 0.0)
		var d := Vector2.from_angle(angle) * r
		draw_line(-d, d, COULEUR, 3.0 if i == 0 else 2.4, true)
