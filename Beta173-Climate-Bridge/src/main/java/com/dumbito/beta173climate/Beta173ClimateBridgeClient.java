package com.dumbito.beta173climate;

import com.dumbito.beta173climate.climate.ClimateTemperature;
import com.dumbito.beta173climate.network.ClimateSeedPayload;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents;

public final class Beta173ClimateBridgeClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        ClientPlayNetworking.registerGlobalReceiver(ClimateSeedPayload.TYPE, (payload, context) ->
                ClimateTemperature.setWorldSeed(payload.seed()));
        ClientPlayConnectionEvents.DISCONNECT.register((handler, client) ->
                ClimateTemperature.clearWorldSeed());
    }
}
