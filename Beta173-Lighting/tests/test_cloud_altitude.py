"""Regression tests for modernized cloud altitude and viewing above the cloud layer.

These tests validate configuration and the source-level face-shading contract.
They do not replace an in-game test with Iris/Sodium.
"""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHADERS = ROOT / "shaders"


class CloudAltitudeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = (SHADERS / "lib" / "config.glsl").read_text(encoding="utf-8")
        cls.vertex = (SHADERS / "gbuffers_clouds.vsh").read_text(encoding="utf-8")
        cls.fragment = (SHADERS / "gbuffers_clouds.fsh").read_text(encoding="utf-8")

    def test_cloud_height_is_remapped_for_modern_overworld(self):
        self.assertIn("#define BETA_CLOUD_HEIGHT 260.99", self.config)
        self.assertIn("#define BETA_VANILLA_CLOUD_HEIGHT 192.33", self.config)
        # Beta height ratio 108.33 / 128 mapped into modern [-64, 320]: approx 260.99.
        modern_remap = -64.0 + (108.33 / 128.0) * (320.0 - (-64.0))
        self.assertAlmostEqual(modern_remap, 260.99, places=2)

    def test_vertex_shader_offsets_native_cloud_mesh_to_configured_height(self):
        self.assertIn(
            "viewPos.xyz += gbufferModelView[1].xyz * (BETA_CLOUD_HEIGHT - BETA_VANILLA_CLOUD_HEIGHT);",
            self.vertex,
        )
        self.assertIn("#ifdef BETA_CLOUD_HEIGHT_FIX", self.vertex)

    def test_top_and_underside_shading_is_independent_of_camera_side(self):
        # The sign of the visible face normal distinguishes top from underside.
        face = self.fragment.split("float beta173CloudFaceShade()", 1)[1].split("\n}", 1)[0]
        self.assertIn("if (abs(nWorld.y) > 0.5)", face)
        self.assertIn("return nWorld.y > 0.0 ? 1.0 : 0.7;", face)
        self.assertNotIn("worldY > BETA_CLOUD_BASE", face)
        self.assertNotIn("cameraPosition.y", face)

    def test_side_face_shading_remains_beta_style(self):
        face = self.fragment.split("float beta173CloudFaceShade()", 1)[1].split("\n}", 1)[0]
        self.assertIn("return abs(nWorld.x) > abs(nWorld.z) ? 0.9 : 0.8;", face)


if __name__ == "__main__":
    unittest.main()
