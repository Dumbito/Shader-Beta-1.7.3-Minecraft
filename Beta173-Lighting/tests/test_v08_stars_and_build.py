"""Pruebas del mapa de estrellas de Beta y del empaquetado sin #include (v0.8).

Ejecutar desde la raiz del repositorio:
    python3 -m unittest discover -s Beta173-Lighting/tests -v

No compilan GLSL ni prueban el resultado visual dentro de Minecraft.
"""
from __future__ import annotations

import math
import struct
import sys
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_pack  # noqa: E402
import generate_starmap as gs  # noqa: E402


def read_gray_png(path: Path) -> np.ndarray:
    data = path.read_bytes()
    pos, idat, w, h = 8, b"", 0, 0
    while pos < len(data):
        n, tag = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        pos += 12 + n
        if tag == b"IHDR":
            w, h = struct.unpack(">II", body[:8])
        elif tag == b"IDAT":
            idat += body
    raw = zlib.decompress(idat)
    return np.frombuffer(raw, dtype=np.uint8).reshape(h, w + 1)[:, 1:]


def to_pixel(direction, width, height):
    x, y, z = direction
    u = math.atan2(x, z) / (2 * math.pi) + 0.5
    v = math.asin(max(-1.0, min(1.0, y))) / math.pi + 0.5
    return min(height - 1, int(v * height)), min(width - 1, int(u * width))


def world_to_star_frame(d, theta):
    """Copia en Python de beta173WorldToStarFrame (GLSL)."""
    s, c = math.sin(theta), math.cos(theta)
    return (d[2], d[1] * c - d[0] * s, -d[1] * s - d[0] * c)


def star_frame_to_world(p, theta):
    """Rx(theta) y luego Ry(-90 grados): el marco con el que el juego dibuja sol y luna."""
    x, y, z = p
    s, c = math.sin(theta), math.cos(theta)
    y1, z1 = y * c - z * s, y * s + z * c
    return (-z1, y1, x)


class JavaRandomTests(unittest.TestCase):
    def test_matches_known_java_values(self):
        self.assertEqual(gs.JavaRandom(42).next_double(), 0.7275636800328681)
        value = gs.JavaRandom(0)._next(32)
        if value >= 1 << 31:
            value -= 1 << 32
        self.assertEqual(value, -1155484576)


class StarGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stars = gs.beta_stars()

    def test_accepted_star_count_is_stable(self):
        # Beta hace 1500 intentos y solo acepta los puntos dentro de la esfera unidad
        self.assertEqual(len(self.stars), 780)

    def test_quads_are_flat_square_and_tangent(self):
        for center, size, quad in self.stars[:200]:
            c = np.array(center)
            offsets = quad - c * gs.STAR_RADIUS
            self.assertLess(float(np.abs(offsets @ c).max()), 1e-9)
            e1, e2 = quad[1] - quad[0], quad[3] - quad[0]
            self.assertAlmostEqual(float(np.linalg.norm(e1)), 2 * size, places=9)
            self.assertAlmostEqual(float(np.linalg.norm(e2)), 2 * size, places=9)
            self.assertAlmostEqual(float(e1 @ e2), 0.0, places=9)

    def test_sizes_match_beta_range(self):
        sizes = [s for _, s, _ in self.stars]
        self.assertGreaterEqual(min(sizes), 0.25)
        self.assertLess(max(sizes), 0.5)


class StarMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = ROOT / "shaders" / "textures" / "starmap.png"
        cls.img = read_gray_png(cls.path)
        cls.stars = gs.beta_stars()

    def test_map_has_expected_size(self):
        self.assertEqual(self.img.shape, (gs.MAP_HEIGHT, gs.MAP_WIDTH))

    def test_every_star_center_is_lit(self):
        h, w = self.img.shape
        for center, _, _ in self.stars:
            row, col = to_pixel(center, w, h)
            self.assertGreater(int(self.img[row, col]), 0, f"estrella sin pintar en {center}")

    def test_far_from_stars_is_dark(self):
        h, w = self.img.shape
        lit = int((self.img > 0).sum())
        self.assertLess(lit / (h * w), 0.02)
        self.assertGreater(lit, 10000)

    def test_map_matches_generator(self):
        fresh = gs.rasterize(self.stars)
        self.assertTrue(np.array_equal(fresh, self.img), "starmap.png no coincide con generate_starmap.py")


class StarFrameTests(unittest.TestCase):
    def test_round_trip(self):
        for theta in (0.0, 0.7, 2.1, 4.0, 6.0):
            for local in ((0.0, 1.0, 0.0), (0.3, 0.5, math.sqrt(1 - 0.34)), (1.0, 0.0, 0.0)):
                world = star_frame_to_world(local, theta)
                back = world_to_star_frame(world, theta)
                for a, b in zip(local, back):
                    self.assertAlmostEqual(a, b, places=9)

    def test_sun_path_east_to_west(self):
        # angulo celeste 0 = mediodia (arriba), 0.25 = atardecer (oeste, -X), 0.75 = amanecer (este, +X)
        noon = star_frame_to_world((0, 1, 0), 0.0)
        sunset = star_frame_to_world((0, 1, 0), 0.25 * 2 * math.pi)
        sunrise = star_frame_to_world((0, 1, 0), 0.75 * 2 * math.pi)
        self.assertAlmostEqual(noon[1], 1.0, places=9)
        self.assertAlmostEqual(sunset[0], -1.0, places=9)
        self.assertAlmostEqual(sunrise[0], 1.0, places=9)


class ShaderSourceTests(unittest.TestCase):
    def test_skybasic_uses_same_frame_as_python(self):
        src = (ROOT / "shaders" / "gbuffers_skybasic.fsh").read_text(encoding="utf-8")
        self.assertIn("return vec3(d.z, d.y * c - d.x * s, -d.y * s - d.x * c);", src)
        self.assertIn("atan(local.x, local.z) / (BETA_PI * 2.0) + 0.5", src)
        self.assertIn("asin(clamp(local.y, -1.0, 1.0)) / BETA_PI + 0.5", src)

    def test_properties_reference_existing_star_map(self):
        props = (ROOT / "shaders" / "shaders.properties").read_text(encoding="utf-8")
        self.assertIn("texture.noise=textures/starmap.png", props)
        self.assertTrue((ROOT / "shaders" / "textures" / "starmap.png").is_file())

    def test_cloud_constants_keep_beta_shading_with_modern_height(self):
        cfg = (ROOT / "shaders" / "lib" / "config.glsl").read_text(encoding="utf-8")
        self.assertIn("#define BETA_CLOUD_HEIGHT 260.99", cfg)
        frag = (ROOT / "shaders" / "gbuffers_clouds.fsh").read_text(encoding="utf-8")
        for shade in ("1.0 : 0.7", "0.9 : 0.8"):
            self.assertIn(shade, frag)


class BuildPackTests(unittest.TestCase):
    def test_zip_has_no_includes_and_shaders_at_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = build_pack.write_zip("test", Path(tmp))
            with zipfile.ZipFile(out) as zf:
                self.assertIsNone(zf.testzip())
                names = zf.namelist()
                self.assertTrue(all(n.startswith("shaders/") or n == "README.md" for n in names))
                self.assertIn("shaders/shaders.properties", names)
                self.assertIn("shaders/textures/starmap.png", names)
                self.assertFalse([n for n in names if n.startswith("shaders/lib/")])
                for n in names:
                    if n.endswith((".vsh", ".fsh")):
                        text = zf.read(n).decode("utf-8")
                        self.assertNotIn("#include", text, n)
                        self.assertTrue(text.startswith("#version 330 compatibility"), n)

    def test_overrides_change_only_the_built_zip(self):
        before = (ROOT / "shaders" / "lib" / "config.glsl").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            out = build_pack.write_zip("t", Path(tmp), {"BETA_DEBUG": "1", "BETA_STAR_FIELD": "off"})
            with zipfile.ZipFile(out) as zf:
                sky = zf.read("shaders/gbuffers_skybasic.fsh").decode("utf-8")
        self.assertIn("#define BETA_DEBUG 1", sky)
        self.assertIn("// BETA_STAR_FIELD desactivado", sky)
        self.assertNotIn("#define BETA_STAR_FIELD", sky)
        self.assertEqual(before, (ROOT / "shaders" / "lib" / "config.glsl").read_text(encoding="utf-8"))
        with self.assertRaises(KeyError):
            build_pack.build_files({"BETA_NO_EXISTE": "1"})

    def test_every_source_include_exists(self):
        import re
        for path in (ROOT / "shaders").rglob("*"):
            if path.suffix in {".vsh", ".fsh", ".glsl"}:
                for inc in re.findall(r'#include "([^"]+)"', path.read_text(encoding="utf-8")):
                    self.assertTrue((ROOT / "shaders" / inc.lstrip("/")).is_file(), f"{path.name} -> {inc}")


if __name__ == "__main__":
    unittest.main()
