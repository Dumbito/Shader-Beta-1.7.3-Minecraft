package com.dumbito.beta173climate.network;

import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.Identifier;

public record ClimateSeedPayload(long seed) implements CustomPacketPayload {
    public static final Type<ClimateSeedPayload> TYPE = new Type<>(
            Identifier.fromNamespaceAndPath("beta173_climate_bridge", "world_seed"));
    public static final StreamCodec<RegistryFriendlyByteBuf, ClimateSeedPayload> CODEC =
            StreamCodec.composite(ByteBufCodecs.VAR_LONG, ClimateSeedPayload::seed, ClimateSeedPayload::new);

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }
}
