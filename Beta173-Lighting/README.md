# Beta173 Lighting v0.7.2 — Beta Cloud Cycle & Stars

Shaderpack experimental para Iris que reconstruye iluminación, niebla y cielo de Minecraft Beta 1.7.3.

## Cambios de v0.7.2

- Replica en `gbuffers_clouds.fsh` la fórmula original de `World.drawClouds`: ciclo de color de día/noche y respuesta a lluvia/tormenta.
- Restaura la salida RGBA original de estrellas de `RenderGlobal` (`glColor4f(b, b, b, b)`).
- Conserva la geometría y el alfa del pase de nubes de Iris.
- Mantiene `stars=true`, `clouds=fancy`, `sky=true`, `sun=true` y `moon=true` en `shaders.properties`.
- Conserva las fórmulas de iluminación y perfiles de niebla de las versiones anteriores.

**Compatibilidad:** el empaquetado y las pruebas automatizadas pasan. La representación de nubes y estrellas aún necesita validación visual en Minecraft, especialmente con Minecraft 26.3 e Iris 1.11.7. La interacción Iris/Sodium puede afectar a las nubes; no se afirma una corrección visual definitiva hasta comprobarla en el juego.

## Instalación

1. Descarga [Beta173-Lighting-0.7.2.zip](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/releases/download/v0.7.2/Beta173-Lighting-0.7.2.zip).
2. Copia el ZIP sin descomprimir en la carpeta `shaderpacks` de tu instancia.
3. Selecciónalo desde **Opciones → Ajustes de vídeo → Shader Packs** y comprueba el resultado dentro del juego.

## Perfiles de niebla

En `shaders/lib/config.glsl`:

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

- La temperatura del bioma sigue siendo una aproximación neutral.
- La propagación de luz y el motor moderno difieren de Beta 1.7.3.
- La visibilidad final de estrellas y nubes debe validarse con la versión concreta de Minecraft, Iris y Sodium.
