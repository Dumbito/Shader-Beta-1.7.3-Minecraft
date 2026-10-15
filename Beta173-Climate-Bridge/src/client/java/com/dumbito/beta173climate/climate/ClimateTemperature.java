package com.dumbito.beta173climate.climate;

import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.irisshaders.iris.gl.uniform.FloatSupplier;

/**
 * Provides the positional, world-seed-based climate value used by Beta 1.7.3 World.getSkyColor.
 * The modern Iris temperature uniform is kept intact as a fallback when the remote server does not
 * run this mod (and consequently has not sent the world's seed).
 */
public final class ClimateTemperature {
    private static final Object LOCK = new Object();
    private static long activeSeed;
    private static boolean seedAvailable;
    private static LegacyClimateNoise sampler;
    private static int lastX = Integer.MIN_VALUE;
    private static int lastZ = Integer.MIN_VALUE;
    private static long lastSampleSeed;
    private static float lastTemperature;

    private ClimateTemperature() { }

    public static void setWorldSeed(long seed) {
        synchronized (LOCK) {
            if (!seedAvailable || activeSeed != seed) {
                activeSeed = seed;
                sampler = new LegacyClimateNoise(seed);
                lastX = Integer.MIN_VALUE;
                lastZ = Integer.MIN_VALUE;
                lastSampleSeed = seed;
            }
            seedAvailable = true;
        }
    }

    public static void clearWorldSeed() {
        synchronized (LOCK) {
            seedAvailable = false;
            sampler = null;
            lastX = Integer.MIN_VALUE;
            lastZ = Integer.MIN_VALUE;
        }
    }

    public static float sampleOr(FloatSupplier vanillaFallback) {
        Minecraft client = Minecraft.getInstance();
        Entity camera = client.getCameraEntity();
        Level level = client.level;
        if (camera == null || level == null) {
            return vanillaFallback.getAsFloat();
        }

        synchronized (LOCK) {
            if (!seedAvailable || sampler == null) {
                return vanillaFallback.getAsFloat();
            }
            BlockPos position = camera.blockPosition();
            int x = position.getX();
            int z = position.getZ();
            if (x != lastX || z != lastZ || lastSampleSeed != activeSeed) {
                lastTemperature = (float) sampler.temperatureAt(x, z);
                lastX = x;
                lastZ = z;
                lastSampleSeed = activeSeed;
            }
            return lastTemperature;
        }
    }
}
