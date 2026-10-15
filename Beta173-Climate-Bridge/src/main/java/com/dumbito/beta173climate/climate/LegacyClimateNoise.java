package com.dumbito.beta173climate.climate;

import java.util.Random;

/**
 * Double-precision port of Beta 1.7.3's WorldChunkManager.getTemperature and its
 * NoiseGeneratorOctaves2/NoiseGenerator2 implementation. Math operation order and Java Random
 * are intentionally retained to minimize differences from the legacy game.
 */
public final class LegacyClimateNoise {
    private static final double SCALE = 0.02500000037252903D;
    private static final double F2 = 0.5D * (Math.sqrt(3.0D) - 1.0D);
    private static final double G2 = (3.0D - Math.sqrt(3.0D)) / 6.0D;
    private static final int[][] GRADIENTS = {
            {1, 1, 0}, {-1, 1, 0}, {1, -1, 0}, {-1, -1, 0},
            {1, 0, 1}, {-1, 0, 1}, {1, 0, -1}, {-1, 0, -1},
            {0, 1, 1}, {0, -1, 1}, {0, 1, -1}, {0, -1, -1}
    };

    private final SimplexOctave[] octaves = new SimplexOctave[4];

    public LegacyClimateNoise(long worldSeed) {
        Random random = new Random(worldSeed * 9871L);
        for (int i = 0; i < octaves.length; i++) {
            octaves[i] = new SimplexOctave(random);
        }
    }

    /** Returns the original noise temperature at a Beta-era block X/Z coordinate. */
    public double temperatureAt(int blockX, int blockZ) {
        double value = 0.0D;
        double frequency = 1.0D;
        double amplitude = 1.0D;
        double scaleX = SCALE / 1.5D;
        double scaleZ = SCALE / 1.5D;

        for (SimplexOctave octave : octaves) {
            double x = (double) blockX * scaleX * frequency + octave.offsetX;
            double z = (double) blockZ * scaleZ * frequency + octave.offsetZ;
            value += octave.sample(x, z) * (0.55D / amplitude);
            frequency *= 0.5D;
            amplitude *= 0.5D;
        }
        return value;
    }

    private static int wrap(double value) {
        return value > 0.0D ? (int) value : (int) value - 1;
    }

    private static double gradientDot(int[] gradient, double x, double z) {
        return (double) gradient[0] * x + (double) gradient[1] * z;
    }

    private static double corner(double x, double z, int gradientIndex) {
        double attenuation = 0.5D - x * x - z * z;
        if (attenuation < 0.0D) {
            return 0.0D;
        }
        attenuation *= attenuation;
        return attenuation * attenuation * gradientDot(GRADIENTS[gradientIndex], x, z);
    }

    private static final class SimplexOctave {
        private final int[] permutation = new int[512];
        private final double offsetX;
        private final double offsetZ;

        private SimplexOctave(Random random) {
            offsetX = random.nextDouble() * 256.0D;
            offsetZ = random.nextDouble() * 256.0D;
            random.nextDouble(); // Beta consumes the unused Y offset before shuffling.

            for (int i = 0; i < 256; i++) {
                permutation[i] = i;
            }
            for (int i = 0; i < 256; i++) {
                int swapIndex = random.nextInt(256 - i) + i;
                int previous = permutation[i];
                permutation[i] = permutation[swapIndex];
                permutation[swapIndex] = previous;
                permutation[i + 256] = permutation[i];
            }
        }

        private double sample(double pointX, double pointZ) {
            double skew = (pointX + pointZ) * F2;
            int i = wrap(pointX + skew);
            int j = wrap(pointZ + skew);
            double unskew = (double) (i + j) * G2;
            double x0 = pointX - ((double) i - unskew);
            double z0 = pointZ - ((double) j - unskew);

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
            int g0 = permutation[ii + permutation[jj]] % 12;
            int g1 = permutation[ii + i1 + permutation[jj + j1]] % 12;
            int g2 = permutation[ii + 1 + permutation[jj + 1]] % 12;

            return 70.0D * (corner(x0, z0, g0)
                    + corner(x1, z1, g1)
                    + corner(x2, z2, g2));
        }
    }
}
