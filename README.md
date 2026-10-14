# Beta173 Lighting — Minecraft Beta 1.7.3

Proyecto experimental para reconstruir parte del aspecto de Minecraft Beta 1.7.3 en Minecraft moderno mediante Iris, priorizando la iluminación por niveles, la niebla histórica y el cielo clásico.

## Última versión: v0.8.1 — Dimension Fog & Cloud Height

**[⬇ Descargar Beta173-Lighting v0.8.1 (.zip)](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.8.1.zip)**

### Cambios de v0.8.1

- Añade rutas de niebla específicas por dimensión: el Overworld conserva el perfil histórico de Beta, el Nether usa niebla roja y el End utiliza los parámetros nativos de niebla expuestos por Iris.
- Ajusta la luz ambiental por dimensión, diferenciando el Nether del End mediante los uniformes de Iris.
- Remapea la altura de las nubes a **Y=260.99** para el rango vertical del Overworld moderno. Es una adaptación fija, no una altura dinámica según el relieve.
- Conserva el sombreado inspirado en Beta para las caras de las nubes: superior 1.0, inferior 0.7 y laterales 0.9/0.8.
- Mantiene las estrellas de Beta y el ciclo de color de nubes introducidos en v0.8.
- El ZIP contiene los shaders compilados a nivel de paquete, sin directivas `#include` pendientes.

**Validación automatizada:** 27 pruebas pasaron; la integridad del ZIP y cinco pares de programas GLSL también se validaron. Esto no sustituye la comprobación visual dentro de Minecraft con la versión concreta de Iris/Sodium.

### Instalación

1. Descarga `Beta173-Lighting-0.8.1.zip` desde el enlace superior.
2. Copia el ZIP, sin descomprimir, en la carpeta `shaderpacks` de tu instancia de Minecraft.
3. Inicia Minecraft con Iris.
4. En **Opciones → Ajustes de vídeo → Shader Packs**, selecciona **Beta173-Lighting-0.8.1**.
5. Comprueba el cielo, las nubes y la niebla en el Overworld, Nether y End.

### Perfiles de niebla

Edita `shaders/lib/config.glsl` si quieres cambiar el perfil histórico del Overworld:

| Valor | Perfil | Distancia final |
|---:|---|---:|
| 0 | Far | 256 bloques |
| 1 | Normal | 128 bloques |
| 2 | Short | 64 bloques |
| 3 | Tiny | 32 bloques |

El selector reproduce las fórmulas históricas; no controla la cantidad de chunks que carga Minecraft.

### Pruebas

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s Beta173-Lighting/tests -p 'test_*.py' -v
```

Las pruebas automatizadas comprueban invariantes y código fuente, no simulan todo el motor de Minecraft.

### Limitaciones conocidas

- La temperatura del bioma sigue siendo una aproximación neutral.
- La altura de nube Y=260.99 es fija; puede no ser ideal sobre todos los picos y biomas.
- El sombreado de las caras de las nubes todavía requiere confirmación visual, especialmente al observarlas desde arriba.
- La propagación de luz y el renderizado moderno no son idénticos al motor original.
- La fidelidad final de estrellas, nubes y niebla depende de la combinación de Minecraft, Iris y Sodium.

### Historial

- **v0.8.1 — Dimension Fog & Cloud Height:** niebla por dimensión y altura de nubes adaptada al Overworld moderno.
- **[v0.8 — Beta Stars & Night Clouds](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/releases/tag/v0.8):** campo de estrellas Beta y ciclo nocturno de nubes.
- **[v0.7.2 — Beta Cloud Cycle & Stars](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/releases/tag/v0.7.2):** ciclo de color de nubes y salida RGBA de estrellas.
- **[v0.7 — Sky, Stars & Clouds](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/releases/tag/v0.7):** configuración inicial de Iris para estrellas y nubes.
- [v0.6 — Historical Fog Profiles](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.6.zip): perfiles de niebla históricos.

Código de referencia: https://github.com/jacobo-mc/mc_b1.7.3_release
