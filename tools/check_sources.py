"""Verify released PDFToolkit source pins and the installed documentation inputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess


PACKAGES = {
    "roukmoute/pdf": "https://github.com/PDFToolkit/pdf",
    "pdftoolkit/pdf-reader": "https://github.com/PDFToolkit/pdf-reader",
    "pdftoolkit/pdf-images": "https://github.com/PDFToolkit/pdf-images",
    "pdftoolkit/pdf-fonts": "https://github.com/PDFToolkit/pdf-fonts",
    "pdftoolkit/opentype": "https://github.com/PDFToolkit/opentype",
    "pdftoolkit/pdf-to-html": "https://github.com/PDFToolkit/pdf-to-html",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def git(*arguments: str, root: Path | None = None) -> str:
    command = ["git", *(["-C", str(root)] if root else []), *arguments]
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout.strip()


def load_manifest(path: Path) -> dict[str, dict]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    require(manifest["schemaVersion"] == 1, "Unsupported source manifest")
    records = manifest["packages"]
    packages = {item["name"]: item for item in records}
    require(len(records) == len(packages) and set(packages) == set(PACKAGES), "Every PDFToolkit package must appear exactly once")
    for name, item in packages.items():
        require(item["repository"] == PACKAGES[name], f"Unexpected source repository: {name}")
        require(re.fullmatch(r"[0-9a-f]{40}", item["revision"]) is not None, f"Source must be an exact commit: {name}")
        require(re.fullmatch(r"\d+\.\d+\.\d+", item["version"]) is not None, f"Source must be a stable release: {name}")
        require(item["optional"] is (name != "roukmoute/pdf"), f"Incorrect package boundary: {name}")
    return packages


def check(source_root: Path, manifest: Path, remote: bool = False, opentype_root: Path | None = None, pdf_to_html_root: Path | None = None) -> dict[str, dict]:
    packages = load_manifest(manifest)
    core = packages["roukmoute/pdf"]
    require(git("rev-parse", "HEAD", root=source_root) == core["revision"], "Core checkout does not match the released source pin")
    require(git("rev-parse", f"v{core['version']}^{{commit}}", root=source_root) == core["revision"], "Core tag does not identify the pinned commit")
    lock = json.loads((source_root / "composer.lock").read_text(encoding="utf-8"))
    locked = {item["name"]: item for item in lock["packages"] + lock["packages-dev"]}
    installed_manifest = json.loads((source_root / "vendor/composer/installed.json").read_text(encoding="utf-8"))
    installed = {item["name"]: item for item in installed_manifest["packages"]}
    require(pdf_to_html_root is not None, "The released PDF-to-HTML source checkout is required")
    html_lock = json.loads((pdf_to_html_root / "composer.lock").read_text(encoding="utf-8"))
    html_locked = {item["name"]: item for item in html_lock["packages"] + html_lock["packages-dev"]}
    html_installed_manifest = json.loads((pdf_to_html_root / "vendor/composer/installed.json").read_text(encoding="utf-8"))
    html_installed = {item["name"]: item for item in html_installed_manifest["packages"]}
    for name, source in packages.items():
        if name == "pdftoolkit/pdf-to-html":
            require(git("rev-parse", "HEAD", root=pdf_to_html_root) == source["revision"], "PDF-to-HTML checkout differs from the released source pin")
            require(git("rev-parse", f"v{source['version']}^{{commit}}", root=pdf_to_html_root) == source["revision"], "PDF-to-HTML tag differs from the released source pin")
            composer = json.loads((pdf_to_html_root / "composer.json").read_text(encoding="utf-8"))
            require(composer["name"] == name, "PDF-to-HTML source package identity differs")
            require((pdf_to_html_root / "docs").is_dir(), "Missing PDF-to-HTML guides")
            for dependency in ("roukmoute/pdf", "pdftoolkit/pdf-reader"):
                for label, inventory in (("lock", html_locked), ("installed", html_installed)):
                    record = inventory.get(dependency, {})
                    require(record.get("version", "").removeprefix("v") == packages[dependency]["version"], f"PDF-to-HTML {label} release differs: {dependency}")
                    require(record.get("source", {}).get("reference") == packages[dependency]["revision"] and record.get("dist", {}).get("reference") == packages[dependency]["revision"], f"PDF-to-HTML {label} commit differs: {dependency}")
        elif name == "pdftoolkit/opentype":
            require(opentype_root is not None, "The independent OpenType source checkout is required")
            require(git("rev-parse", "HEAD", root=opentype_root) == source["revision"], "OpenType checkout differs from the released source pin")
            require(git("rev-parse", f"v{source['version']}^{{commit}}", root=opentype_root) == source["revision"], "OpenType tag differs from the released source pin")
            composer = json.loads((opentype_root / "composer.json").read_text(encoding="utf-8"))
            require(composer["name"] == name, "Independent OpenType source package identity differs")
            require(not any(dependency == "roukmoute/pdf" or dependency.startswith("pdftoolkit/pdf-") for dependency in composer.get("require", {})), "OpenType must remain independent from PDF packages")
            require((opentype_root / "docs").is_dir(), "Missing OpenType guides")
        elif name != "roukmoute/pdf":
            selected_lock, selected_installed = (html_locked, html_installed) if name == "pdftoolkit/pdf-reader" else (locked, installed)
            module_root = pdf_to_html_root if name == "pdftoolkit/pdf-reader" else source_root
            for label, inventory in (("lock", selected_lock), ("installed", selected_installed)):
                require(name in inventory, f"Missing {label} source: {name}")
                record = inventory[name]
                require(record["version"].removeprefix("v") == source["version"], f"{label} release differs: {name}")
                require(record["source"]["reference"] == source["revision"], f"{label} source commit differs: {name}")
                require(record["dist"]["reference"] == source["revision"], f"{label} distribution commit differs: {name}")
            require((module_root / "vendor" / name / "docs").is_dir(), f"Missing module guide sources: {name}")
        if remote:
            tag = f"refs/tags/v{source['version']}"
            references = dict(line.split("\t", 1)[::-1] for line in git("ls-remote", source["repository"], tag, tag + "^{}").splitlines())
            require(references.get(tag + "^{}", references.get(tag)) == source["revision"], f"Published tag differs: {name}")
    print(f"Verified {len(packages)} released package pins and their independent source inputs.")
    return packages


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--opentype-root", type=Path, help="Independent released OpenType checkout")
    parser.add_argument("--pdf-to-html-root", type=Path, help="Released PDF-to-HTML checkout with its locked reader")
    parser.add_argument("--manifest", type=Path, default=Path(__file__).resolve().parents[1] / "resources/sources.json")
    parser.add_argument("--remote", action="store_true", help="Also verify every published remote tag")
    parser.add_argument("--github-output", type=Path, help="Export the core checkout inputs for GitHub Actions")
    args = parser.parse_args()
    if args.github_output:
        packages = load_manifest(args.manifest)
        core = packages["roukmoute/pdf"]
        opentype = packages["pdftoolkit/opentype"]
        html = packages["pdftoolkit/pdf-to-html"]
        with args.github_output.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(f"opentype_revision={opentype['revision']}\nopentype_version={opentype['version']}\n")
            stream.write(f"pdf_to_html_revision={html['revision']}\npdf_to_html_version={html['version']}\n")
            stream.write(f"core_revision={core['revision']}\ncore_version={core['version']}\ncore_alias={'.'.join(core['version'].split('.')[:2])}.x-dev\n")
    else:
        check(args.source_root.resolve(), args.manifest.resolve(), args.remote, args.opentype_root.resolve() if args.opentype_root else None, args.pdf_to_html_root.resolve() if args.pdf_to_html_root else None)
