class_name ProcessionFenetre
extends Node2D
## La procession vue de la chambre (e3_procession, DA) : des silhouettes réduites qui passent
## dans la rue sous la fenêtre, vers la droite, en boucle. Elles sont découpées dans le
## rectangle de la vitre (rien ne déborde sur le mur) et la croisée claire est redessinée
## par-dessus. Sur la vitre noire, seules les flammes et leurs réserves de papier se voient.
## Coordonnées en repère local du lieu (la chambre) : poser ce nœud à l'origine du lieu.

## Rectangle de la vitre, en repère local.
@export var vitre: Rect2 = Rect2(300.0, 520.0, 200.0, 220.0)
## Croisée claire (montant vertical et traverse) redessinée devant les silhouettes.
@export var croisee: Array[Rect2] = [Rect2(398.0, 520.0, 4.0, 220.0), Rect2(300.0, 628.0, 200.0, 4.0)]
@export var couleur_croisee: Color = Color8(232, 229, 218)
## Dessin de la DA (cadre, croisée, appui) posé non centré au coin de la vitre ; à défaut,
## la croisée est redessinée en rectangles clairs.
@export var dessin_croisee: String = "res://assets/graphics/fx/fx_croisee-chambre.png"
@export var personnage: StringName = &"procession"
@export var nombre: int = 5
@export var ecart: float = 70.0
@export var echelle: float = 0.28
## Pieds des silhouettes (y) et abscisse de départ de la boucle.
@export var y_pieds: float = 735.0
@export var x_depart: float = 260.0
@export var vitesse: float = 35.0

const Z := -15

var silhouettes: Array[Personnage] = []
var decoupe: Control
var _parcouru: float = 0.0


func _ready() -> void:
	# Devant le fond peint du lieu, derrière Tobie.
	z_index = Z
	decoupe = Control.new()
	decoupe.name = "Vitre"
	decoupe.clip_contents = true
	decoupe.mouse_filter = Control.MOUSE_FILTER_IGNORE
	decoupe.position = vitre.position
	decoupe.size = vitre.size
	add_child(decoupe)
	for i in nombre:
		var p := Personnage.creer(personnage)
		if p == null:
			break
		p.name = "Silhouette%d" % i
		p.scale = Vector2.ONE * echelle
		p.dephasage = i
		decoupe.add_child(p)
		silhouettes.append(p)
	if ResourceLoader.exists(dessin_croisee):
		var cadre := Sprite2D.new()
		cadre.name = "Croisee"
		cadre.texture = load(dessin_croisee) as Texture2D
		cadre.centered = false
		cadre.position = vitre.position
		cadre.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		add_child(cadre)
		croisee = []
	for i in croisee.size():
		var montant := ColorRect.new()
		montant.name = "Croisee%d" % i
		montant.color = couleur_croisee
		montant.mouse_filter = Control.MOUSE_FILTER_IGNORE
		montant.position = croisee[i].position
		montant.size = croisee[i].size
		add_child(montant)
	_placer()


func _process(delta: float) -> void:
	_parcouru += vitesse * delta
	_placer()


## Période de la boucle : la file entière (nombre × écart), pour que le pas reste régulier.
func periode() -> float:
	return maxf(ecart, ecart * nombre)


## Abscisse locale (repère du lieu) de la silhouette i : la première mène, les autres suivent.
func x_silhouette(i: int) -> float:
	return x_depart + fposmod(_parcouru - ecart * i, periode())


func _placer() -> void:
	for i in silhouettes.size():
		silhouettes[i].position = Vector2(x_silhouette(i), y_pieds) - vitre.position
