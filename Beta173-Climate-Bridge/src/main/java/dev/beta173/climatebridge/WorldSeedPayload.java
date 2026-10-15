package dev.beta173.climatebridge;

import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.Identifier;

/** Sends the raw seed only when the server operator has explicitly opted in. */
public record WorldSeedPayload(long seed) implements CustomPacketPayload {
    public static final Type<WorldSeedPayload> TYPE = new Type<>(
        Identifier.fromNamespaceAndPath("beta173_climate_bridge", "world_seed")
    );
    public static final StreamCodec<RegistryFriendlyByteBuf, WorldSeedPayload> STREAM_CODEC =
        StreamCodec.composite(ByteBufCodecs.VAR_LONG, WorldSeedPayload::seed, WorldSeedPayload::new);

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }
}
