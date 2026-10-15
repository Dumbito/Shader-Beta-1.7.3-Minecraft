"""Static regression tests for the Beta 1.7.3 cloud geometry port."""
from __future__ import annotations

import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHADERS = ROOT / "shaders"


def png_size(path: Path) -> tuple[int, int, int, int]:
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise AssertionError(f"invalid PNG signature: {path}")
    pos = 8
    while pos < len(data):
        size = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + size]
        if tag == b"IHDR":
            width, height, depth, color_type, *_ = struct.unpack(">IIBBBBB", body)
            return width, height, depth, color_type
        pos += size + 12
    raise AssertionError("IHDR chunk not found")


class BetaCloudGeometryTests(unittest.TestCase):
    def test_original_cloud_texture_is_256_rgba_png(self):
        width, height, depth, color_type = png_size(SHADERS / "textures" / "beta173_clouds.png")
        self.assertEqual((width, height, depth, color_type), (256, 256, 8, 6))

    def test_iris_cloud_program_is_enabled_and_uses_custom_texture(self):
        props = (SHADERS / "shaders.properties").read_text(encoding="utf-8")
        self.assertIn("clouds=fancy", props)
        self.assertIn("customTexture.beta173CloudMap = textures/beta173_clouds.png", props)
        self.assertTrue((SHADERS / "gbuffers_clouds.gsh").is_file())

    def test_grid_geometry_matches_beta_dimensions(self):
        source = (SHADERS / "gbuffers_clouds.gsh").read_text(encoding="utf-8")
        for expression in (
            "BETA_CLOUD_TILE_COUNT = 6",
            "BETA_CLOUD_SEGMENTS = 8",
            "BETA_CLOUD_TILE_SIZE = 96",
            "BETA_CLOUD_SEGMENT_SIZE = 12.0",
            "BETA_CLOUD_EDGE_EPSILON = 0.0009765625",
            "firstFace = gl_PrimitiveIDIn * 16",
            "face < 840",
        ):
            self.assertIn(expression, source)

    def test_cloud_shading_alpha_scroll_and_depth_space_are_retained(self):
        gsh = (SHADERS / "gbuffers_clouds.gsh").read_text(encoding="utf-8")
        fsh = (SHADERS / "gbuffers_clouds.fsh").read_text(encoding="utf-8")
        cfg = (SHADERS / "lib" / "config.glsl").read_text(encoding="utf-8")
        self.assertIn("#define BETA_CUSTOM_CLOUD_GEOMETRY 0 // [0 1]", cfg)
        self.assertIn("#elif BETA_CUSTOM_CLOUD_GEOMETRY", fsh)
        self.assertIn("#if BETA_CUSTOM_CLOUD_GEOMETRY", gsh)
        # Estable por defecto: pasa el mesh original y conserva el alfa del motor.
        self.assertIn("cloudColor = sourceCloudColor[i];", gsh)
        self.assertIn("cloudViewPos = sourceCloudViewPos[i];", gsh)
        self.assertIn("fragColor = vec4(beta173CloudColor() * beta173CloudFaceShade(), cloudColor.a);", fsh)
        for shade in ("1.0", "0.7", "0.9", "0.8"):
            self.assertIn(shade, gsh)
        self.assertIn("ticks * 0.03", gsh)
        self.assertIn("gbufferProjection * viewPosition", gsh)
        self.assertIn("0.8 * mask.a", fsh)

    def test_texture_metadata_uses_crisp_wrapped_cloud_mask(self):
        meta = (SHADERS / "textures" / "beta173_clouds.png.mcmeta").read_text(encoding="utf-8")
        self.assertIn('"blur": false', meta)
        self.assertIn('"clamp": false', meta)


if __name__ == "__main__":
    unittest.main()
