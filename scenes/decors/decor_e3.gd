class_name DecorE3
extends DecorParallaxe
## Décor de surface de l'étape 3, le Village aux cloches muettes (planche du DA) : cinq plans
## parallaxes pour la lisière et la rue (7680 px), sol à y 900. Un village trop intact :
## les deux fausses notes (lampions pendus à l'envers, baie du clocher vide) sont peintes dans
## le plan 3. La nuit vient de la teinte d'EtapeBase : aucun modulate ici.
## Masque les fonds, sols et murs gris de la maquette (Surface/*/Fond, Sol, Mur*).
## Les lieux (Lieux/<Nom>) reçoivent chacun un fond fixe (env_e3_plan3_<lieu>_NN), posé dans
## leur repère local, derrière le jeu ; leurs gris (Fond, Sol, Plafond, Mur*) sont masqués.

const DOSSIER := "res://assets/graphics/env/e3/env_e3_"
## [nom du plan, vitesse, couche] du plus lointain au plus proche.
const PLANS := [
	["plan0_ciel", 0.05, -50],
	["plan1_lointain", 0.2, -40],
	["plan2_milieu", 0.5, -30],
	["plan3_surface", 1.0, -20],
	["plan4_premier-plan", 1.4, 20],
]

## [nœud du lieu sous Lieux, nom du fond, abscisse du fond dans le lieu]. La chambre (1440)
## est peinte sur 1920 avec ses murs en coupe dans les marges : la caméra la centre.
const LIEUX := [
	["MaisonIlde", "maison-ilde", 0.0],
	["Clocher", "clocher", 0.0],
	["Chambre", "chambre", -240.0],
	["CheminNuit", "chemin-nuit", 0.0],
	["CheminAube", "chemin-aube", 0.0],
]
const Z_LIEU := -20

@export var masquer_fonds_maquette: bool = true

var plans: Array[Parallax2D] = []


func _ready() -> void:
	for p: Array in PLANS:
		var plan := creer_plan(DOSSIER + String(p[0]), float(p[1]), int(p[2]))
		if plan != null:
			add_child(plan)
			plans.append(plan)
	if masquer_fonds_maquette and not plans.is_empty():
		masquer_fonds_gris()
	_habiller_lieux()


## Fond fixe de chaque lieu : tuiles bout à bout dans le repère du lieu, derrière le jeu.
func _habiller_lieux() -> void:
	var lieux := get_parent().get_node_or_null("Lieux") if get_parent() else null
	if lieux == null:
		return
	for l: Array in LIEUX:
		var lieu := lieux.get_node_or_null(String(l[0])) as Node2D
		if lieu == null:
			continue
		var fond := Node2D.new()
		fond.name = "Dessin"
		fond.z_index = Z_LIEU
		fond.position = Vector2(float(l[2]), 0.0)
		var x := 0.0
		for n in range(1, 10):
			var chemin := "%splan3_%s_%02d.png" % [DOSSIER, String(l[1]), n]
			if not ResourceLoader.exists(chemin):
				break
			var tuile := Sprite2D.new()
			tuile.texture = load(chemin) as Texture2D
			tuile.centered = false
			tuile.position = Vector2(x, 0.0)
			tuile.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
			fond.add_child(tuile)
			x += tuile.texture.get_width()
		if fond.get_child_count() == 0:
			fond.free()
			continue
		lieu.add_child(fond)
		lieu.move_child(fond, 0)
		if masquer_fonds_maquette:
			_masquer_gris_lieu(lieu)


func _masquer_gris_lieu(lieu: Node) -> void:
	masquer_maquette(lieu)
	var fond_gris := lieu.get_node_or_null("Fond") as CanvasItem
	if fond_gris != null:
		fond_gris.visible = false
	# Voile noir de maquette de la ZoneSombre (chemin de nuit) : il passait devant Tobie et
	# assombrissait le ruban avant la détection du rouge. Le noir est peint dans le fond.
	var voile_zone := lieu.get_node_or_null("ZoneSombre/Visuel") as CanvasItem
	if voile_zone != null:
		voile_zone.visible = false
	for corps: Node in lieu.get_children():
		var nom := String(corps.name)
		if corps is StaticBody2D and (nom == "Sol" or nom == "Plafond" or nom.begins_with("Mur")):
			var visuel := corps.get_node_or_null("Visuel") as CanvasItem
			if visuel != null:
				visuel.visible = false
