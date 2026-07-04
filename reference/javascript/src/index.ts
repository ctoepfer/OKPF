// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 OKPF Contributors
/**
 * okpf — JavaScript/TypeScript reference implementation
 * for the Open Knowledge Pack Format.
 *
 * Primary entry point:
 *
 *   import { Pack } from 'okpf';
 *
 *   const pack = await Pack.load('./examples/brewing/');
 *   console.log(pack.manifest.name);    // "Water Chemistry for Brewing"
 *   console.log(pack.capabilities);     // ["retrieval", "evaluation", ...]
 *   for (const ev of pack.evaluations) {
 *     console.log(ev.question);
 *   }
 */

export const OKPF_VERSION = "0.0.1";
export const OKPF_SPEC_VERSION = "0.1.0";

// Re-export the Pack class as the primary API
export { Pack } from './pack.js';
export type {
  EvaluationCase,
  EvaluationSet,
  ArtifactContent,
  ValidationError,
  ValidationResult,
} from './pack.js';

// ---------------------------------------------------------------------------
// Type definitions
// ---------------------------------------------------------------------------

export interface ManifestRef {
  $ref: string;
}

export interface ContentArtifact {
  /** Optional in the current schema -- only `path` is required. Falls back to `path` when absent. */
  id: string;
  path: string;
  type?: string;
  format?: string;
  title?: string;
  description?: string;
  sha256?: string;
  /** Free-form string in the current schema (no fixed enum). Common values: guide, source, reference, data, image. */
  role?: string;
  language?: string;
}

/** Current v0.1.0 license shape. Also accepts a $ref to a sibling file (see ManifestRef). */
export interface License {
  type?: string;
  details?: string;
  path?: string;
  [key: string]: unknown;
}

/** AI interoperability hints — all fields optional and advisory. */
export interface AiMetadata {
  recommended_use?: Array<
    | "rag" | "fine-tuning" | "evaluation" | "workflow-execution"
    | "simulation" | "robotics" | "tutoring" | "diagnostics"
    | "reasoning" | "retrieval"
  >;
  safe_for_training?: boolean;
  contains_pii?: boolean;
  modalities?: Array<"text" | "image" | "audio" | "video" | "structured-data" | "code" | "3d" | "multimodal">;
  domains?: string[];
  risk_level?: "none" | "low" | "medium" | "high";
  evaluation_available?: boolean;
  workflow_capable?: boolean;
}

/** Trust and verification metadata — all fields optional and advisory. */
export interface TrustMetadata {
  signed?: boolean;
  verified_contributors?: boolean;
  provenance_complete?: boolean;
  attestations?: Array<{
    type: "peer-review" | "institutional" | "automated-check" | "community-review" | "expert-review";
    issued_by: string;
    issued_at: string;
    scope?: string;
    evidence_uri?: string;
  }>;
  verification_method?: string;
}

export interface Manifest {
  okpf_version: string;
  /** Current v0.1.0 identity field. Prefer this over legacy `id`. */
  package_id?: string;
  /** Legacy alias for package_id -- schema-valid, must be preserved when present. */
  id?: string;
  name: string;
  title?: string;
  version: string;
  domain: string;
  description?: string;
  tags?: string[];
  language?: string;
  /** Not a real v0.1.0 field (kept only for reading older/draft manifests). */
  created?: string;
  updated?: string;
  profiles?: string[];
  license: License | ManifestRef;
  usage_policy?: UsagePolicy;
  /** Current v0.1.0 field for artifact entries. Prefer this over legacy `content`. */
  artifacts?: ContentArtifact[];
  /** Legacy alias for artifacts -- schema-valid, must be preserved when present. */
  content?: ContentArtifact[];
  records?: Array<{ path: string; format?: string; description?: string }>;
  /** Declared capabilities for AI system negotiation. */
  capabilities?: string[];
  /** Optional AI interoperability hints. */
  ai?: AiMetadata;
  /** Optional trust and verification metadata. */
  trust?: TrustMetadata;
  [key: string]: unknown;
}

export interface UsagePolicy {
  allow_rag?: boolean;
  allow_fine_tuning?: boolean;
  allow_evaluation?: boolean;
  allow_commercial_use?: boolean;
  allow_derivatives?: boolean;
  allow_commercial_derivatives?: boolean;
  require_attribution?: boolean;
  notes?: string;
}
