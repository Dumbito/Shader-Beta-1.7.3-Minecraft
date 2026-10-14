#version 330 compatibility

#include "/lib/beta173.glsl"

uniform int renderStage;
uniform float viewWidth;
uniform float viewHeight;
uniform mat4 gbufferModelView;
uniform mat4 gbufferProjectionInverse;

in vec4 glcolor;

out vec4 fragColor;

void main() {
    // Nether / End: dejar el cielo como lo dibuja el juego
    if (!hasSkylight) {
        fragColor = glcolor;
        return;
    }

#ifdef MC_RENDER_STAGE_STARS
    if (renderStage == MC_RENDER_STAGE_STARS) {
        // Beta: glColor4f(b, b, b, b) con b = brillo de estrellas * (1 - lluvia)
        float b = beta173StarBrightness() * (1.0 - beta173Rain());
        // Replica RenderGlobal de Beta: glColor4f(b, b, b, b).
        fragColor = vec4(vec3(b), b);
        return;
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
    vec3 dir = normalize(viewPos.xyz / viewPos.w);
    float up = dot(dir, normalize(gbufferModelView[1].xyz));

    fragColor = vec4(beta173SkyGradient(up), 1.0);
}
