# Beta173 Lighting v0.9.0-pre1 — reconstrucción del campo climático

Shaderpack experimental para Iris que reconstruye la temperatura espacial que Beta 1.7.3 usa para colorear el cielo. **La descarga estable del proyecto sigue siendo v0.8.1**; esta preversión debe probarse visualmente en Minecraft antes de considerarse un lanzamiento.

## Qué reconstruye

La cadena histórica está compuesta por:

1. `World.getSkyColor` obtiene las coordenadas X/Z de la entidad observada y pide `WorldChunkManager.getTemperature(x,z)`.
2. `WorldChunkManager` construye cuatro octavas a partir de `new Random(worldSeed * 9871L)`.
3. `NoiseGeneratorOctaves2` mezcla esas octavas y sus escalas y amplitudes; cada `NoiseGenerator2` genera offsets y una permutación de gradientes, y evalúa ruido Simplex 2D.
4. `BiomeGenBase.getSkyColorByTemp` transforma la temperatura en HSB y `java.awt.Color.HSBtoRGB` convierte el resultado en canales RGB de 8 bits. Java trunca cada canal con `(int)(canal * 255)`, en lugar de redondearlo.
5. El shader conserva la atenuación del ciclo diurno y los ajustes por lluvia y tormenta de las versiones anteriores.

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
