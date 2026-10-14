// Beta173 Lighting - funciones portadas desde el codigo de Minecraft Beta 1.7.3
// Referencia: WorldProvider, WorldProviderHell, World, EntityRenderer y RenderGlobal
// (https://github.com/jacobo-mc/mc_b1.7.3_release)

#include "/lib/config.glsl"

uniform int worldTime;
uniform float rainStrength;
uniform float thunderStrength; // Iris lo entrega ya ponderado por la lluvia, igual que getWeightedThunderStrength
uniform bool hasSkylight;      // false en Nether y End
uniform bool hasCeiling;       // true en dimensiones con techo, como el Nether
uniform float ambientLight;    // luz ambiental nativa de la dimensión, expuesta por Iris
uniform vec3 fogColor;          // color de niebla nativo de Minecraft expuesto por Iris
uniform float fogStart;         // inicio de niebla nativo
uniform float fogEnd;           // fin de niebla nativo
uniform float fogDensity;       // densidad de niebla nativa
uniform int fogMode;             // 2048 EXP, 2049 EXP2, 9729 LINEAR
uniform int isEyeInWater;      // 0 aire, 1 agua, 2 lava

const float BETA_PI = 3.14159265359;

float beta173Rain() {
    return rainStrength;
}

float beta173Thunder() {
#ifdef BETA_THUNDER
    return thunderStrength;
#else
    return 0.0;
#endif
}

float beta173CelestialAngle() {
    float angle = mod(float(worldTime), 24000.0) / 24000.0 - 0.25;
    if (angle < 0.0) angle += 1.0;
    if (angle > 1.0) angle -= 1.0;

    float original = angle;
    angle = 1.0 - (cos(angle * BETA_PI) + 1.0) / 2.0;
    return original + (angle - original) / 3.0;
}

// cos(angulo * 2pi) * 2 + 0.5, limitado a 0..1 (base de cielo, niebla y luz)
float beta173DayFactor() {
    return clamp(cos(beta173CelestialAngle() * BETA_PI * 2.0) * 2.0 + 0.5, 0.0, 1.0);
}

// World.calculateSkylightSubtracted
float beta173SkySubtracted() {
    float f = beta173DayFactor();
    f *= 1.0 - beta173Rain() * 5.0 / 16.0;
    f *= 1.0 - beta173Thunder() * 5.0 / 16.0;
    return floor((1.0 - f) * 11.0);
}

// WorldProvider.generateLightBrightnessTable (0.1 en el Nether)
float beta173Ambient() {
#ifdef BETA_NETHER_AMBIENT
    if (!hasSkylight && hasCeiling) return 0.1;
#endif
    if (!hasSkylight && !hasCeiling) return ambientLight;
    return 0.05;
}

float beta173Brightness(float level) {
    float ambient = beta173Ambient();
    float inverted = 1.0 - level / 15.0;
    return (1.0 - inverted) / (inverted * 3.0 + 1.0) * (1.0 - ambient) + ambient;
}

// Nivel de luz efectivo: max(luz de bloque, luz de cielo - restado)
float beta173LightLevel(vec2 lm) {
    float block = clamp(lm.x, 0.0, 1.0) * 15.0;
    float sky = clamp(lm.y, 0.0, 1.0) * 15.0;
#ifndef BETA_SMOOTH
    block = floor(block + 0.5);
    sky = floor(sky + 0.5);
#endif
    return max(block, max(0.0, sky - beta173SkySubtracted()));
}

// Equivalente a java.awt.Color.getHSBColor
vec3 beta173Hsb(float h, float s, float b) {
    vec3 k = vec3(1.0, 2.0 / 3.0, 1.0 / 3.0);
    vec3 p = abs(fract(vec3(h) + k) * 6.0 - 3.0);
    return b * mix(vec3(1.0), clamp(p - 1.0, 0.0, 1.0), s);
}

// World.getSkyColor + BiomeGenBase.getSkyColorByTemp
vec3 beta173SkyColor() {
    float t = clamp(BETA_SKY_TEMPERATURE / 3.0, -1.0, 1.0);
    vec3 col = beta173Hsb(0.62222224 - t * 0.05, 0.5 + t * 0.1, 1.0) * beta173DayFactor();

    float rain = beta173Rain();
    if (rain > 0.0) {
        float gray = dot(col, vec3(0.3, 0.59, 0.11)) * 0.6;
        float k = 1.0 - rain * 0.75;
        col = col * k + vec3(gray) * (1.0 - k);
    }

    float thunder = beta173Thunder();
    if (thunder > 0.0) {
        float gray = dot(col, vec3(0.3, 0.59, 0.11)) * 0.2;
        float k = 1.0 - thunder * 0.75;
        col = col * k + vec3(gray) * (1.0 - k);
    }
    return col;
}

// WorldProvider.func_4096_a + EntityRenderer.updateFogColor
vec3 beta173FogColor() {
    // Nether: reproduce el color de WorldProviderHell.func_4096_a de Beta 1.7.3.
    // End: usar el color de niebla nativo de la dimensión moderna, no inventar un color Beta.
    if (!hasSkylight) {
        if (hasCeiling) return vec3(0.2, 0.03, 0.03);
        return fogColor;
    }

    // La ruta del Overworld conserva la fórmula histórica de v0.8.
    float d = beta173DayFactor();
    vec3 fog = vec3(0.7529412, 0.84705883, 1.0) * vec3(d * 0.94 + 0.06, d * 0.94 + 0.06, d * 0.91 + 0.09);
    fog += (beta173SkyColor() - fog) * BETA_FOG_SKY_BLEND;

    float rain = beta173Rain();
    if (rain > 0.0) {
        fog.rg *= 1.0 - rain * 0.5;
        fog.b *= 1.0 - rain * 0.4;
    }

    float thunder = beta173Thunder();
    if (thunder > 0.0) {
        fog *= 1.0 - thunder * 0.5;
    }
    return fog;
}

// World.getStarBrightness
float beta173StarBrightness() {
    float v = clamp(1.0 - (cos(beta173CelestialAngle() * BETA_PI * 2.0) * 2.0 + 0.75), 0.0, 1.0);
    return v * v * 0.5;
}

// EntityRenderer.setupFog: lineal en aire (inicio al 25%), exponencial en agua y lava
vec3 beta173ApplyFog(vec3 color, float dist) {
#ifdef BETA_FOG
    if (isEyeInWater == 1) {
        return mix(vec3(0.02, 0.02, 0.2), color, exp(-0.1 * dist));
    }
    if (isEyeInWater == 2) {
        return mix(vec3(0.6, 0.1, 0.0), color, exp(-2.0 * dist));
    }

    // End moderno: respetar el modo, color, densidad y distancias nativas de Iris/Minecraft.
    // Los modos corresponden a GL_EXP, GL_EXP2 y GL_LINEAR.
    if (!hasSkylight && !hasCeiling) {
        float endNativeFogStart = max(fogStart, 0.0);
        float endNativeFogEnd = max(fogEnd, endNativeFogStart + 0.001);
        float endNativeFogFactor;
        if (fogMode == 2048) {
            endNativeFogFactor = exp(-max(fogDensity, 0.0) * dist);
        } else if (fogMode == 2049) {
            float densityDistance = max(fogDensity, 0.0) * dist;
            endNativeFogFactor = exp(-(densityDistance * densityDistance));
        } else {
            float nativeFogRange = max(endNativeFogEnd - endNativeFogStart, 0.001);
            endNativeFogFactor = clamp((endNativeFogEnd - dist) / nativeFogRange, 0.0, 1.0);
        }
        return mix(fogColor, color, clamp(endNativeFogFactor, 0.0, 1.0));
    }

    // Overworld conserva el perfil v0.8; el Nether comienza la niebla en distancia cero.
    bool isNether = !hasSkylight && hasCeiling;
    float betaFogEnd = BETA_FOG_END;
    float betaFogStart = isNether ? 0.0 : betaFogEnd * 0.25;
    float f = clamp((betaFogEnd - dist) / (betaFogEnd - betaFogStart), 0.0, 1.0);
    return mix(beta173FogColor(), color, f);
#else
    return color;
#endif
}

// RenderGlobal.renderSky: el domo se dibuja con niebla activa, asi que el cielo
// pasa de color de cielo (arriba) a color de niebla (horizonte). Debajo del horizonte
// se dibuja un segundo disco oscuro. 'up' = seno de la elevacion de la mirada.
vec3 beta173SkyGradient(float up) {
    vec3 sky = beta173SkyColor();
    vec3 base = up >= 0.0 ? sky : vec3(sky.r * 0.2 + 0.04, sky.g * 0.2 + 0.04, sky.b * 0.6 + 0.1);

    float dist = 16.0 / max(abs(up), 0.0005);
    float betaFogEnd = BETA_FOG_END;
    float betaFogStart = betaFogEnd * 0.25;
    float f = clamp((betaFogEnd - dist) / (betaFogEnd - betaFogStart), 0.0, 1.0);
#ifndef BETA_FOG
    f = 1.0;
#endif
    return mix(beta173FogColor(), base, f);
}
