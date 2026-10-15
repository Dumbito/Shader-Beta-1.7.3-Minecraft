package dev.beta173.climatebridge;

import net.fabricmc.loader.api.FabricLoader;

import java.io.IOException;
import java.io.Reader;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Properties;

/** Server-side opt-in. A seed is never sent to remote clients by default. */
public final class SeedShareConfig {
    private static final String FILE_NAME = "beta173-climate-bridge.properties";
    private static volatile Boolean cached;

    private SeedShareConfig() {
    }

    public static boolean shareWorldSeed() {
        Boolean value = cached;
        if (value != null) return value;

        synchronized (SeedShareConfig.class) {
            value = cached;
            if (value != null) return value;

            Path config = FabricLoader.getInstance().getConfigDir().resolve(FILE_NAME);
            createDefaultIfMissing(config);
            Properties properties = new Properties();
            try (Reader reader = Files.newBufferedReader(config, StandardCharsets.UTF_8)) {
                properties.load(reader);
                value = Boolean.parseBoolean(properties.getProperty("shareWorldSeed", "false"));
            } catch (IOException exception) {
                System.err.println("[Beta173 Climate Bridge] Could not read " + config + ": " + exception);
                value = false;
            }
            cached = value;
            return value;
        }
    }

    private static void createDefaultIfMissing(Path config) {
        if (Files.exists(config)) return;
        try {
            Files.createDirectories(config.getParent());
            String template = "# Beta173 Climate Bridge server configuration\n"
                + "# Set true only if you want clients with the bridge to receive the raw world seed.\n"
                + "# Default false protects servers that prefer not to disclose world-generation data.\n"
                + "shareWorldSeed=false\n";
            Files.writeString(config, template, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
        } catch (java.nio.file.FileAlreadyExistsException ignored) {
            // Another thread or process created the file first.
        } catch (IOException exception) {
            System.err.println("[Beta173 Climate Bridge] Could not create " + config + ": " + exception);
        }
    }
}
