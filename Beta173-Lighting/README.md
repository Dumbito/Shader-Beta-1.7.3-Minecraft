# Beta173 Lighting v0.9.1 — campo climático universal y geometría de nubes Beta (versión oficial)

> **Aviso de compatibilidad de nubes (v0.9.1):** se ha reportado que la geometría custom puede verse transparente, como un marco blanco o con zonas interiores ausentes en algunas combinaciones de Minecraft/Iris/Sodium. La causa probable es que el geometry shader distribuye 840 caras según `gl_PrimitiveIDIn * 16`, una estrategia que no garantiza el mismo número de invocaciones si el motor divide la geometría en distintos draws.
>
> En esta rama correctiva, la geometría reconstruida se conserva como opción **experimental** pero queda **desactivada por defecto**. El modo predeterminado pasa la malla nativa del juego y conserva su alfa. Hasta que se publique un ZIP corregido, los usuarios del paquete oficial 0.9.1 pueden abrir **Shader Pack Settings** y desactivar **BETA_CUSTOM_CLOUD_GEOMETRY** (o la opción de geometría Beta de nubes). Esta corrección aún requiere confirmación visual en el entorno real y no debe considerarse un lanzamiento oficial.

Shaderpack para Iris con fallback climático universal, port del ruido histórico de Beta 1.7.3 mediante el Climate Bridge opcional y reconstrucción de geometría de nubes Beta. **v0.9.1 es la versión oficial publicada.** La suite automatizada valida el paquete y enlaza los programas GLSL, incluida la etapa geometry; la geometría de nubes todavía requiere comprobación visual dentro de la instancia exacta de Minecraft/Iris/Sodium.

## Objetivo: un ZIP que funcione automáticamente en cualquier mundo

Esta rama incorpora una ruta universal sin editar GLSL, reemplazar texturas ni introducir la semilla manualmente:

1. **Shaderpack universal, sin mods extra:** usa el uniforme `temperature` de Iris, actualizado automáticamente para el bioma actual. Funciona en mundos locales y servidores porque no requiere conocer la semilla. Es un respaldo dependiente del bioma moderno, no el ruido espacial exacto de Beta.
2. **Beta173 Climate Bridge (opcional, Fabric 26.3 + Iris 1.11.6+):** en un mundo local obtiene la semilla del servidor integrado y reconstruye en Java el Simplex histórico de cuatro octavas; entrega la temperatura espacial al uniforme `temperature` de Iris. La prueba visual manual de v0.9.0 fue completada y aprobada por el autor, sin afirmar paridad píxel a píxel en todas las condiciones.
3. **Mundos multijugador remotos:** el cliente vanilla recibe una semilla ofuscada, no la semilla original. Si el servidor instala el mismo bridge y habilita explícitamente `shareWorldSeed=true` en `config/beta173-climate-bridge.properties`, puede enviar la semilla cruda al cliente. La opción está desactivada por defecto. Sin cooperación del servidor, el shaderpack conserva el fallback automático por bioma.

El bridge es un mod separado del ZIP: un shaderpack no puede cargar código Java por sí mismo. La CI ejecuta la suite Python, construye y comprueba el ZIP universal, enlaza cinco pares GLSL y compila/prueba el bridge con Java 25. A esto se suma la prueba visual manual de v0.9.0, completada y aprobada por el autor. CI no simula todas las combinaciones del cliente real.

La ruta heredada de ZIP específico por semilla sigue disponible para mundos donde se conozca la semilla original; no es necesaria para instalar ni usar el ZIP universal.

## Descargas oficiales

- [**ZIP oficial v0.9.1 — instalable sin editar código**](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.9.1.zip): clima universal con fallback automático y geometría de nubes Beta seleccionable desde Shader Pack Settings.
- [**ZIP universal v0.9.0 — versión oficial anterior**](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.9.0.zip): fallback por temperatura del bioma si el bridge no está activo; sin el bridge, no simula el ruido espacial histórico de Beta.
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

- **Campo climático histórico:** v0.9.1 elimina el valor neutral fijo. El ZIP universal usa la temperatura del bioma que proporciona Iris como fallback, sin configuración manual. Para reconstruir el campo espacial de Beta se puede instalar Beta173 Climate Bridge: en un mundo de un jugador obtiene automáticamente la semilla y calcula el ruido en Java. En multijugador remoto, el servidor debe instalar el bridge y activar explícitamente `shareWorldSeed=true`; por privacidad, se encuentra desactivado de forma predeterminada.
- **Ruta ZIP específica de semilla:** también continúa disponible para quien no quiera usar el bridge. La herramienta `configure_climate_pack.py` genera los offsets/texturas dentro de una carpeta temporal y construye un paquete separado; no es necesario editar los fuentes a mano. El modo de lectura de `level.dat` depende de que el archivo incluya la semilla; si no la contiene, se puede indicar con `--seed` o mediante el modo interactivo.
- **Precisión numérica y renderer:** el bridge reconstruye el campo climático mediante Java y puede reproducir la conversión HSB histórica; la salida final, sin embargo, sigue pasando por el pipeline moderno. La ruta heredada que calcula el ruido en GLSL emplea `float` donde Java usa `double`, así que esa ruta no garantiza igualdad bit a bit.
- **Coordenadas de cámara:** la ruta GLSL específica de semilla utiliza `cameraPositionInt` y `cameraPositionFract` para reducir los problemas de precisión en mundos grandes. Esta ruta no debe confundirse con el cálculo climático que proporciona el bridge.
- **Geometría de nubes:** la malla personalizada de Beta forma parte del ZIP oficial v0.9.1 y puede desactivarse desde **Shader Pack Settings** para volver a la geometría moderna. Aunque el geometry shader enlace correctamente, la comprobación visual de cobertura, clipping, transparencia, profundidad y desplazamiento debe hacerse en la combinación real de Minecraft/Iris/Sodium.
- **Pruebas:** la suite automatizada, la integridad del ZIP y la compilación GLSL detectan regresiones estructurales, pero no simulan todo el renderer ni todas las semillas, coordenadas, dimensiones, horas o condiciones meteorológicas.

La prueba visual manual aprobada corresponde a v0.9.0. La nueva geometría de nubes incluida en v0.9.1 requiere su propia validación visual; las pruebas automatizadas no deben presentarse como si esa validación ya se hubiera completado.

## Versión oficial v0.9.1

Descarga `Beta173-Lighting-0.9.1.zip` desde el [README principal del repositorio](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft). Copia el ZIP sin descomprimir a `shaderpacks` y selecciónalo en **Opciones → Ajustes de vídeo → Shader Packs**. La geometría de nubes Beta se configura con `BETA_CUSTOM_CLOUD_GEOMETRY` desde **Shader Pack Settings**: desactívala para volver a la malla moderna si observas problemas en tu versión de Iris. Para el ruido climático espacial histórico, instala también el Climate Bridge opcional en la instancia Fabric compatible.

## Geometría de nubes Beta 1.7.3 (v0.9.1)

La geometría personalizada ya forma parte del ZIP oficial v0.9.1. Utiliza la máscara original `environment/clouds.png`, una cuadrícula de 6×6 celdas de 96×96 bloques, subdivisiones laterales de 12 bloques, 4 bloques de grosor, desplazamiento de 0.03 bloques por tick y sombreado histórico 1.0/0.7/0.9/0.8. La malla se genera en `gbuffers_clouds.gsh` dentro del pase de nubes para conservar el test de profundidad con el terreno.

La opción `BETA_CUSTOM_CLOUD_GEOMETRY` está expuesta en **Shader Pack Settings**. Desactívala para usar la geometría moderna del motor como fallback, sin editar el código fuente.

La automatización valida las pruebas de regresión, la integridad del ZIP y el enlace GLSL de vertex, geometry y fragment. Esto verifica la compatibilidad estructural del shader, pero **no sustituye una comprobación visual en Minecraft**: deben revisarse la cobertura completa de nubes, el clipping, la transparencia, la profundidad y el movimiento en la combinación real de Minecraft/Iris/Sodium. El modelo reconstruye el resultado visible, no la llamada OpenGL separada de depth-only del renderer antiguo.

PR de implementación: [#15 — geometría de nubes Beta](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/pull/15).

## Pruebas

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s Beta173-Lighting/tests -p 'test_*.py' -v
```

Las pruebas de ruido y generación de activos cubren la reproducibilidad de `java.util.Random`, valores de regresión, construcción del mapa de gradientes, lectura de semilla NBT y la generación temporal del paquete. Las pruebas no simulan el renderizador completo de Minecraft.


## Validación de la versión oficial v0.9.1

- [Workflow universal de pruebas y empaquetado](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/actions/workflows/universal-climate.yml): suite Python, construcción del ZIP, integridad y enlace GLSL.
- [Workflow del Climate Bridge](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/actions/workflows/build-climate-bridge.yml): compilación y pruebas automatizadas del mod.
- [Checksum SHA-256 de la versión oficial](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/SHA256SUMS-v0.9.1.txt).

**Prueba visual manual:** completada y aprobada por el autor dentro de Minecraft. Como control de calidad continuo, se recomienda probar nuevas semillas, transiciones de bioma y condiciones de clima. Esto es compatible con el estado oficial de v0.9.0 y no equivale a garantizar paridad píxel a píxel.
