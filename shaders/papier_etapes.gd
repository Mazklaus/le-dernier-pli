## Valeurs du shader papier pour les 7 étapes (planche de style du DA, section VI).
## Usage : PapierEtapes.appliquer(materiau_papier, GameState.etape)
class_name PapierEtapes
extends RefCounted

const ETAPES := {
	1: {"papier": Color("#E8E5DA"), "encre": Color("#15130F"), "grain": 0.05},  # Tranchée-Mère
	2: {"papier": Color("#D9D8CF"), "encre": Color("#15130F"), "grain": 0.06},  # No Man's Land
	3: {"papier": Color("#E3D9BF"), "encre": Color("#15130F"), "grain": 0.04},  # Village aux cloches muettes
	4: {"papier": Color("#DED3BD"), "encre": Color("#15130F"), "grain": 0.07},  # Hôpital des Recousus
	5: {"papier": Color("#2A2721"), "encre": Color("#E8E5DA"), "grain": 0.08},  # Forêt de Croix (inversion)
	6: {"papier": Color("#15130F"), "encre": Color("#E8E5DA"), "grain": 0.09},  # Cathédrale enterrée
	7: {"papier": Color("#F7F6F1"), "encre": Color("#15130F"), "grain": 0.02},  # Le Destinataire
}


static func appliquer(materiau: ShaderMaterial, etape: int) -> void:
	var v: Dictionary = ETAPES.get(clampi(etape, 1, 7))
	materiau.set_shader_parameter(&"couleur_papier", v["papier"])
	materiau.set_shader_parameter(&"couleur_encre", v["encre"])
	materiau.set_shader_parameter(&"grain", v["grain"])
