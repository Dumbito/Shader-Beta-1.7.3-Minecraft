# Beta173 Lighting — Minecraft Beta 1.7.3

Proyecto experimental para reconstruir el aspecto de Minecraft Beta 1.7.3 en Minecraft moderno mediante Iris, priorizando la iluminación por niveles y la niebla histórica.

## Última versión: v0.7 — Sky, Stars & Clouds

**[⬇ Descargar Beta173-Lighting v0.7 (.zip)](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/releases/download/v0.7/Beta173-Lighting-0.7.zip)**

[Ver página del release v0.7 y sus detalles](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/releases/tag/v0.7).

### Cambios de v0.7

- Añade `shaders.properties` con `stars=true` y `clouds=fancy` para solicitar a Iris las estrellas y nubes.
- Mantiene activados el renderizado personalizado del cielo, el sol y la luna.
- Conserva los perfiles históricos de niebla Far, Normal, Short y Tiny.
- No modifica las fórmulas de iluminación por bloques de v0.6.

**Nota de validación:** las opciones de Iris solicitan las estrellas y nubes, pero el resultado debe comprobarse en el juego. Esta versión todavía requiere confirmar que la etapa de renderizado del cielo es compatible con la versión concreta de Iris/Minecraft.

### Instalación

1. Descarga `Beta173-Lighting-0.7.zip` desde el enlace directo de arriba.
2. Copia el ZIP sin descomprimir en `shaderpacks` de tu instancia de Minecraft.
3. Inicia Minecraft con Iris y Sodium.
4. En **Opciones → Ajustes de vídeo → Shader Packs**, selecciona **Beta173-Lighting-0.7**.

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
- La activación de estrellas/nubes depende de las capacidades y etapas de renderizado que exponga Iris.
- La fidelidad visual final debe verificarse dentro de Minecraft.

### Historial

- **v0.7 — Sky, Stars & Clouds:** añade configuración de Iris para estrellas y nubes.
- [v0.6 — Historical Fog Profiles](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.6.zip): perfiles de niebla históricos.
- [v0.5 — Regression](Beta173-Lighting-0.5.zip)
- [v0.4 — Historical](Beta173-Lighting-0.4.zip)
- [v0.3 — Cielo, clima y niebla](Beta173-Lighting-0.3.zip)
- [v0.2 — Entidades y objetos](Beta173-Lighting-0.2.zip)
- [v0.1 — Prototipo de iluminación](Beta173-Lighting-0.1.zip)

Código de referencia: https://github.com/jacobo-mc/mc_b1.7.3_release
