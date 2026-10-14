# Beta173 Lighting — Minecraft Beta 1.7.3

Proyecto experimental para reconstruir elementos visuales de Minecraft Beta 1.7.3 en Minecraft moderno mediante Iris, con énfasis en la iluminación, la niebla y el cielo clásico.

## Última versión: v0.8.1 — Dimension Fog & Cloud Height

**[⬇ Descargar Beta173-Lighting v0.8.1 (.zip)](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.8.1.zip)**

La versión 0.8.1 parte del shaderpack v0.8 e incorpora ajustes para las dimensiones y la altura de las nubes.

### Cambios de v0.8.1

- **Niebla por dimensión:** el Overworld conserva el perfil histórico de Beta; el Nether usa niebla rojiza y el End utiliza los parámetros nativos de niebla expuestos por Iris.
- **Luz ambiental por dimensión:** se distingue el Nether del End mediante los uniformes de Iris.
- **Altura de las nubes:** remapeada a **Y=260.99** para el rango vertical del Overworld moderno. Es una altura fija, no se adapta automáticamente al relieve.
- **Cielo de Beta:** conserva las estrellas de Beta y el ciclo de color de las nubes introducidos en v0.8.
- **Sombreado de las nubes:** mantiene los factores inspirados en Beta para las caras superior, inferior y laterales.

**Validación:** las pruebas automatizadas del candidato pasaron (27 pruebas), el ZIP pasó la verificación de integridad y se validaron estáticamente cinco pares de programas GLSL. Estas verificaciones no sustituyen la prueba visual en Minecraft con la versión concreta de Iris y Sodium.

### Instalación

1. Descarga `Beta173-Lighting-0.8.1.zip` desde el enlace superior.
2. Copia el ZIP **sin descomprimir** en la carpeta `shaderpacks` de tu instancia de Minecraft.
3. Inicia Minecraft con Iris.
4. En **Opciones → Ajustes de vídeo → Shader Packs**, selecciona `Beta173-Lighting-0.8.1`.
5. Comprueba el cielo y las nubes en el Overworld, y la niebla en el Overworld, Nether y End.

### Perfiles de niebla del Overworld

El selector histórico está en `shaders/lib/config.glsl`:

| Valor | Perfil | Distancia final |
|---:|---|---:|
| 0 | Far | 256 bloques |
| 1 | Normal | 128 bloques |
| 2 | Short | 64 bloques |
| 3 | Tiny | 32 bloques |

El selector reproduce las fórmulas históricas; no controla la cantidad de chunks que carga Minecraft. La niebla de las dimensiones también depende de los parámetros que exponga Iris.

### Pruebas

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s Beta173-Lighting/tests -p 'test_*.py' -v
```

Las pruebas automatizadas comprueban propiedades del código y del paquete; no simulan por completo el motor de Minecraft.

### Limitaciones conocidas

- La temperatura del bioma sigue siendo una aproximación neutral.
- La altura Y=260.99 es fija y puede no ser ideal sobre todos los picos y biomas.
- El sombreado de las caras de las nubes, especialmente al observarlas desde arriba, aún requiere comprobación visual.
- La iluminación, las estrellas, las nubes y la niebla pueden variar según la versión de Minecraft, Iris y Sodium.

### Historial

- **v0.8.1 — Dimension Fog & Cloud Height:** niebla específica por dimensión y altura de nubes adaptada al Overworld moderno.
- **[v0.8 — Beta Stars & Night Clouds](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.8.zip):** campo de estrellas de Beta y ciclo nocturno de nubes.
- **[v0.7.2 — Beta Cloud Cycle & Stars](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/releases/tag/v0.7.2):** ciclo de color de nubes y salida RGBA de estrellas.
- **[v0.7 — Sky, Stars & Clouds](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/releases/tag/v0.7):** configuración inicial de Iris para estrellas y nubes.
- **[v0.6 — Historical Fog Profiles](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.6.zip):** perfiles de niebla históricos.
- [v0.5 — Regression](Beta173-Lighting-0.5.zip)
- [v0.4 — Historical](Beta173-Lighting-0.4.zip)
- [v0.3 — Cielo, clima y niebla](Beta173-Lighting-0.3.zip)
- [v0.2 — Entidades y objetos](Beta173-Lighting-0.2.zip)
- [v0.1 — Prototipo de iluminación](Beta173-Lighting-0.1.zip)

Código de referencia: https://github.com/jacobo-mc/mc_b1.7.3_release
