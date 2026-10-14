# 33. PDF 2.0 geospatial objects

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.7.0/examples/pdf20-geospatial.php) draws two illustrative panels and attaches geospatial measurement data to the page, a Form XObject and an image. One region declares a geographic reference system; the other declares a projected system. They are independent sample regions, not a conversion of the same surveyed map.

Drawing a grid does not create geographic semantics. The script separately constructs the coordinate systems, control-point pairs, measurement viewports, preferred units and point cloud that describe the PDF objects.

## Run the example

From a core 0.7.0 checkout:

```bash
php examples/pdf20-geospatial.php geospatial.pdf
```

The example uses native PDF objects only. It needs no external image converter, font converter, GIS database or projection executable. A viewer may display the page without offering geographic measurement tools; the preview still shows the actual drawing.

## Declare coordinate systems explicitly

```php
$geographic = new G\GeographicCoordinateSystem(new G\EpsgCode(4326));
$projected = new G\ProjectedCoordinateSystem(new G\EpsgCode(3857));
```

Here `G` aliases `PDF\Document\Geospatial` in the script. A `GeographicCoordinateSystem` accepts exactly one EPSG code or WKT string. A `ProjectedCoordinateSystem` requires at least one of them. WKT is supplied through `AsciiString`; the library does not fetch a registry, parse an entire WKT grammar or infer a projection from the page drawing.

Changing an identifier does not recalculate the control points. Supply coordinates that actually belong to the chosen system. `GeographicPosition` stores latitude before longitude; `ProjectedPosition` stores easting before northing. Values must be finite, and latitude is bounded to −90 through 90 degrees. No arbitrary longitude branch is imposed.

## Keep local and world points synchronized

`GeospatialControlPoint` pairs a `LocalPosition` with a world position. `GeospatialControlPoints` derives `/LPTS` and `/GPTS` from those same pairs, preventing different array lengths or mixed dimensions and coordinate kinds.

```php
$point = new G\GeospatialControlPoint(
    new G\LocalPosition(new N(0), new N(0)),
    new G\GeographicPosition(new N(48.85), new N(2.34)),
);
```

The example uses four control points per region. Local two-dimensional coordinates lie in the object's unit square. `GeospatialBounds` supplies the normalized neatline polygon; it does not replace the viewport's rectangle in page coordinates. The 3D variant uses triples in the permitted 3D/RichMedia contexts, with separate validation rather than silently treating every measure as three-dimensional.

## Give each measurement its actual owner

`GeospatialMeasure` writes `/Type /Measure`, `/Subtype /GEO`, its coordinate system and paired arrays. A `Viewport` supplies the page-space `/BBox`, an optional name and that measure; `Viewports` provides the page's `/VP` array.

For overlapping viewports, `Viewports::forPoint()` selects the last one containing the measurement's first point. `Viewport::local()` converts a page point to normalized local coordinates. Neither operation performs a geographic projection.

The left panel paints a Form XObject with its own `/Measure` and `/PtData`; the right paints a one-pixel image with its own `/Measure`. Their painting matrices position the illustration independently of their geospatial metadata. Effective-graph checks also cover generic dictionaries and incremental replacements, so manually adding entries does not bypass the context or version rules.

## Add display units, a matrix and point data

`PreferredDisplayUnits` receives a linear, area and angular enum in that order. The example chooses metres, square metres and degrees. These preferences describe a reader's measurement display, not the units of the page's graphics operators.

`ProjectedCoordinateSystemMatrix` contains exactly twelve numeric coefficients. It applies the row vector `[x y z 1]` with an implicit final column `[0 0 0 1]`, and takes precedence over GPTS in a projected system. Its `transform()` executes that affine calculation; it does not convert one map projection into another.

`PointDataNames` names the point-cloud columns; each `PointData` tuple has exactly that width. The sample LAT/LON/ALT tuple contains 48.86, 2.35 and 35. `PointDataCollection` associates such clouds with a viewport. Column data and drawing operators remain independent objects.

## Check the serialized relationships

`tools/validate_pdf20_geospatial.py` independently reads emitted GCS/GPTS/LPTS, Bounds, PDU, PCSM, viewports, Form/image owners and point clouds using pypdf and qpdf. It checks initial, incremental and linearized output in all three cross-reference formats, including historical/fallback prefixes.

```bash
python tools/validate_pdf20_geospatial.py \
  --php php --qpdf qpdf --work-dir /tmp/pdf20-geospatial
```

To explore the model, move a viewport, change its unit preferences or add another paired point. Keep the tuples synchronized and choose the coordinate kind explicitly. An independent GIS tool is still needed to establish the correctness of real survey data, WKT meaning or a projection conversion.

## References

ISO 32000-2:2020 clauses 12.9 and 12.10, tables 265–272, physical pages 611–622, describe these objects. The [retained original](https://github.com/PDFToolkit/pdf/blob/v0.7.0/ISO_32000-2_sponsored_EC3.pdf) includes EC3 annotations. The native profile explicitly records issue 358 as `Completed` and issues 533, 534 and 284 as `Accepted`; their distinct approval authorities remain visible in the catalogue.

[Tutorial path](README.md) · [Bundle guide](../pdf-2-0-bundle.md) · [Coverage](../coverage.md)
