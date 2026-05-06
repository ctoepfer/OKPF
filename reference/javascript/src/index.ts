/**
 * okpf — JavaScript/TypeScript reference implementation
 * for the Open Knowledge Pack Format.
 *
 * This is a stub implementation. See README.md for the planned API.
 */

export const OKPF_VERSION = "0.0.1";
export const OKPF_SPEC_VERSION = "0.1.0";

// These will be implemented:
// export { KnowledgePack } from './pack.js';
// export { PackBuilder } from './builder.js';
// export { validate, ValidationResult } from './validate.js';

// Type stubs — will be filled in during implementation

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
  [key: string]: unknown;
}
