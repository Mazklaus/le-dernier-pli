extends Node
## Autoload AudioDirector : point unique de lecture du son (intégration du Sound Designer).
## S'abonne aux signaux de GameState ; GameState ne connaît pas l'audio.
## Web : rien ne joue avant la première interaction joueur (déverrouillée par l'écran titre).
##
## Mixage selon la Lucidité : les règles chiffrées sont dans scripts/regles/mixage_son.gd.
## Ici, on ne fait que les appliquer en fondu aux couches de l'étape et au passe-bas
## du bus Ambiance.

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
	2: ["surface", "autre"],
	3: ["jour", "nuit", "autre"],
	4: ["hopital", "autre"],
	5: ["foret", "autre"],
	6: ["profondeur", "autre"],
	7: ["salle", "autre"],
}
## Groupe des émetteurs qu'on n'entend que dans le noir sans lanterne (ex. les fils de
## l'étape 2). Le Level Designer met l'AudioStreamPlayer2D dans ce groupe, en autoplay :
## AudioDirector le garde muet et le fait monter en fondu quand le messager est dans le noir.
const GROUPE_SON_DU_NOIR := &"son_du_noir"
const DUREE_FONDU_NOIR := 3.0
## Couches de la famille « autre » (ce que la Lucidité qui baisse laisse passer) ;
## toutes les autres couches sont du « réel ».
const COUCHES_AUTRE: Array[String] = ["autre"]
## Couches de voix dont le gain suit la position du messager (repères de surface).
const COUCHES_VOIX: Array[String] = ["surface-voix"]
## Entrée et sortie de la musique, en secondes.
const DUREE_FONDU_MUSIQUE := 4.0

var audio_deverrouille: bool = false
var _musique: AudioStreamPlayer
## couche -> lecteur, pour l'étape en cours.
var _couches: Dictionary = {}
## Mélange courant (interpolé par les fondus), en gains linéaires.
var _mix_reel: float = 1.0
var _mix_autre: float = 0.0
var _gain_voix: float = 1.0
## Part de la nuit dans le mélange des couches « jour » et « nuit » (0 : jour, 1 : nuit).
var _mix_nuit: float = 0.0
var _fondu_phase: Tween
var _dans_le_noir: bool = false
var _fondu: Tween
var _fondu_musique: Tween
var _passe_bas: AudioEffectLowPassFilter
var _suivi_joueur: Node2D
var _points_voix: Array[Vector2] = []
var _rng := RandomNumberGenerator.new()
var _cache_variantes: Dictionary = {}
var _derniere_variante: Dictionary = {}


func _ready() -> void:
	_musique = _creer_lecteur(BUS_MUSIQUE)
	_passe_bas = _installer_passe_bas()
	_rng.randomize()
	GameState.palier_change.connect(_sur_palier_change)
	GameState.etat_declenche.connect(_sur_etat_declenche)
	GameState.etat_charge.connect(_sur_etat_charge)
	GameState.zone_sombre_changee.connect(_sur_zone_sombre_changee)
	get_tree().node_added.connect(_sur_noeud_ajoute)
	# SceneRouter est chargé après nous : on s'y abonne une fois tous les autoloads posés.
	_brancher_scene_router.call_deferred()
	# Bruitages déclenchés par l'état du jeu (sceau, marques, lanterne, jauges).
	var bruitages := BruitagesJeu.new()
	bruitages.name = "BruitagesJeu"
	add_child(bruitages)
	set_process(false)


func _process(_delta: float) -> void:
	if not is_instance_valid(_suivi_joueur):
		arreter_suivi_voix()
		return
	var gain := MixageSon.gain_voix(_suivi_joueur.global_position.x, _points_voix)
	if not is_equal_approx(gain, _gain_voix):
		_gain_voix = gain
		_maj_volumes()


## Appelé par l'écran titre au premier clic ou à la première touche.
func deverrouiller() -> void:
	audio_deverrouille = true


## Appelé par SceneRouter au changement d'étape.
func jouer_etape(numero: int) -> void:
	for lecteur: AudioStreamPlayer in _couches.values():
		lecteur.queue_free()
	_couches.clear()
	arreter_suivi_voix()
	if _fondu_musique and _fondu_musique.is_valid():
		_fondu_musique.kill()
	_musique.stop()
	# Chaque étape commence de jour ; etape_prete donne ensuite son état réel.
	definir_nuit(false, 0.0)
	var slug: String = SLUGS_ETAPES.get(numero, "")
	if slug.is_empty():
		return
	for couche: String in COUCHES_AMBIANCE.get(numero, []):
		var lecteur := _creer_lecteur(BUS_AMBIANCE)
		_couches[couche] = lecteur
		_jouer_boucle(lecteur, "res://assets/audio/amb_%s_%s.ogg" % [slug, couche])
	# Une nouvelle étape démarre directement au bon mélange, sans fondu.
	_appliquer_mixage(true)


## Musique d'un moment de l'étape courante (mus_<slug>_<moment>.ogg).
## La musique est rare : elle monte en fondu à un moment précis (déclenché par un dialogue,
## `do AudioDirector.jouer_musique(1, "theme")`) et se retire avec arreter_musique().
## Rejouer le même morceau alors qu'il tourne ne le relance pas.
func jouer_musique(numero: int, moment: String, fondu: float = DUREE_FONDU_MUSIQUE) -> void:
	var slug: String = SLUGS_ETAPES.get(numero, "")
	var chemin := "res://assets/audio/mus_%s_%s.ogg" % [slug, moment]
	if _musique.playing and _musique.stream and _musique.stream.resource_path == chemin:
		_fondu_musique_vers(0.0, fondu)
		return
	_musique.volume_db = MixageSon.GAIN_MUET_DB
	_jouer_boucle(_musique, chemin)
	if _musique.playing:
		_fondu_musique_vers(0.0, fondu)


## Épilogue de l'étape 7 (mus_destinataire_<moment>.ogg, moment = fin-a à fin-e ; la table
## lettre → fin est dans tools/son/README.md, jamais dans un nom de fichier).
## Joué une seule fois, sans boucle, depuis son début ; les couches d'ambiance se retirent
## en `fondu` secondes pour laisser le Cantique seul sous le carton.
func jouer_epilogue(moment: String, fondu: float = DUREE_FONDU_MUSIQUE) -> void:
	var chemin := "res://assets/audio/mus_%s_%s.ogg" % [SLUGS_ETAPES[7], moment]
	if not audio_deverrouille or not ResourceLoader.exists(chemin):
		return
	if _fondu_musique and _fondu_musique.is_valid():
		_fondu_musique.kill()
	var flux := (load(chemin) as AudioStream).duplicate()
	if flux is AudioStreamOggVorbis:
		(flux as AudioStreamOggVorbis).loop = false
	_musique.stream = flux
	_musique.volume_db = 0.0
	_musique.play()
	_retirer_couches(fondu)


## Éteint les couches d'ambiance de l'étape en fondu puis les libère.
func _retirer_couches(fondu: float) -> void:
	if _fondu and _fondu.is_valid():
		_fondu.kill()
	for couche: String in _couches:
		var lecteur: AudioStreamPlayer = _couches[couche]
		if fondu <= 0.0:
			lecteur.queue_free()
			continue
		var t := create_tween().set_trans(Tween.TRANS_SINE)
		t.tween_property(lecteur, "volume_db", MixageSon.GAIN_MUET_DB, fondu)
		t.tween_callback(lecteur.queue_free)
	_couches.clear()


## Retire la musique en fondu puis l'arrête (silence d'exploration).
func arreter_musique(fondu: float = DUREE_FONDU_MUSIQUE) -> void:
	if not _musique.playing:
		return
	_fondu_musique_vers(MixageSon.GAIN_MUET_DB, fondu, true)


func _fondu_musique_vers(volume_db: float, duree: float, arreter_apres: bool = false) -> void:
	if _fondu_musique and _fondu_musique.is_valid():
		_fondu_musique.kill()
	if duree <= 0.0:
		_musique.volume_db = volume_db
		if arreter_apres:
			_musique.stop()
		return
	_fondu_musique = create_tween().set_trans(Tween.TRANS_SINE)
	_fondu_musique.tween_property(_musique, "volume_db", volume_db, duree)
	if arreter_apres:
		_fondu_musique.tween_callback(_musique.stop)


## Timbre de dialogue d'un personnage (pas de doublage) : une variante au hasard parmi
## vox_<personnage>_01 à _03, sur le bus Voix. `personnage` est le slug du fichier
## (tobie, lamarre, cassien, jacquot, ravaude, guetteur, voix-sous-terre).
func jouer_timbre(personnage: String) -> void:
	jouer_variante("vox_%s" % personnage, BUS_VOIX)


## Bruitage à variantes : tire au hasard un fichier existant parmi <base>_01 à _NN
## (ex. jouer_variante("sfx_pas_boue") pour un pas). Évite de rejouer deux fois de suite
## la même variante quand il y en a plusieurs.
func jouer_variante(base: String, bus: StringName = BUS_SFX) -> void:
	var variantes := variantes_de(base)
	if variantes.is_empty():
		return
	var choix := variantes[_rng.randi_range(0, variantes.size() - 1)]
	if variantes.size() > 1 and choix == _derniere_variante.get(base, ""):
		choix = variantes[(variantes.find(choix) + 1) % variantes.size()]
	_derniere_variante[base] = choix
	jouer_sfx(choix, bus)


## Noms des variantes existantes de <base> (_01, _02… jusqu'au premier trou), mis en cache.
func variantes_de(base: String) -> Array[String]:
	if _cache_variantes.has(base):
		return _cache_variantes[base]
	var noms: Array[String] = []
	for n in range(1, 100):
		var nom := "%s_%02d" % [base, n]
		if not ResourceLoader.exists("res://assets/audio/%s.ogg" % nom):
			break
		noms.append(nom)
	_cache_variantes[base] = noms
	return noms


func jouer_sfx(nom: String, bus: StringName = BUS_SFX) -> void:
	if not audio_deverrouille:
		return
	var chemin := "res://assets/audio/%s.ogg" % nom
	if not ResourceLoader.exists(chemin):
		return
	var lecteur := _creer_lecteur(bus)
	lecteur.set_meta(&"sfx", nom)
	lecteur.stream = load(chemin)
	lecteur.finished.connect(lecteur.queue_free)
	lecteur.play()


## Coupe net les bruitages en cours dont le nom commence par `base`
## (ex. arreter_sfx("sfx_ui_maintien") quand l'appui est relâché avant 1,2 s).
func arreter_sfx(base: String) -> void:
	for enfant in get_children():
		if enfant is AudioStreamPlayer and String(enfant.get_meta(&"sfx", "")).begins_with(base):
			(enfant as AudioStreamPlayer).stop()
			enfant.queue_free()


## Recalcule le mélange depuis l'état de GameState (la valeur seule ne suffit pas :
## le palier et l'état Perdu décident). Gardé pour les appels manuels (menu debug).
func set_lucidite(_valeur: int) -> void:
	_appliquer_mixage()


## Le gain des voix de surface suit l'abscisse de `joueur`, interpolé entre les repères
## nommés boyau_arriere, carrefour, periscope, pied_echelle (Marker2D du Level Designer).
func definir_suivi_voix(joueur: Node2D, reperes: Array[Marker2D]) -> void:
	var positions := {}
	for repere in reperes:
		positions[StringName(repere.name)] = repere.global_position.x
	_points_voix = MixageSon.points_depuis_reperes(positions)
	_suivi_joueur = joueur
	set_process(joueur != null and not _points_voix.is_empty())


## Sous terre ou hors de la surface : les voix reviennent à leur gain plein.
func arreter_suivi_voix() -> void:
	_suivi_joueur = null
	_points_voix.clear()
	set_process(false)
	if not is_equal_approx(_gain_voix, 1.0):
		_gain_voix = 1.0
		_maj_volumes()


func _sur_palier_change(_ancien: StringName, _nouveau: StringName) -> void:
	_appliquer_mixage()


func _sur_etat_declenche(etat: StringName) -> void:
	if etat == &"perdu":
		_appliquer_mixage()


func _sur_etat_charge() -> void:
	_dans_le_noir = false
	_appliquer_mixage(true)
	_maj_sons_du_noir(0.0)


func _sur_zone_sombre_changee(dans_zone: bool, lanterne: bool) -> void:
	_dans_le_noir = dans_zone and not lanterne
	_appliquer_mixage()
	_maj_sons_du_noir(DUREE_FONDU_NOIR)


## Un émetteur du noir qui entre dans l'arbre prend tout de suite le bon volume.
func _sur_noeud_ajoute(noeud: Node) -> void:
	if noeud.is_in_group(GROUPE_SON_DU_NOIR):
		_regler_son_du_noir(noeud, 0.0)


func _maj_sons_du_noir(duree: float) -> void:
	for noeud in get_tree().get_nodes_in_group(GROUPE_SON_DU_NOIR):
		_regler_son_du_noir(noeud, duree)


func _regler_son_du_noir(noeud: Node, duree: float) -> void:
	if not (noeud is AudioStreamPlayer or noeud is AudioStreamPlayer2D):
		return
	# Volume « plein » réglé par le Level Designer dans la scène, mémorisé au premier passage.
	if not noeud.has_meta(&"volume_db_plein"):
		noeud.set_meta(&"volume_db_plein", noeud.get(&"volume_db"))
	var cible: float = noeud.get_meta(&"volume_db_plein") if _dans_le_noir else MixageSon.GAIN_MUET_DB
	# Un seul fondu à la fois par émetteur : entrer et sortir du noir en moins de
	# DUREE_FONDU_NOIR ne doit pas laisser deux tweens se disputer volume_db.
	if noeud.has_meta(&"fondu_noir"):
		var precedent: Tween = noeud.get_meta(&"fondu_noir")
		if precedent and precedent.is_valid():
			precedent.kill()
	if duree <= 0.0:
		noeud.set(&"volume_db", cible)
		return
	var fondu := create_tween().set_trans(Tween.TRANS_SINE)
	fondu.tween_property(noeud, "volume_db", cible, duree)
	noeud.set_meta(&"fondu_noir", fondu)


## Jour / nuit (étapes à lieux_nuit) : l'étape prévient par son signal phase_changee.
func _brancher_scene_router() -> void:
	var routeur := get_node_or_null(^"/root/SceneRouter")
	if routeur and not routeur.etape_prete.is_connected(_sur_etape_prete):
		routeur.etape_prete.connect(_sur_etape_prete)


func _sur_etape_prete(etape: Node) -> void:
	if etape.has_signal(&"phase_changee") and not etape.is_connected(&"phase_changee", definir_nuit):
		etape.connect(&"phase_changee", definir_nuit)
	definir_nuit(etape.get(&"nuit") == true, 0.0)


## Fondu croisé entre les couches « jour » et « nuit » de l'étape (duree 0 : immédiat).
## Sans ces couches (étapes 1 et 2), ne change rien.
func definir_nuit(nuit: bool, duree: float = MixageSon.DUREE_FONDU_PHASE) -> void:
	if _fondu_phase and _fondu_phase.is_valid():
		_fondu_phase.kill()
	var cible := 1.0 if nuit else 0.0
	if duree <= 0.0:
		_regler_mix_nuit(cible)
		return
	_fondu_phase = create_tween().set_trans(Tween.TRANS_SINE)
	_fondu_phase.tween_method(_regler_mix_nuit, _mix_nuit, cible, duree)


func _regler_mix_nuit(valeur: float) -> void:
	_mix_nuit = valeur
	_maj_volumes()


## Lance le fondu vers le mélange cible (ou l'applique d'un coup si `instantane`).
func _appliquer_mixage(instantane: bool = false) -> void:
	var cible := MixageSon.cible(GameState.palier, GameState.est_perdu(), _dans_le_noir)
	if _fondu and _fondu.is_valid():
		_fondu.kill()
	if instantane:
		_mix_reel = cible["reel"]
		_mix_autre = cible["autre"]
		if _passe_bas:
			_passe_bas.cutoff_hz = cible["coupure_hz"]
		_maj_volumes()
		return
	_fondu = create_tween().set_parallel(true).set_trans(Tween.TRANS_SINE)
	_fondu.tween_method(_regler_mix_reel, _mix_reel, float(cible["reel"]), MixageSon.DUREE_FONDU)
	_fondu.tween_method(_regler_mix_autre, _mix_autre, float(cible["autre"]), MixageSon.DUREE_FONDU)
	if _passe_bas:
		_fondu.tween_property(_passe_bas, "cutoff_hz", float(cible["coupure_hz"]), MixageSon.DUREE_FONDU)


func _regler_mix_reel(valeur: float) -> void:
	_mix_reel = valeur
	_maj_volumes()


func _regler_mix_autre(valeur: float) -> void:
	_mix_autre = valeur
	_maj_volumes()


func _maj_volumes() -> void:
	for couche: String in _couches:
		var gain := _mix_autre if couche in COUCHES_AUTRE else _mix_reel
		if couche in COUCHES_VOIX:
			gain *= _gain_voix
		gain *= MixageSon.gain_phase(couche, _mix_nuit)
		(_couches[couche] as AudioStreamPlayer).volume_db = MixageSon.vers_db(gain)


func _installer_passe_bas() -> AudioEffectLowPassFilter:
	var bus := AudioServer.get_bus_index(BUS_AMBIANCE)
	if bus == -1:
		return null
	for i in AudioServer.get_bus_effect_count(bus):
		var effet := AudioServer.get_bus_effect(bus, i)
		if effet is AudioEffectLowPassFilter:
			return effet
	var filtre := AudioEffectLowPassFilter.new()
	filtre.cutoff_hz = MixageSon.COUPURE_PAR_PALIER[&"clair"]
	AudioServer.add_bus_effect(bus, filtre, 0)
	return filtre


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
