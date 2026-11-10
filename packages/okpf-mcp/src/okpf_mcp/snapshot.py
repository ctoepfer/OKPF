# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Bounded immutable bytes for the existing reference validator's reader API."""

from __future__ import annotations

import json
import math
import os
import stat
import zipfile
from pathlib import Path
from typing import IO, Any

import yaml
from okpf_validate import PackageReader, _is_safe_path

MAX_FILE = 2 * 1024 * 1024
MAX_PACK = 32 * 1024 * 1024
MAX_ENTRIES = 2048
MAX_DEPTH = 32
MAX_NODES = 100_000


class MountError(ValueError):
    """An explicit mount cannot be safely indexed."""


def safe_name(name: str) -> None:
    if not _is_safe_path(name) or len(name.split("/")) > MAX_DEPTH:
        raise MountError(f"Unsafe or over-deep pack path: {name!r}")


class Snapshot(PackageReader):  # type: ignore[misc]  # Reference reader module is untyped.
    def __init__(self) -> None:
        self.files: dict[str, bytes] = {}
        self.size = 0
        self.entries = 0

    def count(self) -> None:
        self.entries += 1
        if self.entries > MAX_ENTRIES:
            raise MountError("Pack exceeds entry limit")

    def add(self, name: str, stream: IO[bytes], size: int) -> None:
        safe_name(name)
        if name in self.files:
            raise MountError(f"Duplicate entry: {name!r}")
        if size > MAX_FILE or self.size + size > MAX_PACK:
            raise MountError("Pack exceeds byte limit")
        raw = stream.read(MAX_FILE + 1)
        if len(raw) > MAX_FILE or self.size + len(raw) > MAX_PACK:
            raise MountError("Pack exceeds read limit")
        self.files[name] = raw
        self.size += len(raw)

    def iter_paths(self) -> list[str]:
        return sorted(self.files)

    def exists(self, path: str) -> bool:
        return _is_safe_path(path) and path in self.files

    def read_bytes(self, path: str) -> bytes:
        safe_name(path)
        return self.files[path]

    def read_text(self, path: str) -> str:
        return self.read_bytes(path).decode("utf-8")


def snapshot(path: Path) -> Snapshot:
    result = Snapshot()
    if path.is_dir():
        if os.name != "posix":
            raise MountError(
                "Directory mounts require POSIX no-follow reads; use .kpack on this OS"
            )

        # Descriptor-relative traversal prevents parent-directory symlink swaps.
        def walk(fd: int, prefix: str = "") -> None:
            with os.scandir(fd) as entries:
                for entry in entries:
                    result.count()
                    name = prefix + entry.name
                    safe_name(name)
                    info = entry.stat(follow_symlinks=False)
                    if stat.S_ISLNK(info.st_mode):
                        raise MountError(f"Symlink entry: {name!r}")
                    if stat.S_ISDIR(info.st_mode):
                        child = os.open(
                            entry.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd
                        )
                        try:
                            walk(child, name + "/")
                        finally:
                            os.close(child)
                    elif stat.S_ISREG(info.st_mode):
                        child = os.open(
                            entry.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd
                        )
                        with os.fdopen(child, "rb") as stream:
                            actual = os.fstat(stream.fileno())
                            if not stat.S_ISREG(actual.st_mode):
                                raise MountError(f"Non-regular file: {name!r}")
                            result.add(name, stream, actual.st_size)
                    else:
                        raise MountError(f"Non-regular entry: {name!r}")

        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            walk(fd)
        finally:
            os.close(fd)
    elif path.is_file() and path.suffix == ".kpack":
        if path.stat().st_size > MAX_PACK:
            raise MountError("Archive exceeds container size limit")
        with zipfile.ZipFile(path) as archive:
            seen = set()
            for entry in archive.infolist():
                result.count()
                # orig_filename retains NULs that ZipInfo.filename truncates.
                name = entry.orig_filename.rstrip("/") if entry.is_dir() else entry.orig_filename
                safe_name(name)
                if name in seen:
                    raise MountError(f"Duplicate archive entry: {name!r}")
                seen.add(name)
                mode = entry.external_attr >> 16
                if stat.S_ISLNK(mode) or (stat.S_IFMT(mode) not in {0, stat.S_IFREG, stat.S_IFDIR}):
                    raise MountError(f"Unsupported archive entry: {name!r}")
                if entry.flag_bits & 1:
                    raise MountError("Encrypted ZIP containers are unsupported")
                if not entry.is_dir():
                    if entry.file_size > MAX_FILE:
                        raise MountError("Archive entry exceeds byte limit")
                    with archive.open(entry) as stream:
                        result.add(name, stream, entry.file_size)
    else:
        raise MountError("Expected an unpacked pack root or .kpack file")
    return result


def parse_data(text: str, *, yaml_data: bool = False) -> Any:
    """Reject aliases, duplicate keys and non-JSON values before schema traversal."""

    def unique(pairs: list[tuple[Any, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if not isinstance(key, str) or key in value:
                raise MountError("Object keys must be unique strings")
            value[key] = item
        return value

    if yaml_data:

        class Loader(yaml.SafeLoader):
            pass

        def mapping(loader: Loader, node: yaml.MappingNode) -> dict[str, Any]:
            return unique(
                [(loader.construct_object(k), loader.construct_object(v)) for k, v in node.value]
            )

        Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
        if any(
            isinstance(token, (yaml.tokens.AliasToken, yaml.tokens.AnchorToken))
            for token in yaml.scan(text)
        ):
            raise MountError("YAML aliases and anchors are unsupported")
        value = yaml.load(text, Loader=Loader)
    else:
        value = json.loads(text, object_pairs_hook=unique)
    pending = [(value, 0)]
    count = 0
    while pending:
        item, depth = pending.pop()
        count += 1
        if depth > MAX_DEPTH or count > MAX_NODES:
            raise MountError("Structured data exceeds depth/node limit")
        if isinstance(item, dict):
            pending.extend((v, depth + 1) for v in item.values())
        elif isinstance(item, list):
            pending.extend((v, depth + 1) for v in item)
        elif not isinstance(item, (str, int, float, bool, type(None))):
            raise MountError("Only JSON-compatible values are supported")
        elif isinstance(item, float) and not math.isfinite(item):
            raise MountError("Non-finite numbers are unsupported")
    return value
