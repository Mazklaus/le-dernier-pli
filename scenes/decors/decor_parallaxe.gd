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
