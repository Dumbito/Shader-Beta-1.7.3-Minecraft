#version 330 compatibility

flat in float beta173ClimateTemperatureVarying;
#define BETA_CLIMATE_USE_VARYING
#include "/lib/beta173.glsl"

uniform int renderStage;
uniform float viewWidth;
uniform float viewHeight;
uniform mat4 gbufferModelView;
uniform mat4 gbufferModelViewInverse;
uniform mat4 gbufferProjectionInverse;
uniform sampler2D noisetex; // mapa de estrellas de Beta (shaders.properties: texture.noise)

in vec4 glcolor;

out vec4 fragColor;

// Marco local de Beta -> mundo: Rx(theta) y luego Ry(-90), como el sol y la luna del juego.
// Aqui se hace la inversa: direccion de mundo -> marco local de Beta (sol del angulo 0 en +Y).
vec3 beta173WorldToStarFrame(vec3 d) {
    float theta = beta173CelestialAngle() * BETA_PI * 2.0;
    float s = sin(theta);
    float c = cos(theta);
    return vec3(d.z, d.y * c - d.x * s, -d.y * s - d.x * c);
}

// Cobertura 0..1 de las estrellas de Beta en esa direccion del marco local
float beta173StarCoverage(vec3 local) {
    vec2 uv = vec2(atan(local.x, local.z) / (BETA_PI * 2.0) + 0.5,
                   asin(clamp(local.y, -1.0, 1.0)) / BETA_PI + 0.5);
    return texture(noisetex, uv).r;
}

void main() {
#if BETA_DEBUG == 1
    // Diagnostico: que etapa de Iris llega a este programa
    vec3 stageColor = vec3(1.0, 1.0, 0.0); // amarillo: etapa no reconocida
#ifdef MC_RENDER_STAGE_SKY
    if (renderStage == MC_RENDER_STAGE_SKY) stageColor = vec3(0.0, 0.5, 1.0);        // azul
#endif
#ifdef MC_RENDER_STAGE_SUNSET
    if (renderStage == MC_RENDER_STAGE_SUNSET) stageColor = vec3(1.0, 0.5, 0.0);     // naranja
#endif
#ifdef MC_RENDER_STAGE_STARS
    if (renderStage == MC_RENDER_STAGE_STARS) stageColor = vec3(1.0, 0.0, 1.0);      // magenta
#endif
#ifdef MC_RENDER_STAGE_VOID
    if (renderStage == MC_RENDER_STAGE_VOID) stageColor = vec3(0.4, 0.0, 0.0);       // rojo oscuro
#endif
#ifdef MC_RENDER_STAGE_CUSTOM_SKY
    if (renderStage == MC_RENDER_STAGE_CUSTOM_SKY) stageColor = vec3(0.0, 1.0, 0.0); // verde
#endif
    fragColor = vec4(stageColor, 1.0);
    return;
#endif

#if BETA_DEBUG == 3
    // Diagnostico: blanco = hasSkylight no llega al shader
    if (!hasSkylight) {
        fragColor = vec4(1.0);
        return;
    }
#endif

    // Nether / End: dejar el cielo como lo dibuja el juego
    if (!hasSkylight) {
        fragColor = glcolor;
        return;
    }

#ifdef MC_RENDER_STAGE_STARS
    if (renderStage == MC_RENDER_STAGE_STARS) {
#ifdef BETA_STAR_FIELD
        // Las estrellas se dibujan mas abajo, dentro del cielo: descartar las del motor
        discard;
#else
        // Beta: glColor4f(b, b, b, b) con b = brillo de estrellas * (1 - lluvia)
        float b = beta173StarBrightness() * (1.0 - beta173Rain());
        fragColor = vec4(vec3(b), b);
        return;
#endif
    }
#endif

#ifdef MC_RENDER_STAGE_SUNSET
    if (renderStage == MC_RENDER_STAGE_SUNSET) {
        // El abanico de amanecer/atardecer usa la misma formula que Beta
        fragColor = glcolor;
        return;
    }
#endif

    vec4 ndc = vec4(gl_FragCoord.xy / vec2(viewWidth, viewHeight) * 2.0 - 1.0, 1.0, 1.0);
    vec4 viewPos = gbufferProjectionInverse * ndc;
    vec3 dirView = normalize(viewPos.xyz / viewPos.w);
    float up = dot(dirView, normalize(gbufferModelView[1].xyz));

#if BETA_DEBUG == 3
    // Diagnostico: R = lluvia, G = tormenta, B = brillo de estrellas x2
    fragColor = vec4(beta173Rain(), beta173Thunder(), beta173StarBrightness() * 2.0, 1.0);
    return;
#endif

    vec3 color = beta173SkyGradient(up);

#ifdef BETA_STAR_FIELD
    // Beta mezcla las estrellas con (SRC_ALPHA, ONE) y color (b, b, b, b): suma b * b
    float b = beta173StarBrightness() * (1.0 - beta173Rain());
#if BETA_DEBUG == 2
    b = 1.0;
#endif
    if (b > 0.0 && up > 0.0) {
        vec3 dirWorld = mat3(gbufferModelViewInverse) * dirView;
        float coverage = beta173StarCoverage(beta173WorldToStarFrame(dirWorld));
        color += vec3(coverage * b * b);
    }
#endif

#if BETA_DEBUG == 4
    // Diagnostico: anillos de 2 grados alrededor de donde Beta pone el sol (+Y local) y la luna (-Y local)
    {
        vec3 dirWorld = mat3(gbufferModelViewInverse) * dirView;
        vec3 local = beta173WorldToStarFrame(dirWorld);
        float ang = degrees(acos(clamp(abs(local.y), 0.0, 1.0)));
        if (local.y > 0.0 && abs(ang - 25.0) < 1.0) color = vec3(0.0, 1.0, 1.0);
        if (local.y < 0.0 && abs(ang - 20.0) < 1.0) color = vec3(1.0, 0.5, 0.0);
    }
#endif

    fragColor = vec4(color, 1.0);
}
