# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""Test configuration and fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

# Add reference/python to path so okpf module is importable
REPO_ROOT = Path(__file__).parent.parent
REF_PYTHON = REPO_ROOT / "reference" / "python"
if str(REF_PYTHON) not in sys.path:
    sys.path.insert(0, str(REF_PYTHON))
