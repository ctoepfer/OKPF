# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
import io
import stat
import zipfile

import pytest
import yaml

from okpf_mcp.catalog import Catalog
from okpf_mcp.snapshot import MountError, Snapshot, parse_data, snapshot


@pytest.mark.parametrize(
    "name",
    [
        "../escape",
        "/absolute",
        "C:/drive",
        "a\\..\\escape",
        "a/../../escape",
        "./alias",
        "a//alias",
    ],
)
def test_zip_paths(tmp_path, name):
    path = tmp_path / "bad.kpack"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(name, "x")
    with pytest.raises(MountError):
        snapshot(path)


def test_nul_and_duplicates(tmp_path):
    path = tmp_path / "bad.kpack"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("aXb", "x")
    path.write_bytes(path.read_bytes().replace(b"aXb", b"a\x00b"))
    with pytest.raises(MountError):
        snapshot(path)
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("same", "x")
        with pytest.warns(UserWarning):
            z.writestr("same", "y")
    with pytest.raises(MountError, match="Duplicate"):
        snapshot(path)


def test_symlinks_and_archive_symlink(pack, tmp_path):
    secret = tmp_path / "secret"
    secret.write_text("outside data")
    (pack / "escape").symlink_to(secret)
    assert not Catalog([str(pack)]).mounts
    (pack / "escape").unlink()
    (pack / "escape").symlink_to(tmp_path, target_is_directory=True)
    assert not Catalog([str(pack)]).mounts
    path = tmp_path / "link.kpack"
    with zipfile.ZipFile(path, "w") as z:
        info = zipfile.ZipInfo("link")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        z.writestr(info, "../secret")
    with pytest.raises(MountError):
        snapshot(path)


def test_byte_and_entry_limits(pack, tmp_path, monkeypatch):
    import okpf_mcp.snapshot as module

    monkeypatch.setattr(module, "MAX_FILE", 100)
    with pytest.raises(MountError, match="limit"):
        snapshot(pack)
    archive = tmp_path / "large.kpack"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("large", b"x" * 10000)
    with pytest.raises(MountError, match="limit"):
        snapshot(archive)
    monkeypatch.setattr(module, "MAX_FILE", 1000000)
    monkeypatch.setattr(module, "MAX_ENTRIES", 1)
    with pytest.raises(MountError, match="limit"):
        snapshot(pack)
    monkeypatch.setattr(module, "MAX_PACK", 2)
    with pytest.raises(MountError, match="limit"):
        Snapshot().add("x", io.BytesIO(b"xxx"), 0)


@pytest.mark.parametrize(
    "text,is_yaml",
    [
        ('{"a":1,"a":2}', False),
        ('{"a":NaN}', False),
        ("a: 1\na: 2", True),
        ("a: &a [*a]", True),
        ("!!python/object/apply:os.system [false]", True),
        ("date: 2020-01-01", True),
        ("[" * 40 + "0" + "]" * 40, False),
    ],
)
def test_structured_parse_guards(text, is_yaml):
    with pytest.raises((ValueError, yaml.YAMLError)):
        parse_data(text, yaml_data=is_yaml)
