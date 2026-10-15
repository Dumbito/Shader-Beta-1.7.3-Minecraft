package com.dumbito.beta173climate;

import net.fabricmc.loader.api.FabricLoader;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Properties;

/** Server-side privacy setting for sharing a world seed with compatible clients. */
public final class WorldSeedSharingConfig {
    private static final Logger LOGGER = LoggerFactory.getLogger(Beta173ClimateBridge.MOD_ID);
    private static final Path FILE = FabricLoader.getInstance().getConfigDir()
            .resolve("beta173-climate-bridge.properties");

    private WorldSeedSharingConfig() { }

    /** Defaults to false: a dedicated server must opt in before sending its seed. */
    public static boolean isSeedSharingEnabled() {
        Properties properties = new Properties();
        try {
            if (Files.exists(FILE)) {
                try (InputStream in = Files.newInputStream(FILE)) {
                    properties.load(in);
                }
            } else {
                Files.createDirectories(FILE.getParent());
                try (OutputStream out = Files.newOutputStream(FILE)) {
                    properties.store(out, "Set shareWorldSeed=true only if you want compatible clients to receive the world seed. Defaults to false.");
                }
            }
            return Boolean.parseBoolean(properties.getProperty("shareWorldSeed", "false").trim());
        } catch (IOException e) {
            LOGGER.warn("Could not read {}. World-seed sharing stays disabled for privacy.", FILE, e);
            return false;
        }
    }
}
