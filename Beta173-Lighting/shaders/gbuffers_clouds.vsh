#version 330 compatibility

#include "/lib/config.glsl"

uniform mat4 gbufferModelView;

out vec4 sourceCloudColor;
out vec3 sourceCloudViewPos;

void main() {
    vec4 viewPos = gl_ModelViewMatrix * gl_Vertex;
#ifdef BETA_CLOUD_HEIGHT_FIX
    viewPos.xyz += gbufferModelView[1].xyz * (BETA_CLOUD_HEIGHT - BETA_VANILLA_CLOUD_HEIGHT);
#endif
    gl_Position = gl_ProjectionMatrix * viewPos;
    sourceCloudColor = gl_Color;
    sourceCloudViewPos = viewPos.xyz;
}
