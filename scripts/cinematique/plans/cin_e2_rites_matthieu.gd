extends CinematiquePlans
## e2_rites_matthieu (lot 2, planche validée par le GD le 17/11, retouches comprises) : 8 s,
## option « Lui rendre ses rites » de e2_sacoche. Planches de tools/gen_cin_e2_rites.py.
## P1, 0 à 3 s : gros plan, deux mains sales posent le quignon dans la sacoche vide de Matthieu
##    (3 images) ; lente avancée (plan fixe en effets atténués).
## P2, 3 à 6 s : au bord du trou, de dos, Tobie s'agenouille (2 images) ; la sacoche refermée
##    tout au fond ; lente avancée.
## P3, 6 à 8 s (plan fixe) : de près, de trois quarts, le bas du visage sous la capuche, paupières baissées,
##    sans sourire ; les lèvres disent la prière (2 images, rythme irrégulier).
## De dos et de près, le pli et son ruban (à la poitrine) restent hors champ.

const CIN := "res://assets/graphics/cin/%s.png"
const SON := "sfx_rites_matthieu"
const DUREE := 8.0
const P2 := 3.0
const P3 := 6.0
## P1 : les mains (ZONE_MAINS du générateur), leurs trois images.
const ZONE_MAINS := Vector2(460, 0)
const MAINS := [[0.0, 0], [1.3, 1], [2.3, 2]]
const FOYER_SACOCHE := Vector2(960, 620)
const ZOOM_SACOCHE := 1.06
## P2 : Tobie de dos (ZONE_DOS), debout puis à genoux.
const ZONE_DOS := Vector2(180, 180)
const DOS := [[3.0, 0], [4.3, 1]]
const FOYER_TROU := Vector2(820, 760)
const ZOOM_TROU := 1.08
## P3 : les lèvres (ZONE_LEVRES), ouvertes et closes à mi-voix.
const ZONE_LEVRES := Vector2(1020, 620)
const LEVRES := [[6.0, 0], [6.2, 1], [6.4, 0], [6.55, 1], [6.85, 0], [7.0, 1], [7.15, 0], [7.45, 1], [7.6, 0]]
const FOYER_VISAGE := Vector2(1100, 600)
## Plan fixe : un zoom ferait baver le bord de la vignette des lèvres sur la joue.
const ZOOM_VISAGE := 1.0

var couche: CanvasLayer


func construire() -> Animation:
	var tex := {}
	for nom in ["sacoche", "mains", "trou", "dos", "visage", "levres"]:
		tex[nom] = planche(CIN % ("cin_e2-rites-" + nom))
		if tex[nom] == null:
			return null
	var attenues := bool(Reglages.valeur(&"effets_attenues"))
	couche = couche_plein_ecran()
	var anim := Animation.new()
	anim.length = DUREE
	cle(anim, "Plans:visible", 0.0, true)
	if not AudioDirector.variantes_de(SON).is_empty():
		son(anim, 0.0, SON)

	var plans := [
		["Sacoche", "sacoche", "Mains", "mains", ZONE_MAINS, 3, MAINS, 0.0, P2, FOYER_SACOCHE, ZOOM_SACOCHE],
		["Trou", "trou", "Dos", "dos", ZONE_DOS, 2, DOS, P2, P3, FOYER_TROU, ZOOM_TROU],
		["Visage", "visage", "Levres", "levres", ZONE_LEVRES, 2, LEVRES, P3, DUREE, FOYER_VISAGE, ZOOM_VISAGE],
	]
	for p: Array in plans:
		var noeud := Node2D.new()
		noeud.name = p[0]
		noeud.add_child(sprite("Fond", tex[p[1]], Vector2.ZERO))
		noeud.add_child(sprite(p[2], tex[p[3]], p[4], p[5]))
		couche.add_child(noeud)
		var chemin := "Plans/" + String(p[0])
		var debut: float = p[7]
		var fin: float = p[8]
		cle(anim, chemin + ":visible", 0.0, debut == 0.0)
		if debut > 0.0:
			cle(anim, chemin + ":visible", debut, true)
		if fin < DUREE:
			cle(anim, chemin + ":visible", fin, false)
		for c: Array in p[6]:
			cle(anim, chemin + "/" + String(p[2]) + ":frame", c[0], c[1])
		avancee(anim, chemin, debut, fin, p[9], p[10], attenues)
	cle(anim, "Plans:visible", DUREE, false)
	return anim


## Lente avancée vers le foyer, de 1 à zoom ; un seul cadrage fixe en effets atténués.
static func avancee(anim: Animation, chemin: String, debut: float, fin: float, foyer: Vector2, zoom: float, attenues: bool) -> void:
	var n := roundi((fin - debut) / Cinematique.PAS)
	for k in n + 1:
		var u := float(k) / n
		var z := 1.0 if attenues else lerpf(1.0, zoom, u * u * (3.0 - 2.0 * u))
		cle(anim, chemin + ":scale", debut + k * Cinematique.PAS, Vector2.ONE * z)
		cle(anim, chemin + ":position", debut + k * Cinematique.PAS, (foyer - foyer * z).round())
		if attenues:
			return


func apres() -> void:
	if couche != null:
		couche.visible = false
