# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 OKPF Contributors
"""
okpf — Python reference implementation for the Open Knowledge Pack Format.

Primary entry point:

    from okpf import Pack

    pack = Pack.load("examples/brewing/")
    print(pack.manifest.title)        # "Water Chemistry for Brewing"
    print(pack.capabilities)          # ["retrieval", "evaluation", ...]
    for ev in pack.evaluations:
        print(ev.question)

    result = pack.validate()
    print(result.valid)
"""

__version__ = "0.0.1"
__spec_version__ = "0.1.0"

from okpf.pack import Pack, ArtifactContent
from okpf.manifest import Manifest, ContentArtifact, EvaluationCase, AiMetadata, TrustMetadata
from okpf.validate import validate, ValidationResult, ValidationError

__all__ = [
    "__version__",
    "__spec_version__",
    # Primary API
    "Pack",
    "ArtifactContent",
    # Manifest types
    "Manifest",
    "ContentArtifact",
    "EvaluationCase",
    "AiMetadata",
    "TrustMetadata",
    # Validation
    "validate",
    "ValidationResult",
    "ValidationError",
]
