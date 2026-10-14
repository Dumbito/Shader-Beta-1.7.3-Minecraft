// Port GLSL de NoiseGenerator2 + NoiseGeneratorOctaves2 de Beta 1.7.3.
// El script genera una textura de índices de gradiente desde la semilla original.
// Se usa float GLSL, por lo que no puede ser bit a bit idéntico al double de Java.
uniform sampler2D beta173ClimateGradient;

const float BETA_CLIMATE_F2 = 0.3660254037844386;
const float BETA_CLIMATE_G2 = 0.21132486540518713;
const float BETA_CLIMATE_SCALE = 0.02500000037252903 / 1.5;

int beta173ClimateWrap(float value) {
    // Equivale al helper wrap de NoiseGenerator2, incluso para coordenadas negativas.
    return value > 0.0 ? int(value) : int(value) - 1;
}

int beta173ClimateGradientIndex(int x, int z, int octave) {
    // La textura PNG se guarda con filas invertidas para compensar el orden de upload de Iris.
    // El inverso vertical recupera la celda original octave/z; una lectura por esquina.
    int textureY = 1023 - (octave * 256 + (z & 255));
    float encoded = texelFetch(beta173ClimateGradient,
                               ivec2(x & 255, textureY), 0).r;
    return int(floor(encoded * 255.0 + 0.5));
}

vec2 beta173ClimateGradient(int index) {
    // Primeras dos componentes de los 12 gradientes usados por NoiseGenerator2.
    if (index == 0) return vec2( 1.0,  1.0);
    if (index == 1) return vec2(-1.0,  1.0);
    if (index == 2) return vec2( 1.0, -1.0);
    if (index == 3) return vec2(-1.0, -1.0);
    if (index == 4) return vec2( 1.0,  0.0);
    if (index == 5) return vec2(-1.0,  0.0);
    if (index == 6) return vec2( 1.0,  0.0);
    if (index == 7) return vec2(-1.0,  0.0);
    if (index == 8) return vec2( 0.0,  1.0);
    if (index == 9) return vec2( 0.0, -1.0);
    if (index == 10) return vec2(0.0, 1.0);
    return vec2(0.0, -1.0);
}

float beta173ClimateCorner(vec2 p, int gradientIndex) {
    float attenuation = 0.5 - dot(p, p);
    if (attenuation < 0.0) return 0.0;
    attenuation *= attenuation;
    return attenuation * attenuation * dot(beta173ClimateGradient(gradientIndex), p);
}

float beta173ClimateSimplex(vec2 point, int octave) {
    float skew = (point.x + point.y) * BETA_CLIMATE_F2;
    int i = beta173ClimateWrap(point.x + skew);
    int j = beta173ClimateWrap(point.y + skew);
    float unskew = float(i + j) * BETA_CLIMATE_G2;
    float x0 = point.x - (float(i) - unskew);
    float z0 = point.y - (float(j) - unskew);

    int i1 = x0 > z0 ? 1 : 0;
    int j1 = x0 > z0 ? 0 : 1;
    vec2 p0 = vec2(x0, z0);
    vec2 p1 = vec2(x0 - float(i1) + BETA_CLIMATE_G2,
                    z0 - float(j1) + BETA_CLIMATE_G2);
    vec2 p2 = vec2(x0 - 1.0 + 2.0 * BETA_CLIMATE_G2,
                    z0 - 1.0 + 2.0 * BETA_CLIMATE_G2);

    int g0 = beta173ClimateGradientIndex(i, j, octave);
    int g1 = beta173ClimateGradientIndex(i + i1, j + j1, octave);
    int g2 = beta173ClimateGradientIndex(i + 1, j + 1, octave);
    return 70.0 * (beta173ClimateCorner(p0, g0)
                 + beta173ClimateCorner(p1, g1)
                 + beta173ClimateCorner(p2, g2));
}

vec2 beta173ClimateOffset(int octave) {
    if (octave == 0) return BETA_CLIMATE_OFFSET_0;
    if (octave == 1) return BETA_CLIMATE_OFFSET_1;
    if (octave == 2) return BETA_CLIMATE_OFFSET_2;
    return BETA_CLIMATE_OFFSET_3;
}

float beta173ClimateTemperature(vec2 blockXZ) {
    float value = 0.0;
    float frequency = 1.0;
    float amplitude = 1.0;
    for (int octave = 0; octave < 4; ++octave) {
        vec2 point = blockXZ * (BETA_CLIMATE_SCALE * frequency) + beta173ClimateOffset(octave);
        value += beta173ClimateSimplex(point, octave) * (0.55 / amplitude);
        frequency *= 0.5;
        amplitude *= 0.5;
    }
    return value;
}
