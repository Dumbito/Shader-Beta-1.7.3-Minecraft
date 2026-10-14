// Beta173 Lighting - opciones.
// Para desactivar una funcion, comenta su linea con //

// Atenuacion de la luz del cielo por tormenta electrica (Beta: World.calculateSkylightSubtracted)
#define BETA_THUNDER

// Brillo minimo 0.1 en dimensiones sin luz de cielo (Beta: WorldProviderHell). En el Overworld sigue siendo 0.05
#define BETA_NETHER_AMBIENT

// Usa el nivel de luz continuo en vez de redondearlo por fragmento (evita escalones con Smooth Lighting)
#define BETA_SMOOTH

// Niebla lineal estilo Beta (inicio al 25% de la distancia) + niebla de agua y lava
#define BETA_FOG

// Distancia de la niebla en bloques. Beta "Far" = 256. Ponla igual o menor a tu render distance (chunks x 16)
#define BETA_FOG_END 192.0

// Cuanto se mezcla el color de niebla con el del cielo (Beta "Far": 1 - 0.25^0.25 = 0.2929)
#define BETA_FOG_SKY_BLEND 0.2929

// Temperatura del bioma usada para el tono del cielo (Beta usaba la del bioma; 0.5 = neutro)
#define BETA_SKY_TEMPERATURE 0.5
