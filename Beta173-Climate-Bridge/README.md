# Beta173 Climate Bridge — experimental

Optional Fabric mod for Minecraft 26.3 + Fabric API. On clients with Iris 1.11.6+, it adds three uniforms used by Beta173 Lighting:

- `beta173LegacyClimateAvailable`
- `beta173LegacyClimateTemperature`
- `beta173LegacySkyRgb`

## Modes

- **Singleplayer / integrated server:** the client can access its own server's raw world seed and compute Beta 1.7.3's four-octave Simplex climate field automatically.
- **Multiplayer with this mod on both client and server:** the server can optionally send its raw world seed. The server operator must explicitly set `shareWorldSeed=true` in `config/beta173-climate-bridge.properties`. It defaults to `false`, because disclosing a seed can reveal world-generation information.
- **Multiplayer without server cooperation:** vanilla sends an obfuscated seed to the client; exact historical noise cannot be reconstructed from that value. The universal shaderpack falls back automatically to Iris's current biome `temperature`.

## Build

With Java 25 and Gradle 9.5:

```bash
gradle -p Beta173-Climate-Bridge build
```

Install the resulting `beta173-climate-bridge-0.1.0.jar` in the `mods` folder. For exact remote multiplayer climate, the server must also install the same jar and enable seed sharing in its config. The shaderpack itself remains an ordinary ZIP in `shaderpacks`.

The source/build candidate is experimental until the automated build and in-game tests pass.
