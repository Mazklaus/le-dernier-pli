extends Node
## Autoload AudioDirector : point unique de lecture du son (intégration du Sound Designer).
## S'abonne aux signaux de GameState ; GameState ne connaît pas l'audio.
## Web : rien ne joue avant la première interaction joueur (déverrouillée par l'écran titre).
##
## Squelette : les fonctions existent et sont branchées, le Sound Designer et le
## Gameplay Prog y mettent le contenu (couches d'ambiance, filtres de lucidité).

const BUS_MUSIQUE := &"Musique"
const BUS_AMBIANCE := &"Ambiance"
const BUS_SFX := &"SFX"
const BUS_VOIX := &"Voix"
const BUS_UI := &"UI"

## Slug sonore de chaque étape (convention du Sound Designer).
const SLUGS_ETAPES := {
	1: "tranchee-mere",
	2: "no-mans-land",
	3: "village-cloches-muettes",
	4: "hopital-recousus",
	5: "foret-de-croix",
	6: "cathedrale-enterree",
	7: "destinataire",
}
## Couches d'ambiance globales jouées ensemble à l'entrée d'une étape
## (amb_<slug>_<couche>.ogg). Les boucles de lieux sont posées dans les scènes.
const COUCHES_AMBIANCE := {
	1: ["surface-lit", "surface-voix", "autre"],
}

var audio_deverrouille: bool = false
var _musique: AudioStreamPlayer
var _ambiances: Array[AudioStreamPlayer] = []


func _ready() -> void:
	_musique = _creer_lecteur(BUS_MUSIQUE)
	GameState.jauge_changee.connect(_sur_jauge_changee)
	GameState.palier_change.connect(_sur_palier_change)


## Appelé par l'écran titre au premier clic ou à la première touche.
func deverrouiller() -> void:
	audio_deverrouille = true


## Appelé par SceneRouter au changement d'étape.
func jouer_etape(numero: int) -> void:
	for lecteur in _ambiances:
		lecteur.queue_free()
	_ambiances.clear()
	_musique.stop()
	var slug: String = SLUGS_ETAPES.get(numero, "")
	if slug.is_empty():
		return
	for couche: String in COUCHES_AMBIANCE.get(numero, []):
		var lecteur := _creer_lecteur(BUS_AMBIANCE)
		_ambiances.append(lecteur)
		_jouer_boucle(lecteur, "res://assets/audio/amb_%s_%s.ogg" % [slug, couche])


## Musique d'un moment de l'étape courante (mus_<slug>_<moment>.ogg).
func jouer_musique(numero: int, moment: String) -> void:
	var slug: String = SLUGS_ETAPES.get(numero, "")
	_jouer_boucle(_musique, "res://assets/audio/mus_%s_%s.ogg" % [slug, moment])


## Le timbre d'une rencontre ou d'un objet (sfx_<famille>_<action>_NN.wav).
func jouer_timbre(nom: String) -> void:
	jouer_sfx(nom, BUS_SFX)


func jouer_sfx(nom: String, bus: StringName = BUS_SFX) -> void:
	if not audio_deverrouille:
		return
	var chemin := "res://assets/audio/%s.wav" % nom
	if not ResourceLoader.exists(chemin):
		return
	var lecteur := _creer_lecteur(bus)
	lecteur.stream = load(chemin)
	lecteur.finished.connect(lecteur.queue_free)
	lecteur.play()


func set_lucidite(valeur: int) -> void:
	# À remplir avec le Sound Designer : filtres et couches selon la lucidité.
	pass


func _sur_jauge_changee(nom: StringName, _ancienne: int, nouvelle: int) -> void:
	if nom == GameState.LUCIDITE:
		set_lucidite(nouvelle)


func _sur_palier_change(_ancien: StringName, _nouveau: StringName) -> void:
	pass


func _jouer_boucle(lecteur: AudioStreamPlayer, chemin: String) -> void:
	if not audio_deverrouille or not ResourceLoader.exists(chemin):
		return
	lecteur.stream = load(chemin)
	lecteur.play()


func _creer_lecteur(bus: StringName) -> AudioStreamPlayer:
	var lecteur := AudioStreamPlayer.new()
	lecteur.bus = bus if AudioServer.get_bus_index(bus) != -1 else &"Master"
	add_child(lecteur)
	return lecteur
