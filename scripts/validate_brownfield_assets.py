#!/usr/bin/env python3
"""Validate brownfield/spec assets that can run in hosted CI."""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from json import JSONDecodeError
from pathlib import Path


VALID_ROLES = {"core", "edge"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_manifest(repo_root: Path) -> dict:
    manifest_path = repo_root / "brownfield/fixtures/manifest.json"
    require(manifest_path.exists(), f"missing manifest: {manifest_path}")
    with manifest_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_required_paths(repo_root: Path, manifest: dict) -> None:
    seen = set()
    for relative_path in manifest.get("required_paths", []):
        require(relative_path not in seen, f"duplicate required path: {relative_path}")
        seen.add(relative_path)
        require((repo_root / relative_path).exists(), f"missing required path: {relative_path}")


def validate_fixtures(repo_root: Path, manifest: dict) -> int:
    seen_names = set()
    fixture_count = 0
    for fixture in manifest.get("fixtures", []):
        fixture_count += 1
        name = fixture["name"]
        require(name not in seen_names, f"duplicate fixture name: {name}")
        seen_names.add(name)
        require(fixture["role"] in VALID_ROLES, f"invalid role for fixture {name}: {fixture['role']}")
        service_families = fixture.get("serviceFamilies", [])
        require(service_families, f"fixture {name} must declare at least one service family")
        fixture_path = repo_root / fixture["path"]
        require(fixture_path.exists(), f"fixture {name} path missing: {fixture['path']}")
        require(fixture_path.suffix == ".xml", f"fixture {name} is not xml: {fixture['path']}")
        ET.parse(fixture_path)
    return fixture_count


def validate_specs(repo_root: Path, manifest: dict) -> int:
    seen_ids = set()
    spec_count = 0
    for spec in manifest.get("specs", []):
        spec_count += 1
        spec_id = spec["id"]
        require(spec_id not in seen_ids, f"duplicate spec id: {spec_id}")
        seen_ids.add(spec_id)
        spec_path = repo_root / spec["path"]
        require(spec_path.exists(), f"missing spec file: {spec['path']}")
        content = spec_path.read_text(encoding="utf-8")
        for heading in spec.get("requiredHeadings", []):
            require(heading in content, f"spec {spec_id} missing heading: {heading}")
    return spec_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Path to repository root",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()

    try:
        manifest = load_manifest(repo_root)
        validate_required_paths(repo_root, manifest)
        fixture_count = validate_fixtures(repo_root, manifest)
        spec_count = validate_specs(repo_root, manifest)
    except (ValueError, FileNotFoundError, JSONDecodeError, ET.ParseError) as exc:
        print(f"brownfield asset validation failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"brownfield asset validation passed: "
        f"{fixture_count} fixtures, {spec_count} specs, {len(manifest.get('required_paths', []))} required paths"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
