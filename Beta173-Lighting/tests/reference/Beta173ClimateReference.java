import java.awt.Color;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.Locale;
import java.util.Random;

/**
 * Ejecuta la referencia matemática del código de Minecraft Beta 1.7.3.
 * Port de WorldChunkManager, NoiseGeneratorOctaves2, NoiseGenerator2, World,
 * WorldProvider y BiomeGenBase desde jacobo-mc/mc_b1.7.3_release.
 * Protocolo stdin/stdout tabulado para comparar miles de casos desde Python.
 */
public final class Beta173ClimateReference {
    private static final double F2 = 0.5D * (Math.sqrt(3.0D) - 1.0D);
    private static final double G2 = (3.0D - Math.sqrt(3.0D)) / 6.0D;
    private static final int[][] GRADIENTS = {
        {1,1,0},{-1,1,0},{1,-1,0},{-1,-1,0},
        {1,0,1},{-1,0,1},{1,0,-1},{-1,0,-1},
        {0,1,1},{0,-1,1},{0,1,-1},{0,-1,-1}
    };
    private static final float PI = 3.1415927F;
    private static final float[] SIN_TABLE = new float[65536];
    static {
        for (int i = 0; i < SIN_TABLE.length; ++i) {
            SIN_TABLE[i] = (float)Math.sin((double)i * Math.PI * 2.0D / 65536.0D);
        }
    }

    private static float mathCos(float value) {
        return SIN_TABLE[(int)(value * 10430.378F + 16384.0F) & 65535];
    }

    private static final class NoiseGenerator2 {
        private final int[] permutation = new int[512];
        private final double offsetX, offsetZ;
        NoiseGenerator2(Random random) {
            offsetX = random.nextDouble() * 256.0D;
            offsetZ = random.nextDouble() * 256.0D;
            random.nextDouble(); // tercer offset de NoiseGenerator2, aunque no intervenga en el plano X/Z
            for (int i = 0; i < 256; ++i) permutation[i] = i;
            for (int i = 0; i < 256; ++i) {
                int j = random.nextInt(256 - i) + i;
                int old = permutation[i];
                permutation[i] = permutation[j];
                permutation[j] = old;
                permutation[i + 256] = permutation[i];
            }
        }
        private static int wrap(double value) { return value > 0.0D ? (int)value : (int)value - 1; }
        private static double dot(int[] gradient, double x, double z) {
            return (double)gradient[0] * x + (double)gradient[1] * z;
        }
        void add(double[] output, double x, double z, double scaleX, double scaleZ, double amplitude) {
            double px = x * scaleX + offsetX;
            double pz = z * scaleZ + offsetZ;
            double skew = (px + pz) * F2;
            int i = wrap(px + skew), j = wrap(pz + skew);
            double unskew = (double)(i + j) * G2;
            double x0 = px - ((double)i - unskew), z0 = pz - ((double)j - unskew);
            int i1, j1;
            if (x0 > z0) { i1 = 1; j1 = 0; } else { i1 = 0; j1 = 1; }
            double x1 = x0 - (double)i1 + G2, z1 = z0 - (double)j1 + G2;
            double x2 = x0 - 1.0D + 2.0D * G2, z2 = z0 - 1.0D + 2.0D * G2;
            int ii = i & 255, jj = j & 255;
            int g0 = permutation[ii + permutation[jj]] % 12;
            int g1 = permutation[ii + i1 + permutation[jj + j1]] % 12;
            int g2 = permutation[ii + 1 + permutation[jj + 1]] % 12;
            double a0 = 0.5D - x0*x0 - z0*z0, n0;
            if (a0 < 0.0D) n0 = 0.0D;
            else { a0 *= a0; n0 = a0*a0*dot(GRADIENTS[g0], x0, z0); }
            double a1 = 0.5D - x1*x1 - z1*z1, n1;
            if (a1 < 0.0D) n1 = 0.0D;
            else { a1 *= a1; n1 = a1*a1*dot(GRADIENTS[g1], x1, z1); }
            double a2 = 0.5D - x2*x2 - z2*z2, n2;
            if (a2 < 0.0D) n2 = 0.0D;
            else { a2 *= a2; n2 = a2*a2*dot(GRADIENTS[g2], x2, z2); }
            output[0] += 70.0D * (n0 + n1 + n2) * amplitude;
        }
    }

    private static double climateTemperature(long worldSeed, int blockX, int blockZ) {
        Random random = new Random(worldSeed * 9871L);
        NoiseGenerator2[] octaves = new NoiseGenerator2[4];
        for (int i = 0; i < octaves.length; ++i) octaves[i] = new NoiseGenerator2(random);
        double[] out = {0.0D};
        double frequency = 1.0D, amplitude = 1.0D;
        for (NoiseGenerator2 octave : octaves) {
            octave.add(out, (double)blockX, (double)blockZ,
                (0.02500000037252903D / 1.5D) * frequency,
                (0.02500000037252903D / 1.5D) * frequency,
                0.55D / amplitude);
            frequency *= 0.5D;
            amplitude *= 0.5D;
        }
        return out[0];
    }

    private static int skyBaseRgb(double climateTemperature) {
        float t = (float)climateTemperature;
        t /= 3.0F;
        if (t < -1.0F) t = -1.0F;
        if (t > 1.0F) t = 1.0F;
        return Color.getHSBColor(0.62222224F - t * 0.05F, 0.5F + t * 0.1F, 1.0F).getRGB();
    }

    private static float celestialAngle(long worldTime, float partialTicks) {
        float angle = ((float)(worldTime % 24000L) + partialTicks) / 24000.0F - 0.25F;
        if (angle < 0.0F) angle += 1.0F;
        if (angle > 1.0F) angle -= 1.0F;
        float original = angle;
        angle = 1.0F - (mathCos(angle * PI) + 1.0F) / 2.0F;
        return original + (angle - original) / 3.0F;
    }

    private static float dayFactor(long time, float partial) {
        float value = mathCos(celestialAngle(time, partial) * PI * 2.0F) * 2.0F + 0.5F;
        if (value < 0.0F) value = 0.0F;
        if (value > 1.0F) value = 1.0F;
        return value;
    }

    private static int skySubtracted(long time, float partial, float rain, float thunder) {
        float angle = celestialAngle(time, partial);
        float value = 1.0F - (mathCos(angle * PI * 2.0F) * 2.0F + 0.5F);
        if (value < 0.0F) value = 0.0F;
        if (value > 1.0F) value = 1.0F;
        value = 1.0F - value;
        value = (float)((double)value * (1.0D - (double)(rain * 5.0F) / 16.0D));
        value = (float)((double)value * (1.0D - (double)(thunder * 5.0F) / 16.0D));
        return (int)((1.0F - value) * 11.0F);
    }

    private static float starBrightness(long time, float partial) {
        float value = 1.0F - (mathCos(celestialAngle(time, partial) * PI * 2.0F) * 2.0F + 0.75F);
        if (value < 0.0F) value = 0.0F;
        if (value > 1.0F) value = 1.0F;
        return value * value * 0.5F;
    }

    private static float brightness(int level, float ambient) {
        float inverted = 1.0F - (float)level / 15.0F;
        return (1.0F - inverted) / (inverted * 3.0F + 1.0F) * (1.0F - ambient) + ambient;
    }

    private static float[] skyColor(long seed, int x, int z, long time, float partial,
                                    float rain, float thunder) {
        double temperature = climateTemperature(seed, x, z);
        int rgb = skyBaseRgb(temperature);
        float r = (float)((rgb >> 16) & 255) / 255.0F;
        float g = (float)((rgb >> 8) & 255) / 255.0F;
        float b = (float)(rgb & 255) / 255.0F;
        float day = dayFactor(time, partial);
        r *= day; g *= day; b *= day;
        if (rain > 0.0F) {
            float gray = (r * 0.3F + g * 0.59F + b * 0.11F) * 0.6F;
            float k = 1.0F - rain * 0.75F;
            r = r*k + gray*(1.0F-k); g = g*k + gray*(1.0F-k); b = b*k + gray*(1.0F-k);
        }
        if (thunder > 0.0F) {
            float gray = (r * 0.3F + g * 0.59F + b * 0.11F) * 0.2F;
            float k = 1.0F - thunder * 0.75F;
            r = r*k + gray*(1.0F-k); g = g*k + gray*(1.0F-k); b = b*k + gray*(1.0F-k);
        }
        return new float[] { r, g, b, day, celestialAngle(time, partial), (float)temperature };
    }

    private static String f(float v) { return String.format(Locale.ROOT, "%.9g", v); }
    private static String d(double v) { return String.format(Locale.ROOT, "%.17g", v); }

    public static void main(String[] args) throws Exception {
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(System.in))) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.isBlank()) continue;
                String[] p = line.trim().split("\\s+");
                switch (p[0]) {
                    case "C": {
                        long seed = Long.parseLong(p[1]);
                        int x = Integer.parseInt(p[2]), z = Integer.parseInt(p[3]);
                        System.out.println("C\t" + seed + "\t" + x + "\t" + z + "\t" + d(climateTemperature(seed,x,z)));
                        break;
                    }
                    case "K": {
                        int rgb = skyBaseRgb(Double.parseDouble(p[1]));
                        System.out.println("K\t" + p[1] + "\t" + ((rgb>>16)&255) + "\t" + ((rgb>>8)&255) + "\t" + (rgb&255));
                        break;
                    }
                    case "S": {
                        long seed=Long.parseLong(p[1]); int x=Integer.parseInt(p[2]), z=Integer.parseInt(p[3]);
                        long time=Long.parseLong(p[4]); float partial=Float.parseFloat(p[5]), rain=Float.parseFloat(p[6]), thunder=Float.parseFloat(p[7]);
                        float[] v=skyColor(seed,x,z,time,partial,rain,thunder);
                        int sub=skySubtracted(time,partial,rain,thunder); float stars=starBrightness(time,partial);
                        System.out.println("S\t"+seed+"\t"+x+"\t"+z+"\t"+time+"\t"+f(partial)+"\t"+f(rain)+"\t"+f(thunder)+"\t"+
                            d(climateTemperature(seed,x,z))+"\t"+f(v[0])+"\t"+f(v[1])+"\t"+f(v[2])+"\t"+f(v[3])+"\t"+f(v[4])+"\t"+
                            sub+"\t"+f(stars)+"\t"+((int)(v[0]*255))+"\t"+((int)(v[1]*255))+"\t"+((int)(v[2]*255)));
                        break;
                    }
                    case "F": {
                        long time=Long.parseLong(p[1]); float partial=Float.parseFloat(p[2]), rain=Float.parseFloat(p[3]), thunder=Float.parseFloat(p[4]);
                        System.out.println("F\t"+time+"\t"+f(partial)+"\t"+f(rain)+"\t"+f(thunder)+"\t"+
                            f(celestialAngle(time,partial))+"\t"+f(dayFactor(time,partial))+"\t"+
                            skySubtracted(time,partial,rain,thunder)+"\t"+f(starBrightness(time,partial)));
                        break;
                    }
                    case "B": {
                        int level=Integer.parseInt(p[1]); float ambient=Float.parseFloat(p[2]);
                        System.out.println("B\t"+level+"\t"+f(ambient)+"\t"+f(brightness(level,ambient)));
                        break;
                    }
                    default: throw new IllegalArgumentException("Comando desconocido: " + p[0]);
                }
            }
        }
    }
}
