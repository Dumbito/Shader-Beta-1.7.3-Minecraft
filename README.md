## Experimental development build — not an official release

An unnumbered development package is available for testing experimental lighting and fog changes. It is separate from the numbered releases and does not replace v0.5 as the latest numbered shader pack.

**[Download Beta173-Lighting development build](Beta173-Lighting-dev.zip)**

This build enables `BETA_SMOOTH` and uses an experimental fog end distance of 192 blocks. The GLSL sources pass standalone syntax validation after recursive include expansion, but in-game appearance and Iris compatibility still require testing. This package is not v0.6 and is not an official release.

# Beta173 Lighting — Minecraft Beta 1.7.3

Proyecto experimental para aproximar la iluminación y la niebla históricas de Minecraft Beta 1.7.3 en un entorno moderno con shaders.

## Estado actual: v0.6 — Differential Regression

La versión más reciente del proyecto está integrada en la rama principal `main`.

**v0.6 añade pruebas diferenciales y documentación; no es un nuevo paquete de shader descargable.** El shader experimental empaquetado más reciente sigue siendo v0.5.

- [Ver las pruebas diferenciales v0.6](Beta173-Lighting/tests/test_beta173_differential.py)
- [Ver el README técnico de Beta173-Lighting](Beta173-Lighting/README.md)

Las pruebas comparan transcripciones en Python de las fórmulas históricas de brillo, ángulo celeste, reducción de luz del cielo y brillo estelar con los resultados esperados. No ejecutan el código Java original, no compilan GLSL ni garantizan equivalencia visual dentro del juego.

## Versiones descargables del shader

### v0.5 — Regression

Incluye el perfil de iluminación histórica y pruebas matemáticas independientes para comprobar propiedades de la iluminación, el ciclo celeste, la atenuación del cielo y el brillo de las estrellas.

**[Descargar Beta173-Lighting v0.5](Beta173-Lighting-0.5.zip)**

### v0.4 — Historical

Introduce el perfil histórico estricto, niveles de luz discretos y constantes de niebla inspiradas en el comportamiento de Beta 1.7.3.

**[Descargar Beta173-Lighting v0.4](Beta173-Lighting-0.4.zip)**

### Versiones anteriores

- [v0.3](Beta173-Lighting-0.3.zip)
- [v0.2](Beta173-Lighting-0.2.zip)
- [v0.1](Beta173-Lighting-0.1.zip)

## Ejecutar las pruebas

Desde la raíz del repositorio:

```bash
python -m unittest discover -s Beta173-Lighting/tests -v
```

Las pruebas matemáticas no sustituyen la compilación GLSL ni las pruebas dentro del juego.

## Limitaciones conocidas

- Algunas características del renderizado original se aproximan mediante el sistema de shaders moderno.
- La temperatura del bioma y determinados comportamientos del cielo y la niebla todavía tienen aproximaciones.
- La compatibilidad final depende del entorno de shaders utilizado.
- La interpolación por partial ticks y la mezcla cielo/niebla dependiente de la distancia de renderizado siguen siendo diferencias conocidas.

## Objetivo del proyecto

Priorizar la fidelidad histórica de Minecraft Beta 1.7.3 sobre los efectos visuales modernos.
