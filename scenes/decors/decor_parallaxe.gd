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
		tuile.texture = load(chemin) as Texture2D
		tuile.centered = false
		tuile.position = Vector2(x, 0.0)
		plan.add_child(tuile)
		x += tuile.texture.get_width()
	if plan.get_child_count() == 0:
		plan.free()
		return null
	plan.set_meta(&"largeur", x)
	return plan


## Largeur totale d'un plan construit par creer_plan.
static func largeur(plan: Parallax2D) -> float:
	return float(plan.get_meta(&"largeur", 0.0))


## Masque les gris de la maquette quand le décor est posé : fonds des sections (Surface/*/Fond),
## sol et murs (leur « Visuel »). Le plan 3 les dessine.
func masquer_fonds_gris() -> void:
	var surface := get_parent().get_node_or_null("Surface") if get_parent() else null
	if surface == null:
		return
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
