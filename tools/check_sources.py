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
    require(len(records) == len(packages) and set(packages) == set(PACKAGES), "Four unique PDFToolkit packages are required")
    for name, item in packages.items():
        require(item["repository"] == PACKAGES[name], f"Unexpected source repository: {name}")
        require(re.fullmatch(r"[0-9a-f]{40}", item["revision"]) is not None, f"Source must be an exact commit: {name}")
        require(re.fullmatch(r"\d+\.\d+\.\d+", item["version"]) is not None, f"Source must be a stable release: {name}")
        require(item["optional"] is (name != "roukmoute/pdf"), f"Incorrect package boundary: {name}")
    return packages


def check(source_root: Path, manifest: Path, remote: bool = False) -> dict[str, dict]:
    packages = load_manifest(manifest)
    core = packages["roukmoute/pdf"]
    require(git("rev-parse", "HEAD", root=source_root) == core["revision"], "Core checkout does not match the released source pin")
    require(git("rev-parse", f"v{core['version']}^{{commit}}", root=source_root) == core["revision"], "Core tag does not identify the pinned commit")
    lock = json.loads((source_root / "composer.lock").read_text(encoding="utf-8"))
    locked = {item["name"]: item for item in lock["packages"] + lock["packages-dev"]}
    installed_manifest = json.loads((source_root / "vendor/composer/installed.json").read_text(encoding="utf-8"))
    installed = {item["name"]: item for item in installed_manifest["packages"]}
    for name, source in packages.items():
        if name != "roukmoute/pdf":
            for label, inventory in (("lock", locked), ("installed", installed)):
                require(name in inventory, f"Missing {label} source: {name}")
                record = inventory[name]
                require(record["version"].removeprefix("v") == source["version"], f"{label} release differs: {name}")
                require(record["source"]["reference"] == source["revision"], f"{label} source commit differs: {name}")
                require(record["dist"]["reference"] == source["revision"], f"{label} distribution commit differs: {name}")
            require((source_root / "vendor" / name / "docs").is_dir(), f"Missing module guide sources: {name}")
        if remote:
            tag = f"refs/tags/v{source['version']}"
            references = dict(line.split("\t", 1)[::-1] for line in git("ls-remote", source["repository"], tag, tag + "^{}").splitlines())
            require(references.get(tag + "^{}", references.get(tag)) == source["revision"], f"Published tag differs: {name}")
    print("Verified four released package pins and the installed module inputs.")
    return packages


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).resolve().parents[1] / "resources/sources.json")
    parser.add_argument("--remote", action="store_true", help="Also verify every published remote tag")
    parser.add_argument("--github-output", type=Path, help="Export the core checkout inputs for GitHub Actions")
    args = parser.parse_args()
    if args.github_output:
        core = load_manifest(args.manifest)["roukmoute/pdf"]
        with args.github_output.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(f"core_revision={core['revision']}\ncore_version={core['version']}\ncore_alias={'.'.join(core['version'].split('.')[:2])}.x-dev\n")
    else:
        check(args.source_root.resolve(), args.manifest.resolve(), args.remote)
