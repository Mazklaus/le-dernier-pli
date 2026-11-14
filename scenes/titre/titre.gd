extends Control
## Écran titre (maquette UI/UX, section « Écran titre »).
## 1. Invite silencieuse : la première pression (clic, touche, bouton) déverrouille l'audio.
## 2. Menu : Reprendre la route (grisé jusqu'au jalon 2), Nouvelle marche, Options, Le studio.
##    Pas de Quitter sur le web. Navigation ui_up/ui_down/ui_accept, ui_cancel pour revenir.

enum Ecran { INVITE, MENU, OPTIONS, STUDIO }

var ecran: Ecran = Ecran.INVITE

@onready var _invite: Control = %Invite
@onready var _menu: Control = %Menu
@onready var _options: Control = %Options
@onready var _studio: Control = %Studio
@onready var _bouton_reprendre: Button = %Reprendre
@onready var _bouton_nouvelle: Button = %NouvelleMarche
@onready var _bouton_options: Button = %BoutonOptions
@onready var _bouton_studio: Button = %BoutonStudio
@onready var _bouton_quitter: Button = %Quitter


func _ready() -> void:
	_bouton_reprendre.disabled = true  # sauvegarde au jalon 2
	_bouton_quitter.visible = not OS.has_feature("web")
	_bouton_nouvelle.pressed.connect(_nouvelle_marche)
	_bouton_options.pressed.connect(_afficher.bind(Ecran.OPTIONS))
	_bouton_studio.pressed.connect(_afficher.bind(Ecran.STUDIO))
	_bouton_quitter.pressed.connect(get_tree().quit)
	%RetourStudio.pressed.connect(_afficher.bind(Ecran.MENU))
	_options.connect(&"retour_demande", _afficher.bind(Ecran.MENU))
	_afficher(Ecran.INVITE)


## _input et non _unhandled_input : à l'invite, aucun Control ne doit pouvoir avaler
## le premier clic (bug #10).
func _input(event: InputEvent) -> void:
	if ecran == Ecran.INVITE and _est_une_pression(event):
		get_viewport().set_input_as_handled()
		AudioDirector.deverrouiller()
		_afficher(Ecran.MENU)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"ui_cancel") and ecran != Ecran.MENU and ecran != Ecran.INVITE:
		get_viewport().set_input_as_handled()
		_afficher(Ecran.MENU)


func _afficher(cible: Ecran) -> void:
	var precedent := ecran
	ecran = cible
	_invite.visible = cible == Ecran.INVITE
	_menu.visible = cible == Ecran.MENU
	_options.visible = cible == Ecran.OPTIONS
	_studio.visible = cible == Ecran.STUDIO
	match cible:
		Ecran.MENU:
			var focus := _bouton_nouvelle
			if precedent == Ecran.OPTIONS:
				focus = _bouton_options
			elif precedent == Ecran.STUDIO:
				focus = _bouton_studio
			focus.grab_focus.call_deferred()
		Ecran.OPTIONS:
			_options.call(&"prendre_focus")
		Ecran.STUDIO:
			%RetourStudio.grab_focus.call_deferred()


func _nouvelle_marche() -> void:
	GameState.reinitialiser()
	SceneRouter.aller_etape(1)


static func _est_une_pression(event: InputEvent) -> bool:
	if event is InputEventKey or event is InputEventJoypadButton:
		return event.is_pressed() and not event.is_echo()
	if event is InputEventMouseButton or event is InputEventScreenTouch:
		return event.is_pressed()
	return false
