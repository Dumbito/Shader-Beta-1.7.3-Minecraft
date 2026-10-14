#version 330 compatibility

// Conserva la geometria y el color/alpha de las nubes vanilla de Iris.
out vec4 cloudColor;

void main() {
    gl_Position = ftransform();
    cloudColor = gl_Color;
}
