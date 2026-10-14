#version 330 compatibility

uniform sampler2D gtexture;
uniform int worldTime;
uniform float rainStrength;
uniform float alphaTestRef = 0.1;

in vec2 lmcoord;
in vec2 texcoord;
in vec4 glcolor;

out vec4 fragColor;

float beta173Brightness(int level) {
    float inverted = 1.0 - float(level) / 15.0;
    return (1.0 - inverted) / (inverted * 3.0 + 1.0) * 0.95 + 0.05;
}

float beta173CelestialAngle(float timeOfDay) {
    float angle = mod(timeOfDay, 24000.0) / 24000.0 - 0.25;
    if (angle < 0.0) angle += 1.0;
    if (angle > 1.0) angle -= 1.0;

    float original = angle;
    angle = 1.0 - (cos(angle * 3.14159265359) + 1.0) / 2.0;
    return original + (angle - original) / 3.0;
}

int beta173SkySubtracted() {
    float angle = beta173CelestialAngle(float(worldTime));
    float skyFactor = clamp(cos(angle * 6.28318530718) * 2.0 + 0.5, 0.0, 1.0);
    float weatherFactor = 1.0 - rainStrength * 5.0 / 16.0;
    float darkness = 1.0 - skyFactor * weatherFactor;
    return int(clamp(darkness * 11.0, 0.0, 11.0));
}

void main() {
    vec4 albedo = texture(gtexture, texcoord) * glcolor;
    if (albedo.a < alphaTestRef) discard;

    int blockLevel = int(floor(clamp(lmcoord.x, 0.0, 1.0) * 15.0 + 0.5));
    int skyLevel = int(floor(clamp(lmcoord.y, 0.0, 1.0) * 15.0 + 0.5));

    int effectiveSky = max(0, skyLevel - beta173SkySubtracted());
    int effectiveLight = max(blockLevel, effectiveSky);
    albedo.rgb *= beta173Brightness(effectiveLight);

    fragColor = albedo;
}
