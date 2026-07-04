# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Bundled copy of the canonical top-level schemas/ directory (data only).

This exists so validation still works when `okpf` is installed via pip
without a full repo checkout. The top-level schemas/ directory remains the
canonical, authoritative source (see CLAUDE.md) -- tests/test_schema_bundle_in_sync.py
fails CI if this copy drifts from it.
"""
