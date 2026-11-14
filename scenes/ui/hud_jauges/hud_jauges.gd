class_name HudJauges
extends Control
## HUD des jauges (maquette UI/UX v0.6) : plaque en haut à gauche avec Vivres (sacoche +
## 10 bâtons), Huile (lanterne + 6 bâtons) et Lucidité (œil + nom du palier, jamais de
## chiffre) ; plaque en haut à droite avec le sceau et le carnet.
## Lit GameState par son API et ses signaux. Options : Reglages.hud_contextuel (le HUD
## s'efface 3 s après le dernier changement), valeurs_chiffrees, effets_attenues.
## La bulle le retient pleinement visible tant qu'une rencontre affiche des coûts (retenir).

const GROUPE: StringName = &"hud_jauges"
## Boîte des icônes de jauge : les dessins du DA (80 px) ont ~8 px de marge transparente,
## une boîte de 100 px les affiche à ~80 px à 1080 comme dans la spec.
const TAILLE_ICONE := 100.0

const SEUIL_BAS := 1
const DELAI_CONTEXTUEL := 3.0
const DUREE_FONDU := 0.6
const MARGE := 38.0
const NOMS_PALIERS := {&"clair": "Clair", &"trouble": "Trouble", &"egare": "Égaré"}

var _icones: Dictionary = {}  # jauge -> TextureRect
var _libelles: Dictionary = {}  # jauge -> Label
var _chiffres: Dictionary = {}  # jauge -> Label
var _batons: Dictionary = {}  # jauge -> Batons
var _sceau: TextureRect
var _carnet: TextureRect
var _ceinture: PanelContainer
var _coin: PanelContainer
var _fondu: Tween
var _minuteur: Timer
var _temps: float = 0.0
var _retenu: bool = false


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_to_group(GROUPE)
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_construire()
	_minuteur = Timer.new()
	_minuteur.one_shot = true
	_minuteur.timeout.connect(_estomper)
	add_child(_minuteur)
	GameState.jauge_changee.connect(_sur_jauge_changee)
	GameState.palier_change.connect(func(_a: StringName, _n: StringName) -> void: _sur_changement())
	GameState.etat_declenche.connect(func(_e: StringName) -> void: _sur_changement())
	GameState.sceau_change.connect(func(_d: StringName) -> void: _sur_changement())
	GameState.marque_gagnee.connect(func(_m: Dictionary) -> void: _sur_changement())
	GameState.etat_charge.connect(actualiser)
	Reglages.reglage_change.connect(func(_c: StringName, _v: Variant) -> void: actualiser())
	actualiser()
	_montrer()


func _process(delta: float) -> void:
	_temps += delta
	var attenue: bool = Reglages.valeur(&"effets_attenues")
	for jauge: StringName in [GameState.VIVRES, GameState.HUILE]:
		var icone: TextureRect = _icones[jauge]
		var bas := GameState.valeur(jauge) <= SEUIL_BAS
		icone.scale = Vector2.ONE * (1.0 + 0.08 * maxf(0.0, sin(_temps * TAU / 1.4))) if bas and not attenue else Vector2.ONE
	# Trouble et Égaré : les icônes tremblent (plus fort à l'Égaré).
	var force := 0.0 if attenue else {&"clair": 0.0, &"trouble": 0.6, &"egare": 1.4}.get(GameState.palier, 0.0) as float
	var secousse := Vector2.ZERO
	if force > 0.0 and fmod(_temps, 1.8 / force) < 0.12:
		secousse = Vector2(randf_range(-1.5, 1.5), randf_range(-1.0, 1.0)) * force
	for jauge: StringName in _icones:
		(_icones[jauge] as TextureRect).position = secousse
	_sceau.position = secousse


## Relit tout l'état de GameState (au démarrage, après un chargement, un réglage).
func actualiser() -> void:
	var chiffres: bool = Reglages.valeur(&"valeurs_chiffrees")
	for jauge: StringName in GameState.JAUGES:
		var v := GameState.valeur(jauge)
		(_icones[jauge] as TextureRect).texture = StylePapier.icone(icone_jauge(jauge, v, GameState.palier))
		var libelle: Label = _libelles[jauge]
		libelle.text = libelle_jauge(jauge, v, GameState.palier, GameState.est_perdu())
		var souligne := jauge != GameState.LUCIDITE and v <= SEUIL_BAS
		libelle.add_theme_constant_override(&"underline_thickness", 2 if souligne else 0)
		libelle.set_meta(&"bas", souligne)
		if _batons.has(jauge):
			(_batons[jauge] as Batons).valeur = v
		if _chiffres.has(jauge):
			var chiffre: Label = _chiffres[jauge]
			chiffre.visible = chiffres
			chiffre.text = "%d / %d" % [v, GameState.maximum(jauge)]
	_sceau.texture = StylePapier.icone(icone_sceau())


## Nom court de l'icône du DA pour une jauge.
static func icone_jauge(jauge: StringName, v: int, palier: StringName) -> String:
	match jauge:
		GameState.VIVRES:
			return "sacoche-pleine" if v >= 6 else ("sacoche-moitie" if v >= 2 else "sacoche-vide")
		GameState.HUILE:
			return "lanterne-pleine" if v >= 3 else ("lanterne-faible" if v >= 1 else "lanterne-eteinte")
		GameState.LUCIDITE:
			return "oeil-%s" % palier
	return ""


## Libellé sous l'icône : nom de la jauge, état à zéro, palier pour la Lucidité.
static func libelle_jauge(jauge: StringName, v: int, palier: StringName, perdu: bool) -> String:
	match jauge:
		GameState.VIVRES:
			return "Affamé" if v == 0 else "Vivres"
		GameState.HUILE:
			return "Éteinte" if v == 0 else "Huile"
		GameState.LUCIDITE:
			return "Perdu" if perdu else NOMS_PALIERS.get(palier, "")
	return ""


static func icone_sceau() -> String:
	if GameState.sceau_ouvert:
		return "sceau-ouvert"
	if GameState.sceau_rechauffe:
		return "sceau-rechauffe"
	if GameState.sceau_abime:
		return "sceau-abime"
	return "sceau-intact"


func _sur_jauge_changee(_nom: StringName, _ancienne: int, _nouvelle: int) -> void:
	_sur_changement()


func _sur_changement() -> void:
	actualiser()
	_montrer()


## Mode contextuel : le HUD revient à chaque changement, puis s'efface après 3 s,
## sauf si une jauge est au seuil bas.
func _montrer() -> void:
	_fondre(1.0)
	if Reglages.valeur(&"hud_contextuel") and not _retenu:
		_minuteur.start(DELAI_CONTEXTUEL)
	else:
		_minuteur.stop()


## Tant que `actif`, le HUD reste pleinement visible (rencontre avec coûts : le joueur
## compare le coût à son stock) ; ensuite le mode contextuel reprend son délai.
func retenir(actif: bool) -> void:
	if actif == _retenu:
		return
	_retenu = actif
	if actif:
		_minuteur.stop()
		_fondre(1.0)
	else:
		_montrer()


func _estomper() -> void:
	if _retenu or not Reglages.valeur(&"hud_contextuel"):
		return
	if GameState.valeur(GameState.VIVRES) <= SEUIL_BAS or GameState.valeur(GameState.HUILE) <= SEUIL_BAS:
		return
	_fondre(0.0)


func _fondre(cible: float) -> void:
	if _fondu and _fondu.is_valid():
		_fondu.kill()
	_fondu = create_tween()
	_fondu.tween_property(self, "modulate:a", cible, DUREE_FONDU)


func _construire() -> void:
	_ceinture = PanelContainer.new()
	_ceinture.add_theme_stylebox_override(&"panel", StylePapier.plaque(20.0))
	_ceinture.position = Vector2(MARGE, MARGE)
	add_child(_ceinture)
	var rangee := HBoxContainer.new()
	rangee.add_theme_constant_override(&"separation", 38)
	_ceinture.add_child(rangee)
	for jauge: StringName in GameState.JAUGES:
		rangee.add_child(_jauge(jauge))

	_coin = PanelContainer.new()
	_coin.add_theme_stylebox_override(&"panel", StylePapier.plaque(16.0))
	_coin.anchor_left = 1.0
	_coin.anchor_right = 1.0
	_coin.offset_right = -MARGE
	_coin.offset_top = MARGE
	_coin.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	add_child(_coin)
	var colonne := VBoxContainer.new()
	colonne.alignment = BoxContainer.ALIGNMENT_CENTER
	colonne.add_theme_constant_override(&"separation", 8)
	_coin.add_child(colonne)
	_sceau = _icone(96.0)
	colonne.add_child(_cellule(_sceau, "Le pli"))
	_carnet = _icone(64.0)
	_carnet.texture = StylePapier.icone("carnet")
	colonne.add_child(_cellule(_carnet, "Carnet"))


func _jauge(jauge: StringName) -> Control:
	var colonne := VBoxContainer.new()
	colonne.alignment = BoxContainer.ALIGNMENT_END
	colonne.add_theme_constant_override(&"separation", 6)
	var icone := _icone(TAILLE_ICONE)
	_icones[jauge] = icone
	var support := Control.new()
	support.custom_minimum_size = Vector2.ONE * TAILLE_ICONE
	support.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	support.add_child(icone)
	colonne.add_child(support)
	if jauge != GameState.LUCIDITE:
		var batons := Batons.new()
		batons.maximum = GameState.maximum(jauge)
		batons.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		_batons[jauge] = batons
		colonne.add_child(batons)
	var libelle := _texte("", StylePapier.POLICE_TITRE, 26, StylePapier.ENCRE)
	_libelles[jauge] = libelle
	colonne.add_child(libelle)
	if jauge != GameState.LUCIDITE:
		var chiffre := _texte("", StylePapier.POLICE_TEXTE, 18, StylePapier.LAVIS)
		_chiffres[jauge] = chiffre
		colonne.add_child(chiffre)
	return colonne


func _cellule(icone: TextureRect, texte: String) -> Control:
	var colonne := VBoxContainer.new()
	colonne.alignment = BoxContainer.ALIGNMENT_CENTER
	var support := Control.new()
	support.custom_minimum_size = icone.custom_minimum_size
	support.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	support.add_child(icone)
	colonne.add_child(support)
	colonne.add_child(_texte(texte, StylePapier.POLICE_TITRE, 24, StylePapier.ENCRE))
	return colonne


func _icone(taille: float) -> TextureRect:
	var icone := TextureRect.new()
	icone.custom_minimum_size = Vector2(taille, taille)
	icone.size = Vector2(taille, taille)
	icone.pivot_offset = Vector2(taille, taille) / 2.0
	icone.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	icone.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	icone.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return icone


func _texte(texte: String, police: String, taille: int, couleur: Color) -> Label:
	var etiquette := Label.new()
	etiquette.text = texte
	etiquette.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	etiquette.add_theme_color_override(&"font_color", couleur)
	etiquette.add_theme_font_size_override(&"font_size", taille)
	var f := StylePapier.police(police)
	if f:
		etiquette.add_theme_font_override(&"font", f)
	return etiquette
