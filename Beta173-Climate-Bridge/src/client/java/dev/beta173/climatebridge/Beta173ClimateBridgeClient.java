package dev.beta173.climatebridge;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;

/** Client receivers for a cooperating remote server. */
public final class Beta173ClimateBridgeClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        ClientPlayConnectionEvents.JOIN.register((handler, sender, client) ->
            ClimateSeedStore.clearRemoteSeed()
        );
        ClientPlayConnectionEvents.DISCONNECT.register((handler, client) ->
            ClimateSeedStore.clearRemoteSeed()
        );
        ClientPlayNetworking.registerGlobalReceiver(WorldSeedPayload.TYPE, (payload, context) ->
            ClimateSeedStore.setRemoteSeed(payload.seed())
        );
    }
}
