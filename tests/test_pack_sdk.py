# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Tests for okpf.Pack against real example packs (both directory and .kpack).

Pack.load() previously crashed with KeyError('id') on every current-shape
example pack in this repo -- Manifest.from_dict required legacy 'id' and
'created' fields and only read 'content', never 'artifacts'. These tests
exist specifically to catch that class of regression, since the SDK
(Manifest/Pack) had zero prior coverage against real examples.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "reference" / "python"))

from okpf import Pack  # noqa: E402
from okpf.cli import _pack  # noqa: E402


@pytest.mark.parametrize("example_name", [
    "hello-world",
    "minimal",
    "software-onboarding",
    "local-history-lost-electric-sign",
])
def test_pack_load_directory_examples(example_name: str) -> None:
    pack = Pack.load(str(REPO_ROOT / "examples" / example_name))
    try:
        assert pack.manifest.package_id
        assert pack.manifest.display_name
    finally:
        pack.close()


def test_pack_load_reads_artifacts_not_just_legacy_content() -> None:
    pack = Pack.load(str(REPO_ROOT / "examples" / "software-onboarding"))
    try:
        assert len(pack.content) == 3
        content = pack.read(pack.content[0].id)
        assert content.text
    finally:
        pack.close()


def test_pack_load_resolves_evals_file_references() -> None:
    # examples/software-onboarding's manifest declares evals as file
    # references ({"path": "evals/....json"}), not inline eval objects.
    pack = Pack.load(str(REPO_ROOT / "examples" / "software-onboarding"))
    try:
        evaluations = pack.evaluations
        assert len(evaluations) == 4
        assert all(ev.id and ev.question for ev in evaluations)
    finally:
        pack.close()


def test_manifest_missing_package_id_and_id_raises_key_error() -> None:
    from okpf.manifest import Manifest

    with pytest.raises(KeyError):
        Manifest.from_dict({"okpf_version": "0.1.0", "name": "x", "version": "0.1.0", "domain": "d"})


def test_pack_load_kpack_archive(tmp_path: Path) -> None:
    source = REPO_ROOT / "examples" / "software-onboarding"
    archive = tmp_path / "software-onboarding.kpack"
    assert _pack(str(source), str(archive)) == 0

    pack = Pack.load(str(archive))
    try:
        assert pack.manifest.package_id == "okpf-example-software-onboarding"
        assert len(pack.content) == 3

        content = pack.read(pack.content[0].id)
        assert content.text

        evaluations = pack.evaluations
        assert len(evaluations) == 4
    finally:
        pack.close()


def test_pack_validate_works_for_directory_and_kpack(tmp_path: Path) -> None:
    source = REPO_ROOT / "examples" / "software-onboarding"
    archive = tmp_path / "software-onboarding.kpack"
    assert _pack(str(source), str(archive)) == 0

    dir_pack = Pack.load(str(source))
    kpack_pack = Pack.load(str(archive))
    try:
        assert dir_pack.validate().valid
        assert kpack_pack.validate().valid
    finally:
        dir_pack.close()
        kpack_pack.close()


def test_pack_context_manager_closes_reader() -> None:
    with Pack.load(str(REPO_ROOT / "examples" / "hello-world")) as pack:
        assert pack.manifest.package_id
    # No assertion beyond "doesn't raise" -- __exit__ should not error.


def test_pack_load_nonexistent_path_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        Pack.load(str(tmp_path / "does-not-exist"))


def test_pack_get_artifact_unknown_id_raises_key_error() -> None:
    pack = Pack.load(str(REPO_ROOT / "examples" / "hello-world"))
    try:
        with pytest.raises(KeyError):
            pack.get_artifact("does-not-exist")
    finally:
        pack.close()


def test_pack_repr_uses_package_id() -> None:
    pack = Pack.load(str(REPO_ROOT / "examples" / "hello-world"))
    try:
        assert "package_id=" in repr(pack)
    finally:
        pack.close()
