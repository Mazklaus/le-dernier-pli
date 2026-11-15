class_name Epilogue
extends Control
## Carton d'épilogue, après la Mère-Cloche : la gravure fixe du DA (cin_epilogue-<lettre>),
## le Cantique sans boucle (AudioDirector.jouer_epilogue) et, sur le papier laissé en bas de
## la gravure, les lignes du titre epilogue_<clé> de e7_epilogues.dialogue, une à une. Puis
## les Noms retenus et les Promesses encore ouvertes, enfin l'invite de retour au titre.
## Interagir (ou clic) : tout afficher d'un coup ; une fois tout affiché, retour au titre.

enum Etat { LIGNES, MEMOIRE, FINI }

## Zone de papier sous le cadre de la gravure (1920×1080 : le cadre s'arrête vers y 785 ; marge du bas égale à l'écart sous le filet, DA).
const ZONE_TEXTE := Rect2(200.0, 800.0, 1520.0, 240.0)
const FONDU := 1.2
## Temps de lecture d'une ligne : un socle, plus un temps par caractère.
const LECTURE_SOCLE := 2.0
const LECTURE_PAR_CARACTERE := 0.05
const PAUSE_AVANT_MEMOIRE := 3.0
const TAILLE_TEXTE := 30
const TAILLE_MEMOIRE := 26

var cle: String
var lignes: PackedStringArray = []
var etat: Etat = Etat.LIGNES
var gravure: TextureRect
var colonne_lignes: VBoxContainer
var colonne_memoire: VBoxContainer
var invite: Label

var _sequence: Tween


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	var fond := ColorRect.new()
	fond.color = StylePapier.PAPIER
	fond.set_anchors_preset(Control.PRESET_FULL_RECT)
	fond.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(fond)
	cle = EpilogueFin.cle(GameState.fin(), GameState.rencontre_vue(EpilogueFin.DRAPEAU_CLOCHES))
	gravure = TextureRect.new()
	gravure.name = "Gravure"
	gravure.set_anchors_preset(Control.PRESET_FULL_RECT)
	gravure.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	gravure.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	gravure.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var chemin := EpilogueFin.gravure(cle)
	if ResourceLoader.exists(chemin):
		gravure.texture = load(chemin) as Texture2D
	add_child(gravure)
	colonne_lignes = _colonne("Lignes")
	colonne_memoire = _colonne("Memoire")
	colonne_memoire.modulate.a = 0.0
	invite = _ligne("Interagir : revenir au titre", TAILLE_MEMOIRE - 4, StylePapier.MINE)
	invite.name = "Invite"
	invite.position = Vector2(ZONE_TEXTE.position.x, ZONE_TEXTE.end.y - 32.0)
	invite.size.x = ZONE_TEXTE.size.x
	invite.modulate.a = 0.0
	add_child(invite)
	AudioDirector.jouer_epilogue(EpilogueFin.moment(cle))
	lignes = await lire_lignes(EpilogueFin.DIALOGUE, EpilogueFin.titre(cle))
	_remplir_memoire()
	_derouler()


## Lignes de texte d'un titre de dialogue (sans exécuter de choix : un carton n'en a pas).
static func lire_lignes(chemin: String, titre: String) -> PackedStringArray:
	var resultat := PackedStringArray()
	if not ResourceLoader.exists(chemin):
		return resultat
	var ressource := load(chemin) as DialogueResource
	var ligne: DialogueLine = await DialogueManager.get_next_dialogue_line(ressource, titre)
	while ligne != null and resultat.size() < 32:
		if not ligne.text.strip_edges().is_empty():
			resultat.append(ligne.text.strip_edges())
		if ligne.next_id.is_empty() or StringName(ligne.next_id) in [DMConstants.ID_END, DMConstants.ID_END_CONVERSATION]:
			break
		ligne = await DialogueManager.get_next_dialogue_line(ressource, ligne.next_id)
	return resultat


static func duree_lecture(ligne: String) -> float:
	return LECTURE_SOCLE + LECTURE_PAR_CARACTERE * ligne.length()


func _colonne(nom: String) -> VBoxContainer:
	var colonne := VBoxContainer.new()
	colonne.name = nom
	colonne.position = ZONE_TEXTE.position
	colonne.size = ZONE_TEXTE.size
	colonne.alignment = BoxContainer.ALIGNMENT_BEGIN
	colonne.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(colonne)
	return colonne


func _ligne(texte: String, taille: int, couleur: Color = StylePapier.ENCRE, italique: bool = false) -> Label:
	var label := Label.new()
	label.text = texte
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_color_override(&"font_color", couleur)
	label.add_theme_font_size_override(&"font_size", taille)
	var police := StylePapier.police(StylePapier.POLICE_ITALIQUE if italique else StylePapier.POLICE_TEXTE)
	if police != null:
		label.add_theme_font_override(&"font", police)
	return label


func _remplir_memoire() -> void:
	var noms := EpilogueFin.noms_retenus(GameState.marques)
	var promesses := EpilogueFin.promesses_ouvertes(GameState.marques)
	if not noms.is_empty():
		colonne_memoire.add_child(_ligne("Les noms qu'il a portés", TAILLE_MEMOIRE - 4, StylePapier.LAVIS, true))
		colonne_memoire.add_child(_ligne(" · ".join(noms), TAILLE_MEMOIRE))
	if not promesses.is_empty():
		colonne_memoire.add_child(_ligne("Ce qu'il avait promis", TAILLE_MEMOIRE - 4, StylePapier.LAVIS, true))
		colonne_memoire.add_child(_ligne(" · ".join(promesses), TAILLE_MEMOIRE))


## Les lignes paraissent une à une, puis cèdent la place à la mémoire, puis l'invite.
func _derouler() -> void:
	_sequence = create_tween()
	for texte in lignes:
		var label := _ligne(texte, TAILLE_TEXTE)
		label.modulate.a = 0.0
		colonne_lignes.add_child(label)
		_sequence.tween_property(label, "modulate:a", 1.0, FONDU)
		_sequence.tween_interval(duree_lecture(texte))
	_sequence.tween_interval(PAUSE_AVANT_MEMOIRE)
	_sequence.tween_callback(func() -> void: etat = Etat.MEMOIRE)
	if colonne_memoire.get_child_count() > 0:
		_sequence.tween_property(colonne_lignes, "modulate:a", 0.0, FONDU)
		_sequence.tween_property(colonne_memoire, "modulate:a", 1.0, FONDU)
	_sequence.tween_property(invite, "modulate:a", 1.0, FONDU)
	_sequence.tween_callback(func() -> void: etat = Etat.FINI)


## Tout afficher d'un coup (lignes déjà lues : on passe à la mémoire).
func passer() -> void:
	if _sequence != null and _sequence.is_valid():
		_sequence.kill()
	for label in colonne_lignes.get_children():
		(label as CanvasItem).modulate.a = 1.0
	var memoire := colonne_memoire.get_child_count() > 0
	colonne_lignes.modulate.a = 0.0 if memoire else 1.0
	colonne_memoire.modulate.a = 1.0
	invite.modulate.a = 1.0
	etat = Etat.FINI


func _unhandled_input(event: InputEvent) -> void:
	if not (event.is_action_pressed(&"interagir") or event.is_action_pressed(&"clic") \
			or event.is_action_pressed(&"ui_accept")):
		return
	get_viewport().set_input_as_handled()
	if etat == Etat.FINI:
		SceneRouter.retour_titre()
	else:
		passer()
