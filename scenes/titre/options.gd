extends Control
## Panneau Options, partagé entre l'écran titre et le menu pause en jeu.
## Chaque contrôle lit et écrit l'autoload Reglages.

signal retour_demande

const TAILLES := ["Petit", "Normal", "Grand", "Très grand"]
const BUS := ["Master", "Musique", "Ambiance", "SFX", "Voix", "UI"]
const NOMS_BUS := {
	"Master": "Volume général", "Musique": "Musique", "Ambiance": "Ambiance",
	"SFX": "Effets", "Voix": "Voix", "UI": "Interface",
}

var _premier: Control

@onready var _liste: VBoxContainer = %Liste


func _ready() -> void:
	var taille := OptionButton.new()
	for t: String in TAILLES:
		taille.add_item(t)
	taille.selected = Reglages.valeur(&"taille_texte")
	taille.item_selected.connect(func(i: int) -> void: Reglages.changer(&"taille_texte", i))
	_ligne("Taille du texte", taille)
	_premier = taille
	_case(&"effets_attenues", "Effets atténués")
	_case(&"hud_contextuel", "Jauges discrètes")
	_case(&"valeurs_chiffrees", "Valeurs chiffrées")
	_case(&"double_appui", "Double appui pour les choix irréversibles")
	for bus: String in BUS:
		var curseur := HSlider.new()
		curseur.min_value = 0.0
		curseur.max_value = 1.0
		curseur.step = 0.05
		curseur.custom_minimum_size.x = 320
		var cle := StringName("volume_" + bus)
		curseur.value = Reglages.valeur(cle)
		curseur.value_changed.connect(func(v: float) -> void: Reglages.changer(cle, v))
		_ligne(NOMS_BUS[bus], curseur)
	var retour := Button.new()
	retour.text = "Retour"
	retour.pressed.connect(func() -> void: retour_demande.emit())
	_liste.add_child(retour)


func prendre_focus() -> void:
	_premier.grab_focus.call_deferred()


func _case(cle: StringName, libelle: String) -> void:
	var case := CheckButton.new()
	case.button_pressed = Reglages.valeur(cle)
	case.toggled.connect(func(actif: bool) -> void: Reglages.changer(cle, actif))
	_ligne(libelle, case)


func _ligne(libelle: String, controle: Control) -> void:
	var ligne := HBoxContainer.new()
	var etiquette := Label.new()
	etiquette.text = libelle
	etiquette.custom_minimum_size.x = 520
	ligne.add_child(etiquette)
	ligne.add_child(controle)
	_liste.add_child(ligne)
