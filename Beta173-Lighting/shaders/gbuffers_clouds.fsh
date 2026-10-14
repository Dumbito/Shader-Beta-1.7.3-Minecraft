#version 330 compatibility

#include "/lib/beta173.glsl"

// World.drawClouds(float): color historico, lluvia, factor celeste y tormenta.
// La geometria y el alfa siguen viniendo del pase CLOUDS de Iris.
in vec4 cloudColor;
out vec4 fragColor;

vec3 beta173CloudColor() {
    vec3 color = vec3(1.0);
    float rain = beta173Rain();

    if (rain > 0.0) {
        float gray = dot(color, vec3(0.3, 0.59, 0.11)) * 0.6;
        float k = 1.0 - rain * 0.95;
        color = color * k + vec3(gray) * (1.0 - k);
    }

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

void main() {
    fragColor = vec4(cloudColor.rgb * beta173CloudColor(), cloudColor.a);
}
