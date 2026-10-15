package com.dumbito.beta173climate.mixin;

import com.dumbito.beta173climate.climate.ClimateTemperature;
import net.irisshaders.iris.gl.uniform.FloatSupplier;
import net.irisshaders.iris.gl.uniform.UniformHolder;
import net.irisshaders.iris.gl.uniform.UniformUpdateFrequency;
import net.irisshaders.iris.uniforms.BiomeUniforms;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Replaces Iris' temperature supplier but leaves its temperature uniform name unchanged. */
@Mixin(value = BiomeUniforms.class, remap = false)
public abstract class BiomeUniformsMixin {
    @Redirect(
            method = "addBiomeUniforms",
            at = @At(
                    value = "INVOKE",
                    target = "Lnet/irisshaders/iris/gl/uniform/UniformHolder;uniform1f(Lnet/irisshaders/iris/gl/uniform/UniformUpdateFrequency;Ljava/lang/String;Lnet/irisshaders/iris/gl/uniform/FloatSupplier;)Lnet/irisshaders/iris/gl/uniform/UniformHolder;"
            ),
            remap = false
    )
    private static UniformHolder beta173$overrideTemperature(
            UniformHolder holder,
            UniformUpdateFrequency frequency,
            String name,
            FloatSupplier original
    ) {
        FloatSupplier supplier = "temperature".equals(name)
                ? () -> ClimateTemperature.sampleOr(original)
                : original;
        return holder.uniform1f(frequency, name, supplier);
    }
}
