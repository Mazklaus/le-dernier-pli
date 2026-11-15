## Menu de débogage QA (F1, action Input Map "debug_menu").
## Fixe Vivres, Huile, Lucidité, les drapeaux du Sceau et saute à une rencontre.
## Ne touche JAMAIS aux variables de GameState : tout passe par la section
## ADAPTATEUR ci-dessous, seul endroit à aligner sur l'API publique.
extends CanvasLayer

# --- ADAPTATEUR (API publique de GameState, brouillon Gameplay Prog) -------
#   GameState.valeur(nom) -> int, GameState.maximum(nom) -> int
#   GameState.modifier_jauge(nom, delta)  : la fonction unique de modification
#   GameState.vers_dictionnaire() / depuis_dictionnaire(d) : seule voie publique
#     pour poser OU retirer un drapeau du Sceau sans en payer le coût
#     (abimer_sceau/rechauffer_sceau/ouvrir_sceau sont irréversibles et payants).
#   SceneRouter : périmètre Lead Prog, fonction de saut encore à confirmer.
const GAUGES: Array[StringName] = [&"vivres", &"huile", &"lucidite"]
const SEAL_FLAGS: Array[StringName] = [&"sceau_abime", &"sceau_rechauffe", &"sceau_ouvert"]
const ENCOUNTERS: Array[StringName] = [
	&"e1_reveil", &"e1_ordre", &"e1_cantine", &"e1_cendre",
	&"e1_guetteur", &"e1_sape", &"e1_adieu", &"e1_parapet",
	&"e2_poste", &"e2_barbeles", &"e2_mort", &"e2_sacoche", &"e2_cantique",
	&"e3_lisiere", &"e3_noce", &"e3_ilde", &"e3_clocher", &"e3_procession",
	&"e4_porche", &"e4_salle", &"e4_anselme", &"e4_crypte", &"e4_benediction",
	&"e5_sentier", &"e5_autre", &"e5_campement", &"e5_croix", &"e5_clairiere",
	&"e6_nef", &"e6_eloi", &"e6_tablee", &"e6_veilleur", &"e6_seuil",
	&"e7_cloches", &"e7_lise", &"e7_sceau", &"e7_mere_cloche",
]  # Level Designer : choisir une rencontre d'une autre étape y saute (SceneRouter.aller_rencontre)


func _get_gauge(id: StringName) -> int:
	return GameState.valeur(id)


func _gauge_max(id: StringName) -> int:
	return GameState.maximum(id)


func _set_gauge(id: StringName, target: int) -> void:
	# Passe par la fonction unique : signaux, paliers et effets se déclenchent.
	GameState.modifier_jauge(id, target - _get_gauge(id))


func _get_flag(id: StringName) -> bool:
	return bool(GameState.vers_dictionnaire().get(String(id), false))


func _set_flag(id: StringName, value: bool) -> void:
	var etat: Dictionary = GameState.vers_dictionnaire()
	etat[String(id)] = value
	# Cohérence de la spec : réchauffé ou ouvert implique abîmé.
	if value and id != &"sceau_abime":
		etat["sceau_abime"] = true
	GameState.depuis_dictionnaire(etat)
	_refresh()


func _goto_encounter(id: StringName) -> void:
	if SceneRouter.has_method(&"aller_rencontre"):
		SceneRouter.call(&"aller_rencontre", id)
	else:
		push_warning("DebugMenu : SceneRouter n'expose pas encore de saut de rencontre")
# --- FIN ADAPTATEUR ---------------------------------------------------------

var _panel: PanelContainer
var _spins: Dictionary = {}  # StringName -> SpinBox
var _checks: Dictionary = {}  # StringName -> CheckBox
var _encounter_pick: OptionButton
var _force_lie: CheckBox
## Mémoire vidéo occupée par les textures (mesure du budget web), rafraîchie chaque seconde.
var _memoire: Label
var _memoire_attente: float = 0.0


func _ready() -> void:
	layer = 128
	process_mode = Node.PROCESS_MODE_ALWAYS
	_build_ui()
	_panel.hide()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"debug_menu"):
		_panel.visible = not _panel.visible
		if _panel.visible:
			_refresh()
		get_viewport().set_input_as_handled()


func _build_ui() -> void:
	_panel = PanelContainer.new()
	_panel.position = Vector2(16, 16)
	add_child(_panel)
	var box := VBoxContainer.new()
	_panel.add_child(box)

	var title := Label.new()
	title.text = "DEBUG (F1)"
	box.add_child(title)

	_memoire = Label.new()
	_memoire.name = "MemoireVideo"
	box.add_child(_memoire)

	for id in GAUGES:
		var row := HBoxContainer.new()
		var lbl := Label.new()
		lbl.text = String(id)
		lbl.custom_minimum_size.x = 100
		var spin := SpinBox.new()
		spin.min_value = 0
		spin.value_changed.connect(func(v: float) -> void: _set_gauge(id, int(v)))
		row.add_child(lbl)
		row.add_child(spin)
		box.add_child(row)
		_spins[id] = spin

	for id in SEAL_FLAGS:
		var check := CheckBox.new()
		check.text = String(id)
		check.toggled.connect(func(on: bool) -> void: _set_flag(id, on))
		box.add_child(check)
		_checks[id] = check

	# Captures UI : force le coût faux + leurre à l'Égaré (bavure garantie).
	_force_lie = CheckBox.new()
	_force_lie.text = "forcer coût faux (Égaré)"
	_force_lie.toggled.connect(func(on: bool) -> void: GameState.debug_forcer_cout_faux = on)
	box.add_child(_force_lie)

	var jump_row := HBoxContainer.new()
	_encounter_pick = OptionButton.new()
	for id in ENCOUNTERS:
		_encounter_pick.add_item(String(id))
	var go := Button.new()
	go.text = "Aller"
	go.pressed.connect(func() -> void:
		_goto_encounter(ENCOUNTERS[_encounter_pick.selected]))
	jump_row.add_child(_encounter_pick)
	jump_row.add_child(go)
	box.add_child(jump_row)


func _process(delta: float) -> void:
	if not _panel.visible:
		return
	_memoire_attente -= delta
	if _memoire_attente <= 0.0:
		_memoire_attente = 1.0
		_memoire.text = texte_memoire()


## « textures : 212 Mo (vidéo : 240 Mo) », pour la mesure du budget web.
static func texte_memoire() -> String:
	var textures := Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED) / 1048576.0
	var video := Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / 1048576.0
	return "textures : %d Mo (vidéo : %d Mo)" % [roundi(textures), roundi(video)]


func _refresh() -> void:
	_memoire.text = texte_memoire()
	for id in GAUGES:
		var spin := _spins[id] as SpinBox
		spin.max_value = _gauge_max(id)  # Lucidité : 10, puis 3 après Perdu
		spin.set_value_no_signal(_get_gauge(id))
	for id in SEAL_FLAGS:
		(_checks[id] as CheckBox).set_pressed_no_signal(_get_flag(id))
	_force_lie.set_pressed_no_signal(GameState.debug_forcer_cout_faux)
