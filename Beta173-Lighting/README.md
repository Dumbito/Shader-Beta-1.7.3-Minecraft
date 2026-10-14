# Beta173 Lighting v0.8 — Estrellas y nubes de Beta

Shaderpack experimental para Iris que reconstruye iluminación, niebla y cielo de Minecraft Beta 1.7.3.

Referencia de ingeniería inversa: [mc_b1.7.3_release](https://github.com/jacobo-mc/mc_b1.7.3_release) (solo como referencia; las fórmulas están portadas, no copiadas).

## Cambios de v0.8

- **Sin `#include` en el ZIP.** `tools/build_pack.py` incrusta la biblioteca en cada programa, así que el pack no depende de que Iris resuelva includes.
- **Estrellas de Beta dibujadas dentro del cielo** (`gbuffers_skybasic.fsh`), sin depender del pase de estrellas del motor, que se descarta. Posiciones, tamaños y rotaciones salen de `RenderGlobal.renderStars()`: `java.util.Random(10842)`, 1500 intentos, **780 estrellas aceptadas**, radio 100, lado de 0.5 a 1.0. `tools/generate_starmap.py` rasteriza esas estrellas en `shaders/textures/starmap.png`. La mezcla es la de Beta: `glColor4f(b, b, b, b)` con `(SRC_ALPHA, ONE)`, es decir, se suma `b * b`.
- **Nubes con color y sombreado de Beta** (`World.drawClouds` y `renderCloudsFancy`): arriba 1.0, abajo 0.7, caras X 0.9, caras Z 0.8. Ya no se multiplica sobre el color del motor, así que no puede haber oscurecimiento doble. El alfa sigue siendo el del motor porque es la máscara de dónde hay nube.
- **Nubes a la altura de Beta** (108.33 en vez de 192.33).
- Modos de diagnóstico ampliados (`BETA_DEBUG` 1 a 4).

**Estado:** el código compila (glslang, 1200 combinaciones de opciones) y las pruebas pasan, pero **nada de esto se ha visto todavía dentro de Minecraft**. Las pruebas no demuestran fidelidad visual.

## v0.9 experimental: ruido climático original de Beta

Esta versión de desarrollo reconstruye el campo espacial que Beta 1.7.3 calculaba con `WorldChunkManager.getTemperature(x,z)`: cuatro octavas de Simplex 2D (`NoiseGeneratorOctaves2`) inicializadas con la semilla del mundo, sus offsets Java-Random, las permutaciones de gradiente y la fórmula HSB de `BiomeGenBase.getSkyColorByTemp`.

**No se activa con la semilla de ejemplo.** El archivo incluido mantiene el modo neutral para que una instalación limpia no se haga pasar por una reproducción fiel. En la raíz del repositorio, ejecuta:

```bash
python3 Beta173-Lighting/tools/generate_climate_seed.py --seed <semilla-exacta-de-/seed>
python3 Beta173-Lighting/tools/build_pack.py 0.9-climate
```

Usa el ZIP resultante únicamente con el mundo para el que generaste la textura. Si Iris ha reiniciado las coordenadas de `cameraPosition`, ajusta `--origin-x` y `--origin-z` y vuelve a generar. La aproximación puede no coincidir en cámara de tercera persona, y GLSL `float` no reproduce bit a bit la aritmética `double` de Java. Falta comprobarlo visualmente en el cliente; esta rama no debe tratarse aún como lanzamiento estable.

## Instalación

1. Copia `Beta173-Lighting-0.8.zip` (raíz del repositorio) sin descomprimir en la carpeta `shaderpacks` de tu instancia.
2. Selecciónalo en **Opciones → Ajustes de vídeo → Shader Packs**.

Para construir el ZIP desde las fuentes:

```bash
python3 Beta173-Lighting/tools/build_pack.py 0.8
```

Para generar un ZIP de diagnóstico sin tocar el código (el ZIP no usa `#include`, así que las opciones van dentro de cada shader):

```bash
python3 Beta173-Lighting/tools/build_pack.py 0.8-debug1 BETA_DEBUG=1
python3 Beta173-Lighting/tools/build_pack.py 0.8-nubes-motor BETA_CLOUD_COLOR_MODE=1
python3 Beta173-Lighting/tools/build_pack.py 0.8-sin-estrellas BETA_STAR_FIELD=off
```

## Opciones (`shaders/lib/config.glsl`)

| Opción | Valor | Qué hace |
|---|---|---|
| `BETA_STAR_FIELD` | comentar | Vuelve al pase de estrellas del motor |
| `BETA_CLOUD_COLOR_MODE` | `0` / `1` / `2` | Color de Beta / solo el del motor / v0.7.2 (multiplicar) |
| `BETA_CLOUD_HEIGHT_FIX` | comentar | Deja las nubes a la altura del juego |
| `BETA_DEBUG` | `1` | Colorea las etapas del cielo (azul SKY, naranja SUNSET, magenta STARS, verde CUSTOM_SKY, rojo oscuro VOID, amarillo = no reconocida) y pinta las nubes de rojo |
| `BETA_DEBUG` | `2` | Estrellas de Beta al máximo brillo, incluso de día |
| `BETA_DEBUG` | `3` | El cielo muestra uniformes: R = lluvia, G = tormenta, B = brillo de estrellas ×2 (blanco = `hasSkylight` no llega) |
| `BETA_DEBUG` | `4` | Anillo cian donde Beta pone el sol y naranja donde pone la luna |

## Perfiles de niebla

| `BETA_RENDER_DISTANCE` | Perfil | Distancia final |
|---:|---|---:|
| 0 | Far | 256 bloques |
| 1 | Normal | 128 bloques |
| 2 | Short | 64 bloques |
| 3 | Tiny | 32 bloques |

El selector no controla los chunks que carga Minecraft.

## Pruebas

```bash
python3 -m unittest discover -s Beta173-Lighting/tests -p 'test_*.py' -v
```

Las pruebas automatizadas no sustituyen una prueba visual en Minecraft.

## Limitaciones

- La orientación de las estrellas asume el marco con el que el juego dibuja el sol y la luna (Rx y luego Ry de -90°). Se comprueba con `BETA_DEBUG 4`.
- Si Iris voltea la textura verticalmente al cargarla, las estrellas quedarían reflejadas respecto al original (mismo aspecto, otra disposición).
- Las nubes conservan la geometría del motor; no se ha reconstruido el sistema de nubes de Beta (celdas de 12 bloques, desplazamiento, dos pasadas).
- Sol, luna y fases de la luna siguen siendo los del juego moderno.
- El modo neutral es el fallback. El port climático v0.9 está en investigación y requiere generar la textura/offsets con la semilla del mundo; no se garantiza igualdad bit a bit ni coordenadas absolutas tras wrapping.
- La propagación de luz y el motor moderno difieren de Beta 1.7.3.
