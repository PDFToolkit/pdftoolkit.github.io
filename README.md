# PDFToolkit documentation

[English](README.md) · [Français](README.fr.md)

The website opens in [English](https://pdftoolkit.github.io/) by default;
the complete [French documentation](https://pdftoolkit.github.io/fr/) is
available through the language selector on every page.

The shared documentation for PDFToolkit lives at **https://pdftoolkit.github.io/**.
It includes the core, PDF reader, image converters and font converters, with
their guides, complete API reference, tutorials, executable PHP source and PDF
previews. Start with [the package guide](https://pdftoolkit.github.io/guides/packages.html)
or the module you need:

- [Core](https://pdftoolkit.github.io/modules/core/)
- [PDF reader](https://pdftoolkit.github.io/modules/reader/)
- [Images](https://pdftoolkit.github.io/modules/images/)
- [Fonts](https://pdftoolkit.github.io/modules/fonts/)
- [OpenType](https://pdftoolkit.github.io/modules/opentype/)
- [Codecs](https://pdftoolkit.github.io/modules/codecs/)
- [PDF to HTML](https://pdftoolkit.github.io/modules/to-html/)

This repository contains the shared prose, site assets, generator and deployment
workflow. PHP code, executable examples, fixtures and original specification
documents remain in [their package repositories](https://github.com/orgs/PDFToolkit/repositories).
The module guides are published here from their released package sources.
The core groups its eighteen original reference PDFs under
`resources/reference-documents/`, preserving their original names and bytes.
Public reference downloads keep their existing URLs.

Reader 0.7 adds explicit graph import, bounded CCITT and native/PHP image decoding. Images 0.2 adds all legal static PNG depths and Adam7, calibrated/ICC colour and JPEG YCCK. Fonts 0.2 connects static TrueType/CFF programs to explicit OpenType layout; OpenType 0.4 adds collections, Unicode cmap formats and feature ranges. The [coverage guides](https://pdftoolkit.github.io/guides/coverage.html) distinguish these mechanisms from rendering, automatic Unicode shaping and signature trust.

## Install the libraries

The PHP libraries are available on Packagist. Install the core with Composer:

```sh
composer require "roukmoute/pdf:^0.12"
```

The documented release series are core **0.12**, Reader **0.7**, Images and Fonts **0.2**, OpenType **0.4**, Codecs **0.1** and PDF-to-HTML **0.7**. They require **64-bit PHP 8.3 or later**; qualification covers PHP 8.3, 8.4 and 8.5. The source manifest pins exact versions and revisions. OpenType and Codecs have no PDF core dependency.

Choose the optional modules according to the files your application handles:

- [Core: roukmoute/pdf](https://packagist.org/packages/roukmoute/pdf)
- [PDF reader: pdftoolkit/pdf-reader](https://packagist.org/packages/pdftoolkit/pdf-reader)
- [Images: pdftoolkit/pdf-images](https://packagist.org/packages/pdftoolkit/pdf-images)
- [Fonts: pdftoolkit/pdf-fonts](https://packagist.org/packages/pdftoolkit/pdf-fonts)
- [OpenType: pdftoolkit/opentype](https://packagist.org/packages/pdftoolkit/opentype)
- [Codecs: pdftoolkit/pdf-codecs](https://packagist.org/packages/pdftoolkit/pdf-codecs)
- [PDF to HTML: pdftoolkit/pdf-to-html](https://packagist.org/packages/pdftoolkit/pdf-to-html)

The image/font/reader modules install the core. Fonts also installs the independent OpenType model; PDF-to-HTML installs Reader. Codecs is a separate pure-PHP decoder library. On explicit image decoding, Reader selects a qualified Ghostscript/prlimit native profile first, then the installed PHP library for unavailable capabilities. If neither is available, it gives an actionable Composer command; it never installs a dependency silently. The [image codec guide](https://pdftoolkit.github.io/modules/reader/image-codecs.html) documents exact profiles, budgets and metadata.

PDF-to-HTML 0.7 derives semantic content from tagged PDFs with checked structure
associations, Unicode, images, tables, navigation and form fields. Its
[clause ledger](https://pdftoolkit.github.io/modules/to-html/requirements.html)
links the retained reference to executable decisions and independent tests.
The [profiles and policies](https://pdftoolkit.github.io/modules/to-html/policies.html)
separate semantic output, optional ResetForm/SubmitForm behavior and trusted PDF
scripts. The [graphics guide](https://pdftoolkit.github.io/modules/to-html/graphics.html)
explains isolated PDF export and the application-supplied rendering engine.
Rendering, authentication and unsupported codecs remain explicit capabilities;
the default profile executes no PDF scripts or form actions.

PDF-to-HTML 0.7 preserves native MathML layout when mapping Layout placement,
including shared classes. Explicit author CSS and MathML display remain authoritative.
The [MathML coverage guide](https://pdftoolkit.github.io/modules/to-html/coverage.html#mathml-placement-and-browser-integration)
explains the rules and independent Chromium/Firefox checks.

PDF-to-HTML 0.6 adds reusable button appearance rendering, explicit source-bound
[signature validation](https://pdftoolkit.github.io/modules/to-html/signatures.html)
and native status popovers. The selected certificate verifies mathematical
integrity of a complete PDF revision; trust, revocation and later-change
permissions remain separate. Content, list/attribute and form corrections are
tracked in the bilingual clause ledger and checked with independent tools.

Reader 0.4 and PDF-to-HTML 0.4 provide explicit native password authentication with
verified user/owner permissions. The [reader guide](https://pdftoolkit.github.io/modules/reader/authentication.html)
and [HTML guide](https://pdftoolkit.github.io/modules/to-html/authentication.html)
explain credentials, crypt filters, rejection boundaries and viewer obligations.
Reader 0.5 also provides explicit [Adobe.PubSec authentication](https://pdftoolkit.github.io/modules/reader/public-key-authentication.html),
with independent filter keys, authenticated recipient rights and source MAC
verification. Certificate decryption does not establish signature trust.
OpenType 0.2 independently provides GSUB/GPOS/GDEF and explicit variation
coordinates; see [positioning](https://pdftoolkit.github.io/modules/opentype/positioning.html)
for native adjustments and the remaining shaping/outline boundaries.

## PDF 2.0 guides and examples

The [PDF 2.0 guide](https://pdftoolkit.github.io/guides/pdf-2-0.html) and
[companion-specifications guide](https://pdftoolkit.github.io/guides/pdf-2-0-bundle.html)
explain ISO 32000-2:2020 EC3, modern encryption and signatures, PDF MAC,
metadata/declarations, associated files, document parts and qualified structure
roles, document timestamps, DSS/VRI evidence, geospatial measurements and
structure destinations. The [37 tutorials](https://pdftoolkit.github.io/tutorials/) include
executable examples and actual PDF previews. WTPDF auditing reports mechanical
checks and pending evidence; it does not certify accessibility or PDF/UA.

Core 0.8 adds [197 executed dictionary rules and reviewed source corrections](https://pdftoolkit.github.io/guides/source-audits.html),
conservative [applied redaction](https://pdftoolkit.github.io/tutorials/36-applied-redaction.html)
with fresh PDF output, and optional WTPDF XML rich-text comparison. The guides
distinguish the 65-record Adobe errata classification from complete implementation
and retain the unreviewed EC3, document-policy and external/human requirements.
Core 0.8.1 adds verified native-history and complete-delta protections for
bounded incremental signing/maintenance, plus font-domain validation during
redaction. The [security guide](https://pdftoolkit.github.io/guides/security.html)
explains supported operations, rejected changes and runtime provenance migration.
Core 0.10.0 adds bounded native filling, P3 markup and per-update UR3
authority; its [guide](https://pdftoolkit.github.io/guides/protected-revisions.html) and
[tutorial 37](https://pdftoolkit.github.io/tutorials/37-protected-form-fill.html) explain
the supported operations, frozen appearance boundaries and independent-oracle limits.

Further source-bound additions cover ordered barcode messages and native
widget appearances, effective annotation/action/rectilinear-measure relationships,
selected Type 3 glyph usage and contextual WTPDF deprecation recommendations.
Source PDF MAC verification has its [reader guide](https://pdftoolkit.github.io/modules/reader/source-mac.html) and explicit required-input
policy. The guides retain symbology, rendering, opaque-content and trust boundaries;
their checks provide evidence for those operations, not complete PDF conformance.

## Reproducible sources

[resources/sources.json](resources/sources.json) records the selected stable
package versions and their exact Git commits. The build checks that each tag
identifies the recorded commit and that installed optional modules match it.
API source links use those commits. Documentation source links use this
repository's own commit.

## Build and contribute

See [the build guide](docs/en/site/README.md) for local commands and requirements.
The workflow builds actual PDF examples, checks them with independent readers,
renders all their pages, generates every API page and validates the whole site.
It also verifies the HTML module's glyph and inline/fax fixtures, actual semantic
HTML, isolated graphics, original rendering contexts and widget appearances with HTML5/pypdf/Poppler,
page-navigation targets, source signature integrity, the Node runtime and the figure-export/safe-reset/explicit-certificate examples.
Those additional validation outputs stay in the build workspace; only the
documented tutorial artifacts are published.

When a package release is published, update its source pin, validate the site,
and publish a new documentation release. Package installations remain
independent: generating this site does not add modules to core consumers.

## Existing addresses

Existing URLs under `https://pdftoolkit.github.io/pdf/` remain supported by the
core project's compatibility deployment. HTML navigation preserves its path,
query and fragment; PDF and other binary URLs continue to serve the actual bytes.

Documentation began in [PDFToolkit/pdf](https://github.com/PDFToolkit/pdf).
The shared content was migrated from core 0.5.2, commit
`ad1384a1400f9b13614e08aa352410b0af4b1e9c`, under the retained [MIT license](LICENSE).
