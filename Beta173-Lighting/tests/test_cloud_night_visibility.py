"""Regression tests for cloud visibility across dusk and night in v1.0.1."""
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
    """Float-independent reference of the celestial-angle shaping used by GLSL."""
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


def cloud_rgb_multiplier(tick: int, minimum_daylight: float = 0.12) -> tuple[float, float, float]:
    daylight = max(beta173_day_factor(tick), minimum_daylight)
    return daylight * 0.9 + 0.1, daylight * 0.9 + 0.1, daylight * 0.85 + 0.15


class CloudNightVisibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fragment = FRAGMENT.read_text(encoding="utf-8")
        cls.config = CONFIG.read_text(encoding="utf-8")
        cls.color_fn = function_source(cls.fragment, "vec3 beta173CloudColor()")
        cls.daylight_fn = function_source(cls.fragment, "float beta173CloudDaylight()")
        cls.main_fn = function_source(cls.fragment, "void main()")

    def test_night_floor_is_configurable_without_editing_shader_code(self) -> None:
        self.assertIn("#define BETA_CLOUD_NIGHT_MIN_DAYLIGHT 0.12 // [0.08 0.10 0.12 0.14 0.16 0.18 0.20]", self.config)
        self.assertIn("return max(beta173DayFactor(), BETA_CLOUD_NIGHT_MIN_DAYLIGHT);", self.daylight_fn)

    def test_cloud_rgb_never_falls_below_night_visibility_floor(self) -> None:
        for tick in (12000, 12500, 13000, 13500, 14000, 15000, 18000, 22000, 23000):
            with self.subTest(tick=tick):
                red, green, blue = cloud_rgb_multiplier(tick)
                self.assertGreaterEqual(red, 0.208 - 1e-9)
                self.assertGreaterEqual(green, 0.208 - 1e-9)
                self.assertGreaterEqual(blue, 0.252 - 1e-9)
                for channel in (red, green, blue):
                    self.assertLessEqual(channel, 1.0)
                    self.assertGreaterEqual(channel, 0.0)

    def test_dusk_and_dawn_are_continuous_without_tick_cutoffs(self) -> None:
        critical_windows = ((11999, 12000, 12001), (12999, 13000, 13001), (13999, 14000, 14001),
                           (22999, 23000, 23001), (23999, 0, 1))
        for window in critical_windows:
            values = [cloud_rgb_multiplier(tick) for tick in window]
            with self.subTest(window=window):
                for left, right in zip(values, values[1:]):
                    self.assertLess(max(abs(a - b) for a, b in zip(left, right)), 0.01)

    def test_time_changes_rgb_but_never_adds_time_based_alpha_or_discard(self) -> None:
        self.assertIn("float day = beta173CloudDaylight();", self.color_fn)
        self.assertIn("fragColor = vec4(beta173CloudColor() * beta173CloudFaceShade(), cloudColor.a);", self.main_fn)
        self.assertIn("fragColor = vec4(beta173CloudColor() * betaCloudShade, 0.8 * mask.a);", self.main_fn)
        self.assertNotIn("discard", self.color_fn)
        self.assertNotIn("worldTime", self.color_fn)

    def test_custom_mask_and_native_alpha_contract_are_preserved(self) -> None:
        # Custom mode discards only transparent mask texels; its alpha is still mask-derived.
        self.assertIn("if (mask.a < 0.01) discard;", self.main_fn)
        self.assertIn("0.8 * mask.a", self.main_fn)
        # Stable/native geometry still preserves its input alpha in all weather/time states.
        self.assertIn("fragColor = vec4(beta173CloudColor() * beta173CloudFaceShade(), cloudColor.a);", self.main_fn)
        self.assertIn("return max(beta173DayFactor(), BETA_CLOUD_NIGHT_MIN_DAYLIGHT);", self.daylight_fn)


if __name__ == "__main__":
    unittest.main()
