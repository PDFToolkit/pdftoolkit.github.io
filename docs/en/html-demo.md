# HTML gallery and local conversion

Explore real PDFs, their derived HTML, the PHP code that produces each example,
and the diagnostics that explain the result. The gallery keeps the input PDF,
rendered page previews, exact HTML source and byte hashes together. Its code lives
in the separately released [PDF-to-HTML demo](https://github.com/PDFToolkit/pdf-to-html-demo),
using the stable [HTML converter](https://pdftoolkit.github.io/modules/to-html/index.html).

## Convert a file on this device

Choose a PDF to run the PHP converter inside a browser Worker. The application
loads its PHP/WebAssembly runtime and dependencies from this site. It does not
send the chosen PDF, its filename, a password or the result to a server, and does
not save those values in browser storage. Loading the page and its public runtime
assets still makes ordinary requests to the site's host.

Each conversion has a fresh Worker. Cancel stops that Worker. Input size,
execution time and PHP memory are bounded; unsupported or invalid input produces
an error or diagnostics instead of a claim of complete conversion. The published
runtime currently accepts at most 8 MiB of PDF input, allows 30 seconds per
conversion and sets a 128 MiB PHP memory limit. Expanded preview documents are
also bounded to 16 million characters. Closing or reloading the page
clears the session. The converter is designed for tagged PDF: visual similarity
to an arbitrary untagged source is not guaranteed.

The displayed result is isolated from the documentation page. Imported PDFs do
not gain permission to execute scripts, submit forms or navigate the parent
page. Downloads are created locally when requested.

## Read the visual examples

The examples cover structure, tables and lists, MathML, form defaults and reset,
widget appearances, signature status and a rendered graphic. Compare the source
page preview with the derived HTML, then inspect the PHP example and diagnostics.
The HTML download contains the actual conversion output. A rendered PDF preview
is a visual reference, not evidence that an HTML layout is pixel-identical.

The gallery's explicit application capabilities are documented per example.
Graphics rasterization and signature verification require an implementation or
selected certificate; their demonstrated results do not imply that arbitrary
uploaded files receive those capabilities. A signature integrity result does not
establish certificate trust, validity at signing time or permission for later
changes. See the [graphics guide](https://pdftoolkit.github.io/modules/to-html/graphics.html)
and [signature guide](https://pdftoolkit.github.io/modules/to-html/signatures.html).

Only the published reset example enables the project's bounded reset runtime
inside its isolated preview. Its script is selected from the verified example
assets and authorized by its exact content hash. This implements the allowed
reset action; it does not execute PDF ECMAScript. Other gallery outputs and all imported files use a preview with
scripts disabled.

## Inspect and reproduce the output

Each card exposes the source PDF, HTML text, PHP code and diagnostic JSON. The
public gallery manifest records hashes and source identities. Without JavaScript,
the page still offers rendered previews and those downloads. The application and
runtime are pinned independently from the documentation and PHP packages.

For a PHP application, follow the
[executable conversion tutorial](https://pdftoolkit.github.io/tutorials/35-derive-html.html).
The [policies guide](https://pdftoolkit.github.io/modules/to-html/policies.html)
and [coverage guide](https://pdftoolkit.github.io/modules/to-html/coverage.html)
explain the interpretation choices and supported mechanisms.
