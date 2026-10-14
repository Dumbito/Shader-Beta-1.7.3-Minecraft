# Beta173 Lighting — Minecraft Beta 1.7.3

Proyecto experimental para reconstruir el aspecto de Minecraft Beta 1.7.3 en Minecraft moderno mediante Iris, priorizando la iluminación por niveles, la niebla histórica y el cielo clásico.

## Última versión: v0.8 — Beta Stars & Night Clouds

**[⬇ Descargar Beta173-Lighting v0.8 (.zip)](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.8.zip)**

### Cambios de v0.8

- Aplica un umbral a la cobertura del mapa de estrellas para evitar que sus valores grises parciales se interpreten como cobertura tenue.
- Oscurece las nubes con el factor de día, permitiendo que desaparezcan durante la noche.
- Incluye el paquete ZIP recompilado, sin directivas `#include`.

**Estado de validación:** el ZIP pasó la prueba de integridad y contiene 13 archivos. Las correcciones de shader están integradas en el repositorio; la fidelidad visual final de estrellas y nubes todavía debe confirmarse dentro de Minecraft con la combinación concreta de versión, Iris y Sodium.

### Instalación

1. Descarga `Beta173-Lighting-0.8.zip` desde el enlace directo de arriba.
2. Copia el ZIP sin descomprimir en la carpeta `shaderpacks` de tu instancia de Minecraft.
3. Inicia Minecraft con Iris.
4. En **Opciones → Ajustes de vídeo → Shader Packs**, selecciona **Beta173-Lighting**.
5. Prueba el cielo de noche y las nubes en condiciones diurnas y nocturnas.

### Perfiles de niebla

Edita `shaders/lib/config.glsl` si quieres cambiar el perfil:

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

Las pruebas automatizadas y la validación GLSL estática no sustituyen la comprobación visual dentro del juego.

### Limitaciones conocidas

- La temperatura del bioma sigue siendo una aproximación neutral.
- La propagación de luz y el renderizado moderno no son idénticos al motor original.
- La activación y representación de estrellas/nubes depende de las etapas de renderizado que exponga Iris y de su compatibilidad con Sodium.
- La fidelidad visual final debe verificarse dentro de Minecraft.

### Historial

- **v0.8 — Beta Stars & Night Clouds:** umbral de cobertura para las estrellas y oscurecimiento nocturno de nubes.
- **[v0.7.2 — Beta Cloud Cycle & Stars](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/releases/tag/v0.7.2):** ciclo de color de nubes y salida RGBA de estrellas.
- **[v0.7 — Sky, Stars & Clouds](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/releases/tag/v0.7):** configuración inicial de Iris para estrellas y nubes.
- [v0.6 — Historical Fog Profiles](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.6.zip): perfiles de niebla históricos.
- [v0.5 — Regression](Beta173-Lighting-0.5.zip)
- [v0.4 — Historical](Beta173-Lighting-0.4.zip)
- [v0.3 — Cielo, clima y niebla](Beta173-Lighting-0.3.zip)
- [v0.2 — Entidades y objetos](Beta173-Lighting-0.2.zip)
- [v0.1 — Prototipo de iluminación](Beta173-Lighting-0.1.zip)

Código de referencia: https://github.com/jacobo-mc/mc_b1.7.3_release
