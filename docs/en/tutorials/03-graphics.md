# 03. Paths, colors and transformations

[Tutorial index](README.md) · [Previous: pages and text](02-pages-and-text.md) · [Next: document outline](04-navigation.md)

This lesson draws rectangles, a Bézier curve and a dashed segment. It then applies a translation and rotation to the same local rectangle. The complete script is [graphics.php](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/graphics.php).

## Run the example

Use PHP 8.3 or later and the dependencies installed by `composer install`. Document assembly follows the [first tutorial](01-first-document.md). From the root of a core checkout:

```sh
php examples/graphics.php graphics.pdf
```

The first argument names the output. Without an argument, the file is `examples/graphics.pdf`. Its parent directory must already exist.

## What you get

An A4 page with two blue rectangles, one filled and one stroked; an orange curve and its dashed chord; and two light-blue rectangles at the bottom, one rotated by 30 degrees. Labels remain black and horizontal.

![Page from the vector graphics tutorial](../../tutorials/previews/graphics.png)

## 1. Construct a path, then paint it

A path begins with a current point or a rectangle. Construction operators add its geometry; a painting operator then determines its rendering and ends the path.

| Object | Operator | Function |
| --- | --- | --- |
| `AppendRectangle` | `re` | Add a rectangle with `x`, `y`, width and height. |
| `MoveTo` | `m` | Start a subpath at a point. |
| `LineTo` | `l` | Add a segment from the current point. |
| `CurveTo` | `c` | Add a curve with two control points and an end point. |
| `FillPathNonzero` | `f` | Fill using the nonzero winding rule. |
| `StrokePath` | `S` | Stroke the outline. |
| `FillAndStrokePathNonzero` | `B` | Fill and stroke the outline. |

The first rectangle combines `re` with `f`, the second `re` with `S`. The bottom rectangle uses `B`. The curve starts at `(54, 410)`, uses control points `(175, 500)` and `(405, 320)`, and ends at `(541, 410)`. Control points guide the curve without necessarily being points it passes through.

After `f`, `S` or `B`, the path is finished. To paint the same shape again, reconstruct it. The `ContentStreams` validator also rejects a color change or `Q` inside an unfinished path: settings precede geometry, then painting finishes it.

Reference: ISO 32000-1, **8.5.2–8.5.3** for path construction and painting.

## 2. Set two independent colors

`SetNonstrokingRGBColor` (`rg`) selects the color used for fills and for text in its default rendering mode. `SetStrokingRGBColor` (`RG`) selects the outline color. PDF operators are case-sensitive.

The three DeviceRGB components range from 0 to 1. `SetLineWidth` (`w`) sets the outline width. `SetLineCapStyle(LineCapStyle::Round)` (`J`) rounds the curve's ends. `SetLineDashPattern` (`d`) receives a `LineDashPattern`: `[4 4]` alternates four painted units with four empty units, starting with phase zero.

DeviceRGB colors suit this demonstration; their exact rendering depends on the reader and device. Color-managed output needs an appropriate color space, such as ICCBased, and explicit resources.

Reference: **8.4.3–8.4.4** for graphics-state parameters, **8.6.4.3** and **8.6.8** for DeviceRGB and color operators.

## 3. Isolate drawing with q and Q

`SaveGraphicsState` (`q`) pushes the current graphics state. `RestoreGraphicsState` (`Q`) restores the saved transformation matrix, colors, line width and other parameters. Each shape in the script is enclosed by this pair.

This explains why dashes do not affect subsequent rectangles and why their fill colors do not color the labels. It also protects text from the rotation applied to the last shape.

The current path's geometry is not part of the saved state. `Q` therefore does not end or cancel a path. The script paints each path before restoring the state, and balances all `q`/`Q` pairs.

Reference: **8.4.2** and **8.4.4**.

## 4. Draw in a local coordinate system

`ConcatenateMatrix` (`cm`) receives a `Matrix` of six `NumericType` values: `[a b c d e f]`. For a local point `(x, y)`, this example's transformation gives:

```text
x' = a × x + c × y + e
y' = b × x + d × y + f
```

Here the page uses normal coordinates, with one unit equal to **1/72 inch** and the origin at the lower left. The local rectangle is centered at `(0, 0)` and measures 100 × 80 units; its construction therefore begins at `(-50, -40)`.

- `[1 0 0 1 130 205]` places its center at `(130, 205)` without rotation.
- `[0.8660254 0.5 -0.5 0.8660254 415 205]` rotates it by 30 degrees and places its center at `(415, 205)`. The values are rounded `cos(30°)` and `sin(30°)`.

`cm` **concatenates** its matrix with the current matrix. The result depends on the existing state, and the order of multiple transformations matters. Each example starts again from the page state thanks to `q` and `Q`. Rotation does not modify the page's `/Rotate`: it transforms only the drawing in that block.

Reference: **8.3.2–8.3.3** for coordinate systems and matrices, **8.4.4** for `cm`.

## Try it

- Replace `StrokePath` with `FillAndStrokePathNonzero` to add a fill to a rectangle.
- Change the curve's two control points while keeping its start and end points.
- Use `[2 0 0 2 e f]` in an isolated block: the rectangle's size and outline width are transformed together.
- Add a second `q`/`Q` pair inside a block to experiment with nested states.

Positioning and margins are explicit. A path can extend beyond the page if its coordinates or transformation place it outside the paper; inspect the PDF after changing matrices.

[Tutorial index](README.md) · [Previous: pages and text](02-pages-and-text.md) · [Next: document outline](04-navigation.md)
