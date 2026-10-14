## Experimental development package — unnumbered

The repository root contains `Beta173-Lighting-dev.zip`, a separate test package built from the current shader programs and experimental versions of `shaders/lib/beta173.glsl` and `shaders/lib/config.glsl`.

Experimental settings include `BETA_SMOOTH`, `BETA_FOG_END 192.0`, and `BETA_FOG_SKY_BLEND 0.2929`. These settings differ from the strict historical profile described below and must not be treated as the official numbered release.

The package is not v0.6. Standalone GLSL syntax validation passes after recursive include expansion; visual behavior and compatibility must still be tested in Minecraft with Iris. The existing v0.5 remains the latest numbered shader release.

# Beta173 Lighting — perfil histórico v0.5

Shaderpack experimental para Iris que reconstruye en Minecraft moderno las fórmulas de iluminación, ciclo celeste y niebla de Minecraft Beta 1.7.3. La prioridad de esta rama es la fidelidad histórica, no conservar la apariencia del renderizador moderno.

## Fuente de referencia

Código fuente reconstruido de Beta 1.7.3: https://github.com/jacobo-mc/mc_b1.7.3_release

Funciones de referencia: `WorldProvider`, `WorldProviderHell`, `World`, `EntityRenderer` y `RenderGlobal`.

## Perfil estricto

- Niveles de luz discretos 0–15; no usar interpolación continua para simular Smooth Lighting moderno.
- Curva histórica de la tabla de brillo: ambiente 0.05 en Overworld y 0.1 en dimensiones sin luz de cielo.
- Curva de ángulo celeste basada en el ciclo de 24 000 ticks y la interpolación cosenoidal de Beta.
- Atenuación del cielo por lluvia y tormenta, según la fórmula de `World.calculateSkylightSubtracted`.
- Cálculo aproximado del color de cielo y niebla y brillo de estrellas a partir de las fórmulas históricas.
- Niebla de referencia a 256 bloques, equivalente al ajuste Far de Beta; no equivale necesariamente al far plane configurado en Minecraft moderno.

## Límites conocidos — no confundir aproximación con port completo

- Iris solo expone el tiempo del mundo como un valor entero en este shader; no se reproduce la interpolación de partial ticks de forma idéntica.
- El lightmap de Minecraft moderno no representa necesariamente los mismos valores que los niveles de luz de Beta. Redondear a 0–15 reduce la diferencia, pero no sustituye la propagación de luz original.
- La temperatura del bioma del cielo está fijada en 0.5 porque esta rama todavía no recibe la temperatura histórica del bioma de forma fiable.
- El cielo original también incluye geometría y estados de renderizado del juego: amanecer/atardecer, sol, fases lunares, nubes y destello de relámpago no quedan reproducidos íntegramente por el shader.
- El renderizado de Nether/End y sus nieblas requiere tratamiento específico por dimensión; no se debe asumir equivalencia completa.
- Un shaderpack no puede reemplazar la propagación de iluminación que Minecraft calcula en CPU. Para fidelidad total de iluminación sería necesario un mod de renderizado y/o lógica del motor.

## Opciones

Editar `shaders/lib/config.glsl`. Las opciones activas corresponden al perfil histórico. `BETA_FOG_END` y `BETA_FOG_SKY_BLEND` están fijados a los valores de referencia de Beta Far; modificarlos deja de ser el perfil histórico estricto.

## Verificación matemática

Se añadió una batería de regresión independiente de Python en `tests/test_beta173_reference.py`. Ejecutar desde la raíz del repositorio:

```bash
python -m unittest discover -s Beta173-Lighting/tests -v
```

Comprueba extremos y monotonía de la curva de brillo, periodicidad del ángulo celeste, límites de la resta de luz del cielo, efecto de lluvia/tormenta, rango del brillo estelar y constantes clave del shader. Estas pruebas validan la especificación matemática y evitan regresiones en constantes; **no compilan GLSL ni sustituyen las pruebas dentro de Minecraft**.

## Estado v0.5

Esta versión añade comprobaciones de regresión matemática para proteger los cálculos históricos mientras continúa el portado. Sigue sin equivaler a un port completo: no se afirma fidelidad visual total hasta comparar las fórmulas y el comportamiento del juego en condiciones controladas.


## v0.6 — comparación diferencial

La rama `v0.6-beta173-differential` añade `tests/test_beta173_differential.py`, que compara las ecuaciones portadas con transcripciones de las fórmulas Java del repositorio de referencia de Jacob:

- `WorldProvider.generateLightBrightnessTable()`
- `WorldProvider.calculateCelestialAngle()`
- `World.calculateSkylightSubtracted()`
- `World.getStarBrightness()`

La suite comprueba múltiples tiempos del ciclo y combinaciones de lluvia/tormenta. También registra dos diferencias conocidas: la interpolación `partialTicks` no está expuesta al shader y la mezcla entre cielo y niebla usa una constante fija, mientras que el renderizador Java calcula esa mezcla según la distancia de renderizado.

Ejecutar toda la batería desde la raíz del repositorio:

```bash
python -m unittest discover -s Beta173-Lighting/tests -v
```

**Alcance:** estas son pruebas diferenciales de ecuaciones transcritas; no ejecutan el código Java de Jacob dentro de la prueba, no compilan GLSL y no comparan imágenes del juego. Las diferencias de precisión de coma flotante Java/GLSL y el lightmap del motor moderno siguen requiriendo validación adicional.
