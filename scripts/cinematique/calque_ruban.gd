class_name CalqueRuban
extends Sprite2D
## Le ruban rouge de Tobie dans une cinématique : posé en enfant d'un Sprite2D qui joue une
## planche chr_tobie_<geste>_01, il affiche le calque chr_tobie_<geste>_01_red avec la même
## image, le même cadrage et le même retournement, et bat comme en jeu (SilhouetteTobie).
## Suit aussi les changements de planche (repos puis marche…) faits par l'animation.
## Usage : CalqueRuban.poser(sprite_de_tobie).

var _source: Texture2D
var _cache := {}


static func poser(tobie: Sprite2D) -> CalqueRuban:
	var r := CalqueRuban.new()
	r.name = "Ruban"
	tobie.add_child(r)
	r._suivre()
	return r


func _process(_delta: float) -> void:
	_suivre()
	modulate.a = Battement.opacite(Battement.maintenant(), GameState.palier, Reglages.valeur(&"effets_attenues"))


func _suivre() -> void:
	var tobie := get_parent() as Sprite2D
	if tobie == null:
		return
	if tobie.texture != _source:
		_source = tobie.texture
		texture = _calque(_source)
	centered = tobie.centered
	offset = tobie.offset
	if hframes != tobie.hframes or vframes != tobie.vframes:
		frame = 0
		hframes = tobie.hframes
		vframes = tobie.vframes
	frame = clampi(tobie.frame, 0, hframes * vframes - 1)
	flip_h = tobie.flip_h
	texture_filter = tobie.texture_filter


func _calque(base: Texture2D) -> Texture2D:
	if base == null or not base.resource_path.ends_with(".png"):
		return null
	var chemin := base.resource_path.trim_suffix(".png") + "_red.png"
	if not _cache.has(chemin):
		_cache[chemin] = load(chemin) as Texture2D if ResourceLoader.exists(chemin) else null
	return _cache[chemin]
