# Beta173 Lighting v0.9.0-pre1 — reconstrucción del campo climático

Shaderpack experimental para Iris que porta el campo de temperatura espacial utilizado por Minecraft Beta 1.7.3 para calcular el tono del cielo. La descarga estable publicada sigue siendo v0.8.1; esta preversión se construye desde las fuentes y requiere datos generados para la semilla del mundo.

## Qué reconstruye

La cadena de referencia es:

1. World.getSkyColor toma las coordenadas X/Z de la posición del jugador.
2. WorldChunkManager.getTemperature(x, z) evalúa ruido Simplex 2D generado desde new Random(worldSeed * 9871L), con cuatro octavas.
3. Cada NoiseGenerator2 consume offsets y genera una permutación desde java.util.Random.
4. BiomeGenBase.getSkyColorByTemp divide la temperatura por 3, limita el resultado a [-1, 1] y calcula el color HSB: h = 0.62222224 - t * 0.05; s = 0.5 + t * 0.1; b = 1.
5. El shader conserva la atenuación diurna y los ajustes de lluvia/tormenta ya portados.

La implementación incluye el consumo de Java Random, offsets y permutaciones de cuatro octavas, el ruido Simplex 2D y la cuantización RGB de 8 bits de Java. Como GLSL opera con float y el original utiliza double, no se garantiza igualdad bit a bit. La fidelidad visual sigue pendiente de validar en Minecraft.

## Construir para una semilla concreta

Iris no expone la semilla del mundo como uniforme estándar. Por eso el shaderpack genérico no puede reconstruir por sí solo la misma permutación para todas las partidas. El generador crea dos recursos específicos:

- shaders/textures/beta173_climate_gradient.png: lookup de índices de gradiente para las cuatro octavas.
- shaders/lib/climate_seed.glsl: offsets de octava y marca de configuración.

Entra al mundo, ejecuta /seed y copia el número. Desde la raíz del repositorio, ejecuta:

    python3 Beta173-Lighting/tools/generate_climate_seed.py --seed SEMILLA_REAL
    python3 Beta173-Lighting/tools/build_pack.py 0.9.0-pre1

Sustituye SEMILLA_REAL por el valor real, incluido el signo menos cuando corresponda. El ZIP generado queda personalizado para ese mundo; genera otra vez los recursos para otra semilla. No publiques los archivos generados si prefieres mantener privada la semilla.

Si no ejecutas el generador, el shader conserva el valor neutral BETA_SKY_TEMPERATURE 0.5 como respaldo. No hace falta modificar el código Java del juego.

Si la cámara se reinicia al desplazarse a distancias muy largas, comprueba la continuidad espacial. El generador acepta los argumentos opcionales --origin-x y --origin-z para ajustar el origen si la instalación concreta de Iris lo requiere. No se deben cambiar sin antes verificar el problema.

## Validación

Ejecuta desde la raíz:

    python3 -m unittest discover -s Beta173-Lighting/tests -p 'test_*.py' -v

La suite climática cubre la secuencia de Java Random, vectores numéricos de referencia, cuatro permutaciones, variación espacial, la textura PNG, los offsets, la reconstrucción de posición del jugador y la conversión HSB/RGB. Las pruebas automatizadas no demuestran que GLSL compile en todas las configuraciones ni sustituyen una comparación visual dentro de Minecraft.

## Límites conocidos

- La semilla debe proporcionarse manualmente; no se lee automáticamente desde el mundo.
- La evaluación GLSL no es bit a bit idéntica al cálculo Java de doble precisión.
- El origen de cámara y la posición del jugador deben comprobarse en distintas distancias y perspectivas.
- Falta validación visual comparativa del cielo bajo distintos tiempos, biomas y estados meteorológicos.
- Esta preversión no modifica la geometría de nubes ni la corrección de sombreado de sus caras.

## Descarga estable

La versión descargable estable continúa siendo Beta173-Lighting-0.8.1.zip, disponible en el README principal. No existe un ZIP universal v0.9 preconfigurado porque cada compilación experimental depende de la semilla del mundo objetivo.
