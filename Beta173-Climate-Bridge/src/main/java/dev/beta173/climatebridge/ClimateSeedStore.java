package dev.beta173.climatebridge;

/** Holds a server-provided seed only for the active remote connection. */
public final class ClimateSeedStore {
    private static volatile Long remoteSeed;

    private ClimateSeedStore() {
    }

    public static Long remoteSeed() {
        return remoteSeed;
    }

    public static void setRemoteSeed(long seed) {
        remoteSeed = seed;
    }

    public static void clearRemoteSeed() {
        remoteSeed = null;
    }
}
