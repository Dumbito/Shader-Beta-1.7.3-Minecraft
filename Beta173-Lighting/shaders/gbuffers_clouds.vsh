#version 330 compatibility

#include "/lib/config.glsl"

// Conserva la geometria de las nubes vanilla de Iris.
// Con BETA_CLOUD_HEIGHT_FIX las baja a la altura de Beta (108.33 en vez de 192.33).
// El desplazamiento se hace en espacio de vista a lo largo del "arriba" del mundo,
// asi no depende de como el juego construya la geometria de las nubes.
uniform mat4 gbufferModelView;

out vec4 cloudColor;
out vec3 cloudViewPos;

void main() {
    vec4 viewPos = gl_ModelViewMatrix * gl_Vertex;
#ifdef BETA_CLOUD_HEIGHT_FIX
    viewPos.xyz += gbufferModelView[1].xyz * (BETA_CLOUD_HEIGHT - BETA_VANILLA_CLOUD_HEIGHT);
#endif
    gl_Position = gl_ProjectionMatrix * viewPos;
    cloudColor = gl_Color;
    cloudViewPos = viewPos.xyz;
}
