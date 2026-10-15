# 06. Two representations of an image

This example displays the same colored pattern side by side: a compressed **image XObject** referenced by the page on the left, and an **inline image** within the drawing instructions on the right. PHP generates the entire 16 × 16 pixel pattern; no image file or download is needed.

![Preview of the two RGB pattern representations](../../tutorials/previews/images.png)

## Run the example

From the root of a core checkout, after `composer install`:

```sh
php examples/images.php images.pdf
```

The output path is optional; it defaults to `examples/images.pdf`. The complete script is [examples/images.php](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/images.php).

## 1. Produce the samples

`$pixels` contains raw RGB bytes, arranged row by row. Each pixel occupies three bytes: red, green and blue. With 16 × 16 pixels and 8 bits per component, the content measures **768 bytes**. The bright palette and four-pixel blocks make enlargement easy to observe.

These data have neither a PNG nor a JPEG header. The PDF dictionary supplies their interpretation:

| Entry | PHP object | Meaning |
| --- | --- | --- |
| `/Width 16` | `WidthEntry(IntegerType)` | Number of pixels in a row. |
| `/Height 16` | `HeightEntry(IntegerType)` | Number of rows. |
| `/BitsPerComponent 8` | `BitsPerComponentEntry(IntegerType)` | A component fits in one byte. |
| `/ColorSpace /DeviceRGB` | `ColorSpaceEntry(NameType)` | Each pixel has three components. |
| `/Interpolate false` | `InterpolateEntry(BooleanType)` | Request sharp edges when enlarged. |

These entry classes belong to Table 89 of the specification. The same immutable entry objects serve both representations.

## 2. Build an image XObject

`ImageDictionaryTable89` adds `/Type /XObject` and `/Subtype /Image` to the pixel description. `StreamObject` associates this dictionary with the data; `FlateDecode` compresses them with zlib during serialization. The written stream then has `/Filter /FlateDecode` and a `/Length` calculated from the compressed bytes.

The filter name describes the operation the **PDF reader** applies to recover pixels. The script supplies uncompressed pixels to `StreamObject`, which performs the corresponding encoding.

```php
$image = new StreamObject($pixels, $imageDictionary, new FlateDecode());

new XObject(new DictionaryType(
    new Entry(new NameType('Im1'), new IndirectReference($image)),
));
```

The page's `/Resources` dictionary links `/Im1` to the indirect stream. `InvokeXObject(new NameType('Im1'))` produces `/Im1 Do`. The same stream can be invoked several times with different transformations without copying its pixels.

## 3. Set size and position

Pixel dimensions describe image content. A PDF image is painted in the unit square; the current matrix determines its size on the page.

```text
q
216 0 0 216 64 400 cm
/Im1 Do
Q
```

Here `ConcatenateMatrix` applies scaling to 216 × 216 points, followed by translation to `(64, 400)`. The 16 pixels are therefore enlarged. `SaveGraphicsState` (`q`) and `RestoreGraphicsState` (`Q`) enclose the transformation so that other drawings and text retain their normal coordinates.

## 4. Insert an inline image

`InlineImage` writes an instruction composed of `BI`, the direct dictionary, `ID`, the bytes and `EI`. It appears directly in the content stream, with no `/Im1` resource or separate image object.

The example passes 768 raw bytes and declares no filter for this image. Its dictionary contains dimensions, bit depth, color and interpolation; the XObject's `/Type` and `/Subtype` entries are absent.

A second matrix places it at `(332, 400)` with the same size. The two patterns should therefore look identical, although their organization in the file differs.

## Try it

- Reuse `/Im1` with another `InvokeXObject` and matrix to compare sizes without recreating the image stream.
- Set `/Interpolate` to `true` and observe the reader's interpolation decision at high magnification.
- Change the palette or pattern while retaining exactly `Width × Height × 3` bytes with 8 bits per RGB component.
- Replacing pixels with already encoded JPEG data requires a different filter and construction; a complete PNG byte string cannot be used as raw RGB pixels.

## Things to know

This example covers opaque `/DeviceRGB` images, without masks or color profiles. It does not provide a PNG/JPEG loader. Generated classes describe specification entries; they do not constitute an image decoder.

An inline image cannot contain a binary sequence that would be interpreted as an ambiguous `EI` terminator. `InlineImage` rejects this situation. The tutorial's palette avoids it; an image XObject suits arbitrary data and reused images.

References in [ISO 32000-1:2008](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/PDF32000_2008.pdf): **7.3.8** (streams), **7.4.4** (FlateDecode), **8.3.3** (transformations), **8.8** (XObjects), **8.9.5 and Table 89** (image dictionary), **8.9.7** (inline images).

[← 5. Links](05-links.md) · [All tutorials](README.md) · [7. Axial shading →](07-gradient.md)
