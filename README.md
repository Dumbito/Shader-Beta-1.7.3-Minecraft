# Beta173 Lighting — Minecraft Beta 1.7.3

Proyecto experimental para aproximar la iluminación y la niebla históricas de Minecraft Beta 1.7.3 en un entorno moderno con shaders.

## Versiones disponibles

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

## Pruebas

Desde la raíz del repositorio, ejecuta:

```bash
python -m unittest discover -s Beta173-Lighting/tests -v
```

Las pruebas comprueban propiedades matemáticas y constantes del shader. No sustituyen la compilación GLSL ni las pruebas dentro del juego.

## Limitaciones conocidas

- Algunas características del renderizado original se aproximan mediante el sistema de shaders moderno.
- La temperatura del bioma y determinados comportamientos del cielo y la niebla todavía tienen aproximaciones.
- La compatibilidad final depende del entorno de shaders utilizado.

## Estado del proyecto

Proyecto en desarrollo. El objetivo es priorizar la fidelidad histórica sobre los efectos visuales modernos.
