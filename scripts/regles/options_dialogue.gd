class_name OptionsDialogue
extends RefCounted
## Règles de présentation des répliques et des options pour la bulle de dialogue.
## Convention des tags Dialogue Manager (validée avec le Narrative Designer) :
##   [#cout_vivres=1] [#cout_huile=2] [#cout_lucidite=1]  coûts, affichés avant le choix
##                                                         et prélevés par la bulle au choix ;
##   [#sans_prelevement] coûts affichés seulement : le script de l'option les prélève déjà
##                       (ex. GameState.entrer_zone_sombre() dans la sape) ;
##   [#cache]           option cachée (et non grisée) quand sa condition [if …] échoue ;
##   [#hallucination]   option fausse (Trouble et en dessous) : elle bave à l'écran ;
##   [#timbre=slug]     timbre de voix d'une réplique, quand le nom affiché ne suffit pas ;
##   [#enfoui]          à l'Égaré (palier lu au moment du choix), le coût en Lucidité de
##                      l'option baisse de 1, sans descendre sous 0 (GD, étape 6). Le coût
##                      réduit est affiché, puis la règle des coûts douteux s'applique.
##   [#geste=tendre]    sur une réplique : son personnage joue le geste (planche
##                      chr_<nom>_tendre_01) quand elle s'affiche ; [#geste=rose:danser]
##                      vise un autre personnage de la rencontre (directive animation du GD) ;
##   [#tenir]           avec un geste : le personnage garde la dernière image du geste au lieu
##                      de revenir à la respiration, jusqu'au geste suivant.
## Fonctions pures sur des PackedStringArray de tags : testables sans Dialogue Manager.

const PREFIXE_COUT := "cout_"
const TAG_CACHE := "cache"
const TAG_SANS_PRELEVEMENT := "sans_prelevement"
const TAG_HALLUCINATION := "hallucination"
const TAG_TIMBRE := "timbre"
const TAG_ENFOUI := "enfoui"
const TAG_GESTE := "geste"
const TAG_TENIR := "tenir"
const ACCENTS := {"à": "a", "â": "a", "ä": "a", "ç": "c", "é": "e", "è": "e", "ê": "e", "ë": "e",
	"î": "i", "ï": "i", "ô": "o", "ö": "o", "ù": "u", "û": "u", "ü": "u", "ÿ": "y", "œ": "oe", "æ": "ae"}


static func a_tag(tags: PackedStringArray, nom: String) -> bool:
	for t in tags:
		if t == nom or t.begins_with(nom + "="):
			return true
	return false


static func valeur_tag(tags: PackedStringArray, nom: String) -> String:
	var prefixe := nom + "="
	for t in tags:
		if t.begins_with(prefixe):
			return t.substr(prefixe.length()).strip_edges()
	return ""


## Coûts déclarés par les tags d'une option : {&"vivres": 1, …} (valeurs positives).
static func couts(tags: PackedStringArray) -> Dictionary:
	var resultat := {}
	for t in tags:
		if not t.begins_with(PREFIXE_COUT) or not t.contains("="):
			continue
		var nom := StringName(t.substr(PREFIXE_COUT.length()).get_slice("=", 0))
		var valeur := absi(t.get_slice("=", 1).strip_edges().to_int())
		if nom in GameState.JAUGES and valeur > 0:
			resultat[nom] = valeur
	return resultat


## Présentation de toutes les options d'une réplique. `options` : liste de
## {"texte": String, "tags": PackedStringArray, "autorisee": bool}, dans l'ordre.
## Renvoie, pour les options visibles seulement :
## {"index": int (position d'origine), "texte", "couts_reels", "couts_affiches",
##  "a_prelever": Dictionary (vide si [#sans_prelevement]), "bave": bool, "disponible": bool}.
## `bave` = coût douteux (GameState.couts_affiches_rencontre) ou hallucination.
static func presenter(options: Array, rng: RandomNumberGenerator = null) -> Array[Dictionary]:
	var visibles: Array[Dictionary] = []
	var liste_couts: Array = []
	for i in options.size():
		var o: Dictionary = options[i]
		var tags: PackedStringArray = o.get("tags", PackedStringArray())
		var autorisee: bool = o.get("autorisee", true)
		if not autorisee and a_tag(tags, TAG_CACHE):
			continue
		var c := couts(tags)
		if a_tag(tags, TAG_ENFOUI):
			c = cout_enfoui(c, GameState.palier)
		visibles.append({
			"index": i,
			"texte": String(o.get("texte", "")).strip_edges(),
			"couts_reels": c,
			"couts_affiches": c.duplicate(),
			"a_prelever": {} if a_tag(tags, TAG_SANS_PRELEVEMENT) else c.duplicate(),
			"bave": a_tag(tags, TAG_HALLUCINATION),
			"disponible": autorisee,
		})
		liste_couts.append(c)
	var affiches: Array[Dictionary] = GameState.couts_affiches_rencontre(liste_couts, rng)
	for i in visibles.size():
		visibles[i]["couts_affiches"] = affiches[i]["couts"]
		if affiches[i]["cout_douteux"]:
			visibles[i]["bave"] = true
	return visibles


## Coûts d'une option [#enfoui] : −1 Lucidité à l'Égaré, jamais sous 0 (clé retirée à 0).
static func cout_enfoui(c: Dictionary, palier: StringName) -> Dictionary:
	var resultat := c.duplicate()
	if palier == GameState.EGARE and resultat.has(GameState.LUCIDITE):
		var reste := maxi(0, int(resultat[GameState.LUCIDITE]) - 1)
		if reste == 0:
			resultat.erase(GameState.LUCIDITE)
		else:
			resultat[GameState.LUCIDITE] = reste
	return resultat


## Slug du timbre de voix d'une réplique (vox_<slug>_NN.ogg), ou "" pour la narration.
static func slug_timbre(personnage: String, tags: PackedStringArray) -> String:
	var force := valeur_tag(tags, TAG_TIMBRE)
	if force != "":
		return force
	var slug := personnage.strip_edges().to_lower()
	for accent: String in ACCENTS:
		slug = slug.replace(accent, ACCENTS[accent])
	return slug.replace(" ", "-")


## Geste demandé par les tags d'une réplique : {"cible": slug du personnage, "geste": nom,
## "explicite": cible nommée, "tenir": garder la dernière image}, ou {} sans tag geste.
## Sans cible explicite (« nom:geste »), la cible est le locuteur.
static func geste(locuteur: String, tags: PackedStringArray) -> Dictionary:
	var valeur := valeur_tag(tags, TAG_GESTE).strip_edges()
	if valeur == "":
		return {}
	var cible := slug_timbre(locuteur, PackedStringArray())
	var nom := valeur
	if valeur.contains(":"):
		cible = valeur.get_slice(":", 0).strip_edges()
		nom = valeur.get_slice(":", 1).strip_edges()
	if nom == "":
		return {}
	return {"cible": StringName(cible), "geste": StringName(nom), "explicite": valeur.contains(":"),
		"tenir": a_tag(tags, TAG_TENIR)}
