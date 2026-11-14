// Papier par étape : remappe la scène (dessinée en encre #15130F sur papier
// #E8E5DA) vers le papier et l'encre de l'étape, ajoute le grain, et laisse
// passer le rouge intact. À poser sur un ColorRect plein écran, dans un
// CanvasLayer AU-DESSUS du trait tremblé et SOUS l'interface.
// Compatible renderer Compatibility (GLES3 / WebGL2).
shader_type canvas_item;

uniform sampler2D ecran : hint_screen_texture, filter_linear;
uniform vec4 couleur_papier : source_color = vec4(0.910, 0.898, 0.855, 1.0); // #E8E5DA
uniform vec4 couleur_encre : source_color = vec4(0.082, 0.075, 0.059, 1.0);  // #15130F
uniform vec4 couleur_rouge : source_color = vec4(0.608, 0.110, 0.110, 1.0);  // #9B1C1C
// Seuil de détection du rouge (r - max(g, b)).
uniform float seuil_rouge : hint_range(0.0, 1.0) = 0.18;
// 0 = rouge normal, 1 = rouge effacé (devient encre), pour les effets de Lucidité.
uniform float rouge_efface : hint_range(0.0, 1.0) = 0.0;
uniform float grain : hint_range(0.0, 0.3) = 0.06;
// Taille du grain en pixels à 1080p.
uniform float taille_grain_px : hint_range(1.0, 8.0) = 1.5;
// Le grain ne change que quelques fois par seconde : papier, pas pellicule.
uniform float grain_par_seconde : hint_range(0.0, 24.0) = 6.0;

float hash(vec2 p) {
	p = fract(p * vec2(123.34, 456.21));
	p += dot(p, p + 45.32);
	return fract(p.x * p.y);
}

void fragment() {
	vec3 src = texture(ecran, SCREEN_UV).rgb;
	// Position de chaque pixel entre l'encre de référence (0) et le papier de référence (1).
	const vec3 ENCRE_REF = vec3(0.082, 0.075, 0.059);
	const vec3 PAPIER_REF = vec3(0.910, 0.898, 0.855);
	float l = dot(src, vec3(0.299, 0.587, 0.114));
	float l_encre = dot(ENCRE_REF, vec3(0.299, 0.587, 0.114));
	float l_papier = dot(PAPIER_REF, vec3(0.299, 0.587, 0.114));
	float t = clamp((l - l_encre) / (l_papier - l_encre), 0.0, 1.0);
	vec3 remappe = mix(couleur_encre.rgb, couleur_papier.rgb, t);

	// Le rouge garde sa couleur (sauf si on l'efface).
	float rougeur = smoothstep(seuil_rouge, seuil_rouge + 0.12, src.r - max(src.g, src.b));
	vec3 rouge = mix(couleur_rouge.rgb, couleur_encre.rgb, rouge_efface);
	vec3 c = mix(remappe, rouge, rougeur);

	vec2 taille_ecran = 1.0 / SCREEN_PIXEL_SIZE;
	float k = taille_ecran.y / 1080.0;
	float pas = floor(TIME * grain_par_seconde);
	float n = hash(floor(SCREEN_UV * taille_ecran / (taille_grain_px * k)) + pas * 7.13) - 0.5;
	c += n * grain;
	COLOR = vec4(c, 1.0);
}
