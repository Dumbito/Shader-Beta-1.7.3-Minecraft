#!/usr/bin/env python3
"""Genera el mapa equirectangular de estrellas de Beta 1.7.3.

Reproduce RenderGlobal.renderStars() de Beta 1.7.3: java.util.Random(10842), 1500 intentos,
radio 100, semilla/tamano/rotacion tal como en el original. El resultado se rasteriza en
una textura equirectangular (u = lon, v = lat) en el marco local de Beta, donde el sol del
angulo celeste 0 esta en +Y.

Convencion (igual que en gbuffers_skybasic.fsh):
    u = atan(x, z) / (2*pi) + 0.5
    v = asin(y) / pi + 0.5          (fila 0 de la imagen = v 0 = y -1)

Uso:
    python3 generate_starmap.py ../shaders/textures/starmap.png
"""
from __future__ import annotations

import math
import struct
import sys
import zlib
from pathlib import Path

import numpy as np

STAR_SEED = 10842
STAR_ATTEMPTS = 1500
STAR_RADIUS = 100.0
MAP_WIDTH = 4096
MAP_HEIGHT = 2048
SUPERSAMPLE = 2


class JavaRandom:
    """java.util.Random (LCG de 48 bits)."""

    MULT = 0x5DEECE66D
    MASK = (1 << 48) - 1

    def __init__(self, seed: int) -> None:
        self.seed = (seed ^ self.MULT) & self.MASK

    def _next(self, bits: int) -> int:
        self.seed = (self.seed * self.MULT + 0xB) & self.MASK
        return self.seed >> (48 - bits)

    def next_float(self) -> np.float32:
        return np.float32(self._next(24) / float(1 << 24))

    def next_double(self) -> float:
        return ((self._next(26) << 27) + self._next(27)) * (1.0 / (1 << 53))


def beta_stars():
    """Devuelve la lista de estrellas: (centro unitario, tamano, 4 vertices de Beta)."""
    rng = JavaRandom(STAR_SEED)
    two = np.float32(2.0)
    one = np.float32(1.0)
    stars = []
    for _ in range(STAR_ATTEMPTS):
        x = float(rng.next_float() * two - one)
        y = float(rng.next_float() * two - one)
        z = float(rng.next_float() * two - one)
        size = float(np.float32(0.25) + rng.next_float() * np.float32(0.25))
        len2 = x * x + y * y + z * z
        if not (len2 < 1.0 and len2 > 0.01):
            continue
        inv = 1.0 / math.sqrt(len2)
        x, y, z = x * inv, y * inv, z * inv
        cx, cy, cz = x * STAR_RADIUS, y * STAR_RADIUS, z * STAR_RADIUS
        a1 = math.atan2(x, z)
        s1, c1 = math.sin(a1), math.cos(a1)
        a2 = math.atan2(math.sqrt(x * x + z * z), y)
        s2, c2 = math.sin(a2), math.cos(a2)
        a3 = rng.next_double() * math.pi * 2.0
        s3, c3 = math.sin(a3), math.cos(a3)
        verts = []
        for i in range(4):
            d41 = ((i & 2) - 1) * size
            d43 = (((i + 1) & 2) - 1) * size
            d47 = d41 * c3 - d43 * s3
            d49 = d43 * c3 + d41 * s3
            d53 = d47 * s2
            d55 = -d47 * c2
            d57 = d55 * s1 - d49 * c1
            d61 = d49 * s1 + d55 * c1
            verts.append((cx + d57, cy + d53, cz + d61))
        stars.append(((x, y, z), size, np.array(verts)))
    return stars


def rasterize(stars, width=MAP_WIDTH, height=MAP_HEIGHT, supersample=SUPERSAMPLE):
    w, h = width * supersample, height * supersample
    cover = np.zeros((h, w), dtype=np.uint8)
    for (cx, cy, cz), size, q in stars:
        c = np.array([cx, cy, cz])
        lat = math.asin(max(-1.0, min(1.0, cy)))
        lon = math.atan2(cx, cz)
        margin = 2.0 * math.sqrt(2.0) * size / STAR_RADIUS + 2.0 * math.pi / w
        j0 = max(0, int(math.floor((lat - margin) / math.pi * h + h / 2.0)))
        j1 = min(h - 1, int(math.ceil((lat + margin) / math.pi * h + h / 2.0)))
        rows = np.arange(j0, j1 + 1)
        coslat = max(math.cos(lat), 1e-6)
        near_pole = abs(lat) + margin >= math.pi / 2.0
        if near_pole:
            cols = np.arange(w)
        else:
            half = int(math.ceil(margin / coslat / (2.0 * math.pi) * w))
            half = min(half, w // 2)
            c0 = int(round((lon / (2.0 * math.pi) + 0.5) * w - 0.5))
            cols = np.arange(c0 - half, c0 + half + 1) % w
        jj, ii = np.meshgrid(rows, cols, indexing="ij")
        pl = ((jj + 0.5) / h - 0.5) * math.pi
        po = ((ii + 0.5) / w - 0.5) * 2.0 * math.pi
        d = np.stack([np.cos(pl) * np.sin(po), np.sin(pl), np.cos(pl) * np.cos(po)], axis=-1)
        dc = d @ c
        ok = dc > 1e-6
        t = np.where(ok, STAR_RADIUS / np.where(ok, dc, 1.0), 0.0)
        p = d * t[..., None]
        e1 = q[1] - q[0]
        e2 = q[3] - q[0]
        rel = p - q[0]
        a = rel @ e1 / float(e1 @ e1)
        b = rel @ e2 / float(e2 @ e2)
        inside = ok & (a >= 0.0) & (a <= 1.0) & (b >= 0.0) & (b <= 1.0)
        cover[jj[inside], ii[inside]] = 255
    if supersample > 1:
        cover = cover.reshape(height, supersample, width, supersample).astype(np.float32).mean(axis=(1, 3))
        cover = np.rint(cover).astype(np.uint8)
    return cover


def write_png_gray(path: Path, img: np.ndarray) -> None:
    h, w = img.shape
    raw = b"".join(b"\x00" + img[row].tobytes() for row in range(h))

    def chunk(tag: bytes, data: bytes) -> bytes:
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def main(argv: list[str]) -> int:
    out = Path(argv[1]) if len(argv) > 1 else Path("starmap.png")
    stars = beta_stars()
    cover = rasterize(stars)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_png_gray(out, cover)
    print(f"{len(stars)} estrellas aceptadas de {STAR_ATTEMPTS}; {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
