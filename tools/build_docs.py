"""Generate and independently validate the PDFToolkit documentation inputs and site."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

from check_sources import check


def run(command: list, cwd: Path, output: Path | None = None, env: dict[str, str] | None = None) -> None:
    if output:
        with output.open("wb") as stream:
            subprocess.run(list(map(str, command)), cwd=cwd, check=True, stdout=stream, env=env)
    else:
        subprocess.run(list(map(str, command)), cwd=cwd, check=True, env=env)


def prepare_reader_oracle_autoload(reader: Path, html: Path) -> None:
    """Bind installed-package CLI reporters to the real locked consumer loader."""
    autoload = html / "vendor/autoload.php"
    if not autoload.is_file():
        raise ValueError("The released HTML checkout must have its locked vendor autoloader")
    directory = reader / "vendor"
    directory.mkdir(exist_ok=True)
    bridge = directory / "autoload.php"
    escaped = autoload.as_posix().replace("\\", "\\\\").replace("'", "\\'")
    contents = (
        "<?php\n\n// Documentation validation only: reuse the actual locked consumer.\n"
        f"return require '{escaped}';\n"
    )
    if bridge.exists() and bridge.read_text(encoding="utf-8") != contents:
        raise ValueError("Refusing to replace an existing reader validation autoloader")
    bridge.write_text(contents, encoding="utf-8", newline="\n")


def validate_html_module(args, html: Path, work: Path, pdfs: Path) -> None:
    """Exercise released module behavior without adding validation outputs to site assets."""
    for command in (
        [sys.executable, "tools/validate_reference.py"],
        [sys.executable, "tools/build_reading_fixture.py", "--check"],
        [sys.executable, "tools/build_glyph_list.py", "--check"],
        [sys.executable, "tools/build_inline_fixture.py", "--check"],
        [sys.executable, "tools/build_inline_fax_fixture.py", "--check"],
        [sys.executable, "tools/validate_inline_derivation.py", "--php", args.php],
        [sys.executable, "tools/validate_graphics.py", "--php", args.php, "--pdftoppm", args.pdftoppm],
        [sys.executable, "tools/validate_graphics_context.py", "--php", args.php, "--pdftoppm", args.pdftoppm],
        [sys.executable, "tools/validate_inline_fax.py", "--php", args.php, "--pdftoppm", args.pdftoppm],
        [sys.executable, "tools/validate_derivation.py", "--php", args.php],
        [sys.executable, "tools/validate_authentication.py", "--php", args.php, "--qpdf", args.qpdf],
        [sys.executable, "tools/validate_source_integrity.py", "--php", args.php, "--qpdf", args.qpdf,
         "--work-dir", work / "html-source-integrity"],
        [sys.executable, "tools/validate_public_key_authentication.py", "--php", args.php],
    ):
        run(command, html)
    runtime = work / "pdf-html-runtime.js"
    run([args.php, html / "tests/Script/runtime-fixture.php"], html, runtime)
    run([args.node, "--check", runtime], html)
    run([args.node, html / "tests/Script/runtime.cjs", runtime], html,
        env={**os.environ, "PDF_RUNTIME_TEST_PHP": str(args.php)})
    identifiers = work / "page-identifiers.json"
    run([args.php, html / "tests/export-page-identifiers.php"], html, identifiers)
    run([sys.executable, "tools/validate_page_identifiers.py", identifiers], html)
    examples = pdfs / "html-validation"
    examples.mkdir(exist_ok=True)
    figure = examples / "figure.pdf"
    run([args.php, html / "examples/02-export-figure.php", html / "tests/Fixtures/tagged.pdf", figure], html)
    run([args.qpdf, "--check", figure], html)
    run([args.php, html / "examples/03-safe-form-reset.php", examples / "safe-reset.html"], html)
    run([args.php, html / "examples/04-authenticate-source-mac.php",
         html / "tests/Fixtures/source-integrity/tagged-mac-r6-standalone.pdf", examples / "authenticated.html"],
        html, env={**os.environ, "PDFTOOLKIT_PASSWORD": "native-user"})


def build(args) -> None:
    content = args.content_root.resolve()
    source = args.source_root.resolve()
    work = args.work_dir.resolve()
    work.mkdir(parents=True, exist_ok=True)
    pdfs, previews = work / "pdfs", work / "pdf-pages"
    pdfs.mkdir(exist_ok=True)
    previews.mkdir(exist_ok=True)
    manifest = args.sources.resolve() if args.sources else content / "resources/sources.json"
    opentype = args.opentype_root.resolve()
    html = args.pdf_to_html_root.resolve()
    check(source, manifest, args.remote, opentype, html)
    run([sys.executable, "-m", "unittest", "discover", "-s", content / "tests", "-p", "test_*.py"], content)
    for command in (
        [sys.executable, "tools/generate_specification.py", "--check"],
        [sys.executable, "tools/generate_adobe_supplement.py", "--check"],
        [sys.executable, "tools/generate_iso32000_2.py", "--check"],
        [sys.executable, "tools/compile_iso32000_2_catalogue.py", "--check"],
        [sys.executable, "tools/build_saslprep_tables.py", "--check"],
        [sys.executable, "tools/validate_adobe_references.py"],
        [sys.executable, "tools/validate_ec3_semantic_reviews.py"],
        [sys.executable, "tools/validate_iso32000_bundle.py"],
        [sys.executable, "tools/generate_structure_inclusion.py", "--check"],
        [sys.executable, "tools/check_wtpdf_requirements.py"],
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_wtpdf_requirements.py"],
    ):
        run(command, source)
    reader = html / "vendor/pdftoolkit/pdf-reader"
    prepare_reader_oracle_autoload(reader, html)
    run([sys.executable, "tools/validate_source_mac.py", "--php", args.php, "--qpdf", args.qpdf,
         "--work-dir", work / "source-mac-validation"], reader)
    run([sys.executable, "tools/validate_metadata_security.py", "--php", args.php, "--qpdf", args.qpdf], reader)
    run([sys.executable, "tools/validate_public_key_authentication.py", "--php", args.php,
         "--work-dir", work / "public-key-validation"], reader)
    run([sys.executable, "tools/validate_public_key_aliases.py", "--php", args.php,
         "--work-dir", work / "public-key-alias-validation",
         "--fixtures-dir", work / "public-key-validation"], reader)
    validate_html_module(args, html, work, pdfs)
    api = work / "api.json"
    run([args.php, content / "tools/export_api.php", api, source, manifest, opentype, html], source)
    for example in sorted((source / "examples").glob("*.php")):
        output = pdfs / (example.stem + ".pdf")
        run([args.php, example, output, *([args.openssl] if example.stem == 'pdf20-timestamp-dss' else [])], source)
        run([args.qpdf, "--check", output], source)
        run([args.pdftoppm, "-r", "96", "-png", output, previews / example.stem], source)
    module = html / "vendor/pdftoolkit/pdf-reader"
    output = pdfs / "reading-pages.pdf"
    shutil.copyfile(module / "tests/Fixtures/page-tree/classic.pdf", output)
    run([args.qpdf, "--check", output], source)
    run([args.php, module / "examples/pages.php", output], source, pdfs / "reading-pages.txt")
    run([args.pdftoppm, "-r", "96", "-png", output, previews / "reading-pages"], source)
    output = pdfs / "derive-html.pdf"
    shutil.copyfile(html / "tests/Fixtures/tagged.pdf", output)
    run([args.qpdf, "--check", output], source)
    run([args.php, html / "examples/01-derive-tagged-pdf.php", output, pdfs / "derive-html.html"], html, pdfs / "derive-html.txt")
    run([args.pdftoppm, "-r", "96", "-png", output, previews / "derive-html"], source)
    for validator in ("validate_mechanisms.py", "validate_adobe_supplement.py", "validate_pdf20_fonts.py"):
        run([sys.executable, "tools/" + validator, pdfs], source)
    run([sys.executable, "tools/validate_pdf20_foundations.py", "--php", args.php, "--qpdf", args.qpdf, "--example", pdfs / "pdf20-associated-files.pdf"], source)
    run([sys.executable, "tools/validate_pdf20_metadata.py", "--php", args.php, "--qpdf", args.qpdf, "--work-dir", work / "pdf20-metadata"], source)
    run([sys.executable, "tools/validate_iso32000_crypto.py", "--php", args.php, "--qpdf", args.qpdf, "--openssl", args.openssl, "--work-dir", work / "pdf20-crypto"], source)
    run([sys.executable, "tools/validate_pdf20_timestamps.py", "--php", args.php, "--qpdf", args.qpdf, "--openssl", args.openssl, "--work-dir", work / "pdf20-timestamps"], source)
    run([sys.executable, "tools/validate_pdf20_geospatial.py", "--php", args.php, "--qpdf", args.qpdf, "--work-dir", work / "pdf20-geospatial"], source)
    run([sys.executable, "tools/validate_pdf20_structure_destinations.py", "--php", args.php, "--qpdf", args.qpdf, "--work-dir", work / "pdf20-structure-destinations"], source)
    run([sys.executable, "tools/validate_public_key_security.py", "--php", args.php, "--pdf-version", "2.0"], source)
    poppler = ["--poppler-glib-bin", args.poppler_glib_bin] if args.poppler_glib_bin else ["--pdftotext", args.pdftotext]
    run([sys.executable, "tools/validate_pdf20_tagging.py", "--php", args.php, "--qpdf", args.qpdf, "--example", pdfs / "pdf20-tagged-namespaces.pdf", *poppler], source)
    run([sys.executable, "tools/validate_source_mechanisms.py", pdfs, "--php", args.php, "--qpdf", args.qpdf, *poppler], source)
    run([sys.executable, "tools/validate_secure_redaction.py", "--php", args.php, "--qpdf", args.qpdf,
         "--pdftoppm", args.pdftoppm, "--work-dir", work / "redaction-validation"], source)
    run([sys.executable, "tools/validate_barcode_appearances.py", "--php", args.php, "--qpdf", args.qpdf,
         "--pdftoppm", args.pdftoppm, "--work-dir", work / "barcode-validation"], source)
    run([sys.executable, "tools/validate_wtpdf_type3_usage.py", "--php", args.php, "--qpdf", args.qpdf,
         "--pdftoppm", args.pdftoppm, "--work-dir", work / "wtpdf-type3-validation"], source)
    run([sys.executable, "tools/validate_annotation_appearances.py", "--php", args.php, "--qpdf", args.qpdf,
         "--pdftoppm", args.pdftoppm, "--work-dir", work / "annotation-appearance-validation"], source)
    run([sys.executable, content / "tools/build_site.py", "--content-root", content, "--source-root", source,
         "--opentype-root", opentype, "--pdf-to-html-root", html, "--sources", manifest, "--api", api, "--pdf-dir", pdfs, "--pdf-preview-dir", previews,
         "--output", args.output.resolve(), "--base-path", "/", "--docs-revision", args.docs_revision], content)
    run([sys.executable, content / "tools/check_site.py", args.output.resolve()], content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--opentype-root", type=Path, required=True, help="Independent released OpenType checkout")
    parser.add_argument("--pdf-to-html-root", type=Path, required=True, help="Released PDF-to-HTML checkout and its locked reader")
    parser.add_argument("--sources", type=Path)
    parser.add_argument("--work-dir", type=Path, default=Path("_build"))
    parser.add_argument("--output", type=Path, default=Path("_site"))
    parser.add_argument("--docs-revision", required=True)
    parser.add_argument("--php", default="php")
    parser.add_argument("--node", default="node", help="Node executable for the released HTML module's runtime oracle")
    parser.add_argument("--qpdf", default="qpdf")
    parser.add_argument("--openssl", default=shutil.which("openssl"), help="Explicit OpenSSL executable for offline signature/timestamp examples and oracles")
    parser.add_argument("--pdftoppm", default="pdftoppm")
    parser.add_argument("--pdftotext", default="pdftotext")
    parser.add_argument("--poppler-glib-bin", type=Path)
    parser.add_argument("--remote", action="store_true")
    options = parser.parse_args()
    if options.openssl is None:
        parser.error("Select the offline OpenSSL executable with --openssl.")
    build(options)
