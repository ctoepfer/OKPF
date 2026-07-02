# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Command-line tools for the OKPF reference implementation."""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import shutil
import zipfile
from pathlib import Path
from typing import Any

from okpf_validate import Issue, ValidationResult, load_manifest, validate_pack
from okpf.demo import create_demo_pack, validate_demo_pack, inspect_pack_summary, run_eval_quiz
from okpf import scaffold
from okpf.scaffold import TemplateError

# Directories to exclude when packing a directory into a .kpack archive.
_EXCLUDE_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".venv",
    ".git",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
}
_EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".egg-info"}


def main() -> int:
    parser = argparse.ArgumentParser(prog="okpf", description="OKPF reference CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate an OKPF package")
    validate_parser.add_argument("pack_path")
    validate_parser.add_argument("--profile", help="Run optional validation for a named profile")
    validate_parser.add_argument(
        "--strict-profile",
        action="store_true",
        help="Treat profile validation warnings as errors",
    )

    inspect_parser = subparsers.add_parser("inspect", help="Inspect an OKPF package manifest")
    inspect_parser.add_argument("pack_path")
    info_parser = subparsers.add_parser("info", help="Show an OKPF package summary")
    info_parser.add_argument("pack_path")

    pack_parser = subparsers.add_parser("pack", help="Pack a directory into a .kpack archive")
    pack_parser.add_argument("pack_dir", help="Source pack directory")
    pack_parser.add_argument("output", help="Output .kpack file path")

    unpack_parser = subparsers.add_parser("unpack", help="Unpack a .kpack archive to a directory")
    unpack_parser.add_argument("kpack_file", help="Source .kpack file")
    unpack_parser.add_argument("output_dir", help="Output directory")
    unpack_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite output directory if it is not empty",
    )

    compare_parser = subparsers.add_parser(
        "compare-layout",
        help="Export an OKPF pack in alternative layouts for benchmark comparison",
    )
    compare_parser.add_argument("pack_dir", help="Source OKPF pack directory")
    compare_parser.add_argument("output_dir", help="Output directory for comparison exports")

    demo_parser = subparsers.add_parser("demo", help="Run an end-to-end OKPF demo")
    demo_parser.add_argument("source_file", help="Source Markdown or text file to demo")

    subparsers.add_parser("templates", help="List built-in okpf init templates")

    init_parser = subparsers.add_parser("init", help="Scaffold a new OKPF pack from a template")
    init_parser.add_argument("dest", help="Directory to create the pack in")
    init_parser.add_argument("--template", default="minimal", help="Template id (see `okpf templates`)")
    init_parser.add_argument("--package-id", dest="package_id", help="Override the template's default package_id")
    init_parser.add_argument("--name", help="Override the template's default name")
    init_parser.add_argument("--domain", help="Override the template's default domain")
    init_parser.add_argument("--license", dest="license_type", help="Override the template's default license type")
    init_parser.add_argument("--creator-name", dest="creator_name", help="Override the template's default creator name")
    init_parser.add_argument("--version", help="Override the template's default version")
    init_parser.add_argument("--force", action="store_true", help="Write into a non-empty destination directory")

    add_parser = subparsers.add_parser("add", help="Add a file to an OKPF pack's manifest")
    add_parser.add_argument("pack_dir", help="Pack directory containing manifest.json")
    add_parser.add_argument("file", help="File to add")
    add_parser.add_argument("--role", help="Artifact role, e.g. guide, source, reference")
    add_parser.add_argument("--type", dest="mime_type", help="MIME type, e.g. text/markdown")
    add_parser.add_argument("--title", help="Human-readable title")
    add_parser.add_argument("--description", help="Short description")
    add_parser.add_argument(
        "--section", choices=("artifacts", "records"), default="artifacts",
        help="Manifest section to add the entry to (default: artifacts)",
    )
    add_parser.add_argument("--force", action="store_true", help="Overwrite an existing entry with the same path")

    fix_parser = subparsers.add_parser("fix", help="Apply additive fixes for common validation issues")
    fix_parser.add_argument("pack_dir", help="Pack directory containing manifest.json")
    fix_parser.add_argument("--dry-run", action="store_true", help="Report changes without writing them")

    explain_parser = subparsers.add_parser("explain", help="Validate a pack and explain each issue in plain language")
    explain_parser.add_argument("pack_path")

    args = parser.parse_args()
    if args.command == "validate":
        return _validate(args.pack_path, args.profile, args.strict_profile)
    if args.command in {"inspect", "info"}:
        return _inspect(args.pack_path)
    if args.command == "pack":
        return _pack(args.pack_dir, args.output)
    if args.command == "unpack":
        return _unpack(args.kpack_file, args.output_dir, force=args.force)
    if args.command == "compare-layout":
        return _compare_layout(args.pack_dir, args.output_dir)
    if args.command == "demo":
        return _demo(args.source_file)
    if args.command == "templates":
        return _list_templates()
    if args.command == "init":
        return _init(
            args.dest,
            template_id=args.template,
            package_id=args.package_id,
            name=args.name,
            domain=args.domain,
            license_type=args.license_type,
            creator_name=args.creator_name,
            version=args.version,
            force=args.force,
        )
    if args.command == "add":
        return _add(
            args.pack_dir,
            args.file,
            role=args.role,
            mime_type=args.mime_type,
            title=args.title,
            description=args.description,
            section=args.section,
            force=args.force,
        )
    if args.command == "fix":
        return _fix(args.pack_dir, dry_run=args.dry_run)
    if args.command == "explain":
        return _explain(args.pack_path)
    parser.error(f"Unknown command: {args.command}")
    return 2


def _validate(pack_path: str, profile: str | None = None, strict_profile: bool = False) -> int:
    result = validate_pack(pack_path, profile=profile, strict_profile=strict_profile)
    if result.valid:
        name = result.package_id or pack_path
        print(f"OKPF package is valid: {name}")
        for issue in result.warnings:
            print(issue)
        return 0

    print(f"OKPF package is invalid: {pack_path}")
    for issue in result.errors:
        print(issue)
    for issue in result.warnings:
        print(issue)
    return 1


def _inspect(pack_path: str) -> int:
    manifest, errors = load_manifest(pack_path)
    if manifest is None:
        print(f"Could not inspect OKPF package: {pack_path}")
        for error in errors:
            print(f"[ERROR] {error}")
        return 1

    artifacts = _as_list(manifest.get("artifacts")) + _as_list(manifest.get("content"))
    records = _as_list(manifest.get("records"))
    profiles = _as_list(manifest.get("profiles"))
    license_value = manifest.get("license", {})
    usage_policy = manifest.get("usage_policy", {})
    legacy_fields = [
        field_name for field_name in ("id", "content")
        if field_name in manifest and {"id": "package_id", "content": "artifacts"}[field_name] not in manifest
    ]

    print(f"Name: {manifest.get('title') or manifest.get('name') or '(untitled)'}")
    print(f"Package ID: {manifest.get('package_id') or manifest.get('id') or '(none)'}")
    print(f"Version: {manifest.get('version') or '(none)'}")
    print(f"OKPF version: {manifest.get('okpf_version') or '(none)'}")
    print(f"Domain: {manifest.get('domain') or '(none)'}")
    print(f"Description: {manifest.get('description') or '(none)'}")
    print(f"Language: {manifest.get('language') or '(none)'}")
    print(f"Profiles: {', '.join(profiles) if profiles else '(none)'}")
    print(f"Artifact count: {len(artifacts)}")
    print(f"Record file count: {len(records)}")
    print(f"Legacy fields: {', '.join(legacy_fields) if legacy_fields else '(none)'}")
    print(f"License: {_summarize_license(license_value)}")
    print(f"Usage policy: {_summarize_usage_policy(usage_policy)}")
    return 0


def _pack(pack_dir: str, output: str) -> int:
    """Pack a directory into a .kpack ZIP archive."""
    source = Path(pack_dir).resolve()
    dest = Path(output)

    if not source.is_dir():
        print(f"[ERROR] Source is not a directory: {pack_dir!r}")
        return 1

    manifest_path = source / "manifest.json"
    if not manifest_path.is_file():
        print(f"[ERROR] No manifest.json found in {pack_dir!r}")
        return 1

    if dest.suffix != ".kpack":
        print(f"[WARNING] Output path does not end with .kpack: {output!r}")

    dest.parent.mkdir(parents=True, exist_ok=True)

    files_added = 0
    files_skipped = 0

    try:
        with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path in sorted(source.rglob("*")):
                if not file_path.is_file():
                    continue

                # Skip excluded directories anywhere in the path.
                rel = file_path.relative_to(source)
                parts = rel.parts
                if any(part in _EXCLUDE_DIRS for part in parts):
                    files_skipped += 1
                    continue
                if any(part.endswith(".egg-info") for part in parts):
                    files_skipped += 1
                    continue
                if file_path.suffix in _EXCLUDE_SUFFIXES:
                    files_skipped += 1
                    continue

                # Build a POSIX-style relative entry name.
                entry_name = "/".join(parts)

                # Final safety check — entry must be a safe relative path.
                if not _is_safe_archive_entry(entry_name):
                    print(f"[ERROR] Unsafe path would be included: {entry_name!r}")
                    return 1

                zf.write(file_path, entry_name)
                files_added += 1

    except OSError as exc:
        print(f"[ERROR] Could not write archive: {exc}")
        return 1

    print(f"Packed {files_added} file(s) into {dest}")
    if files_skipped:
        print(f"Skipped {files_skipped} file(s) in excluded directories.")
    return 0


def _unpack(kpack_file: str, output_dir: str, *, force: bool = False) -> int:
    """Unpack a .kpack ZIP archive to a directory."""
    source = Path(kpack_file)
    dest = Path(output_dir)

    if not source.is_file():
        print(f"[ERROR] Source file not found: {kpack_file!r}")
        return 1

    if source.suffix != ".kpack":
        print(f"[WARNING] Source file does not have .kpack extension: {kpack_file!r}")

    if dest.exists() and any(dest.iterdir()):
        if not force:
            print(f"[ERROR] Output directory is not empty: {output_dir!r}")
            print("Use --force to overwrite.")
            return 1

    try:
        with zipfile.ZipFile(source, "r") as zf:
            # Safety check: inspect all entries before extracting anything.
            unsafe = [info.filename for info in zf.infolist() if not _is_safe_archive_entry(info.filename)]
            if unsafe:
                for entry in unsafe:
                    print(f"[ERROR] Unsafe archive entry: {entry!r}")
                print("[ERROR] Refusing to extract archive with unsafe entries.")
                return 1

            dest.mkdir(parents=True, exist_ok=True)
            zf.extractall(dest)
            count = len([i for i in zf.infolist() if not i.is_dir()])

    except zipfile.BadZipFile as exc:
        print(f"[ERROR] Invalid .kpack archive: {exc}")
        return 1
    except OSError as exc:
        print(f"[ERROR] Could not extract archive: {exc}")
        return 1

    print(f"Unpacked {count} file(s) to {dest}")
    return 0


def _compare_layout(pack_dir: str, output_dir: str) -> int:
    """Export an OKPF pack in alternative layouts for benchmark comparison.

    Generates three exports under output_dir/:
      markdown-folder/   - text/markdown artifacts as flat files
      jsonl-only/        - all records merged into a single JSONL file
      manifest-summary.json - key manifest fields as simple JSON

    Purpose: enable side-by-side comparison of OKPF against simpler alternatives
    for benchmark and adoption evaluation. See docs/benchmark-plan.md.
    """
    source = Path(pack_dir).resolve()

    if not source.is_dir():
        print(f"[ERROR] Source is not a directory: {pack_dir!r}")
        return 1

    manifest, errors = load_manifest(str(source))
    if manifest is None:
        print(f"[ERROR] Could not load manifest from {pack_dir!r}")
        for e in errors:
            print(f"  {e}")
        return 1

    dest = Path(output_dir)
    md_dir = dest / "markdown-folder"
    jsonl_dir = dest / "jsonl-only"
    dest.mkdir(parents=True, exist_ok=True)
    md_dir.mkdir(exist_ok=True)
    jsonl_dir.mkdir(exist_ok=True)

    # Export 1: markdown-folder — copy text/markdown artifacts as flat files.
    artifacts = _as_list(manifest.get("artifacts")) + _as_list(manifest.get("content"))
    md_count = 0
    for entry in artifacts:
        if not isinstance(entry, dict):
            continue
        entry_path = entry.get("path", "")
        mime_type = entry.get("type", "")
        is_markdown = mime_type in {"text/markdown", "text/plain"} or str(entry_path).endswith(".md")
        if not is_markdown:
            continue
        src_file = source / entry_path
        if not src_file.is_file():
            continue
        dest_name = Path(entry_path).name
        shutil.copy2(src_file, md_dir / dest_name)
        md_count += 1

    # Export 2: jsonl-only — merge all records into a single JSONL file.
    records_entries = _as_list(manifest.get("records"))
    merged_records: list[dict[str, Any]] = []
    for entry in records_entries:
        if not isinstance(entry, dict):
            continue
        record_path = entry.get("path", "")
        if not record_path:
            continue
        src_file = source / record_path
        if not src_file.is_file():
            continue
        try:
            text = src_file.read_text(encoding="utf-8")
        except OSError:
            continue
        if str(record_path).endswith(".jsonl"):
            for line in text.splitlines():
                line = line.strip()
                if line:
                    try:
                        merged_records.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        else:
            try:
                data = json.loads(text)
                if isinstance(data, list):
                    merged_records.extend(r for r in data if isinstance(r, dict))
                elif isinstance(data, dict):
                    inner = data.get("records")
                    if isinstance(inner, list):
                        merged_records.extend(r for r in inner if isinstance(r, dict))
                    else:
                        merged_records.append(data)
            except json.JSONDecodeError:
                pass

    merged_path = jsonl_dir / "records.jsonl"
    with merged_path.open("w", encoding="utf-8") as f:
        for record in merged_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # Export 3: manifest-summary.json — key manifest fields as simple JSON.
    summary: dict[str, Any] = {}
    for key in ("package_id", "id", "name", "version", "okpf_version", "domain",
                "description", "language", "tags", "creators", "license", "usage_policy"):
        value = manifest.get(key)
        if value is not None:
            summary[key] = value
    summary["artifact_count"] = len(artifacts)
    summary["record_file_count"] = len(records_entries)
    summary["merged_record_count"] = len(merged_records)
    summary["profiles"] = _as_list(manifest.get("profiles"))

    summary_path = dest / "manifest-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Comparison layout written to {dest}")
    print(f"  markdown-folder/: {md_count} artifact(s)")
    print(f"  jsonl-only/records.jsonl: {len(merged_records)} record(s)")
    print(f"  manifest-summary.json: {len(summary)} field(s)")
    return 0


def _is_safe_archive_entry(entry: str) -> bool:
    """Return True if the archive entry name is a safe relative path."""
    if not entry or "\x00" in entry or "\\" in entry:
        return False
    if entry.startswith("/") or entry.startswith("~"):
        return False
    if len(entry) >= 2 and entry[1] == ":":
        return False
    normalized = posixpath.normpath(entry)
    if normalized in {"", "."}:
        return False
    if normalized.startswith("../") or normalized == "..":
        return False
    return True


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _summarize_license(value: Any) -> str:
    if not isinstance(value, dict):
        return "(none)"
    if "$ref" in value:
        return str(value["$ref"])
    parts = [str(value[key]) for key in ("type", "details") if value.get(key)]
    return "; ".join(parts) if parts else "(declared)"


def _summarize_usage_policy(value: Any) -> str:
    if not isinstance(value, dict) or not value:
        return "(none)"
    enabled = sorted(
        key for key, item in value.items()
        if key.startswith("allow_") and isinstance(item, bool) and item
    )
    disabled = sorted(
        key for key, item in value.items()
        if key.startswith("allow_") and isinstance(item, bool) and not item
    )
    parts: list[str] = []
    if enabled:
        parts.append("allow " + ", ".join(_usage_label(key) for key in enabled))
    if disabled:
        parts.append("disallow " + ", ".join(_usage_label(key) for key in disabled))
    if value.get("require_attribution") is True:
        parts.append("requires attribution")
    elif value.get("require_attribution") is False:
        parts.append("attribution not required")
    if value.get("notes"):
        parts.append(str(value["notes"]))
    return "; ".join(parts) if parts else "(declared)"


def _usage_label(key: str) -> str:
    return key.removeprefix("allow_").replace("_", " ")


def _demo(source_file: str) -> int:
    """Run an end-to-end OKPF demo: pack, validate, inspect, evaluate."""
    print("=== OKPF Demo ===")
    print()

    print("Step 1: Creating pack from source...")
    try:
        kpack_path, temp_dir = create_demo_pack(source_file)
        print(f"✓ Pack created: {kpack_path}")
    except FileNotFoundError as e:
        print(f"✗ {e}")
        return 1
    except Exception as e:
        print(f"✗ Error creating pack: {e}")
        return 1

    print()
    print("Step 2: Validating pack...")
    is_valid = validate_demo_pack(kpack_path)
    if not is_valid:
        return 1

    print()
    print("Step 3: Inspecting pack...")
    inspect_pack_summary(kpack_path)

    print("Step 4: Running evaluation quiz...")
    print("(Leave answer blank to skip a question)")
    print()
    try:
        run_eval_quiz(kpack_path)
    except EOFError:
        print("\n(Quiz interrupted)")

    print("Demo complete! ✓")
    return 0


def _list_templates() -> int:
    for info in scaffold.list_templates():
        print(f"{info.id}\t{info.name}")
        if info.description:
            print(f"\t{info.description}")
    return 0


def _init(
    dest: str,
    *,
    template_id: str,
    package_id: str | None,
    name: str | None,
    domain: str | None,
    license_type: str | None,
    creator_name: str | None,
    version: str | None,
    force: bool = False,
) -> int:
    dest_path = Path(dest)
    if dest_path.exists() and any(dest_path.iterdir()) and not force:
        print(f"[ERROR] Destination is not empty: {dest!r}")
        print("Use --force to write into it anyway.")
        return 1

    try:
        template = scaffold.load_template(template_id)
    except TemplateError as exc:
        print(f"[ERROR] {exc}")
        return 1

    overrides = {
        "package_id": package_id,
        "name": name,
        "domain": domain,
        "license_type": license_type,
        "creator_name": creator_name,
        "version": version,
    }
    variables = {key: value for key, value in overrides.items() if value is not None}

    dest_path.mkdir(parents=True, exist_ok=True)
    try:
        written = scaffold.render_template(template, dest_path, variables)
    except TemplateError as exc:
        print(f"[ERROR] {exc}")
        return 1

    print(f"Created {len(written)} file(s) in {dest_path} from template '{template.id}'")

    result = validate_pack(str(dest_path))
    if result.valid:
        print(f"OKPF package is valid: {result.package_id or dest_path}")
        return 0
    print(f"[WARNING] Generated pack failed validation: {dest_path}")
    for issue in result.errors:
        print(issue)
    return 1


def _add(
    pack_dir: str,
    file_path: str,
    *,
    role: str | None,
    mime_type: str | None,
    title: str | None,
    description: str | None,
    section: str = "artifacts",
    force: bool = False,
) -> int:
    pack_path = Path(pack_dir)
    manifest_path = pack_path / "manifest.json"
    if not manifest_path.is_file():
        print(f"[ERROR] No manifest.json found in {pack_dir!r}")
        return 1

    source_file = Path(file_path)
    if not source_file.is_file():
        print(f"[ERROR] File not found: {file_path!r}")
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    target_rel = Path(section) / source_file.name
    target_path = pack_path / target_rel

    entries = manifest.setdefault(section, [])
    if not isinstance(entries, list):
        print(f"[ERROR] manifest.json#/{section} is not an array")
        return 1

    existing = next((entry for entry in entries if isinstance(entry, dict) and entry.get("path") == target_rel.as_posix()), None)
    if existing is not None and not force:
        print(f"[ERROR] An entry for {target_rel.as_posix()!r} already exists. Use --force to replace it.")
        return 1

    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.resolve() != source_file.resolve():
        shutil.copy2(source_file, target_path)

    digest = hashlib.sha256(target_path.read_bytes()).hexdigest()

    entry: dict[str, Any] = {"path": target_rel.as_posix(), "sha256": digest}
    if mime_type:
        entry["type"] = mime_type
    if role:
        entry["role"] = role
    if title:
        entry["title"] = title
    if description:
        entry["description"] = description

    if existing is not None:
        entries[entries.index(existing)] = entry
    else:
        entries.append(entry)

    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Added {target_rel.as_posix()} to manifest.json#/{section}")
    return 0


def _fix(pack_dir: str, *, dry_run: bool = False) -> int:
    pack_path = Path(pack_dir)
    manifest_path = pack_path / "manifest.json"
    if not manifest_path.is_file():
        print(f"[ERROR] No manifest.json found in {pack_dir!r}")
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    changes: list[str] = []

    if "id" in manifest and "package_id" not in manifest:
        manifest["package_id"] = manifest["id"]
        changes.append(f"Added package_id = {manifest['id']!r} (copied from legacy 'id', 'id' preserved)")

    if "content" in manifest and "artifacts" not in manifest and isinstance(manifest["content"], list):
        manifest["artifacts"] = manifest["content"]
        changes.append("Added artifacts (copied from legacy 'content', 'content' preserved)")

    for section in ("artifacts", "content"):
        entries = manifest.get(section)
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("sha256") or not entry.get("path"):
                continue
            entry_path = pack_path / str(entry["path"])
            if entry_path.is_file():
                entry["sha256"] = hashlib.sha256(entry_path.read_bytes()).hexdigest()
                changes.append(f"Filled in sha256 for {entry['path']!r} ({section})")

    if not changes:
        print("No fixes needed.")
        return 0

    verb = "Would apply" if dry_run else "Applied"
    print(f"{verb} {len(changes)} fix(es):")
    for change in changes:
        print(f"  - {change}")

    if not dry_run:
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


_EXPLANATIONS: list[tuple[str, str]] = [
    ("missing required field: 'package_id'",
     "Every pack needs a package_id (or the legacy 'id' field). Add \"package_id\": \"your-org.your-pack\" to manifest.json, or run `okpf fix` if 'id' is already present."),
    ("expected at least one of: artifacts, records, content",
     "A pack needs at least one of an 'artifacts', 'records', or 'content' array listing its files. Add one, or run `okpf add <pack_dir> <file>`."),
    ("legacy field 'id' is present",
     "'id' still works, but new tooling prefers 'package_id'. Run `okpf fix <pack_dir>` to add 'package_id' alongside it."),
    ("legacy field 'content' is present",
     "'content' still works, but new tooling prefers 'artifacts'. Run `okpf fix <pack_dir>` to add 'artifacts' alongside it."),
    ("unsafe path", "Archive/artifact paths must be safe relative paths — no '..', no absolute paths, no backslashes. Fix the path in manifest.json."),
    ("missing required field",
     "A required manifest field is missing. See SPEC.md or docs/manifest.md for the full field list."),
]


def _explain_issue(issue: Issue) -> str:
    message = issue.message.lower()
    for pattern, explanation in _EXPLANATIONS:
        if pattern in message:
            return explanation
    return "See docs/manifest.md and SPEC.md for details on this field."


def _explain(pack_path: str) -> int:
    result = validate_pack(pack_path)
    issues: list[Issue] = list(result.errors) + list(result.warnings)

    if not issues:
        print(f"OKPF package is valid with no issues: {result.package_id or pack_path}")
        return 0

    for issue in issues:
        print(str(issue))
        print(f"  -> {_explain_issue(issue)}")
        print()

    return 0 if result.valid else 1
