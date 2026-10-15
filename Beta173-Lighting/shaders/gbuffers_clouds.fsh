#version 330 compatibility

#include "/lib/beta173.glsl"

uniform mat4 gbufferModelViewInverse;
uniform sampler2D beta173CloudMap;

in vec4 cloudColor;
in vec3 cloudViewPos;
in vec2 betaCloudUV;
flat in float betaCloudShade;

out vec4 fragColor;

// Visibilidad de nube limitada al tramo diurno. La rampa cruza correctamente el tick 24000.
float beta173CloudVisibility() {
    float ticks = mod(float(worldTime), 24000.0);
    float visibility;

    // Anochecer: transición suave desde las nubes normales hasta ocultarlas.
    if (ticks >= BETA_CLOUD_DUSK_START_TICK && ticks < BETA_CLOUD_DUSK_END_TICK) {
        visibility = 1.0 - smoothstep(BETA_CLOUD_DUSK_START_TICK,
                                      BETA_CLOUD_DUSK_END_TICK, ticks);
    }
    // Amanecer: el intervalo cruza el final del día (24000 -> 0).
    else if (ticks >= BETA_CLOUD_DAWN_START_TICK || ticks < BETA_CLOUD_DAWN_END_TICK) {
        float dawnTicks = ticks < BETA_CLOUD_DAWN_END_TICK ? ticks + 24000.0 : ticks;
        visibility = smoothstep(BETA_CLOUD_DAWN_START_TICK,
                                BETA_CLOUD_DAWN_END_TICK + 24000.0, dawnTicks);
    }
    // Noche profunda: no emitir ningún fragmento de nube.
    else if (ticks >= BETA_CLOUD_DUSK_END_TICK && ticks < BETA_CLOUD_DAWN_START_TICK) {
        visibility = 0.0;
    } else {
        visibility = 1.0;
    }
    return clamp(visibility, 0.0, 1.0);
}
vec3 beta173CloudColor() {
    vec3 color = vec3(1.0);
    float rain = beta173Rain();
    if (rain > 0.0) {
        float gray = dot(color, vec3(0.3, 0.59, 0.11)) * 0.6;
        float k = 1.0 - rain * 0.95;
        color = color * k + vec3(gray) * (1.0 - k);
    }

    // Mantener la respuesta de color de v1.0.0: usar la fórmula diurna de Beta.
    float day = beta173DayFactor();
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
    // El diagnóstico puede forzar rojo incluso durante la noche.
    fragColor = vec4(1.0, 0.0, 0.0, 1.0);
    return;
#else
    float cloudVisibility = beta173CloudVisibility();
    if (cloudVisibility <= 0.001) discard;

#if BETA_CUSTOM_CLOUD_GEOMETRY
    vec4 mask = texture(beta173CloudMap, betaCloudUV);
    if (mask.a < 0.01) discard;
    fragColor = vec4(beta173CloudColor() * betaCloudShade,
                     0.8 * mask.a * cloudVisibility);
#elif BETA_CLOUD_COLOR_MODE == 1
    // El perfil de color nativo también respeta el horario diurno.
    fragColor = vec4(cloudColor.rgb, cloudColor.a * cloudVisibility);
#elif BETA_CLOUD_COLOR_MODE == 2
    fragColor = vec4(cloudColor.rgb * beta173CloudColor(),
                     cloudColor.a * cloudVisibility);
#else
    // Modo estable: geometría y color de v1.0.0; solo se añade el horario diurno.
    fragColor = vec4(beta173CloudColor() * beta173CloudFaceShade(),
                     cloudColor.a * cloudVisibility);
#endif
#endif
}
