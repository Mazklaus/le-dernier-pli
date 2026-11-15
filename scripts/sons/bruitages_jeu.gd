class_name BruitagesJeu
extends Node
## Bruitages déclenchés par l'état du jeu (liste du Sound Designer, #37). Posé par
## AudioDirector ; écoute GameState et joue par AudioDirector.jouer_variante :
## - sceau abîmé / réchauffé / ouvert : sfx_sceau_abimer / _rechauffer / _ouvrir ;
## - marque gagnée : sfx_carnet_fremir (bus UI, très discret, jamais une fanfare) ;
## - huile qui remonte : sfx_lanterne_remplir ; vivres qui remontent : sfx_pain_manger ;
## - lanterne allumée en entrant dans le noir : sfx_lanterne_allumer, éteinte en sortant
##   ou faute d'huile : sfx_lanterne_eteindre ;
## - ligne du pli lue en transparence : sfx_pli_lire ;
## - Cassien cendre le messager (e1_cendre vue) : sfx_cendre_front.

const SONS_SCEAU := {
	&"abime": "sfx_sceau_abimer",
	&"rechauffe": "sfx_sceau_rechauffer",
	&"ouvert": "sfx_sceau_ouvrir",
}
const SONS_RENCONTRE := {&"e1_cendre": "sfx_cendre_front"}

var _lanterne_allumee: bool = false


func _ready() -> void:
	GameState.sceau_change.connect(func(d: StringName) -> void: _jouer(son_sceau(d)))
	GameState.marque_gagnee.connect(func(_m: Dictionary) -> void:
		_jouer("sfx_carnet_fremir", AudioDirector.BUS_UI))
	GameState.jauge_changee.connect(func(nom: StringName, a: int, n: int) -> void:
		_jouer(son_jauge(nom, a, n)))
	GameState.ligne_pli_lue.connect(_sur_ligne_pli)
	GameState.zone_sombre_changee.connect(_sur_zone_sombre)
	GameState.etat_declenche.connect(_sur_etat)
	GameState.rencontre_vue_marquee.connect(func(id: StringName) -> void:
		_jouer(String(SONS_RENCONTRE.get(id, ""))))
	GameState.etat_charge.connect(func() -> void: _lanterne_allumee = GameState.lanterne_allumee)


static func son_sceau(drapeau: StringName) -> String:
	return String(SONS_SCEAU.get(drapeau, ""))


## Seules les hausses ont un son : remplir la lanterne, manger. Les baisses (coûts) se lisent
## sur le HUD.
static func son_jauge(nom: StringName, ancienne: int, nouvelle: int) -> String:
	if nouvelle <= ancienne:
		return ""
	match nom:
		&"huile":
			return "sfx_lanterne_remplir"
		&"vivres":
			return "sfx_pain_manger"
	return ""


func _sur_zone_sombre(dans_zone: bool, lanterne: bool) -> void:
	if dans_zone and lanterne and not _lanterne_allumee:
		_jouer("sfx_lanterne_allumer")
	elif _lanterne_allumee and not (dans_zone and lanterne):
		_jouer("sfx_lanterne_eteindre")
	_lanterne_allumee = dans_zone and lanterne


func _sur_ligne_pli(_index: int) -> void:
	_jouer("sfx_pli_lire")


func _sur_etat(etat: StringName) -> void:
	if etat == &"lanterne_eteinte" and _lanterne_allumee:
		_lanterne_allumee = false
		_jouer("sfx_lanterne_eteindre")


func _jouer(base: String, bus: StringName = AudioDirector.BUS_SFX) -> void:
	if base != "":
		AudioDirector.jouer_variante(base, bus)
