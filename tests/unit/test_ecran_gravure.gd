extends GutTest
## Écran gravure posé par EtapeBase : calque sous l'interface, papier de l'étape,
## tremblement coupé par le réglage effets_attenues.

const ETAPE_3 := preload("res://scenes/etapes/etape_03/etape_03.tscn")

var _etape: EtapeBase
var _attenues: bool


func before_each() -> void:
	_attenues = bool(Reglages.valeur(&"effets_attenues"))
	_etape = ETAPE_3.instantiate()
	add_child_autofree(_etape)
	await wait_process_frames(2)


func after_each() -> void:
	Reglages.changer(&"effets_attenues", _attenues)


func test_ecran_pose_une_seule_fois_sur_son_calque() -> void:
	var couche := _etape.get_node_or_null(EtapeBase.NOEUD_GRAVURE) as CanvasLayer
	assert_not_null(couche)
	assert_eq(couche.layer, EtapeBase.COUCHE_GRAVURE)
	assert_eq(_etape.ajouter_gravure(), _etape.materiau_gravure())
	var nb := 0
	for enfant in _etape.get_children():
		if enfant.name == EtapeBase.NOEUD_GRAVURE:
			nb += 1
	assert_eq(nb, 1)


func test_rect_plein_ecran_sans_capter_la_souris() -> void:
	var rect := _etape.get_node(EtapeBase.NOEUD_GRAVURE + "/Rect") as ColorRect
	assert_eq(rect.mouse_filter, Control.MOUSE_FILTER_IGNORE)
	assert_eq(rect.anchor_right, 1.0)
	assert_eq(rect.anchor_bottom, 1.0)


func test_papier_de_l_etape_3() -> void:
	var m := _etape.materiau_gravure()
	assert_eq(m.get_shader_parameter(&"couleur_papier"), Color("#E3D9BF"))


func test_interface_au_dessus_de_l_ecran() -> void:
	var interface := _etape.ajouter_interface()
	assert_not_null(interface)
	assert_gt(interface.layer, EtapeBase.COUCHE_GRAVURE)


func test_effets_attenues_coupe_le_tremblement() -> void:
	var m := _etape.materiau_gravure()
	Reglages.changer(&"effets_attenues", true)
	assert_eq(m.get_shader_parameter(&"amplitude_px"), 0.0)
	Reglages.changer(&"effets_attenues", false)
	assert_eq(m.get_shader_parameter(&"amplitude_px"), EtapeBase.AMPLITUDE_REPOS)
