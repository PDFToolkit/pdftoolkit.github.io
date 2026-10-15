# Building the documentation

The site is published at [pdftoolkit.github.io](https://pdftoolkit.github.io/)
from [PDFToolkit/pdftoolkit.github.io](https://github.com/PDFToolkit/pdftoolkit.github.io).
It presents the core, optional PDF modules, HTML derivation and the independent OpenType model from published versions
selected in the manifest. The documentation text and tools commit is
identified separately from documented package versions and commits.

## Sources and generation

This repository retains guides, tutorials, shared assets, build tools and
the publication workflow. PHP sources, examples, tests, specification
resources and Adobe PDFs remain in their package repositories. The build
reads them from a full core checkout prepared under `_sources/pdf`, with
PDF modules installed by Composer from their published distributions. The OpenType package comes from a separate checkout under `_sources/opentype`, at the published commit and tag selected by the same manifest. Its independent installation changes neither the core nor its lock.

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

All eighteen original Adobe, ISO and companion reference PDFs live in the core’s
`resources/reference-documents/` directory. Source metadata records each path
separately from the original filename and fingerprint. The generator reads these
paths while retaining the existing public reference-download URLs. Test fixtures
and generated examples remain beside their owning tests and scripts.

`tools/export_api.php` loads the prepared core's autoloader and discovers
classes, interfaces, enums and traits in its `src/`, installed PDF modules and the OpenType checkout. It also loads OpenType’s own autoloader.
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
`/modules/images/`, `/modules/fonts/`, `/modules/opentype/` and `/modules/to-html/`. Their package qualifies pages
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

The PDF-to-HTML checkout is separately pinned under `_sources/pdf-to-html`.
Its locked reader supplies the documented reader 0.3.0 without changing the core
lock. Tutorial 35 runs its real CLI against the independently generated tagged
fixture. The build checks the retained reference and fixture bytes, then executes
the package's pypdf/HTML5 oracle. It copies every asset listed in the CLI JSON,
checking filenames, SHA-256 and output collisions. `derivedHtml` stays outside
the bilingual documentation-page inventory and is previewed in an empty sandbox.
Module guides/API are published under `/modules/to-html/`.

The authentication guide is reachable under both `/modules/reader/` and
`/modules/to-html/`; OpenType's native GPOS/variation guide is under
`/modules/opentype/positioning.html`. All have reciprocal French counterparts.
Tutorial 36 runs the core's actual `pdf17-secure-redaction.php` and publishes its
two result pages. The build separately validates source/result bytes and pixels
with qpdf, pypdf and Poppler; its private source copy is never published as the
redacted result. EC3 annotation identities and approval threads are checked
against the unchanged canonical PDF, separately from dictionary generation.

The current selection documents PDF-to-HTML 0.3.0 and reader 0.3.0. The
[requirements ledger](https://pdftoolkit.github.io/modules/to-html/requirements.html),
[policies](https://pdftoolkit.github.io/modules/to-html/policies.html) and
[graphics](https://pdftoolkit.github.io/modules/to-html/graphics.html) guides
distinguish native rules, HTML adaptations and explicit capabilities for
rasterization, authentication and additional codecs.

Native R=2–7 authentication is an explicit reader selection. The HTML package's
independent authentication oracle decrypts actual qpdf fixtures and parses the
derived HTML, checking user/owner permissions, wrong credentials and converter
reuse. Its transient fixtures remain in the validation workspace.

`tools/build_docs.py` reproduces glyph tables and inline/fax fixtures, then runs
the HTML5/pypdf oracles, Poppler pixel comparisons for graphics/contexts/fax,
content-parent anchor checks and the Node runtime. It also executes examples
02/03 for figure export and targeted `/DV` reset, which does not enable PDF
ECMAScript. These two outputs and their assets stay under
`_build/pdfs/html-validation/`; they add neither pages nor assets to the site.

The ISO 32000-2:2020 EC3 catalogue is read from `resources/iso32000-2-2020/`.
Its API panels use explicit edition mappings rather than bare table numbers.
`repositorySpecificationSources` records the original filename, hash, size, pages and links to the PDF and its metadata at the documented core commit. The original is public in that repository following confirmed redistribution authorization; its 19 MB are not duplicated in site output. The build verifies original bytes before publishing that link. Lesson 27 uses a real generated PDF and the selected font module.

`bundleSpecificationSources` separately records all eleven companion originals
from `resources/iso32000-2-bundle/sources.json`. Their names, byte identities,
physical pages and PDF Association provenance are checked before publishing
pinned repository links. The source PDFs remain outside site assets and Composer
archives. API panels distinguish translated project-authored summaries from
original normative English excerpts. Complete base-table inventory and complete
conformance are separate manifest fields.

The build checks the ISO2 catalogue compiler, PHP generator and TS 32005 matrix,
then runs the metadata, AES-GCM/CMS/MAC, timestamp/DSS and tagged-content oracles.
The timestamp example receives the explicitly selected `--openssl` executable.
All examples have paired English/French explanations and actual rendered PDFs.

## Local build

The workflow uses 64-bit PHP 8.3 or later, Composer, Python 3.13, Node 24, OpenSSL, Poppler
(`pdftoppm`) and qpdf 12.4.2. Python dependencies are locked with their
hashes. The published site is static.

From this repository's root, prepare the core checkout at the manifest
commit, then run the same complete build as CI:

```sh
core_repository=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='roukmoute/pdf')['repository'])")
core_revision=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='roukmoute/pdf')['revision'])")
core_alias=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='roukmoute/pdf')['version'].rsplit('.', 1)[0]+'.x-dev')")
opentype_repository=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='pdftoolkit/opentype')['repository'])")
opentype_revision=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='pdftoolkit/opentype')['revision'])")

git clone "$core_repository" _sources/pdf
git -C _sources/pdf checkout --detach "$core_revision"
COMPOSER_ROOT_VERSION="$core_alias" composer install --working-dir=_sources/pdf --no-interaction --prefer-dist
git clone "$opentype_repository" _sources/opentype
git -C _sources/opentype checkout --detach "$opentype_revision"
composer install --working-dir=_sources/opentype --no-interaction --prefer-dist
html_repository=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='pdftoolkit/pdf-to-html')['repository'])")
html_revision=$(python -c "import json; print(next(p for p in json.load(open('resources/sources.json'))['packages'] if p['name']=='pdftoolkit/pdf-to-html')['revision'])")
git clone "$html_repository" _sources/pdf-to-html
git -C _sources/pdf-to-html checkout --detach "$html_revision"
composer install --working-dir=_sources/pdf-to-html --no-interaction --prefer-dist
python -m pip install --require-hashes -r tools/site-requirements.txt
python -m pip install --require-hashes -r _sources/pdf/tools/public-key-validation-requirements.txt
python -m pip install --require-hashes -r _sources/pdf-to-html/tools/validation-requirements.txt
python tools/build_docs.py --source-root _sources/pdf --opentype-root _sources/opentype --pdf-to-html-root _sources/pdf-to-html --docs-revision "$(git rev-parse HEAD)" --remote
```

On PowerShell:

```powershell
$sourceManifest = Get-Content resources/sources.json -Raw | ConvertFrom-Json
$coreSource = $sourceManifest.packages | Where-Object name -eq 'roukmoute/pdf'
$opentypeSource = $sourceManifest.packages | Where-Object name -eq 'pdftoolkit/opentype'
git clone $coreSource.repository _sources/pdf
git -C _sources/pdf checkout --detach $coreSource.revision
$env:COMPOSER_ROOT_VERSION = ($coreSource.version -replace '\.\d+$', '.x-dev')
composer install --working-dir=_sources/pdf --no-interaction --prefer-dist
git clone $opentypeSource.repository _sources/opentype
git -C _sources/opentype checkout --detach $opentypeSource.revision
composer install --working-dir=_sources/opentype --no-interaction --prefer-dist
$htmlSource = $sourceManifest.packages | Where-Object name -eq 'pdftoolkit/pdf-to-html'
git clone $htmlSource.repository _sources/pdf-to-html
git -C _sources/pdf-to-html checkout --detach $htmlSource.revision
composer install --working-dir=_sources/pdf-to-html --no-interaction --prefer-dist
python -m pip install --require-hashes -r tools/site-requirements.txt
python -m pip install --require-hashes -r _sources/pdf/tools/public-key-validation-requirements.txt
python -m pip install --require-hashes -r _sources/pdf-to-html/tools/validation-requirements.txt
$docsRevision = git rev-parse HEAD
python tools/build_docs.py --source-root _sources/pdf --opentype-root _sources/opentype --pdf-to-html-root _sources/pdf-to-html --docs-revision $docsRevision --remote
```

`tools/build_docs.py` verifies published commits and tags, retained sources
and normative generations. It exports the API, executes all examples,
checks their PDFs with qpdf and independent readers, renders every page,
builds the site and checks its links. `--docs-revision` expects the complete
40-character SHA of the documentation commit; it does not replace package
revisions in the manifest. Tool paths can be specified with `--php`,
`--qpdf`, `--openssl` and `--pdftoppm`.

To rebuild only the rendering from already-validated inputs:

```sh
php tools/export_api.php _build/api.json _sources/pdf resources/sources.json _sources/opentype _sources/pdf-to-html
python tools/build_site.py --content-root . --source-root _sources/pdf --opentype-root _sources/opentype --pdf-to-html-root _sources/pdf-to-html --sources resources/sources.json --docs-revision "$(git rev-parse HEAD)" --api _build/api.json --pdf-dir _build/pdfs --pdf-preview-dir _build/pdf-pages --output _site --base-path /
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

## Documentation languages

English is published at the root; French pages are under `/fr/`. Shared English
Markdown lives in `docs/en/`; the original `docs/` guides are French. Packages
keep English guides alongside their code and French counterparts in `docs/fr/`
or `README.fr.md`, `SECURITY.fr.md` and `CHANGELOG.fr.md`.

Add or update both translations together, keeping the same heading hierarchy.
`tools/localization.py` owns explicit interface translations and locale routes.
The builder pairs heading IDs for the language selector, preserves old French
section links, and records the actual translated source path and hash. PDF
examples and original references are shared unchanged by both languages.

Run `node tests/site_locales.cjs` and the full site checker. They verify the
language switch, search filters, section anchors, clipboard messages, each
locale's API inventory, reciprocal alternates and compatibility routes.

## HTML derivation inputs

The optional `--node` argument selects the Node executable and defaults to
`node`. The harness also receives the selected `--php` for its fixture
subprocesses instead of relying on a different PHP on PATH. Rendering oracles
use the selected `--pdftoppm`. The default profile and site frames execute no
runtime; explicitly enabled cases are checked in the private validation
workspace. Every module guide retains its EN/FR counterpart.

The released PDF-to-HTML checkout under `_sources/pdf-to-html` is selected independently. Its locked core and reader must match `resources/sources.json`; the selected reader comes from this checkout’s vendor directory, while the core’s original lock stays unchanged. The API exporter registers only the selected HTML and reader namespaces against their chosen trees. Module guides appear under `/modules/to-html/` in both languages. Tutorial 35 copies the input PDF, renders every page and runs the module CLI to produce actual HTML plus JSON diagnostics. `derivedHtml` inventories output HTML separately from documentation routes, with package/SHA provenance and sandboxed frames; the site checker rejects active content in these previews. The supplied 74-page original remains in the package and is linked at its selected release commit.
