extends CinematiquePlans
## e5_autre_se_retourne (planches de la DA, tools/gen_cin_e5.py) : au bout de la boucle, l'Autre
## marche sur place au loin (« il ne s'approche pas, il ne s'éloigne pas »), s'arrête, sa tête
## tourne à moitié (jamais jusqu'au visage), revient, et il repart du même pas.
## Un plan plein écran : fond cin_autre_01, 6 images (cin_autre_02, grille 3 × 2) en (880, 500),
## rendus au double et posés à l'échelle 1/2 dans un Cadre. 0 et 5 sont les deux appuis de la
## marche : alternés à 3 i/s, il marche sur place. 1 il s'arrête, 2 et 3 la tête tourne (10 i/s),
## tenue sur 3, puis 4 et 1 elle revient, et la marche reprend jusqu'à une tenue finale.
## La caméra pousse lentement vers l'Autre pendant tout le plan (le Cadre grossit autour de lui,
## de 1 à ZOOM_FIN) : c'est elle qui avance, lui ne se rapproche jamais. Une brume (cin_autre_03)
## dérive devant les croix. En effets atténués, deux plans fixes : large, puis serré à l'arrêt.

const FOND := "res://assets/graphics/cin/cin_autre_01.png"
const GESTE := "res://assets/graphics/cin/cin_autre_02.png"
const BRUME := "res://assets/graphics/cin/cin_autre_03.png"
const MARCHE := 2.0
const CADENCE_MARCHE := 1.0 / 3.0
const TENUE_TETE := 1.2
const TENUE_FIN := 0.5
## Les planches sont rendues au double : posées à 1/2, nettes jusqu'à une poussée de 2.
const FINESSE := 2.0
const ZOOM_FIN := 1.6
## Centre de la poussée : l'Autre (milieu de sa zone de 200 × 170 en 880, 500).
const CENTRE := Vector2(980, 585)
## La brume : posée à l'échelle 2, en y 560, elle glisse de 0 à BRUME_DERIVE px.
const BRUME_Y := 560.0
const BRUME_DERIVE := -1400.0

var couche: CanvasLayer


func construire() -> Animation:
	var fond := planche(FOND)
	var geste := planche(GESTE)
	if fond == null or geste == null:
		return null
	couche = couche_plein_ecran()
	var cadre := Node2D.new()
	cadre.name = "Cadre"
	couche.add_child(cadre)
	var s_fond := sprite("Fond", fond, Vector2.ZERO)
	s_fond.scale = Vector2.ONE / FINESSE
	cadre.add_child(s_fond)
	var autre := sprite("Autre", geste, Vector2(880, 500), 3, 2)
	autre.scale = Vector2.ONE / FINESSE
	cadre.add_child(autre)
	var brume_tex := planche(BRUME)
	if brume_tex != null:
		var brume := sprite("Brume", brume_tex, Vector2(0, BRUME_Y))
		brume.scale = Vector2(2, 2)
		couche.add_child(brume)

	var anim := Animation.new()
	cle(anim, "Plans:visible", 0.0, true)
	var t := marcher(anim, 0.0)
	var arret := t
	t = images(anim, "Plans/Cadre/Autre", t, 1, 3) - Cinematique.PAS + TENUE_TETE
	t = images(anim, "Plans/Cadre/Autre", t, 4, 4)
	cle(anim, "Plans/Cadre/Autre:frame", t, 1)
	t += Cinematique.PAS
	t = marcher(anim, t) + TENUE_FIN
	anim.length = snappedf(t, Cinematique.PAS)
	if Reglages.valeur(&"effets_attenues"):
		cadrer(anim, 0.0, 1.0)
		cadrer(anim, arret, ZOOM_FIN)
	else:
		pousser(anim, anim.length)
	deriver(anim, anim.length)
	cle(anim, "Plans:visible", anim.length, false)
	return anim


## Les appuis 0 et 5 en alternance pendant MARCHE secondes, à partir de debut ; rend la fin.
func marcher(anim: Animation, debut: float) -> float:
	var pas := roundi(MARCHE / CADENCE_MARCHE)
	for k in pas:
		cle(anim, "Plans/Cadre/Autre:frame", debut + k * CADENCE_MARCHE, 0 if k % 2 == 0 else 5)
	return debut + MARCHE


## Le Cadre à l'échelle z, centré sur l'Autre, à l'instant t.
func cadrer(anim: Animation, t: float, z: float) -> void:
	cle(anim, "Plans/Cadre:scale", t, Vector2(z, z))
	cle(anim, "Plans/Cadre:position", t, CENTRE - CENTRE * z)


## La poussée lente : une clé tous les dixièmes, adoucie au début et à la fin.
func pousser(anim: Animation, duree: float) -> void:
	var n := roundi(duree / Cinematique.PAS)
	for k in n + 1:
		var u := float(k) / n
		cadrer(anim, k * Cinematique.PAS, lerpf(1.0, ZOOM_FIN, u * u * (3.0 - 2.0 * u)))


## La brume glisse vers la gauche, régulièrement, une clé tous les dixièmes.
func deriver(anim: Animation, duree: float) -> void:
	if couche.get_node_or_null("Brume") == null:
		return
	var n := roundi(duree / Cinematique.PAS)
	for k in n + 1:
		cle(anim, "Plans/Brume:position", k * Cinematique.PAS, Vector2(BRUME_DERIVE * k / n, BRUME_Y))


func apres() -> void:
	if couche != null:
		couche.visible = false
