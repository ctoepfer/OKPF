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
  id: string;
  path: string;
  type: string;
  title?: string;
  description?: string;
  sha256?: string;
  role?: "guide" | "transcript" | "workflow" | "evaluation" | "reference" | "image" | "data" | "other";
  language?: string;
}

export interface LicenseScope {
  use: "open" | "restricted" | "commercial" | "personal" | "unspecified";
  redistribution?: "open" | "restricted" | "prohibited" | "unspecified";
  derivative_works?: "open" | "share-alike" | "restricted" | "prohibited" | "unspecified";
  ai_training?: "permitted" | "restricted" | "prohibited" | "unspecified";
  commercial_use?: "permitted" | "restricted" | "prohibited" | "unspecified";
}

export interface License {
  spdx_expression: string;
  scope: LicenseScope;
  attribution_required?: boolean;
  attribution_text?: string;
  full_text_url?: string;
  custom_terms?: string;
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
  id: string;
  name: string;
  version: string;
  domain: string;
  description?: string;
  tags?: string[];
  language?: string;
  created: string;
  updated?: string;
  license: License | ManifestRef;
  content: ContentArtifact[];
  /** Declared capabilities for AI system negotiation. */
  capabilities?: string[];
  /** Optional AI interoperability hints. */
  ai?: AiMetadata;
  /** Optional trust and verification metadata. */
  trust?: TrustMetadata;
  [key: string]: unknown;
}
