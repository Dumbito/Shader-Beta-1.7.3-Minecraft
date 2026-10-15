package dev.beta173.climatebridge.mixin;

import dev.beta173.climatebridge.LegacyClimateNoise;
import net.irisshaders.iris.gl.uniform.UniformHolder;
import net.irisshaders.iris.gl.uniform.UniformUpdateFrequency;
import net.irisshaders.iris.uniforms.FrameUpdateNotifier;
import net.irisshaders.iris.uniforms.IrisExclusiveUniforms;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.player.Player;
import org.joml.Vector3f;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Adds optional Iris uniforms. With a local integrated world, the raw world seed is
 * available and we can reproduce Beta 1.7.3's climate field. In remote multiplayer,
 * vanilla sends only an obfuscated seed, so this bridge intentionally reports unavailable.
 */
@Mixin(IrisExclusiveUniforms.class)
public abstract class ClimateUniformMixin {
    private static volatile Sample cached;

    @Inject(at = @At("HEAD"), method = "addIrisExclusiveUniforms")
    private static void beta173$registerClimateUniforms(
        UniformHolder uniforms,
        FrameUpdateNotifier updateNotifier,
        CallbackInfo ci
    ) {
        uniforms.uniform1b(
            UniformUpdateFrequency.PER_TICK,
            "beta173LegacyClimateAvailable",
            () -> currentSample() != null
        );
        uniforms.uniform1f(
            UniformUpdateFrequency.PER_TICK,
            "beta173LegacyClimateTemperature",
            () -> {
                Sample sample = currentSample();
                return sample == null ? 0.0F : sample.temperature();
            }
        );
        uniforms.uniform3f(
            UniformUpdateFrequency.PER_TICK,
            "beta173LegacySkyRgb",
            () -> {
                Sample sample = currentSample();
                if (sample == null) return new Vector3f(0.0F);
                int rgb = sample.rgb();
                return new Vector3f(
                    ((rgb >> 16) & 255) / 255.0F,
                    ((rgb >> 8) & 255) / 255.0F,
                    (rgb & 255) / 255.0F
                );
            }
        );
    }

    private static Sample currentSample() {
        Minecraft minecraft = Minecraft.getInstance();
        Player player = minecraft.player;
        var server = minecraft.getSingleplayerServer();
        if (player == null || server == null || minecraft.level == null) return null;

        var overworld = server.overworld();
        if (overworld == null) return null;
        long seed = overworld.getSeed();
        BlockPos blockPosition = player.blockPosition();
        int x = blockPosition.getX();
        int z = blockPosition.getZ();

        Sample previous = cached;
        if (previous != null && previous.seed() == seed && previous.x() == x && previous.z() == z) {
            return previous;
        }

        synchronized (ClimateUniformMixin.class) {
            previous = cached;
            if (previous != null && previous.seed() == seed && previous.x() == x && previous.z() == z) {
                return previous;
            }
            float temperature = LegacyClimateNoise.sample(seed, x, z);
            Sample next = new Sample(seed, x, z, temperature, LegacyClimateNoise.skyRgb(temperature));
            cached = next;
            return next;
        }
    }

    private record Sample(long seed, int x, int z, float temperature, int rgb) {
    }
}
