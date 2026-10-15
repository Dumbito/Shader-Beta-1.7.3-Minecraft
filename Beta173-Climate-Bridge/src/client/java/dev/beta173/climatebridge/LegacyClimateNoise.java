package dev.beta173.climatebridge;

import java.util.Random;

/**
 * Java double-precision port of Minecraft Beta 1.7.3's
 * WorldChunkManager.getTemperature -> NoiseGeneratorOctaves2 -> NoiseGenerator2.
 *
 * The original class casts this result to float before getSkyColorByTemp, so sample()
 * deliberately returns float even though the Simplex calculation itself uses double.
 */
public final class LegacyClimateNoise {
    private static final int OCTAVES = 4;
    private static final double BASE_SCALE = 0.02500000037252903D / 1.5D;
    private static final double F2 = 0.5D * (Math.sqrt(3.0D) - 1.0D);
    private static final double G2 = (3.0D - Math.sqrt(3.0D)) / 6.0D;

    private static final int[][] GRADIENTS = {
        {1, 1, 0}, {-1, 1, 0}, {1, -1, 0}, {-1, -1, 0},
        {1, 0, 1}, {-1, 0, 1}, {1, 0, -1}, {-1, 0, -1},
        {0, 1, 1}, {0, -1, 1}, {0, 1, -1}, {0, -1, -1}
    };

    private LegacyClimateNoise() {
    }

    /**
     * Returns the exact historical temperature sample rounded to the float precision
     * used by World.getSkyColor(Entity, partialTick) in Beta 1.7.3.
     */
    public static float sample(long worldSeed, int blockX, int blockZ) {
        // Java long overflow is intentional: this is the source's seed * 9871L.
        Random random = new Random(worldSeed * 9871L);
        Noise2[] octaves = new Noise2[OCTAVES];
        for (int i = 0; i < OCTAVES; i++) {
            octaves[i] = new Noise2(random);
        }

        double value = 0.0D;
        double frequency = 1.0D;
        double amplitudeDenominator = 1.0D;
        for (int i = 0; i < OCTAVES; i++) {
            Noise2 octave = octaves[i];
            double x = (double) blockX * BASE_SCALE * frequency + octave.offsetX;
            double z = (double) blockZ * BASE_SCALE * frequency + octave.offsetZ;
            value += octave.simplex(x, z) * (0.55D / amplitudeDenominator);
            frequency *= 0.5D;
            amplitudeDenominator *= 0.5D;
        }
        return (float) value;
    }

    /**
     * Exact Beta 1.7.3 HSB-to-RGB path. getSkyColor casts noise to float before
     * calling BiomeGenBase.getSkyColorByTemp; Color.getHSBColor performs the same
     * 8-bit conversion and truncation as the original Java implementation.
     */
    public static int skyRgb(float rawTemperature) {
        float temperature = rawTemperature / 3.0F;
        if (temperature < -1.0F) temperature = -1.0F;
        if (temperature > 1.0F) temperature = 1.0F;
        return java.awt.Color.getHSBColor(
            0.62222224F - temperature * 0.05F,
            0.5F + temperature * 0.1F,
            1.0F
        ).getRGB();
    }

    private static int wrap(double value) {
        return value > 0.0D ? (int) value : (int) value - 1;
    }

    private static double dot(int[] gradient, double x, double z) {
        return (double) gradient[0] * x + (double) gradient[1] * z;
    }

    private static double corner(double x, double z, int gradientIndex) {
        double attenuation = 0.5D - x * x - z * z;
        if (attenuation < 0.0D) return 0.0D;
        attenuation *= attenuation;
        return attenuation * attenuation * dot(GRADIENTS[gradientIndex], x, z);
    }

    private static final class Noise2 {
        private final int[] permutation = new int[512];
        private final double offsetX;
        private final double offsetZ;

        private Noise2(Random random) {
            this.offsetX = random.nextDouble() * 256.0D;
            this.offsetZ = random.nextDouble() * 256.0D;
            random.nextDouble(); // The historical third offset is unused by 2D sampling.

            for (int i = 0; i < 256; i++) {
                permutation[i] = i;
            }
            for (int i = 0; i < 256; i++) {
                int j = random.nextInt(256 - i) + i;
                int swap = permutation[i];
                permutation[i] = permutation[j];
                permutation[j] = swap;
                permutation[i + 256] = permutation[i];
            }
        }

        private double simplex(double x, double z) {
            double skew = (x + z) * F2;
            int i = wrap(x + skew);
            int j = wrap(z + skew);
            double unskew = (double) (i + j) * G2;
            double x0 = x - ((double) i - unskew);
            double z0 = z - ((double) j - unskew);

            int i1;
            int j1;
            if (x0 > z0) {
                i1 = 1;
                j1 = 0;
            } else {
                i1 = 0;
                j1 = 1;
            }

            double x1 = x0 - (double) i1 + G2;
            double z1 = z0 - (double) j1 + G2;
            double x2 = x0 - 1.0D + 2.0D * G2;
            double z2 = z0 - 1.0D + 2.0D * G2;

            int ii = i & 255;
            int jj = j & 255;
            int gi0 = permutation[ii + permutation[jj]] % 12;
            int gi1 = permutation[ii + i1 + permutation[jj + j1]] % 12;
            int gi2 = permutation[ii + 1 + permutation[jj + 1]] % 12;

            return 70.0D * (
                corner(x0, z0, gi0)
                + corner(x1, z1, gi1)
                + corner(x2, z2, gi2)
            );
        }
    }
}
