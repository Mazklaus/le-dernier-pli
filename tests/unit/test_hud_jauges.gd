extends GutTest
## HUD des jauges : correspondances icônes/libellés, mise à jour sur les signaux de GameState,
## mode contextuel. Et le branchement des assets du DA dans la bulle et l'invite.

const SceneBulle := preload("res://scenes/ui/bulle_dialogue/bulle_dialogue.tscn")
const Dialogue := preload("res://scenes/bac_a_sable/bac_a_sable.dialogue")
const SceneInterface := preload("res://scenes/ui/interface_jeu/interface_jeu.tscn")

var _contextuel: Variant
var _chiffres: Variant


func before_all() -> void:
	_contextuel = Reglages.valeur(&"hud_contextuel")
	_chiffres = Reglages.valeur(&"valeurs_chiffrees")


func before_each() -> void:
	GameState.reinitialiser()


func after_all() -> void:
	GameState.reinitialiser()
	Reglages.changer(&"hud_contextuel", _contextuel)
	Reglages.changer(&"valeurs_chiffrees", _chiffres)


func _hud() -> HudJauges:
	var hud := HudJauges.new()
	add_child_autofree(hud)
	return hud


func test_icones_des_jauges() -> void:
	assert_eq(HudJauges.icone_jauge(GameState.VIVRES, 10, &"clair"), "sacoche-pleine")
	assert_eq(HudJauges.icone_jauge(GameState.VIVRES, 6, &"clair"), "sacoche-pleine")
	assert_eq(HudJauges.icone_jauge(GameState.VIVRES, 5, &"clair"), "sacoche-moitie")
	assert_eq(HudJauges.icone_jauge(GameState.VIVRES, 2, &"clair"), "sacoche-moitie")
	assert_eq(HudJauges.icone_jauge(GameState.VIVRES, 1, &"clair"), "sacoche-vide")
	assert_eq(HudJauges.icone_jauge(GameState.HUILE, 3, &"clair"), "lanterne-pleine")
	assert_eq(HudJauges.icone_jauge(GameState.HUILE, 1, &"clair"), "lanterne-faible")
	assert_eq(HudJauges.icone_jauge(GameState.HUILE, 0, &"clair"), "lanterne-eteinte")
	assert_eq(HudJauges.icone_jauge(GameState.LUCIDITE, 2, &"egare"), "oeil-egare")


func test_toutes_les_icones_existent() -> void:
	for nom: String in ["sacoche-pleine", "sacoche-moitie", "sacoche-vide", "lanterne-pleine",
			"lanterne-faible", "lanterne-eteinte", "oeil-clair", "oeil-trouble", "oeil-egare",
			"sceau-intact", "sceau-abime", "sceau-rechauffe", "sceau-ouvert", "carnet",
			"cout-vivres", "cout-huile", "cout-lucidite"]:
		assert_not_null(StylePapier.icone(nom), nom)
	assert_not_null(StylePapier.police(StylePapier.POLICE_ITALIQUE))
	assert_not_null(StylePapier.plaque().texture)


func test_libelles_sans_chiffre_de_lucidite() -> void:
	assert_eq(HudJauges.libelle_jauge(GameState.VIVRES, 0, &"clair", false), "Affamé")
	assert_eq(HudJauges.libelle_jauge(GameState.VIVRES, 3, &"clair", false), "Vivres")
	assert_eq(HudJauges.libelle_jauge(GameState.HUILE, 0, &"clair", false), "Éteinte")
	assert_eq(HudJauges.libelle_jauge(GameState.LUCIDITE, 5, &"trouble", false), "Trouble")
	assert_eq(HudJauges.libelle_jauge(GameState.LUCIDITE, 2, &"egare", false), "Égaré")
	assert_eq(HudJauges.libelle_jauge(GameState.LUCIDITE, 2, &"egare", true), "Perdu")


func test_icone_du_sceau() -> void:
	assert_eq(HudJauges.icone_sceau(), "sceau-intact")
	GameState.sceau_abime = true
	assert_eq(HudJauges.icone_sceau(), "sceau-abime")
	GameState.sceau_ouvert = true
	assert_eq(HudJauges.icone_sceau(), "sceau-ouvert")


func test_le_hud_suit_les_jauges() -> void:
	var hud := _hud()
	GameState.modifier_jauge(GameState.VIVRES, -10)
	assert_eq((hud._batons[GameState.VIVRES] as Batons).valeur, 0)
	assert_eq((hud._libelles[GameState.VIVRES] as Label).text, "Affamé")
	assert_eq((hud._icones[GameState.VIVRES] as TextureRect).texture, StylePapier.icone("sacoche-vide"))
	GameState.modifier_jauge(GameState.LUCIDITE, -5)
	assert_eq((hud._libelles[GameState.LUCIDITE] as Label).text, "Égaré")


func test_valeurs_chiffrees() -> void:
	Reglages.changer(&"valeurs_chiffrees", false)
	var hud := _hud()
	assert_false((hud._chiffres[GameState.HUILE] as Label).visible)
	Reglages.changer(&"valeurs_chiffrees", true)
	assert_true((hud._chiffres[GameState.HUILE] as Label).visible)
	assert_eq((hud._chiffres[GameState.HUILE] as Label).text, "4 / 6")
	assert_false(hud._chiffres.has(GameState.LUCIDITE), "jamais de chiffre pour la Lucidité")


func test_mode_contextuel_s_efface_sauf_jauge_basse() -> void:
	Reglages.changer(&"hud_contextuel", true)
	var hud := _hud()
	hud._estomper()
	await wait_seconds(HudJauges.DUREE_FONDU + 0.2)
	assert_almost_eq(hud.modulate.a, 0.0, 0.01)
	GameState.modifier_jauge(GameState.HUILE, -3)
	await wait_seconds(HudJauges.DUREE_FONDU + 0.2)
	assert_almost_eq(hud.modulate.a, 1.0, 0.01, "un changement fait revenir le HUD")
	hud._estomper()
	await wait_seconds(HudJauges.DUREE_FONDU + 0.2)
	assert_almost_eq(hud.modulate.a, 1.0, 0.01, "huile à 1 : le HUD reste")


func test_batons_bornes() -> void:
	var b := Batons.new()
	add_child_autofree(b)
	b.maximum = 6
	b.valeur = 9
	assert_eq(b.valeur, 6)
	assert_gt(b.custom_minimum_size.x, 0.0)


func test_l_interface_contient_le_hud() -> void:
	var interface: InterfaceJeu = add_child_autofree(SceneInterface.instantiate())
	assert_not_null(interface.hud)
	assert_true(interface.hud is HudJauges)


func test_bulle_polices_plaque_et_icones_de_cout() -> void:
	var bulle: Node = add_child_autofree(SceneBulle.instantiate())
	assert_not_null(bulle.police_replique, "Spectral italique par défaut")
	assert_eq(bulle.police_replique.resource_path, StylePapier.POLICE_ITALIQUE)
	assert_true(bulle._plaque.get_theme_stylebox(&"panel") is StyleBoxTexture, "plaque de papier")
	bulle.start(Dialogue, "couts")
	await wait_process_frames(3)
	bulle._replique.skip_typing()
	await wait_process_frames(3)
	var icones: Array[Node] = bulle._options.find_children("*", "TextureRect", true, false)
	assert_gt(icones.size(), 0, "les coûts s'affichent en icône")
	assert_eq((icones[0] as TextureRect).texture, StylePapier.icone("cout-vivres"))


func test_invite_en_plaque_de_papier() -> void:
	var invite := InviteInteraction.new()
	add_child_autofree(invite)
	assert_true(invite.get_theme_stylebox(&"panel") is StyleBoxTexture)
	assert_not_null(invite.police)


func test_pas_de_traduction_de_disposition_sans_ecran_ni_sur_le_web() -> void:
	# En CI (headless), et sur le web (#23), le glyphe vient de la touche physique.
	assert_false(InviteInteraction.disposition_disponible())
	assert_eq(InviteInteraction.glyphe_action(&"interagir"), "E")


func test_retenu_le_hud_ne_s_efface_pas() -> void:
	Reglages.changer(&"hud_contextuel", true)
	var hud := _hud()
	hud.retenir(true)
	hud._estomper()
	await wait_seconds(HudJauges.DUREE_FONDU + 0.2)
	assert_almost_eq(hud.modulate.a, 1.0, 0.01)
	hud.retenir(false)
	hud._estomper()
	await wait_seconds(HudJauges.DUREE_FONDU + 0.2)
	assert_almost_eq(hud.modulate.a, 0.0, 0.01, "relâché : le mode contextuel reprend")


func test_la_bulle_retient_le_hud_pendant_un_choix_avec_couts() -> void:
	var hud := _hud()
	var bulle: Node = add_child_autofree(SceneBulle.instantiate())
	bulle.start(Dialogue, "couts")
	await wait_process_frames(3)
	bulle._replique.skip_typing()
	await wait_process_frames(3)
	assert_true(hud._retenu, "options avec coûts : HUD retenu")
	bulle.choisir(0)
	await wait_process_frames(3)
	assert_false(hud._retenu, "choix fait : HUD relâché")


func test_options_numerotees_avec_un_point() -> void:
	var bulle: Node = add_child_autofree(SceneBulle.instantiate())
	bulle.start(Dialogue, "couts")
	await wait_process_frames(3)
	bulle._replique.skip_typing()
	await wait_process_frames(3)
	var etiquettes: Array[Node] = bulle._options.find_children("*", "Label", true, false)
	assert_eq((etiquettes[0] as Label).text, "1.")


func test_debug_force_le_cout_faux_a_l_egare() -> void:
	GameState.modifier_jauge(GameState.LUCIDITE, -5)
	assert_eq(GameState.palier, GameState.EGARE)
	GameState.debug_forcer_cout_faux = true
	var couts: Array = [{&"vivres": 1}, {&"huile": 1}]
	for essai in 20:
		var affiches := GameState.couts_affiches_rencontre(couts)
		assert_true(affiches.any(func(a: Dictionary) -> bool: return a["cout_faux"]), "coût faux à chaque tirage")
		assert_eq(affiches.filter(func(a: Dictionary) -> bool: return a["cout_douteux"]).size(), 2, "coût faux + leurre")
	GameState.debug_forcer_cout_faux = false


func test_icone_et_chiffre_serres() -> void:
	var bulle: Node = add_child_autofree(SceneBulle.instantiate())
	bulle.start(Dialogue, "couts")
	await wait_process_frames(3)
	bulle._replique.skip_typing()
	await wait_process_frames(3)
	var icone: TextureRect = bulle._options.find_children("*", "TextureRect", true, false)[0]
	var signe := icone.get_parent() as HBoxContainer
	assert_eq(signe.get_theme_constant(&"separation"), 6)
	assert_eq(signe.get_child_count(), 2)


func test_bavure_forcee_deux_taches_differentes() -> void:
	GameState.modifier_jauge(GameState.LUCIDITE, -5)
	GameState.debug_forcer_cout_faux = true
	var bulle: Node = add_child_autofree(SceneBulle.instantiate())
	bulle.start(Dialogue, "couts")
	await wait_process_frames(3)
	bulle._replique.skip_typing()
	await wait_process_frames(3)
	GameState.debug_forcer_cout_faux = false
	var taches: Array[Node] = bulle._options.find_children("Tache", "TextureRect", true, false)
	assert_eq(taches.size(), 2, "une tache sous chacun des deux chiffres qui bavent")
	if taches.size() == 2:
		assert_not_null((taches[0] as TextureRect).texture)
		var t0 := (taches[0] as TextureRect).texture
		var t1 := (taches[1] as TextureRect).texture
		if t0 is AtlasTexture and t1 is AtlasTexture:
			assert_ne((t0 as AtlasTexture).atlas, (t1 as AtlasTexture).atlas, "variantes différentes")
		assert_true((taches[0] as TextureRect).show_behind_parent)
	for icone: Node in bulle._options.find_children("*", "TextureRect", true, false):
		if icone.name != "Tache":
			assert_eq((icone as TextureRect).modulate, Color.WHITE, "le glyphe de la jauge reste net")


func test_tache_reduite_sous_le_chiffre() -> void:
	GameState.modifier_jauge(GameState.LUCIDITE, -5)
	GameState.debug_forcer_cout_faux = true
	var bulle: Node = add_child_autofree(SceneBulle.instantiate())
	bulle.start(Dialogue, "couts")
	await wait_process_frames(3)
	bulle._replique.skip_typing()
	await wait_process_frames(3)
	GameState.debug_forcer_cout_faux = false
	var tache: TextureRect = bulle._options.find_children("Tache", "TextureRect", true, false)[0]
	var chiffre := tache.get_parent() as Label
	var taille := float(chiffre.get_theme_font_size(&"font_size"))
	assert_almost_eq(tache.size.y, roundf(taille * 0.5), 0.5, "moitié du chiffre, ~12 px à 1080")
	assert_true(tache.texture is AtlasTexture, "sprite recadré sur sa zone utile")
	if tache.texture is AtlasTexture:
		assert_lt((tache.texture as AtlasTexture).region.size.x, 32.0)
	assert_eq(chiffre.get_theme_color(&"font_color"), StylePapier.ENCRE, "chiffre qui bave en encre pleine")
	assert_gt(tache.position.y, chiffre.size.y / 2.0, "sous le milieu du chiffre")



func test_chiffres_de_cout_normaux_en_lavis() -> void:
	var bulle: Node = add_child_autofree(SceneBulle.instantiate())
	bulle.start(Dialogue, "couts")
	await wait_process_frames(3)
	bulle._replique.skip_typing()
	await wait_process_frames(3)
	var icone: TextureRect = bulle._options.find_children("*", "TextureRect", true, false)[0]
	var chiffre := icone.get_parent().get_child(1) as Label
	assert_eq(chiffre.get_theme_color(&"font_color"), StylePapier.LAVIS)
