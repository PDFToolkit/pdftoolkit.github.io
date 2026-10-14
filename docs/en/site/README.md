# Building the documentation

The site is published at [pdftoolkit.github.io](https://pdftoolkit.github.io/)
from [PDFToolkit/pdftoolkit.github.io](https://github.com/PDFToolkit/pdftoolkit.github.io).
It presents the core and three optional modules from published versions
selected in the manifest. The documentation text and tools commit is
identified separately from documented package versions and commits.

## Sources and generation

This repository retains guides, tutorials, shared assets, build tools and
the publication workflow. PHP sources, examples, tests, specification
resources and Adobe PDFs remain in their package repositories. The build
reads them from a full core checkout prepared under `_sources/pdf`, with
modules installed by Composer from their published distributions.

The `resources/sources.json` manifest uses `schemaVersion: 1`. Its `packages`
list describes every package with `name`, `repository`, `version`, `revision`
and `optional`. This file is authoritative for documented versions and
commits. Pages and the site manifest retain these identities separately
from this repository's commit.

The core checkout must retain original PDFs, `resources/`, `examples/`,
`composer.lock` and `vendor/`. A Composer archive does not supply all Adobe
references or all required fixtures. Install development dependencies from
this checkout, preserving its lock; the exporter verifies that installed
module versions and revisions match the manifest. The selected core uses
Packagist to resolve modules; an application using these libraries installs
them with the [package guide](../packages.md) commands without building
the site.

`tools/export_api.php` loads the prepared core's autoloader and discovers
classes, interfaces, enums and traits in its `src/` and installed modules.
It exports their signatures, properties, constants and package provenance.
It reads default-parameter expressions without instantiating the objects
they describe. Source links use manifest commits, including for the core.

`tools/build_site.py` reads texts and assets from `--content-root`, then
examples, normative resources and originals from `--source-root`. It
combines the API and metadata from the core's `resources/iso32000-1/` and
`resources/adobe-supplement-iso32000/` to create component pages, family
indexes and search. Definitions retain constraints, table, document and
reference page. Composed entries distinguish Adobe and ISO sources; see
the [coverage guide](../coverage.md).

Module-specific guides are published under `/modules/reader/`,
`/modules/images/` and `/modules/fonts/`. Their package qualifies pages
and links so Markdown files sharing the same name remain distinct.

Every script in the core's `examples/` must have a tutorial or recipe and
a PDF. The site presents explanations, renderings of every page, complete
code and the generated PDF. Adobe PDFs are also accessible from standard
reference pages. The site manifest's `specificationSources` retains their
names, SHA-256 hashes, page counts and download paths; the checker compares
published bytes with originals.

Module examples are declared in the generator's `EXTERNAL_EXAMPLES`.
Tutorial 12 reads `examples/pages.php` and
`tests/Fixtures/page-tree/classic.pdf` from the installed reader module.
It publishes input-PDF bytes, its three previews and reading console output.
Their provenance uses the reader commit pinned in the manifest; the core
retains its generation examples.

## Local build

The workflow uses PHP 8.3 or later, Composer, Python 3.13, Poppler
(`pdftoppm`) and qpdf 12.4.2. Python dependencies are locked with their
hashes. The published site is static.

From this repository's root, prepare the core checkout at the manifest
commit, then run the same complete build as CI:

```sh
core_repository=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='roukmoute/pdf')['repository'])")
core_revision=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='roukmoute/pdf')['revision'])")
core_alias=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='roukmoute/pdf')['version'].rsplit('.', 1)[0]+'.x-dev')")
git clone "$core_repository" _sources/pdf
git -C _sources/pdf checkout --detach "$core_revision"
COMPOSER_ROOT_VERSION="$core_alias" composer install --working-dir=_sources/pdf --no-interaction --prefer-dist
python -m pip install --require-hashes -r tools/site-requirements.txt
python -m pip install --require-hashes -r _sources/pdf/tools/public-key-validation-requirements.txt
python tools/build_docs.py --source-root _sources/pdf --docs-revision "$(git rev-parse HEAD)" --remote
```

On PowerShell:

```powershell
$sourceManifest = Get-Content resources/sources.json -Raw | ConvertFrom-Json
$coreSource = $sourceManifest.packages | Where-Object name -eq 'roukmoute/pdf'
git clone $coreSource.repository _sources/pdf
git -C _sources/pdf checkout --detach $coreSource.revision
$env:COMPOSER_ROOT_VERSION = ($coreSource.version -replace '\.\d+$', '.x-dev')
composer install --working-dir=_sources/pdf --no-interaction --prefer-dist
python -m pip install --require-hashes -r tools/site-requirements.txt
python -m pip install --require-hashes -r _sources/pdf/tools/public-key-validation-requirements.txt
$docsRevision = git rev-parse HEAD
python tools/build_docs.py --source-root _sources/pdf --docs-revision $docsRevision --remote
```

`tools/build_docs.py` verifies published commits and tags, retained sources
and normative generations. It exports the API, executes all examples,
checks their PDFs with qpdf and independent readers, renders every page,
builds the site and checks its links. `--docs-revision` expects the complete
40-character SHA of the documentation commit; it does not replace package
revisions in the manifest. Tool paths can be specified with `--php`,
`--qpdf` and `--pdftoppm`.

To rebuild only the rendering from already-validated inputs:

```sh
php tools/export_api.php _build/api.json _sources/pdf resources/sources.json
python tools/build_site.py --content-root . --source-root _sources/pdf --sources resources/sources.json --docs-revision "$(git rev-parse HEAD)" --api _build/api.json --pdf-dir _build/pdfs --pdf-preview-dir _build/pdf-pages --output _site --base-path /
python tools/check_site.py _site
```

Use an empty output directory when pages are removed or renamed. The
generator does not delete files in an existing directory; the checker
reports obsolete pages. `_sources/`, `_build/` and `_site/` are working
directories ignored by Git.

## Preview and verification

The central site uses `--base-path /` for publication and local preview:

```sh
python -m http.server 8000 --directory _site
```

Open [localhost:8000](http://localhost:8000/) to check navigation, search,
the mobile menu, previews and downloads. Poppler renders images of every
PDF page. A native PDF viewer is also offered in a collapsible section;
its operation depends on the browser. Open and download buttons remain
available for every example.

`tools/check_site.py` verifies the page inventory, linked files, anchors,
unique identifiers, main headings, search, package coverage and PDF/source
pairs. The `exampleSources` manifest distinguishes generated PDFs from
reading inputs, with hashes of PDFs, sources and console output. The
checker validates provenance links, console-output escaping and all three
input pages. All package sources link to their published commits; the
documentation commit retains its own provenance.

PHP mechanism tests and checks remain in the core and module repositories.
Core CI validates examples on PHP 8.3, 8.4 and 8.5. From the core checkout,
Python checks use its locked dependency files and
`tools/validate_mechanisms.py`, `tools/validate_adobe_supplement.py` and
`tools/validate_adobe_encryption.py` scripts. Encryption checks require
qpdf 12.1 or later.

## Publication

This repository's Pages workflow prepares sources at manifest revisions,
installs locked dependencies, exports the API, produces and validates PDFs,
renders their pages with Poppler, builds the site with `--base-path /` and
runs the checker before deployment. Pages and identity write permissions
are reserved for the deployment job.

The central repository owns root publication. The former `/pdf/` project
site retains redirects from its HTML routes to central routes, passing
query parameters and fragments through. Its old binary downloads remain
accessible. Package repositories retain their sources, tests, releases
and CI; their changes affect the published reference only after an explicit
central-manifest update.

Generated HTML and PDFs are produced during the build. To add a generation
example, write the script in its package repository, then its tutorial or
recipe in this repository and declare its route in `tools/build_site.py`.
Verification fails if a core script has no corresponding page. For a module
example, declare its package, source/input paths and expected page count in
`EXTERNAL_EXAMPLES`, then retain its console output and previews during
the build.
