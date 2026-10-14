#version 330 compatibility

// Brillo de encantamiento: sin iluminacion y SIN discard por alpha.
// El juego lo mezcla con blending aditivo; si se descarta o se oscurece, desaparece.

uniform sampler2D gtexture;

in vec2 texcoord;
in vec4 glcolor;

out vec4 fragColor;

void main() {
    fragColor = texture(gtexture, texcoord) * glcolor;
}
