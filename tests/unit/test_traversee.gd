extends GutTest
## Traversée physique de chaque étape (QA, #128) : le messager doit pouvoir atteindre chaque
## Interactif (rencontre, détail, passage) en marchant, sans saut, depuis un point d'arrivée
## de son niveau (départ de l'étape ou arrivée d'un Passage). Toutes les rencontres sont
## marquées vues, donc les Verrous sont ouverts.
##
## Depuis chaque point d'arrivée, on marche à gauche puis à droite jusqu'à être arrêté :
## cela donne l'intervalle atteignable sur ce sol. Un Interactif est atteint si un
## intervalle du même niveau (même hauteur à NIVEAU_Y près) passe à moins du rayon
## d'interaction de lui.

const VITESSE_TEST := 800.0
const NIVEAU_Y := 300.0
const PAS_MAX := 1200
const IMMOBILE := 8


func before_each() -> void:
	GameState.reinitialiser()


func after_each() -> void:
	Input.action_release(&"deplacer_gauche")
	Input.action_release(&"deplacer_droite")
	GameState.reinitialiser()


func _etapes_existantes() -> Array[int]:
	var liste: Array[int] = []
	for numero in range(1, SceneRouter.NB_ETAPES + 1):
		if SceneRouter.etape_existe(numero):
			liste.append(numero)
	return liste


## Marche dans une direction jusqu'à être arrêté ; renvoie l'abscisse atteinte.
func _marcher(messager: Messager, action: StringName) -> float:
	Input.action_press(action)
	var dernier := messager.global_position.x
	var immobile := 0
	for i in PAS_MAX:
		await wait_physics_frames(1)
		var x := messager.global_position.x
		immobile = immobile + 1 if absf(x - dernier) < 0.5 else 0
		dernier = x
		if immobile >= IMMOBILE:
			break
	Input.action_release(action)
	await wait_physics_frames(1)
	return messager.global_position.x


func test_chaque_interactif_est_atteignable_en_marchant() -> void:
	var echecs: Array[String] = []
	for numero in _etapes_existantes():
		GameState.reinitialiser()
		var etape := (load(SceneRouter.chemin_etape(numero)) as PackedScene).instantiate() as EtapeBase
		add_child(etape)
		await wait_physics_frames(2)
		var interactifs: Array[Interactif] = []
		for n in etape.find_children("*", "", true, false):
			if n is Interactif and not interactifs.has(n):
				interactifs.append(n as Interactif)
				if n is DeclencheurDialogue:
					GameState.marquer_rencontre_vue((n as DeclencheurDialogue).rencontre_id)
				elif n is Passage and (n as Passage).rencontre_requise != &"":
					GameState.marquer_rencontre_vue((n as Passage).rencontre_requise)
		for n in etape.find_children("*", "", true, false):
			if n is Verrou:
				GameState.marquer_rencontre_vue((n as Verrou).rencontre)
		await wait_physics_frames(2)
		var messager := etape.trouver_messager()
		messager.vitesse = VITESSE_TEST
		messager.bloque = false
		# Points d'arrivée : position de départ et arrivée de chaque Passage.
		var departs: Array[Vector2] = [messager.global_position]
		for i in interactifs:
			if i is Passage:
				var a := (i as Passage).trouver_arrivee()
				if a != null and not departs.has(a.global_position):
					departs.append(a.global_position)
		var intervalles: Array[Vector3] = []  # (x_min, x_max, y)
		for d in departs:
			messager.global_position = d + Vector2(0, -8)
			messager.velocity = Vector2.ZERO
			await wait_physics_frames(3)
			var gauche := await _marcher(messager, &"deplacer_gauche")
			var droite := await _marcher(messager, &"deplacer_droite")
			intervalles.append(Vector3(minf(gauche, d.x), maxf(droite, d.x), d.y))
		for i in interactifs:
			var p := i.global_position
			var atteint := false
			for iv in intervalles:
				if absf(p.y - iv.z) <= NIVEAU_Y and p.x >= iv.x - Messager.RAYON_INTERACTION \
						and p.x <= iv.y + Messager.RAYON_INTERACTION:
					atteint = true
					break
			if not atteint:
				echecs.append("étape %d : %s (x %d) hors d'atteinte" % [numero, etape.get_path_to(i), int(p.x)])
		# Une seule étape à la fois : sinon leurs collisions se superposent.
		etape.queue_free()
		await wait_physics_frames(2)
	assert_eq(echecs.size(), 0, "Interactifs inatteignables en marchant :\n%s" % "\n".join(echecs))
