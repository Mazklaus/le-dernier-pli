class_name InviteInteraction
extends PanelContainer
## Invite d'interaction (spec UI/UX v2, demande du Game Director) : plaque de papier déchiré
## au-dessus de la cible du messager, touche dans un carré d'encre plein (lettre en papier)
## puis le libellé, « [E] Examiner l'écriteau ». Apparaît en fondu ; à la sortie de zone elle
## reste pleinement visible PERSISTANCE s puis s'efface en DUREE_EFFACEMENT s (revenir
## annule). Cachée pendant les dialogues. Reste dans les marges de l'écran et sous les plaques
## du HUD (zones_interdites, fournies par InterfaceJeu).

const DUREE_FONDU := 0.15
const PERSISTANCE := 0.6
const DUREE_EFFACEMENT := 0.4
const LIBELLE_MAX := 24
## Libellé en Spectral, en pixels à 1080 (≈ 19 px en 720).
const TAILLE_TEXTE := 28
## Carré de la touche : 1,1 fois la hauteur du texte.
const RAPPORT_TOUCHE := 1.1
## Marge intérieure de la plaque.
const MARGE_PLAQUE := 10.0
## Marge minimale aux bords de l'écran et aux plaques du HUD.
const MARGE_ECRAN := 24.0
## Hauteur au-dessus de l'origine de la cible (ses pieds), en pixels écran à 1080.
const HAUTEUR := 220.0
const ENCRE := StylePapier.ENCRE
const PAPIER := StylePapier.PAPIER

## Police du libellé ; Spectral par défaut.
@export var police: Font

var cible: Interactif = null
## Dernière cible affichée : l'invite la suit pendant sa persistance après la sortie de zone.
var cible_affichee: Interactif = null
## Rectangles écran à ne jamais recouvrir (plaques du HUD).
var zones_interdites: Array[Rect2] = []

var _etiquette: Label
var _touche: PanelContainer
var _lettre: Label
var _fondu: Tween
var _en_dialogue: bool = false


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_theme_stylebox_override(&"panel", StylePapier.plaque(MARGE_PLAQUE + 8.0, 18.0, MARGE_PLAQUE))
	if police == null:
		police = StylePapier.police(StylePapier.POLICE_TEXTE)
	var rangee := HBoxContainer.new()
	rangee.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rangee.add_theme_constant_override(&"separation", 10)
	add_child(rangee)
	# Touche : carré d'encre plein, lettre couleur papier.
	_touche = PanelContainer.new()
	_touche.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var carre := StyleBoxFlat.new()
	carre.bg_color = ENCRE
	_touche.add_theme_stylebox_override(&"panel", carre)
	var cote := roundf(TAILLE_TEXTE * RAPPORT_TOUCHE)
	_touche.custom_minimum_size = Vector2(cote, cote)
	_touche.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	rangee.add_child(_touche)
	_lettre = Label.new()
	_lettre.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_lettre.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_lettre.add_theme_color_override(&"font_color", PAPIER)
	_lettre.add_theme_font_size_override(&"font_size", roundi(TAILLE_TEXTE * 0.8))
	if police:
		_lettre.add_theme_font_override(&"font", police)
	_touche.add_child(_lettre)
	_etiquette = Label.new()
	_etiquette.add_theme_color_override(&"font_color", ENCRE)
	_etiquette.add_theme_font_size_override(&"font_size", TAILLE_TEXTE)
	if police:
		_etiquette.add_theme_font_override(&"font", police)
	rangee.add_child(_etiquette)
	modulate.a = 0.0
	hide()
	DialogueManager.dialogue_started.connect(_sur_dialogue_commence)
	DialogueManager.dialogue_ended.connect(_sur_dialogue_fini)


func _process(_delta: float) -> void:
	if visible and is_instance_valid(cible_affichee):
		var ecran := cible_affichee.get_global_transform_with_canvas().origin
		position = placer(ecran - Vector2(size.x / 2.0, HAUTEUR + size.y), size,
			get_viewport_rect().size, zones_interdites)


## Position bornée : dans les marges de l'écran, et sous toute zone interdite recouverte.
static func placer(voulue: Vector2, taille: Vector2, ecran: Vector2, interdites: Array[Rect2]) -> Vector2:
	var p := voulue
	p.x = clampf(p.x, MARGE_ECRAN, maxf(MARGE_ECRAN, ecran.x - MARGE_ECRAN - taille.x))
	p.y = clampf(p.y, MARGE_ECRAN, maxf(MARGE_ECRAN, ecran.y - MARGE_ECRAN - taille.y))
	for zone in interdites:
		if zone.grow(MARGE_ECRAN).intersects(Rect2(p, taille)):
			p.y = zone.end.y + MARGE_ECRAN
	return p


## Branche l'invite sur un messager.
func suivre(messager: Messager) -> void:
	messager.cible_changee.connect(definir_cible)
	definir_cible(messager.cible)


func definir_cible(nouvelle: Interactif) -> void:
	cible = nouvelle
	if cible != null:
		cible_affichee = cible
		_etiquette.text = libelle_pour(cible.libelle)
		_lettre.text = glyphe_action(&"interagir")
	_actualiser()


## Libellé coupé à LIBELLE_MAX caractères.
static func libelle_pour(libelle: String) -> String:
	var l := libelle.strip_edges()
	if l.length() > LIBELLE_MAX:
		l = l.left(LIBELLE_MAX - 1) + "…"
	return l


## « [E] Parler à Jacquot », libellé coupé à 24 caractères.
static func texte_pour(libelle: String) -> String:
	var l := libelle_pour(libelle)
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
				# Disposition du joueur (Q/D en AZERTY) ; indisponible sans écran (tests, CI)
				# et sur le web (#23), où l'on garde le nom de la touche physique.
				if disposition_disponible():
					code = DisplayServer.keyboard_get_keycode_from_physical(touche.physical_keycode)
			var nom := OS.get_keycode_string(code)
			if nom.is_empty():
				nom = OS.get_keycode_string(touche.physical_keycode)
			return nom
	return "?"


## Le serveur d'affichage sait-il traduire une touche physique dans la disposition du joueur ?
static func disposition_disponible() -> bool:
	return DisplayServer.get_name() != "headless" and not OS.has_feature("web")


func _actualiser() -> void:
	if _fondu and _fondu.is_valid():
		_fondu.kill()
	_fondu = create_tween()
	if cible != null and not _en_dialogue:
		show()
		_fondu.tween_property(self, "modulate:a", 1.0, DUREE_FONDU)
	elif _en_dialogue:
		_fondu.tween_property(self, "modulate:a", 0.0, DUREE_FONDU)
		_fondu.tween_callback(hide)
	else:
		# Sortie de zone : reste lisible un moment, puis s'efface.
		_fondu.tween_interval(PERSISTANCE)
		_fondu.tween_property(self, "modulate:a", 0.0, DUREE_EFFACEMENT)
		_fondu.tween_callback(hide)


func _sur_dialogue_commence(_ressource: Resource) -> void:
	_en_dialogue = true
	_actualiser()


func _sur_dialogue_fini(_ressource: Resource) -> void:
	_en_dialogue = false
	_actualiser()
