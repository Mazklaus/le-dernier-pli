# Générateurs audio (Sound Designer)

Tout le son de l'étape 1 est procédural : aucune ressource externe, donc aucun souci de droits. Graines fixes, la sortie est reproductible.

Dépendances : Python 3, `numpy`, `scipy`, et `ffmpeg` (avec libvorbis) pour la conversion OGG.

| Script | Produit |
| --- | --- |
| `generer_ambiance_tranchee_mere.py` | Couches globales de l'étape 1, boucles de 80 s : `surface-lit`, `surface-voix`, `autre` (plus `reel` et une démo de la Lucidité, non versionnées) |
| `generer_lieux_tranchee_mere.py` | Boucles mono de 20 s des 10 lieux du plan (`couchette`, `cantine`, `chapelle`…) |
| `generer_musique_tranchee_mere.py` | « Le Cantique du Pli », version étape 1 (chœur d'hommes fatigué + harmonium), boucle de 80 s : `mus_tranchee-mere_theme` |
| `generer_bruitages_etape_01.py` | Bruitages et sons d'interface de l'étape 1, `sfx_<famille>_<action>_NN.wav` (pas, échelle, passages, lanterne, sceau, pli, carnet, interface) |
| `generer_ambiance_no_mans_land.py` | Étape 2 : `surface`, `autre`, `fils` (positionnel, groupe `son_du_noir`), `brouillard`, `trou-obus`, `boyau-detour`, `poste`, et `mus_no-mans-land_cantique-lointain` (dérivé de `mus_tranchee-mere_theme`, passer son chemin en 2e argument) |
| `generer_ambiance_village_cloches_muettes.py` | Étape 3 : `jour`, `nuit`, `autre` (80 s, fondu croisé jour/nuit dans AudioDirector), lieux `verger`, `place`, `maison-ilde`, `clocher`, `chambre`, `chemin-nuit`, `chemin-aube`, et les musiques `mus_village-cloches-muettes_noce` (diégétique, 32 s) et `_procession` |
| `generer_ambiance_hopital_recousus.py` | Étape 4 : `hopital`, `autre` (80 s), lieux `porche`, `salle`, `lingerie`, `atelier`, `escalier`, `crypte` (groupe `son_du_noir`), `escalier-service`, `porte-laterale`, et `sfx_porte_fermer_01..03` (2e argument : dossier des bruitages) |
| `generer_epilogues_destinataire.py` | Étape 7 : `salle`, `autre` (80 s, bourdon sans attaque) et les cinq épilogues du Cantique `mus_destinataire_fin-a` à `fin-e`, joués sans boucle par `AudioDirector.jouer_epilogue` |
| `generer_bruitages_cinematiques.py` | Bruitages des gestes et des cinématiques courtes (directive du 15/11), `sfx_<famille>_<action>_01..03.wav` : voir la table ci-dessous |
| `generer_ambiance_foret_cathedrale.py` | Étapes 5 et 6 : `foret-de-croix_{foret,autre}` et lieux `oree`, `boucle`, `campement`, `cimetiere`, `clairiere` ; `cathedrale-enterree_{profondeur,autre}` et lieux `fissure`, `nef`, `village`, `niche-veilleur`, `seuil` ; `sfx_boucle_raccord_01` (le même oiseau et le même craquement à chaque tour) ; `mus_cathedrale-enterree_tablee` (la noce de l'étape 3 à l'envers, plus lente et plus chaude ; 3e argument : `mus_village-cloches-muettes_noce`) |
| `generer_timbres.py` | Timbres de dialogue sans mots, `vox_<personnage>_01..03.wav` |

```sh
mkdir -p /tmp/son && cd /tmp/son
python3 <repo>/tools/son/generer_ambiance_tranchee_mere.py .
python3 <repo>/tools/son/generer_lieux_tranchee_mere.py .
python3 <repo>/tools/son/generer_musique_tranchee_mere.py .
python3 <repo>/tools/son/generer_ambiance_village_cloches_muettes.py .
python3 <repo>/tools/son/generer_bruitages_etape_01.py <repo>/assets/audio
python3 <repo>/tools/son/generer_timbres.py <repo>/assets/audio
python3 <repo>/tools/son/encoder_ogg.py . <repo>/assets/audio   # amb_ q2 (mono si fausse stéréo), mus_ q3 mono
```

Budget du build web : 60 Mo. `encoder_ogg.py` fixe la qualité : `amb_` en Vorbis q2 (~80-96 kbit/s), mono quand la stéréo n'est qu'une copie retardée ; `mus_` en q3 mono (depuis le 15/11, environ 2,3 Mo gagnés), mélange L+R remonté à l’énergie de la stéréo. Chaque `amb_*.ogg` et `mus_*.ogg` doit garder `loop=true` dans son `.import` (vérifié par `tools/check_assets.py`).

Intention sonore, paliers de Lucidité et carte des lieux : https://claude.ai/artifact/KkoyTNTrb3wocb54uZ8ftS

## Épilogues de l'étape 7 : table lettre → fin

Les noms de fichiers restent neutres (règle du Game Director : aucun nom de fin dans un fichier vu par le joueur). La même lettre désigne la même fin pour les gravures du DA (`cin_epilogue_<lettre>`).

| Lettre | Fin | Le Cantique |
| --- | --- | --- |
| a | Le Battant | se résout tout bas ; le battant frappe une cloche muette |
| b | Le Dernier Pli, sacrifice | résolution pleine en ré majeur, tout revient |
| c | Le Dernier Pli, refus | calée sur la ciné de 36 s (planche DA du 17/11) : la grande cloche frappe toutes les 1,8 s, la cire claque et les petites cloches entrent, la volée traverse galeries, forêt, champs et tranchée, revient sous la main, s’espace, puis seule la résonance lointaine tient jusqu’à 40 s ; seule mus_ en stéréo (STEREO_GARDEE) |
| d | Le Quatorzième | l'harmonium seul manque d'air et se brise à la septième mesure |
| e | La Remontée | suspendu sur la, sans se poser |

## Gestes et cinématiques : quel son sur quel moment

Dans une piste de méthode de l'AnimationPlayer (ou depuis un geste de dialogue) : `AudioDirector.jouer_variante("<base>")`, à l'image où le geste se produit. Les cloches ne sonnent pas : `sfx_cloche_souffle` n'a pas d'attaque.

| Étape | Moment | Type | Sons (dans l'ordre) |
| --- | --- | --- | --- |
| 1 | L'officier remet le pli | Ciné | `sfx_pli_tendre` (main tendue → poitrine) |
| 1 | Adieu de Jacquot, couverture | Anim | sifflet = `vox_jacquot_*` ; `sfx_couverture_tomber` |
| 1 | Sortie de tranchée | Ciné | `sfx_echelle_monter` en boucle, puis `sfx_parapet_franchir` quand la caméra le perd |
| 2 | Brisse réchauffe la cire | Anim | `sfx_sceau_rechauffer` |
| 2 | Le Mort indique | Anim | `sfx_mort_bras` à l'image où le bras se lève |
| 2 | Le terrain se referme | Anim | `sfx_terre_ebouler` |
| 3 | La noce | Anim | rien : la musique `mus_village-cloches-muettes_noce` joue déjà sur la place |
| 3 | La procession de nuit | Ciné | rien : `mus_village-cloches-muettes_procession` (lieux_musique) |
| 3 | Le sonneur | Anim | `sfx_corde_tirer` à chaque traction |
| 4 | La greffe de l'œil | Ciné | `sfx_aiguille_coudre` (le fil passe trois fois, hors champ), puis `sfx_greffe_fausse-note` à la coupe au noir (un fredonnement bouche cousue, un quart de ton trop bas, coupé à 0,6 s au retour de l’image) |
| 4 | Les saints qui respirent | Anim | rien : l'émetteur `amb_hopital-recousus_crypte` (son_du_noir) |
| 4 | La bénédiction | Anim | `sfx_cendre_front` |
| 5 | L'entaille et le retour | Anim | `sfx_lame_entailler` |
| 5 | L'Autre Tobie | Ciné | rien de neuf : la couche autre de l'étape monte d'elle-même |
| 5 | Graver son nom | Anim | `sfx_lame_graver`, une fois par lettre |
| 6 | La chute dans la fissure | Ciné | `sfx_sol_ceder`, puis `sfx_lanterne_rouler` |
| 6 | Éloi éclaire | Anim | `sfx_lampe_approcher` |
| 6 | L'éboulement | Ciné | `sfx_voute_effondrer`, puis silence |
| 7 | La descente sous la grande cloche | Ciné | `sfx_cloche_souffle` (la cloche respire, elle ne sonne pas) |
| 7 | L'ouverture du sceau | Ciné | `sfx_sceau_ouvrir`, puis `sfx_pli_deplier` |
| Toutes | Lecture d'une ligne du pli | Anim | `sfx_sceau_rechauffer` puis `sfx_pli_lire` |
