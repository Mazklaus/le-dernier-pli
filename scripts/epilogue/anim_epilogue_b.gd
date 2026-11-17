extends AnimationEpilogue
## Épilogue « Le Dernier Pli », il reste (lettre b, tribut). Planche de la DA validée par le GD le
## 17/11 (direction-artistique/epilogues/planche_dernier_pli.png) : 32 s, quatre plans, une ligne
## par plan. Presque tout est réemployé : la table de e7_moule_brise, l'abri du sergent, le parapet
## de e1_sortie_tranchee ; nouveau : la patère vide, la cendre, la cloche au nom gravé
## (tools/gen_cin_epilogues_anim.py). Le bandeau du texte couvre l'écran sous y 790 : les plans
## faits pour 1080 px de haut sont remontés.

const CIN := "res://assets/graphics/cin/%s.png"
const ABRI := "res://assets/graphics/env/e1/env_e1_plan3_abri-sergent_01.png"
const DUREE := 32.0
const LIGNES: Array[float] = [0.5, 8.5, 16.5, 24.5]
## P1 : la cire figée (image 5 de cin_moule_02 en (560, 480)), remontée sous le bandeau.
const MONTEE_TABLE := -250.0
const MOULE := Vector2(980, 700)
## P2 : la patère, entre deux poteaux de l'abri.
const PATERE := Vector2(1150, 420)
const MONTEE_ABRI := -150.0


func construire() -> Animation:
	var tex := {}
	for nom in ["cin_moule_01", "cin_moule_02", "cin_sortie_01", "cin_epi-b-patere", "cin_epi-b-cendre", "cin_epi-b-nom"]:
		tex[nom] = planche(CIN % nom)
	tex["abri"] = planche(ABRI)
	for t: Variant in tex.values():
		if t == null:
			return null
	temps_lignes = LIGNES
	var anim := Animation.new()
	anim.length = DUREE

	# P1, 0 à 8 s : « Il fut le dernier. » La table, la cire figée, une poussée lente.
	var p1 := plan(anim, "P1", 0.0, 8.0)
	var table := Node2D.new()
	table.name = "Table"
	p1.add_child(table)
	table.add_child(sprite("Fond", tex["cin_moule_01"], Vector2.ZERO))
	var moule := sprite("Moule", tex["cin_moule_02"], Vector2(560, 480), 3, 2)
	moule.frame = 5
	table.add_child(moule)
	pousser(anim, "Cadre/P1/Table", 0.0, 8.0, MOULE, 1.0, 1.12)
	cle(anim, "Cadre/P1:position", 0.0, Vector2(0, MONTEE_TABLE))

	# P2, 8 à 16 s : « aucun garçon ne reçut plus de sacoche. » L'abri, la patère vide, un
	# panoramique vers la droite.
	var p2 := plan(anim, "P2", 8.0, 16.0)
	var abri := Node2D.new()
	abri.name = "Abri"
	p2.add_child(abri)
	abri.add_child(sprite("Fond", tex["abri"], Vector2.ZERO))
	abri.add_child(sprite("Patere", tex["cin_epi-b-patere"], PATERE))
	mouvement(anim, "Cadre/P2/Abri:position", 8.0, 16.0, Vector2(0, MONTEE_ABRI), Vector2(-128, MONTEE_ABRI))

	# P3, 16 à 24 s : « Ce que la Cendre dirait… » Le parapet vide à l'aube, la cendre qui tombe.
	var p3 := plan(anim, "P3", 16.0, 24.0)
	p3.add_child(sprite("Fond", tex["cin_sortie_01"], Vector2(0, -120)))
	var cendre := sprite("Cendre", tex["cin_epi-b-cendre"], Vector2.ZERO, 1, 3)
	cendre.scale = Vector2(2, 2)
	p3.add_child(cendre)
	boucle(anim, "Cadre/P3/Cendre", 16.0, 24.0, [0, 1, 2], 0.3)

	# P4, 24 à 32 s : « une cloche portait un nom gravé, et ne sonnait pas. » Poussée vers le
	# nom, puis le papier revient.
	var p4 := plan(anim, "P4", 24.0, DUREE)
	var cloche := Node2D.new()
	cloche.name = "Cloche"
	p4.add_child(cloche)
	cloche.add_child(sprite("Fond", tex["cin_epi-b-nom"], Vector2.ZERO))
	pousser(anim, "Cadre/P4/Cloche", 24.0, 30.0, Vector2(960, 520), 1.0, 1.35)
	var papier := ColorRect.new()
	papier.name = "Papier"
	papier.color = StylePapier.PAPIER
	papier.size = Vector2(1920, 1080)
	papier.mouse_filter = Control.MOUSE_FILTER_IGNORE
	p4.add_child(papier)
	# transparent dès l'entrée du plan : sans clé avant 30 s, le papier restait opaque
	cle(anim, "Cadre/P4/Papier:modulate", 24.0, Color(1, 1, 1, 0))
	for k in 21:
		cle(anim, "Cadre/P4/Papier:modulate", 30.0 + k * PAS, Color(1, 1, 1, clampf((k - 1) / 18.0, 0.0, 1.0)))
	return anim
