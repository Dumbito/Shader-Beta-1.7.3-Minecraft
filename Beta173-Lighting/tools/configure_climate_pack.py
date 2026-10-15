#!/usr/bin/env python3
"""Crea un ZIP de shaderpack preparado para la semilla de un mundo sin editar GLSL.

Opciones:
  python3 Beta173-Lighting/tools/configure_climate_pack.py
  python3 Beta173-Lighting/tools/configure_climate_pack.py --seed 123456789
  python3 Beta173-Lighting/tools/configure_climate_pack.py --world "/ruta/a/saves/Mi mundo"

Con --world, la semilla se extrae de level.dat (NBT) automáticamente. Sin opciones,
el programa pide la semilla que muestra /seed. El repositorio no se modifica: el ZIP
se construye desde una copia temporal y contiene sus propios datos climáticos.
"""
from __future__ import annotations

import argparse
import gzip
import importlib.util
import io
import shutil
import struct
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import BinaryIO

PACK_ROOT = Path(__file__).resolve().parents[1]


def _read_exact(stream: BinaryIO, size: int) -> bytes:
    data = stream.read(size)
    if len(data) != size:
        raise ValueError("level.dat está truncado o no es un NBT válido")
    return data


def _read_nbt_string(stream: BinaryIO) -> str:
    size = struct.unpack(">H", _read_exact(stream, 2))[0]
    return _read_exact(stream, size).decode("utf-8")


def _read_nbt_payload(stream: BinaryIO, tag_type: int):
    if tag_type == 1:
        return struct.unpack(">b", _read_exact(stream, 1))[0]
    if tag_type == 2:
        return struct.unpack(">h", _read_exact(stream, 2))[0]
    if tag_type == 3:
        return struct.unpack(">i", _read_exact(stream, 4))[0]
    if tag_type == 4:
        return struct.unpack(">q", _read_exact(stream, 8))[0]
    if tag_type == 5:
        return struct.unpack(">f", _read_exact(stream, 4))[0]
    if tag_type == 6:
        return struct.unpack(">d", _read_exact(stream, 8))[0]
    if tag_type == 7:
        length = struct.unpack(">i", _read_exact(stream, 4))[0]
        if length < 0:
            raise ValueError("byte array NBT con longitud negativa")
        return _read_exact(stream, length)
    if tag_type == 8:
        return _read_nbt_string(stream)
    if tag_type == 9:
        child_type = _read_exact(stream, 1)[0]
        length = struct.unpack(">i", _read_exact(stream, 4))[0]
        if length < 0:
            raise ValueError("lista NBT con longitud negativa")
        return [_read_nbt_payload(stream, child_type) for _ in range(length)]
    if tag_type == 10:
        result = {}
        while True:
            child_type = _read_exact(stream, 1)[0]
            if child_type == 0:
                return result
            name = _read_nbt_string(stream)
            result[name] = _read_nbt_payload(stream, child_type)
    if tag_type == 11:
        length = struct.unpack(">i", _read_exact(stream, 4))[0]
        if length < 0:
            raise ValueError("int array NBT con longitud negativa")
        return [struct.unpack(">i", _read_exact(stream, 4))[0] for _ in range(length)]
    if tag_type == 12:
        length = struct.unpack(">i", _read_exact(stream, 4))[0]
        if length < 0:
            raise ValueError("long array NBT con longitud negativa")
        return [struct.unpack(">q", _read_exact(stream, 8))[0] for _ in range(length)]
    raise ValueError(f"tipo de etiqueta NBT no reconocido: {tag_type}")


def read_level_dat_seed(world_path: Path) -> int:
    """Lee la semilla moderna o clásica desde una carpeta de mundo o level.dat."""
    path = world_path / "level.dat" if world_path.is_dir() else world_path
    if not path.is_file():
        raise FileNotFoundError(f"No encuentro level.dat: {path}")
    raw = path.read_bytes()
    if raw.startswith(b"\x1f\x8b"):
        raw = gzip.decompress(raw)
    stream = io.BytesIO(raw)
    tag_type = _read_exact(stream, 1)[0]
    if tag_type != 10:
        raise ValueError("La raíz de level.dat no es un compound NBT")
    _root_name = _read_nbt_string(stream)
    root = _read_nbt_payload(stream, tag_type)
    data = root.get("Data", root)
    if not isinstance(data, dict):
        raise ValueError("level.dat no contiene el compound Data esperado")

    candidates = (
        ("WorldGenSettings", "seed"),  # Minecraft moderno
        ("RandomSeed",),               # Minecraft clásico
        ("Seed",),                     # compatibilidad con layouts alternativos
    )
    for keys in candidates:
        current = data
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                current = None
                break
            current = current[key]
        if isinstance(current, int) and not isinstance(current, bool):
            if -(1 << 63) <= current < (1 << 63):
                return current
    raise ValueError(
        "No encuentro la semilla en Data.WorldGenSettings.seed, Data.RandomSeed ni Data.Seed. "
        "Usa --seed con el valor que devuelve /seed."
    )


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"No puedo cargar módulo Python: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def build_seed_pack(seed: int, output_dir: Path) -> Path:
    if not -(1 << 63) <= seed < (1 << 63):
        raise ValueError("La semilla debe caber en un long firmado de Java (64 bits)")
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_seed = f"neg{abs(seed)}" if seed < 0 else str(seed)
    version = f"0.9-climate-seed-{safe_seed}"

    with tempfile.TemporaryDirectory(prefix="beta173-climate-") as tmp:
        temp_pack = Path(tmp) / "Beta173-Lighting"
        shutil.copytree(
            PACK_ROOT,
            temp_pack,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"),
        )
        generator = load_module(
            "beta173_generate_climate_seed", temp_pack / "tools" / "generate_climate_seed.py"
        )
        texture, seed_source = generator.generate(temp_pack / "shaders", seed)

        # Solo el ZIP configurado carga la tabla climática. texture.noise sigue siendo el mapa
        # de estrellas de Beta y no se sobrescribe.
        props_path = temp_pack / "shaders" / "shaders.properties"
        properties = props_path.read_text(encoding="utf-8")
        directive = "customTexture.beta173ClimateGradient = textures/beta173_climate_gradient.png"
        if directive not in properties:
            props_path.write_text(properties.rstrip() + "\n\n# v0.9: lookup climático específico de esta semilla\n" + directive + "\n", encoding="utf-8")

        builder = load_module("beta173_build_pack_for_seed", temp_pack / "tools" / "build_pack.py")
        output = builder.write_zip(version, output_dir)

    manifest = (
        "Beta173 Lighting v0.9 — clima de Beta 1.7.3\n"
        f"World seed: {seed}\n"
        "Modelo: WorldChunkManager.getTemperature -> NoiseGeneratorOctaves2 "
        "(4 octavas de NoiseGenerator2/Simplex) -> BiomeGenBase.getSkyColorByTemp.\n"
        "La semilla se fijó al construir este ZIP; no edites shaders ni reemplaces texturas.\n"
        "Compatibilidad objetivo: Iris para Minecraft moderno. El shader usa float GLSL,\n"
        "por lo que los resultados pueden diferir mínimamente del double de Java.\n"
    )
    with zipfile.ZipFile(output, "a", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("BETA173-CLIMATE-INFO.txt", manifest)

    with zipfile.ZipFile(output, "r") as archive:
        corrupt = archive.testzip()
        if corrupt is not None:
            raise RuntimeError(f"El ZIP generado no supera integridad CRC: {corrupt}")
        names = archive.namelist()
        if "shaders/textures/beta173_climate_gradient.png" not in names:
            raise RuntimeError("El ZIP no incluye el mapa climático generado")
        sky = archive.read("shaders/gbuffers_skybasic.fsh").decode("utf-8")
        if "#include" in sky:
            raise RuntimeError("Quedó una directiva #include sin resolver en el ZIP")
        if "#define BETA_CLIMATE_SEED_CONFIGURED 1" not in sky:
            raise RuntimeError("La configuración seed-specific no llegó al shader compilado")
    print(f"Semilla usada: {seed}")
    print(f"Tabla generada: {texture.name}; configuración: {seed_source.name}")
    print(f"ZIP listo: {output} ({output.stat().st_size} bytes)")
    print("El contenido del repositorio no fue modificado.")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--seed", type=int, help="semilla exacta mostrada por /seed")
    choice.add_argument("--world", type=Path, help="carpeta del mundo o archivo level.dat")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="carpeta destino para el ZIP (por defecto: directorio actual)",
    )
    args = parser.parse_args()

    try:
        if args.world is not None:
            seed = read_level_dat_seed(args.world.expanduser())
            print(f"Semilla extraída de level.dat: {seed}")
        elif args.seed is not None:
            seed = args.seed
        else:
            raw = input("Semilla exacta del mundo (copia el número de /seed): ").strip()
            if not raw:
                raise ValueError("No se ingresó ninguna semilla")
            seed = int(raw, 10)
        build_seed_pack(seed, args.output_dir)
    except (OSError, ValueError, EOFError, zipfile.BadZipFile) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
