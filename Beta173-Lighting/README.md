# Beta173 Lighting

Experimental Iris shaderpack inspired by Minecraft Beta 1.7.3.

Version 0.2:
- Added gbuffers_textured_lit: entities, held items, dropped items and block entities now use the same Beta 1.7.3 lighting as terrain (Iris falls back to this program).
- Added gbuffers_armor_glint: enchantment glint is drawn unlit and without alpha discard.

Version 0.1:
- Historical brightness table.
- Historical celestial-angle interpolation.
- Approximate sky attenuation by time and rain.
- Maximum of attenuated sky light and block light.

Limitations:
- A shaderpack cannot replace Minecraft CPU-side light propagation.
- Modern lightmap coordinates may not map exactly to Beta 1.7.3 levels.
- Thunder attenuation, particles and historical sky colors are not implemented.
- In-game testing is required.
