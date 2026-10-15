# 17. Colors, patterns and seven shading types

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/colours-patterns.php)
presents color spaces, repeating patterns and all seven ISO shading types on two pages.

```sh
php examples/colours-patterns.php colours-patterns.pdf
```

The color space defines component meaning. `CalGray`, `CalRGB` and `Lab` take
calibrated parameters; `ICCBased` receives an explicit profile and its component
count. `Indexed` has a palette. `Separation` and `DeviceN` associate colorants
with a transformation into an alternate space. The core neither generates nor
analyzes external ICC profiles.

`TilingPattern` defines a cell, its `BBox`, repetition steps and resources.
A colored pattern paints its own colors. An uncolored pattern is a stencil
whose color is selected at use time. Validation follows dependencies to reject
incompatible color operations.

Shadings 1, 2 and 3 use a function, an axis or two circles. Types 4 and 5 describe
triangles; 6 and 7 describe Coons or tensor-product patches. Binary mesh formats
set quantized coordinates and components, most-significant bits first, continuation
flags and explicit `/Decode`. These objects actually produce mesh bytes.

`ShadingPattern` turns a shading into a pattern resource. Matrices place samples
on the page while preserving resource identity. Changing points, colors or format
bit counts changes the result and its precision.

CI verifies all seven dictionaries, streams and patch-continuation vectors.
The test profile has its own provenance in the fixtures.

Reference: ISO 8.6–8.7, physical pages 146–215.

[Index](README.md) · [Complete code](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/colours-patterns.php)
