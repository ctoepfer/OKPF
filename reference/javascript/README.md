# okpf-js — JavaScript/TypeScript Reference Implementation

A TypeScript library for reading and validating OKPF knowledge packs.

**Status:** Scoped parity with the Python reference — `Pack.load()` and
`validate()` work against real current-schema packs (directories only; see
Known gaps). No `PackBuilder`/pack-authoring API, no `ajv` JSON-Schema
validation yet — see Known gaps below.
**Node.js:** 18+
**Browser:** Not yet (planned, via bundler)

---

## Setup

```bash
cd reference/javascript
npm install
npm run build      # compiles src/ -> dist/
npx tsc --noEmit   # type-check without emitting
```

Not published to npm yet.

## Usage

```typescript
import { Pack } from 'okpf';

const pack = await Pack.load('./examples/software-onboarding/');

console.log(pack.packageId);      // "okpf-example-software-onboarding"
console.log(pack.displayName);    // manifest 'title' if set, else 'name'
console.log(pack.manifest.domain); // "software-engineering"
console.log(pack.capabilities);    // declared 'capabilities', if any

// Content
for (const artifact of pack.content) {
  console.log(artifact.id, artifact.path, artifact.role);
}
const guide = await pack.read(pack.content[0].id);
console.log(guide.text);

// Evaluations -- resolves file-reference entries
// ({"path": "evals/x.json"}) as well as inline evaluation objects.
for (const ev of pack.evaluations) {
  console.log(ev.question);
}

// Validation
const result = pack.validate();
console.log(result.valid);
```

`validate()` accepts `package_id`/`id` and `artifacts`/`content` aliasing,
same rule as the Python reference (`reference/python/okpf_validate.py`,
`reference/python/okpf/validate.py`).

## Known gaps

Tracked here instead of silently left stale, unlike this file's previous
version (which described a `KnowledgePack`/`PackBuilder` API that was
never actually built):

- **No `.kpack` archive support.** `Pack.load()` is directory-only. The
  Python reference (`reference/python/okpf/pack.py`) has this via a
  `PackageReader` abstraction (directory or ZIP) — porting that is the
  natural next step.
- **No `ajv` JSON-Schema validation.** `validate()` does the same
  hand-rolled required-field/safe-path/SHA-256 checks as the Python SDK
  validator, not full schema validation against
  `schemas/v0.1.0/manifest.schema.json`.
- **No `PackBuilder`/pack-authoring API.** Nothing here writes packs.
- **No test suite yet.** `jest`/`ts-jest` are configured in
  `package.json` but no `test/` directory exists. Verify changes with
  `npx tsc --noEmit` plus a manual script loading a real `examples/` pack
  (see Contributing) until a real suite exists.
- **No lint config.** `npm run lint` references `eslint` but neither an
  `eslint.config.js` nor the `eslint` package itself exist yet.

## File structure

```
reference/javascript/
├── README.md
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts   # type definitions + public exports
│   └── pack.ts    # Pack class, validate(), evaluation/artifact resolution
└── dist/          # build output (git-ignored)
```

## Contributing

Good first issues:

1. Port `.kpack` (ZIP) support from `reference/python/okpf/pack.py`.
2. Wire up `ajv`/`ajv-formats` (already devDependencies) against
   `schemas/v0.1.0/manifest.schema.json` for real JSON-Schema validation.
3. Set up `jest`/`ts-jest` and port `tests/test_pack_sdk.py`'s cases —
   that file exists specifically because `Pack.load()`/`Manifest` had
   **zero** test coverage against real example packs for a long time,
   which is exactly how the Python SDK silently drifted out of sync with
   the schema before. Any change here should be exercised against at
   least one real `examples/` pack, not just synthetic fixtures.
4. Add an `eslint.config.js` and the `eslint` package itself.

See [CONTRIBUTING.md](../../CONTRIBUTING.md) to get started.
