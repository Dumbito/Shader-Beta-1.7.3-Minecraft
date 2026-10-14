from __future__ import annotations

import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHADER_PATH = ROOT / "shaders" / "lib" / "beta173.glsl"
CONFIG_PATH = ROOT / "shaders" / "lib" / "config.glsl"


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


def native_visibility(mode: int, distance: float, start: float, end: float, density: float) -> float:
    if mode == 2048:
        return math.exp(-max(density, 0.0) * distance)
    if mode == 2049:
        scaled = max(density, 0.0) * distance
        return math.exp(-(scaled * scaled))
    return min(1.0, max(0.0, (end - distance) / max(end - start, 0.001)))


class DimensionFogRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SHADER_PATH.read_text(encoding="utf-8")
        cls.config = CONFIG_PATH.read_text(encoding="utf-8")
        cls.ambient = function_source(cls.source, "float beta173Ambient()")
        cls.fog_color = function_source(cls.source, "vec3 beta173FogColor()")
        cls.apply_fog = function_source(cls.source, "vec3 beta173ApplyFog(vec3 color, float dist)")
        cls.sky_gradient = function_source(cls.source, "vec3 beta173SkyGradient(float up)")

    def test_iris_dimension_and_fog_uniforms_are_declared(self):
        for declaration in (
            "uniform bool hasCeiling;",
            "uniform float ambientLight;",
            "uniform vec3 fogColor;",
            "uniform float fogStart;",
            "uniform float fogEnd;",
            "uniform float fogDensity;",
            "uniform int fogMode;",
        ):
            with self.subTest(declaration=declaration):
                self.assertIn(declaration, self.source)

    def test_nether_uses_historical_red_fog_and_zero_start(self):
        self.assertIn("if (hasCeiling) return vec3(0.2, 0.03, 0.03);", self.fog_color)
        self.assertIn("bool isNether = !hasSkylight && hasCeiling;", self.apply_fog)
        self.assertIn("float betaFogStart = isNether ? 0.0 : betaFogEnd * 0.25;", self.apply_fog)
        self.assertIn("if (!hasSkylight && hasCeiling) return 0.1;", self.ambient)

    def test_end_uses_native_color_density_mode_and_distances(self):
        branch_start = self.apply_fog.index("if (!hasSkylight && !hasCeiling)")
        branch_end = self.apply_fog.index("bool isNether", branch_start)
        end_branch = self.apply_fog[branch_start:branch_end]
        self.assertIn("return fogColor;", self.fog_color)
        for token in ("fogStart", "fogEnd", "fogDensity", "fogMode == 2048", "fogMode == 2049"):
            with self.subTest(token=token):
                self.assertIn(token, end_branch)
        self.assertIn("mix(fogColor, color, clamp(endNativeFogFactor, 0.0, 1.0))", end_branch)
        self.assertIn("if (!hasSkylight && !hasCeiling) return ambientLight;", self.ambient)

    def test_water_and_lava_handling_precedes_dimension_routes(self):
        water = self.apply_fog.index("if (isEyeInWater == 1)")
        lava = self.apply_fog.index("if (isEyeInWater == 2)")
        end = self.apply_fog.index("if (!hasSkylight && !hasCeiling)")
        self.assertLess(water, lava)
        self.assertLess(lava, end)
        self.assertIn("exp(-0.1 * dist)", self.apply_fog)
        self.assertIn("exp(-2.0 * dist)", self.apply_fog)

    def test_overworld_historical_fog_formula_is_retained(self):
        for token in (
            "float d = beta173DayFactor();",
            "vec3 fog = vec3(0.7529412, 0.84705883, 1.0)",
            "fog += (beta173SkyColor() - fog) * BETA_FOG_SKY_BLEND;",
            "fog.rg *= 1.0 - rain * 0.5;",
            "fog.b *= 1.0 - rain * 0.4;",
            "fog *= 1.0 - thunder * 0.5;",
        ):
            with self.subTest(token=token):
                self.assertIn(token, self.fog_color)
        self.assertIn("float betaFogEnd = BETA_FOG_END;", self.apply_fog)
        self.assertIn("float betaFogStart = isNether ? 0.0 : betaFogEnd * 0.25;", self.apply_fog)
        self.assertIn("#define BETA_FOG_END 256.0", self.config)
        self.assertIn("#define BETA_FOG_SKY_BLEND 0.2928932", self.config)
        self.assertIn("float betaFogEnd = BETA_FOG_END;", self.sky_gradient)

    def test_native_linear_fog_boundaries(self):
        self.assertAlmostEqual(native_visibility(9729, 10.0, 10.0, 100.0, 0.1), 1.0)
        self.assertAlmostEqual(native_visibility(9729, 100.0, 10.0, 100.0, 0.1), 0.0)
        self.assertAlmostEqual(native_visibility(9729, 55.0, 10.0, 100.0, 0.1), 0.5)

    def test_native_exponential_modes_are_distinct_and_bounded(self):
        exp = native_visibility(2048, 20.0, 0.0, 100.0, 0.1)
        exp2 = native_visibility(2049, 20.0, 0.0, 100.0, 0.1)
        self.assertAlmostEqual(exp, math.exp(-2.0))
        self.assertAlmostEqual(exp2, math.exp(-4.0))
        for value in (exp, exp2):
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)


if __name__ == "__main__":
    unittest.main()
