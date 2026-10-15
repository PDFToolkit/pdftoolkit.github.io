# 21. Explicit images, transparency and layers

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/native-graphics.php)
produces two pages with seven images, masks, a transparency group and layers.
The data are directly constructed PDF samples without external image files.

```sh
php examples/native-graphics.php native-graphics.pdf
```

`SampleLayout` specifies color space and depth. At depths of 1, 2 and 4 bits,
components are packed most-significant bit first; each row is rounded separately
to a byte. At 16 bits, each component occupies two bytes. `ImageSamples` checks
length against those dimensions.

`Decode` transforms sample values into components. An `ImageMask` stencil uses
one-bit depth and the current color. A color-key mask makes pixels with certain
values transparent; an explicit mask or `/SMask` supplies another image. `Matte`
describes a preblended color that must be accounted for to recover original colors.

A Form XObject has its own coordinates, `BBox`, matrix and resources. `Group`
declares a transparency group, its blending space and isolation options.
`GraphicsStateParameters` composes ExtGState parameters such as alpha, blend
mode and luminosity mask. Drawing then selects this resource with operator `gs`.

`OptionalContentGroup` gives a layer an identity. `OCProperties` lists the
document's groups and initial configuration. `OCMD` and visibility expressions
combine their states with And, Or and Not. The writer verifies actually reached
groups, including those in images and Forms.

Change samples, Decode, alpha or layer configuration to compare these mechanisms.
The reader decides their rendering; the core supplies their objects and tested
numeric operations. Illustrated halftone thresholds are PDF data without
conversion of an external image.

CI verifies images, threshold streams, resources and visibility expressions,
along with independent RGB and CMYK blending vectors.

Reference: ISO 8.8–8.11 and 11, physical pages 215–261 and 321–380.

[Index](README.md) · [Complete code](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/native-graphics.php)
