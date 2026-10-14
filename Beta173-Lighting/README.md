# Beta173 Lighting

Experimental Iris shaderpack that ports the lighting, sky and fog of Minecraft Beta 1.7.3 to modern Minecraft (tested target: 26.3).

## Reference

The formulas come from the reconstructed Beta 1.7.3 source, used for reference only:
https://github.com/jacobo-mc/mc_b1.7.3_release

Ported (not copied) from `WorldProvider`, `WorldProviderHell`, `World`, `EntityRenderer` and `RenderGlobal`.

## Version 0.3
- Thunder attenuation of sky light (`World.calculateSkylightSubtracted`).
- Minimum brightness 0.1 in dimensions without sky light (`WorldProviderHell`), 0.05 in the Overworld.
- Continuous light level instead of per-fragment rounding, so Smooth Lighting no longer shows steps.
- Beta fog: linear (starts at 25% of the distance) in air, exponential in water and lava, with Beta fog colors by time of day, rain and thunder.
- Beta sky: flat sky color that blends into the fog color toward the horizon, dark disc below it, star brightness. Sunrise/sunset fan, sun, moon and clouds stay as the game draws them.

## Version 0.2
- Added gbuffers_textured_lit: entities, held items, dropped items and block entities use the same Beta 1.7.3 lighting as terrain (Iris falls back to this program).
- Added gbuffers_armor_glint: enchantment glint is drawn unlit and without alpha discard.

## Version 0.1
- Historical brightness table.
- Historical celestial-angle interpolation.
- Approximate sky attenuation by time and rain.
- Maximum of attenuated sky light and block light.

## Options

Edit `shaders/lib/config.glsl`. Each feature can be turned off by commenting its `#define` line:
`BETA_THUNDER`, `BETA_NETHER_AMBIENT`, `BETA_SMOOTH`, `BETA_FOG`.
`BETA_FOG_END` sets the fog distance in blocks (keep it at or below your render distance).
To go back to the vanilla sky, delete `gbuffers_skybasic.vsh` and `gbuffers_skybasic.fsh`.

## Limitations
- A shaderpack cannot replace Minecraft CPU-side light propagation.
- Modern lightmap coordinates may not map exactly to Beta 1.7.3 levels.
- Not implemented: Nether/End fog, lightning flash, biome-dependent sky tint (a fixed temperature is used), cloud height and color, moon phases, particles beyond the shared lit program.
- In-game testing is required.
