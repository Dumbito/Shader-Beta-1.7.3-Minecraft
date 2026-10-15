#version 330 compatibility

// En Iris, entidades, mano, items tirados, block entities y clima caen a este programa.

flat in float beta173ClimateTemperatureVarying;
#define BETA_CLIMATE_USE_VARYING
#include "/lib/beta173.glsl"

uniform sampler2D gtexture;
uniform float alphaTestRef = 0.1;
uniform vec4 entityColor;

in vec2 lmcoord;
in vec2 texcoord;
in vec4 glcolor;
in float viewDist;

out vec4 fragColor;

void main() {
    vec4 albedo = texture(gtexture, texcoord) * glcolor;
    if (albedo.a < alphaTestRef) discard;

    // Overlay rojo al recibir dano (solo entidades; en mano/items vale 0)
    albedo.rgb = mix(albedo.rgb, entityColor.rgb, entityColor.a);

    albedo.rgb *= beta173Brightness(beta173LightLevel(lmcoord));
    albedo.rgb = beta173ApplyFog(albedo.rgb, viewDist);

    fragColor = albedo;
}
