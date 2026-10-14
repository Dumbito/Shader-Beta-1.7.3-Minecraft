// Beta173 Lighting v0.4 — perfil histórico estricto.
// Las constantes representan el comportamiento de referencia de Beta 1.7.3.
// No activar suavizado moderno: los niveles de luz originales son discretos.

// World.calculateSkylightSubtracted: atenuación por lluvia y tormenta.
#define BETA_THUNDER

// WorldProviderHell: brillo ambiente 0.1 en dimensiones sin luz de cielo.
#define BETA_NETHER_AMBIENT

// EntityRenderer.setupFog: niebla histórica.
#define BETA_FOG

// Distancia de referencia Beta "Far". El far plane moderno puede diferir.
#define BETA_FOG_END 256.0

// EntityRenderer.updateFogColor en Beta "Far": 1 - (1/4)^0.25.
#define BETA_FOG_SKY_BLEND 0.2928932

// Limitación del shader: Beta elegía este valor según la temperatura del bioma.
// 0.5 es una aproximación neutral hasta disponer de temperatura de bioma fiable.
#define BETA_SKY_TEMPERATURE 0.5
