# Apply redaction and write a fresh PDF

[English](36-applied-redaction.md) · [Français](../../tutorials/36-applied-redaction.md)

A `Redact` annotation identifies content to remove. Painting an opaque rectangle
does not remove the underlying text or images. The Adobe addendum, physical
pages 2–4, requires destruction of the affected data and a replacement appearance.
Core 0.8.0 introduces `SecureRedaction` for an explicitly normalized object graph.

## Run the actual example

```sh
composer require "roukmoute/pdf:^0.10.0"
php examples/pdf17-secure-redaction.php redacted.pdf --source=original.pdf
```

The optional second argument writes the original to a separate file for
comparison. The redacted result never embeds that original or appends a revision
to it. The complete executable PHP source and the two resulting pages are below.

## Understand the input

The example constructs two small pages sharing the same image. The second page
contains secret text, an `ActualText` replacement and a redaction annotation over
the secret text and image. Catalog XMP metadata also contains a secret. A green
rectangle outside the selected area provides a visible preservation check.

The page ends with a deliberately persistent translation matrix. The processor
must isolate the replacement mark from that source graphics state so the mark
appears in the annotation's coordinates.

## Make the operation explicit

```php
use PDF\Document\Redaction\RedactionAnnotation;
use PDF\Document\Redaction\RedactionPageRequest;
use PDF\Document\Redaction\RedactionPlan;
use PDF\Document\Redaction\SecureRedaction;

$result = (new SecureRedaction())->apply(
    $catalog,
    new RedactionPlan(
        new RedactionPageRequest($page, new RedactionAnnotation($annotation)),
    ),
);
$result->writeTo($destination);
```

`$catalog`, `$page` and `$annotation` are the actual objects assembled by the
application. The plan binds a selected annotation to its page; it does not search
the filesystem or silently import an external document. The immutable result is
written as a fresh file with a new reachable graph and no previous revisions.

## Follow what is removed

The default processor has no trusted font-outline geometry backend. It therefore
removes every text object on the selected page conservatively. Font `Widths` or
`FontBBox` declarations alone cannot prove that text lies outside the area. An
explicit `RedactionFontGeometry` implementation can provide actual geometry when
the application needs finer preservation.

An affected image or Form is indivisible. The tainted shared image is removed
from **both** pages, including its earlier use outside the selected page. The
green vector rectangles survive. This intentional excess deletion prevents a
shared resource from retaining affected payloads elsewhere in the result.
The same rule follows reverse dependencies through `Mask`, `SMask` and nested
Forms before rebuilding any final page. A surviving image cannot retain a
deleted image indirectly as its transparency mask.

The fresh catalog drops annotations, metadata, forms/XFA, attachments, actions,
outlines, structure and alternate-text channels. Unused rendering resources are
pruned. The result does not preserve the source's accessibility structure.
Retained fonts lose ancillary descriptor data such as `CharSet`, `FontFamily`
and `Style`. Context-specific dictionaries validate the types of retained
values: a string concealed under a numeric field is rejected.
Core 0.8.1 also validates the actual font domain and subtype. A simple Type1 or
TrueType font cannot retain superfluous `CIDSystemInfo` or `DescendantFonts`
entries. A Type0 font requires its actual CID descendant and compatible encoding;
legitimate CID identifiers remain in that domain. Invalid combinations are
rejected before any result, rather than carrying unused strings into the output.

## Produce the replacement appearance

`QuadPoints` takes precedence over `Rect` for the selected regions. Path bounds
use conservative control-point hulls, transformed coordinates and stroke extent.
Rectangle bounds include all four transformed corners under rotation or shear.
An unpainted path terminated by `n` is also removed when its recoverable geometry
crosses a region.
The example paints a black replacement with repeated, centred white `REDACTED`
text using an explicit default appearance. If `RO` is supplied, that replacement
Form takes precedence over colour and overlay-text entries.

The processor retains only supported normalized data. The default image path
accepts exact device-colour sample rows. Retained opaque image encodings, colour
profiles or complex font programs need an explicit `RedactionResourceSanitizer`
that parses and rebuilds those resources. Opaque affected images can instead be
deleted without decoding.

## Respect the accepted input boundary

Unsupported opaque content, unknown operators, unnormalized graphics states,
patterns, shadings, optional content, external XObjects, text clipping and
crossing clipping paths are rejected. Instruction, graph, nesting, image and
overlay-repeat budgets are explicit. This processor is not a general editor for
arbitrary external PDFs, and it cannot detect steganography in retained content.

The independent validator runs qpdf, inspects reachable objects and decoded
streams with pypdf, and renders source/result pages with Poppler. It checks the
absence of secret text, image and metadata payloads, the survival of green
vectors, the placement of the replacement and the single output revision.
Those checks demonstrate this normalized example's destruction and rendering;
applications must still validate their own input domain and publication process.
The regression oracle renders sixteen pages in total, including four transformed
rectangle cases and two transitive Mask/SMask dependency cases. Dependency work
also counts repeated graph edges against the instruction budget.

[Source audits](../source-audits.md) · [Security](../security.md) · [Tutorials](README.md)
