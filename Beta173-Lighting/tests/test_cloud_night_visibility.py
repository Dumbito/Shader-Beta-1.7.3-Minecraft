"""Regression tests for daytime-only cloud visibility in v1.0.2."""
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


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    x = min(1.0, max(0.0, (value - edge0) / (edge1 - edge0)))
    return x * x * (3.0 - 2.0 * x)


def cloud_visibility(
    tick: int,
    dawn_start: float = 22000.0,
    dawn_end: float = 1000.0,
    dusk_start: float = 12000.0,
    dusk_end: float = 13500.0,
) -> float:
    """Numerical reference for beta173CloudVisibility()."""
    ticks = tick % 24000
    if dusk_start <= ticks < dusk_end:
        visibility = 1.0 - smoothstep(dusk_start, dusk_end, ticks)
    elif ticks >= dawn_start or ticks < dawn_end:
        dawn_ticks = ticks + 24000.0 if ticks < dawn_end else float(ticks)
        visibility = smoothstep(dawn_start, dawn_end + 24000.0, dawn_ticks)
    elif dusk_end <= ticks < dawn_start:
        visibility = 0.0
    else:
        visibility = 1.0
    return max(0.0, min(1.0, visibility))


def beta173_day_factor(tick: int) -> float:
    angle = (tick % 24000) / 24000.0 - 0.25
    if angle < 0.0:
        angle += 1.0
    if angle > 1.0:
        angle -= 1.0
    original = angle
    shaped = 1.0 - (math.cos(angle * math.pi) + 1.0) / 2.0
    angle = original + (shaped - original) / 3.0
    return min(1.0, max(0.0, math.cos(angle * math.tau) * 2.0 + 0.5))


class CloudDaylightVisibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fragment = FRAGMENT.read_text(encoding="utf-8")
        cls.config = CONFIG.read_text(encoding="utf-8")
        cls.visibility_fn = function_source(cls.fragment, "float beta173CloudVisibility()")
        cls.color_fn = function_source(cls.fragment, "vec3 beta173CloudColor()")
        cls.main_fn = function_source(cls.fragment, "void main()")

    def test_visibility_settings_are_exposed_without_manual_source_edits(self) -> None:
        expected = (
            "#define BETA_CLOUD_DAWN_START_TICK 22000.0",
            "#define BETA_CLOUD_DAWN_END_TICK 1000.0",
            "#define BETA_CLOUD_DUSK_START_TICK 12000.0",
            "#define BETA_CLOUD_DUSK_END_TICK 13500.0",
        )
        for token in expected:
            with self.subTest(token=token):
                self.assertIn(token, self.config)
        for token in ("BETA_CLOUD_DAWN_START_TICK", "BETA_CLOUD_DAWN_END_TICK",
                      "BETA_CLOUD_DUSK_START_TICK", "BETA_CLOUD_DUSK_END_TICK",
                      "smoothstep(", "return clamp(visibility, 0.0, 1.0);"):
            with self.subTest(token=token):
                self.assertIn(token, self.visibility_fn)

    def test_clouds_are_completely_hidden_during_deep_night(self) -> None:
        for tick in (13500, 14000, 15000, 18000, 20000, 21999, 22000):
            with self.subTest(tick=tick):
                self.assertAlmostEqual(cloud_visibility(tick), 0.0, places=8)
        self.assertIn("if (cloudVisibility <= 0.001) discard;", self.main_fn)

    def test_dawn_visibility_ramps_up_smoothly_across_midnight_wrap(self) -> None:
        ticks = (22000, 22500, 23000, 23500, 23999, 0, 500, 1000)
        values = [cloud_visibility(tick) for tick in ticks]
        for left, right in zip(values, values[1:]):
            self.assertGreaterEqual(right + 1e-8, left)
        self.assertAlmostEqual(values[0], 0.0, places=8)
        self.assertAlmostEqual(values[-1], 1.0, places=8)
        self.assertAlmostEqual(cloud_visibility(23999), cloud_visibility(0), delta=0.001)
        self.assertGreater(cloud_visibility(23000), 0.0)
        self.assertLess(cloud_visibility(23000), 1.0)

    def test_dusk_visibility_ramps_down_and_stays_zero_at_night(self) -> None:
        self.assertAlmostEqual(cloud_visibility(12000), 1.0, places=8)
        self.assertAlmostEqual(cloud_visibility(12750), 0.5, places=8)
        self.assertGreater(cloud_visibility(12500), cloud_visibility(13000))
        self.assertAlmostEqual(cloud_visibility(13500), 0.0, places=8)
        self.assertAlmostEqual(cloud_visibility(18000), 0.0, places=8)

    def test_cloud_color_returns_to_v100_behavior(self) -> None:
        self.assertIn("float day = beta173DayFactor();", self.color_fn)
        self.assertNotIn("beta173CloudDaylight", self.color_fn)
        self.assertNotIn("beta173CloudNightFloor", self.fragment)
        self.assertNotIn("BETA_CLOUD_NIGHT_MIN_DAYLIGHT", self.config)

    def test_all_cloud_render_modes_respect_visibility(self) -> None:
        for token in (
            "0.8 * mask.a * cloudVisibility",
            "cloudColor.a * cloudVisibility",
            "if (cloudVisibility <= 0.001) discard;",
        ):
            with self.subTest(token=token):
                self.assertIn(token, self.main_fn)
        self.assertIn("cloudColor.rgb * beta173CloudColor()", self.main_fn)
        self.assertIn("beta173CloudFaceShade()", self.main_fn)

    def test_dusk_dawn_edges_do_not_pop_at_tick_boundaries(self) -> None:
        windows = (
            (11999, 12000, 12001),
            (12999, 13000, 13001),
            (13499, 13500, 13501),
            (21999, 22000, 22001),
            (23999, 0, 1),
        )
        for window in windows:
            values = [cloud_visibility(t) for t in window]
            with self.subTest(window=window):
                for left, right in zip(values, values[1:]):
                    self.assertLess(abs(right - left), 0.01)


if __name__ == "__main__":
    unittest.main()
