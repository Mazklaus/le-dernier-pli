class_name LuciditeEcran
extends Node
## Relie le palier de Lucidité à l'écran gravure (valeurs de la DA) : le trait tremble plus et
## le rouge pâlit quand la Lucidité baisse, avec un fondu de 0,6 s au changement de palier.
## - Clair : amplitude_px 1,5, rouge_efface 0
## - Trouble : amplitude_px 3,0, rouge_efface 0
## - Égaré : amplitude_px 5,0, rouge_efface 0,3 (le rouge pâlit sans devenir rose sale)
## Effets atténués : amplitude 0, rouge_efface s'applique (c'est une couleur, pas un
## mouvement). L'amplitude ne suit pas le Battement : seul le ruban bat (DA).

const DUREE_FONDU := 0.6
## palier -> [amplitude_px, rouge_efface]
const VALEURS := {
	&"clair": Vector2(1.5, 0.0),
	&"trouble": Vector2(3.0, 0.0),
	&"egare": Vector2(5.0, 0.3),
}

var materiau: ShaderMaterial
## Valeurs courantes (amplitude hors atténuation, rouge_efface).
var courant: Vector2 = VALEURS[&"clair"]

var _depart: Vector2 = VALEURS[&"clair"]
var _cible: Vector2 = VALEURS[&"clair"]
var _progres: float = 1.0


static func valeurs_pour(palier: StringName) -> Vector2:
	return VALEURS.get(palier, VALEURS[&"clair"])


func _ready() -> void:
	courant = valeurs_pour(GameState.palier)
	_depart = courant
	_cible = courant
	GameState.palier_change.connect(_sur_palier_change)
	GameState.etat_charge.connect(_sauter_au_palier)
	appliquer()


func _process(delta: float) -> void:
	if _progres < 1.0:
		_progres = minf(1.0, _progres + delta / DUREE_FONDU)
		courant = _depart.lerp(_cible, _progres)
	# À chaque image : l'écran gravure remet l'amplitude de repos quand le réglage change.
	appliquer()


func appliquer() -> void:
	if materiau == null:
		return
	var attenue: bool = Reglages.valeur(&"effets_attenues")
	materiau.set_shader_parameter(&"amplitude_px", 0.0 if attenue else courant.x)
	materiau.set_shader_parameter(&"rouge_efface", courant.y)


func _sur_palier_change(_ancien: StringName, nouveau: StringName) -> void:
	_depart = courant
	_cible = valeurs_pour(nouveau)
	_progres = 0.0


## Après un chargement : pas de fondu, on se place directement au palier.
func _sauter_au_palier() -> void:
	courant = valeurs_pour(GameState.palier)
	_cible = courant
	_progres = 1.0
	appliquer()
