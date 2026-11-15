extends Node
## Autoload Reglages : options du joueur (maquette UI/UX), séparées de la sauvegarde du jeu.
## Stockées dans user://reglages.cfg (IndexedDB sur le web). Les autres systèmes lisent
## les valeurs et écoutent reglage_change.

signal reglage_change(cle: StringName, valeur: Variant)

const FICHIER := "user://reglages.cfg"
const SECTION := "reglages"

## Valeurs par défaut. Volumes en linéaire 0..1, appliqués aux bus du même nom.
const DEFAUTS := {
	&"taille_texte": 1,  # 0 petit, 1 normal, 2 grand, 3 très grand
	&"effets_attenues": false,  # tremblement, distorsions de Lucidité réduits
	&"hud_contextuel": true,  # jauges visibles seulement quand elles changent
	&"valeurs_chiffrees": false,  # afficher les chiffres des jauges
	&"double_appui": false,  # confirmer un choix irréversible par un second appui
	&"volume_Master": 1.0,
	&"volume_Musique": 0.8,
	&"volume_Ambiance": 0.8,
	&"volume_SFX": 0.9,
	&"volume_Voix": 1.0,
	&"volume_UI": 0.8,
}

var _valeurs: Dictionary = {}


func _ready() -> void:
	charger()


func valeur(cle: StringName) -> Variant:
	return _valeurs.get(cle, DEFAUTS.get(cle))


func changer(cle: StringName, nouvelle: Variant) -> void:
	if not DEFAUTS.has(cle):
		push_error("Reglages : clé inconnue %s" % cle)
		return
	if _valeurs.get(cle) == nouvelle:
		return
	_valeurs[cle] = nouvelle
	_appliquer(cle)
	reglage_change.emit(cle, nouvelle)
	sauver()


func charger() -> void:
	_valeurs = DEFAUTS.duplicate()
	var cfg := ConfigFile.new()
	if cfg.load(FICHIER) == OK:
		for cle: StringName in DEFAUTS:
			var lu: Variant = cfg.get_value(SECTION, String(cle), DEFAUTS[cle])
			if typeof(lu) == typeof(DEFAUTS[cle]):
				_valeurs[cle] = lu
	else:
		# Tout premier lancement : sur le web, on suit la préférence du navigateur
		# (prefers-reduced-motion) ; le joueur reste libre de changer ensuite (UI/UX).
		_valeurs[&"effets_attenues"] = mouvement_reduit_demande()
	for cle: StringName in _valeurs:
		_appliquer(cle)


## Le navigateur demande-t-il moins d'animations (prefers-reduced-motion) ? Faux hors web.
static func mouvement_reduit_demande() -> bool:
	if not OS.has_feature("web"):
		return false
	var reponse: Variant = JavaScriptBridge.eval(
		"!!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches)", true)
	return reponse == true


func sauver() -> void:
	var cfg := ConfigFile.new()
	for cle: StringName in _valeurs:
		cfg.set_value(SECTION, String(cle), _valeurs[cle])
	cfg.save(FICHIER)


func _appliquer(cle: StringName) -> void:
	var texte := String(cle)
	if texte.begins_with("volume_"):
		var bus := AudioServer.get_bus_index(texte.trim_prefix("volume_"))
		if bus != -1:
			var lineaire: float = _valeurs[cle]
			AudioServer.set_bus_volume_db(bus, linear_to_db(maxf(lineaire, 0.0001)))
			AudioServer.set_bus_mute(bus, lineaire <= 0.0)
