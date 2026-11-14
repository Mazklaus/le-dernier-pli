// Trait tremblé : déformation plein écran façon gravure qui vibre.
// À poser sur un ColorRect plein écran dans un CanvasLayer placé AU-DESSUS du
// monde et SOUS l'interface (l'UI ne doit pas trembler).
// Compatible renderer Compatibility (GLES3 / WebGL2).
// 3 variantes de bruit qui tournent à `images_par_seconde` (6 par défaut),
// comme les 3 dessins d'une animation "boiling line".
shader_type canvas_item;

uniform sampler2D ecran : hint_screen_texture, filter_linear;
// Amplitude en pixels écran à 1080p. 1.5 = repos ; monter quand la Lucidité baisse.
uniform float amplitude_px : hint_range(0.0, 12.0) = 1.5;
// Taille des ondulations, en pixels à 1080p.
uniform float echelle_px : hint_range(4.0, 200.0) = 38.0;
uniform float images_par_seconde : hint_range(1.0, 24.0) = 6.0;
uniform int variantes : hint_range(1, 8) = 3;

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
	// Facteur d'échelle pour que l'effet soit identique quelle que soit la résolution.
	float k = taille_ecran.y / 1080.0;
	float image = mod(floor(TIME * images_par_seconde), float(variantes));
	vec2 graine = vec2(image * 17.3, image * 31.7);
	vec2 p = SCREEN_UV * taille_ecran / (echelle_px * k) + graine;
	vec2 d = vec2(bruit(p), bruit(p + vec2(5.2, 1.3))) * 2.0 - 1.0;
	vec2 uv = SCREEN_UV + d * amplitude_px * k * SCREEN_PIXEL_SIZE;
	COLOR = texture(ecran, uv);
}
