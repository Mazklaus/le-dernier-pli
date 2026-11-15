extends GutTest
## Règle du Game Director : le rouge du sceau et du ruban reste reconnu dans chaque lieu de
## chaque étape, de jour comme de nuit, en Clair et en Trouble. Mesuré en sortie de l'écran
## gravure : r − max(g, b) > 0,18. L'Égaré est exclu : rouge_efface y pâlit le rouge exprès.
##
## Les tests tournent sans rendu (--headless) : on rejoue donc ici, en GDScript, la chaîne
## de couleur d'un pixel rouge : une éventuelle teinte de scène (CanvasModulate « Eclairage »,
## l'ancien chemin de la nuit), puis les étapes 3 et 4 de shaders/ecran_gravure.gdshader
## (remappage papier/encre, uniforme teinte, détection du rouge, rouge exact). Le grain (±grain/2, sans effet sur le rouge exact) et le
## tremblé (déplacement des UV) sont laissés de côté.
## Si le shader change sa façon de traiter la couleur (teinte de nuit déplacée dans le shader,
## par exemple), _sortie_gravure() doit suivre.

const SEUIL_SORTIE := 0.18
const PALIERS_TESTES: Array[StringName] = [&"clair", &"trouble"]
const LUMA := Vector3(0.299, 0.587, 0.114)
const ENCRE_REF := Color(0.082, 0.075, 0.059)
const PAPIER_REF := Color(0.910, 0.898, 0.855)


func before_each() -> void:
	GameState.reinitialiser()


func after_each() -> void:
	GameState.reinitialiser()


func _etapes_existantes() -> Array[int]:
	var liste: Array[int] = []
	for numero in range(1, SceneRouter.NB_ETAPES + 1):
		if SceneRouter.etape_existe(numero):
			liste.append(numero)
	return liste


func _instancier(numero: int) -> EtapeBase:
	var scene := load(SceneRouter.chemin_etape(numero)) as PackedScene
	var etape := scene.instantiate() as EtapeBase
	add_child_autofree(etape)
	return etape


## Les lieux d'une étape : la surface (&"") et chaque sous-scène de « Lieux », nommée comme
## son marqueur d'entrée (entree_<lieu>).
func _lieux(etape: EtapeBase) -> Array[StringName]:
	var liste: Array[StringName] = [&""]
	var lieux := etape.get_node_or_null("Lieux")
	if lieux == null:
		return liste
	for lieu in lieux.get_children():
		for marqueur in lieu.find_children("entree_*", "Marker2D", true, false):
			liste.append(StringName(String(marqueur.name).trim_prefix("entree_")))
			break
	return liste


func _teinte_scene(etape: EtapeBase) -> Color:
	var eclairage := etape.get_node_or_null("Eclairage") as CanvasModulate
	return eclairage.color if eclairage != null else Color.WHITE


## Valeur d'un paramètre du matériau, ou sa valeur par défaut dans le shader s'il n'a jamais
## été posé (get_shader_parameter renvoie alors null).
func _param(m: ShaderMaterial, nom: StringName) -> Variant:
	var v: Variant = m.get_shader_parameter(nom)
	if v == null:
		v = _defaut_dans_le_source(m.shader.code, nom)
	assert_not_null(v, "paramètre %s introuvable dans l'écran gravure" % nom)
	return v


## Sans rendu, le serveur ne connaît pas les valeurs par défaut des uniforms : on les lit
## dans le code du shader (« uniform float nom ... = 0.18; », « vec4(r, g, b, a) »).
static func _defaut_dans_le_source(code: String, nom: StringName) -> Variant:
	var re := RegEx.new()
	re.compile("uniform\\s+(\\w+)\\s+%s\\b[^=;]*=\\s*([^;]+);" % nom)
	var r := re.search(code)
	if r == null:
		return null
	var valeur := r.get_string(2).strip_edges()
	if r.get_string(1) == "vec4":
		var nombres := valeur.trim_prefix("vec4(").trim_suffix(")").split(",")
		return Color(float(nombres[0]), float(nombres[1]), float(nombres[2]), float(nombres[3]))
	if r.get_string(1) == "bool":
		return valeur == "true"
	return float(valeur)


func _f(m: ShaderMaterial, nom: StringName) -> float:
	var v: Variant = _param(m, nom)
	return float(v) if v != null else 0.0


func _c(m: ShaderMaterial, nom: StringName) -> Color:
	var v: Variant = _param(m, nom)
	return v as Color if v != null else Color.BLACK


static func _rougeur(c: Color) -> float:
	return c.r - maxf(c.g, c.b)


static func _luma(c: Color) -> float:
	return Vector3(c.r, c.g, c.b).dot(LUMA)


## Couleur en sortie de l'écran gravure pour un pixel du monde de couleur « source »
## (avant la teinte de la scène « teinte », Eclairage, s'il en reste un).
func _sortie_gravure(source: Color, teinte: Color, m: ShaderMaterial) -> Color:
	var src := Color(source.r * teinte.r, source.g * teinte.g, source.b * teinte.b)
	var encre := _c(m, &"couleur_encre")
	var papier := _c(m, &"couleur_papier")
	var rouge := _c(m, &"couleur_rouge")
	var seuil := _f(m, &"seuil_rouge")
	var t := clampf((_luma(src) - _luma(ENCRE_REF)) / (_luma(PAPIER_REF) - _luma(ENCRE_REF)), 0.0, 1.0)
	var c := encre.lerp(papier, t)
	var teinte_gravure := _c(m, &"teinte")
	c = Color(c.r * teinte_gravure.r, c.g * teinte_gravure.g, c.b * teinte_gravure.b)
	var r := smoothstep(seuil, seuil + 0.12, _rougeur(src))
	return c.lerp(rouge.lerp(encre, _f(m, &"rouge_efface")), r)


func test_le_rouge_reste_reconnu_partout_en_clair_et_en_trouble() -> void:
	var etapes := _etapes_existantes()
	assert_gt(etapes.size(), 0, "aucune étape construite trouvée")
	var echecs: Array[String] = []
	var cas := 0
	for numero in etapes:
		var etape := _instancier(numero)
		await wait_process_frames(2)
		var m := etape.materiau_gravure()
		if m == null:
			echecs.append("étape %d : pas d'écran gravure" % numero)
			continue
		# Le rouge des assets (sceau, ruban) : la couleur exacte que le shader restitue.
		var rouge_asset := _c(m, &"couleur_rouge")
		for lieu in _lieux(etape):
			for nuit in [false, true]:
				etape.entrer_lieu(lieu)
				etape.definir_nuit(nuit)
				var teinte := _teinte_scene(etape)
				var teinte_gravure := _c(m, &"teinte")
				for palier in PALIERS_TESTES:
					m.set_shader_parameter(&"rouge_efface", LuciditeEcran.valeurs_pour(palier).y)
					var sortie := _sortie_gravure(rouge_asset, teinte, m)
					cas += 1
					if _rougeur(sortie) <= SEUIL_SORTIE:
						echecs.append("étape %d, lieu « %s », %s, %s : r − max(g, b) = %.3f en sortie (scène %s, gravure %s)"
								% [numero, lieu if lieu != &"" else "surface", "nuit" if nuit else "jour",
								palier, _rougeur(sortie), teinte.to_html(false), teinte_gravure.to_html(false)])
	assert_gt(cas, 0, "aucun cas testé")
	assert_eq(echecs.size(), 0, "rouge non reconnu (%d cas sur %d) :\n%s"
			% [echecs.size(), cas, "\n".join(echecs)])


## Garde-fou du modèle : sans teinte, le rouge exact sort tel quel, et l'Égaré le pâlit bien
## sous le seuil de couleur pure (c'est voulu, d'où son exclusion).
func test_modele_sans_teinte() -> void:
	var etape := _instancier(_etapes_existantes()[0])
	await wait_process_frames(2)
	var m := etape.materiau_gravure()
	var rouge := _c(m, &"couleur_rouge")
	m.set_shader_parameter(&"rouge_efface", 0.0)
	var sortie := _sortie_gravure(rouge, Color.WHITE, m)
	assert_almost_eq(sortie.r, rouge.r, 0.001)
	assert_almost_eq(sortie.g, rouge.g, 0.001)
	m.set_shader_parameter(&"rouge_efface", LuciditeEcran.valeurs_pour(&"egare").y)
	assert_lt(_rougeur(_sortie_gravure(rouge, Color.WHITE, m)), _rougeur(rouge))


## Garde-fou du modèle côté shader : la teinte s'applique avant le rouge exact (étape 4),
## sinon le modèle ci-dessus ne décrit plus le shader.
func test_le_shader_teinte_avant_le_rouge_exact() -> void:
	var code := (load("res://shaders/ecran_gravure.gdshader") as Shader).code
	var teinte := code.find("c *= teinte.rgb")
	var rouge := code.find("float rougeur")
	assert_gt(teinte, -1, "le shader n'applique plus « c *= teinte.rgb » : adapter _sortie_gravure()")
	assert_gt(rouge, teinte, "la teinte doit précéder la détection du rouge exact")
