# Beta173 Climate Bridge — experimental

Optional Fabric client mod for Minecraft 26.3 + Iris 1.11.6+. It adds three Iris uniforms that allow Beta173 Lighting to use the original Beta 1.7.3 climate-temperature algorithm automatically in a local single-player world:

- `beta173LegacyClimateAvailable`
- `beta173LegacyClimateTemperature`
- `beta173LegacySkyRgb`

The bridge obtains the raw seed from the integrated server, calculates the four-octave Simplex field at the player's integer X/Z coordinates, and applies the original Java HSB-to-8-bit-RGB conversion. The computation is cached until the seed or block coordinates change.

## Important multiplayer limitation

Vanilla Minecraft 26.3 obfuscates the seed sent to a remote client. A client-only mod cannot invert that hash to recover the raw world seed. Therefore, without a server-side plugin/mod that cooperates, the bridge deliberately reports the raw seed unavailable in multiplayer. The universal shaderpack then falls back to Iris's current biome `temperature` uniform; it still works automatically, but this fallback is not the exact historical noise field.

## Build

From this directory, with Java 25 and Gradle 9.5:

```bash
gradle build
```

Copy `build/libs/beta173-climate-bridge-0.1.0.jar` into the Minecraft instance's `mods` directory. The shaderpack remains a regular ZIP in `shaderpacks`.

This is source/CI candidate only until the build and in-game checks pass. No precompiled JAR is claimed stable.
