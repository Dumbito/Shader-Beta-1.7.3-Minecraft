"""Regression tests for cloud RGB visibility across dusk and night in v1.0.1."""
from __future__ import annotations

import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHADERS = ROOT / "shaders"
CONFIG = SHADERS / "lib" / "config.glsl"
FRAGMENT = SHADERS / "gbuffers_clouds.fsh"


def function_source(source: str, signature: str) -> str:
    start = source.index(signature)
    brace = source.index("{", start)
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise AssertionError("Unclosed function: " + signature)


def beta173_celestial_angle(tick: int) -> float:
    angle = (tick % 24000) / 24000.0 - 0.25
    if angle < 0.0:
        angle += 1.0
    if angle > 1.0:
        angle -= 1.0
    original = angle
    shaped = 1.0 - (math.cos(angle * math.pi) + 1.0) / 2.0
    return original + (shaped - original) / 3.0


def beta173_day_factor(tick: int) -> float:
    return min(1.0, max(0.0, math.cos(beta173_celestial_angle(tick) * math.tau) * 2.0 + 0.5))


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    x = min(1.0, max(0.0, (value - edge0) / (edge1 - edge0)))
    return x * x * (3.0 - 2.0 * x)


def cloud_daylight(
    tick: int,
    dusk_start: float = 12000.0,
    dusk_end: float = 18000.0,
    dusk_minimum: float = 0.60,
    night_minimum: float = 0.12,
) -> float:
    """Mirror the smooth dusk floor used by beta173CloudNightFloor()."""
    time = tick % 24000
    dusk = smoothstep(dusk_start, dusk_end, float(time))
    floor = dusk_minimum + (night_minimum - dusk_minimum) * dusk
    return max(beta173_day_factor(time), floor)


def cloud_rgb_multiplier(tick: int) -> tuple[float, float, float]:
    daylight = cloud_daylight(tick)
    return daylight * 0.9 + 0.1, daylight * 0.9 + 0.1, daylight * 0.85 + 0.15


class CloudNightVisibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fragment = FRAGMENT.read_text(encoding="utf-8")
        cls.config = CONFIG.read_text(encoding="utf-8")
        cls.floor_fn = function_source(cls.fragment, "float beta173CloudNightFloor()")
        cls.daylight_fn = function_source(cls.fragment, "float beta173CloudDaylight()")
        cls.color_fn = function_source(cls.fragment, "vec3 beta173CloudColor()")
        cls.main_fn = function_source(cls.fragment, "void main()")

    def test_dusk_and_night_curve_are_configurable_without_editing_code(self) -> None:
        expected = (
            "#define BETA_CLOUD_DUSK_START_TICK 12000.0",
            "#define BETA_CLOUD_DUSK_END_TICK 18000.0",
            "#define BETA_CLOUD_DUSK_MIN_DAYLIGHT 0.60",
            "#define BETA_CLOUD_NIGHT_MIN_DAYLIGHT 0.12",
        )
        for token in expected:
            with self.subTest(token=token):
                self.assertIn(token, self.config)
        for token in ("smoothstep(", "BETA_CLOUD_DUSK_START_TICK", "BETA_CLOUD_DUSK_END_TICK",
                      "BETA_CLOUD_DUSK_MIN_DAYLIGHT", "BETA_CLOUD_NIGHT_MIN_DAYLIGHT"):
            with self.subTest(token=token):
                self.assertIn(token, self.floor_fn)
        self.assertIn("max(beta173DayFactor(), beta173CloudNightFloor())", self.daylight_fn)

    def test_dusk_visibility_is_boosted_while_midnight_still_darkens(self) -> None:
        # At 13,000 ticks the original celestial factor is lower than the new dusk floor.
        self.assertLess(beta173_day_factor(13000), 0.60)
        self.assertGreaterEqual(cloud_daylight(13000), 0.55)
        # The floor itself decreases smoothly through evening and reaches its night value.
        self.assertGreater(cloud_daylight(15000), cloud_daylight(17000))
        self.assertAlmostEqual(cloud_daylight(18000), 0.12, places=8)
        red, green, blue = cloud_rgb_multiplier(18000)
        self.assertAlmostEqual(red, 0.208, places=8)
        self.assertAlmostEqual(green, 0.208, places=8)
        self.assertAlmostEqual(blue, 0.252, places=8)

    def test_dusk_and_dawn_have_no_tick_cutoff(self) -> None:
        windows = (
            (11999, 12000, 12001),
            (12999, 13000, 13001),
            (13999, 14000, 14001),
            (17999, 18000, 18001),
            (23999, 0, 1),
        )
        for window in windows:
            values = [cloud_rgb_multiplier(t) for t in window]
            with self.subTest(window=window):
                for left, right in zip(values, values[1:]):
                    self.assertLess(max(abs(a - b) for a, b in zip(left, right)), 0.01)

    def test_time_modifies_rgb_only_not_alpha_or_geometry(self) -> None:
        self.assertIn("float day = beta173CloudDaylight();", self.color_fn)
        self.assertIn("fragColor = vec4(beta173CloudColor() * beta173CloudFaceShade(), cloudColor.a);", self.main_fn)
        self.assertIn("fragColor = vec4(beta173CloudColor() * betaCloudShade, 0.8 * mask.a);", self.main_fn)
        self.assertNotIn("discard", self.color_fn)
        self.assertNotIn("worldTime", self.color_fn)

    def test_native_alpha_and_custom_mask_are_preserved(self) -> None:
        self.assertIn("if (mask.a < 0.01) discard;", self.main_fn)
        self.assertIn("0.8 * mask.a", self.main_fn)
        self.assertIn("fragColor = vec4(beta173CloudColor() * beta173CloudFaceShade(), cloudColor.a);", self.main_fn)
        self.assertIn("return max(beta173DayFactor(), beta173CloudNightFloor());", self.daylight_fn)


if __name__ == "__main__":
    unittest.main()
