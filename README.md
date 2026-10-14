# Beta173 Lighting — Minecraft Beta 1.7.3

Proyecto experimental para reconstruir el aspecto de Minecraft Beta 1.7.3 en Minecraft moderno mediante Iris, priorizando la iluminación por niveles, la niebla histórica y el cielo clásico.

## Última versión: v0.7.2 — Beta Cloud Cycle & Stars

**[⬇ Descargar Beta173-Lighting v0.7.2 (.zip)](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/releases/download/v0.7.2/Beta173-Lighting-0.7.2.zip)**

[Ver página del release v0.7.2 y sus detalles](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/releases/tag/v0.7.2).

### Cambios de v0.7.2

- Replica en `gbuffers_clouds.fsh` la fórmula de `World.drawClouds` de Beta 1.7.3: oscurecimiento nocturno y respuesta al clima/tormenta.
- Restaura la salida RGBA original de estrellas de `RenderGlobal` (`glColor4f(b, b, b, b)`).
- Conserva la geometría y el alfa del pase de nubes de Iris.
- Mantiene la configuración de Iris para solicitar estrellas, nubes fancy, cielo, sol y luna.
- Conserva los perfiles históricos de niebla y las fórmulas de iluminación de las versiones anteriores.

**Estado de validación:** las pruebas automatizadas del repositorio pasan y el ZIP está publicado. Sin embargo, la visibilidad de nubes y estrellas todavía debe verificarse en ejecución con la combinación concreta de Minecraft e Iris. En Minecraft 26.3 con Iris 1.11.7, la compatibilidad de nubes puede depender también de Iris/Sodium; esta versión no debe considerarse una corrección visual confirmada hasta probarla dentro del juego.

### Instalación

1. Descarga `Beta173-Lighting-0.7.2.zip) desde el enlace directo de arriba.
2. Copia el ZIP sin descomprimir en `shaderpacks` de tu instancia de Minecraft.
3. Inicia Minecraft con Iris.
4. En **Opciones → Ajustes de vídeo → Shader Packs**, selecciona **Beta173-Lighting-0.7.1**.
5. Entra en un mundo con clima despejado y comprueba las estrellas y las nubes.

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

La suite existente contiene 19 tests de Python. Las pruebas automatizadas y la validación GLSL estática no sustituyen la comprobación visual dentro del juego.

### Limitaciones conocidas

- La temperatura del bioma sigue siendo una aproximación neutral.
- La propagación de luz y el renderizado moderno no son idénticos al motor original.
- La activación y representación de estrellas/nubes depende de las etapas de renderizado que exponga Iris y de su compatibilidad con Sodium.
- La fidelidad visual final debe verificarse dentro de Minecraft.

### Historial

- **v0.7.2 — Beta Cloud Cycle & Stars:** aplica el ciclo de color original de nubes y restaura la salida RGBA original de las estrellas; pendiente de confirmación visual en el juego.
- **[v0.7 — Sky, Stars & Clouds](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/releases/tag/v0.7):** configuración inicial de Iris para estrellas y nubes.
- [v0.6 — Historical Fog Profiles](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.6.zip): perfiles de niebla históricos.
- [v0.5 — Regression](Beta173-Lighting-0.5.zip)
- [v0.4 — Historical](Beta173-Lighting-0.4.zip)
- [v0.3 — Cielo, clima y niebla](Beta173-Lighting-0.3.zip)
- [v0.2 — Entidades y objetos](Beta173-Lighting-0.2.zip)
- [v0.1 — Prototipo de iluminación](Beta173-Lighting-0.1.zip)

Código de referencia: https://github.com/jacobo-mc/mc_b1.7.3_release
