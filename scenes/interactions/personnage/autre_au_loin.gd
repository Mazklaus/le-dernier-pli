class_name AutreAuLoin
extends Node2D
## L'Autre en jeu (étape 5, demande du GD du 17/11) : quand Tobie dit « Quelqu'un marche »
## (début de la rencontre `declencheur`), la silhouette apparaît au bout du sentier, marche sur
## place (planche chr_autre_marche_01 de la DA, comme la ciné : lanterne, même silhouette).
## Elle reste toujours hors d'atteinte : « il ne s'approche pas, il ne s'éloigne pas non plus ».
## Elle garde l'écart qu'elle avait avec Tobie à son apparition, sans dépasser `recul_max` au-delà
## de sa place ; acculée, si Tobie s'approche à moins de `distance_fuite`, elle se dissout dans
## la brume et ne revient plus.

enum Etat { CACHE, PRESENT, DISSIPE }

const NOM := &"autre"
const DUREE_APPARITION := 1.0
const DUREE_DISSIPATION := 1.5

## La rencontre qui la fait apparaître (e5_autre).
@export var declencheur: NodePath
## Échelle de la silhouette : plus petite que Tobie, elle est loin.
@export var echelle: float = 0.6
## Opacité dans la brume.
@export var opacite: float = 0.85
## Recul possible au-delà de sa place (px), avant d'être acculée au bout du sentier.
@export var recul_max: float = 120.0
## Acculée, elle se dissout si Tobie arrive plus près que ça (px).
@export var distance_fuite: float = 300.0

var etat: Etat = Etat.CACHE
var dessin: Personnage = null
var ecart: float = 0.0
var x_depart: float = 0.0


func _ready() -> void:
	x_depart = position.x
	dessin = Personnage.creer(NOM)
	if dessin != null:
		dessin.scale = Vector2.ONE * echelle
		add_child(dessin)
	visible = false
	set_process(false)
	var d := get_node_or_null(declencheur) as DeclencheurDialogue
	if d != null:
		d.dialogue_commence.connect(func(_d: DeclencheurDialogue) -> void: apparaitre())


## La position où elle se tient : à `ecart` devant Tobie, sans dépasser le bout du sentier.
static func position_suivie(x_tobie: float, ecart_garde: float, x_max: float) -> float:
	return minf(x_tobie + ecart_garde, x_max)


## Acculée (au bout de son recul) et Tobie trop près : elle se dissout.
static func doit_se_dissiper(x_autre: float, x_tobie: float, x_max: float, fuite: float) -> bool:
	return x_autre >= x_max and absf(x_autre - x_tobie) < fuite


func apparaitre() -> bool:
	if etat != Etat.CACHE or dessin == null:
		return false
	etat = Etat.PRESENT
	var tobie := _x_tobie()
	ecart = position.x - tobie if not is_nan(tobie) else 0.0
	visible = true
	if Reglages.valeur(&"effets_attenues") or not is_inside_tree():
		modulate.a = opacite
	else:
		modulate.a = 0.0
		create_tween().tween_property(self, "modulate:a", opacite, DUREE_APPARITION)
	set_process(true)
	return true


func _process(_delta: float) -> void:
	var tobie := _x_tobie()
	if etat != Etat.PRESENT or is_nan(tobie):
		return
	var x_max := x_depart + recul_max
	position.x = position_suivie(tobie, ecart, x_max)
	if doit_se_dissiper(position.x, tobie, x_max, distance_fuite):
		dissiper()


func dissiper() -> void:
	if etat != Etat.PRESENT:
		return
	etat = Etat.DISSIPE
	set_process(false)
	if Reglages.valeur(&"effets_attenues") or not is_inside_tree():
		visible = false
		return
	var t := create_tween()
	t.tween_property(self, "modulate:a", 0.0, DUREE_DISSIPATION)
	t.tween_callback(hide)


## Abscisse de Tobie dans le repère du parent, ou NAN sans messager.
func _x_tobie() -> float:
	if not is_inside_tree():
		return NAN
	var m := get_tree().get_first_node_in_group(Messager.GROUPE) as Node2D
	if m == null:
		return NAN
	return get_parent().to_local(m.global_position).x if get_parent() is Node2D else m.global_position.x
