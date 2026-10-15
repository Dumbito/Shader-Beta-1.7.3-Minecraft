"""Matriz diferencial ejecutada contra una referencia Java de Beta 1.7.3."""
from __future__ import annotations

import math
import shutil
import subprocess
import tempfile
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JAVA_REF = ROOT / "tests" / "reference" / "Beta173ClimateReference.java"
sys.path.insert(0, str(ROOT / "tools"))
import generate_climate_seed as climate  # noqa: E402
import test_beta173_differential as historical  # noqa: E402


def _shader_hsb_rgb(temperature: float) -> tuple[int, int, int]:
    t = max(-1.0, min(1.0, temperature / 3.0))
    h = ((0.62222224 - t * 0.05) % 1.0) * 6.0
    s = 0.5 + t * 0.1
    sector = int(h)
    f = h - sector
    p = 1.0 - s
    q = 1.0 - s * f
    r = 1.0 - s * (1.0 - f)
    if sector == 0:
        rgb = (1.0, r, p)
    elif sector == 1:
        rgb = (q, 1.0, p)
    elif sector == 2:
        rgb = (p, 1.0, r)
    elif sector == 3:
        rgb = (p, q, 1.0)
    elif sector == 4:
        rgb = (r, p, 1.0)
    else:
        rgb = (1.0, p, q)
    return tuple(math.floor(max(0.0, min(1.0, c)) * 255.0) for c in rgb)


def _shader_sky_rgb(seed, x, z, time, rain, thunder):
    base = _shader_hsb_rgb(climate.climate_temperature(seed, x, z))
    col = [c / 255.0 for c in base]
    day = historical.glsl_day_factor(time)
    col = [c * day for c in col]
    if rain > 0.0:
        gray = (col[0] * 0.3 + col[1] * 0.59 + col[2] * 0.11) * 0.6
        k = 1.0 - rain * 0.75
        col = [c * k + gray * (1.0 - k) for c in col]
    if thunder > 0.0:
        gray = (col[0] * 0.3 + col[1] * 0.59 + col[2] * 0.11) * 0.2
        k = 1.0 - thunder * 0.75
        col = [c * k + gray * (1.0 - k) for c in col]
    return col


class ExecutableJavaDifferentialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        java, javac = shutil.which("java"), shutil.which("javac")
        if not java or not javac:
            raise unittest.SkipTest("Se necesita JDK (java + javac) para pruebas diferenciales")
        cls.java = java
        cls.temp = tempfile.TemporaryDirectory(prefix="beta173-java-reference-")
        cls.addClassCleanup(cls.temp.cleanup)
        result = subprocess.run(
            [javac, "-encoding", "UTF-8", "-d", cls.temp.name, str(JAVA_REF)],
            capture_output=True, text=True, timeout=90,
        )
        if result.returncode:
            raise RuntimeError(f"No se pudo compilar la referencia Java:\n{result.stderr}")
        cls.classpath = cls.temp.name

    @classmethod
    def run_reference(cls, commands):
        result = subprocess.run(
            [cls.java, "-cp", cls.classpath, "Beta173ClimateReference"],
            input="\n".join(commands) + "\n", capture_output=True, text=True, timeout=90,
        )
        if result.returncode:
            raise RuntimeError(f"Falló la referencia Java:\n{result.stderr}")
        lines = result.stdout.splitlines()
        if len(lines) != len(commands):
            raise AssertionError(f"La referencia devolvió {len(lines)} líneas para {len(commands)} comandos")
        return [line.split("\t") for line in lines]

    def test_climate_noise_matches_java_over_seed_coordinate_and_signed_boundaries(self):
        seeds = (0, 1, -1, 42, 123456789, -123456789, 2**63 - 1, -(2**63))
        coords = (
            (0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1),
            (100, 200), (-100, -200), (16000, 16000), (-16000, -16000),
            (29999999, 29999999), (29999999, -29999999),
            (-29999999, 29999999), (-29999999, -29999999),
            (2**31 - 1, -(2**31)), (-(2**31), 2**31 - 1),
        )
        commands = [f"C {seed} {x} {z}" for seed in seeds for x, z in coords]
        results = self.run_reference(commands)
        self.assertEqual(len(results), 144)
        max_error = 0.0
        for result in results:
            _, seed, x, z, java_temp = result
            python_temp = climate.climate_temperature(int(seed), int(x), int(z))
            error = abs(python_temp - float(java_temp))
            max_error = max(max_error, error)
            self.assertLessEqual(
                error, 1e-12,
                f"seed={seed}, x={x}, z={z}: Python={python_temp:.17g}, Java={java_temp}",
            )
        self.assertLess(max_error, 1e-12)

    def test_hsb_rgb_quantization_matches_java_at_temperature_clamps_and_sectors(self):
        temps = (-1000.0, -3.000001, -3.0, -2.999999, -1.5, -0.000001, 0.0,
                 0.000001, 0.5, 1.5, 2.999999, 3.0, 3.000001, 1000.0)
        results = self.run_reference([f"K {t:.17g}" for t in temps])
        self.assertEqual(len(results), len(temps))
        for row in results:
            temp = float(row[1])
            java_rgb = tuple(map(int, row[2:5]))
            shader_rgb = _shader_hsb_rgb(temp)
            with self.subTest(temperature=temp):
                self.assertLessEqual(
                    max(abs(a - b) for a, b in zip(shader_rgb, java_rgb)), 1,
                    f"GLSL-like RGB={shader_rgb}; Java HSBtoRGB={java_rgb}",
                )

    def test_sky_color_matrix_covers_time_and_weather_against_java(self):
        seeds = (0, 42, 123456789, -987654321)
        coords = ((0, 0), (-1, -1), (100, 200), (-100, -200), (29999999, -29999999))
        times = (0, 1, 5999, 6000, 6001, 11999, 12000, 18000, 23999, 24000, -1)
        weather = ((0.0, 0.0), (0.01, 0.0), (0.25, 0.0), (0.5, 0.25),
                   (1.0, 0.0), (1.0, 0.5), (1.0, 1.0))
        commands = [
            f"S {seed} {x} {z} {time} 0 {rain:.8g} {thunder:.8g}"
            for seed in seeds for x, z in coords for time in times for rain, thunder in weather
        ]
        results = self.run_reference(commands)
        self.assertEqual(len(results), 1540)
        max_error = 0.0
        for row in results:
            _, seed, x, z, time, partial, rain, thunder, temperature, rj, gj, bj, day, angle, sub, stars, *_ = row
            expected = tuple(map(float, (rj, gj, bj)))
            actual = tuple(_shader_sky_rgb(int(seed), int(x), int(z), int(time), float(rain), float(thunder)))
            error = max(abs(a - b) for a, b in zip(actual, expected))
            max_error = max(max_error, error)
            self.assertLessEqual(
                error, 1.2 / 255.0,
                f"seed={seed}, xyz=({x},{z}), time={time}, rain={rain}, thunder={thunder}, "
                f"error={error:.7f}, shader={actual}, Java={expected}",
            )
        self.assertLessEqual(max_error, 1.2 / 255.0)

    def test_angle_day_fog_subtraction_stars_weather_and_partial_tick_boundaries(self):
        times = (0, 1, 5999, 6000, 6001, 11999, 12000, 12001, 17999, 18000,
                 18001, 23999, 24000, 24001, 47999, 48000)
        partials = (0.0, 0.000001, 0.5, 0.999999, 1.0)
        weather = ((0.0, 0.0), (0.000001, 0.0), (0.25, 0.0), (0.5, 0.25),
                   (1.0, 0.0), (1.0, 0.5), (1.0, 1.0))
        commands = [
            f"F {time} {partial:.8g} {rain:.8g} {thunder:.8g}"
            for time in times for partial in partials for rain, thunder in weather
        ]
        results = self.run_reference(commands)
        self.assertEqual(len(results), len(times) * len(partials) * len(weather))
        for row in results:
            _, time, partial, rain, thunder, angle_java, day_java, sub_java, star_java = row
            time, partial, rain, thunder = int(time), float(partial), float(rain), float(thunder)
            angle_java, day_java, star_java = float(angle_java), float(day_java), float(star_java)
            self.assertTrue(0.0 <= angle_java <= 1.0)
            self.assertTrue(0.0 <= day_java <= 1.0)
            self.assertTrue(0.0 <= star_java <= 0.5)
            self.assertTrue(0 <= int(sub_java) <= 11)
            if partial == 0.0:
                self.assertLessEqual(abs(historical.glsl_celestial_angle(time) - angle_java), 0.0003)
                self.assertLessEqual(abs(historical.glsl_day_factor(time) - day_java), 0.001)
                self.assertLessEqual(abs(historical.glsl_star_brightness(time) - star_java), 0.001)
                self.assertLessEqual(abs(historical.glsl_sky_subtracted(time, rain, thunder) - int(sub_java)), 1)

    def test_brightness_curve_matches_java_float_boundaries(self):
        ambients = (0.05, 0.1)
        commands = [f"B {level} {ambient:.8g}" for ambient in ambients for level in range(16)]
        results = self.run_reference(commands)
        self.assertEqual(len(results), 32)
        for row in results:
            _, level, ambient, value_java = row
            expected = historical.glsl_brightness(int(level), float(ambient))
            self.assertLessEqual(
                abs(expected - float(value_java)), 2e-7,
                f"level={level}, ambient={ambient}, Python={expected:.10f}, Java={value_java}",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
