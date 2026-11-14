class_name Battement
extends RefCounted
## Horloge partagée du battement de Lucidité basse (règle de la DA, alignée avec l'UI/UX) :
## deux coups puis un silence, en paliers nets à 10 i/s.
## - Clair : rien ne bat (opacité 1).
## - Trouble : cycle de 1,2 s (12 images) : 1 → 0,55 → 1 → 0,55 → 1, puis silence.
## - Égaré : même battement en 0,8 s (8 images), et toutes les 4 à 7 s, au hasard, une
##   disparition complète de 2 images.
## - Effets atténués : rien ne bat, rien ne tremble.
## Tout est fonction du temps du moteur (Time.get_ticks_msec) : le ruban de Tobie, le sceau du
## HUD et les tremblements sont en phase sans rien partager d'autre, et le hasard de l'Égaré
## est le même pour tous (tiré d'un hachage du créneau, pas d'un générateur).

const IMAGES_PAR_SECONDE := 10.0
const OPACITE_COUP := 0.55
## Images du cycle par palier (0 : pas de battement).
const IMAGES_CYCLE := {&"trouble": 12, &"egare": 8}
## Images du cycle où tombe un coup (opacité basse, tremblements).
const IMAGES_COUP := [1, 3]
## Disparitions de l'Égaré : une par créneau de 5,5 s, décalée de 0 à 1,5 s, ce qui donne
## des écarts de 4 à 7 s entre deux disparitions.
const CRENEAU_DISPARITION := 5.5
const DECALAGE_DISPARITION := 1.5
const IMAGES_DISPARITION := 2


## Temps de l'horloge partagée, en secondes.
static func maintenant() -> float:
	return Time.get_ticks_msec() / 1000.0


## Image courante (10 i/s) d'un temps donné.
static func image(temps: float) -> int:
	return int(floor(temps * IMAGES_PAR_SECONDE))


static func bat(palier: StringName, attenue: bool) -> bool:
	return not attenue and IMAGES_CYCLE.has(palier)


## Un coup tombe-t-il sur cette image ? (déclencheur des tremblements)
static func coup(temps: float, palier: StringName, attenue: bool) -> bool:
	if not bat(palier, attenue):
		return false
	return (image(temps) % int(IMAGES_CYCLE[palier])) in IMAGES_COUP


## Disparition complète du ruban (Égaré seulement).
static func disparu(temps: float, palier: StringName, attenue: bool) -> bool:
	if palier != &"egare" or attenue:
		return false
	var creneau := int(floor(temps / CRENEAU_DISPARITION))
	var debut := creneau * CRENEAU_DISPARITION + decalage(creneau)
	return temps >= debut and temps < debut + IMAGES_DISPARITION / IMAGES_PAR_SECONDE


## Décalage pseudo-aléatoire mais stable d'un créneau, de 0 à DECALAGE_DISPARITION s, par
## pas d'une image.
static func decalage(creneau: int) -> float:
	var pas := int(DECALAGE_DISPARITION * IMAGES_PAR_SECONDE) + 1
	return float(absi(hash(creneau * 7919 + 17)) % pas) / IMAGES_PAR_SECONDE


## Opacité du ruban (Tobie, sceau du HUD) à un instant.
static func opacite(temps: float, palier: StringName, attenue: bool) -> float:
	if disparu(temps, palier, attenue):
		return 0.0
	return OPACITE_COUP if coup(temps, palier, attenue) else 1.0
