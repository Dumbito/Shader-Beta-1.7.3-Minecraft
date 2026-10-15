#version 330 compatibility

#include "/lib/beta173.glsl"

uniform mat4 gbufferModelViewInverse;

in vec4 cloudColor;
in vec3 cloudViewPos;

out vec4 fragColor;

// World.drawClouds(float): color historico, lluvia, factor celeste y tormenta.
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

// RenderGlobal.renderCloudsFancy: arriba 1.0, abajo 0.7, caras X 0.9, caras Z 0.8.
// La cara se deduce de la geometria en pantalla, sin depender de atributos del motor.
float beta173CloudFaceShade() {
    vec3 nView = normalize(cross(dFdx(cloudViewPos), dFdy(cloudViewPos)));
    vec3 nWorld = mat3(gbufferModelViewInverse) * nView;
    if (abs(nWorld.y) > 0.5) {
        // La normal reconstruida por derivadas apunta hacia el lado visible de la cara.
        // Normal Y positiva: superficie superior clara; negativa: cara inferior sombreada.
        // No depende de la altura de cámara ni de la altura absoluta del mundo.
        return nWorld.y > 0.0 ? 1.0 : 0.7;
    }
    return abs(nWorld.x) > abs(nWorld.z) ? 0.9 : 0.8;
}

void main() {
#if BETA_DEBUG == 1
    // Diagnostico: si ves nubes rojas y opacas, este programa SI se ejecuta sobre las nubes
    fragColor = vec4(1.0, 0.0, 0.0, 1.0);
#elif BETA_CLOUD_COLOR_MODE == 1
    fragColor = cloudColor;
#elif BETA_CLOUD_COLOR_MODE == 2
    fragColor = vec4(cloudColor.rgb * beta173CloudColor(), cloudColor.a);
#else
    // El alfa sigue siendo el del motor: es la mascara de donde hay nube
    fragColor = vec4(beta173CloudColor() * beta173CloudFaceShade(), cloudColor.a);
#endif
}
