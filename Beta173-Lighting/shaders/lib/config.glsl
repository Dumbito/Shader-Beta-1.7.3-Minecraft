// Beta173 Lighting — reconstruccion de la distancia de renderizado de Beta 1.7.3.
// Selector manual: 0 = Far, 1 = Normal, 2 = Short, 3 = Tiny.
// Esto reproduce la matematica historica; no controla los chunks de Iris.

#define BETA_THUNDER
#define BETA_NETHER_AMBIENT
#define BETA_FOG

// Equivalente a GameSettings.renderDistance en Beta 1.7.3.
#define BETA_RENDER_DISTANCE 0

// EntityRenderer.setupCameraTransform y EntityRenderer.updateFogColor.
#if BETA_RENDER_DISTANCE == 0
    #define BETA_FOG_END 256.0
    #define BETA_FOG_SKY_BLEND 0.2928932
#elif BETA_RENDER_DISTANCE == 1
    #define BETA_FOG_END 128.0
    #define BETA_FOG_SKY_BLEND 0.2401643
#elif BETA_RENDER_DISTANCE == 2
    #define BETA_FOG_END 64.0
    #define BETA_FOG_SKY_BLEND 0.1591036
#elif BETA_RENDER_DISTANCE == 3
    #define BETA_FOG_END 32.0
    #define BETA_FOG_SKY_BLEND 0.0
#else
    #error BETA_RENDER_DISTANCE debe ser 0, 1, 2 o 3
#endif

// Fallback solo para rutas de dimensión sin cielo. En el Overworld:
// - el ZIP universal usa automáticamente el uniforme Iris "temperature" si no conoce la semilla;
// - Beta173 Climate Bridge activa el campo histórico exacto en mundos de un jugador;
// - un ZIP específico de semilla usa climate_seed.glsl + climate_noise.glsl.
#define BETA_SKY_TEMPERATURE 0.5

// ---------------------------------------------------------------------------
// Estrellas, nubes y diagnostico (v0.8)
// ---------------------------------------------------------------------------

// Estrellas de Beta dibujadas por este shader dentro del cielo (RenderGlobal.renderStars:
// java.util.Random(10842), 1500 intentos -> 780 estrellas, radio 100, mismo tamano y rotacion).
// No dependen del pase de estrellas del motor, que se descarta. Comenta la linea para volver
// al pase del motor.
#define BETA_STAR_FIELD

// Geometría experimental de nubes Beta mediante geometry shader.
// 0 = geometría nativa de Minecraft + color/sombreado Beta (modo estable por defecto).
// 1 = malla reconstruida de Beta (experimental; puede depender del particionado de draws Iris).
// La opción se puede cambiar desde Shader Pack Settings; no hace falta editar este archivo.
#define BETA_CUSTOM_CLOUD_GEOMETRY 0 // [0 1]

// Horario de nubes: visibles durante el día, ocultas por completo por la noche.
// Ajustables desde Shader Pack Settings; no hace falta editar GLSL.
// Amanecer cruza el tick 24000: empieza antes de 0 y termina de aparecer al tick 1000.
#define BETA_CLOUD_DAWN_START_TICK 22000.0 // [21000 21500 22000 22500 23000]
#define BETA_CLOUD_DAWN_END_TICK 1000.0 // [500 1000 1500 2000 2500]
// Al anochecer desaparecen progresivamente entre los ticks 12000 y 13500.
#define BETA_CLOUD_DUSK_START_TICK 12000.0 // [11000 11500 12000 12500]
#define BETA_CLOUD_DUSK_END_TICK 13500.0 // [13000 13500 14000 14500 15000]


// Color de las nubes:
//   0 = color y sombreado de Beta (World.drawClouds + caras 1.0 / 0.7 / 0.9 / 0.8). Ignora el
//       color del motor, asi que no puede haber oscurecimiento doble.
//   1 = solo el color que da el motor, sin tocarlo.
//   2 = comportamiento de v0.7.2: el color de Beta se multiplica sobre el del motor.
#define BETA_CLOUD_COLOR_MODE 0

// Altura de las nubes. Beta: WorldProvider.getCloudHeight() = 108, mas 0.33 en el render.
// BETA_VANILLA_CLOUD_HEIGHT es la altura que usa el juego moderno (192.33 desde 1.18).
// Comenta BETA_CLOUD_HEIGHT_FIX para dejar las nubes a la altura del juego.
#define BETA_CLOUD_HEIGHT_FIX
#define BETA_VANILLA_CLOUD_HEIGHT 192.33
// Altura moderna: remapea la proporción de Beta (108.33/128)
// al rango Overworld [-64, 320]: -64 + (108.33/128)*384 ~= 260.99.
#define BETA_CLOUD_HEIGHT 260.99

#ifdef BETA_CLOUD_HEIGHT_FIX
    #define BETA_CLOUD_BASE BETA_CLOUD_HEIGHT
#else
    #define BETA_CLOUD_BASE BETA_VANILLA_CLOUD_HEIGHT
#endif

// BETA_DEBUG:
//   0 = apagado (comportamiento normal)
//   1 = cada etapa del cielo se pinta de un color y las nubes salen rojas y opacas:
//         azul = SKY, naranja = SUNSET, MAGENTA = STARS, verde = CUSTOM_SKY,
//         rojo oscuro = VOID, AMARILLO = etapa no reconocida
//   2 = estrellas de Beta al maximo brillo (aunque sea de dia, para ver el mapa)
//   3 = el cielo muestra uniformes: R = lluvia, G = tormenta, B = brillo de estrellas x2
//       (si todo el cielo sale BLANCO, el uniforme hasSkylight no llega al shader)
//   4 = anillo CIAN alrededor de donde Beta pone el sol y anillo NARANJA donde pone la luna;
//       si el sol y la luna del juego quedan centrados en sus anillos, el marco de las estrellas es correcto
#define BETA_DEBUG 0
