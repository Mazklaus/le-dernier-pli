class_name InviteInteraction
extends PanelContainer
## Invite d'interaction (maquette UI/UX) : petite plaque de papier au-dessus de la cible du
## messager, « [E] Parler à Jacquot ». Apparaît et disparaît en fondu de 0,15 s sur
## cible_changee, cachée pendant les dialogues. Le glyphe suit la touche de « interagir ».

const DUREE_FONDU := 0.15
const LIBELLE_MAX := 24
## Hauteur au-dessus de l'origine de la cible (ses pieds), en pixels écran à 1080.
const HAUTEUR := 220.0
const ENCRE := StylePapier.ENCRE

## Police du libellé ; Spectral par défaut.
@export var police: Font

var cible: Interactif = null

var _etiquette: Label
var _fondu: Tween
var _en_dialogue: bool = false


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	# Petite plaque de papier déchiré du DA (bord réduit à 18 px pour une plaque d'une ligne).
	add_theme_stylebox_override(&"panel", StylePapier.plaque(22.0, 18.0, 10.0))
	if police == null:
		police = StylePapier.police(StylePapier.POLICE_TEXTE)
	_etiquette = Label.new()
	_etiquette.add_theme_color_override(&"font_color", ENCRE)
	_etiquette.add_theme_font_size_override(&"font_size", 20)
	if police:
		_etiquette.add_theme_font_override(&"font", police)
	add_child(_etiquette)
	modulate.a = 0.0
	hide()
	DialogueManager.dialogue_started.connect(_sur_dialogue_commence)
	DialogueManager.dialogue_ended.connect(_sur_dialogue_fini)


func _process(_delta: float) -> void:
	if visible and is_instance_valid(cible):
		var ecran := cible.get_global_transform_with_canvas().origin
		position = ecran - Vector2(size.x / 2.0, HAUTEUR + size.y)


## Branche l'invite sur un messager.
func suivre(messager: Messager) -> void:
	messager.cible_changee.connect(definir_cible)
	definir_cible(messager.cible)


func definir_cible(nouvelle: Interactif) -> void:
	cible = nouvelle
	if cible != null:
		_etiquette.text = texte_pour(cible.libelle)
	_actualiser()


## « [E] Parler à Jacquot », libellé coupé à 24 caractères.
static func texte_pour(libelle: String) -> String:
	var l := libelle.strip_edges()
	if l.length() > LIBELLE_MAX:
		l = l.left(LIBELLE_MAX - 1) + "…"
	var glyphe := glyphe_action(&"interagir")
	return "[%s] %s" % [glyphe, l] if l != "" else "[%s]" % glyphe


## Nom de la première touche clavier d'une action, dans la disposition du joueur.
static func glyphe_action(action: StringName) -> String:
	if not InputMap.has_action(action):
		return "?"
	for evenement in InputMap.action_get_events(action):
		if evenement is InputEventKey:
			var touche := evenement as InputEventKey
			var code := touche.keycode
			if touche.physical_keycode != KEY_NONE:
				code = touche.physical_keycode
				# Disposition du joueur (Q/D en AZERTY) ; indisponible sans écran (tests, CI).
				if DisplayServer.get_name() != "headless":
					code = DisplayServer.keyboard_get_keycode_from_physical(touche.physical_keycode)
			var nom := OS.get_keycode_string(code)
			if nom.is_empty():
				nom = OS.get_keycode_string(touche.physical_keycode)
			return nom
	return "?"


func _actualiser() -> void:
	var montrer := cible != null and not _en_dialogue
	if _fondu and _fondu.is_valid():
		_fondu.kill()
	if montrer:
		show()
	_fondu = create_tween()
	_fondu.tween_property(self, "modulate:a", 1.0 if montrer else 0.0, DUREE_FONDU)
	if not montrer:
		_fondu.tween_callback(hide)


func _sur_dialogue_commence(_ressource: Resource) -> void:
	_en_dialogue = true
	_actualiser()


func _sur_dialogue_fini(_ressource: Resource) -> void:
	_en_dialogue = false
	_actualiser()
