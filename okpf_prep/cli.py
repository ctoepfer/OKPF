from __future__ import annotations

import sys
from pathlib import Path

import click

from .extractors import extract_text
from .profiles import load_profile, validate_profile
from .runner import prepare_training_pack


@click.group()
def cli() -> None:
    """okpf-prep — prepare source documents into OKPF training packs."""


@cli.command("prepare")
@click.option("--source", required=True, help="Path to the source document.")
@click.option("--profile", required=True, help="Path to the training profile YAML.")
@click.option("--out", required=True, help="Output directory for the training pack.")
@click.option(
    "--backend",
    default="mock",
    show_default=True,
    type=click.Choice(["mock", "ollama"]),
    help="AI backend to use.",
)
@click.option("--model", default=None, help="Model name (Ollama backend only).")
@click.option(
    "--ollama-url",
    default="http://localhost:11434",
    show_default=True,
    help="Ollama base URL.",
)
def prepare(
    source: str,
    profile: str,
    out: str,
    backend: str,
    model: str | None,
    ollama_url: str,
) -> None:
    """Prepare a source document into an OKPF training pack."""
    click.echo(f"Source:  {source}")
    click.echo(f"Profile: {profile}")
    click.echo(f"Output:  {out}")
    click.echo(f"Backend: {backend}" + (f" / {model}" if model else ""))

    result = prepare_training_pack(
        source_path=source,
        profile_path=profile,
        output_dir=out,
        backend=backend,
        model=model,
        ollama_url=ollama_url,
    )

    if result.warnings:
        for w in result.warnings:
            click.echo(f"  WARN  {w}", err=True)
    if result.errors:
        for e in result.errors:
            click.echo(f"  ERROR {e}", err=True)

    click.echo(f"\nRecords generated : {result.record_count}")
    click.echo(f"Validation status : {result.validation_status}")
    click.echo(f"Manifest          : {result.manifest_path}")
    click.echo(f"Records           : {result.records_path}")
    click.echo(f"Extracted text    : {result.extracted_text_path}")
    click.echo(f"Report            : {result.report_path}")

    if result.validation_status != "pass" or result.errors:
        sys.exit(1)


@cli.command("validate-profile")
@click.argument("profile_path")
def validate_profile_cmd(profile_path: str) -> None:
    """Validate a training profile YAML file."""
    try:
        profile = load_profile(profile_path)
    except (FileNotFoundError, ValueError) as exc:
        click.echo(f"ERROR: {exc}", err=True)
        sys.exit(1)

    result = validate_profile(profile)

    if result.warnings:
        for w in result.warnings:
            click.echo(f"WARN  {w}")
    if result.errors:
        for e in result.errors:
            click.echo(f"ERROR {e}", err=True)
        sys.exit(1)

    click.echo(f"Profile '{profile.id}' is valid.")


@cli.command("extract-text")
@click.argument("source_path")
@click.option("--out", default=None, help="Write extracted text to this file.")
def extract_text_cmd(source_path: str, out: str | None) -> None:
    """Extract text from a source document and print or write it."""
    try:
        extracted = extract_text(source_path)
    except (FileNotFoundError, ValueError) as exc:
        click.echo(f"ERROR: {exc}", err=True)
        sys.exit(1)

    for w in extracted.warnings:
        click.echo(f"WARN  {w}", err=True)

    if out:
        Path(out).write_text(extracted.text, encoding="utf-8")
        click.echo(f"Extracted text written to {out}")
        click.echo(f"Characters: {len(extracted.text)}")
        if extracted.page_count is not None:
            click.echo(f"Pages: {extracted.page_count}")
    else:
        click.echo(extracted.text)


# Entry point alias used by pyproject.toml scripts
main = cli

if __name__ == "__main__":
    cli()
