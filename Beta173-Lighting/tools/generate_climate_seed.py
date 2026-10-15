#!/usr/bin/env python3
"""Genera los datos seed-specific del ruido climatico de Minecraft Beta 1.7.3.

Uso desde la raiz del repositorio:
    python3 Beta173-Lighting/tools/generate_climate_seed.py --seed 123456789

Para jugadores, se recomienda tools/configure_climate_pack.py: genera el ZIP completo en
una carpeta temporal, sin editar los archivos del repositorio ni reemplazar otros packs.
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
    """Subset of java.util.Random with its exact 48-bit LCG behavior."""
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
            # Replica el overflow de int con signo de java.util.Random.nextInt.
            expression = (bits - value + (bound - 1)) & 0xFFFFFFFF
            if expression < (1 << 31):
                return value


@dataclass(frozen=True)
class Octave:
    offset_x: float
    offset_z: float
    permutation: tuple[int, ...]


def create_octaves(world_seed: int) -> list[Octave]:
    """Port de WorldChunkManager -> NoiseGeneratorOctaves2(seed * 9871, 4)."""
    rng = JavaRandom(world_seed * 9871)
    octaves: list[Octave] = []
    for _ in range(OCTAVES):
        # NoiseGenerator2 consume tres nextDouble antes de mezclar la permutacion.
        offset_x = rng.next_double() * 256.0
        offset_z = rng.next_double() * 256.0
        _unused_y_offset = rng.next_double() * 256.0
        permutation = list(range(256))
        for i in range(256):
            j = rng.next_int(256 - i) + i
            permutation[i], permutation[j] = permutation[j], permutation[i]
        octaves.append(Octave(offset_x, offset_z, tuple(permutation)))
    return octaves


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def write_texture(octaves: list[Octave], path: Path) -> None:
    """Escribe una tabla lossless RGBA8 (256 x 1024) con los indices de gradiente.

    Una banda de 256 filas por octava. Cada texel precalcula p[x + p[z]] % 12.
    El shader hace texelFetch para no interpolar datos discretos.
    """
    width, height = 256, OCTAVES * 256
    raw = bytearray()
    # OpenGL accede por la fila 0 inferior; el PNG convencional se almacena desde arriba.
    for png_y in range(height):
        gl_y = height - 1 - png_y
        octave_index, z = divmod(gl_y, 256)
        permutation = octaves[octave_index].permutation
        raw.append(0)  # PNG filter None
        for x in range(width):
            gradient_index = permutation[(x + permutation[z]) & 255] % 12
            raw.extend((gradient_index, 0, 0, 255))

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _png_chunk(b"IHDR", ihdr)
    png += _png_chunk(b"IDAT", zlib.compress(bytes(raw), level=9))
    png += _png_chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def generate_seed_glsl(world_seed: int, octaves: list[Octave]) -> str:
    lines = [
        "// GENERADO por tools/generate_climate_seed.py; no editar a mano.",
        f"// World seed tomada de /seed o de Data.WorldGenSettings.seed: {world_seed}",
        "#define BETA_CLIMATE_SEED_CONFIGURED 1",
    ]
    for i, octave in enumerate(octaves):
        lines.append(
            f"const vec2 BETA_CLIMATE_OFFSET_{i} = "
            f"vec2({octave.offset_x:.12f}, {octave.offset_z:.12f});"
        )
    lines.append("")
    return "\n".join(lines)


def generate(shader_root: Path, world_seed: int) -> tuple[Path, Path]:
    octaves = create_octaves(world_seed)
    texture_path = shader_root / "textures" / "beta173_climate_gradient.png"
    glsl_path = shader_root / "lib" / "climate_seed.glsl"
    write_texture(octaves, texture_path)
    glsl_path.parent.mkdir(parents=True, exist_ok=True)
    glsl_path.write_text(generate_seed_glsl(world_seed, octaves), encoding="utf-8")
    return texture_path, glsl_path


# CPU reference implementation ported from NoiseGenerator2/NoiseGeneratorOctaves2.
# Kept here so regression tests can detect unintended changes to the mathematical model.
_GRADIENTS_2D = (
    (1.0, 1.0), (-1.0, 1.0), (1.0, -1.0), (-1.0, -1.0),
    (1.0, 0.0), (-1.0, 0.0), (1.0, 0.0), (-1.0, 0.0),
    (0.0, 1.0), (0.0, -1.0), (0.0, 1.0), (0.0, -1.0),
)
_F2 = (3.0 ** 0.5 - 1.0) / 2.0
_G2 = (3.0 - 3.0 ** 0.5) / 6.0


def _java_wrap(value: float) -> int:
    truncated = int(value)  # Java double-to-int conversion truncates toward zero.
    return truncated if value > 0.0 else truncated - 1


def _corner(x: float, z: float, gradient_index: int) -> float:
    attenuation = 0.5 - x * x - z * z
    if attenuation < 0.0:
        return 0.0
    attenuation *= attenuation
    gx, gz = _GRADIENTS_2D[gradient_index]
    return attenuation * attenuation * (gx * x + gz * z)


def simplex_2d(x: float, z: float, permutation: tuple[int, ...]) -> float:
    skew = (x + z) * _F2
    i = _java_wrap(x + skew)
    j = _java_wrap(z + skew)
    unskew = (i + j) * _G2
    x0 = x - (i - unskew)
    z0 = z - (j - unskew)
    i1, j1 = (1, 0) if x0 > z0 else (0, 1)
    x1, z1 = x0 - i1 + _G2, z0 - j1 + _G2
    x2, z2 = x0 - 1.0 + 2.0 * _G2, z0 - 1.0 + 2.0 * _G2
    p = permutation
    g0 = p[((i & 255) + p[j & 255]) & 255] % 12
    g1 = p[((i & 255) + i1 + p[((j & 255) + j1) & 255]) & 255] % 12
    g2 = p[((i & 255) + 1 + p[((j & 255) + 1) & 255]) & 255] % 12
    return 70.0 * (
        _corner(x0, z0, g0) + _corner(x1, z1, g1) + _corner(x2, z2, g2)
    )


def climate_temperature(world_seed: int, block_x: int, block_z: int) -> float:
    """Reproduce WorldChunkManager.getTemperature(x,z) using double precision."""
    value = 0.0
    frequency = amplitude = 1.0
    for octave in create_octaves(world_seed):
        px = block_x * (0.02500000037252903 / 1.5) * frequency + octave.offset_x
        pz = block_z * (0.02500000037252903 / 1.5) * frequency + octave.offset_z
        value += simplex_2d(px, pz, octave.permutation) * (0.55 / amplitude)
        frequency *= 0.5
        amplitude *= 0.5
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", required=True, type=int, help="semilla exacta de /seed")
    parser.add_argument(
        "--shader-root",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "shaders",
    )
    args = parser.parse_args()
    if not -(1 << 63) <= args.seed < (1 << 63):
        parser.error("--seed debe caber en un long firmado de Java (64 bits)")
    texture, source = generate(args.shader_root, args.seed)
    print(f"Semilla: {args.seed}")
    print(f"Textura climatica: {texture}")
    print(f"Offsets por octava: {source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
