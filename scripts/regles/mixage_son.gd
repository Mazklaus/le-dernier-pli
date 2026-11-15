class_name MixageSon
extends RefCounted
## Règles du mixage d'ambiance selon la Lucidité (intention sonore du Sound Designer).
## Fonctions pures : aucune dépendance à l'arbre de scènes ni à GameState, testables seules.
##
## Chaque étape joue deux familles de couches : le « réel » (ce que le messager entend
## vraiment) et l'« autre » (ce que la Lucidité qui baisse laisse passer). Le palier fixe
## leur mélange ; l'état Perdu et le noir sans lanterne le poussent vers l'autre.

## Gains linéaires [réel, autre] par palier de GameState.
const MELANGE_PAR_PALIER := {
	&"clair": Vector2(1.0, 0.0),
	&"trouble": Vector2(0.70, 0.45),
	&"egare": Vector2(0.25, 1.0),
}
## Perdu (définitif) : remplace le mélange du palier, quelle que soit la valeur.
const MELANGE_PERDU := Vector2(0.10, 1.0)
## Zone sombre traversée lanterne éteinte : l'autre monte de 20 points, plafonné à 1.
const BONUS_NOIR := 0.20

## Fréquence de coupure du passe-bas du bus Ambiance : les aigus se ferment en descendant.
const COUPURE_PAR_PALIER := {
	&"clair": 20000.0,
	&"trouble": 7000.0,
	&"egare": 2500.0,
}
const COUPURE_PERDU := 1200.0

## Durée d'un changement de palier : le joueur ne doit jamais entendre de bascule nette.
const DUREE_FONDU := 10.0

## Gain des voix de surface à chaque repère (Marker2D posés par le Level Designer) :
## l'ambiance s'appauvrit de gauche à droite, quel que soit l'ordre de visite.
const GAIN_VOIX_REPERES := {
	&"boyau_arriere": 1.0,
	&"carrefour": 0.7,
	&"periscope": 0.35,
	&"pied_echelle": 0.1,
}

const GAIN_MUET_DB := -80.0

## Étapes qui passent du jour à la nuit (3, puis 4 et 6) : la couche « jour » et la couche
## « nuit » se croisent à puissance constante, le temps du fondu au noir du Passage.
const DUREE_FONDU_PHASE := 6.0


## Gain d'une couche selon la part de nuit (0 : plein jour, 1 : pleine nuit).
## Toute couche autre que « jour » et « nuit » n'est pas concernée (1).
static func gain_phase(couche: String, nuit: float) -> float:
	match couche:
		"jour":
			return cos(clampf(nuit, 0.0, 1.0) * PI / 2.0)
		"nuit":
			return sin(clampf(nuit, 0.0, 1.0) * PI / 2.0)
	return 1.0


## Mélange cible pour un état donné : {"reel": float, "autre": float, "coupure_hz": float}.
static func cible(palier: StringName, perdu: bool, dans_le_noir: bool) -> Dictionary:
	var melange: Vector2 = MELANGE_PAR_PALIER.get(palier, MELANGE_PAR_PALIER[&"clair"])
	var coupure: float = COUPURE_PAR_PALIER.get(palier, COUPURE_PAR_PALIER[&"clair"])
	if perdu:
		melange = MELANGE_PERDU
		coupure = COUPURE_PERDU
	var autre := melange.y
	if dans_le_noir:
		autre = minf(1.0, autre + BONUS_NOIR)
	return {"reel": melange.x, "autre": autre, "coupure_hz": coupure}


## Gain des voix de surface à l'abscisse `x`, par interpolation linéaire entre des points
## (x, gain) triés par x. Avant le premier point ou après le dernier, le gain est constant.
static func gain_voix(x: float, points: Array[Vector2]) -> float:
	if points.is_empty():
		return 1.0
	if x <= points[0].x:
		return points[0].y
	for i in range(1, points.size()):
		var a := points[i - 1]
		var b := points[i]
		if x <= b.x:
			var t := 0.0 if is_equal_approx(a.x, b.x) else (x - a.x) / (b.x - a.x)
			return lerpf(a.y, b.y, t)
	return points[-1].y


## Points (x, gain) à partir des repères nommés de la scène ; les noms inconnus sont ignorés.
static func points_depuis_reperes(positions: Dictionary) -> Array[Vector2]:
	var points: Array[Vector2] = []
	for nom: StringName in positions:
		if GAIN_VOIX_REPERES.has(nom):
			points.append(Vector2(float(positions[nom]), GAIN_VOIX_REPERES[nom]))
	points.sort_custom(func(a: Vector2, b: Vector2) -> bool: return a.x < b.x)
	return points


## Gain linéaire vers décibels, avec un plancher muet pour 0.
static func vers_db(gain: float) -> float:
	return GAIN_MUET_DB if gain <= 0.0001 else maxf(GAIN_MUET_DB, linear_to_db(gain))
