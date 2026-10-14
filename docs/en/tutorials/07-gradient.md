# 07. An axial gradient and a PDF function

This example creates a rectangle transitioning from turquoise blue to orange. The PDF contains a **type 2 function**, a **type 2 axial shading** and a clipping path. The reader calculates gradient colors from these objects.

![Preview of the turquoise and orange axial gradient](../../tutorials/previews/gradient.png)

## Run the example

From the root of a core checkout, after `composer install`:

```sh
php examples/gradient.php gradient.pdf
```

The output path is optional; it defaults to `examples/gradient.pdf`. See the complete script [examples/gradient.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/gradient.php).

## 1. Define color as a function

`ExponentialInterpolationFunction` represents the type 2 PDF function. It receives a number `t` and returns three numbers here, the RGB components of a color:

```text
C(t) = C0 + t^N × (C1 − C0)
```

`Domain` contains the input interval `[0, 1]`. `C0 = [0.10, 0.65, 0.85]` gives turquoise at the start; `C1 = [1.00, 0.72, 0.20]` gives orange at the end. Exponent `N` is `1`, producing linear interpolation. At `t = 0.5`, the color is the average of the two colors.

`Range` contains three intervals `[0, 1]`, one for each output component. The same immutable `NumberInterval` object is reused for these intervals. `NumberArray` gathers components while retaining each as a numeric object.

The **function** type describes the calculation. The **shading** type, also numbered `2` here, describes how to distribute that calculation's parameters across page space.

## 2. Build the axial shading

`Type2ShadingDictionaryTable80` receives the common entries from Table 78 and axial-shading entries from Table 80:

| Entry | Example value | Role |
| --- | --- | --- |
| `/ShadingType` | `2` | Select axial shading. |
| `/ColorSpace` | `/DeviceRGB` | The function's three outputs are RGB components. |
| `/Coords` | `[64 500 548 500]` | Connect start point `(64, 500)` to end point `(548, 500)`. |
| `/Domain` | `[0 1]` | Associate those points with `t=0` and `t=1`. |
| `/Function` | Indirect reference to `$function` | Calculate color for each parameter. |
| `/Extend` | `[false false]` | Request no color extension beyond the axis endpoints. |

The axis is horizontal. Parameter `t` varies along it; color remains constant perpendicular to it. `/Coords` therefore does not define a rectangle by itself.

`ShadingTypeEntry` and `ColorSpaceEntry` carry Table 78 provenance. `CoordsEntry`, `DomainEntry`, `FunctionEntry` and `ExtendEntry` come from Table 80. This composition expresses both parts of the dictionary described by the specification.

## 3. Name the resource

The page resources' `/Shading` dictionary associates `/Sh1` with an indirect reference to the shading dictionary. `PaintShading(new NameType('Sh1'))` produces `/Sh1 sh` and looks up this local resource.

The graph contains two distinct indirect objects: the shading and the function it references. The writer assigns their numbers while traversing the graph; the script never writes object numbers by hand.

## 4. Limit the painted area

The content stream encloses the gradient with these instructions:

```text
q
64 400 484 200 re
W
n
/Sh1 sh
Q
```

1. `q` saves the graphics state, including the current clipping path.
2. `re` creates a rectangle at `(64, 400)`, 484 points wide and 200 points high.
3. `W` requests that this path become a clipping path using the nonzero rule.
4. `n` ends the path without painting it and applies the requested clipping.
5. `sh` paints the shading in this area.
6. `Q` restores the previous graphics state.

Clipping gives the gradient its rectangular shape. Restoring the state lets explanations appear below, outside the rectangle: they would be hidden if clipping remained active.

## Try it

- Change `N` from `1` to `2`: the axis and endpoint colors stay the same, but orange appears more gradually.
- Position the `/Coords` endpoints vertically to change the direction of variation.
- Change the clipping rectangle while retaining `/Coords` to distinguish geometry from color parameterization.
- Shorten the axis and compare `/Extend [false false]` with `[true true]` inside the same rectangle.

## Things to know

The script handles an axial `/DeviceRGB` shading with a function having one input and three outputs. It does not cover radial shadings, meshes, transparency or ICC profiles.

Entry classes check the types described by their tables. The example's construction also respects semantic relationships: four coordinates, three function outputs for RGB, a compatible domain and two extension booleans. Generated classes alone do not guarantee all these relationships in an arbitrary assembly.

References in [ISO 32000-1:2008](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/PDF32000_2008.pdf): **7.10.3 and Table 40** (type 2 function), **8.4.2** (graphics state), **8.5.4** (clipping), **8.7.4.3 and Table 78** (shading and `sh`), **8.7.4.5.3 and Table 80** (axial shading).

[← 6. Images](06-images.md) · [All tutorials](README.md) · [8. Object streams →](08-object-stream.md)
