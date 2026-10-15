#version 330 compatibility

#include "/lib/beta173.glsl"

out vec4 glcolor;
flat out float beta173ClimateTemperatureVarying;

void main() {
    gl_Position = ftransform();
    glcolor = gl_Color;
    beta173ClimateTemperatureVarying = beta173SkyClimateTemperature();
}
