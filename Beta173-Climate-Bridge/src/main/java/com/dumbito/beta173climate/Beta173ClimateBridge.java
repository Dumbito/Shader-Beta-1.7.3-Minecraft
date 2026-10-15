package com.dumbito.beta173climate;

import com.dumbito.beta173climate.network.ClimateSeedPayload;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.fabricmc.fabric.api.networking.v1.PacketSender;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.network.ServerGamePacketListenerImpl;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class Beta173ClimateBridge implements ModInitializer {
    public static final String MOD_ID = "beta173_climate_bridge";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    @Override
    public void onInitialize() {
        PayloadTypeRegistry.clientboundPlay().register(ClimateSeedPayload.TYPE, ClimateSeedPayload.CODEC);
        ServerPlayConnectionEvents.JOIN.register(Beta173ClimateBridge::sendWorldSeed);
        LOGGER.info("Beta 1.7.3 climate bridge initialized.");
    }

    private static void sendWorldSeed(ServerGamePacketListenerImpl listener, PacketSender sender, MinecraftServer server) {
        ServerPlayer player = listener.player;
        // The integrated single-player server belongs to the local player. Dedicated servers
        // must explicitly opt in through config/beta173-climate-bridge.properties.
        if (!server.isSingleplayer() && !WorldSeedSharingConfig.isSeedSharingEnabled()) {
            return;
        }
        if (player.level() instanceof ServerLevel level
                && ServerPlayNetworking.canSend(player, ClimateSeedPayload.TYPE)) {
            sender.sendPacket(new ClimateSeedPayload(level.getSeed()));
        }
    }
}
