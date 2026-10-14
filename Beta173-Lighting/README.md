# Beta173 Lighting v0.7 — Sky, Stars & Clouds

Shaderpack experimental para Iris que reconstruye iluminación y niebla de Minecraft Beta 1.7.3.

## Cambios de v0.7

- Añade `shaders/shaders.properties` con `stars=true` y `clouds=fancy`.
- Mantiene `sky=true`, `sun=true` y `moon=true`.
- Conserva las fórmulas y perfiles de niebla de v0.6.
- La configuración solicita a Iris estrellas y nubes, pero debe verificarse en ejecución que la etapa de renderizado del cielo sea compatible con la versión concreta de Iris/Minecraft.

## Instalación

Copia el ZIP sin descomprimir en la carpeta `shaderpacks` de la instancia y selecciónalo desde **Opciones → Ajustes de vídeo → Shader Packs**.

## Perfiles de niebla

En `shaders/lib/config.glsl`:

| `BETA_RENDER_DISTANCE` | Perfil | Distancia final |
|---:|---|---:|
| 0 | Far | 256 bloques |
| 1 | Normal | 128 bloques |
| 2 | Short | 64 bloques |
| 3 | Tiny | 32 bloques |

El selector no controla los chunks que carga Minecraft.

## Pruebas

```bash
python3 -m unittest discover -s Beta173-Lighting/tests -p 'test_*.py' -v
```

Las pruebas automatizadas no sustituyen una prueba visual en Minecraft.

## Limitaciones

- La temperatura del bioma sigue siendo una aproximación neutral.
- La propagación de luz y el motor moderno difieren de Beta 1.7.3.
- Las estrellas y nubes deben validarse dentro del juego con la versión de Iris usada.
