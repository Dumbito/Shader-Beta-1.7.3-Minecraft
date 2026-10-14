#!/usr/bin/env python3
"""Empaqueta el shaderpack SIN directivas #include.

Las fuentes de shaders/ usan '#include "/lib/..."' para no repetir codigo. Este script
incrusta cada include dentro de cada programa y genera un ZIP con shaders/ en la raiz.
Asi el pack no depende de que Iris resuelva includes en la maquina del jugador.

Uso (desde la raiz del repositorio):
    python3 Beta173-Lighting/tools/build_pack.py 0.8
    python3 Beta173-Lighting/tools/build_pack.py 0.8-debug BETA_DEBUG=1 BETA_CLOUD_COLOR_MODE=2
    python3 Beta173-Lighting/tools/build_pack.py 0.8-sin-estrellas BETA_STAR_FIELD=off

NOMBRE=VALOR cambia un #define de lib/config.glsl solo en el ZIP generado (NOMBRE=off lo desactiva).
Salida: Beta173-Lighting-<version>.zip en el directorio actual
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "shaders"
INCLUDE = re.compile(r'^[ \t]*#include\s+"([^"]+)"[ \t]*$', re.MULTILINE)
PROGRAM_SUFFIXES = {".vsh", ".fsh", ".gsh", ".csh"}


def apply_overrides(text: str, overrides: dict[str, str]) -> str:
    for name, value in overrides.items():
        pattern = re.compile(r"^#define %s\b.*$" % re.escape(name), re.MULTILINE)
        if not pattern.search(text):
            raise KeyError(f"{name} no existe en lib/config.glsl")
        replacement = f"// {name} desactivado" if value == "off" else f"#define {name} {value}"
        text = pattern.sub(replacement, text, count=1)
    return text


def inline(path: Path, stack: tuple[Path, ...] = (), overrides: dict[str, str] | None = None) -> str:
    if path in stack:
        raise RuntimeError("include circular: " + " -> ".join(p.name for p in stack + (path,)))
    text = path.read_text(encoding="utf-8")
    if overrides and path == SRC / "lib" / "config.glsl":
        text = apply_overrides(text, overrides)

    def replace(match: re.Match) -> str:
        target = SRC / match.group(1).lstrip("/")
        if not target.is_file():
            raise FileNotFoundError(f"{path.relative_to(SRC)} incluye {match.group(1)}, que no existe")
        body = inline(target, stack + (path,), overrides)
        return f"// ---- {match.group(1)} ----\n{body}\n// ---- fin {match.group(1)} ----"

    return INCLUDE.sub(replace, text)


def build_files(overrides: dict[str, str] | None = None) -> dict[str, bytes]:
    """Devuelve {ruta dentro del zip: contenido} con los includes ya incrustados."""
    files: dict[str, bytes] = {}
    for path in sorted(SRC.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(SRC)
        if rel.parts[0] == "lib":
            continue  # la biblioteca ya esta incrustada en cada programa
        if path.suffix in PROGRAM_SUFFIXES and len(rel.parts) == 1:
            source = inline(path, (), overrides)
            if "#include" in source:
                raise RuntimeError(f"quedan #include sin resolver en {rel}")
            files[f"shaders/{rel.as_posix()}"] = source.encode("utf-8")
        else:
            files[f"shaders/{rel.as_posix()}"] = path.read_bytes()
    return files


def write_zip(version: str, out_dir: Path, overrides: dict[str, str] | None = None) -> Path:
    out = out_dir / f"Beta173-Lighting-{version}.zip"
    files = build_files(overrides)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in files.items():
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, data)
        readme = ROOT / "README.md"
        if readme.is_file():
            zf.write(readme, "README.md")
    return out


def main(argv: list[str]) -> int:
    version = argv[1] if len(argv) > 1 else "dev"
    overrides = dict(arg.split("=", 1) for arg in argv[2:])
    out = write_zip(version, Path.cwd(), overrides)
    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
        assert not any(b"#include" in zf.read(n) for n in names if n.endswith((".vsh", ".fsh")))
    print(f"{out} ({out.stat().st_size} bytes, {len(names)} archivos, sin #include)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
