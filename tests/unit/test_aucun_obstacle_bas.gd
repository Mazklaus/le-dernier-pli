extends GutTest
## Tobie ne saute pas : un corps solide bas posé au sol (une banquette, une caisse) le bloque
## pour de bon (bug #128, banquette du périscope de l'étape 1). Hors sol, plafond et verrous,
## tout solide d'une étape doit être un mur pleine hauteur, jamais une marche.

const ETAPES: Array[String] = [
	"res://scenes/etapes/etape_01/etape_01.tscn", "res://scenes/etapes/etape_02/etape_02.tscn",
	"res://scenes/etapes/etape_03/etape_03.tscn", "res://scenes/etapes/etape_04/etape_04.tscn",
	"res://scenes/etapes/etape_05/etape_05.tscn", "res://scenes/etapes/etape_06/etape_06.tscn",
	"res://scenes/etapes/etape_07/etape_07.tscn",
]
const HAUTEUR_MUR_MIN := 400.0


func test_aucun_solide_bas_ne_barre_le_chemin() -> void:
	for chemin in ETAPES:
		var etape: Node = (load(chemin) as PackedScene).instantiate()
		add_child_autofree(etape)
		for n in etape.find_children("*", "StaticBody2D", true, false):
			if n is Verrou or n is VerrouRetour or n.name in [&"Sol", &"Plafond"]:
				continue
			for forme in n.find_children("*", "CollisionShape2D", false, false):
				var rect := (forme as CollisionShape2D).shape as RectangleShape2D
				if rect != null:
					assert_gte(rect.size.y, HAUTEUR_MUR_MIN,
						"%s : %s est un obstacle bas infranchissable" % [chemin.get_file(), etape.get_path_to(n)])
