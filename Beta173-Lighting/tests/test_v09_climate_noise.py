"""Tests for the Beta 1.7.3 climate/noise port and seed texture generator."""
from __future__ import annotations

import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_climate_seed as climate


def decode_rgba8_png(path: Path) -> tuple[int, int, bytes]:
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise AssertionError("PNG signature inválida")
    pos, chunks, width, height, raw = 8, {}, 0, 0, b""
    while pos < len(data):
        size = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + size]
        pos += size + 12
        chunks[tag] = body
        if tag == b"IHDR":
            width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", body)
            if (bit_depth, color_type, compression, filtering, interlace) != (8, 6, 0, 0, 0):
                raise AssertionError("Solo se admite PNG RGBA8 sin entrelazado")
        elif tag == b"IDAT":
            raw += body
    rows = zlib.decompress(raw)
    stride = width * 4
    pix = bytearray()
    for y in range(height):
        offset = y * (stride + 1)
        if rows[offset] != 0:
            raise AssertionError("Filtro PNG inesperado")
        pix.extend(rows[offset + 1:offset + 1 + stride])
    return width, height, bytes(pix)


class JavaRandomTests(unittest.TestCase):
    def test_known_java_random_values(self):
        self.assertEqual(climate.JavaRandom(42).next_double(), 0.7275636800328681)
        value = climate.JavaRandom(0).next_bits(32)
        if value >= 1 << 31:
            value -= 1 << 32
        self.assertEqual(value, -1155484576)


class LegacyClimateTests(unittest.TestCase):
    def test_seeded_noise_matches_reference_values_from_java_port(self):
        cases = (
            (0, 0, 0, 0.10756615286025406),
            (0, 100, 200, 1.4942328627451067),
            (0, -100, -200, -1.9186637877363122),
            (42, 0, 0, 0.9949961836974850),
            (-123456789, 12345, -9876, 2.3235507113419720),
        )
        for seed, x, z, expected in cases:
            with self.subTest(seed=seed, x=x, z=z):
                self.assertAlmostEqual(climate.climate_temperature(seed, x, z), expected, places=12)

    def test_octaves_have_independent_permutations_and_valid_offsets(self):
        octaves = climate.create_octaves(123456789)
        self.assertEqual(len(octaves), 4)
        for octave in octaves:
            self.assertEqual(sorted(octave.permutation), list(range(256)))
            self.assertGreaterEqual(octave.offset_x, 0.0)
            self.assertLess(octave.offset_x, 256.0)
            self.assertGreaterEqual(octave.offset_z, 0.0)
            self.assertLess(octave.offset_z, 256.0)
        self.assertEqual(len({o.permutation for o in octaves}), 4)

    def test_coordinate_changes_change_the_climate_field(self):
        values = {climate.climate_temperature(777, x, -x) for x in range(-512, 513, 64)}
        self.assertGreater(len(values), 8)


class ShaderPortTests(unittest.TestCase):
    def test_sky_uses_high_precision_player_position_not_camera_location_alone(self):
        source = (ROOT / "shaders" / "lib" / "beta173.glsl").read_text(encoding="utf-8")
        self.assertIn("uniform ivec3 cameraPositionInt;", source)
        self.assertIn("uniform vec3 cameraPositionFract;", source)
        self.assertIn("uniform vec3 eyePosition;", source)
        self.assertIn("cameraWorldXZ + (eyePosition.xz - cameraPosition.xz)", source)
        self.assertIn("floor(playerWorldXZ + vec2(BETA_CLIMATE_ORIGIN_X, BETA_CLIMATE_ORIGIN_Z))", source)

    def test_hsb_conversion_matches_java_rgb_byte_rounding(self):
        source = (ROOT / "shaders" / "lib" / "beta173.glsl").read_text(encoding="utf-8")
        self.assertIn("int sector = int(h);", source)
        self.assertIn("return floor(rgb * 255.0 + 0.5) / 255.0;", source)


class GeneratedAssetTests(unittest.TestCase):
    def test_shader_texture_y_index_compensates_png_scanline_order(self):
        shader = (ROOT / "shaders" / "lib" / "climate_noise.glsl").read_text(encoding="utf-8")
        self.assertIn("1023 - (octave * 256 + (z & 255))", shader)

    def test_shader_sampler_and_gradient_function_use_distinct_identifiers(self):
        shader = (ROOT / "shaders" / "lib" / "climate_noise.glsl").read_text(encoding="utf-8")
        self.assertIn("uniform sampler2D beta173ClimateGradient;", shader)
        self.assertIn("vec2 beta173ClimateGradientVector(int index)", shader)
        self.assertIn("beta173ClimateGradientVector(gradientIndex)", shader)

    def test_generates_seed_specific_png_and_glsl_offsets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "shaders"
            texture, seed_source = climate.generate(root, -123456789, origin_x=30000, origin_z=-15000)
            self.assertTrue(texture.is_file())
            self.assertTrue(seed_source.is_file())
            width, height, pixels = decode_rgba8_png(texture)
            self.assertEqual((width, height), (256, 1024))
            octaves = climate.create_octaves(-123456789)
            for octave_index, octave in enumerate(octaves):
                for z in (0, 1, 127, 255):
                    gl_y = octave_index * 256 + z
                    png_y = height - 1 - gl_y
                    for x in (0, 1, 127, 255):
                        expected = octave.permutation[(x + octave.permutation[z]) & 255] % 12
                        actual = pixels[(png_y * width + x) * 4]
                        self.assertEqual(actual, expected, (octave_index, x, z))
            glsl = seed_source.read_text(encoding="utf-8")
            self.assertIn("#define BETA_CLIMATE_SEED_CONFIGURED 1", glsl)
            self.assertIn("#define BETA_CLIMATE_ORIGIN_X 30000.0", glsl)
            self.assertIn("#define BETA_CLIMATE_ORIGIN_Z -15000.0", glsl)
            self.assertIn("World seed (comando /seed): -123456789", glsl)
            for i in range(4):
                self.assertIn(f"BETA_CLIMATE_OFFSET_{i}", glsl)


if __name__ == "__main__":
    unittest.main()
