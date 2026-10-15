# Beta173 Lighting
### Reconstruyendo la iluminación, el cielo y la atmósfera de Minecraft Beta 1.7.3 en Minecraft moderno

> **v1.0.1 — parche de nubes:** mejora la visibilidad del color de las nubes durante la noche con un mínimo configurable, sin cambiar geometría, altura, máscara alfa ni desplazamiento. Se mantiene como requisito la prueba visual para cualquier desaparición geométrica o fallo de profundidad.

<p align="center">
  <strong>Un proyecto de ingeniería inversa visual, traducción matemática y shaders GLSL para Iris; v1.0.0 es la primera versión estable oficial.</strong>
</p>

<p align="center">
  <a href="https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-1.0.1.zip">Descargar v1.0.1 — parche de nubes</a> ·
  <a href="https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-1.0.0.zip">Descargar v1.0.0 estable anterior</a> ·
  <a href="https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.9.0.zip">Descargar v0.9.0 (versión anterior; prueba visual aprobada)</a> ·
  <a href="https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.8.1.zip">Descargar v0.8.1 (versión anterior)</a> ·
  <a href="https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Climate-Bridge-0.1.0-mc26.3.jar">Descargar Climate Bridge 0.1.0 (Fabric 26.3)</a> ·
  <a href="https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.9.0-pre1.zip">Descargar v0.9.0-pre1 (base anterior)</a> ·
  <a href="https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-v0.9-climate-builder.zip">Kit generador climático por semilla</a> ·
  <a href="https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/actions/workflows/universal-climate.yml">Pruebas y publicación de v1.0.0</a> ·
  <a href="https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/tree/main/Beta173-Lighting">Código actualizado en main</a> ·
  <a href="https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/blob/main/Beta173-Lighting/README.md">Guía de v1.0.0</a> ·
  <a href="https://github.com/jacobo-mc/mc_b1.7.3_release">Referencia de Minecraft Beta 1.7.3</a>
</p>

---

## 🩹 v1.0.1 — visibilidad de nubes al anochecer y durante la noche

**Parche de mantenimiento sobre la versión estable v1.0.0.** Conserva la geometría nativa predeterminada y la malla Beta experimental: no cambia la forma, la altura ni la velocidad de desplazamiento de las nubes.

- Añade `BETA_CLOUD_NIGHT_MIN_DAYLIGHT` (predeterminado `0.12`), ajustable desde **Shader Pack Settings**. Modifica solamente el RGB: evita que el color de las nubes se confunda con el cielo oscuro.
- No introduce un cambio brusco en los ticks 12 000 o 13 000. La respuesta sigue la curva celeste y continúa de forma gradual por anochecer, noche y amanecer.
- La opacidad no se vincula al reloj: el modo estable conserva `cloudColor.a`; la geometría experimental conserva `mask.a`. No se agrega ningún recorte de alfa por hora.
- Añade pruebas de regresión para ticks críticos (12 000, 13 000, noche profunda, amanecer y retorno a 0) y para la opacidad de ambas rutas.

**Alcance del parche:** el código de color no puede demostrar por sí solo que se haya corregido un problema real de profundidad o de emisión de geometría. Si las nubes también desaparecen cuando el color se fuerza visible, hace falta una prueba dentro de Minecraft para aislar renderizado/profundidad; no se declara resuelto un fallo de depth-buffer sin esa comprobación.

**Instalación:** descarga el ZIP v1.0.1, cópialo sin descomprimir a `shaderpacks` y selecciónalo en Shader Packs. No hace falta editar archivos GLSL.

---

## ✅ v1.0.0 — primera versión estable oficial

**Beta173 Lighting v1.0.0** queda publicada como primera versión estable del proyecto. El ZIP universal conserva funcionamiento automático sin tener que editar GLSL, copiar texturas ni introducir la semilla manualmente. Si se desea el campo climático espacial de Beta 1.7.3, el Climate Bridge opcional reconstruye el ruido a partir de la semilla real cuando el entorno la proporciona.

### Qué consolida v1.0.0

- **Validación diferencial ejecutable:** la suite compila y ejecuta una referencia Java transcrita desde las clases de Beta 1.7.3 y compara resultados de esa implementación con el port y sus expresiones equivalentes.
- **Matriz ampliada:** 144 casos de ruido climático por combinación de semillas y coordenadas (incluidos signos negativos y extremos); 14 casos de temperatura/HSB alrededor de sus límites; 1.540 evaluaciones del color del cielo con diferentes semillas, coordenadas, horas, lluvia y tormenta; 560 combinaciones de ciclo celeste, tiempo parcial, condiciones meteorológicas, resta de luz del cielo y brillo de estrellas; y 32 entradas de la curva de brillo.
- **Nubes con comportamiento seguro por defecto:** la malla nativa de Minecraft se conserva como opción predeterminada para evitar depender de cómo Iris divida las invocaciones del geometry shader. La geometría personalizada inspirada en Beta sigue disponible como opción experimental en Shader Pack Settings.
- **Flujo climático sin modificación manual:** el ZIP universal funciona con el fallback automático de Iris; para el campo climático histórico, el Climate Bridge obtiene y calcula la semilla en un mundo local, mientras que los servidores dedicados deben compartirla de forma explícita.
- **Paquete y documentación:** CI construye el ZIP oficial, comprueba su integridad, busca includes sin resolver y enlaza las etapas GLSL. El workflow publica los artefactos y su checksum.

### Qué significan los resultados

La referencia Java ejecuta las ecuaciones climáticas, la conversión HSBtoRGB, la tabla trigonométrica histórica de MathHelper, la curva de brillo y otros cálculos relevantes. La implementación GLSL utiliza `float` y el pipeline moderno, mientras que partes de Java trabajan con `float`, `double` o tablas lookup en fases específicas. Por ello, las tolerancias están declaradas en las pruebas: la comparación automatizada demuestra coherencia numérica dentro de límites definidos, **no** identidad bit a bit ni paridad píxel a píxel en Minecraft.

La suite cubre casos representativos y límites intencionales, pero no sustituye una prueba visual en cada versión de Minecraft, Iris, Sodium, driver o GPU. En v1.0.0 la malla custom de nubes no se activa por defecto; el usuario puede probarla bajo su propia combinación si desea comparar con el aspecto geométrico de Beta.

### Descargas y verificación

- [**Descargar Beta173-Lighting v1.0.0 (.zip)**](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-1.0.0.zip)
- [**Beta173 Climate Bridge 0.1.0 — Fabric 26.3 (opcional)**](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Climate-Bridge-0.1.0-mc26.3.jar)
- [Checksum SHA-256 oficial v1.0.0](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/SHA256SUMS-v1.0.0.txt)
- [Workflow de validación y publicación](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/actions/workflows/universal-climate.yml)
- [Matriz diferencial Java](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/blob/main/Beta173-Lighting/tests/test_v10_java_differential.py)

La v0.9.1 queda conservada como versión anterior y se mantiene su historial. Esta edición marca el primer punto estable basado en pruebas diferenciales más amplias, paquete reproducible y opción segura por defecto para las nubes.

---

### Beta173 Climate Bridge — port climático mediante mod

El mod [Beta173-Climate-Bridge](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/tree/main/Beta173-Climate-Bridge) reconstruye en Java la secuencia de ruido Simplex de cuatro octavas basada en la semilla del mundo usada por Beta 1.7.3. En lugar de exigir cambios a mano en GLSL, intercepta el uniforme existente `temperature` de Iris 1.11.6 para Minecraft 26.3. No añade bloques, objetos, interfaces ni recursos visuales.

- [Descargar el mod compilado para Fabric 26.3 (JAR)](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Climate-Bridge-0.1.0-mc26.3.jar)
- [Descargar el código fuente completo (ZIP)](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Climate-Bridge-0.1.0-source.zip)
- [Ver las pruebas y el workflow de compilación](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/actions/workflows/build-climate-bridge.yml)

**Servidor y privacidad:** en un mundo de un jugador la semilla se envía desde el servidor integrado al cliente local. En un servidor dedicado, la opción `shareWorldSeed=true` de `config/beta173-climate-bridge.properties` debe activarse expresamente por el administrador; por defecto está desactivada. Si no llega una semilla compatible, el mod deja intacto el valor de Iris y actúa como fallback.

**Compatibilidad de v0.9.0:** Minecraft Java 26.3, Fabric Loader 0.19.5+, Fabric API 0.162.0+26.3, Iris 1.11.6+mc26.3 y Java 25+. La suite automatizada cubre el código y el empaquetado; además, el autor confirmó que la prueba visual manual del shaderpack se completó y aprobó en Minecraft.

---

## 📦 v0.9.0-pre1 — paquete de transición anterior

**Estado: archivo histórico anterior a la v0.9.0 oficial; no es la descarga estable actual.** Se conservan dos archivos por compatibilidad: el [ZIP base instalable](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.9.0-pre1.zip), que mantiene el fallback neutral hasta conocer la semilla, y el [kit generador climático](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-v0.9-climate-builder.zip), que crea un ZIP específico para tu mundo sin editar código. Iris no expone por sí solo la semilla cruda a los shaders; por eso el paquete de pre1 exigía generar datos por mundo. La rama universal añade un fallback sin semilla y un bridge opcional para recuperar el cálculo exacto cuando la semilla está disponible. La prueba visual manual de v0.9.0 fue completada y aprobada por el autor; el archivo pre1 se conserva solo como referencia histórica y no es el paquete recomendado.

La ruta específica por semilla reconstruye la cadena histórica completa:

- `World.getSkyColor(x,z)` pide la temperatura espacial en las coordenadas X/Z del jugador.
- `WorldChunkManager.getTemperature` combina cuatro octavas de `NoiseGeneratorOctaves2`, inicializadas desde `new Random(worldSeed * 9871L)`.
- Cada `NoiseGenerator2` aporta offsets, la permutación de `java.util.Random`, los gradientes Simplex 2D y las ponderaciones históricas por octava.
- `BiomeGenBase.getSkyColorByTemp` aplica HSB y cuantiza cada canal RGB a 8 bits como Java; después continúan la atenuación diurna, la lluvia y la tormenta portadas en versiones anteriores.
- Para evitar multiplicar el coste del ruido por cada píxel, la temperatura del jugador se calcula por vértice y se pasa como valor plano a los programas de terreno y entidades que aplican niebla.

### Crear tu ZIP climático sin editar líneas de código

Elige la forma más cómoda. No es necesario abrir ni modificar archivos GLSL, ni reemplazar texturas manualmente.

**A. Leer la semilla desde un mundo local**

```bash
python3 Beta173-Lighting/tools/configure_climate_pack.py --world "/ruta/a/saves/Mi mundo"
```

Pasa la carpeta del mundo o directamente su archivo `level.dat`. La herramienta intenta extraer `Data.WorldGenSettings.seed` en mundos modernos y `Data.RandomSeed` en formatos clásicos.

**B. Usar el número de `/seed`**

```bash
python3 Beta173-Lighting/tools/configure_climate_pack.py --seed 123456789
```

Sustituye `123456789` por la semilla exacta de tu mundo, incluido el signo si es negativa. Esta opción es útil en servidores o cuando el archivo local no contiene la semilla.

**C. Dejar que la herramienta la pida**

```bash
python3 Beta173-Lighting/tools/configure_climate_pack.py
```

Copia el número que muestra `/seed` cuando aparezca la solicitud.

Por defecto, el ZIP se guarda en el directorio actual. Para indicar una carpeta, añade por ejemplo `--output-dir "$HOME/Descargas"`. La herramienta trabaja sobre una copia temporal: genera la tabla climática y los offsets, configura la textura Iris y construye/valida el ZIP sin modificar los archivos originales del repositorio. El nombre del ZIP incluye la semilla para distinguirlo.

Instala el ZIP resultante en la carpeta `shaderpacks` de la instancia con la que juegas **ese mismo mundo**. Al cambiar de mundo con una semilla distinta, genera otro ZIP con esa semilla.

### Qué está reconstruido y qué falta validar

La estructura del ruido, sus cuatro octavas, la inicialización de aleatoriedad, la tabla de gradientes y la conversión histórica del color están implementadas. El cálculo usa las coordenadas enteras de cámara no desplazadas que expone Iris y recupera la fracción de posición, lo que evita depender del uniforme `cameraPosition` que se reinicia para mantener precisión.

Aun así, esto **no promete igualdad bit a bit**: Java hace el cálculo climático con `double`, mientras que los shaders usan `float`; pequeñas diferencias pueden aparecer cerca de los umbrales de cuantización RGB. La prueba visual manual de v0.9.0 fue completada y aprobada por el autor. Se pueden ampliar las pruebas con nuevas semillas, coordenadas y condiciones meteorológicas; no se afirma paridad píxel a píxel con Beta.

---

## 🌌 ¿Qué es Beta173 Lighting?

**Beta173 Lighting es un shaderpack de reconstrucción visual que recupera parte del comportamiento de Minecraft Java Edition Beta 1.7.3 dentro del pipeline moderno mediante Iris y GLSL. La v1.0.0 es la primera versión estable oficial; no reemplaza el motor completo ni promete identidad píxel a píxel.**

No pretende ser una copia exacta del motor antiguo ni un mod que sustituya el código interno de Minecraft. El proyecto selecciona sistemas concretos del renderizado histórico —la curva de iluminación, la pérdida de luz del cielo, el color del cielo y de la niebla, el ciclo de las estrellas y el aspecto de las nubes— y los vuelve a expresar como programas de shader compatibles con la arquitectura moderna.

La idea central es sencilla:

> **No basta con hacer que Minecraft moderno se vea “retro”. Queremos estudiar cómo calculaba Beta 1.7.3 determinados efectos y trasladar esas reglas, hasta donde permite un shaderpack, al pipeline gráfico actual.**

Este objetivo combina tres trabajos que se complementan:

1. **Investigación del comportamiento histórico:** localizar las funciones relevantes en el código Java de referencia y entender qué entradas y operaciones producen un resultado visual.
2. **Portado matemático:** expresar esas operaciones en GLSL, adaptando sus entradas a los uniformes, texturas, coordenadas y etapas de renderizado disponibles en Iris.
3. **Validación y experimentación:** probar las ecuaciones con Python, protegerlas mediante pruebas de regresión, comprobar el empaquetado, validar los programas GLSL cuando sea posible y, finalmente, inspeccionar su apariencia dentro del juego.

El resultado es una reconstrucción progresiva, no una afirmación de equivalencia total. Cada versión añade una parte del comportamiento, descubre límites del pipeline moderno y corrige las discrepancias que vamos identificando.

## 🧭 Índice

- [La inspiración y las referencias](#-la-inspiración-y-las-referencias)
- [Qué proyectos y tecnologías utilizamos](#-qué-proyectos-y-tecnologías-utilizamos)
- [Cómo trasladamos Beta a un motor moderno](#-cómo-trasladamos-beta-a-un-motor-moderno)
- [Los sistemas que reconstruimos](#-los-sistemas-que-reconstruimos)
- [Historia completa: v0.1–v1.0.0](#-historia-completa-v01v100)
- [Arquitectura del repositorio](#-arquitectura-del-repositorio)
- [Configuración](#️-configuración)
- [Instalación](#-instalación)
- [Pruebas y validación](#-pruebas-y-validación)
- [Limitaciones conocidas](#️-limitaciones-conocidas)
- [Objetivos futuros](#-objetivos-futuros)
- [Créditos y referencias](#-créditos-y-referencias)

---

## ✨ La inspiración y las referencias

### Minecraft Beta 1.7.3: el objetivo visual e histórico

La inspiración principal es **Minecraft Java Edition Beta 1.7.3**. El interés no está únicamente en sus texturas o en una estética pixelada; está en la forma en que se comportaban la iluminación y la atmósfera del juego.

En Beta, el aspecto de una escena estaba relacionado con reglas concretas: una tabla de brillo con una curva determinada, un ángulo celeste suavizado, una reducción de luz del cielo a lo largo del día, ajustes por lluvia y tormenta, una transición entre el cielo y la niebla, y un ciclo de brillo para las estrellas. El renderizado de las nubes también tenía una respuesta de color y factores de sombreado específicos.

Beta173 Lighting toma esas reglas como **referencia de comportamiento**, no como una orden de replicar indiscriminadamente cada efecto del juego original. Priorizamos los componentes que pueden estudiarse y aproximarse razonablemente dentro de un shaderpack moderno.

### El código Java reconstruido de Beta 1.7.3

La referencia técnica directa que documenta el proyecto es [jacobo-mc/mc_b1.7.3_release](https://github.com/jacobo-mc/mc_b1.7.3_release), una reconstrucción del código fuente de Minecraft Beta 1.7.3.

Consultamos métodos y clases como:

- <code>WorldProvider</code>: tabla de brillo, ángulo celeste y propiedades del mundo.
- <code>WorldProviderHell</code>: diferencias históricas del Nether, como su iluminación ambiental.
- <code>World</code>: atenuación de la luz del cielo y brillo de las estrellas.
- <code>EntityRenderer</code>: color de niebla y configuración histórica de determinados efectos.
- <code>RenderGlobal</code>: generación de estrellas y renderizado de nubes.
- <code>World.drawClouds</code> y la rutina de nubes de <code>RenderGlobal</code>: comportamiento de color y factores por cara de las nubes.

Los nombres exactos pueden variar entre versiones o reconstrucciones, por lo que la referencia se usa para estudiar la lógica y contrastar sus fórmulas.

**Esta referencia no es un motor que Beta173 Lighting ejecute en tiempo real.** No se introduce un segundo Minecraft, no se llama al código Java histórico desde el shader y no se necesita compilar la referencia para jugar. Se transcriben las operaciones relevantes y se reimplementan en otro lenguaje y en otro punto de la arquitectura.

### ¿Qué significa “inspirado por” y qué significa “tomado de”?

Es importante distinguir tres cosas:

| Elemento | Función en este proyecto |
|---|---|
| Minecraft Beta 1.7.3 | Es la referencia histórica y visual que intentamos aproximar. |
| <code>mc_b1.7.3_release</code> | Es la fuente de consulta para investigar las fórmulas y el comportamiento Java. |
| Iris, GLSL y el pipeline moderno | Son el entorno técnico donde se implementan de nuevo esas reglas. |

El historial del proyecto incluye el uso inicial de un repositorio de referencia y su posterior exclusión del árbol principal del proyecto. El shaderpack publicado no necesita ese repositorio de referencia como dependencia durante la partida. Las funciones relevantes se expresan de nuevo para el shaderpack.

Esto no significa que cada idea matemática sea nueva: precisamente intentamos reproducir resultados históricos. Por eso damos crédito a la referencia y diferenciamos claramente entre **usar código como fuente de estudio** e **incluir o ejecutar ese código como parte del producto**.

---

## 🧰 Qué proyectos y tecnologías utilizamos

### Iris Shaders: el cargador y la interfaz de shaders

[Iris Shaders](https://github.com/IrisShaders/Iris) proporciona la infraestructura para cargar shaderpacks y expone al shader una serie de datos del renderizado. Beta173 Lighting se organiza como programas GLSL que Iris ejecuta en las etapas correspondientes.

Según la etapa y la versión, el shader puede recibir datos como la hora del mundo, la intensidad de lluvia, información sobre la dimensión, coordenadas de la textura de iluminación, color de vértice, matrices de cámara o parámetros de niebla. Esos datos hacen posible reconstruir parte del comportamiento histórico sin cambiar el código Java del juego.

El contrato real depende de la versión de Iris y del pipeline que esté utilizando. Por eso comprobar un archivo GLSL aislado no garantiza que todos los uniformes se comporten igual en cualquier versión.

### Sodium: rendimiento del renderizado moderno

[Sodium](https://github.com/CaffeineMC/sodium) forma parte del entorno moderno en el que se prueba el shaderpack. No es el motor histórico de Beta ni el origen de las fórmulas: es una parte del entorno de renderizado actual.

La combinación concreta de Minecraft, Iris y Sodium puede afectar a qué geometría, etapas y datos llegan al shader. Por eso el proyecto incluye comprobaciones estáticas, pero reserva la última palabra sobre el aspecto visual a la prueba dentro del juego.

### GLSL: volver a escribir las reglas, no llamar al código antiguo

Los shaders están escritos en GLSL. Funciones como <code>beta173Brightness</code>, <code>beta173CelestialAngle</code>, <code>beta173SkySubtracted</code>, <code>beta173FogColor</code> y <code>beta173ApplyFog</code> representan operaciones portadas a este lenguaje.

Una función Java del pasado no se convierte automáticamente en un shader correcto. Hay que identificar qué datos tenía la función original, qué parte de esos datos está disponible en GPU y qué diferencias aparecen al transformar coordenadas, rangos numéricos, interpolaciones, colores y etapas de mezcla.

### Python y las herramientas de construcción

Python cumple dos funciones principales:

- **Validación:** pruebas numéricas, comparaciones diferenciales, comprobaciones de invariantes y pruebas de regresión para proteger los comportamientos que ya se han reconstruido.
- **Construcción:** generación del mapa de estrellas y empaquetado final del shaderpack.

El script <code>Beta173-Lighting/tools/build_pack.py</code> resuelve los <code>#include</code> utilizados durante el desarrollo e incrusta las bibliotecas en los programas finales. Así se evita que el ZIP dependa de que el ordenador de cada jugador resuelva esas directivas de inclusión.

---

## 🔬 Cómo trasladamos Beta a un motor moderno

Un shaderpack no tiene acceso a todo lo que hacía el motor Java histórico. Esa restricción determina tanto el diseño como los límites de la reconstrucción.

### 1. Investigar la regla original

Primero localizamos la función de referencia y aislamos la operación que interesa. Por ejemplo, una curva de brillo puede depender del nivel de luz; la atenuación del cielo depende del ciclo celeste y del clima; el color de niebla puede mezclar un color base con el del cielo y modificarse por lluvia o tormenta.

No tratamos una captura de pantalla como especificación matemática suficiente: el objetivo es identificar la regla que podría producir el comportamiento observado.

### 2. Separar los datos históricos de los datos del motor moderno

Beta 1.7.3 y Minecraft actual no presentan al shader los mismos datos con la misma semántica. El shaderpack debe tomar las entradas modernas que sí existen y convertirlas, cuando es posible, a los rangos que espera la fórmula histórica.

Por ejemplo, el shader recibe coordenadas de una textura de iluminación moderna. Para aproximar niveles históricos discretos, las normaliza, limita el rango y las traduce a una escala de 0 a 15. Esto recupera una representación útil para la fórmula, pero **no recrea la propagación original de la luz por el mundo**.

### 3. Traducir la ecuación a GLSL

La matemática se vuelve una función de shader. El caso de la iluminación contiene una curva de brillo; el del ciclo celeste mantiene las operaciones de normalización y suavizado angular; la atenuación de cielo combina el factor del día con lluvia y tormenta.

En esta fase también se decide dónde aplicar cada operación. Una función de iluminación aplicada a terreno no afecta por sí sola a la mano, los objetos, las entidades o las nubes: cada grupo puede recorrer una etapa diferente del pipeline de Iris. Para cubrir varios grupos se necesitan programas compatibles con esas etapas.

### 4. Adaptar las dimensiones y las propiedades del motor

Los datos de Iris ayudan a distinguir escenarios que históricamente se calculaban dentro de Java. En v0.8.1, por ejemplo, el shader comprueba si la dimensión tiene luz de cielo y si tiene techo. Con esa información separa la ruta del Nether de la del End.

Esto evita asumir que todas las dimensiones sin cielo deben compartir el mismo aspecto. Para el Nether se conserva una aproximación histórica de niebla rojiza; para el End se recurre a parámetros nativos de niebla que expone el motor moderno. En el Overworld se mantiene el perfil histórico de niebla desarrollado para el proyecto.

### 5. Proteger la traducción con pruebas

Cada corrección puede deshacer accidentalmente una fórmula anterior. Por eso las pruebas reflejan las ecuaciones en Python y comparan resultados en varias horas del ciclo o condiciones meteorológicas. Otras pruebas comprueban que existan funciones y constantes esperadas y que el ZIP tenga el formato previsto.

Las pruebas responden preguntas acotadas: ¿coincide la ecuación transcrita?, ¿se mantiene dentro del rango?, ¿está resuelto el empaquetado?, ¿quedan directivas <code>#include</code>? No responden por sí solas si una nube se ve natural desde arriba o si el color del cielo es idéntico en una partida real.

### El flujo, de la referencia al juego

~~~mermaid
flowchart TD
    A["Código Java de referencia de Beta 1.7.3"] --> B["Identificar función y comportamiento"]
    B --> C["Transcribir la regla matemática"]
    C --> D["Adaptar entradas y coordenadas a Iris"]
    D --> E["Implementar funciones GLSL"]
    E --> F["Pruebas numéricas y de regresión en Python"]
    F --> G["Construir ZIP e incrustar includes"]
    G --> H["Validar integridad y programas GLSL"]
    H --> I["Probar visualmente en Minecraft + Iris + Sodium"]
    I --> J["Registrar diferencias y corregir"]
    J --> B
~~~

Este ciclo es iterativo. Una versión nueva no implica que todo el juego se haya reconstruido: representa un conjunto concreto de sistemas implementados o corregidos.

---

## 💡 Los sistemas que reconstruimos

### Iluminación por niveles

La curva de brillo histórica se expresa como una función que recibe un nivel de iluminación entre 0 y 15 y devuelve su brillo. El proyecto aplica esa curva a la luz recuperada desde el lightmap moderno.

En términos conceptuales, el flujo es:

1. Leer las coordenadas de luz proporcionadas por el pipeline moderno.
2. Convertirlas a una escala que represente los niveles históricos.
3. Calcular la luz efectiva combinando luz de bloque y luz de cielo atenuada.
4. Evaluar la curva de brillo de Beta.
5. Multiplicar el color del material por ese brillo.

No significa que Minecraft moderno pase a almacenar sus niveles de luz internamente como lo hacía Beta. Es una traducción en la etapa del shader.

### Ciclo celeste y atenuación de la luz del cielo

La función <code>beta173CelestialAngle</code> adapta la interpolación del ángulo celeste de Beta a GLSL. <code>beta173DayFactor</code> deriva de ese ángulo un factor acotado para el día. <code>beta173SkySubtracted</code> reduce la luz del cielo según hora y clima, con atenuación adicional por lluvia y tormenta cuando corresponde.

Estas funciones compartidas permiten que iluminación, cielo, estrellas y niebla se apoyen en una misma referencia temporal. Así se evita crear por separado varios ciclos que podrían divergir entre sí.

### Cielo y niebla

El color del cielo se reconstruye con una aproximación del color HSB usado por el código Java, un factor de día y ajustes por clima. También se reconstruye una transición entre el color de cielo y el de niebla hacia el horizonte.

La niebla histórica del Overworld usa una progresión lineal en aire, con el inicio situado en una fracción de la distancia final configurada. El comportamiento en agua y lava usa atenuaciones exponenciales. La distancia final se elige mediante perfiles inspirados en las opciones históricas de distancia de renderizado.

La versión 0.8.1 añade rutas específicas por dimensión: el Nether utiliza una niebla rojiza y una distancia inicial distinta; el End usa color, densidad, modo y distancias nativas cuando Iris los expone. Esta separación es una adaptación al motor moderno, no una afirmación de que Beta 1.7.3 tuviera la misma implementación de niebla del End que el juego actual.

### Estrellas de Beta

El proyecto estudia la rutina histórica de generación de estrellas de <code>RenderGlobal</code>. El generador de Python implementa el generador congruencial de 48 bits de <code>java.util.Random</code>, usa la semilla 10842 y reproduce el procedimiento de muestreo. De 1500 intentos se aceptan 780 estrellas para la configuración de referencia.

En v0.8 el resultado se rasteriza como un mapa equirectangular. El shader calcula las coordenadas de muestreo a partir de la dirección del cielo, transforma la dirección al marco de estrellas de Beta y suma la contribución según el brillo estelar y la cobertura del mapa.

La textura permite representar la disposición histórica mediante un shader, sin depender exclusivamente del pase nativo de estrellas. Sin embargo, la orientación aparente depende de cómo el motor moderno y el cargador gestionen la textura y las matrices; por ello existen comprobaciones específicas y modos de diagnóstico.

### Nubes

La estrategia actual **no reemplaza por completo el sistema de geometría de nubes de Minecraft moderno**. Iris sigue proporcionando la geometría, el color base y la máscara alfa de su etapa de nubes; el shader modifica principalmente color y sombreado.

El comportamiento de color se inspira en <code>World.drawClouds</code>, con respuesta a hora y clima. Los factores históricos por orientación de las caras se expresan como brillo relativo: superior 1.0, inferior 0.7 y laterales 0.9/0.8. La alfa que llega del motor sigue siendo importante porque define qué fragmentos pertenecen a la nube.

La altura merece una distinción especial. En Beta la altura nominal de nubes era aproximadamente 108,33, mientras que la geometría nativa moderna usa otra altura. v0.8 intentó acercarla a Beta; v0.8.1 adopta **Y=260,99** como remapeo fijo para el rango vertical moderno. No es una equivalencia física perfecta ni un sistema que ajuste automáticamente la altura al terreno; es una decisión de adaptación que debe juzgarse visualmente.

---

## 🗓️ Historia completa: v0.1–v1.0.0

La numeración registra una evolución por capas. Las versiones menores correctivas son importantes: parte del trabajo no consiste en añadir efectos, sino en descubrir que una etapa moderna aplica una mezcla, un color o una geometría que no coincide con la suposición inicial.

| Versión | Enfoque | Qué aportó |
|---|---|---|
| **v0.1** | Prototipo de iluminación | Primera curva de brillo histórica, interpolación del ángulo celeste, atenuación aproximada de luz de cielo por hora y lluvia, y combinación entre luz de cielo atenuada y luz de bloque. |
| **v0.2** | Entidades y objetos | Lleva la iluminación reconstruida más allá del terreno mediante programas para entidades, mano, objetos sostenidos o caídos y block entities. Añade un programa específico para el brillo de encantamiento, que no debe oscurecerse como un material iluminado normal. |
| **v0.3** | Cielo, clima y niebla | Incorpora atenuación por tormenta, iluminación ambiental distinta para dimensiones sin cielo, luz continua experimental, niebla histórica en aire y atenuaciones en agua y lava, color de cielo con transición al horizonte y brillo de estrellas calculado. |
| **v0.4** | Fidelidad de niveles | Vuelve a imponer niveles discretos de luz de 0 a 15 en vez de dejar que la interpolación moderna suavice la entrada. Es una decisión a favor de la curva histórica, aun sabiendo que el resultado ya no es igual a una reconstrucción con iluminación moderna suavizada. |
| **v0.5** | Regresión matemática | Añade pruebas para proteger la tabla de brillo, la periodicidad del ángulo celeste, la atenuación del cielo, el brillo de estrellas y otros invariantes. Las comprobaciones ayudan a distinguir una regresión matemática de un problema visual. |
| **v0.6** | Comparación diferencial | Añade una batería que contrasta transcripciones de fórmulas Java con sus equivalentes matemáticos usados por el shader, a través de distintos tiempos y condiciones meteorológicas. Documenta las brechas que no se pueden igualar únicamente desde GLSL. |
| **v0.7** | Integración de cielo y nubes | Añade configuración para las etapas de cielo, estrellas y nubes de Iris, conservando los sistemas de iluminación y niebla existentes. Comienza el trabajo de adaptar los efectos a los pases reales del motor moderno. |
| **v0.7.1** | Corrección de nubes y estrellas | Añade programas de nubes compatibles con el pase del motor para preservar su geometría, color de vértice y alfa. Corrige la salida del brillo estelar para evitar multiplicaciones de alfa no deseadas. |
| **v0.7.2** | Ciclo de color de nubes | Refina la respuesta de color histórica de las nubes ante día, lluvia y tormenta y restaura la salida RGBA de estrellas observada en la referencia. La geometría y la máscara de las nubes siguen procediendo del motor moderno. |
| **v0.8** | Estrellas de Beta y paquete reproducible | Genera un mapa de estrellas a partir de la rutina histórica, lo integra en el shader del cielo, refina la cobertura de estrellas y el oscurecimiento nocturno de nubes, implementa el sombreado y color de nube inspirados en Beta e incorpora un empaquetador que resuelve los <code>#include</code>. |
| **v0.8.1** | Niebla por dimensión y altura de nubes | Separa las rutas de niebla y luz ambiental de Overworld, Nether y End; el End puede usar parámetros de niebla nativos de Iris. Remapea la altura de las nubes a Y=260,99 para el rango moderno. Fue la versión estable anterior a v0.9.0. |
| **v1.0.0** | Primera versión estable | Amplía la validación diferencial con una referencia Java ejecutable para ruido climático, conversión HSB/RGB, color del cielo, ciclo celeste, meteorología, estrellas y curva de brillo. Corrige el perfil de nubes para que la geometría nativa sea la opción predeterminada y la malla Beta custom sea experimental. CI aprobada para pruebas, ZIP, etapas GLSL y Climate Bridge; no se afirma paridad píxel a píxel. |
| **v0.9.0** | Campo climático universal y Climate Bridge | Publica un shaderpack universal con fallback automático por bioma y un mod opcional que reconstruye el ruido espacial dependiente de la semilla de Beta 1.7.3 sin editar GLSL a mano. CI, empaquetado e integridad validados; la prueba visual manual fue completada y aprobada por el autor. El port conserva limitaciones numéricas entre `double` de Java y `float` de GLSL. |

### La evolución en cuatro etapas

**Etapa I — reconstruir la iluminación (v0.1–v0.2).** El proyecto comienza con el terreno y luego extiende el mismo modelo matemático a objetos, entidades y elementos de la mano. Aparece una lección importante: en Iris no toda la escena atraviesa el mismo programa de shader.

**Etapa II — recuperar la atmósfera (v0.3–v0.6).** Entra el cielo, la niebla, el clima y el control discreto de la luz. Las pruebas matemáticas convierten las fórmulas en reglas verificables, al tiempo que documentan lo que el shader no puede reproducir del motor completo.

**Etapa III — adaptar las etapas visuales (v0.7–v0.8).** Estrellas y nubes presentan problemas distintos a la iluminación de materiales. Se necesita preservar la geometría que genera Minecraft moderno, respetar la mezcla alfa y resolver el mapa de estrellas en el marco correcto. También se construye el ZIP de forma reproducible.

**Etapa IV — diferencias entre dimensiones y altura moderna (v0.8.1).** El foco se desplaza a las propiedades que varían por dimensión y a la altura de las nubes en un mundo con rango vertical moderno. La compatibilidad no se resuelve solo con fórmulas históricas: también requiere utilizar correctamente los parámetros de Iris.

**Etapa V — campo climático universal (v0.9.0).** Se reconstruye el ruido espacial de Beta y se ofrece un fallback automático para mundos sin semilla disponible. El Climate Bridge permite obtener la semilla del mundo localmente y, en multijugador, solo cuando el servidor decide compartirla.

**Etapa VI — validación estable (v1.0.0).** Se añade una referencia Java ejecutable que compara las fórmulas en una matriz amplia de semillas, coordenadas límite, horas, tiempos parciales y clima. El paquete estable conserva las nubes nativas por defecto para reducir incompatibilidades y deja la geometría reconstruida como experimento.

### Documentos y artefactos de versión

- [Paquete v0.8 en la raíz del repositorio](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.8.zip)
- [Paquete oficial v1.0.0 en la raíz del repositorio](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-1.0.0.zip)
- [Paquete histórico v0.9.1 en la raíz del repositorio](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.9.1.zip)
- [Paquete histórico v0.9.0 anterior](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.9.0.zip)
- [Paquete v0.8.1 anterior en la raíz del repositorio](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.8.1.zip)
- [Release v0.8](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/releases/tag/v0.8)
- [Release v0.7.2](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/releases/tag/v0.7.2)
- [Release v0.7.1](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/releases/tag/v0.7.1)
- [Release v0.7](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/releases/tag/v0.7)
- [Fuentes v1.0.0 en main y generador climático](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/tree/main/Beta173-Lighting)
- [Guía de generación por semilla](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/blob/main/Beta173-Lighting/README.md)

---

## 🏗️ Arquitectura del repositorio

La carpeta de fuentes está organizada para permitir que el código común se mantenga separado durante el desarrollo y se incruste al crear el ZIP.

| Ruta | Responsabilidad |
|---|---|
| <code>Beta173-Lighting/shaders/gbuffers_terrain.fsh</code> / <code>.vsh</code> | Iluminación de terreno y aplicación de niebla a la distancia de vista. |
| <code>Beta173-Lighting/shaders/gbuffers_textured_lit.fsh</code> / <code>.vsh</code> | Programa compartido para geometría texturizada iluminada, como entidades, mano y objetos. |
| <code>Beta173-Lighting/shaders/gbuffers_armor_glint.fsh</code> / <code>.vsh</code> | Tratamiento del brillo de encantamiento. |
| <code>Beta173-Lighting/shaders/gbuffers_skybasic.fsh</code> / <code>.vsh</code> | Cielo, gradiente, dirección de estrellas, cobertura del mapa y etapas relacionadas. |
| <code>Beta173-Lighting/shaders/gbuffers_clouds.fsh</code> / <code>.vsh</code> | Color, sombreado y adaptación de altura de las nubes; conserva la geometría de la etapa moderna. |
| <code>Beta173-Lighting/shaders/lib/beta173.glsl</code> | Funciones compartidas para luz, hora del día, cielo, niebla, estrellas y clima. |
| <code>Beta173-Lighting/shaders/lib/config.glsl</code> | Opciones del proyecto: perfiles de niebla, altura de nubes, modo de color y diagnósticos. |
| <code>Beta173-Lighting/shaders/textures/starmap.png</code> | Mapa rasterizado de cobertura de estrellas. |
| <code>Beta173-Lighting/tools/generate_starmap.py</code> | Genera el mapa equirectangular a partir de la geometría histórica de estrellas. |
| <code>Beta173-Lighting/tools/build_pack.py</code> | Resuelve inclusiones, aplica opciones para compilaciones de diagnóstico y construye el ZIP. |
| <code>Beta173-Lighting/tests/</code> | Pruebas de ecuaciones, regresiones, geometría de estrellas y empaquetado. |

### ¿Por qué el ZIP no conserva las carpetas de biblioteca?

Durante el desarrollo, archivos como <code>gbuffers_terrain.fsh</code> incluyen <code>/lib/beta173.glsl</code> y la biblioteca de configuración. Repetir todas esas funciones manualmente en varios programas sería difícil de mantener y podría provocar que la luz o la niebla divergieran entre etapas.

Por eso el código fuente utiliza inclusiones. Al generar el ZIP, <code>build_pack.py</code> incorpora el contenido de esas bibliotecas dentro de cada programa GLSL y no deja las directivas <code>#include</code> sin resolver. Los archivos de <code>lib</code> se omiten como archivos independientes en el paquete final porque su contenido ya está integrado en los programas que lo necesitan.

El ZIP resultante está pensado para instalarse como un shaderpack normal; no es necesario ejecutar Python al iniciar Minecraft.

---

## ⚙️ Configuración

La configuración de las fuentes se encuentra en <code>Beta173-Lighting/shaders/lib/config.glsl</code>. Las opciones disponibles pueden variar entre una rama de desarrollo y el ZIP publicado; si modificas el proyecto, vuelve a generar el paquete después de cada cambio.

### Perfiles históricos de niebla

La opción <code>BETA_RENDER_DISTANCE</code> selecciona el perfil usado por la fórmula histórica:

| Valor | Perfil | Distancia final |
|---:|---|---:|
| <code>0</code> | Far | 256 bloques |
| <code>1</code> | Normal | 128 bloques |
| <code>2</code> | Short | 64 bloques |
| <code>3</code> | Tiny | 32 bloques |

Este selector cambia la distancia de la niebla calculada por el shader. **No controla la cantidad de chunks que Minecraft carga** y no sustituye las opciones de distancia de renderizado del juego.

### Color de las nubes

En la configuración v0.8, <code>BETA_CLOUD_COLOR_MODE</code> ofrece tres comportamientos:

- <code>0</code>: color y sombreado reconstruidos al estilo de Beta; evita multiplicar de nuevo el color completo que entrega el motor.
- <code>1</code>: utiliza el color del motor sin alterarlo.
- <code>2</code>: mantiene el comportamiento experimental de v0.7.2, multiplicando el color reconstruido sobre el color del motor.

Es una herramienta de comparación, no una garantía de que todos los modos luzcan idénticos en cada versión del juego.

### Altura de las nubes

La opción <code>BETA_CLOUD_HEIGHT_FIX</code> activa el desplazamiento de la geometría nativa hacia la altura configurada. En v0.8.1, la altura remapeada del paquete candidato es **Y=260,99**. Para dejar la geometría a la altura moderna por defecto, el ajuste de altura puede desactivarse en el código fuente antes de reconstruir el ZIP.

Este ajuste es fijo. No calcula la altitud óptima en tiempo real ni sigue la forma de montañas y biomas.

### Diagnóstico

<code>BETA_DEBUG</code> ofrece modos de depuración que ayudan a identificar problemas en las etapas de cielo, estrellas, datos del mundo y nubes. Antes de crear una versión normal, vuelve a <code>BETA_DEBUG 0</code>; los otros valores son herramientas de análisis y pueden cambiar intencionadamente los colores de la escena.

Si una opción se cambia en las fuentes, ejecuta de nuevo la batería de pruebas y reconstruye el paquete. Editar un shader dentro de un ZIP ya generado no modifica automáticamente las fuentes del repositorio.

---

## 📦 Instalación

1. Descarga [**Beta173-Lighting-0.9.1.zip**](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Lighting-0.9.1.zip).
2. Copia el ZIP, **sin descomprimirlo**, en `shaderpacks` de la instancia que usa Iris y selecciónalo en **Opciones → Ajustes de vídeo → Shader Packs**.
3. Para activar la reconstrucción climática histórica por semilla, instala opcionalmente [**Beta173 Climate Bridge 0.1.0 para Fabric 26.3**](https://github.com/Dumbito/Shader-Beta-1.7.3-Minecraft/raw/refs/heads/main/Beta173-Climate-Bridge-0.1.0-mc26.3.jar) en `mods/`, junto con Fabric Loader, Fabric API e Iris en las versiones compatibles descritas abajo. En un mundo local, la semilla se obtiene automáticamente.
4. En un servidor dedicado, el envío de semilla sigue desactivado por defecto; solo funciona si el administrador instala el bridge y habilita explícitamente `shareWorldSeed=true`. Si no se comparte la semilla, el shaderpack utiliza el fallback por temperatura del bioma de Iris.

El paquete se instala sin editar código. La prueba visual manual de v0.9.0 fue completada y aprobada por el autor; esto no implica paridad píxel a píxel en toda semilla o condición.

---

## 🧪 Pruebas y validación

Las pruebas tienen objetivos distintos y deben interpretarse por separado.

### Pruebas matemáticas y de regresión

Las pruebas Python reflejan ciertas ecuaciones Java en funciones Python y las comparan con las fórmulas equivalentes del shader. Entre las propiedades comprobadas están:

- Los 16 niveles de la curva de brillo y sus límites.
- La periodicidad del ángulo celeste.
- El rango y la monotonía esperada de la atenuación de luz del cielo.
- Varias combinaciones de hora, lluvia y tormenta.
- La fórmula y los invariantes de brillo de estrellas.
- La presencia de constantes o ramas de shader necesarias para una corrección.
- El tamaño, la cobertura y la reproducibilidad del mapa de estrellas.
- La integridad del ZIP y la resolución de las inclusiones.

Para ejecutar la suite desde la raíz del repositorio:

~~~bash
python3 -m unittest discover -s Beta173-Lighting/tests -p 'test_*.py' -v
~~~

### Validación del empaquetado

El empaquetador comprueba que las inclusiones estén resueltas y que el ZIP contenga las rutas de shaders que necesita. También se puede comprobar la integridad del archivo con:

~~~bash
unzip -t Beta173-Lighting-0.8.1.zip
~~~

### Validación GLSL

Cuando está disponible <code>glslangValidator</code>, se pueden validar los programas emparejando cada vertex shader con su fragment shader correspondiente. La comprobación estática permite detectar errores de sintaxis o de enlace entre etapas, pero no reproduce la compilación ni todos los uniformes internos del entorno real de Iris.

En el candidato v0.8.1 usado durante el desarrollo, **27 pruebas automatizadas pasaron**, el ZIP superó la comprobación de integridad y se validaron cinco pares de programas GLSL. Son resultados estáticos del candidato; no equivalen a una prueba visual automatizada dentro de Minecraft.

### Validación visual manual: superada

El autor confirmó que la prueba visual de la v0.9.0 dentro de Minecraft fue completada y aprobada. Esta comprobación se suma a la suite automatizada, al empaquetado reproducible y al enlace GLSL verificado por CI. Demuestra que la versión probada funciona en el entorno usado, pero no equivale a una prueba automática de todas las combinaciones de semillas, dimensiones, clima y hardware, ni garantiza identidad píxel a píxel con Beta.

---

## ⚠️ Limitaciones conocidas

**Beta173 Lighting reproduce componentes concretos; no reconstruye el motor completo.** Entre las limitaciones actuales se encuentran:

- **Propagación de luz:** un shader no reemplaza los algoritmos Java que calculan, propagan y almacenan la iluminación del mundo. La reconstrucción actúa sobre los datos que ya expone el motor moderno.
- **Lightmap moderno:** las coordenadas del lightmap actual solo pueden convertirse de forma aproximada en los niveles históricos de Beta. La correspondencia no implica que las dos simulaciones de iluminación sean idénticas.
- **Interpolación temporal:** determinadas funciones históricas recibían fracciones de tick o datos del motor que no siempre están disponibles de la misma forma en el shader.
- **Campo climático (v0.9.0):** el ZIP universal funciona sin editar código; con el Climate Bridge obtiene la semilla del mundo local y reconstruye el ruido espacial histórico. Java usa `double` y GLSL `float`, por lo que no se promete igualdad bit a bit aunque la prueba visual manual de v0.9.0 haya sido aprobada.
- **Sol y luna:** el proyecto se centra en el cielo, las estrellas y la niebla; no reconstruye de forma completa la geometría, el movimiento o las fases de los cuerpos celestes históricos.
- **Geometría de nubes:** las nubes utilizan la geometría del motor moderno; todavía no se ha reproducido íntegramente el sistema de celdas, desplazamiento y múltiples pasadas de Beta.
- **Altura de nube:** Y=260,99 es una adaptación fija al rango vertical moderno; puede no ser ideal sobre todos los picos.
- **Niebla por dimensión:** la ruta del End depende de los parámetros nativos que proporcione la versión de Iris utilizada.
- **Compatibilidad de renderizado:** los pases y uniformes disponibles pueden variar entre versiones de Minecraft, Iris y Sodium.
- **Fidelidad visual:** la prueba manual de v0.9.0 fue aprobada por el autor; nuevas combinaciones de Minecraft, Iris, Sodium, semillas o clima pueden requerir validación adicional.

Estas limitaciones son parte de la documentación del proyecto, no una lista de problemas que deban darse necesariamente en todas las instalaciones. Su efecto debe comprobarse con la combinación de software concreta.

---

## 🚧 Objetivos futuros

Las siguientes líneas representan trabajo potencial, no funciones que deban considerarse ya terminadas:

- Corregir y verificar el sombreado de las nubes al observarlas desde arriba y desde abajo, manteniendo una clasificación estable de cada cara.
- Revisar las diferencias entre la geometría de nubes de Beta y la geometría nativa moderna, sin romper la compatibilidad con Iris.
- Refinar la correspondencia entre los niveles de lightmap modernos y los niveles discretos históricos.
- Ampliar las comparaciones diferenciales para más fórmulas y condiciones de borde.
- Ampliar la matriz de validación climática de v0.9.0 con más semillas, coordenadas, horas y condiciones meteorológicas, comparando los resultados con la referencia Java.
- Probar sistemáticamente amanecer, mediodía, atardecer, noche, lluvia, tormenta y niebla en cada dimensión.
- Documentar por versión las combinaciones de Minecraft, Iris y Sodium en las que se haya probado visualmente el shaderpack.
- Mantener los perfiles de diagnóstico y el empaquetado reproducible para que futuras correcciones no deshagan las anteriores.

El orden puede cambiar según los resultados de las pruebas. La prioridad es preferir cambios verificables y reversibles frente a introducir efectos que parezcan correctos en una sola captura, pero fallen en otras condiciones.

---

## 🤝 Créditos y referencias

- **Minecraft Java Edition Beta 1.7.3:** referencia histórica y visual del comportamiento que se intenta reproducir.
- **[jacobo-mc/mc_b1.7.3_release](https://github.com/jacobo-mc/mc_b1.7.3_release):** referencia de código para estudiar las funciones Java y contrastar las fórmulas históricas. No se ejecuta como motor en el shaderpack.
- **[Iris Shaders](https://github.com/IrisShaders/Iris):** cargador de shaderpacks y entorno de integración con el pipeline moderno.
- **[Sodium](https://github.com/CaffeineMC/sodium):** componente del entorno moderno de renderizado usado en las pruebas de compatibilidad.
- **GLSL:** lenguaje utilizado para implementar los programas de shader.
- **Python:** herramientas de pruebas, generación de mapa de estrellas y construcción del paquete.

Las referencias se mencionan para dejar claro de dónde proceden las ideas históricas y cuál es el entorno donde se implementan. Los nombres y las marcas pertenecen a sus respectivos autores y proyectos.

## 📜 Licencia y uso de terceros

Consulta el archivo de licencia que acompañe a cada componente y a cualquier contenido de terceros antes de redistribuirlo o modificarlo. La referencia histórica, la documentación técnica, el código del shaderpack y las texturas generadas pueden tener condiciones distintas. Este README no sustituye las licencias correspondientes.

---

<p align="center">
  <strong>Beta173 Lighting</strong><br>
  Estudiar el pasado del renderizado, traducir sus reglas y comprobar hasta dónde pueden llegar dentro de un motor moderno.
</p>
