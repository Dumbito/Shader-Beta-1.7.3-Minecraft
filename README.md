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

## Historial de versiones

### [v0.6 — Historical Fog Profiles](Beta173-Lighting-0.6.zip)
- Perfiles de niebla Far, Normal, Short y Tiny: 256, 128, 64 y 32 bloques.
- Mezcla cielo/niebla calculada por perfil y tratamiento diferenciado de dimensiones.
- Pruebas diferenciales y matemáticas de las fórmulas históricas.
- 19 tests de Python y validación GLSL estática aprobados.
- Pendiente: comprobar la apariencia real dentro de Minecraft con Iris y Sodium.

### [v0.5 — Regression](Beta173-Lighting-0.5.zip)
- Añade pruebas de regresión matemática para proteger las fórmulas de iluminación.
- Comprueba la curva de brillo, el ciclo celeste, la atenuación de luz del cielo, las estrellas y constantes clave.
- Las pruebas no demuestran equivalencia visual dentro del juego.

### [v0.4 — Historical](Beta173-Lighting-0.4.zip)
- Establece un perfil de iluminación histórica estricta.
- Recupera niveles discretos de luz de 0 a 15 y constantes ambientales de referencia.
- Fija la niebla de referencia en 256 bloques, correspondiente a Far.
- Documenta las diferencias que el shaderpack no puede reproducir por sí solo.

### [v0.3 — Cielo, clima y niebla](Beta173-Lighting-0.3.zip)
- Añade atenuación de la luz del cielo por lluvia y tormenta.
- Introduce brillo ambiental mínimo según la dimensión.
- Incorpora niebla inspirada en Beta para aire, agua y lava.
- Añade color del cielo, transición hacia el horizonte y brillo de estrellas.

### [v0.2 — Entidades y objetos](Beta173-Lighting-0.2.zip)
- Amplía la iluminación a entidades, objetos sostenidos, objetos en el suelo y entidades de bloques.
- Añade un programa específico para el brillo de encantamiento.

### [v0.1 — Prototipo de iluminación](Beta173-Lighting-0.1.zip)
- Primera implementación de la tabla histórica de brillo.
- Interpolación del ángulo celeste.
- Atenuación aproximada de la luz del cielo por tiempo y lluvia.
- Combinación de luz del cielo y luz de bloques.

## Objetivo

Priorizar la fidelidad histórica de Minecraft Beta 1.7.3 sobre los efectos visuales modernos.
