#version 330 compatibility

#include "/lib/config.glsl"

layout(triangles) in;
layout(triangle_strip, max_vertices = 64) out;

in vec4 sourceCloudColor[];
in vec3 sourceCloudViewPos[];

out vec4 cloudColor;
out vec3 cloudViewPos;
out vec2 betaCloudUV;
flat out float betaCloudShade;

uniform mat4 gbufferModelView;
uniform mat4 gbufferProjection;
uniform vec3 cameraPosition;
uniform ivec3 cameraPositionInt;
uniform vec3 cameraPositionFract;
uniform int worldTime;
uniform int worldDay;

const int BETA_CLOUD_TILE_COUNT = 6;
const int BETA_CLOUD_SEGMENTS = 8;
const int BETA_CLOUD_TILE_SIZE = 96;
const int BETA_CLOUD_GRID_SIZE = 3072;
const int BETA_CLOUD_TEXTURE_SIZE = 256;
const float BETA_CLOUD_SEGMENT_SIZE = 12.0;
const float BETA_CLOUD_TEXTURE_STEP = 1.0 / 256.0;
const float BETA_CLOUD_EDGE_EPSILON = 0.0009765625;

int betaCloudWrapInt(int value, int period) {
    int wrapped = value % period;
    return wrapped < 0 ? wrapped + period : wrapped;
}

float betaCloudScrollBlocks() {
    // World.drawClouds: cloudOffsetX advances 1/tick, then * 0.03 blocks.
    // The texture repeats every 3072 blocks (256 cells * 12 blocks).
    // 128 days * 24000 ticks is a whole number of 3072-block cloud cycles.
    float day = mod(float(worldDay), 128.0);
    float ticks = mod(day * 24000.0 + float(worldTime), 102400.0);
    return ticks * 0.03;
}

void betaCloudEmitVertex(vec3 relativePosition, vec2 uv, float shade) {
    vec4 viewPosition = gbufferModelView * vec4(relativePosition, 1.0);
    gl_Position = gbufferProjection * viewPosition;
    cloudColor = vec4(1.0);
    cloudViewPos = viewPosition.xyz;
    betaCloudUV = uv;
    betaCloudShade = shade;
    EmitVertex();
}

void betaCloudEmitQuad(
    vec3 p0, vec3 p1, vec3 p2, vec3 p3,
    vec2 uv0, vec2 uv1, vec2 uv2, vec2 uv3,
    float shade
) {
    betaCloudEmitVertex(p0, uv0, shade);
    betaCloudEmitVertex(p1, uv1, shade);
    betaCloudEmitVertex(p2, uv2, shade);
    betaCloudEmitVertex(p3, uv3, shade);
    EndPrimitive();
}

void betaCloudEmitCellFace(
    int faceInCell, int cellX, int cellZ,
    float x0, float x1, float z0, float z1,
    float bottomY, float topY, int baseGridX, int baseGridZ
) {
    float u0 = float(betaCloudWrapInt(baseGridX + cellX * 8, BETA_CLOUD_TEXTURE_SIZE)) * BETA_CLOUD_TEXTURE_STEP;
    float u1 = float(betaCloudWrapInt(baseGridX + (cellX + 1) * 8, BETA_CLOUD_TEXTURE_SIZE)) * BETA_CLOUD_TEXTURE_STEP;
    float v0 = float(betaCloudWrapInt(baseGridZ + cellZ * 8, BETA_CLOUD_TEXTURE_SIZE)) * BETA_CLOUD_TEXTURE_STEP;
    float v1 = float(betaCloudWrapInt(baseGridZ + (cellZ + 1) * 8, BETA_CLOUD_TEXTURE_SIZE)) * BETA_CLOUD_TEXTURE_STEP;
    int localFace = faceInCell;

    // Beta top and bottom planes: one 96x96-block quad, texture region 8x8 pixels.
    if (localFace == 0) {
        if (bottomY <= 5.0) {
            betaCloudEmitQuad(
                vec3(x0, topY, z1), vec3(x1, topY, z1),
                vec3(x1, topY, z0), vec3(x0, topY, z0),
                vec2(u0, v1), vec2(u1, v1), vec2(u1, v0), vec2(u0, v0), 1.0
            );
        }
        return;
    }
    localFace -= 1;

    if (localFace == 0) {
        if (bottomY > -5.0) {
            betaCloudEmitQuad(
                vec3(x0, bottomY, z0), vec3(x1, bottomY, z0),
                vec3(x1, bottomY, z1), vec3(x0, bottomY, z1),
                vec2(u0, v0), vec2(u1, v0), vec2(u1, v1), vec2(u0, v1), 0.7
            );
        }
        return;
    }
    localFace -= 1;

    // Walls parallel to Z: shade 0.9, one face at each 12-block X segment.
    if (cellX > -1) {
        if (localFace < BETA_CLOUD_SEGMENTS) {
            int segment = localFace;
            float x = x0 + float(segment) * BETA_CLOUD_SEGMENT_SIZE;
            float u = fract((float(baseGridX + cellX * 8 + segment) + 0.5) * BETA_CLOUD_TEXTURE_STEP);
            betaCloudEmitQuad(
                vec3(x, bottomY, z1), vec3(x, topY, z1),
                vec3(x, topY, z0), vec3(x, bottomY, z0),
                vec2(u, v1), vec2(u, v1), vec2(u, v0), vec2(u, v0), 0.9
            );
            return;
        }
        localFace -= BETA_CLOUD_SEGMENTS;
    }

    if (cellX <= 1) {
        if (localFace < BETA_CLOUD_SEGMENTS) {
            int segment = localFace;
            float x = x0 + (float(segment + 1) - BETA_CLOUD_EDGE_EPSILON) * BETA_CLOUD_SEGMENT_SIZE;
            float u = fract((float(baseGridX + cellX * 8 + segment) + 0.5) * BETA_CLOUD_TEXTURE_STEP);
            betaCloudEmitQuad(
                vec3(x, bottomY, z1), vec3(x, topY, z1),
                vec3(x, topY, z0), vec3(x, bottomY, z0),
                vec2(u, v1), vec2(u, v1), vec2(u, v0), vec2(u, v0), 0.9
            );
            return;
        }
        localFace -= BETA_CLOUD_SEGMENTS;
    }

    // Walls parallel to X: shade 0.8, one face at each 12-block Z segment.
    if (cellZ > -1) {
        if (localFace < BETA_CLOUD_SEGMENTS) {
            int segment = localFace;
            float z = z0 + float(segment) * BETA_CLOUD_SEGMENT_SIZE;
            float v = fract((float(baseGridZ + cellZ * 8 + segment) + 0.5) * BETA_CLOUD_TEXTURE_STEP);
            betaCloudEmitQuad(
                vec3(x0, topY, z), vec3(x1, topY, z),
                vec3(x1, bottomY, z), vec3(x0, bottomY, z),
                vec2(u0, v), vec2(u1, v), vec2(u1, v), vec2(u0, v), 0.8
            );
            return;
        }
        localFace -= BETA_CLOUD_SEGMENTS;
    }

    if (cellZ <= 1) {
        if (localFace < BETA_CLOUD_SEGMENTS) {
            int segment = localFace;
            float z = z0 + (float(segment + 1) - BETA_CLOUD_EDGE_EPSILON) * BETA_CLOUD_SEGMENT_SIZE;
            float v = fract((float(baseGridZ + cellZ * 8 + segment) + 0.5) * BETA_CLOUD_TEXTURE_STEP);
            betaCloudEmitQuad(
                vec3(x0, topY, z), vec3(x1, topY, z),
                vec3(x1, bottomY, z), vec3(x0, bottomY, z),
                vec2(u0, v), vec2(u1, v), vec2(u1, v), vec2(u0, v), 0.8
            );
        }
    }
}

void betaCloudEmitFaceOrdinal(int faceOrdinal) {
    int remaining = faceOrdinal;
    float cameraXModulo = float(betaCloudWrapInt(cameraPositionInt.x, BETA_CLOUD_GRID_SIZE));
    float cameraZModulo = float(betaCloudWrapInt(cameraPositionInt.z, BETA_CLOUD_GRID_SIZE));
    float scrollX = betaCloudScrollBlocks();
    float gridXFloat = (cameraXModulo + cameraPositionFract.x + scrollX) / BETA_CLOUD_SEGMENT_SIZE;
    float gridZFloat = (cameraZModulo + cameraPositionFract.z) / BETA_CLOUD_SEGMENT_SIZE + 0.33000001311302185;
    float fracX = fract(gridXFloat);
    float fracZ = fract(gridZFloat);
    int baseGridX = betaCloudWrapInt(int(floor(gridXFloat)), BETA_CLOUD_TEXTURE_SIZE);
    int baseGridZ = betaCloudWrapInt(int(floor(gridZFloat)), BETA_CLOUD_TEXTURE_SIZE);

    float bottomY = BETA_CLOUD_BASE + 0.33 - cameraPosition.y;
    float topY = BETA_CLOUD_BASE + 4.33 - BETA_CLOUD_EDGE_EPSILON - cameraPosition.y;

    for (int tileX = 0; tileX < BETA_CLOUD_TILE_COUNT; ++tileX) {
        for (int tileZ = 0; tileZ < BETA_CLOUD_TILE_COUNT; ++tileZ) {
            int cellX = tileX - 2;
            int cellZ = tileZ - 2;
            int cellFaceCount = 2
                + (cellX > -1 ? BETA_CLOUD_SEGMENTS : 0)
                + (cellX <= 1 ? BETA_CLOUD_SEGMENTS : 0)
                + (cellZ > -1 ? BETA_CLOUD_SEGMENTS : 0)
                + (cellZ <= 1 ? BETA_CLOUD_SEGMENTS : 0);

            if (remaining >= cellFaceCount) {
                remaining -= cellFaceCount;
                continue;
            }

            float x0 = float(cellX * BETA_CLOUD_TILE_SIZE) - fracX * BETA_CLOUD_SEGMENT_SIZE;
            float x1 = x0 + float(BETA_CLOUD_TILE_SIZE);
            float z0 = float(cellZ * BETA_CLOUD_TILE_SIZE) - fracZ * BETA_CLOUD_SEGMENT_SIZE;
            float z1 = z0 + float(BETA_CLOUD_TILE_SIZE);
            betaCloudEmitCellFace(
                remaining, cellX, cellZ, x0, x1, z0, z1,
                bottomY, topY, baseGridX, baseGridZ
            );
            return;
        }
    }
}

void main() {
#if BETA_CUSTOM_CLOUD_GEOMETRY
    // One source triangle dispatches 16 historical faces; 53 triangles cover all 840.
    // The geometry is emitted inside the native cloud draw to retain scene depth testing.
    int firstFace = gl_PrimitiveIDIn * 16;
    if (firstFace >= 840) return;
    for (int i = 0; i < 16; ++i) {
        int face = firstFace + i;
        if (face < 840) betaCloudEmitFaceOrdinal(face);
    }
#else
    // Modo estable: passthrough del mesh nativo. No depende de gl_PrimitiveIDIn
    // para reconstruir una malla global, porque Iris puede dividirlo en varios draws.
    for (int i = 0; i < 3; ++i) {
        gl_Position = gl_in[i].gl_Position;
        cloudColor = sourceCloudColor[i];
        cloudViewPos = sourceCloudViewPos[i];
        betaCloudUV = vec2(0.0);
        betaCloudShade = 1.0;
        EmitVertex();
    }
    EndPrimitive();
#endif
}
