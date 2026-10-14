# Beta173 Lighting v0.6 — Historical Fog Profiles

Shaderpack experimental para Iris que reconstruye fórmulas de iluminación, ciclo celeste y niebla de Minecraft Beta 1.7.3. La prioridad es la fidelidad histórica, no reproducir los efectos modernos.

## Cambios de v0.6

- Perfiles históricos de distancia de niebla: Far, Normal, Short y Tiny.
- Distancias finales de 256, 128, 64 y 32 bloques, respectivamente.
- Inicio de niebla del terreno al 25 % de la distancia final en el Overworld.
- Inicio de niebla desde el observador en el Nether.
- Mezcla de color cielo/niebla calculada por perfil.
- Tratamiento explícito para evitar que el End herede automáticamente la niebla del Nether.
- Pruebas de regresión y comparación de las ecuaciones transcritas desde el código de referencia.

## Fuente de referencia

Código fuente de Beta 1.7.3:
https://github.com/jacobo-mc/mc_b1.7.3_release

Funciones relevantes: `WorldProvider`, `WorldProviderHell`, `World`, `EntityRenderer` y `RenderGlobal`.

## Configuración

Edita `shaders/lib/config.glsl`:

| `BETA_RENDER_DISTANCE` | Perfil | Distancia final |
|---:|---|---:|
| 0 | Far | 256 bloques |
| 1 | Normal | 128 bloques |
| 2 | Short | 64 bloques |
| 3 | Tiny | 32 bloques |

`BETA_FOG_END` y `BETA_FOG_SKY_BLEND` se seleccionan a partir del perfil. El selector controla las fórmulas históricas del shader, no la distancia de chunks de Iris.

## Modelo de niebla

En el terreno del Overworld, la niebla lineal comienza al 25 % de la distancia final y llega a su máximo al 100 %. En el Nether, comienza desde el observador. El End no se clasifica automáticamente como Nether.

Los valores de mezcla cielo/niebla por perfil se reconstruyen a partir de la fórmula de `EntityRenderer.updateFogColor()` de Beta 1.7.3.

## Verificación automatizada

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s Beta173-Lighting/tests -v
```

La batería contiene pruebas de referencia y pruebas diferenciales para las fórmulas transcritas. Se han validado 19 pruebas de Python y 12 combinaciones de compilación GLSL: tres shaders por cuatro perfiles.

Estas pruebas no ejecutan el código Java original dentro del test y no sustituyen una comparación visual en el juego.

## Limitaciones conocidas

- `BETA_SKY_TEMPERATURE` permanece en 0.5 como aproximación neutral; todavía falta recuperar la temperatura real del bioma.
- Iris no expone todos los estados internos ni la interpolación de `partialTicks` de la misma manera que el motor histórico.
- El lightmap moderno y la propagación de luz en CPU no son equivalentes a los de Beta.
- El cielo, el sol, la luna, las nubes, los relámpagos y los estados específicos de cada dimensión no se reproducen íntegramente.
- La compilación GLSL no demuestra compatibilidad ni fidelidad visual en ejecución.

**Estado:** código y pruebas estáticas validados; falta la prueba visual dentro de Minecraft con Iris y Sodium.

## Objetivo

Priorizar el comportamiento histórico de Minecraft Beta 1.7.3 sobre los efectos visuales modernos.
