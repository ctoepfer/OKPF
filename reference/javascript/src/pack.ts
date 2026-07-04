// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 OKPF Contributors
/**
 * Pack — primary entry point for loading and interacting with OKPF knowledge packs.
 *
 * Supports Node.js directory packs. ZIP (.kpack) archive support is not
 * implemented yet (Python's Pack.load() has it; see reference/python/okpf/pack.py).
 *
 * @example
 * import { Pack } from 'okpf';
 *
 * const pack = await Pack.load('./examples/software-onboarding/');
 * console.log(pack.displayName);
 * console.log(pack.capabilities);
 * for (const ev of pack.evaluations) {
 *   console.log(ev.question);
 * }
 */

import * as fs from 'node:fs';
import * as path from 'node:path';
import {
  type Manifest,
  type ContentArtifact,
  type AiMetadata,
  type TrustMetadata,
} from './index.js';


// ---------------------------------------------------------------------------
// Evaluation types
// ---------------------------------------------------------------------------

export interface EvaluationCase {
  id: string;
  question: string;
  /** Free-form in practice -- most examples in this repo omit it entirely. */
  type?: string;
  difficulty?: 'beginner' | 'intermediate' | 'expert';
  expected_answer?: string | Record<string, unknown>;
  choices?: Array<{ id: string; text: string; correct?: boolean }>;
  /** Repo convention for linking an eval case back to specific records. */
  record_ids?: string[];
  source_artifacts?: string[];
  tags?: string[];
  explanation?: string;
}

export interface EvaluationSet {
  version?: string;
  created?: string;
  description?: string;
  evaluations: EvaluationCase[];
}


// ---------------------------------------------------------------------------
// Artifact content
// ---------------------------------------------------------------------------

export interface ArtifactContent {
  artifact: ContentArtifact;
  buffer: Buffer;
  /** Decoded text content. Throws for binary artifacts with non-UTF-8 content. */
  text: string;
}

function makeArtifactContent(artifact: ContentArtifact, buffer: Buffer): ArtifactContent {
  return {
    artifact,
    buffer,
    get text() {
      return buffer.toString('utf-8');
    },
  };
}


// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

export interface ValidationError {
  path: string;
  message: string;
  severity: 'error' | 'warning';
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
  packId?: string;
  packVersion?: string;
}

// Matches the current v0.1.0 schema (see schemas/v0.1.0/manifest.schema.json
// and reference/python/okpf_validate.py) -- 'created' is not a real field,
// and identity/payload are checked separately below to support the
// package_id/id and artifacts/records/content aliasing rule.
const REQUIRED_MANIFEST_FIELDS = ['okpf_version', 'name', 'version', 'domain', 'license'] as const;
const PAYLOAD_FIELDS = ['artifacts', 'records', 'content'] as const;

/** Reads `artifacts`, falling back to legacy `content` -- same rule as the Python reference. */
function artifactEntries(manifest: Record<string, unknown>): Record<string, unknown>[] {
  const artifacts = manifest['artifacts'];
  if (Array.isArray(artifacts)) return artifacts as Record<string, unknown>[];
  const content = manifest['content'];
  return Array.isArray(content) ? (content as Record<string, unknown>[]) : [];
}

function validatePack(packPath: string): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];
  let packId: string | undefined;
  let packVersion: string | undefined;

  const manifestPath = path.join(packPath, 'manifest.json');
  if (!fs.existsSync(manifestPath)) {
    errors.push({ path: 'manifest.json', message: 'File not found', severity: 'error' });
    return { valid: false, errors, warnings };
  }

  let manifest: Record<string, unknown>;
  try {
    manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
  } catch (e) {
    errors.push({ path: 'manifest.json', message: `Invalid JSON: ${e}`, severity: 'error' });
    return { valid: false, errors, warnings };
  }

  packId = (manifest['package_id'] ?? manifest['id']) as string | undefined;
  packVersion = manifest['version'] as string | undefined;

  for (const f of REQUIRED_MANIFEST_FIELDS) {
    if (!(f in manifest)) {
      errors.push({ path: 'manifest.json', message: `Missing required field: '${f}'`, severity: 'error' });
    }
  }

  if (!('package_id' in manifest) && !('id' in manifest)) {
    errors.push({ path: 'manifest.json', message: "Missing required field: 'package_id'", severity: 'error' });
  }

  if (!PAYLOAD_FIELDS.some((f) => f in manifest)) {
    errors.push({
      path: 'manifest.json',
      message: 'Expected at least one of: artifacts, records, content',
      severity: 'error',
    });
  }

  const artifacts = artifactEntries(manifest);
  if (artifacts.length > 0) {
    const seenIds = new Set<string>();
    artifacts.forEach((artifact, i) => {
      const prefix = `manifest.json#/artifacts[${i}]`;
      // Only `path` is required on artifact entries in the current schema.
      if (!('path' in artifact)) {
        errors.push({ path: prefix, message: "Missing required field: 'path'", severity: 'error' });
      }
      const artId = artifact['id'] as string | undefined;
      if (artId && seenIds.has(artId)) {
        errors.push({ path: prefix, message: `Duplicate artifact id: '${artId}'`, severity: 'error' });
      }
      if (artId) seenIds.add(artId);

      const artPath = artifact['path'] as string;
      if (artPath) {
        const fullPath = path.join(packPath, artPath);
        if (!fs.existsSync(fullPath)) {
          errors.push({ path: prefix, message: `Content file not found: '${artPath}'`, severity: 'error' });
        } else if (!artifact['sha256']) {
          warnings.push({ path: prefix, message: `No SHA-256 hash declared for '${artPath}'`, severity: 'warning' });
        }
      }
    });
  }

  return { valid: errors.length === 0, errors, warnings, packId, packVersion };
}


// ---------------------------------------------------------------------------
// Pack class
// ---------------------------------------------------------------------------

function resolveRef(value: unknown, basePath: string): unknown {
  if (
    value !== null &&
    typeof value === 'object' &&
    '$ref' in (value as object)
  ) {
    const ref = (value as Record<string, string>)['$ref'];
    const refPath = path.join(basePath, ref);
    if (fs.existsSync(refPath)) {
      return JSON.parse(fs.readFileSync(refPath, 'utf-8'));
    }
  }
  return value;
}

function normalizeArtifacts(entries: Record<string, unknown>[]): ContentArtifact[] {
  return entries.map((entry) => ({
    ...(entry as unknown as ContentArtifact),
    // `id` is optional in the current schema (only `path` is required) --
    // fall back to path so every artifact has a stable, always-present id.
    id: (entry['id'] as string | undefined) ?? (entry['path'] as string),
    path: entry['path'] as string,
  }));
}

function parseManifest(data: Record<string, unknown>, basePath: string): Manifest {
  const resolvedLicense = resolveRef(data['license'], basePath) as Manifest['license'];
  const normalizedArtifacts = normalizeArtifacts(artifactEntries(data));
  return {
    ...(data as unknown as Manifest),
    license: resolvedLicense,
    artifacts: normalizedArtifacts,
    content: normalizedArtifacts,
  };
}

export class Pack {
  readonly path: string;
  readonly manifest: Manifest;

  private constructor(packPath: string, manifest: Manifest) {
    this.path = packPath;
    this.manifest = manifest;
  }

  /**
   * Load a knowledge pack from a directory path.
   *
   * Reads manifest.json and resolves $ref pointers to sibling files.
   * ZIP archive (.kpack) support is planned.
   */
  static async load(packPath: string): Promise<Pack> {
    const resolved = path.resolve(packPath);

    if (!fs.existsSync(resolved) || !fs.statSync(resolved).isDirectory()) {
      throw new Error(`Pack path not found or not a directory: ${packPath}`);
    }

    const manifestPath = path.join(resolved, 'manifest.json');
    if (!fs.existsSync(manifestPath)) {
      throw new Error(`manifest.json not found in ${packPath}`);
    }

    const raw = JSON.parse(fs.readFileSync(manifestPath, 'utf-8')) as Record<string, unknown>;
    const manifest = parseManifest(raw, resolved);

    return new Pack(resolved, manifest);
  }

  /** The manifest's own `title` field if set, else `name`. */
  get displayName(): string {
    return this.manifest.title ?? this.manifest.name;
  }

  /**
   * Declared capabilities of this pack.
   *
   * Examples: ["retrieval", "evaluation", "workflow-execution"]
   * Use for capability negotiation before loading full content.
   */
  get capabilities(): string[] {
    return this.manifest.capabilities ?? [];
  }

  /** AI interoperability metadata declared in the manifest. */
  get aiMetadata(): AiMetadata | undefined {
    return (this.manifest as unknown as Record<string, unknown>)['ai'] as AiMetadata | undefined;
  }

  /** Trust and verification metadata declared in the manifest. */
  get trust(): TrustMetadata | undefined {
    return (this.manifest as unknown as Record<string, unknown>)['trust'] as TrustMetadata | undefined;
  }

  /**
   * Evaluation test cases declared in this pack.
   *
   * Returns an empty array if no evaluations are present. Each entry may be
   * an inline evaluation case, or -- the convention used throughout this
   * repo's examples -- a file reference (`{"path": "evals/x.json"}`) that
   * is resolved relative to the pack root.
   */
  get evaluations(): EvaluationCase[] {
    const manifestData = this.manifest as unknown as Record<string, unknown>;
    const raw = manifestData['evaluations'] ?? manifestData['evals'];
    if (!raw) return [];

    // May already be resolved (object with evaluations array) or a $ref
    const resolved = resolveRef(raw, this.path) as Record<string, unknown> | unknown[] | null;

    if (resolved && typeof resolved === 'object' && !Array.isArray(resolved) && 'evaluations' in resolved) {
      return (resolved as unknown as EvaluationSet).evaluations ?? [];
    }
    if (!Array.isArray(resolved)) return [];

    const cases: EvaluationCase[] = [];
    for (const entry of resolved) {
      if (!entry || typeof entry !== 'object') continue;
      const record = entry as Record<string, unknown>;
      if ('path' in record && !('question' in record) && !('id' in record)) {
        cases.push(...this._loadEvalFile(record['path'] as string));
      } else {
        cases.push(record as unknown as EvaluationCase);
      }
    }
    return cases;
  }

  private _loadEvalFile(relativePath: string): EvaluationCase[] {
    const fullPath = path.join(this.path, relativePath);
    if (!fs.existsSync(fullPath)) return [];
    const data = JSON.parse(fs.readFileSync(fullPath, 'utf-8'));
    if (Array.isArray(data)) return data as EvaluationCase[];
    if (data && typeof data === 'object' && 'evaluations' in data) {
      return (data as EvaluationSet).evaluations ?? [];
    }
    return [];
  }

  /** All content artifacts declared in the manifest. */
  get content(): ContentArtifact[] {
    return this.manifest.artifacts ?? this.manifest.content ?? [];
  }

  /**
   * Look up a content artifact by its ID (or path, if no explicit id was declared).
   *
   * @throws {Error} if no artifact with the given ID exists.
   */
  getArtifact(artifactId: string): ContentArtifact {
    const artifact = this.content.find(a => a.id === artifactId);
    if (!artifact) {
      throw new Error(`No artifact with id '${artifactId}' in pack '${this.packageId}'`);
    }
    return artifact;
  }

  /** The manifest's package_id, falling back to legacy id. */
  get packageId(): string | undefined {
    return this.manifest.package_id ?? this.manifest.id;
  }

  /**
   * Read the content of an artifact by ID.
   *
   * For text artifacts, use .text on the returned ArtifactContent.
   * For binary artifacts (images, etc.), use .buffer.
   */
  async read(artifactId: string): Promise<ArtifactContent> {
    const artifact = this.getArtifact(artifactId);
    const artifactPath = path.join(this.path, artifact.path);

    if (!fs.existsSync(artifactPath)) {
      throw new Error(`Artifact file not found: '${artifact.path}' in pack '${this.packageId}'`);
    }

    const buffer = fs.readFileSync(artifactPath);
    return makeArtifactContent(artifact, buffer);
  }

  /**
   * Read all artifacts with a specific semantic role.
   *
   * Common roles: "guide", "transcript", "workflow", "evaluation", "data", "image".
   */
  async readByRole(role: string): Promise<ArtifactContent[]> {
    const matching = this.content.filter(a => a.role === role);
    return Promise.all(matching.map(a => this.read(a.id)));
  }

  /**
   * Load a workflow artifact as a parsed JSON object.
   *
   * The workflow conforms to task.schema.json.
   *
   * @throws {Error} if the artifact is not application/json.
   */
  async getWorkflow(artifactId: string): Promise<Record<string, unknown>> {
    const artifact = this.getArtifact(artifactId);
    if (artifact.type !== 'application/json') {
      throw new Error(
        `Artifact '${artifactId}' has type '${artifact.type}', expected application/json`
      );
    }
    const content = await this.read(artifactId);
    return JSON.parse(content.text) as Record<string, unknown>;
  }

  /**
   * Validate this pack against the OKPF specification.
   *
   * Does not throw on validation failure — check result.valid instead.
   */
  validate(): ValidationResult {
    return validatePack(this.path);
  }

  toString(): string {
    return `Pack(packageId='${this.packageId}', version='${this.manifest.version}', domain='${this.manifest.domain}')`;
  }
}
