extends Node
## Autoload GameState : tout l'état du messager (spec jauges v0.1 du Game Designer).
## Ne connaît ni l'audio ni l'UI : il émet des signaux, les autres s'y abonnent
## (AudioDirector, HUD, carnet). Sérialisable en Dictionary pour l'autosave du jalon 2.
##
## Pas de class_name : le nom global est celui de l'autoload. Les tests instancient
## ce script directement (preload(...).new()).

signal jauge_changee(nom: StringName, ancienne: int, nouvelle: int)
signal palier_change(ancien: StringName, nouveau: StringName)
signal etat_declenche(etat: StringName)  # &"affame", &"perdu", &"lanterne_eteinte"
signal marque_gagnee(marque: Dictionary)
signal promesse_resolue(id: StringName, etat: StringName)
signal sceau_change(drapeau: StringName)  # &"abime", &"rechauffe", &"ouvert"
signal etape_changee(etape: int)
## Émis après depuis_dictionnaire() (menu debug, autosave) : les abonnés relisent tout l'état.
signal etat_charge()
## Une rencontre vient d'être jouée pour la première fois (verrous, passages).
signal rencontre_vue_marquee(id: StringName)
## Entrée/sortie de zone sombre, pour l'audio (couche « autre » +20 % dans le noir) et le rendu.
signal zone_sombre_changee(dans_zone: bool, lanterne: bool)

const VIVRES: StringName = &"vivres"
const HUILE: StringName = &"huile"
const LUCIDITE: StringName = &"lucidite"
const JAUGES: Array[StringName] = [VIVRES, HUILE, LUCIDITE]

const CLAIR: StringName = &"clair"
const TROUBLE: StringName = &"trouble"
const EGARE: StringName = &"egare"

const VIVRES_MAX := 10
const HUILE_MAX := 6
const LUCIDITE_MAX_NORMAL := 10
const LUCIDITE_MAX_PERDU := 3
const DEPART := {VIVRES: 6, HUILE: 4, LUCIDITE: 8}

## Spec v0.2 révisée, palier Égaré : tirage par rencontre (mensonge + leurre / leurre seul / rien).
const PROBA_MENSONGE := 0.5
const PROBA_LEURRE_SEUL := 0.25
const PLI_NB_LIGNES := 6

var vivres: int
var huile: int
var lucidite: int
var lucidite_max: int
var palier: StringName
var sceau_abime: bool
var sceau_rechauffe: bool
var sceau_ouvert: bool
var lanterne_allumee: bool
var marques: Array[Dictionary] = []
var etape: int
## Rencontres ayant déjà donné une marque (règle « une marque, une rencontre »).
var rencontres_marquees: Array[StringName] = []
## Dernière étape où une ligne du pli a été lue (une ligne par étape).
var etape_derniere_lecture: int
## Nombre de lignes du pli déjà lues en transparence (lues dans l'ordre, 0 à 6).
var pli_lignes_lues: int
## Rencontres déjà jouées (interactions à usage unique, verrous de progression).
var rencontres_vues: Array[StringName] = []
## Objets portés (ex. le pain promis à Jacquot, l'objet d'ombre de la sape).
var objets: Array[StringName] = []


func _init() -> void:
	reinitialiser()


func reinitialiser() -> void:
	vivres = DEPART[VIVRES]
	huile = DEPART[HUILE]
	lucidite = DEPART[LUCIDITE]
	lucidite_max = LUCIDITE_MAX_NORMAL
	palier = palier_pour(lucidite)
	sceau_abime = false
	sceau_rechauffe = false
	sceau_ouvert = false
	lanterne_allumee = false
	marques = []
	etape = 1
	rencontres_marquees = []
	etape_derniere_lecture = 0
	pli_lignes_lues = 0
	objets = []
	rencontres_vues = []


# --- Jauges --------------------------------------------------------------------

func valeur(nom: StringName) -> int:
	match nom:
		VIVRES: return vivres
		HUILE: return huile
		LUCIDITE: return lucidite
	push_error("Jauge inconnue : %s" % nom)
	return 0


func maximum(nom: StringName) -> int:
	match nom:
		VIVRES: return VIVRES_MAX
		HUILE: return HUILE_MAX
		LUCIDITE: return lucidite_max
	return 0


## LA fonction unique de modification de jauge. Borne la valeur, applique la conversion
## Affamé, déclenche les états et marques de première fois, recalcule le palier.
func modifier_jauge(nom: StringName, delta: int) -> void:
	if nom not in JAUGES:
		push_error("Jauge inconnue : %s" % nom)
		return
	if delta == 0:
		return
	var ancienne := valeur(nom)
	var brute := ancienne + delta
	var nouvelle := clampi(brute, 0, maximum(nom))
	var impaye := brute < 0
	_ecrire(nom, nouvelle)
	if nouvelle != ancienne:
		jauge_changee.emit(nom, ancienne, nouvelle)

	match nom:
		VIVRES:
			if nouvelle == 0 and ancienne > 0:
				etat_declenche.emit(&"affame")
				_marque_automatique(Marques.LA_FAIM)
			# Affamé : un coût en Vivres impossible à payer devient −1 Lucidité.
			if impaye:
				modifier_jauge(LUCIDITE, -1)
		HUILE:
			if nouvelle == 0 and lanterne_allumee:
				lanterne_allumee = false
				etat_declenche.emit(&"lanterne_eteinte")
		LUCIDITE:
			if nouvelle == 0 and lucidite_max != LUCIDITE_MAX_PERDU:
				lucidite_max = LUCIDITE_MAX_PERDU
				etat_declenche.emit(&"perdu")
				_marque_automatique(Marques.CE_QUI_A_ETE_VU)
			_recalculer_palier()


func est_affame() -> bool:
	return vivres == 0


func est_perdu() -> bool:
	return lucidite_max == LUCIDITE_MAX_PERDU


static func palier_pour(valeur_lucidite: int) -> StringName:
	if valeur_lucidite >= 7:
		return CLAIR
	if valeur_lucidite >= 4:
		return TROUBLE
	return EGARE  # 0 compris : la spec ne définit pas de palier à 0 (question ouverte).


func _ecrire(nom: StringName, v: int) -> void:
	match nom:
		VIVRES: vivres = v
		HUILE: huile = v
		LUCIDITE: lucidite = v


func _recalculer_palier() -> void:
	var nouveau := palier_pour(lucidite)
	if nouveau != palier:
		var ancien := palier
		palier = nouveau
		palier_change.emit(ancien, nouveau)


# --- Coûts, effets, conditions des options de dialogue ---------------------------
# Format commun (indépendant de Dialogue Manager) :
#   couts  = {"vivres": 1, "huile": 2}            valeurs positives = ce qu'on paie
#   effets = {"vivres": 1, "lucidite": -1}        deltas signés
#   condition = {"jauge_min": {"huile": 1}, "marque": &"doigt_de_saint",
#                "sceau": &"ouvert" | &"ferme" | &"abime" | &"rechauffe", "palier": &"egare"}

func appliquer_couts(couts: Dictionary) -> void:
	for nom in couts:
		modifier_jauge(StringName(nom), -absi(int(couts[nom])))


func appliquer_effets(effets: Dictionary) -> void:
	for nom in effets:
		modifier_jauge(StringName(nom), int(effets[nom]))


## Coûts tels que l'interface doit les afficher pour TOUTES les options d'une rencontre
## (spec v0.2 révisée). Reçoit la liste des dictionnaires de coûts, dans l'ordre des options,
## et renvoie [{"couts": Dictionary, "cout_douteux": bool, "cout_faux": bool}, ...].
## Au palier Égaré, un tirage par rencontre :
##   50 % : une option affiche un coût faux de ±1 (jamais sous 0) + une autre option (leurre,
##          coût vrai) ; les deux portent cout_douteux ;
##   25 % : un leurre seul, sans mensonge ;
##   25 % : rien.
## Il faut au moins deux options avec un coût : une rencontre à un seul coût ne ment jamais.
## `cout_faux` sert au debug et aux tests : l'UI n'affiche que `cout_douteux`.
## Le coût réellement prélevé reste celui passé à appliquer_couts() : l'interface trompe, elle ne vole pas.
func couts_affiches_rencontre(couts_options: Array, rng: RandomNumberGenerator = null) -> Array[Dictionary]:
	var resultat: Array[Dictionary] = []
	var candidates: Array[int] = []
	for i in couts_options.size():
		var couts: Dictionary = couts_options[i]
		resultat.append({"couts": couts.duplicate(), "cout_douteux": false, "cout_faux": false})
		if not couts.is_empty():
			candidates.append(i)
	if palier != EGARE or candidates.size() < 2:
		return resultat
	if rng == null:
		rng = RandomNumberGenerator.new()
		rng.randomize()
	var tirage := rng.randf()
	if tirage >= PROBA_MENSONGE + PROBA_LEURRE_SEUL:
		return resultat
	var a: int = candidates.pop_at(rng.randi_range(0, candidates.size() - 1))
	if tirage >= PROBA_MENSONGE:
		resultat[a]["cout_douteux"] = true
		return resultat
	var b: int = candidates[rng.randi_range(0, candidates.size() - 1)]
	var affiches: Dictionary = resultat[a]["couts"]
	var cles := affiches.keys()
	var cle: Variant = cles[rng.randi_range(0, cles.size() - 1)]
	var vrai := int(affiches[cle])
	var faux := vrai + (1 if rng.randf() < 0.5 else -1)
	if faux < 0:
		faux = vrai + 1
	affiches[cle] = faux
	resultat[a]["cout_douteux"] = true
	resultat[a]["cout_faux"] = true
	resultat[b]["cout_douteux"] = true
	return resultat


## Une option est disponible si toutes ses conditions sont remplies. Les coûts ne bloquent
## pas : un coût en Vivres impayable se convertit (Affamé), les autres sont bornés à 0.
func condition_remplie(condition: Dictionary) -> bool:
	if condition.has("jauge_min"):
		var mins: Dictionary = condition["jauge_min"]
		for nom in mins:
			if valeur(StringName(nom)) < int(mins[nom]):
				return false
	if condition.has("marque") and not possede_marque(StringName(condition["marque"])):
		return false
	if condition.has("sceau") and not _sceau_est(StringName(condition["sceau"])):
		return false
	if condition.has("palier") and palier != StringName(condition["palier"]):
		return false
	if condition.has("objet") and not possede_objet(StringName(condition["objet"])):
		return false
	if condition.has("rencontre_vue") and not rencontre_vue(StringName(condition["rencontre_vue"])):
		return false
	return true


func _sceau_est(etat: StringName) -> bool:
	match etat:
		&"ouvert": return sceau_ouvert
		&"ferme": return not sceau_ouvert
		&"intact": return not sceau_abime and not sceau_ouvert
		&"abime": return sceau_abime
		&"rechauffe": return sceau_rechauffe
	push_error("État de sceau inconnu : %s" % etat)
	return false


# --- Marques -----------------------------------------------------------------------

## Ajoute une marque. Renvoie false si la rencontre a déjà donné une marque
## ou si la marque est déjà possédée (une marque ne se gagne qu'une fois).
func ajouter_marque(id: StringName, famille: StringName, rencontre: StringName = &"") -> bool:
	if possede_marque(id):
		return false
	if rencontre != &"" and rencontre in rencontres_marquees:
		return false
	var m := Marques.creer(id, famille)
	marques.append(m)
	if rencontre != &"":
		rencontres_marquees.append(rencontre)
	marque_gagnee.emit(m)
	return true


func possede_marque(id: StringName) -> bool:
	return not trouver_marque(id).is_empty()


func trouver_marque(id: StringName) -> Dictionary:
	for m in marques:
		if m["id"] == id:
			return m
	return {}


## Fixe une Promesse ouverte à tenue ou trahie. Une promesse résolue ne change plus.
func resoudre_promesse(id: StringName, tenue: bool) -> bool:
	var m := trouver_marque(id)
	if m.is_empty() or m["famille"] != Marques.PROMESSE or m["etat"] != Marques.OUVERTE:
		return false
	m["etat"] = Marques.TENUE if tenue else Marques.TRAHIE
	promesse_resolue.emit(id, m["etat"])
	return true


func _marque_automatique(id: StringName) -> void:
	ajouter_marque(id, Marques.CICATRICE)


# --- Sceau (drapeaux jamais remis à faux) ----------------------------------------

func abimer_sceau() -> void:
	if not sceau_abime:
		sceau_abime = true
		sceau_change.emit(&"abime")


## Spec v0.2 : les gestes volontaires sur le Sceau (réchauffer, lire, ouvrir) sont
## désactivés à l'étape 1. Abîmer reste possible : c'est un accident (chute, fouille).
func gestes_sceau_permis() -> bool:
	return etape >= 2


## Réchauffer la cire à la lanterne : 1 Huile. Implique abîmé.
func peut_rechauffer_sceau() -> bool:
	return gestes_sceau_permis() and not sceau_rechauffe and not sceau_ouvert and huile >= 1


func rechauffer_sceau() -> bool:
	if not peut_rechauffer_sceau():
		return false
	modifier_jauge(HUILE, -1)
	abimer_sceau()
	sceau_rechauffe = true
	sceau_change.emit(&"rechauffe")
	return true


## Lire en transparence la prochaine ligne non lue du pli : sceau réchauffé, 1 Huile,
## une ligne par étape au plus, six lignes en tout.
func peut_lire_ligne() -> bool:
	return gestes_sceau_permis() and sceau_rechauffe and not sceau_ouvert and huile >= 1 \
		and etape_derniere_lecture != etape and pli_lignes_lues < PLI_NB_LIGNES


## Renvoie l'index (0 à 5) de la ligne lue, ou -1 si la lecture est impossible.
func lire_ligne_pli() -> int:
	if not peut_lire_ligne():
		return -1
	modifier_jauge(HUILE, -1)
	etape_derniere_lecture = etape
	pli_lignes_lues += 1
	return pli_lignes_lues - 1


func peut_ouvrir_sceau() -> bool:
	return gestes_sceau_permis() and not sceau_ouvert


func ouvrir_sceau() -> bool:
	if not peut_ouvrir_sceau():
		return false
	sceau_ouvert = true
	sceau_change.emit(&"ouvert")
	return true


# --- Rencontres --------------------------------------------------------------------

func marquer_rencontre_vue(id: StringName) -> void:
	if id != &"" and id not in rencontres_vues:
		rencontres_vues.append(id)
		rencontre_vue_marquee.emit(id)


func rencontre_vue(id: StringName) -> bool:
	return id in rencontres_vues


# --- Objets --------------------------------------------------------------------------

func ajouter_objet(id: StringName) -> void:
	if id not in objets:
		objets.append(id)


func possede_objet(id: StringName) -> bool:
	return id in objets


func retirer_objet(id: StringName) -> bool:
	if id not in objets:
		return false
	objets.erase(id)
	return true


## Manger un objet promis à quelqu'un (ex. le pain de Jacquot) : gain de Vivres,
## et la Promesse liée passe à trahie si elle était encore ouverte.
func manger_objet_promis(objet: StringName, gain_vivres: int, promesse: StringName) -> bool:
	if not retirer_objet(objet):
		return false
	modifier_jauge(VIVRES, gain_vivres)
	resoudre_promesse(promesse, false)
	return true


# --- Étapes et zones sombres --------------------------------------------------------

## La marche : −1 Vivres à chaque passage ; −1 Lucidité en quittant une étape ≥ 2
## (lecture de la courbe : on entre en étape 2 à 8, en étape 3 à 7).
func passer_etape() -> void:
	modifier_jauge(VIVRES, -1)
	if etape >= 2:
		modifier_jauge(LUCIDITE, -1)
	etape += 1
	etape_changee.emit(etape)


## Entrée dans une zone sombre. Renvoie true si la lanterne est allumée.
## Sans huile, la zone se joue forcément dans le noir.
func entrer_zone_sombre(veut_allumer: bool) -> bool:
	if veut_allumer and huile >= 1:
		lanterne_allumee = false
		modifier_jauge(HUILE, -1)
		# La dernière goutte suffit à traverser cette zone.
		lanterne_allumee = true
	else:
		lanterne_allumee = false
		modifier_jauge(LUCIDITE, -1)
	zone_sombre_changee.emit(true, lanterne_allumee)
	return lanterne_allumee


func sortir_zone_sombre() -> void:
	lanterne_allumee = false
	zone_sombre_changee.emit(false, false)


# --- Fin ------------------------------------------------------------------------------

## Spec v0.2 : les Promesses encore ouvertes sont résolues juste avant le calcul.
## `resolutions` associe un id de Promesse à true (tenue) ou false (trahie), selon ce que
## la scène finale décide ; une Promesse absente de `resolutions` reste ouverte et compte 0.
func resoudre_promesses_avant_fin(resolutions: Dictionary) -> void:
	for id in resolutions:
		resoudre_promesse(StringName(id), bool(resolutions[id]))


func promesses_ouvertes() -> Array[StringName]:
	var ids: Array[StringName] = []
	for m in marques:
		if m["famille"] == Marques.PROMESSE and m["etat"] == Marques.OUVERTE:
			ids.append(m["id"])
	return ids


func fin() -> StringName:
	return CalculFin.calculer(marques, sceau_ouvert)


# --- Sérialisation (autosave jalon 2) ---------------------------------------------------

func vers_dictionnaire() -> Dictionary:
	return {
		"version": 1,
		"vivres": vivres,
		"huile": huile,
		"lucidite": lucidite,
		"lucidite_max": lucidite_max,
		"sceau_abime": sceau_abime,
		"sceau_rechauffe": sceau_rechauffe,
		"sceau_ouvert": sceau_ouvert,
		"lanterne_allumee": lanterne_allumee,
		"marques": marques.duplicate(true),
		"etape": etape,
		"rencontres_marquees": rencontres_marquees.duplicate(),
		"etape_derniere_lecture": etape_derniere_lecture,
		"pli_lignes_lues": pli_lignes_lues,
		"objets": objets.duplicate(),
		"rencontres_vues": rencontres_vues.duplicate(),
	}


func depuis_dictionnaire(d: Dictionary) -> void:
	reinitialiser()
	lucidite_max = int(d.get("lucidite_max", LUCIDITE_MAX_NORMAL))
	vivres = clampi(int(d.get("vivres", vivres)), 0, VIVRES_MAX)
	huile = clampi(int(d.get("huile", huile)), 0, HUILE_MAX)
	lucidite = clampi(int(d.get("lucidite", lucidite)), 0, lucidite_max)
	palier = palier_pour(lucidite)
	sceau_abime = bool(d.get("sceau_abime", false))
	sceau_rechauffe = bool(d.get("sceau_rechauffe", false))
	sceau_ouvert = bool(d.get("sceau_ouvert", false))
	lanterne_allumee = bool(d.get("lanterne_allumee", false))
	for m: Dictionary in d.get("marques", []):
		marques.append({"id": StringName(m["id"]), "famille": StringName(m["famille"]), "etat": StringName(m.get("etat", ""))})
	etape = int(d.get("etape", 1))
	for r in d.get("rencontres_marquees", []):
		rencontres_marquees.append(StringName(r))
	etape_derniere_lecture = int(d.get("etape_derniere_lecture", 0))
	pli_lignes_lues = clampi(int(d.get("pli_lignes_lues", 0)), 0, PLI_NB_LIGNES)
	for o in d.get("objets", []):
		objets.append(StringName(o))
	for v in d.get("rencontres_vues", []):
		rencontres_vues.append(StringName(v))
	etat_charge.emit()
