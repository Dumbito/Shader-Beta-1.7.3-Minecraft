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

// Aproximacion neutral: falta recuperar la temperatura real del bioma.
#define BETA_SKY_TEMPERATURE 0.5
