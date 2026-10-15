#!/usr/bin/env python3
"""Generate an exact Java-Random permutation texture for Beta 1.7.3 climate noise.

Run from the repository root:
    python3 Beta173-Lighting/tools/generate_climate_seed.py --seed -123456789

The seed is the value returned by the world's /seed command. The generator writes
shaders/textures/beta173_climate_gradient.png and shaders/lib/climate_seed.glsl.
This is world-specific: do not reuse these generated files for worlds with another seed.
"""
from __future__ import annotations

import argparse
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

MASK = (1 << 48) - 1
MULTIPLIER = 0x5DEECE66D
ADDEND = 0xB
OCTAVES = 4


class JavaRandom:
    """Minimal bit-compatible java.util.Random (48-bit LCG)."""
    def __init__(self, seed: int):
        self.state = (seed ^ MULTIPLIER) & MASK

    def next_bits(self, bits: int) -> int:
        self.state = (self.state * MULTIPLIER + ADDEND) & MASK
        return self.state >> (48 - bits)

    def next_double(self) -> float:
        return ((self.next_bits(26) << 27) + self.next_bits(27)) / float(1 << 53)

    def next_int(self, bound: int) -> int:
        if bound <= 0:
            raise ValueError("bound debe ser positivo")
        if (bound & -bound) == bound:
            return (bound * self.next_bits(31)) >> 31
        while True:
            bits = self.next_bits(31)
            value = bits % bound
            # Java evalúa el sumador como int de 32 bits con signo.
            expr = (bits - value + (bound - 1)) & 0xFFFFFFFF
            if expr < 0x80000000:
                return value


@dataclass(frozen=True)
class Octave:
    offset_x: float
    offset_z: float
    permutation: tuple[int, ...]


def create_octaves(world_seed: int) -> list[Octave]:
    """Port of WorldChunkManager's NoiseGeneratorOctaves2(Random(seed*9871), 4)."""
    rng = JavaRandom(world_seed * 9871)
    octaves: list[Octave] = []
    for _ in range(OCTAVES):
        # NoiseGenerator2 consumes three nextDouble calls before shuffling.
        off_x = rng.next_double() * 256.0
        off_z = rng.next_double() * 256.0
        _unused_y_offset = rng.next_double() * 256.0
        permutation = list(range(256))
        for i in range(256):
            j = rng.next_int(256 - i) + i
            permutation[i], permutation[j] = permutation[j], permutation[i]
        octaves.append(Octave(off_x, off_z, tuple(permutation)))
    return octaves


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_texture(octaves: list[Octave], path: Path) -> None:
    """Write precomputed gradient indices to a 256x1024 lossless RGBA8 texture.

    Each 256-row band corresponds to one octave. Storing p[x + p[z]] % 12 in the
    texture reduces the shader's permutation lookup from two texture reads to one.
    """
    width, height = 256, OCTAVES * 256
    raw = bytearray()
    # PNG rows are top-to-bottom while OpenGL texelFetch uses bottom-to-top coordinates.
    for png_y in range(height):
        gl_y = height - 1 - png_y
        octave_index, z = divmod(gl_y, 256)
        permutation = octaves[octave_index].permutation
        raw.append(0)  # PNG filter: None
        for x in range(width):
            gradient_index = permutation[((x + permutation[z]) & 255)] % 12
            raw.extend((gradient_index, 0, 0, 255))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)  # RGBA8
    png = b"\x89PNG\r\n\x1a\n" + _png_chunk(b"IHDR", ihdr)
    png += _png_chunk(b"IDAT", zlib.compress(bytes(raw), level=9)) + _png_chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def generate_seed_glsl(world_seed: int, octaves: list[Octave], origin_x: int = 0, origin_z: int = 0) -> str:
    lines = [
        "// GENERADO por tools/generate_climate_seed.py; no editar a mano.",
        f"// World seed (comando /seed): {world_seed}",
        "// Offset de coordenadas opcional para compensar el wrapping de cameraPosition de Iris.",
        "#define BETA_CLIMATE_SEED_CONFIGURED 1",
        f"#define BETA_CLIMATE_ORIGIN_X {origin_x}.0",
        f"#define BETA_CLIMATE_ORIGIN_Z {origin_z}.0",
    ]
    for i, octave in enumerate(octaves):
        lines.append(
            f"const vec2 BETA_CLIMATE_OFFSET_{i} = vec2({octave.offset_x:.12f}, {octave.offset_z:.12f});"
        )
    lines.append("")
    return "\n".join(lines)


def generate(shader_root: Path, world_seed: int, origin_x: int = 0, origin_z: int = 0) -> tuple[Path, Path]:
    octaves = create_octaves(world_seed)
    texture_path = shader_root / "textures" / "beta173_climate_gradient.png"
    glsl_path = shader_root / "lib" / "climate_seed.glsl"
    write_texture(octaves, texture_path)
    glsl_path.parent.mkdir(parents=True, exist_ok=True)
    glsl_path.write_text(generate_seed_glsl(world_seed, octaves, origin_x, origin_z), encoding="utf-8")
    return texture_path, glsl_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", required=True, type=int, help="semilla exacta que devuelve /seed")
    parser.add_argument("--origin-x", type=int, default=0, help="corrección de X si cameraPosition se ha reiniciado")
    parser.add_argument("--origin-z", type=int, default=0, help="corrección de Z si cameraPosition se ha reiniciado")
    parser.add_argument("--shader-root", type=Path, default=Path(__file__).resolve().parents[1] / "shaders")
    args = parser.parse_args()
    texture, seed_source = generate(args.shader_root, args.seed, args.origin_x, args.origin_z)
    print(f"Semilla de mundo: {args.seed}")
    print(f"Textura: {texture}")
    print(f"Offsets: {seed_source}")
    print("Ahora construye un ZIP con tools/build_pack.py y úsalo solo en ese mundo/semilla.")
    print("Nota: cameraPosition de Iris puede hacer wrapping; usa --origin-x/--origin-z si corresponde.")
    return 0


# CPU reference path used by tests to validate the shader's noise formula.
_GRADIENTS_2D = (
    (1.0, 1.0), (-1.0, 1.0), (1.0, -1.0), (-1.0, -1.0),
    (1.0, 0.0), (-1.0, 0.0), (1.0, 0.0), (-1.0, 0.0),
    (0.0, 1.0), (0.0, -1.0), (0.0, 1.0), (0.0, -1.0),
)
_F2 = 0.5 * (3.0 ** 0.5 - 1.0)
_G2 = (3.0 - 3.0 ** 0.5) / 6.0


def _java_wrap(value: float) -> int:
    truncated = int(value)  # Python int, like Java's cast, truncates toward zero.
    return truncated if value > 0.0 else truncated - 1


def _corner(point_x: float, point_z: float, gradient_index: int) -> float:
    attenuation = 0.5 - point_x * point_x - point_z * point_z
    if attenuation < 0.0:
        return 0.0
    attenuation *= attenuation
    gx, gz = _GRADIENTS_2D[gradient_index]
    return attenuation * attenuation * (gx * point_x + gz * point_z)


def simplex_2d(point_x: float, point_z: float, octave: Octave) -> float:
    """Float64 reference of the exact NoiseGenerator2 simplex formula."""
    skew = (point_x + point_z) * _F2
    i = _java_wrap(point_x + skew)
    j = _java_wrap(point_z + skew)
    unskew = (i + j) * _G2
    x0 = point_x - (i - unskew)
    z0 = point_z - (j - unskew)
    i1, j1 = (1, 0) if x0 > z0 else (0, 1)
    x1, z1 = x0 - i1 + _G2, z0 - j1 + _G2
    x2, z2 = x0 - 1.0 + 2.0 * _G2, z0 - 1.0 + 2.0 * _G2
    p = octave.permutation
    g0 = p[((i & 255) + p[j & 255]) & 255] % 12
    g1 = p[((i & 255) + i1 + p[((j & 255) + j1) & 255]) & 255] % 12
    g2 = p[((i & 255) + 1 + p[((j & 255) + 1) & 255]) & 255] % 12
    return 70.0 * (_corner(x0, z0, g0) + _corner(x1, z1, g1) + _corner(x2, z2, g2))


def climate_temperature(world_seed: int, block_x: int, block_z: int) -> float:
    """Reproduce WorldChunkManager.getTemperature(x,z) on Beta 1.7.3."""
    value = 0.0
    frequency = amplitude = 1.0
    for octave in create_octaves(world_seed):
        px = (block_x * (0.02500000037252903 / 1.5) * frequency) + octave.offset_x
        pz = (block_z * (0.02500000037252903 / 1.5) * frequency) + octave.offset_z
        value += simplex_2d(px, pz, octave) * (0.55 / amplitude)
        frequency *= 0.5
        amplitude *= 0.5
    return value


if __name__ == "__main__":
    raise SystemExit(main())
