// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 OKPF Contributors
/**
 * Pack — primary entry point for loading and interacting with OKPF knowledge packs.
 *
 * Supports Node.js directory packs. ZIP (.kpack) archive support is planned.
 *
 * @example
 * import { Pack } from 'okpf';
 *
 * const pack = await Pack.load('./examples/brewing/');
 * console.log(pack.manifest.title);
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
  type: 'qa' | 'multiple-choice' | 'rubric' | 'benchmark' | 'checklist' | 'open-ended';
  question: string;
  difficulty?: 'beginner' | 'intermediate' | 'expert';
  expected_answer?: string | Record<string, unknown>;
  choices?: Array<{ id: string; text: string; correct?: boolean }>;
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

const REQUIRED_MANIFEST_FIELDS = [
  'okpf_version', 'id', 'name', 'version', 'domain', 'created', 'license', 'content',
] as const;

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

  packId = manifest['id'] as string | undefined;
  packVersion = manifest['version'] as string | undefined;

  for (const f of REQUIRED_MANIFEST_FIELDS) {
    if (!(f in manifest)) {
      errors.push({ path: 'manifest.json', message: `Missing required field: '${f}'`, severity: 'error' });
    }
  }

  const content = manifest['content'];
  if (!Array.isArray(content) || content.length === 0) {
    errors.push({ path: 'manifest.json#/content', message: 'Must be a non-empty array', severity: 'error' });
  } else {
    const seenIds = new Set<string>();
    content.forEach((artifact: Record<string, unknown>, i) => {
      const prefix = `manifest.json#/content[${i}]`;
      for (const req of ['id', 'path', 'type']) {
        if (!(req in artifact)) {
          errors.push({ path: prefix, message: `Missing required field: '${req}'`, severity: 'error' });
        }
      }
      const artId = artifact['id'] as string;
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

function parseManifest(data: Record<string, unknown>, basePath: string): Manifest {
  const resolvedLicense = resolveRef(data['license'], basePath) as Manifest['license'];
  return {
    ...(data as unknown as Manifest),
    license: resolvedLicense,
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

  /** Alias for manifest.name — convenience for AI system consumption. */
  get title(): string {
    return this.manifest.name;
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
   * Returns an empty array if no evaluations are present.
   */
  get evaluations(): EvaluationCase[] {
    const raw = (this.manifest as unknown as Record<string, unknown>)['evaluations'];
    if (!raw) return [];

    // May already be resolved (object with evaluations array) or a $ref
    const resolved = resolveRef(raw, this.path) as Record<string, unknown> | EvaluationCase[] | null;
    if (Array.isArray(resolved)) return resolved as EvaluationCase[];
    if (resolved && typeof resolved === 'object' && 'evaluations' in resolved) {
      return (resolved as EvaluationSet).evaluations ?? [];
    }
    return [];
  }

  /** All content artifacts declared in the manifest. */
  get content(): ContentArtifact[] {
    return this.manifest.content;
  }

  /**
   * Look up a content artifact by its ID.
   *
   * @throws {Error} if no artifact with the given ID exists.
   */
  getArtifact(artifactId: string): ContentArtifact {
    const artifact = this.manifest.content.find(a => a.id === artifactId);
    if (!artifact) {
      throw new Error(`No artifact with id '${artifactId}' in pack '${this.manifest.id}'`);
    }
    return artifact;
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
      throw new Error(`Artifact file not found: '${artifact.path}' in pack '${this.manifest.id}'`);
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
    const matching = this.manifest.content.filter(a => a.role === role);
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
    return `Pack(id='${this.manifest.id}', version='${this.manifest.version}', domain='${this.manifest.domain}')`;
  }
}
