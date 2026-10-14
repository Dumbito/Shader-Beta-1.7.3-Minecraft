# Beta173 Lighting — Minecraft Beta 1.7.3

Proyecto experimental para reconstruir el comportamiento histórico de la iluminación y la niebla de Minecraft Beta 1.7.3 en Minecraft moderno mediante Iris.

## v0.6 — Historical Fog Profiles

Esta versión incorpora perfiles de distancia de niebla basados en las fórmulas de `EntityRenderer` de Beta 1.7.3, además de las pruebas diferenciales y matemáticas del proyecto.

**[Descargar Beta173-Lighting v0.6](Beta173-Lighting-0.6.zip)**

### Perfiles históricos

Configura `BETA_RENDER_DISTANCE` en `Beta173-Lighting/shaders/lib/config.glsl`:

| Valor | Perfil de Beta | Distancia final de niebla |
|---:|---|---:|
| 0 | Far | 256 bloques |
| 1 | Normal | 128 bloques |
| 2 | Short | 64 bloques |
| 3 | Tiny | 32 bloques |

La niebla del terreno comienza al 25 % de la distancia final en el Overworld. En el Nether comienza desde el observador. La mezcla de color del cielo también utiliza los valores reconstruidos de cada perfil.

**Importante:** el selector reproduce las fórmulas históricas de distancia; no controla la distancia de chunks que carga Iris o Minecraft.

## Verificación

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s Beta173-Lighting/tests -v
```

Las pruebas automatizadas comprueban las ecuaciones de referencia y los perfiles de niebla. La validación GLSL independiente también se ha ejecutado para tres shaders en los cuatro perfiles.

## Limitaciones

- La temperatura del bioma se aproxima con un valor neutral de 0.5.
- El renderizado moderno no reproduce íntegramente la propagación de luz ni todos los estados del motor original.
- La identificación de dimensiones depende de los uniformes que expone Iris.
- La compilación estática no demuestra equivalencia visual ni compatibilidad total en ejecución.

La apariencia final de v0.6 todavía requiere pruebas dentro de Minecraft con Iris y Sodium. No se afirma fidelidad visual completa.

## Versiones anteriores

- [v0.5 — Regression](Beta173-Lighting-0.5.zip)
- [v0.4 — Historical](Beta173-Lighting-0.4.zip)
- [v0.3](Beta173-Lighting-0.3.zip)
- [v0.2](Beta173-Lighting-0.2.zip)
- [v0.1](Beta173-Lighting-0.1.zip)

## Objetivo

Priorizar la fidelidad histórica de Minecraft Beta 1.7.3 sobre los efectos visuales modernos.
