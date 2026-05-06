# okpf-js — JavaScript/Node Reference Implementation

A JavaScript library for reading, validating, and creating OKPF knowledge packs.

**Status:** Stub / Work in Progress  
**Node.js:** 18+  
**Browser:** Yes (planned, via bundler)

---

## Installation (planned)

```bash
npm install okpf
```

---

## Planned API

### Reading a Pack

```javascript
import { KnowledgePack } from 'okpf';

// Open a pack directory or .kpack archive
const pack = await KnowledgePack.open('./examples/brewing/');

console.log(pack.name);          // "Water Chemistry for Brewing"
console.log(pack.version);       // "0.1.0"
console.log(pack.license.spdx);  // "CC-BY-4.0"

// Iterate over content
for (const artifact of pack.content) {
  console.log(`${artifact.id}: ${artifact.path} (${artifact.type})`);
}

// Read a specific artifact
const guide = await pack.read('guide');
console.log(guide.text); // Markdown content
```

### Validating a Pack

```javascript
import { validate } from 'okpf';

const result = await validate('./examples/brewing/');

if (result.valid) {
  console.log('Pack is valid');
} else {
  for (const error of result.errors) {
    console.error(`  ${error.path}: ${error.message}`);
  }
}
```

### Creating a Pack

```javascript
import { PackBuilder } from 'okpf';

const builder = new PackBuilder({
  name: 'My Knowledge Pack',
  domain: 'my-domain',
  version: '0.1.0',
});

builder.setLicense('CC-BY-4.0', { use: 'open', redistribution: 'open' });
builder.addContributor({ name: 'Jane Smith', role: 'author' });
builder.addContent('content/guide.md', { id: 'guide', role: 'guide' });

const pack = await builder.build();
await pack.save('my-pack.kpack');
```

---

## File Structure (planned)

```
reference/javascript/
├── README.md
├── package.json
├── src/
│   ├── index.ts          # Public API exports
│   ├── pack.ts           # KnowledgePack class
│   ├── manifest.ts       # Manifest parsing and validation
│   ├── license.ts        # License handling
│   ├── provenance.ts     # Provenance records
│   ├── contributors.ts   # Contributor records
│   ├── evaluations.ts    # Evaluation support
│   ├── builder.ts        # PackBuilder
│   └── validate.ts       # Validation logic
└── test/
    ├── pack.test.ts
    ├── validate.test.ts
    └── builder.test.ts
```

---

## Contributing

The JavaScript reference implementation needs contributors. Good first issues:

1. Implement `KnowledgePack.open()` using Node.js `fs` module
2. Implement manifest JSON Schema validation using `ajv`
3. Implement SHA-256 hash verification with Node.js `crypto`
4. Write TypeScript types for all OKPF schemas
5. Write tests against the brewing example pack

See [CONTRIBUTING.md](../../CONTRIBUTING.md) to get started.
