package dev.beta173.climatebridge;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;

/** Common initialization: a cooperative server can offer the original world seed. */
public final class Beta173ClimateBridge implements ModInitializer {
    @Override
    public void onInitialize() {
        PayloadTypeRegistry.playS2C().register(WorldSeedPayload.TYPE, WorldSeedPayload.STREAM_CODEC);

        ServerPlayConnectionEvents.JOIN.register((handler, sender, server) -> {
            if (!SeedShareConfig.shareWorldSeed()) return;
            var overworld = server.overworld();
            if (overworld != null) {
                ServerPlayNetworking.send(handler.player, new WorldSeedPayload(overworld.getSeed()));
            }
        });
    }
}
