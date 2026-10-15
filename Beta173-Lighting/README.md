# Beta173 Lighting v0.9.0 — campo climático universal (versión oficial)

Shaderpack para Iris con fallback climático universal y un port del ruido histórico de Beta 1.7.3 mediante el Climate Bridge opcional. **Estado: versión oficial publicada. La prueba visual manual en Minecraft fue completada y aprobada por el autor del proyecto.**

## Objetivo: un ZIP que funcione automáticamente en cualquier mundo

Esta rama incorpora una ruta universal sin editar GLSL, reemplazar texturas ni introducir la semilla manualmente:

1. **Shaderpack universal, sin mods extra:** usa el uniforme `temperature` de Iris, actualizado automáticamente para el bioma actual. Funciona en mundos locales y servidores porque no requiere conocer la semilla. Es un respaldo dependiente del bioma moderno, no el ruido espacial exacto de Beta.
2. **Beta173 Climate Bridge (opcional, Fabric 26.3 + Iris 1.11.6+):** en un mundo local obtiene la semilla del servidor integrado y reconstruye en Java el Simplex histórico de cuatro octavas; entrega la temperatura espacial al uniforme `temperature` de Iris. La prueba visual manual de v0.9.0 fue completada y aprobada por el autor, sin afirmar paridad píxel a píxel en todas las condiciones.
3. **Mundos multijugador remotos:** el cliente vanilla recibe una semilla ofuscada, no la semilla original. Si el servidor instala el mismo bridge y habilita explícitamente `shareWorldSeed=true` en `config/beta173-climate-bridge.properties`, puede enviar la semilla cruda al cliente. La opción está desactivada por defecto. Sin cooperación del servidor, el shaderpack conserva el fallback automático por bioma.

El bridge es un mod separado del ZIP: un shaderpack no puede cargar código Java por sí mismo. La CI ejecuta la suite Python, construye y comprueba el ZIP universal, enlaza cinco pares GLSL y compila/prueba el bridge con Java 25. A esto se suma la prueba visual manual de v0.9.0, completada y aprobada por el autor. CI no simula todas las combinaciones del cliente real.

La ruta heredada de ZIP específico por semilla sigue disponible para mundos donde se conozca la semilla original; no es necesaria para instalar ni usar el ZIP universal.

## Descargas v0.9

- [**ZIP universal v0.9.0 oficial — instalable sin modificar código**](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.9.0.zip): fallback por temperatura del bioma si el bridge no está activo; sin el bridge, no simula el ruido espacial histórico de Beta.
- [**Beta173 Climate Bridge 0.1.0 — Fabric 26.3 (opcional)**](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Climate-Bridge-0.1.0-mc26.3.jar): port del ruido histórico mediante el uniforme `temperature` de Iris.
- [**ZIP base v0.9.0-pre1 — instalable**](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.9.0-pre1.zip): paquete general con fallback seguro; no activa una tabla climática de una semilla ajena.
- [**Kit generador climático v0.9**](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-v0.9-climate-builder.zip): fuentes y herramienta para crear automáticamente el ZIP específico de tu mundo.
- [**v0.8.1 — versión anterior**](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.8.1.zip).
- [**Paquete histórico v0.9.0 RC1**](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.9.0-universal-rc1.zip).

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

La prueba visual manual de v0.9.0 fue completada y aprobada por el autor. Como seguimiento, se recomienda ampliar las pruebas en semillas, coordenadas y condiciones meteorológicas adicionales; eso no impide que v0.9.0 sea la versión oficial.

## Versión oficial v0.9.0

Descarga `Beta173-Lighting-0.9.0.zip` desde el [README principal del repositorio](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft#beta173-lighting). Copia el ZIP sin descomprimir a `shaderpacks` y selecciónalo en **Opciones → Ajustes de vídeo → Shader Packs**. Para el ruido climático espacial histórico, instala también el Climate Bridge opcional en la instancia Fabric compatible.

## Pruebas

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s Beta173-Lighting/tests -p 'test_*.py' -v
```

Las pruebas de ruido y generación de activos cubren la reproducibilidad de `java.util.Random`, valores de regresión, construcción del mapa de gradientes, lectura de semilla NBT y la generación temporal del paquete. Las pruebas no simulan el renderizador completo de Minecraft.


## Validación de la versión oficial v0.9.0

- [Workflow universal de pruebas y empaquetado](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/actions/workflows/universal-climate.yml): suite Python, construcción del ZIP, integridad y enlace GLSL.
- [Workflow del Climate Bridge](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/actions/workflows/build-climate-bridge.yml): compilación y pruebas automatizadas del mod.
- [Checksum SHA-256 de la versión oficial](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/SHA256SUMS-v0.9.0.txt).

**Prueba visual manual:** completada y aprobada por el autor dentro de Minecraft. Como control de calidad continuo, se recomienda probar nuevas semillas, transiciones de bioma y condiciones de clima. Esto es compatible con el estado oficial de v0.9.0 y no equivale a garantizar paridad píxel a píxel.
