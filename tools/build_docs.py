"""Generate and independently validate the PDFToolkit documentation inputs and site."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

from check_sources import check


def run(command: list, cwd: Path, output: Path | None = None) -> None:
    if output:
        with output.open("wb") as stream:
            subprocess.run(list(map(str, command)), cwd=cwd, check=True, stdout=stream)
    else:
        subprocess.run(list(map(str, command)), cwd=cwd, check=True)


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
    check(source, manifest, args.remote, opentype)
    run([sys.executable, "-m", "unittest", "discover", "-s", content / "tests", "-p", "test_*.py"], content)
    for command in (
        [sys.executable, "tools/generate_specification.py", "--check"],
        [sys.executable, "tools/generate_adobe_supplement.py", "--check"],
        [sys.executable, "tools/generate_iso32000_2_pilot.py", "--check"],
        [sys.executable, "tools/build_saslprep_tables.py", "--check"],
        [sys.executable, "tools/validate_adobe_references.py"],
    ):
        run(command, source)
    api = work / "api.json"
    run([args.php, content / "tools/export_api.php", api, source, manifest, opentype], source)
    for example in sorted((source / "examples").glob("*.php")):
        output = pdfs / (example.stem + ".pdf")
        run([args.php, example, output], source)
        run([args.qpdf, "--check", output], source)
        run([args.pdftoppm, "-r", "96", "-png", output, previews / example.stem], source)
    module = source / "vendor/pdftoolkit/pdf-reader"
    output = pdfs / "reading-pages.pdf"
    shutil.copyfile(module / "tests/Fixtures/page-tree/classic.pdf", output)
    run([args.qpdf, "--check", output], source)
    run([args.php, module / "examples/pages.php", output], source, pdfs / "reading-pages.txt")
    run([args.pdftoppm, "-r", "96", "-png", output, previews / "reading-pages"], source)
    for validator in ("validate_mechanisms.py", "validate_adobe_supplement.py"):
        run([sys.executable, "tools/" + validator, pdfs], source)
    run([sys.executable, "tools/validate_pdf20_foundations.py", "--php", args.php, "--qpdf", args.qpdf, "--example", pdfs / "pdf20-associated-files.pdf"], source)
    run([sys.executable, "tools/validate_public_key_security.py", "--php", args.php, "--pdf-version", "2.0"], source)
    poppler = ["--poppler-glib-bin", args.poppler_glib_bin] if args.poppler_glib_bin else ["--pdftotext", args.pdftotext]
    run([sys.executable, "tools/validate_source_mechanisms.py", pdfs, "--php", args.php, "--qpdf", args.qpdf, *poppler], source)
    run([sys.executable, content / "tools/build_site.py", "--content-root", content, "--source-root", source,
         "--opentype-root", opentype, "--sources", manifest, "--api", api, "--pdf-dir", pdfs, "--pdf-preview-dir", previews,
         "--output", args.output.resolve(), "--base-path", "/", "--docs-revision", args.docs_revision], content)
    run([sys.executable, content / "tools/check_site.py", args.output.resolve()], content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--opentype-root", type=Path, required=True, help="Independent released OpenType checkout")
    parser.add_argument("--sources", type=Path)
    parser.add_argument("--work-dir", type=Path, default=Path("_build"))
    parser.add_argument("--output", type=Path, default=Path("_site"))
    parser.add_argument("--docs-revision", required=True)
    parser.add_argument("--php", default="php")
    parser.add_argument("--qpdf", default="qpdf")
    parser.add_argument("--pdftoppm", default="pdftoppm")
    parser.add_argument("--pdftotext", default="pdftotext")
    parser.add_argument("--poppler-glib-bin", type=Path)
    parser.add_argument("--remote", action="store_true")
    build(parser.parse_args())
