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

This repository contains the shared prose, site assets, generator and deployment
workflow. PHP code, executable examples, fixtures and original specification
documents remain in [their package repositories](https://github.com/orgs/PDFToolkit/repositories).
The module guides are published here from their released package sources.
The core groups its eighteen original reference PDFs under
`resources/reference-documents/`, preserving their original names and bytes.
Public reference downloads keep their existing URLs.

## Install the libraries

The PHP libraries are available on Packagist. Install the core with Composer:

```sh
composer require "roukmoute/pdf:^0.7.1"
```

The documented releases are core **0.7.1**, PDF reader **0.1.9**, images/fonts **0.1.8**
and independent OpenType **0.1.0**. They require **PHP 8.3 or later** and are
checked on PHP 8.3, 8.4 and 8.5. Core **0.7** additionally requires 64-bit PHP;
OpenType remains independent of the PDF core.

Choose the optional modules according to the files your application handles:

- [Core: roukmoute/pdf](https://packagist.org/packages/roukmoute/pdf)
- [PDF reader: pdftoolkit/pdf-reader](https://packagist.org/packages/pdftoolkit/pdf-reader)
- [Images: pdftoolkit/pdf-images](https://packagist.org/packages/pdftoolkit/pdf-images)
- [Fonts: pdftoolkit/pdf-fonts](https://packagist.org/packages/pdftoolkit/pdf-fonts)
- [OpenType: pdftoolkit/opentype](https://packagist.org/packages/pdftoolkit/opentype)

The three PDF modules install the core as a dependency. OpenType provides its own object model and installs without PDF dependencies. The package guide explains
their Composer commands and supported versions.

## PDF 2.0 guides and examples

The [PDF 2.0 guide](https://pdftoolkit.github.io/guides/pdf-2-0.html) and
[companion-specifications guide](https://pdftoolkit.github.io/guides/pdf-2-0-bundle.html)
explain ISO 32000-2:2020 EC3, modern encryption and signatures, PDF MAC,
metadata/declarations, associated files, document parts and qualified structure
roles, document timestamps, DSS/VRI evidence, geospatial measurements and
structure destinations. The [34 tutorials](https://pdftoolkit.github.io/tutorials/) include
executable examples and actual PDF previews. WTPDF auditing reports mechanical
checks and pending evidence; it does not certify accessibility or PDF/UA.

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
