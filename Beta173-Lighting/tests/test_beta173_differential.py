"""Differential regression checks against the reconstructed Beta 1.7.3 Java source.

Reference:
  https://github.com/jacobo-mc/mc_b1.7.3_release
  WorldProvider.java: generateLightBrightnessTable(), calculateCelestialAngle()
  World.java: calculateSkylightSubtracted(), getStarBrightness()
  EntityRenderer.java: updateFogColor()

Run:
  python -m unittest discover -s Beta173-Lighting/tests -v

The Java equations below are transcribed from the cited source, not executed
inside a JVM. GLSL is mirrored in Python for numerical comparison. This tests
the mathematical port; it does not compile shaders or prove visual equivalence.
"""
from __future__ import annotations

import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHADER = ROOT / "shaders" / "lib" / "beta173.glsl"
CONFIG = ROOT / "shaders" / "lib" / "config.glsl"
TAU = math.tau


# Transcription of WorldProvider.calculateCelestialAngle(long, float).
def java_celestial_angle(world_time: int, partial_ticks: float = 0.0) -> float:
    angle = ((world_time % 24000) + partial_ticks) / 24000.0 - 0.25
    if angle < 0.0:
        angle += 1.0
    if angle > 1.0:
        angle -= 1.0
    original = angle
    angle = 1.0 - (math.cos(angle * math.pi) + 1.0) / 2.0
    return original + (angle - original) / 3.0


# Transcription of WorldProvider.generateLightBrightnessTable().
def java_brightness(level: int, ambient: float = 0.05) -> float:
    inverted = 1.0 - level / 15.0
    return (1.0 - inverted) / (inverted * 3.0 + 1.0) * (1.0 - ambient) + ambient


# Transcription of World.calculateSkylightSubtracted(float), at partial ticks 0.
def java_sky_subtracted(world_time: int, rain: float = 0.0,
                        weighted_thunder: float = 0.0) -> int:
    angle = java_celestial_angle(world_time)
    factor = min(1.0, max(0.0, math.cos(angle * TAU) * 2.0 + 0.5))
    factor *= 1.0 - rain * 5.0 / 16.0
    factor *= 1.0 - weighted_thunder * 5.0 / 16.0
    return int((1.0 - factor) * 11.0)


# Transcription of World.getStarBrightness(float), at partial ticks 0.
def java_star_brightness(world_time: int) -> float:
    angle = java_celestial_angle(world_time)
    value = min(1.0, max(0.0, 1.0 - (math.cos(angle * TAU) * 2.0 + 0.75)))
    return value * value * 0.5


# Python mirrors of the relevant v0.5 GLSL functions.
def glsl_brightness(level: int, ambient: float = 0.05) -> float:
    inverted = 1.0 - level / 15.0
    return (1.0 - inverted) / (inverted * 3.0 + 1.0) * (1.0 - ambient) + ambient


def glsl_celestial_angle(world_time: int) -> float:
    angle = (world_time % 24000) / 24000.0 - 0.25
    if angle < 0.0:
        angle += 1.0
    if angle > 1.0:
        angle -= 1.0
    original = angle
    angle = 1.0 - (math.cos(angle * math.pi) + 1.0) / 2.0
    return original + (angle - original) / 3.0


def glsl_day_factor(world_time: int) -> float:
    return min(1.0, max(0.0, math.cos(glsl_celestial_angle(world_time) * TAU) * 2.0 + 0.5))


def glsl_sky_subtracted(world_time: int, rain: float = 0.0,
                        weighted_thunder: float = 0.0) -> int:
    factor = glsl_day_factor(world_time)
    factor *= 1.0 - rain * 5.0 / 16.0
    factor *= 1.0 - weighted_thunder * 5.0 / 16.0
    return math.floor((1.0 - factor) * 11.0)


def glsl_star_brightness(world_time: int) -> float:
    value = min(1.0, max(0.0, 1.0 - (math.cos(glsl_celestial_angle(world_time) * TAU) * 2.0 + 0.75)))
    return value * value * 0.5


class Beta173DifferentialTests(unittest.TestCase):
    def test_brightness_table_matches_java_reference(self):
        for ambient in (0.05, 0.1):
            for level in range(16):
                with self.subTest(ambient=ambient, level=level):
                    self.assertAlmostEqual(
                        glsl_brightness(level, ambient),
                        java_brightness(level, ambient),
                        places=12,
                    )

    def test_shader_celestial_angle_matches_java_at_zero_partial_ticks(self):
        for world_time in range(0, 24000, 113):
            with self.subTest(world_time=world_time):
                self.assertAlmostEqual(
                    glsl_celestial_angle(world_time),
                    java_celestial_angle(world_time, 0.0),
                    places=12,
                )

    def test_shader_day_factor_matches_java_expression(self):
        for world_time in range(0, 24000, 137):
            angle = java_celestial_angle(world_time)
            expected = min(1.0, max(0.0, math.cos(angle * TAU) * 2.0 + 0.5))
            self.assertAlmostEqual(glsl_day_factor(world_time), expected, places=12)

    def test_sky_subtraction_matches_java_across_time_and_weather(self):
        weather = (0.0, 0.25, 0.5, 1.0)
        for world_time in range(0, 24000, 197):
            for rain in weather:
                for thunder in weather:
                    with self.subTest(time=world_time, rain=rain, thunder=thunder):
                        self.assertEqual(
                            glsl_sky_subtracted(world_time, rain, thunder),
                            java_sky_subtracted(world_time, rain, thunder),
                        )

    def test_star_brightness_matches_java(self):
        for world_time in range(0, 24000, 101):
            with self.subTest(world_time=world_time):
                self.assertAlmostEqual(
                    glsl_star_brightness(world_time),
                    java_star_brightness(world_time),
                    places=12,
                )

    def test_shader_source_contains_the_compared_equations(self):
        shader = SHADER.read_text(encoding="utf-8")
        self.assertIn("float beta173CelestialAngle()", shader)
        self.assertIn("float beta173SkySubtracted()", shader)
        self.assertIn("float beta173Brightness(float level)", shader)
        self.assertIn("float beta173StarBrightness()", shader)

    def test_brightness_function_matches_reference_formula_shape(self):
        shader = SHADER.read_text(encoding="utf-8")
        self.assertIn("(1.0 - inverted) / (inverted * 3.0 + 1.0)", shader)
        for level in range(16):
            for ambient in (0.05, 0.1):
                with self.subTest(level=level, ambient=ambient):
                    self.assertGreaterEqual(java_brightness(level, ambient), ambient)
                    self.assertLessEqual(java_brightness(level, ambient), 1.0)

    def test_partial_tick_interpolation_is_a_documented_gap(self):
        shader = SHADER.read_text(encoding="utf-8")
        self.assertIn("uniform int worldTime;", shader)
        self.assertNotRegex(shader, r"uniform\s+float\s+\w*partial\w*Ticks")
        # Java accepts partialTicks and the shader currently cannot reproduce it.
        self.assertNotAlmostEqual(
            java_celestial_angle(6000, 0.0),
            java_celestial_angle(6000, 0.5),
            places=10,
        )

    def test_fog_blend_is_selected_per_historical_render_distance(self):
        config = CONFIG.read_text(encoding="utf-8")
        expected = {
            0: ("256.0", "0.2928932"),
            1: ("128.0", "0.2401643"),
            2: ("64.0", "0.1591036"),
            3: ("32.0", "0.0"),
        }
        for distance, (fog_end, blend) in expected.items():
            with self.subTest(render_distance=distance):
                directive = "#if" if distance == 0 else "#elif"
                self.assertIn(f"{directive} BETA_RENDER_DISTANCE == {distance}", config)
                self.assertIn(f"#define BETA_FOG_END {fog_end}", config)
                self.assertIn(f"#define BETA_FOG_SKY_BLEND {blend}", config)

        java_blends = {
            distance: 1.0 - (1.0 / (4.0 - distance)) ** 0.25
            for distance in (0, 1, 2, 3)
        }
        for distance, (_, blend) in expected.items():
            self.assertAlmostEqual(float(blend), java_blends[distance], places=6)

if __name__ == "__main__":
    unittest.main()
