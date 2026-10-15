#version 330 compatibility

#include "/lib/beta173.glsl"

uniform mat4 gbufferModelViewInverse;
uniform sampler2D beta173CloudMap;

in vec4 cloudColor;
in vec3 cloudViewPos;
in vec2 betaCloudUV;
flat in float betaCloudShade;

out vec4 fragColor;

// Rampa configurable: mantiene legibles las nubes al atardecer y las oscurece
// poco a poco hasta la noche. Solo afecta el RGB; no toca alfa ni geometria.
float beta173CloudNightFloor() {
    float ticks = mod(float(worldTime), 24000.0);
    float dusk = smoothstep(BETA_CLOUD_DUSK_START_TICK, BETA_CLOUD_DUSK_END_TICK, ticks);
    return mix(BETA_CLOUD_DUSK_MIN_DAYLIGHT, BETA_CLOUD_NIGHT_MIN_DAYLIGHT, dusk);
}

float beta173CloudDaylight() {
    return max(beta173DayFactor(), beta173CloudNightFloor());
}

vec3 beta173CloudColor() {
    vec3 color = vec3(1.0);
    float rain = beta173Rain();
    if (rain > 0.0) {
        float gray = dot(color, vec3(0.3, 0.59, 0.11)) * 0.6;
        float k = 1.0 - rain * 0.95;
        color = color * k + vec3(gray) * (1.0 - k);
    }

    // Respuesta continua durante el ciclo completo; no hay corte en 12000/13000 ticks.
    float day = beta173CloudDaylight();
    color *= vec3(day * 0.9 + 0.1, day * 0.9 + 0.1, day * 0.85 + 0.15);

    float thunder = beta173Thunder();
    if (thunder > 0.0) {
        float gray = dot(color, vec3(0.3, 0.59, 0.11)) * 0.2;
        float k = 1.0 - thunder * 0.95;
        color = color * k + vec3(gray) * (1.0 - k);
    }
    return color;
}

float beta173CloudFaceShade() {
    vec3 nView = normalize(cross(dFdx(cloudViewPos), dFdy(cloudViewPos)));
    vec3 nWorld = mat3(gbufferModelViewInverse) * nView;
    if (abs(nWorld.y) > 0.5) return nWorld.y > 0.0 ? 1.0 : 0.7;
    return abs(nWorld.x) > abs(nWorld.z) ? 0.9 : 0.8;
}

void main() {
#if BETA_DEBUG == 1
    fragColor = vec4(1.0, 0.0, 0.0, 1.0);
#elif BETA_CUSTOM_CLOUD_GEOMETRY
    vec4 mask = texture(beta173CloudMap, betaCloudUV);
    if (mask.a < 0.01) discard;
    fragColor = vec4(beta173CloudColor() * betaCloudShade, 0.8 * mask.a);
#elif BETA_CLOUD_COLOR_MODE == 1
    fragColor = cloudColor;
#elif BETA_CLOUD_COLOR_MODE == 2
    fragColor = vec4(cloudColor.rgb * beta173CloudColor(), cloudColor.a);
#else
    // Modo estable: conserva el alfa/máscara nativa; el tiempo solo modifica el RGB.
    fragColor = vec4(beta173CloudColor() * beta173CloudFaceShade(), cloudColor.a);
#endif
}
