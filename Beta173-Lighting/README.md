# Beta173 Lighting v0.9 — campo climático universal (candidato experimental)

Shaderpack experimental para Iris que reconstruye el campo climático de Minecraft Beta 1.7.3. **La versión estable publicada sigue siendo v0.8.1**; el candidato universal de esta rama debe pasar CI y pruebas visuales antes de reemplazarla.

## Objetivo: un ZIP que funcione automáticamente en cualquier mundo

Esta rama incorpora una ruta universal sin editar GLSL, reemplazar texturas ni introducir la semilla manualmente:

1. **Shaderpack universal, sin mods extra:** usa el uniforme `temperature` de Iris, actualizado automáticamente para el bioma actual. Funciona en mundos locales y servidores porque no requiere conocer la semilla. Es un respaldo dependiente del bioma moderno, no el ruido espacial exacto de Beta.
2. **Beta173 Climate Bridge (opcional, Fabric 26.3 + Iris 1.11.6+):** en un mundo de un jugador obtiene la semilla real del servidor integrado, reconstruye en Java el Simplex histórico de cuatro octavas y pasa a Iris el color HSB/RGB exacto de 8 bits. Así no hace falta configurar una semilla por mundo.
3. **Mundos multijugador remotos:** el cliente vanilla recibe una semilla ofuscada, no la semilla original. Si el servidor instala el mismo bridge y habilita explícitamente `shareWorldSeed=true` en `config/beta173-climate-bridge.properties`, puede enviar la semilla cruda al cliente. La opción está desactivada por defecto. Sin cooperación del servidor, el shaderpack conserva el fallback automático por bioma.

El bridge es un mod separado del ZIP: un shaderpack no puede cargar código Java por sí mismo. Ambos artefactos son experimentales. El shaderpack y sus enlaces GLSL ya pasan CI; la extensión multijugador del bridge debe completar una nueva compilación y aún falta comprobar el resultado visualmente en Minecraft.

La ruta heredada de ZIP específico por semilla sigue disponible para mundos donde se conozca la semilla original; no es necesaria para instalar ni usar el ZIP universal.

## Descargas v0.9

- [**ZIP base v0.9.0-pre1 — instalable**](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.9.0-pre1.zip): paquete general con fallback seguro; no activa una tabla climática de una semilla ajena.
- [**Kit generador climático v0.9**](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-v0.9-climate-builder.zip): fuentes y herramienta para crear automáticamente el ZIP específico de tu mundo.
- [**v0.8.1 — estable anterior**](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.8.1.zip).

Para usar el port climático reconstruido, descarga y extrae el kit; después ejecuta desde una terminal:

```bash
python3 Beta173-Lighting/tools/configure_climate_pack.py --world "/ruta/a/saves/Mi mundo" --output-dir "$HOME/Descargas"
```

También puedes usar `--seed NUMERO` (la semilla de `/seed`) o ejecutar el comando sin opciones para que la herramienta la solicite. El kit no se instala como shaderpack: la herramienta genera el ZIP final por semilla, listo para colocarlo en `shaderpacks`. No es necesario editar GLSL ni copiar texturas manualmente.


## Qué reconstruye

La cadena histórica está compuesta por:

1. `World.getSkyColor` obtiene las coordenadas X/Z de la entidad observada y pide `WorldChunkManager.getTemperature(x,z)`.
2. `WorldChunkManager` construye cuatro octavas a partir de `new Random(worldSeed * 9871L)`.
3. `NoiseGeneratorOctaves2` mezcla esas octavas y sus escalas y amplitudes; cada `NoiseGenerator2` genera offsets y una permutación de gradientes, y evalúa ruido Simplex 2D.
4. `BiomeGenBase.getSkyColorByTemp` transforma la temperatura en HSB y `java.awt.Color.HSBtoRGB` convierte el resultado en canales RGB de 8 bits. Java trunca cada canal con `(int)(canal * 255)`, en lugar de redondearlo.
5. El shader conserva la atenuación del ciclo diurno y los ajustes por lluvia y tormenta de las versiones anteriores.

Para no recalcular las cuatro octavas por cada fragmento de pantalla, el resultado climático del jugador se calcula en los vertex shaders y se transmite como un valor `flat` a los fragment shaders de terreno y entidades que aplican niebla.

No usamos el uniforme moderno `temperature` de Iris para simular el ruido de Beta. La textura RGBA8 específica de la semilla codifica la tabla de índices de gradiente, mientras que los offsets se escriben automáticamente en un archivo GLSL generado.

## Construir el ZIP de tu mundo sin editar código

No abras archivos GLSL ni reemplaces texturas a mano. Usa la herramienta de configuración:

### Opción 1: mundo guardado localmente

```bash
python3 Beta173-Lighting/tools/configure_climate_pack.py --world "/ruta/a/saves/Mi mundo"
```

`--world` acepta la carpeta del mundo o el archivo `level.dat`. Intenta leer la semilla desde `Data.WorldGenSettings.seed` (mundos modernos) o `Data.RandomSeed` (formatos clásicos).

### Opción 2: semilla conocida

```bash
python3 Beta173-Lighting/tools/configure_climate_pack.py --seed 123456789
```

Cambia `123456789` por el número exacto que devuelve `/seed`, incluidos los signos negativos.

### Opción 3: introducirla cuando la herramienta la pida

```bash
python3 Beta173-Lighting/tools/configure_climate_pack.py
```

La herramienta solicitará la semilla. Este modo sirve también para mundos remotos, si el servidor permite conocerla.

El ZIP se crea en el directorio actual. Para cambiar el destino, añade `--output-dir "$HOME/Descargas"`. El nombre incluye la semilla utilizada y el ZIP incorpora `BETA173-CLIMATE-INFO.txt` como referencia.

**El proceso no modifica el repositorio.** Copia los archivos a una carpeta temporal, genera textura y offsets, añade la directiva `customTexture` de Iris solo a ese paquete temporal, resuelve los `#include`, construye el ZIP y comprueba su integridad. Al terminar, puedes borrar o conservar el ZIP; no necesitas mantener una versión de las fuentes modificada para una semilla concreta.

Instala el ZIP resultante, sin descomprimir, en `shaderpacks` de la instancia que usa ese mundo. El paquete es **específico de la semilla**: genera uno diferente al cambiar de mundo/semilla.

## Precisión y limitaciones

- La implementación reproduce el orden de inicialización de `java.util.Random`, los cuatro offsets/permutaciones, el muestreo de gradientes, las escalas/amplitudes de las octavas y el método Simplex 2D de Beta 1.7.3.
- Para las coordenadas se usa `cameraPositionInt` con `cameraPositionFract` de Iris y la corrección entre la cámara y la posición de los ojos. Esto evita depender del uniforme `cameraPosition`, que puede reiniciarse para limitar errores de precisión.
- El port en GLSL usa `float`, mientras que Java utiliza `double`. La reproducción matemática es estructuralmente fiel, pero no se garantiza igualdad bit a bit y pequeñas diferencias pueden cambiar un canal cerca de un umbral de cuantización.
- La lectura de `level.dat` solo funciona si la semilla está incluida en ese archivo. Para servidores o mundos con datos ocultos, usa `--seed` o el modo interactivo.
- La comprobación del ZIP y las pruebas automáticas no sustituyen la revisión visual con la versión concreta de Minecraft, Iris y Sodium.

Hasta verificar el color del cielo en varias coordenadas, durante el día/noche y bajo lluvia/tormenta, la v0.9 sigue siendo experimental.

## Versión estable v0.8.1

Para instalar la versión estable, descarga `Beta173-Lighting-0.8.1.zip` desde el [README principal del repositorio](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft#beta173-lighting). Copia el ZIP sin descomprimir a `shaderpacks` y selecciónalo en **Opciones → Ajustes de vídeo → Shader Packs**.

## Pruebas

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s Beta173-Lighting/tests -p 'test_*.py' -v
```

Las pruebas de ruido y generación de activos cubren la reproducibilidad de `java.util.Random`, valores de regresión, construcción del mapa de gradientes, lectura de semilla NBT y la generación temporal del paquete. Las pruebas no simulan el renderizador completo de Minecraft.
