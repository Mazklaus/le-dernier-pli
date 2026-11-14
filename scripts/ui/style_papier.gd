class_name StylePapier
extends RefCounted
## Style commun des plaques de papier (bulle, invite, HUD) : assets du DA (PR #18).

const ENCRE := Color("15130f")
const PAPIER := Color("e8e5da")
const LAVIS := Color("4a463d")
const MINE := Color("8c877a")
const ROUGE := Color("9b1c1c")

const POLICE_TITRE := "res://assets/fonts/IMFellEnglishSC-Regular.ttf"
const POLICE_TEXTE := "res://assets/fonts/Spectral-Regular.ttf"
const POLICE_ITALIQUE := "res://assets/fonts/Spectral-Italic.ttf"
const PLAQUE := "res://assets/graphics/ui/ui_plaque-papier.png"
const DOSSIER_UI := "res://assets/graphics/ui/"


## Plaque de papier au bord déchiré : StyleBoxTexture en 9 tranches. `bord` est la marge de
## texture (40 px conseillés par le DA, moins pour une petite plaque), `marge` celle du contenu.
static func plaque(marge: float = 24.0, bord: float = 40.0, marge_verticale: float = -1.0) -> StyleBoxTexture:
	var style := StyleBoxTexture.new()
	style.texture = load(PLAQUE) as Texture2D
	style.texture_margin_left = bord
	style.texture_margin_right = bord
	style.texture_margin_top = bord
	style.texture_margin_bottom = bord
	var mv := marge if marge_verticale < 0.0 else marge_verticale
	style.content_margin_left = marge
	style.content_margin_right = marge
	style.content_margin_top = mv
	style.content_margin_bottom = mv
	return style


static func police(chemin: String) -> Font:
	return load(chemin) as Font if ResourceLoader.exists(chemin) else null


## Icône UI du DA par nom court (« sacoche-pleine » → ui_sacoche-pleine.png).
static func icone(nom: String) -> Texture2D:
	var chemin := DOSSIER_UI + "ui_%s.png" % nom
	return load(chemin) as Texture2D if ResourceLoader.exists(chemin) else null
