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
## Hauteur de la goutte en fraction de la taille de police (~ moitié du chiffre, 12 px à 1080).
const RAPPORT_TACHE := 0.5
const TACHES := ["bavure-tache_01", "bavure-tache_02", "bavure-tache_03"]
## Taille de la réplique selon Reglages.taille_texte (petit, normal, grand, très grand), à 1080.
const TAILLES_TEXTE := [28, 32, 38, 44]
## Icône de coût du DA par jauge (ui_cout-*.png, 32 px).
const ICONES_COUTS := {&"vivres": "cout-vivres", &"huile": "cout-huile", &"lucidite": "cout-lucidite"}
const LARGEUR := 1076.0
const MARGE_ECRAN := Vector2(46, 42)
## Écart entre le texte d'une option et son coût, en em de la police de l'option (UI/UX).
const ECART_COUT_EM := 0.8
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
var _options_posees: bool = false


func _ready() -> void:
	layer = 16
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
	# La bavure tremble : petit décalage aléatoire. Sous Lucidité basse, sur les coups du
	# battement partagé (en phase avec le ruban de Tobie et le HUD), sinon quelques fois par
	# seconde.
	var maintenant := Battement.maintenant()
	if Battement.bat(GameState.palier, false):
		if not Battement.coup(maintenant, GameState.palier, false):
			for etiquette in _baves:
				if is_instance_valid(etiquette):
					etiquette.position.y = 0.0
			return
	elif Engine.get_process_frames() % 6 != 0:
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
		# Option grisée : un refus très sourd (aucun son propre aux options qui bavent).
		AudioDirector.jouer_variante("sfx_ui_refus", AudioDirector.BUS_UI)
		return
	AudioDirector.jouer_variante("sfx_ui_valider", AudioDirector.BUS_UI)
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
	_options_posees = false
	for b in _boutons:
		if not b.disabled:
			b.grab_focus()
			break
	_options_posees = true


func _bouton_option(i: int, option: Dictionary) -> Button:
	var bouton := Button.new()
	bouton.flat = true
	bouton.focus_mode = Control.FOCUS_ALL
	bouton.disabled = not option["disponible"]
	bouton.custom_minimum_size.y = _taille() * 1.5
	bouton.pressed.connect(choisir.bind(i))
	bouton.set_meta(&"option", option)
	if not bouton.disabled:
		bouton.mouse_entered.connect(_survoler)
		bouton.focus_entered.connect(_survoler)
		# Aperçu du coût affiché sur le HUD tant que l'option a le focus (UI/UX).
		bouton.mouse_entered.connect(_apercu.bind(option))
		bouton.focus_entered.connect(_apercu.bind(option))
		bouton.mouse_exited.connect(_fin_apercu.bind(bouton))
		bouton.focus_exited.connect(_fin_apercu.bind(bouton))
	var rangee := HBoxContainer.new()
	rangee.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rangee.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	rangee.add_theme_constant_override(&"separation", 14)
	bouton.add_child(rangee)
	rangee.add_child(_etiquette("%d." % (i + 1), police_texte, roundi(_taille() * 0.76), LAVIS))
	# Le coût suit le texte de l'option, à 0,8 em (UI/UX : aligné à droite, il n'était pas lu).
	var taille_option := roundi(_taille() * 0.93)
	var phrase := HBoxContainer.new()
	phrase.name = "Phrase"
	phrase.mouse_filter = Control.MOUSE_FILTER_IGNORE
	phrase.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	phrase.add_theme_constant_override(&"separation", roundi(taille_option * ECART_COUT_EM))
	rangee.add_child(phrase)
	var texte := _etiquette(option["texte"], police_texte, taille_option, ENCRE)
	texte.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	phrase.add_child(texte)
	var affiches: Dictionary = option["couts_affiches"]
	# Une option trop longue est coupée (points de suspension) pour garder son coût dans la bulle.
	var place := largeur_texte_option(_taille(), affiches.size())
	if police_texte != null and police_texte.get_string_size(texte.text, HORIZONTAL_ALIGNMENT_LEFT, -1, taille_option).x > place:
		texte.custom_minimum_size.x = place
		texte.clip_text = true
		texte.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	for nom: StringName in affiches:
		# Icône et chiffre serrés (6 px) pour se lire comme un seul signe.
		var signe := HBoxContainer.new()
		signe.mouse_filter = Control.MOUSE_FILTER_IGNORE
		signe.add_theme_constant_override(&"separation", 6)
		phrase.add_child(signe)
		var icone := TextureRect.new()
		icone.texture = StylePapier.icone(ICONES_COUTS.get(nom, ""))
		icone.custom_minimum_size = Vector2.ONE * roundf(_taille() * 0.9)
		icone.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icone.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		icone.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		icone.mouse_filter = Control.MOUSE_FILTER_IGNORE
		icone.tooltip_text = String(nom)
		signe.add_child(icone)
		# Chiffres de coût en lavis ; ceux qui bavent passent en encre pleine épaissie.
		var cout := _etiquette("−%d" % int(affiches[nom]), police_texte, roundi(_taille() * 0.78), LAVIS)
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


## Survol d'une option (souris ou focus clavier) : sfx_ui_survol, sauf pour le premier focus
## posé d'office à l'affichage des options.
func _survoler() -> void:
	if _options_posees:
		AudioDirector.jouer_variante("sfx_ui_survol", AudioDirector.BUS_UI)


## Encre qui bave : halo rouge et contour épaissi ; tremble sauf en « effets atténués ».
func _faire_baver(etiquette: Label) -> void:
	etiquette.add_theme_color_override(&"font_shadow_color", ROUGE_HALO)
	etiquette.add_theme_constant_override(&"shadow_outline_size", 6)
	etiquette.add_theme_constant_override(&"shadow_offset_x", 0)
	etiquette.add_theme_constant_override(&"shadow_offset_y", 0)
	# Encre pleine épaissie : contraste noir contre le lavis des coûts normaux.
	etiquette.add_theme_color_override(&"font_color", ENCRE)
	etiquette.add_theme_color_override(&"font_outline_color", ENCRE)
	etiquette.add_theme_constant_override(&"outline_size", 3)
	etiquette.set_meta(&"bave", true)
	_baves.append(etiquette)


## Tache d'encre du DA sous un chiffre qui bave, comme une goutte tombée de la plume :
## opaque, haute d'environ la moitié du chiffre (~12 px à 1080), centrée, son haut touchant
## le bas du chiffre. Le sprite 32×32 est recadré sur sa zone utile pour ne pas rapetisser.
## Une variante différente par chiffre. Reste en effets atténués (le tremblement se fige).
func _ajouter_tache(etiquette: Label) -> TextureRect:
	var tache := TextureRect.new()
	tache.name = "Tache"
	tache.texture = recadrer(StylePapier.icone(TACHES[_variante_tache % TACHES.size()]))
	_variante_tache += 1
	tache.show_behind_parent = true
	tache.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tache.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	tache.stretch_mode = TextureRect.STRETCH_SCALE
	var taille_police := float(etiquette.get_theme_font_size(&"font_size"))
	# Hauteur des chiffres ≈ 0,7 × la taille de police (Spectral).
	var hauteur_chiffre := taille_police * 0.7
	var hauteur := roundf(taille_police * RAPPORT_TACHE)
	var largeur := hauteur
	if tache.texture != null and tache.texture.get_height() > 0:
		largeur = roundf(hauteur * tache.texture.get_width() / tache.texture.get_height())
	tache.size = Vector2(largeur, hauteur)
	etiquette.add_child(tache)
	# Placée quand le chiffre a sa taille (texte centré verticalement dans le Label).
	etiquette.resized.connect(func() -> void:
		tache.position = Vector2(etiquette.size.x / 2.0 - largeur / 2.0, etiquette.size.y / 2.0 + hauteur_chiffre / 2.0))
	return tache


## Texture recadrée sur ses pixels non transparents (AtlasTexture), ou telle quelle.
static func recadrer(texture: Texture2D) -> Texture2D:
	if texture == null:
		return null
	var image := texture.get_image()
	if image == null:
		return texture
	var zone := image.get_used_rect()
	if zone.size == Vector2i.ZERO or zone.size == image.get_size():
		return texture
	var atlas := AtlasTexture.new()
	atlas.atlas = texture
	atlas.region = Rect2(zone)
	return atlas


## Largeur laissée au texte d'une option : la bulle moins ses marges, le numéro et la place
## des coûts (icône, chiffre, écart de 0,8 em chacun).
static func largeur_texte_option(taille: int, nb_couts: int) -> float:
	var numero := taille * 0.76 * 2.0 + 14.0
	var un_cout := taille * 0.9 + 6.0 + taille * 0.78 * 1.4 + taille * 0.93 * ECART_COUT_EM
	return maxf(120.0, LARGEUR - 100.0 - numero - nb_couts * un_cout)


func _apercu(option: Dictionary) -> void:
	var couts: Dictionary = option["couts_affiches"]
	if is_inside_tree():
		get_tree().call_group(HudJauges.GROUPE, &"apercu_couts", couts, bool(option["bave"]))


## La souris ou le focus quitte l'option : l'aperçu revient à l'option qui garde le focus
## (évalué après le changement de focus), sinon il s'efface.
func _fin_apercu(_bouton: Button) -> void:
	_reprendre_apercu.call_deferred()


func _reprendre_apercu() -> void:
	if not is_inside_tree():
		return
	var focus := get_viewport().gui_get_focus_owner()
	if focus is Button and focus in _boutons and (focus as Button).has_meta(&"option"):
		_apercu((focus as Button).get_meta(&"option"))
	else:
		get_tree().call_group(HudJauges.GROUPE, &"fin_apercu")


func _vider_options() -> void:
	if is_inside_tree():
		get_tree().call_group(HudJauges.GROUPE, &"fin_apercu")
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
