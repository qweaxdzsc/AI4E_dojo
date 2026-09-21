# PCNO-derived numerical components

Source: Code Ocean capsule 8000337 v1.0, commit dc4cd4417ed7f97715ffb47496690ce60f7665a3.
https://codeocean.com/capsule/8000337/tree/v1

These components retain the upstream GPL-3.0 license, reproduced in `abilities/PCNO_LICENSE`:
fourier4d, unet_volume, global_features, fourier_unet4d, spatiotemporal_field,
geothermal physics, wellbore, and geothermal_economics.

Changes: modular imports and documentation; PDE_F.vis masks only inactive branch inputs
before evaluating the original expressions, preventing invalid gradients in the unused
fractional-power branch. Active formulas and source units remain unchanged.
The contrib PCNO source.json records original file digests and definition mapping.
