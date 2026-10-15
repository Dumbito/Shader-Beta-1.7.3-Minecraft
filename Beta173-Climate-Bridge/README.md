# Beta173 Climate Bridge v0.1.0

**Fabric client/server companion for Beta173 Lighting.** This mod restores the seed-based, position-dependent climate value used by Minecraft Beta 1.7.3 and supplies it through Iris' existing temperature uniform. It adds no items, blocks, GUI or visual assets.

## Compatibility

- Minecraft Java Edition **26.3**
- Fabric Loader **0.19.5+**
- Fabric API **0.162.0+26.3**
- Iris **1.11.6+ for Minecraft 26.3**
- Java **25+**

The mixin targets Iris 1.11.6's BiomeUniforms implementation. Other Iris versions may change the injection point; do not assume compatibility without a build/runtime test.

## What it ports

1. WorldChunkManager creates NoiseGeneratorOctaves2 from new Random(worldSeed * 9871L) with four octaves.
2. Each NoiseGenerator2 preserves Java Random's permutation, simplex skew/unskew, gradient table and attenuation formula.
3. The four octave samples use the original 0.02500000037252903D / 1.5D scale, frequency and amplitude progression.
4. The resulting temperature is sampled at the camera entity's floored block X/Z. Iris' uniform name remains temperature, so a shaderpack that already reads Iris' temperature does not need mod-specific GLSL or a hand-edited line.
5. In single-player, the integrated server sends the world seed automatically. On dedicated multiplayer servers the seed is opt-in via config/beta173-climate-bridge.properties; without a compatible seed packet, the original Iris biome-base-temperature supplier remains as a fallback.

This is a source-level port of Beta's climate noise, not proof of pixel-perfect output: modern Iris/Minecraft still use a different rendering pipeline, and the shaderpack has to consume the Iris temperature uniform for this bridge to affect the sky.

## Install

1. Install the matching Fabric Loader, Fabric API and Iris versions above.
2. Put Beta173-Climate-Bridge-0.1.0-mc26.3.jar in the Minecraft instance's mods/ folder.
3. Use a Beta173 Lighting shader build whose sky function reads uniform float temperature; rather than a fixed BETA_SKY_TEMPERATURE constant.
4. Restart Minecraft and enter the world. In single-player/LAN, the integrated server supplies the seed automatically. For a dedicated multiplayer server, install the mod on both client and server and set shareWorldSeed=true in the server's config/beta173-climate-bridge.properties only if the administrator agrees to share the seed. The setting defaults to false. On a server without the mod, or without this opt-in, the bridge safely falls back to Iris' normal temperature.

The source ZIP is not an installable mod JAR. The root README contains links to the compiled JAR and source ZIP after a successful GitHub Actions build.

## Build from source

Requires JDK 25 and network access to the Fabric and Modrinth Maven repositories:

    gradle test build

The JAR is written to build/libs/.

## Limitations / verification

- Dedicated servers do not disclose the seed by default. Enable shareWorldSeed=true only on servers where the administrator has chosen to share it. Without the setting, the Iris fallback is used.
- Iris internals are not a public custom-uniform registration API. The mod intentionally pins to Iris 1.11.6 for 26.3 and may require updates if BiomeUniforms.addBiomeUniforms changes.
- Automated tests check the noise port's determinism and numeric safety. They do not replace in-game comparisons of the sky across coordinates and seeds.
