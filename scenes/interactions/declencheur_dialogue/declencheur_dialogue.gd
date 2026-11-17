class_name DeclencheurDialogue
extends Interactif
## Point d'interaction : lance un dialogue quand le messager appuie sur « interagir ».
## Tout se règle dans l'inspecteur, sans code par rencontre :
## - un verrou (`rencontre_requise`) joue un autre titre tant qu'une rencontre n'a pas été vue
##   (ex. Jacquot : `refus_sans_cendre` tant que `e1_cendre` n'est pas vue, puis `debut`) ;
## - `fin_etape` appelle SceneRouter.etape_suivante() à la fin du dialogue (ex. le parapet).

signal dialogue_commence(declencheur: DeclencheurDialogue)
signal dialogue_termine(declencheur: DeclencheurDialogue)
## Une réplique de la rencontre demande un geste ([#geste=…]) : les objets animés du lieu
## (ex. la couverture anti-gaz) peuvent l'écouter, en plus des personnages dessinés.
signal geste_demande(cible: StringName, geste: StringName)

## Identifiant de rencontre du plan (ex. &"e1_adieu").
@export var rencontre_id: StringName
@export var dialogue: DialogueResource
@export var titre: String = "debut"

@export_group("Verrou")
## Tant que cette rencontre n'est pas vue, on joue `titre_si_verrouille`.
@export var rencontre_requise: StringName
@export var titre_si_verrouille: String = ""

@export_group("Comportement")
## Le déclencheur s'éteint une fois sa rencontre jouée (titre principal).
@export var une_seule_fois: bool = false
## À la fin du dialogue principal, passe à l'étape suivante.
@export var fin_etape: bool = false
## Détail à examiner : repère gravé (astérisque) tant qu'il n'est pas examiné. Activé
## d'office pour les détails à examiner (rencontre_id contenant « _detail_ »).
@export var est_detail: bool = false

@export_group("Sons")
## Bruitage du geste au début de la rencontre (ex. sfx_periscope_regarder pour le Guetteur).
@export var son_debut: String = ""
## Bruitage du geste à la fin, si la rencontre a été jouée (ex. sfx_echelle_monter : Tobie
## monte au parapet).
@export var son_fin: String = ""

@export_group("Apparence")
## Personnage dessiné de la rencontre (planche chr_<nom>_repos_01 de la DA), posé aux pieds du
## déclencheur ; masque le rectangle « Visuel » de la maquette. Vide : pas de personnage.
@export var personnage: StringName
## Autres personnages de la rencontre, avec leur décalage depuis le déclencheur
## (ex. la noce : {&"rose": Vector2(-200, 0), &"violoneux": Vector2(200, 0)}).
@export var compagnons: Dictionary = {}
## Cortège : nombre de silhouettes de `personnage` alignées vers la gauche tous les
## `ecart_cortege` px, déphasées d'une image (la procession de l'étape 3). 0 ou 1 : seul.
@export var cortege: int = 0
@export var ecart_cortege: float = 140.0
## Personnages qui n'entrent qu'en cours de rencontre, avec leur décalage depuis le déclencheur
## (ex. Ilde à la porte de la chambre, à l'aube : {&"ilde": Vector2(450, 0)}). Cachés au départ,
## chacun apparaît en fondu à la réplique balisée [#entree=<nom>], puis reste là.
@export var entrees: Dictionary = {}
## Tant que la rencontre n'est pas vue, le personnage montre la première image de ce geste au
## lieu de respirer (ex. le mort, bras pendant, avant « Son bras se lève »). Vide : repos.
@export var pose_initiale: StringName
## Distance (une main) à laquelle Tobie se place pour ses gestes ([#geste=tobie:…]), tourné
## vers le déclencheur : le couteau ou la cloche touchent la croix.
@export var ecart_geste_tobie: float = 60.0

const TAG_ENTREE := "entree"
## [#sortie=<nom>] : le personnage s'efface (Anselme reste derrière la porte qui se referme).
const TAG_SORTIE := "sortie"
## Cible [#geste=tous:<geste>] : tous les personnages dessinés de la rencontre, en désordre.
const TOUS := &"tous"
## Décalage entre deux personnages pour un geste de tous (« un cliquetis, pas un ballet »).
const DECALAGE_TOUS := 0.15
const DUREE_ENTREE := 0.5

var en_cours: bool = false
var repere: RepereExamen = null
var dessin: Personnage = null


func _ready() -> void:
	super()
	if est_detail or String(rencontre_id).contains("_detail_"):
		repere = RepereExamen.new()
		repere.rencontre_id = rencontre_id
		add_child(repere)
	_poser_personnages()


## Pose le personnage, son cortège et ses compagnons ; masque le rectangle de la maquette.
func _poser_personnages() -> void:
	dessin = Personnage.creer(personnage)
	if dessin != null:
		add_child(dessin)
		for i in range(1, cortege):
			var suivant := Personnage.creer(personnage)
			suivant.name = "Cortege%d" % i
			suivant.position = Vector2(-ecart_cortege * i, 0.0)
			suivant.dephasage = i
			add_child(suivant)
	if dessin != null and pose_initiale != &"" and not GameState.rencontre_vue(rencontre_id):
		dessin.poser_debut_geste(pose_initiale)
	for nom: StringName in compagnons:
		var compagnon := Personnage.creer(nom)
		if compagnon != null:
			compagnon.name = "Compagnon_%s" % nom
			compagnon.position = compagnons[nom]
			add_child(compagnon)
	for nom: StringName in entrees:
		var entrant := Personnage.creer(nom)
		if entrant != null:
			entrant.name = "Entree_%s" % nom
			entrant.position = entrees[nom]
			entrant.visible = false
			add_child(entrant)
	if dessin != null or not compagnons.is_empty():
		var visuel := get_node_or_null("Visuel") as CanvasItem
		if visuel != null:
			visuel.visible = false


func est_verrouille() -> bool:
	return rencontre_requise != &"" and titre_si_verrouille != "" \
		and not GameState.rencontre_vue(rencontre_requise)


func titre_a_jouer() -> String:
	return titre_si_verrouille if est_verrouille() else titre


func est_disponible() -> bool:
	if dialogue == null or en_cours:
		return false
	if une_seule_fois and not est_verrouille() and GameState.rencontre_vue(rencontre_id):
		return false
	return true


func interagir(_messager: Messager) -> void:
	if not est_disponible():
		return
	var verrouille := est_verrouille()
	en_cours = true
	dialogue_commence.emit(self)
	if son_debut != "":
		AudioDirector.jouer_variante(son_debut)
	DialogueManager.got_dialogue.connect(_sur_replique)
	DialogueManager.show_dialogue_balloon(dialogue, titre_a_jouer())
	await DialogueManager.dialogue_ended
	DialogueManager.got_dialogue.disconnect(_sur_replique)
	terminer(verrouille)


func _sur_replique(ligne: DialogueLine) -> void:
	entrer_replique(ligne.tags)
	jouer_geste_replique(ligne.character, ligne.tags)


## Fait apparaître le personnage nommé par [#entree=<nom>] (voir `entrees`). Vrai s'il entre.
func entrer_replique(tags: PackedStringArray) -> bool:
	var sortant := OptionsDialogue.valeur_tag(tags, TAG_SORTIE)
	if sortant != "":
		faire_sortir(StringName(sortant))
	var nom := OptionsDialogue.valeur_tag(tags, TAG_ENTREE)
	return nom != "" and faire_entrer(StringName(nom))


## Efface en fondu un personnage dessiné de la rencontre (principal, compagnon ou entrant).
## Faux s'il n'existe pas ou n'est déjà plus là.
func faire_sortir(nom_personnage: StringName) -> bool:
	var sortant := personnage_nomme(nom_personnage)
	if sortant == null or not sortant.visible:
		return false
	if Reglages.valeur(&"effets_attenues") or not is_inside_tree():
		sortant.visible = false
	else:
		var t := create_tween()
		t.tween_property(sortant, "modulate:a", 0.0, DUREE_ENTREE)
		t.tween_callback(sortant.hide)
	return true


## Montre un personnage de `entrees` en fondu (à l'instant si les effets sont atténués).
## Faux s'il n'existe pas ou s'il est déjà là.
func faire_entrer(nom_personnage: StringName) -> bool:
	var entrant := get_node_or_null("Entree_%s" % nom_personnage) as Personnage
	if entrant == null or entrant.visible:
		return false
	entrant.visible = true
	if not Reglages.valeur(&"effets_attenues") and is_inside_tree():
		entrant.modulate.a = 0.0
		create_tween().tween_property(entrant, "modulate:a", 1.0, DUREE_ENTREE)
	return true


## Joue le geste demandé par une réplique : sur le personnage visé, sinon (locuteur sans
## dessin propre, comme « Le sonneur ») sur le personnage principal. Un geste de Tobie est
## joué par le messager, tourné vers le déclencheur (ou vers son repère « geste_<nom> ») à
## `ecart_geste_tobie` ; il ne fait bouger personne d'autre. Vrai si un personnage a joué le geste.
func jouer_geste_replique(locuteur: String, tags: PackedStringArray) -> bool:
	var demande := OptionsDialogue.geste(locuteur, tags)
	if demande.is_empty():
		return false
	var cible: StringName = demande["cible"]
	var geste: StringName = demande["geste"]
	geste_demande.emit(cible, geste)
	if cible == &"tobie":
		var messager := get_tree().get_first_node_in_group(Messager.GROUPE) as Messager if is_inside_tree() else null
		return messager != null and messager.jouer_geste(geste, repere_geste(geste), ecart_geste_tobie)
	if cible == TOUS:
		return jouer_geste_tous(geste) > 0
	var p := personnage_nomme(cible)
	if p == null and not demande["explicite"] and cible != &"tobie":
		p = dessin
	return p != null and p.jouer_geste(geste, demande["tenir"])


## Joue un geste sur chaque personnage dessiné visible de la rencontre (principal, cortège,
## compagnons, entrants déjà là), chacun DECALAGE_TOUS plus tard que le précédent. Ceux qui
## n'ont pas la planche ne bougent pas. Renvoie le nombre de personnages qui le joueront.
func jouer_geste_tous(geste: StringName) -> int:
	var n := 0
	for enfant in get_children():
		var p := enfant as Personnage
		if p == null or not p.visible or Personnage.chemin_geste(p.nom, geste) == "":
			continue
		if n == 0 or not is_inside_tree():
			p.jouer_geste(geste)
		else:
			get_tree().create_timer(DECALAGE_TOUS * n).timeout.connect(p.jouer_geste.bind(geste))
		n += 1
	return n


## Le point que vise Tobie pour un geste : un Marker2D enfant nommé « geste_<nom> » (ex.
## geste_graver, devant une autre croix que celle du déclencheur), sinon le déclencheur.
func repere_geste(geste: StringName) -> Node2D:
	var repere := get_node_or_null(NodePath("geste_" + String(geste))) as Node2D
	return repere if repere != null else self


## Le personnage dessiné de la rencontre qui porte ce nom (principal, cortège exclu, ou
## compagnon), ou null.
func personnage_nomme(nom_personnage: StringName) -> Personnage:
	if dessin != null and dessin.nom == nom_personnage:
		return dessin
	var compagnon := get_node_or_null("Compagnon_%s" % nom_personnage) as Personnage
	return compagnon if compagnon != null else get_node_or_null("Entree_%s" % nom_personnage) as Personnage


## Fin du dialogue : la rencontre n'est comptée comme vue que si son titre principal a été joué.
func terminer(etait_verrouille: bool) -> void:
	en_cours = false
	if not etait_verrouille:
		GameState.marquer_rencontre_vue(rencontre_id)
		if son_fin != "":
			AudioDirector.jouer_variante(son_fin)
	dialogue_termine.emit(self)
	if fin_etape and not etait_verrouille:
		SceneRouter.etape_suivante()
