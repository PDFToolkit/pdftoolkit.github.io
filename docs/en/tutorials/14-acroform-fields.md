# 14. AcroForm fields and appearances

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.9.1/examples/acroform-fields.php)
produces a page with a name, country list, checkbox, radio buttons, reset button
and empty signature field.

```sh
php examples/acroform-fields.php acroform-fields.pdf
```

`FieldTree` carries inherited values: Helvetica resource, default text appearance
and alignment. `NonTerminalField` creates the `Person` group; its children have
partial names. The full name `Person.Name` follows from the tree.

Value `/V` and appearance `/AP` have different purposes. The former describes
data; the latter is a Form XObject drawing the widget with its own `BBox` and
resources. Changing the value does not recalculate the appearance: supply a
new appearance or explicitly choose `NeedAppearances`.

Editable text in both `/Tx` **and** `/Ch` fields is enclosed in a `/Tx BMC ... EMC`
sequence. This marker's name remains `Tx`, even for a `Ch` list. A reader replaces
only that sequence during editing; the frame stays outside. Without the marker,
the ISO procedure appends new text at the end of the stream and preserves the
old drawing, which can produce overlapping text in Acrobat Reader.

The script composes this sequence with `BeginMarkedContent`, `SaveGraphicsState`,
`BeginTextObject`, `EndTextObject`, `RestoreGraphicsState` and `EndMarkedContent`
objects. Clipping is inside too: `Q` restores it and it can be replaced with the
text. Button and signature appearances remain separate drawings; they do not
require this variable-text marker.

`WidgetAnnotation` connects a field to its rectangle on the page. The field lists
its widgets in `/Kids`, each widget points back through `/Parent`, and the page
references them in `/Annots`. The writer checks that they belong to the actual
catalog. A checkbox has `/Off` and `/Yes` appearances; `/AS` selects the state.

The list distinguishes display labels from export values.
`ChoiceValueDomain::ExportValues` makes the choice explicit where some ISO wording
is ambiguous; `/I` retains selected indices in `/Opt`. The initial appearance
draws `France` and `Belgique` on two lines, with both selections inside the variable
sequence. It does not draw export codes `FR` and `BE`, which belong to field data.

Core 0.8 keeps the default `ChoiceIndexSemantics::Pdf17` contract for this PDF
1.7 example. Select `ChoiceIndexSemantics::Pdf20Ec3` explicitly for the corrected
PDF 2.0 rules: indices can be used without `MultiSelect`; distinct display names
sharing an export value require them; an array-valued `V` alone does not. The
effective document version must then be PDF 2.0. This constructor argument comes
before variadic extra entries. The [source-audit guide](../source-audits.md)
explains correction #468 and its exact retained source thread.

Change values, options, rectangles or states in the script to observe each link.
The signature field stays empty here; [tutorial 20](20-signed-document.md) creates
a signature. Barcode codecs, scripts and XFA execution require their own engines.

Reference: ISO 12.7, physical pages 438–473; variable text and replacement
procedure §12.7.3.3, pages 443–444. Adobe supplement pages 42–48 and page 121,
notes 118–119: without `/MK`, Acrobat preserves content outside the `/Tx` sequence.
The presence of `/MK` requests complete appearance regeneration; it is not
required for this script's custom appearances.

[Index](README.md) · [Complete code](https://github.com/PDFToolkit/pdf/blob/v0.9.1/examples/acroform-fields.php)
