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
| `generer_timbres.py` | Timbres de dialogue sans mots, `vox_<personnage>_01..03.wav` |

```sh
mkdir -p /tmp/son && cd /tmp/son
python3 <repo>/tools/son/generer_ambiance_tranchee_mere.py .
python3 <repo>/tools/son/generer_lieux_tranchee_mere.py .
python3 <repo>/tools/son/generer_musique_tranchee_mere.py .
python3 <repo>/tools/son/generer_ambiance_village_cloches_muettes.py .
python3 <repo>/tools/son/generer_bruitages_etape_01.py <repo>/assets/audio
python3 <repo>/tools/son/generer_timbres.py <repo>/assets/audio
for f in amb_*.wav mus_*.wav; do ffmpeg -y -i "$f" -c:a libvorbis -q:a 6 "<repo>/assets/audio/${f%.wav}.ogg"; done
```

Chaque `amb_*.ogg` et `mus_*.ogg` doit garder `loop=true` dans son `.import` (vérifié par `tools/check_assets.py`).

Intention sonore, paliers de Lucidité et carte des lieux : https://claude.ai/artifact/KkoyTNTrb3wocb54uZ8ftS

## Épilogues de l'étape 7 : table lettre → fin

Les noms de fichiers restent neutres (règle du Game Director : aucun nom de fin dans un fichier vu par le joueur). La même lettre désigne la même fin pour les gravures du DA (`cin_epilogue_<lettre>`).

| Lettre | Fin | Le Cantique |
| --- | --- | --- |
| a | Le Battant | se résout tout bas ; le battant frappe une cloche muette |
| b | Le Dernier Pli, sacrifice | résolution pleine en ré majeur, tout revient |
| c | Le Dernier Pli, refus | la même résolution, puis les cloches sonnent (la seule fois du jeu), coupure nette |
| d | Le Quatorzième | l'harmonium seul manque d'air et se brise à la septième mesure |
| e | La Remontée | suspendu sur la, sans se poser |
