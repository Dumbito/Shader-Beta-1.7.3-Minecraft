#version 330 compatibility

// Passthrough explícito para que Iris use su pipeline CLOUDS con el shaderpack.
in vec4 cloudColor;
out vec4 fragColor;

void main() {
    fragColor = cloudColor;
}
