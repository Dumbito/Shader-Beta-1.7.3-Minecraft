"""Regression tests for the reconstructed Beta 1.7.3 climate/noise field."""
from __future__ import annotations

import gzip
import struct
import sys
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_climate_seed as climate  # noqa: E402
import configure_climate_pack as configure  # noqa: E402


def decode_rgba8_png(path: Path) -> tuple[int, int, bytes]:
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise AssertionError("firma PNG inválida")
    pos, width, height, compressed = 8, 0, 0, bytearray()
    while pos < len(data):
        size = struct.unpack(">I", data[pos:pos + 4])[0]
        kind = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + size]
        pos += size + 12
        if kind == b"IHDR":
            width, height, depth, color_type, comp, filt, interlace = struct.unpack(">IIBBBBB", body)
            if (depth, color_type, comp, filt, interlace) != (8, 6, 0, 0, 0):
                raise AssertionError("formato inesperado: se necesita RGBA8 sin entrelazado")
        elif kind == b"IDAT":
            compressed.extend(body)
    raw = zlib.decompress(bytes(compressed))
    stride = width * 4
    pixels = bytearray()
    for y in range(height):
        start = y * (stride + 1)
        if raw[start] != 0:
            raise AssertionError("filtro PNG inesperado")
        pixels.extend(raw[start + 1:start + 1 + stride])
    return width, height, bytes(pixels)


def nbt_string(value: str) -> bytes:
    encoded = value.encode("utf-8")
    return struct.pack(">H", len(encoded)) + encoded


def nbt_tag(tag_type: int, name: str, payload: bytes) -> bytes:
    return bytes((tag_type,)) + nbt_string(name) + payload


def nbt_long(name: str, value: int) -> bytes:
    return nbt_tag(4, name, struct.pack(">q", value))


def modern_level_dat(seed: int) -> bytes:
    world_gen = nbt_tag(10, "WorldGenSettings", nbt_long("seed", seed) + b"\x00")
    data = nbt_tag(10, "Data", world_gen + b"\x00")
    return gzip.compress(b"\x0a" + nbt_string("") + data + b"\x00")


def legacy_level_dat(seed: int) -> bytes:
    data = nbt_tag(10, "Data", nbt_long("RandomSeed", seed) + b"\x00")
    return gzip.compress(b"\x0a" + nbt_string("") + data + b"\x00")


class JavaRandomTests(unittest.TestCase):
    def test_matches_known_java_random_values(self):
        self.assertEqual(climate.JavaRandom(42).next_double(), 0.7275636800328681)
        rng = climate.JavaRandom(0)
        value = rng.next_bits(32)
        if value >= 1 << 31:
            value -= 1 << 32
        self.assertEqual(value, -1155484576)

    def test_next_int_matches_java_reference_sequence(self):
        rng = climate.JavaRandom(42)
        self.assertEqual([rng.next_int(bound) for bound in (251, 256, 255, 239)],
                         [55, 13, 153, 112])

    def test_next_int_produces_values_inside_bounds(self):
        rng = climate.JavaRandom(9876)
        self.assertTrue(all(0 <= rng.next_int(256) < 256 for _ in range(500)))
        self.assertTrue(all(0 <= rng.next_int(251) < 251 for _ in range(500)))


class LegacyClimateTests(unittest.TestCase):
    def test_noise_matches_pinned_reference_values(self):
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

    def test_each_world_seed_produces_four_distinct_octaves(self):
        a = climate.create_octaves(42)
        b = climate.create_octaves(43)
        self.assertEqual(len(a), 4)
        self.assertEqual(len(b), 4)
        for octave in a:
            self.assertEqual(sorted(octave.permutation), list(range(256)))
            self.assertGreaterEqual(octave.offset_x, 0.0)
            self.assertLess(octave.offset_x, 256.0)
            self.assertGreaterEqual(octave.offset_z, 0.0)
            self.assertLess(octave.offset_z, 256.0)
        self.assertNotEqual(a[0], b[0])

    def test_first_octave_offsets_match_java_reference(self):
        first = climate.create_octaves(123456789)[0]
        self.assertAlmostEqual(first.offset_x, 251.06314645013387, places=13)
        self.assertAlmostEqual(first.offset_z, 210.0285267002532, places=13)
        self.assertEqual(first.permutation[:10], (51, 0, 168, 69, 160, 183, 205, 249, 255, 214))

    def test_climate_field_changes_with_world_coordinates(self):
        values = {climate.climate_temperature(777, x, -x) for x in range(-512, 513, 64)}
        self.assertGreater(len(values), 8)


class SeedAssetTests(unittest.TestCase):
    def test_generated_texture_contains_the_permutation_lookup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "shaders"
            texture, seed_source = climate.generate(root, -123456789)
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
                        self.assertEqual(actual, expected)
            source = seed_source.read_text(encoding="utf-8")
            self.assertIn("#define BETA_CLIMATE_SEED_CONFIGURED 1", source)
            self.assertIn("World seed tomada de /seed o de Data.WorldGenSettings.seed: -123456789", source)
            for i in range(4):
                self.assertIn(f"BETA_CLIMATE_OFFSET_{i}", source)

    def test_generator_is_deterministic_for_same_seed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            texture_a, source_a = climate.generate(root / "a", 42)
            texture_b, source_b = climate.generate(root / "b", 42)
            self.assertEqual(texture_a.read_bytes(), texture_b.read_bytes())
            self.assertEqual(source_a.read_text(), source_b.read_text())


class LevelDatSeedTests(unittest.TestCase):
    def test_reads_modern_nested_world_gen_settings_seed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "level.dat"
            path.write_bytes(modern_level_dat(-123456789012345))
            self.assertEqual(configure.read_level_dat_seed(path), -123456789012345)

    def test_reads_legacy_random_seed_from_world_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            world = Path(tmp) / "World"
            world.mkdir()
            (world / "level.dat").write_bytes(legacy_level_dat(123456789))
            self.assertEqual(configure.read_level_dat_seed(world), 123456789)

    def test_missing_world_seed_explains_manual_seed_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "level.dat"
            path.write_bytes(gzip.compress(b"\x0a" + nbt_string("") + nbt_tag(10, "Data", b"\x00") + b"\x00"))
            with self.assertRaisesRegex(ValueError, "Usa --seed"):
                configure.read_level_dat_seed(path)


class PackAutomationTests(unittest.TestCase):
    def test_seed_pack_builds_without_mutating_source_files(self):
        source_props = ROOT / "shaders" / "shaders.properties"
        source_before = source_props.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            output = configure.build_seed_pack(-12345, Path(tmp))
            self.assertTrue(output.is_file())
            self.assertIn("neg12345", output.name)
            with zipfile.ZipFile(output) as archive:
                self.assertIsNone(archive.testzip())
                names = archive.namelist()
                self.assertIn("BETA173-CLIMATE-INFO.txt", names)
                self.assertIn("shaders/textures/beta173_climate_gradient.png", names)
                self.assertIn("shaders/shaders.properties", names)
                props = archive.read("shaders/shaders.properties").decode("utf-8")
                self.assertIn("customTexture.beta173ClimateGradient", props)
                sky = archive.read("shaders/gbuffers_skybasic.fsh").decode("utf-8")
                self.assertNotIn("#include", sky)
                self.assertIn("#define BETA_CLIMATE_SEED_CONFIGURED 1", sky)
                self.assertIn("beta173ClimateTemperature", sky)
            self.assertEqual(source_before, source_props.read_text(encoding="utf-8"))

    def test_unconfigured_source_uses_automatic_universal_fallback(self):
        props = (ROOT / "shaders" / "shaders.properties").read_text(encoding="utf-8")
        self.assertNotIn("customTexture.beta173ClimateGradient", props)
        seed = (ROOT / "shaders" / "lib" / "climate_seed.glsl").read_text(encoding="utf-8")
        self.assertIn("#define BETA_CLIMATE_SEED_CONFIGURED 0", seed)
        beta = (ROOT / "shaders" / "lib" / "beta173.glsl").read_text(encoding="utf-8")
        self.assertIn("uniform float temperature;", beta)
        self.assertIn("return temperature;", beta)
        self.assertIn("beta173LegacyClimateAvailable", beta)
        self.assertIn("beta173LegacySkyRgb", beta)

    def test_iris_base_temperature_is_only_the_fallback_when_seed_is_unavailable(self):
        beta = (ROOT / "shaders" / "lib" / "beta173.glsl").read_text(encoding="utf-8")
        helper_branch = beta.index("if (beta173LegacyClimateAvailable) return beta173LegacyClimateTemperature;")
        baked_seed_branch = beta.index("#if BETA_CLIMATE_SEED_CONFIGURED", helper_branch)
        universal_fallback = beta.index("return temperature;", baked_seed_branch)
        self.assertLess(helper_branch, baked_seed_branch)
        self.assertLess(baked_seed_branch, universal_fallback)
        self.assertIn("if (beta173LegacyClimateAvailable) return beta173LegacySkyRgb;", beta)


class ShaderIntegrationTests(unittest.TestCase):
    def test_fog_programs_evaluate_climate_per_vertex_not_per_fragment(self):
        for name in ("gbuffers_terrain", "gbuffers_textured_lit"):
            vertex = (ROOT / "shaders" / f"{name}.vsh").read_text(encoding="utf-8")
            fragment = (ROOT / "shaders" / f"{name}.fsh").read_text(encoding="utf-8")
            self.assertIn("flat out float beta173ClimateTemperatureVarying", vertex)
            self.assertIn("beta173ClimateTemperatureVarying = beta173SkyClimateTemperature()", vertex)
            self.assertIn("flat in float beta173ClimateTemperatureVarying", fragment)
            self.assertIn("#define BETA_CLIMATE_USE_VARYING", fragment)
            self.assertLess(fragment.index("#define BETA_CLIMATE_USE_VARYING"),
                            fragment.index('#include "/lib/beta173.glsl"'))

    def test_seed_specific_custom_texture_is_not_required_by_default_pack(self):
        props = (ROOT / "shaders" / "shaders.properties").read_text(encoding="utf-8")
        seed = (ROOT / "shaders" / "lib" / "climate_seed.glsl").read_text(encoding="utf-8")
        noise = (ROOT / "shaders" / "lib" / "climate_noise.glsl").read_text(encoding="utf-8")
        beta = (ROOT / "shaders" / "lib" / "beta173.glsl").read_text(encoding="utf-8")
        self.assertNotIn("customTexture.beta173ClimateGradient", props)
        self.assertIn("#define BETA_CLIMATE_SEED_CONFIGURED 0", seed)
        self.assertIn("uniform sampler2D beta173ClimateGradient", noise)
        self.assertIn("return floor(clamp(rgb, 0.0, 1.0) * 255.0) / 255.0;", beta)
        self.assertIn("relativeEyePosition.xz", beta)


if __name__ == "__main__":
    unittest.main()
