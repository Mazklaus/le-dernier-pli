class_name EtapeBase
extends Node2D
## Base des scènes d'étape. Fournit le saut de débogage attendu par SceneRouter :
## aller_rencontre(id) pose le messager devant le DeclencheurDialogue de cette rencontre.
## Ajoute aussi l'interface en jeu (InterfaceJeu) si l'étape n'en a pas.
## Voix de surface : si l'étape a un nœud « ReperesVoix » (Marker2D boyau_arriere, carrefour,
## periscope, pied_echelle), le gain des voix suit le messager tant qu'il est à la surface
## (y ≤ limite_surface_y), et revient plein sous terre. Mis à jour à chaque téléportation.
## Écran gravure : un CanvasLayer (COUCHE_GRAVURE) porte le shader plein écran
## shaders/ecran_gravure.gdshader (trait tremblé, papier de l'étape, grain, rouge préservé).
## Tout ce qui doit échapper à l'effet (interface, bulles) va sur un calque supérieur.
## Une étape qui redéfinit _ready() doit appeler super().

const NOEUD_REPERES_VOIX := "ReperesVoix"
const NOEUD_GRAVURE := "EcranGravure"
const COUCHE_GRAVURE := 10
const SHADER_GRAVURE: Shader = preload("res://shaders/ecran_gravure.gdshader")
## Amplitude du trait tremblé au repos (px à 1080p) ; 0 avec le réglage effets_attenues.
const AMPLITUDE_REPOS := 1.5

## Ordonnée (globale) sous laquelle le messager est sous terre (lieux souterrains).
@export var limite_surface_y: float = INF
## Numéro de l'étape (musiques AudioDirector.jouer_musique).
@export var numero_etape: int = 0
## Musique par lieu : franchir un Passage vers un de ces lieux lance la musique du moment
## associé (fondu entrant) ; vers tout autre lieu, elle s'arrête (fondu sortant).
## Ex. étape 1 : {&"abri_sergent": "theme", &"chapelle": "theme"}.
@export var lieux_musique: Dictionary = {}
## Lieux de nuit : franchir un Passage vers l'un d'eux bascule l'étape en nuit (CanvasModulate
## « Eclairage » teinté teinte_nuit, signal phase_changee) ; vers tout autre lieu, retour au
## jour. Ex. étape 3 : [&"chambre", &"chemin_nuit"]. Le basculement a lieu dans le noir si le
## Passage a un fondu_noir.
@export var lieux_nuit: Array[StringName] = []
@export var teinte_nuit: Color = Color(0.32, 0.35, 0.48)
## Bornes horizontales de la caméra à la surface (le décor parallaxe est calculé pour elles) ;
## levées sous terre. x > y : pas de borne.
@export var bornes_camera_surface: Vector2 = Vector2(1, 0)
## Pas du messager à la surface et sous terre (variantes du Sound Designer).
@export var pas_surface: String = "sfx_pas_boue"
@export var pas_sous_terre: String = "sfx_pas_terre"


signal phase_changee(nuit: bool)

var nuit: bool = false


func _ready() -> void:
	ajouter_gravure()
	ajouter_interface()
	brancher_suivi_voix()
	brancher_musique_lieux()
	brancher_bornes_camera()
	SceneRouter.etape_prete.emit(self)


## Borne la caméra à la surface (bornes_camera_surface), la libère sous terre, et choisit le
## son des pas, à chaque téléportation du messager.
func brancher_bornes_camera() -> void:
	var messager := trouver_messager()
	if messager == null:
		return
	if not messager.teleporte.is_connected(_sur_teleporte_bornes):
		messager.teleporte.connect(_sur_teleporte_bornes)
	maj_bornes_camera.call_deferred()


func maj_bornes_camera() -> void:
	var messager := trouver_messager()
	if messager == null:
		return
	# Le sol sous les pas suit aussi le niveau (surface ou sous terre).
	messager.son_pas = pas_surface if est_en_surface(messager.global_position) else pas_sous_terre
	if bornes_camera_surface.x > bornes_camera_surface.y:
		return
	if est_en_surface(messager.global_position):
		messager.borner_camera(int(bornes_camera_surface.x), int(bornes_camera_surface.y))
	else:
		messager.liberer_camera()


func _sur_teleporte_bornes(_position_globale: Vector2) -> void:
	maj_bornes_camera()


## Relie les Passages de l'étape (tous les Interactif de type Passage) au son de passage, et
## à la musique et à la nuit par lieu (lieux_musique, lieux_nuit).
func brancher_musique_lieux() -> void:
	for n in get_tree().get_nodes_in_group(Interactif.GROUPE):
		if n is Passage and is_ancestor_of(n):
			var passage := n as Passage
			if not passage.franchi.is_connected(_sur_passage_franchi):
				passage.franchi.connect(_sur_passage_franchi)


## Son d'un passage : l'escalier quand on change de niveau (surface ↔ sous terre), la toile
## sinon (bâche, porte de lieu).
func son_passage(depart: Vector2, arrivee: Vector2) -> String:
	return "sfx_passage_escalier" if est_en_surface(depart) != est_en_surface(arrivee) \
		else "sfx_passage_toile"


func _sur_passage_franchi(passage: Passage, vers: StringName) -> void:
	var messager := trouver_messager()
	if messager != null and passage != null:
		AudioDirector.jouer_variante(son_passage(passage.global_position, messager.global_position))
	entrer_lieu(vers)


## Applique la musique et la nuit d'un lieu (&"" : la surface), qu'on y entre par un Passage,
## un saut de débogage ou, plus tard, un chargement.
func entrer_lieu(lieu: StringName) -> void:
	if not lieux_musique.is_empty():
		if lieux_musique.has(lieu):
			AudioDirector.jouer_musique(numero_etape, String(lieux_musique[lieu]))
		else:
			AudioDirector.arreter_musique()
	if not lieux_nuit.is_empty():
		definir_nuit(lieu in lieux_nuit)


## Lieu (sous-scène de « Lieux ») qui contient ce nœud, nommé comme son marqueur d'entrée
## (entree_<lieu>) ; &"" pour la surface.
func lieu_de(noeud: Node) -> StringName:
	var lieux := get_node_or_null("Lieux")
	if lieux == null or noeud == null or not lieux.is_ancestor_of(noeud):
		return &""
	for lieu in lieux.get_children():
		if lieu == noeud or lieu.is_ancestor_of(noeud):
			for marqueur in lieu.find_children("entree_*", "Marker2D", true, false):
				return StringName(String(marqueur.name).trim_prefix("entree_"))
	return &""


## Bascule jour / nuit : teinte de la scène (pas de l'interface) et signal pour les ambiances.
func definir_nuit(actif: bool) -> void:
	var eclairage := get_node_or_null("Eclairage") as CanvasModulate
	if eclairage == null:
		eclairage = CanvasModulate.new()
		eclairage.name = "Eclairage"
		add_child(eclairage)
	eclairage.color = teinte_nuit if actif else Color.WHITE
	if actif != nuit:
		nuit = actif
		phase_changee.emit(nuit)


## Relie le gain des voix de surface (AudioDirector) à la position du messager.
func brancher_suivi_voix() -> void:
	var messager := trouver_messager()
	if messager == null or reperes_voix().is_empty():
		return
	if not messager.teleporte.is_connected(_sur_teleporte):
		messager.teleporte.connect(_sur_teleporte)
	# Différé : l'étape place encore le messager au départ après super()._ready().
	maj_suivi_voix.call_deferred()


func reperes_voix() -> Array[Marker2D]:
	var reperes: Array[Marker2D] = []
	var noeud := get_node_or_null(NOEUD_REPERES_VOIX)
	if noeud != null:
		for enfant in noeud.get_children():
			if enfant is Marker2D:
				reperes.append(enfant as Marker2D)
	return reperes


func est_en_surface(position_globale: Vector2) -> bool:
	return position_globale.y <= limite_surface_y


func maj_suivi_voix() -> void:
	var messager := trouver_messager()
	if messager == null:
		return
	if est_en_surface(messager.global_position):
		AudioDirector.definir_suivi_voix(messager, reperes_voix())
	else:
		AudioDirector.arreter_suivi_voix()


func _sur_teleporte(_position_globale: Vector2) -> void:
	maj_suivi_voix()


## Pose l'écran gravure (une seule fois) et lui applique le papier de l'étape.
func ajouter_gravure() -> ShaderMaterial:
	var existant := materiau_gravure()
	if existant != null:
		return existant
	var couche := CanvasLayer.new()
	couche.name = NOEUD_GRAVURE
	couche.layer = COUCHE_GRAVURE
	var rect := ColorRect.new()
	rect.name = "Rect"
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	var materiau := ShaderMaterial.new()
	materiau.shader = SHADER_GRAVURE
	rect.material = materiau
	couche.add_child(rect)
	add_child(couche)
	PapierEtapes.appliquer(materiau, numero_etape)
	_appliquer_effets_attenues()
	# La Lucidité pilote le tremblé et le rouge (LuciditeEcran).
	var lucidite := LuciditeEcran.new()
	lucidite.name = "LuciditeEcran"
	lucidite.materiau = materiau
	couche.add_child(lucidite)
	if not Reglages.reglage_change.is_connected(_sur_reglage_change):
		Reglages.reglage_change.connect(_sur_reglage_change)
	return materiau


## Matériau de l'écran gravure, pour piloter amplitude_px ou rouge_efface (Lucidité).
## null si l'écran n'est pas encore posé.
func materiau_gravure() -> ShaderMaterial:
	var rect := get_node_or_null(NOEUD_GRAVURE + "/Rect") as ColorRect
	return rect.material as ShaderMaterial if rect != null else null


func _appliquer_effets_attenues() -> void:
	var materiau := materiau_gravure()
	if materiau == null:
		return
	var attenues := bool(Reglages.valeur(&"effets_attenues"))
	materiau.set_shader_parameter(&"amplitude_px", 0.0 if attenues else AMPLITUDE_REPOS)


func _sur_reglage_change(cle: StringName, _valeur: Variant) -> void:
	if cle == &"effets_attenues":
		_appliquer_effets_attenues()


## Instancie InterfaceJeu et la branche sur le messager, sauf si l'étape en a déjà une.
func ajouter_interface() -> InterfaceJeu:
	for enfant in get_children():
		if enfant is InterfaceJeu:
			return enfant as InterfaceJeu
	var messager := trouver_messager()
	if messager == null:
		return null
	var interface: InterfaceJeu = (load(InterfaceJeu.SCENE) as PackedScene).instantiate()
	add_child(interface)
	interface.brancher(messager)
	return interface


func aller_rencontre(id: StringName) -> void:
	var messager := trouver_messager()
	var declencheur := trouver_declencheur(id)
	if messager == null or declencheur == null:
		push_warning("%s : rencontre %s introuvable (messager ou déclencheur absent)" % [name, id])
		return
	messager.placer_devant(declencheur)
	# Même teinte et même musique qu'en arrivant par le Passage (nuit de la chambre…).
	entrer_lieu(lieu_de(declencheur))


func trouver_messager() -> Messager:
	for n in get_tree().get_nodes_in_group(Messager.GROUPE):
		if n is Messager and is_ancestor_of(n):
			return n as Messager
	return null


func trouver_declencheur(id: StringName) -> DeclencheurDialogue:
	for n in get_tree().get_nodes_in_group(Interactif.GROUPE):
		if n is DeclencheurDialogue and is_ancestor_of(n) and (n as DeclencheurDialogue).rencontre_id == id:
			return n as DeclencheurDialogue
	return null
