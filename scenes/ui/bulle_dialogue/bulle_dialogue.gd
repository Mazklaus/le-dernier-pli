extends CanvasLayer
## Bulle de dialogue (maquette UI/UX v0.6) : plaque de papier en bas à droite, locuteur en
## petites capitales, réplique en italique tapée lettre à lettre, options numérotées avec
## leurs coûts. Branchée comme bulle de Dialogue Manager (runtime/balloon_path).
## Règles de présentation (coûts, bavure, options cachées, timbre) : OptionsDialogue.
## Entrées : « interagir » ou « clic » pour avancer, « choix_1 » à « choix_4 », ui_up / ui_down.

const ENCRE := StylePapier.ENCRE
const LAVIS := StylePapier.LAVIS
const ROUGE_HALO := Color(0.608, 0.11, 0.11, 0.35)
## Amplitude du tremblement de la bavure, en pixels (renforcée à la demande de l'UI/UX).
const TREMBLEMENT := 3.0
const TACHES := ["bavure-tache_01", "bavure-tache_02", "bavure-tache_03"]
## Taille de la réplique selon Reglages.taille_texte (petit, normal, grand, très grand), à 1080.
const TAILLES_TEXTE := [28, 32, 38, 44]
## Icône de coût du DA par jauge (ui_cout-*.png, 32 px).
const ICONES_COUTS := {&"vivres": "cout-vivres", &"huile": "cout-huile", &"lucidite": "cout-lucidite"}
const LARGEUR := 1076.0
const MARGE_ECRAN := Vector2(46, 42)
const ACTIONS_CHOIX: Array[StringName] = [&"choix_1", &"choix_2", &"choix_3", &"choix_4"]

## Polices de la maquette ; à défaut, celles du DA (IM Fell English SC, Spectral, Spectral italique).
@export var police_locuteur: Font
@export var police_texte: Font
@export var police_replique: Font

var ressource: DialogueResource
var ligne: DialogueLine
var options_affichees: Array[Dictionary] = []

var _etats: Array = []
var _attend_suite: bool = false
var _plaque: PanelContainer
var _locuteur: Label
var _replique: DialogueLabel
var _options: VBoxContainer
var _boutons: Array[Button] = []
var _baves: Array[Label] = []
var _variante_tache: int = 0
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	layer = 10
	_rng.randomize()
	if police_locuteur == null:
		police_locuteur = StylePapier.police(StylePapier.POLICE_TITRE)
	if police_texte == null:
		police_texte = StylePapier.police(StylePapier.POLICE_TEXTE)
	if police_replique == null:
		police_replique = StylePapier.police(StylePapier.POLICE_ITALIQUE)
	_construire()
	_plaque.hide()
	Reglages.reglage_change.connect(_sur_reglage_change)


func _process(_delta: float) -> void:
	if Reglages.valeur(&"effets_attenues"):
		return
	# La bavure tremble : petit décalage aléatoire, quelques fois par seconde.
	if Engine.get_process_frames() % 6 != 0:
		return
	for etiquette in _baves:
		if is_instance_valid(etiquette):
			etiquette.position.y = _rng.randf_range(-TREMBLEMENT, TREMBLEMENT)


func _unhandled_input(event: InputEvent) -> void:
	# Seule la bulle reçoit les entrées tant qu'elle est ouverte.
	get_viewport().set_input_as_handled()
	if ligne == null:
		return
	if event.is_action_pressed(&"interagir") or event.is_action_pressed(&"clic"):
		if _replique.is_typing:
			_replique.skip_typing()
		elif _attend_suite:
			_suivante(ligne.next_id)
		return
	for i in ACTIONS_CHOIX.size():
		if event.is_action_pressed(ACTIONS_CHOIX[i]) and i < options_affichees.size():
			choisir(i)
			return


## Appelé par Dialogue Manager.
func start(avec_ressource: DialogueResource, cue: String = "", etats_supplementaires: Array = []) -> void:
	ressource = avec_ressource
	_etats = [self] + etats_supplementaires
	_afficher(await ressource.get_next_dialogue_line(cue, _etats))


## Choisit l'option visible n° `i` (0 = la première affichée).
func choisir(i: int) -> void:
	if i < 0 or i >= options_affichees.size() or _replique.is_typing:
		return
	var option := options_affichees[i]
	if not option["disponible"]:
		return
	var a_prelever: Dictionary = option["a_prelever"]
	if not a_prelever.is_empty():
		GameState.appliquer_couts(a_prelever)
	var reponse: DialogueResponse = ligne.responses[option["index"]]
	_suivante(reponse.next_id)


func _exit_tree() -> void:
	_retenir_hud(false)


## Garde le HUD des jauges pleinement visible pendant un choix avec coûts.
func _retenir_hud(actif: bool) -> void:
	if is_inside_tree():
		get_tree().call_group(HudJauges.GROUPE, &"retenir", actif)


func _suivante(id: String) -> void:
	_attend_suite = false
	_afficher(await ressource.get_next_dialogue_line(id, _etats))


func _afficher(nouvelle: DialogueLine) -> void:
	ligne = nouvelle
	if ligne == null:
		queue_free()
		return
	_vider_options()
	_locuteur.visible = not ligne.character.is_empty()
	_locuteur.text = ligne.character
	var slug := OptionsDialogue.slug_timbre(ligne.character, ligne.tags) if not ligne.character.is_empty() else ""
	if slug != "":
		AudioDirector.jouer_timbre(slug)
	_appliquer_tailles()
	_plaque.show()
	_replique.dialogue_line = ligne
	if not ligne.text.is_empty():
		_replique.type_out()
		await _replique.finished_typing
	if ligne == null:
		return
	if ligne.responses.size() > 0:
		_montrer_options()
	else:
		_attend_suite = true


func _montrer_options() -> void:
	var brutes: Array = []
	for r: DialogueResponse in ligne.responses:
		brutes.append({"texte": r.text, "tags": r.tags, "autorisee": r.is_allowed})
	options_affichees = OptionsDialogue.presenter(brutes, _rng)
	_variante_tache = _rng.randi_range(0, TACHES.size() - 1)
	_retenir_hud(options_affichees.any(func(o: Dictionary) -> bool: return not (o["couts_affiches"] as Dictionary).is_empty()))
	for i in options_affichees.size():
		var bouton := _bouton_option(i, options_affichees[i])
		_options.add_child(bouton)
		_boutons.append(bouton)
	for b in _boutons:
		if not b.disabled:
			b.grab_focus()
			break


func _bouton_option(i: int, option: Dictionary) -> Button:
	var bouton := Button.new()
	bouton.flat = true
	bouton.focus_mode = Control.FOCUS_ALL
	bouton.disabled = not option["disponible"]
	bouton.custom_minimum_size.y = _taille() * 1.5
	bouton.pressed.connect(choisir.bind(i))
	var rangee := HBoxContainer.new()
	rangee.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rangee.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	rangee.add_theme_constant_override(&"separation", 14)
	bouton.add_child(rangee)
	rangee.add_child(_etiquette("%d." % (i + 1), police_texte, roundi(_taille() * 0.76), LAVIS))
	var texte := _etiquette(option["texte"], police_texte, roundi(_taille() * 0.93), ENCRE)
	texte.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	texte.clip_text = true
	rangee.add_child(texte)
	var affiches: Dictionary = option["couts_affiches"]
	for nom: StringName in affiches:
		# Icône et chiffre serrés (6 px) pour se lire comme un seul signe.
		var signe := HBoxContainer.new()
		signe.mouse_filter = Control.MOUSE_FILTER_IGNORE
		signe.add_theme_constant_override(&"separation", 6)
		rangee.add_child(signe)
		var icone := TextureRect.new()
		icone.texture = StylePapier.icone(ICONES_COUTS.get(nom, ""))
		icone.custom_minimum_size = Vector2.ONE * roundf(_taille() * 0.9)
		icone.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icone.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		icone.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		icone.mouse_filter = Control.MOUSE_FILTER_IGNORE
		icone.tooltip_text = String(nom)
		signe.add_child(icone)
		var cout := _etiquette("−%d" % int(affiches[nom]), police_texte, roundi(_taille() * 0.78), ENCRE)
		cout.set_meta(&"jauge", nom)
		signe.add_child(cout)
		if option["bave"]:
			# Le glyphe de la jauge reste net : seul le chiffre bave, avec sa tache.
			_faire_baver(cout)
			_ajouter_tache(cout)
	if option["bave"] and affiches.is_empty():
		_faire_baver(texte)
	if bouton.disabled:
		rangee.modulate.a = 0.42
	return bouton


## Encre qui bave : halo rouge et contour épaissi ; tremble sauf en « effets atténués ».
func _faire_baver(etiquette: Label) -> void:
	etiquette.add_theme_color_override(&"font_shadow_color", ROUGE_HALO)
	etiquette.add_theme_constant_override(&"shadow_outline_size", 6)
	etiquette.add_theme_constant_override(&"shadow_offset_x", 0)
	etiquette.add_theme_constant_override(&"shadow_offset_y", 0)
	etiquette.add_theme_color_override(&"font_outline_color", Color(ENCRE, 0.5))
	etiquette.add_theme_constant_override(&"outline_size", 2)
	etiquette.set_meta(&"bave", true)
	_baves.append(etiquette)


## Tache d'encre du DA sous un chiffre qui bave, comme une goutte tombée de la plume :
## un tiers de la hauteur du chiffre, centrée, son haut touchant le bas du chiffre (le
## chiffre reste lisible, même faux). Une variante différente par chiffre. Reste en effets
## atténués (seul le tremblement se fige).
func _ajouter_tache(etiquette: Label) -> TextureRect:
	var tache := TextureRect.new()
	tache.name = "Tache"
	tache.texture = StylePapier.icone(TACHES[_variante_tache % TACHES.size()])
	_variante_tache += 1
	tache.show_behind_parent = true
	tache.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tache.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	tache.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	var taille_police := float(etiquette.get_theme_font_size(&"font_size"))
	# Hauteur des chiffres ≈ 0,7 × la taille de police (Spectral).
	var hauteur_chiffre := taille_police * 0.7
	var cote := roundf(hauteur_chiffre / 3.0)
	tache.size = Vector2(cote, cote)
	etiquette.add_child(tache)
	# Placée quand le chiffre a sa taille (texte centré verticalement dans le Label).
	etiquette.resized.connect(func() -> void:
		tache.position = Vector2(etiquette.size.x / 2.0 - cote / 2.0, etiquette.size.y / 2.0 + hauteur_chiffre / 2.0))
	return tache


func _vider_options() -> void:
	_retenir_hud(false)
	for b in _boutons:
		b.queue_free()
	_boutons.clear()
	_baves.clear()
	options_affichees.clear()


func _etiquette(texte: String, police: Font, taille: int, couleur: Color) -> Label:
	var etiquette := Label.new()
	etiquette.text = texte
	etiquette.mouse_filter = Control.MOUSE_FILTER_IGNORE
	etiquette.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	etiquette.add_theme_color_override(&"font_color", couleur)
	etiquette.add_theme_font_size_override(&"font_size", taille)
	if police:
		etiquette.add_theme_font_override(&"font", police)
	return etiquette


func _taille() -> int:
	var index: int = clampi(int(Reglages.valeur(&"taille_texte")), 0, TAILLES_TEXTE.size() - 1)
	return TAILLES_TEXTE[index]


func _appliquer_tailles() -> void:
	var t := _taille()
	_locuteur.add_theme_font_size_override(&"font_size", roundi(t * 1.12))
	_replique.add_theme_font_size_override(&"normal_font_size", t)
	_replique.add_theme_font_size_override(&"italics_font_size", t)


func _sur_reglage_change(cle: StringName, _valeur: Variant) -> void:
	if cle == &"taille_texte":
		_appliquer_tailles()


func _construire() -> void:
	var racine := Control.new()
	racine.mouse_filter = Control.MOUSE_FILTER_IGNORE
	racine.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(racine)

	_plaque = PanelContainer.new()
	_plaque.anchor_left = 1.0
	_plaque.anchor_right = 1.0
	_plaque.anchor_top = 1.0
	_plaque.anchor_bottom = 1.0
	_plaque.offset_left = -MARGE_ECRAN.x - LARGEUR
	_plaque.offset_right = -MARGE_ECRAN.x
	_plaque.offset_bottom = -MARGE_ECRAN.y
	_plaque.grow_vertical = Control.GROW_DIRECTION_BEGIN
	# Plaque de papier au bord déchiré du DA (9 tranches, marge de texture 40 px).
	var style := StylePapier.plaque(50.0, 40.0, 36.0)
	_plaque.add_theme_stylebox_override(&"panel", style)
	racine.add_child(_plaque)

	var colonne := VBoxContainer.new()
	colonne.add_theme_constant_override(&"separation", 10)
	_plaque.add_child(colonne)

	var entete := HBoxContainer.new()
	entete.add_theme_constant_override(&"separation", 16)
	colonne.add_child(entete)
	_locuteur = _etiquette("", police_locuteur, 36, ENCRE)
	entete.add_child(_locuteur)
	var filet := HSeparator.new()
	filet.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	entete.add_child(filet)

	_replique = DialogueLabel.new()
	_replique.bbcode_enabled = true
	_replique.fit_content = true
	_replique.scroll_active = false
	_replique.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_replique.custom_minimum_size.x = LARGEUR - 100
	_replique.add_theme_color_override(&"default_color", ENCRE)
	if police_replique:
		# Réplique tout en Spectral italique (retour UI/UX).
		_replique.add_theme_font_override(&"normal_font", police_replique)
		_replique.add_theme_font_override(&"italics_font", police_replique)
	if police_texte:
		_replique.add_theme_font_override(&"bold_font", police_texte)
	colonne.add_child(_replique)

	_options = VBoxContainer.new()
	_options.add_theme_constant_override(&"separation", 4)
	colonne.add_child(_options)
