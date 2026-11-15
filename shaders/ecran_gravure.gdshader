// Écran gravure : UNE seule passe plein écran (une seule copie d'écran par
// image, important sur WebGL2 bas de gamme) qui fait, dans l'ordre :
//   1. le trait tremblé : UV déformé par un bruit, 3 variantes à 6 images/s ;
//   2. un seul échantillonnage de l'écran à cet UV ;
//   3. le remappage papier/encre de l'étape (inversion possible), le grain et la teinte ;
//   4. le rouge et la couleur d'accent, préservés exactement (sans grain ni teinte).
// À poser sur un ColorRect plein écran dans un CanvasLayer au-dessus du monde
// et sous l'interface. Compatible renderer Compatibility (GLES3 / WebGL2).
// Valeurs par étape : scripts/rendu/papier_etapes.gd.
shader_type canvas_item;

uniform sampler2D ecran : hint_screen_texture, filter_linear;

group_uniforms trait_tremble;
// Amplitude en pixels écran à 1080p. 1.5 = repos ; monter quand la Lucidité baisse.
uniform float amplitude_px : hint_range(0.0, 12.0) = 1.5;
// Taille des ondulations, en pixels à 1080p.
uniform float echelle_px : hint_range(4.0, 200.0) = 38.0;
uniform float images_par_seconde : hint_range(1.0, 24.0) = 6.0;
uniform int variantes : hint_range(1, 8) = 3;

group_uniforms papier;
uniform vec4 couleur_papier : source_color = vec4(0.910, 0.898, 0.855, 1.0); // #E8E5DA
uniform vec4 couleur_encre : source_color = vec4(0.082, 0.075, 0.059, 1.0);  // #15130F
uniform float grain : hint_range(0.0, 0.3) = 0.05;
// Taille du grain en pixels à 1080p.
uniform float taille_grain_px : hint_range(1.0, 8.0) = 1.5;
// Le grain ne change que quelques fois par seconde : papier, pas pellicule.
uniform float grain_par_seconde : hint_range(0.0, 24.0) = 6.0;

// Teinte de l'éclairage (nuit, par lieu). Multiplie tout sauf le rouge et l'accent,
// qui restent exacts : seul rouge_efface a le droit d'atténuer le rouge.
uniform vec4 teinte : source_color = vec4(1.0, 1.0, 1.0, 1.0);

group_uniforms rouge;
// Reste exactement cette couleur à toutes les étapes (règle du Game Director).
uniform vec4 couleur_rouge : source_color = vec4(0.608, 0.110, 0.110, 1.0);  // #9B1C1C
// Seuil de détection du rouge (r - max(g, b)).
uniform float seuil_rouge : hint_range(0.0, 1.0) = 0.18;
// 0 = rouge normal, 1 = rouge effacé (devient encre), pour les effets de Lucidité.
uniform float rouge_efface : hint_range(0.0, 1.0) = 0.0;

group_uniforms accent;
// Seconde couleur des étapes 5 à 7 (ocre de cire, vert-de-gris), préservée
// exactement comme le rouge. Détectée par proximité avec la couleur exacte.
uniform bool accent_actif = false;
uniform vec4 couleur_accent : source_color = vec4(0.690, 0.541, 0.243, 1.0); // #B08A3E
uniform float tolerance_accent : hint_range(0.0, 0.5) = 0.12;
group_uniforms;

const vec3 LUMA = vec3(0.299, 0.587, 0.114);
const vec3 ENCRE_REF = vec3(0.082, 0.075, 0.059);  // encre des assets
const vec3 PAPIER_REF = vec3(0.910, 0.898, 0.855); // papier des assets

float hash(vec2 p) {
	p = fract(p * vec2(123.34, 456.21));
	p += dot(p, p + 45.32);
	return fract(p.x * p.y);
}

float bruit(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x),
			mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

void fragment() {
	vec2 taille_ecran = 1.0 / SCREEN_PIXEL_SIZE;
	float k = taille_ecran.y / 1080.0; // identique quelle que soit la résolution

	// 1. Trait tremblé.
	float image = mod(floor(TIME * images_par_seconde), float(variantes));
	vec2 graine = vec2(image * 17.3, image * 31.7);
	vec2 p = SCREEN_UV * taille_ecran / (echelle_px * k) + graine;
	vec2 d = vec2(bruit(p), bruit(p + vec2(5.2, 1.3))) * 2.0 - 1.0;
	vec2 uv = SCREEN_UV + d * amplitude_px * k * SCREEN_PIXEL_SIZE;

	// 2. Un seul échantillonnage.
	vec3 src = texture(ecran, uv).rgb;

	// 3. Remappage papier/encre et grain.
	float t = clamp((dot(src, LUMA) - dot(ENCRE_REF, LUMA))
			/ (dot(PAPIER_REF, LUMA) - dot(ENCRE_REF, LUMA)), 0.0, 1.0);
	vec3 c = mix(couleur_encre.rgb, couleur_papier.rgb, t);
	float pas = floor(TIME * grain_par_seconde);
	c += (hash(floor(SCREEN_UV * taille_ecran / (taille_grain_px * k)) + pas * 7.13) - 0.5) * grain;
	c *= teinte.rgb;

	// 4. Rouge et accent, exacts.
	float rougeur = smoothstep(seuil_rouge, seuil_rouge + 0.12, src.r - max(src.g, src.b));
	c = mix(c, mix(couleur_rouge.rgb, couleur_encre.rgb, rouge_efface), rougeur);
	if (accent_actif) {
		float proche = 1.0 - smoothstep(tolerance_accent * 0.5, tolerance_accent,
				distance(src, couleur_accent.rgb));
		c = mix(c, couleur_accent.rgb, proche);
	}

	COLOR = vec4(c, 1.0);
}
