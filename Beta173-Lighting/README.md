# Beta173 Lighting — perfil histórico v0.4

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

## Estado

Esta rama es una etapa de portado, no una declaración de equivalencia visual completa. No se afirma fidelidad total sin comparar las fórmulas y el comportamiento del juego en condiciones controladas.
