extends CinematiquePlans
## e6_chute_fissure (planches de la DA, tools/gen_cin_e6.py) : la terre se fend sous Tobie, il
## dévale la coulée de racines jusqu'à la pierre. Dessinée pour l'écran inversé de l'étape 6.
## Plan A, la clairière : fond cin_chute_01, 6 images de 600×560 (cin_chute_02, grille 3 × 2) en
##          (660, 300) : une tenue sur 0, la fente s'ouvre (1 à 5 à 10 i/s), une tenue sur 5.
## Plan B, sous la terre : fond cin_chute_03, Tobie en 6 images de 240×240 transparentes
##          (cin_chute_04, en ligne), posé par son centre sur CHEMIN (clés discrètes), puis une
##          tenue sur la dernière image, à quatre pattes.

const DOSSIER := "res://assets/graphics/cin/cin_chute_%02d.png"
## Le sol qui cède (bruitage du Sound Designer, sans emploi jusqu'ici), calé sur la fente.
const SON_FENTE := "sfx_sol_ceder"
const TENUE_DEBUT_A := 0.6
const TENUE_FIN_A := 0.6
const TENUE_FIN_B := 1.0
const DEMI_TOBIE := Vector2(120, 120)
## (instant depuis le début du plan B, image, centre x, centre y), repris de tools/gen_cin_e6.py.
const CHEMIN := [
	[0.0, 0, 330, 190], [0.3, 0, 440, 262], [0.6, 1, 560, 330], [0.8, 2, 660, 392],
	[1.0, 3, 760, 450], [1.2, 1, 860, 506], [1.4, 2, 960, 560], [1.6, 3, 1060, 616],
	[1.8, 1, 1160, 668], [2.0, 2, 1258, 716], [2.2, 3, 1350, 760], [2.4, 4, 1452, 790],
	[2.6, 5, 1500, 780],
]

var couche: CanvasLayer


func construire() -> Animation:
	var t: Array[Texture2D] = []
	for i in range(1, 5):
		t.append(planche(DOSSIER % i))
	if t.has(null):
		return null
	couche = couche_plein_ecran()
	var a := Node2D.new()
	a.name = "A"
	a.add_child(sprite("Fond", t[0], Vector2.ZERO))
	a.add_child(sprite("Fente", t[1], Vector2(660, 300), 3, 2))
	var b := Node2D.new()
	b.name = "B"
	b.add_child(sprite("Fond", t[2], Vector2.ZERO))
	b.add_child(sprite("Tobie", t[3], position_chemin(0), 6, 1))
	couche.add_child(a)
	couche.add_child(b)

	var anim := Animation.new()
	cle(anim, "Plans:visible", 0.0, true)
	cle(anim, "Plans/A:visible", 0.0, true)
	cle(anim, "Plans/B:visible", 0.0, false)
	cle(anim, "Plans/A/Fente:frame", 0.0, 0)
	if not AudioDirector.variantes_de(SON_FENTE).is_empty():
		son(anim, TENUE_DEBUT_A, SON_FENTE)
	var t_b := images(anim, "Plans/A/Fente", TENUE_DEBUT_A, 1, 5) - Cinematique.PAS + TENUE_FIN_A
	cle(anim, "Plans/A:visible", t_b, false)
	cle(anim, "Plans/B:visible", t_b, true)
	for k in CHEMIN.size():
		var etape: Array = CHEMIN[k]
		cle(anim, "Plans/B/Tobie:frame", t_b + float(etape[0]), etape[1])
		cle(anim, "Plans/B/Tobie:position", t_b + float(etape[0]), position_chemin(k))
	var fin: float = t_b + float(CHEMIN[-1][0]) + TENUE_FIN_B
	anim.length = snappedf(fin, Cinematique.PAS)
	cle(anim, "Plans:visible", anim.length, false)
	return anim


## Coin haut-gauche du sprite de Tobie pour la k-ième étape du chemin (posé par son centre).
static func position_chemin(k: int) -> Vector2:
	var etape: Array = CHEMIN[k]
	return Vector2(etape[2], etape[3]) - DEMI_TOBIE


func apres() -> void:
	if couche != null:
		couche.visible = false
