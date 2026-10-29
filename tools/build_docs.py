"""Generate and independently validate the PDFToolkit documentation inputs and site."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from check_sources import check, html_dependencies, select_reader, execution_dependencies
from html_demo import DemoBuild, DemoSource
from build_site import CORE_PACKAGE, MODULES, guide_pages
from guide_headings import translated_anchors


def executable_path(value: str | Path | None) -> str | None:
    """Anchor explicit paths before changing cwd, without resolving venv symlinks."""
    if value is None:
        return None
    value = os.path.expanduser(str(value))
    if os.path.dirname(value):
        return os.path.abspath(value)
    return value


def prepare_executables(args) -> None:
    for name in ('php', 'node', 'qpdf', 'openssl', 'pdftoppm', 'image_pdftoppm',
                 'imagemagick', 'pdftotext', 'ghostscript', 'poppler_glib_bin'):
        setattr(args, name, executable_path(getattr(args, name)))


def run(command: list, cwd: Path, output: Path | None = None, env: dict[str, str] | None = None) -> None:
    if output:
        with output.open("wb") as stream:
            subprocess.run(list(map(str, command)), cwd=cwd, check=True, stdout=stream, env=env)
    else:
        subprocess.run(list(map(str, command)), cwd=cwd, check=True, env=env)


def prepare_reader_oracle_autoload(reader: Path, consumer: Path) -> None:
    """Bind installed-package CLI reporters to the real locked consumer loader."""
    autoload = consumer / "vendor/autoload.php"
    if not autoload.is_file():
        raise ValueError("The selected Reader consumer must have its locked vendor autoloader")
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


def validate_image_and_font_modules(args, source: Path, opentype: Path, codecs: Path, images: Path, work: Path) -> None:
    fonts = source / 'vendor/pdftoolkit/pdf-fonts'
    prepare_reader_oracle_autoload(fonts, source)
    for tool in ('validate_png.py', 'validate_png_color.py', 'validate_jpeg.py'):
        command = [sys.executable, 'tools/' + tool, '--php', args.php,
                   '--qpdf', args.qpdf, '--pdftoppm', args.image_pdftoppm or args.pdftoppm,
                   '--report', work / (tool.removesuffix('.py') + '.json')]
        if tool != 'validate_jpeg.py':
            command.extend(['--imagemagick', args.imagemagick])
        run(command, images)
    run([sys.executable, 'tools/validate_opentype.py', '--php', args.php,
         '--output', work / 'font-layout-validation'], fonts)
    for tool in ('validate_cmaps.py', 'validate_collections.py', 'validate_feature_parameters.py', 'validate_feature_ranges.py'):
        run([sys.executable, 'tools/' + tool, '--php', args.php], opentype)
    for codec in ('jpeg', 'jbig2'):
        run([sys.executable, 'tools/validate_' + codec + '.py', '--php', args.php,
             '--report', work / (codec + '-codec-validation.json')], codecs)
    run([sys.executable, 'tools/build_jpx_oracle.py', '--output', work / 'openjpeg-oracle'], codecs)
    run([sys.executable, 'tools/validate_jpx.py', '--php', args.php,
         '--oracle', work / 'openjpeg-oracle/jpx-oracle', '--output', work / 'jpx-codec-validation'], codecs)


def validate_html_module(args, html: Path, work: Path, pdfs: Path) -> None:
    """Exercise released module behavior without adding validation outputs to site assets."""
    for command in (
        [sys.executable, "tools/validate_reference.py"],
        [sys.executable, "tools/build_reading_fixture.py", "--check"],
        [sys.executable, "tools/build_glyph_list.py", "--check"],
        [sys.executable, "tools/build_inline_fixture.py", "--check"],
        [sys.executable, "tools/build_inline_fax_fixture.py", "--check"],
        [sys.executable, "tools/build_sample_images_fixture.py", "--check"],
        [sys.executable, "tools/build_codec_image_sources.py", "--check"],
        [sys.executable, "tools/build_codec_images_fixture.py", "--check"],
        [sys.executable, "tools/validate_codec_images.py", "--php", args.php,
         "--qpdf", args.qpdf, "--export", work / "html-codec-images",
         "--report", work / "html-codec-images-validation.json"],
        [sys.executable, "tools/validate_sample_images.py", "--php", args.php,
         "--qpdf", args.qpdf, "--pdftoppm", args.pdftoppm,
         "--report", work / "html-sample-images-validation.json"],
        [sys.executable, "tools/validate_inline_derivation.py", "--php", args.php],
        [sys.executable, "tools/validate_graphics.py", "--php", args.php, "--pdftoppm", args.pdftoppm],
        [sys.executable, "tools/validate_graphics_context.py", "--php", args.php, "--pdftoppm", args.pdftoppm],
        [sys.executable, "tools/validate_appearances.py", "--php", args.php, "--pdftoppm", args.pdftoppm,
         "--work-dir", work / "html-appearances"],
        [sys.executable, "tools/validate_signatures.py", "--php", args.php,
         "--report", work / "html-signatures/report.json"],
        [sys.executable, "tools/validate_inline_fax.py", "--php", args.php, "--pdftoppm", args.pdftoppm],
        [sys.executable, "tools/validate_derivation.py", "--php", args.php],
        [sys.executable, "tools/validate_authentication.py", "--php", args.php, "--qpdf", args.qpdf],
        [sys.executable, "tools/validate_source_integrity.py", "--php", args.php, "--qpdf", args.qpdf,
         "--work-dir", work / "html-source-integrity"],
        [sys.executable, "tools/validate_public_key_authentication.py", "--php", args.php],
    ):
        run(command, html)
    # Reuse the demo's locked Playwright installation for both browser engines.
    # Keep module discovery explicit when the HTML checkout has no node_modules.
    run([args.node, html / "tools/validate_codec_images.cjs", work / "html-codec-images",
         work / "html-codec-images-browsers"], html,
        env={**os.environ, "NODE_PATH": str(args.demo_root.absolute() / "node_modules")})
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
    run([args.php, html / "examples/05-verify-pdf-signature.php",
         html / "tests/Fixtures/signatures/signed-padded.pdf", html / "tests/Fixtures/signatures/signer.der",
         examples / "signed.html"], html)


def build(args) -> None:
    prepare_executables(args)
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
    codecs = args.codecs_root.resolve()
    images = args.images_root.resolve()
    packages = check(source, manifest, args.remote, opentype, html, codecs, images)
    reader_consumer = select_reader(source, html, packages)
    reader = reader_consumer / "vendor/pdftoolkit/pdf-reader"
    guide_roots = {name: source / 'vendor' / name for name in MODULES}
    guide_roots.update({'documentation': content, CORE_PACKAGE: source,
                        'pdftoolkit/pdf-reader': reader, 'pdftoolkit/pdf-images': images,
                        'pdftoolkit/opentype': opentype, 'pdftoolkit/pdf-codecs': codecs,
                        'pdftoolkit/pdf-to-html': html})
    anchors = translated_anchors(guide_pages(), guide_roots)
    (work / 'guide-headings-validation.json').write_text(json.dumps({
        'status': 'pass', 'pairs': len(anchors), 'routes': sorted(anchors),
    }, indent=2) + '\n', encoding='utf-8')
    (work / "validation-sources.json").write_text(json.dumps({
        "executionDependencies": execution_dependencies(source, images, html, packages),
        "documentedReader": packages["pdftoolkit/pdf-reader"],
        "readerConsumer": str(reader_consumer),
        "readerCore": packages["roukmoute/pdf"] if reader_consumer == source else html_dependencies(html)[0],
        "htmlPackage": packages["pdftoolkit/pdf-to-html"],
        "htmlValidationDependencies": html_dependencies(html),
    }, indent=2) + "\n", encoding="utf-8")
    run([sys.executable, "-m", "unittest", "discover", "-s", content / "tests", "-p", "test_*.py"], content, env={**os.environ, "PDFTOOLKIT_TEST_PHP": args.php})
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
    prepare_reader_oracle_autoload(reader, reader_consumer)
    run([sys.executable, "tools/validate_source_mac.py", "--php", args.php, "--qpdf", args.qpdf,
         "--work-dir", work / "source-mac-validation"], reader)
    run([sys.executable, "tools/validate_metadata_security.py", "--php", args.php, "--qpdf", args.qpdf], reader)
    run([sys.executable, "tools/validate_public_key_authentication.py", "--php", args.php,
         "--work-dir", work / "public-key-validation"], reader)
    run([sys.executable, "tools/validate_public_key_aliases.py", "--php", args.php,
         "--work-dir", work / "public-key-alias-validation",
         "--fixtures-dir", work / "public-key-validation"], reader)
    run([sys.executable, "tools/validate_revision_history.py", "--php", args.php, "--qpdf", args.qpdf,
         "--work-dir", work / "reader-revision-history-validation"], reader)
    run([sys.executable, "tools/validate_external_streams.py", "--php", args.php, "--qpdf", args.qpdf,
         "--work-dir", work / "reader-external-streams-validation"], reader)
    run([sys.executable, "tools/validate_import.py", "--php", args.php, "--qpdf", args.qpdf,
         "--work-dir", work / "reader-import-validation", "--report", work / "reader-import-validation.json"], reader)
    run([sys.executable, "tools/validate_fax.py", "--php", args.php, "--qpdf", args.qpdf,
         "--pdftoppm", args.pdftoppm, "--report", work / "reader-fax-validation.json"], reader)
    run([sys.executable, "tools/validate_image_codecs.py", "--php", args.php,
         "--qpdf", args.qpdf, "--require-native",
         "--report", work / "reader-image-codecs-validation.json"], reader)
    validate_image_and_font_modules(args, source, opentype, codecs, images, work)
    validate_html_module(args, html, work, pdfs)
    demo = args.demo_root.resolve()
    demo_build = work / 'html-demo'
    demo_source = DemoSource.load(content / 'resources/demo-source.json')
    DemoBuild(demo_source, demo, sys.executable, args.php, args.pdftoppm, args.node).run(demo_build, html, args.remote)
    run([sys.executable, "tools/validate_demo.py", demo_build, "--report", work / "html-demo-validation.json",
         "--pdftoppm", args.pdftoppm, "--require-release"], demo)
    api = work / "api.json"
    run([args.php, content / "tools/export_api.php", api, source, manifest, opentype, html, reader_consumer, codecs, images], source)
    for example in sorted((source / "examples").glob("*.php")):
        output = pdfs / (example.stem + ".pdf")
        run([args.php, example, output, *([args.openssl] if example.stem == 'pdf20-timestamp-dss' else [])], source)
        run([args.qpdf, "--check", output], source)
        run([args.pdftoppm, "-r", "96", "-png", output, previews / example.stem], source)
    module = reader
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
    run([sys.executable, "tools/validate_pdf20_metadata.py", "--php", args.php, "--qpdf", args.qpdf, "--work-dir", work / "pdf20-metadata", "--pdftoppm", args.pdftoppm], source)
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
    run([sys.executable, "tools/validate_type3_resources.py", "--php", args.php, "--qpdf", args.qpdf,
         "--pdftoppm", args.pdftoppm, "--ghostscript", args.ghostscript,
         "--work-dir", work / "type3-resource-validation"], source)
    run([sys.executable, "tools/validate_annotation_appearances.py", "--php", args.php, "--qpdf", args.qpdf,
         "--pdftoppm", args.pdftoppm, "--work-dir", work / "annotation-appearance-validation"], source)
    run([sys.executable, "tools/validate_incremental_permissions.py", "--php", args.php, "--qpdf", args.qpdf,
         "--pdftoppm", args.pdftoppm, "--work-dir", work / "incremental-permissions-validation"], source)
    run([sys.executable, "tools/validate_encrypted_usage_rights.py", "--php", args.php, "--qpdf", args.qpdf,
         "--work-dir", work / "encrypted-usage-rights-validation"], source)
    for tool in ('validate_page_outlines.py', 'validate_action_contracts.py'):
        run([sys.executable, 'tools/' + tool, '--php', args.php,
             '--report', work / (tool.removesuffix('.py') + '.json')], source)
    run([sys.executable, 'tools/validate_calculator_functions.py', '--php', args.php,
         '--ghostscript', args.ghostscript, '--report', work / 'calculator-functions-validation.json'], source)
    run([sys.executable, content / "tools/build_site.py", "--content-root", content, "--source-root", source,
         "--opentype-root", opentype, "--codecs-root", codecs, "--images-root", images, "--pdf-to-html-root", html, "--demo-root", demo, "--demo-build", demo_build, "--sources", manifest, "--api", api, "--pdf-dir", pdfs, "--pdf-preview-dir", previews,
         "--output", args.output.resolve(), "--base-path", "/", "--docs-revision", args.docs_revision], content)
    run([sys.executable, content / "tools/check_site.py", args.output.resolve()], content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--opentype-root", type=Path, required=True, help="Independent released OpenType checkout")
    parser.add_argument("--images-root", type=Path, required=True, help="Separate released Images checkout and its own locked core")
    parser.add_argument("--codecs-root", type=Path, required=True, help="Independent released image codecs checkout")
    parser.add_argument("--pdf-to-html-root", type=Path, required=True, help="Released PDF-to-HTML checkout and its locked reader")
    parser.add_argument("--demo-root", type=Path, required=True, help="Separately released browser demo checkout")
    parser.add_argument("--sources", type=Path)
    parser.add_argument("--work-dir", type=Path, default=Path("_build"))
    parser.add_argument("--output", type=Path, default=Path("_site"))
    parser.add_argument("--docs-revision", required=True)
    parser.add_argument("--php", default="php")
    parser.add_argument("--node", default="node", help="Node executable for the released HTML module's runtime oracle")
    parser.add_argument("--qpdf", default="qpdf")
    parser.add_argument("--openssl", default=shutil.which("openssl"), help="Explicit OpenSSL executable for offline signature/timestamp examples and oracles")
    parser.add_argument("--pdftoppm", default="pdftoppm")
    parser.add_argument("--image-pdftoppm", help="Pinned Poppler renderer for the Images colour-management corpus")
    parser.add_argument("--imagemagick", default="convert")
    parser.add_argument("--pdftotext", default="pdftotext")
    parser.add_argument("--ghostscript", default="gs")
    parser.add_argument("--poppler-glib-bin", type=Path)
    parser.add_argument("--remote", action="store_true")
    options = parser.parse_args()
    if options.openssl is None:
        parser.error("Select the offline OpenSSL executable with --openssl.")
    build(options)
