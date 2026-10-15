#version 330 compatibility

#include "/lib/beta173.glsl"

out vec2 lmcoord;
out vec2 texcoord;
out vec4 glcolor;
out float viewDist;
flat out float beta173ClimateTemperatureVarying;

void main() {
    gl_Position = ftransform();
    texcoord = (gl_TextureMatrix[0] * gl_MultiTexCoord0).xy;
    lmcoord = (gl_TextureMatrix[1] * gl_MultiTexCoord1).xy;
    lmcoord = lmcoord / (30.0 / 32.0) - (1.0 / 32.0);
    glcolor = gl_Color;
    viewDist = length((gl_ModelViewMatrix * gl_Vertex).xyz);
    // Se calcula por vértice: evita ejecutar 4 octavas de ruido en cada fragmento de terreno.
    beta173ClimateTemperatureVarying = beta173SkyClimateTemperature();
}
