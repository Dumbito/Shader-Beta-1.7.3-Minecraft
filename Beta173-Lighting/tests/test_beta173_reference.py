"""Regression checks for the Beta 1.7.3 lighting port.

Run from the repository root:
    python -m unittest discover -s Beta173-Lighting/tests -v

These tests validate the translated mathematical specification and guard key
shader constants. They do NOT compile GLSL or prove in-game visual equivalence.
"""
from __future__ import annotations

import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHADERS = ROOT / "shaders"


def celestial_angle(world_time: int) -> float:
    angle = (world_time % 24000) / 24000.0 - 0.25
    if angle < 0.0:
        angle += 1.0
    if angle > 1.0:
        angle -= 1.0
    original = angle
    angle = 1.0 - (math.cos(angle * math.pi) + 1.0) / 2.0
    return original + (angle - original) / 3.0


def day_factor(world_time: int) -> float:
    return min(1.0, max(0.0, math.cos(celestial_angle(world_time) * math.tau) * 2.0 + 0.5))


def sky_subtracted(world_time: int, rain: float = 0.0, thunder: float = 0.0) -> int:
    factor = day_factor(world_time)
    factor *= 1.0 - min(1.0, max(0.0, rain)) * 5.0 / 16.0
    factor *= 1.0 - min(1.0, max(0.0, thunder)) * 5.0 / 16.0
    return int((1.0 - factor) * 11.0)


def brightness(level: int, ambient: float = 0.05) -> float:
    inverted = 1.0 - level / 15.0
    return (1.0 - inverted) / (inverted * 3.0 + 1.0) * (1.0 - ambient) + ambient


def star_brightness(world_time: int) -> float:
    value = 1.0 - (math.cos(celestial_angle(world_time) * math.tau) * 2.0 + 0.75)
    value = min(1.0, max(0.0, value))
    return value * value * 0.5


class Beta173MathTests(unittest.TestCase):
    def test_brightness_table_endpoints(self):
        self.assertAlmostEqual(brightness(0), 0.05)
        self.assertAlmostEqual(brightness(15), 1.0)
        self.assertAlmostEqual(brightness(0, 0.1), 0.1)
        self.assertAlmostEqual(brightness(15, 0.1), 1.0)

    def test_brightness_table_is_monotonic(self):
        values = [brightness(level) for level in range(16)]
        self.assertEqual(values, sorted(values))
        self.assertEqual(len(set(values)), 16)

    def test_celestial_angle_is_periodic(self):
        for t in (0, 1000, 6000, 12000, 18000, 23999):
            self.assertAlmostEqual(celestial_angle(t), celestial_angle(t + 24000), places=12)

    def test_sky_subtraction_stays_in_historical_range(self):
        for t in range(0, 24000, 137):
            value = sky_subtracted(t)
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 11)
            self.assertEqual(value, int(value))

    def test_weather_does_not_increase_sky_brightness(self):
        for t in range(0, 24000, 997):
            clear = sky_subtracted(t)
            rain = sky_subtracted(t, rain=1.0)
            storm = sky_subtracted(t, rain=1.0, thunder=1.0)
            self.assertGreaterEqual(rain, clear)
            self.assertGreaterEqual(storm, rain)

    def test_star_brightness_range(self):
        for t in range(0, 24000, 113):
            value = star_brightness(t)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 0.5)

    def test_shader_keeps_discrete_light_and_historical_fog_constants(self):
        lighting = (SHADERS / "lib" / "beta173.glsl").read_text(encoding="utf-8")
        config = (SHADERS / "lib" / "config.glsl").read_text(encoding="utf-8")
        self.assertIn("floor(clamp(lm.x, 0.0, 1.0) * 15.0 + 0.5)", lighting)
        self.assertIn("floor(clamp(lm.y, 0.0, 1.0) * 15.0 + 0.5)", lighting)
        self.assertIn("#define BETA_FOG_END 256.0", config)
        self.assertIn("#define BETA_FOG_SKY_BLEND 0.2928932", config)
        self.assertNotIn("BETA_SMOOTH", config)


if __name__ == "__main__":
    unittest.main()
