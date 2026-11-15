class_name DecorParallaxe
extends Node2D
## Décor d'étape en plans parallaxes (planche du DA) : chaque plan est une suite de tuiles
## <prefixe>planN_<nom>_01, _02… (2048 px de large au plus, 1080 de haut) posées bout à bout
## dans un Parallax2D dont la vitesse est celle du plan (0 = fixe à l'écran, 1 = le monde).
## Les plans < 1 passent derrière le jeu, les plans > 1 devant le messager.
## Filtrage linéaire, sans mipmaps (réglages d'import du DA).

## Couche de rendu des plans : derrière la maquette et le messager, ou devant.
const Z_FOND := -100
const Z_DEVANT := 50


## Construit un plan à partir de ses tuiles ; renvoie null si aucune tuile n'existe.
static func creer_plan(chemin_base: String, vitesse: float, z: int) -> Parallax2D:
	var plan := Parallax2D.new()
	plan.name = chemin_base.get_file()
	plan.scroll_scale = Vector2(vitesse, 1.0)
	plan.z_index = z
	plan.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	var x := 0.0
	for n in range(1, 100):
		var chemin := "%s_%02d.png" % [chemin_base, n]
		if not ResourceLoader.exists(chemin):
			break
		var tuile := Sprite2D.new()
		tuile.texture = charger_tuile(chemin)
		tuile.centered = false
		tuile.position = Vector2(x, 0.0)
		plan.add_child(tuile)
		x += tuile.texture.get_width()
	if plan.get_child_count() == 0:
		plan.free()
		return null
	plan.set_meta(&"largeur", x)
	return plan


## Charge une tuile : son AtlasTexture rogné (<nom>.tres, écrit par tools/rogner_tuiles.py)
## s'il existe, sinon le PNG. Le .tres a la taille et la position d'origine (marge), seul
## le dessin utile est en mémoire vidéo.
static func charger_tuile(chemin_png: String) -> Texture2D:
	var rognee := chemin_png.get_basename() + ".tres"
	if ResourceLoader.exists(rognee):
		return load(rognee) as Texture2D
	return load(chemin_png) as Texture2D


## Largeur totale d'un plan construit par creer_plan.
static func largeur(plan: Parallax2D) -> float:
	return float(plan.get_meta(&"largeur", 0.0))


## Masque les gris de la maquette quand le décor est posé : fonds des sections (Surface/*/Fond),
## sol et murs (leur « Visuel »). Le plan 3 les dessine.
func masquer_fonds_gris() -> void:
	var surface := get_parent().get_node_or_null("Surface") if get_parent() else null
	if surface == null:
		return
	masquer_maquette(surface)
	for section in surface.get_children():
		var fond := section.get_node_or_null("Fond") as CanvasItem
		if fond != null:
			fond.visible = false
		# Sol et murs : enfants directs de Surface (étape 2) ou des sections (étape 1).
		for corps: Node in [section] + section.get_children():
			var nom := String(corps.name)
			if corps is StaticBody2D and (nom == "Sol" or nom.begins_with("Mur")):
				var visuel := corps.get_node_or_null("Visuel") as CanvasItem
				if visuel != null:
					visuel.visible = false


## Fond fixe d'un lieu (pièce, chemin fermé) : tuiles <chemin_base>_NN.png bout à bout depuis
## (0, 0), sans parallaxe. null si aucune tuile n'existe.
static func dessin_lieu(chemin_base: String, nom_noeud: String, z: int) -> Node2D:
	var dessin := Node2D.new()
	dessin.name = nom_noeud
	dessin.z_index = z
	var x := 0.0
	for n in range(1, 10):
		var chemin := "%s_%02d.png" % [chemin_base, n]
		if not ResourceLoader.exists(chemin):
			break
		var tuile := Sprite2D.new()
		tuile.texture = load(chemin) as Texture2D
		tuile.centered = false
		tuile.position = Vector2(x, 0.0)
		tuile.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		dessin.add_child(tuile)
		x += tuile.texture.get_width()
	if dessin.get_child_count() == 0:
		dessin.free()
		return null
	return dessin


## Gris de maquette d'un lieu habillé : Fond, Visuel de Sol/Plafond/Mur*, et le voile noir de la
## ZoneSombre (il passait devant Tobie et assombrissait le ruban ; le noir est peint dans le fond).
static func masquer_gris_lieu(lieu: Node) -> void:
	masquer_maquette(lieu)
	for chemin: String in ["Fond", "ZoneSombre/Visuel"]:
		var gris := lieu.get_node_or_null(chemin) as CanvasItem
		if gris != null:
			gris.visible = false
	for corps: Node in lieu.get_children():
		var nom := String(corps.name)
		if corps is StaticBody2D and (nom == "Sol" or nom == "Plafond" or nom.begins_with("Mur")):
			var visuel := corps.get_node_or_null("Visuel") as CanvasItem
			if visuel != null:
				visuel.visible = false


## Rectangles et étiquettes de la maquette dans un lieu habillé (QA, #96) : le « Visuel » des
## Interactif (passages, détails, rencontres) et des Verrou (ceintures, chicane), et toutes
## les étiquettes posées dans le monde (noms des rencontres, titres et notes du Level
## Designer). Le dessin d'un personnage, le repère d'un détail et le dessin posé sur un
## verrou restent visibles : seul le nœud nommé « Visuel » est masqué.
static func masquer_maquette(racine: Node) -> void:
	for n in racine.find_children("*", "", true, false):
		if n is Label and (n as Label).get_canvas_layer_node() == null:
			(n as Label).visible = false
		elif n is Interactif or n is Verrou:
			var visuel := n.get_node_or_null("Visuel") as CanvasItem
			if visuel != null:
				visuel.visible = false
