# 30. PDF 2.0 namespaces and WTPDF checks

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/pdf20-tagged-namespaces.php) constructs a page whose logical structure is independent of its drawing operations. It combines PDF 2.0 roles, the table-of-contents types unique to PDF 1.7 and a custom paragraph. An embedded font, reciprocal ParentTree links and XMP metadata make these relationships inspectable in the actual file.

The preview shows five lines. Their positions do not establish their meaning: the script explicitly constructs the H1, P, TOC, TOCI and Reference elements that describe them.

## Run the example

From a core 0.7.1 checkout with its locked development dependencies:

```bash
php examples/pdf20-tagged-namespaces.php namespaces.pdf --audit-json
```

The first argument selects the output PDF. `--audit-json` writes a separate report to standard error; it does not mix JSON into the PDF bytes. `--xref-stream` and `--hybrid` select a cross-reference stream and a hybrid section respectively. Without these options, the writer produces a classic cross-reference table.

The optional `pdftoolkit/pdf-fonts` module reads the demonstration Noto Sans font. The core receives normalized PDF objects: embedded program, descriptor, CID metrics, CID/GID mapping and ToUnicode CMap. Installing the core alone does not install this converter.

## Qualify meaning with a namespace

In PDF 2.0, a type name alone does not always identify its semantics. `StructureRole` combines that name with a `StructureNamespace` object:

```php
$pdf20 = new StructureNamespace(StandardStructureNamespace::PDF20);
$pdf17 = new StructureNamespace(StandardStructureNamespace::PDF17);
$document = new StructureElement(
    new StructureRole(new NameType('Document'), $pdf20),
);
```

Each element writes `/S` for its type and an indirect `/NS` reference to its namespace dictionary. `StructureNamespaces` supplies the document's canonical instances to `StructureTreeRoot`. Two objects carrying the same namespace identifier are not interchangeable in this model: a namespace set owns one instance for each identifier.

Types shared by PDF 1.7 and PDF 2.0 use the PDF 2.0 namespace in a mixed tree. Certain types, including TOC, TOCI and Reference, remain defined in the PDF 1.7 namespace. ISO/TS 32005 specifies their containment relationships with other elements. The script therefore keeps these namespaces distinct instead of renaming every type.

## Define a custom role without a global registry

The demonstration namespace `urn:pdftoolkit:example:report` contains `ReportParagraph`. Its mapping explicitly targets P in the PDF 2.0 namespace:

```php
$report = new StructureNamespace(
    'urn:pdftoolkit:example:report',
    new NamespaceRoleMap(new NamespaceRoleMapping(
        new NameType('ReportParagraph'),
        new StructureRole(new NameType('P'), $pdf20),
    )),
);
```

The `/RoleMapNS` dictionary contains a target of the form `[/P namespace-reference]`. A name alone would identify the default PDF 1.7 namespace, even when the mapping belongs to another namespace. Transitive resolution preserves this distinction, detects cycles and has an explicit operation budget.

The writer checks that used and targeted namespaces belong to the document's set. Effective-graph validation also checks generic dictionaries and frozen revision facts: constructing `/NS` entries manually does not bypass the PDF 2.0 minimum version.

## Connect drawing operations to logical elements

Each line is enclosed by a marked-content sequence with an MCID. These numbers are local to the content container; they are not global structure-element identifiers. The page carries `/StructParents 0`, which identifies its ParentTree key.

`PageMarkedContent` connects each MCID to its `StructureElement`. `StructureTreeRoot` derives the reciprocal ParentTree: MCID 0 points to the heading, 1 to the custom paragraph, 2 to the table-of-contents reference, and 3 and 4 to the remaining paragraphs. The same tree provides `/P` links between parents and children.

The table of contents adds another relationship. Its Reference element has a `/Ref` array targeting H1. This structural reference does not create a clickable link area; the script constructs no Link annotation. `addReference()` also supports reciprocal citations between a citing element and an FENote when a document needs them.

## Select inclusion rules and corrections

`StructureInclusionRules` applies all 53 rows of ISO/TS 32005 table 5 to resolved roles. It checks permitted children, occurrence bounds, inherited constraints through Part/Div/NonStruct and Ruby/Warichu assemblies. The exemption for a standalone PDF 1.7 tree remains distinct from the rules for a mixed tree.

The default `Published2023` mode follows the supplied source. The example explicitly selects `StructureInclusionCorrections::Resolved336And440`: the PDF Association resolutions permit Sub inside Code and replace the undefined WP/Figure `c` cell with `0..n`. This selection is not presented as a new ISO edition. Other errata discussions are not silently incorporated.

## Separate declarations from verification

The XMP packet contains a `dc:title` with `x-default` and `fr` values. It also contains two explicit author declarations for this small example: ISO/TS 32005 and the WTPDF reuse level. A declaration is an assertion; its presence does not prove that assertion true.

The WTPDF identifiers supplied by the specification are exactly:

```text
http://pdfa.org/declarations/wtpdf/#reuse1.0
http://pdfa.org/declarations/wtpdf/#accessibility1.0
```

The script then requests a separate audit:

```php
$audit = (new WtPdfAudit())->inspect(
    $catalog,
    new EffectivePdfVersion($header, $catalog),
    WtPdfConformanceLevel::Reuse,
);
$audit->assertNoDetectedFailures();
```

The audit inserts no declarations. It distinguishes `Failed`, `HumanReviewRequired` and `AdditionalValidationRequired`. The example has no detected failures but retains pending reviews. `assertNoDetectedFailures()` therefore does not mean “certified accessible document”.

Mechanical checks cover namespaces, regular tables with spanning cells, certain list/note relationships, annotations, metadata, embedded-file descriptions and actual font usage. They distinguish rendered fonts, whose programs must be embedded, from fonts used exclusively in text rendering mode 3. They also check certain CID/GID and ToUnicode relationships.

Semantic type selection, suitable descriptions, intended reading order and form context require human review. Font programs, embedding rights, certain metrics, MathML grammar and other exhaustive rules need additional validation. The [detailed coverage record](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/wtpdf-1.0/coverage.json) separates these limits from executed checks. This partial audit is not WTPDF or PDF/UA-2 certification.

## Verify generated bytes

Core 0.8 can additionally compare a field's XML `RV` rich text with its inherited
canonical `V`, using an explicitly selected `WtPdfRichTextChecks` and native
`WtPdfXmlRichTextParser` backend. The [bundle guide](../pdf-2-0-bundle.md#compare-rich-text-field-content-explicitly)
shows the construction and security boundary. Unsupported XML/CSS or absent
parsing evidence remains pending; it cannot be counted as an audit success.

`tools/validate_pdf20_tagging.py` inspects indirect references, custom mapping, ParentTree, MCIDs, Ref and XMP XML using pypdf and qpdf. It also checks every glyph shown in this example: GID presence, Unicode mapping and agreement between PDF widths and metrics in the actual embedded TrueType program. Poppler supplies independent text extraction. All three cross-reference formats are exercised.

You can change the text, introduce a second custom namespace or replace the table of contents with a list. Every change must preserve associations between operators, MCIDs, containers, parents and resolved types. The visible file and audit report are complementary results to inspect.

## References

The [retained bundle sources](https://github.com/PDFToolkit/pdf/tree/v0.11.0/resources/reference-documents) come from the [PDF Association](https://www.pdfa.org/sponsored-standards/). Relevant physical pages: ISO 32000-2, 739–744 for dictionaries and namespaces, 809–810 for standard namespaces; ISO/TS 32005, 9–13 for mixed-namespace rules and 14–46 for the full table; WTPDF, 9–10 for conformance levels, 14–30 for structure and 32–49 for other constraints. The bundle catalogue records each original file's hash and identity.

[Tutorial path](README.md) · [PDF 2.0 guide](../pdf-2-0.md) · [Coverage](../coverage.md)
