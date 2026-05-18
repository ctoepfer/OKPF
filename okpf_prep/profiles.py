from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .models import ValidationResult

REQUIRED_FIELDS = ("id", "name", "description", "domain", "input_types", "allowed_record_types")


@dataclass
class ChunkingConfig:
    strategy: str = "section-aware"
    max_chars: int = 12000
    overlap_chars: int = 500


@dataclass
class OutputConfig:
    format: str = "okpf"
    okpf_version: str = "0.1.0"
    package_type: str = "knowledge_pack"


@dataclass
class ConversionConfig:
    preserve_source_text: bool = True
    require_source_refs: bool = True
    summarize_long_sections: bool = False
    confidence_required: bool = True


@dataclass
class ValidationConfig:
    record_type_policy: str = "strict"


@dataclass
class PromptConfig:
    system: str = ""
    instructions: str = ""


@dataclass
class TrainingProfile:
    id: str
    name: str
    description: str
    domain: str
    input_types: list[str]
    allowed_record_types: list[str]
    target_brains: list[str] = field(default_factory=list)
    output: OutputConfig = field(default_factory=OutputConfig)
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    conversion: ConversionConfig = field(default_factory=ConversionConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    prompt: PromptConfig = field(default_factory=PromptConfig)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "input_types": self.input_types,
            "allowed_record_types": self.allowed_record_types,
            "target_brains": self.target_brains,
        }


def load_profile(profile_path: str | Path) -> TrainingProfile:
    path = Path(profile_path)
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {path}")
    with path.open() as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Profile must be a YAML mapping: {path}")
    return _parse_profile(data, path)


def _parse_profile(data: dict[str, Any], source: Path) -> TrainingProfile:
    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        raise ValueError(f"Profile {source} missing required fields: {missing}")

    raw_output = data.get("output", {})
    output = OutputConfig(
        format=raw_output.get("format", "okpf"),
        okpf_version=raw_output.get("okpf_version", "0.1.0"),
        package_type=raw_output.get("package_type", "knowledge_pack"),
    )

    raw_chunking = data.get("chunking", {})
    chunking = ChunkingConfig(
        strategy=raw_chunking.get("strategy", "section-aware"),
        max_chars=int(raw_chunking.get("max_chars", 12000)),
        overlap_chars=int(raw_chunking.get("overlap_chars", 500)),
    )

    raw_conv = data.get("conversion", {})
    conversion = ConversionConfig(
        preserve_source_text=bool(raw_conv.get("preserve_source_text", True)),
        require_source_refs=bool(raw_conv.get("require_source_refs", True)),
        summarize_long_sections=bool(raw_conv.get("summarize_long_sections", False)),
        confidence_required=bool(raw_conv.get("confidence_required", True)),
    )

    raw_val = data.get("validation", {})
    validation = ValidationConfig(
        record_type_policy=raw_val.get("record_type_policy", "strict"),
    )

    raw_prompt = data.get("prompt", {})
    prompt = PromptConfig(
        system=raw_prompt.get("system", ""),
        instructions=raw_prompt.get("instructions", ""),
    )

    input_types = [t.lstrip(".").lower() for t in data["input_types"]]
    allowed_record_types = list(data["allowed_record_types"])

    return TrainingProfile(
        id=str(data["id"]),
        name=str(data["name"]),
        description=str(data["description"]),
        domain=str(data["domain"]),
        input_types=input_types,
        allowed_record_types=allowed_record_types,
        target_brains=list(data.get("target_brains", [])),
        output=output,
        chunking=chunking,
        conversion=conversion,
        validation=validation,
        prompt=prompt,
    )


def validate_profile(profile: TrainingProfile) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if not profile.id:
        errors.append("Profile 'id' must not be empty.")
    if not profile.name:
        errors.append("Profile 'name' must not be empty.")
    if not profile.input_types:
        errors.append("Profile 'input_types' must list at least one type.")
    if not profile.allowed_record_types:
        errors.append("Profile 'allowed_record_types' must list at least one type.")
    if profile.chunking.max_chars < 100:
        errors.append("chunking.max_chars must be >= 100.")
    if profile.chunking.overlap_chars >= profile.chunking.max_chars:
        errors.append("chunking.overlap_chars must be less than max_chars.")
    if not profile.prompt.system:
        warnings.append("Profile has no prompt.system — the AI will receive no system instruction.")
    if not profile.prompt.instructions:
        warnings.append("Profile has no prompt.instructions.")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
