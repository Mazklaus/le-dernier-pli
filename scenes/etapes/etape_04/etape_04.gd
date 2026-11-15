extends EtapeBase
## Étape 4 : l'Hôpital des Recousus.
## Maquette grise du Level Designer : une descente fermée, où l'on est conduit. Porche (surface),
## salle (-1, avec la lingerie en seul écart), atelier d'Anselme (-2), escalier des ex-voto,
## crypte (-3, zone sombre courte ouverte par e4_crypte), puis l'escalier de service remonte
## d'un coup à une porte latérale (e4_benediction, fin d'étape). Aucun passage de retour, sauf
## entre la lingerie et la salle ; chaque porte s'ouvre sur la rencontre qui précède.
## Plan de référence : https://claude.ai/artifact/JPeGYS2vfSZivP9DcWvQyM

## Le messager arrive du village par la rue du porche.
const POINT_DE_DEPART: StringName = &"entree_porche"


func _ready() -> void:
	super()
	var messager := trouver_messager()
	var depart := find_child(String(POINT_DE_DEPART), true, false) as Marker2D
	if messager != null and depart != null:
		messager.global_position = depart.global_position
