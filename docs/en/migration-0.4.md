# Migrating to core 0.4

PHP 8.3 remains the minimum version, with CI on 8.3, 8.4 and 8.5. The core
retains its three production extensions and depends on no optional module.
Module releases 0.1.2 accept core series 0.2, 0.3 and 0.4.

The last five static factories are replaced by explicit constructions.
Values and children have their own objects.

| Previous construction | Explicit construction |
| --- | --- |
| `Matrix::identity()` | `new Matrix()` |
| `LineDashPattern::solid()` | `new LineDashPattern()` |
| `NameTree::branch($a, $b)` | `new NameTree(new NameTreeChildren($a, $b))` |
| `NumberTree::branch($a, $b)` | `new NumberTree(new NumberTreeChildren($a, $b))` |
| `HexadecimalString::fromHex($digits)` | `new HexadecimalString(new HexadecimalDigits($digits))` |

`HexadecimalString($bytes)` still receives raw bytes. The `HexadecimalDigits`
form receives hexadecimal digits: these are distinct contracts. Tree branches
check their limits and do not mix children and leaf pairs in one node.

`TextString` selects PDFDocEncoding when the text is representable, otherwise
UTF-16BE. `PDFDocEncodedString` requires PDFDocEncoding; a `LiteralString` can
receive UTF-16BE bytes explicitly prefixed with a BOM. `PdfDocEncodedPassword`
retains its explicit-byte contract for historical algorithms; encode text
with `PDFDocEncoding` before supplying it if necessary.

Fonts have explicit programs, metrics, encodings and options. A subset
identity uses `SubsetFontName`, with `FontSubsetTag` and the original name.
The writer shares a per-file registry; a plain name mimicking the `ABCDEF+`
prefix does not replace this object.

`SampleLayout` objects can now declare other depths and color spaces. Existing
converters continue to supply the same eight-bit samples. To process a
generic layout, use its `space()` and `components()` methods rather than
assuming its property is always an enum.

Writers check the catalog, effective pages and reachable components, as well
as known version requirements for selected features. `Catalog.Version` can
raise the version advertised in the header. A new object must therefore
respect the document context in which it is actually written.

`FileWriter::revision()` now retains the encryption operation. An encrypted
update reuses that operation and protects Encrypt's identity. Signatures and
linearization have separate writers and document-specific states. No global
registry or implicit file search is added.

[Coverage](coverage.md) · [Architecture](architecture.md) · [Releases](../../CHANGELOG.md)
