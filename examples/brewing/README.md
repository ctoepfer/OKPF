# Example Pack: Water Chemistry for Brewing

**Domain:** Brewing  
**OKPF Version:** 0.1.0  
**Pack Version:** 0.1.0  
**License:** CC BY 4.0

---

## About This Pack

This is a complete example OKPF knowledge pack demonstrating the format using the domain of brewing water chemistry. It covers:

- The role of mineral ions in brewing
- Classic regional water profiles
- How to adjust your water for different beer styles
- A step-by-step adjustment workflow
- Test cases to evaluate comprehension

## Pack Contents

| File | Description |
|------|-------------|
| `manifest.json` | Pack descriptor |
| `license.json` | CC BY 4.0 license |
| `contributors.json` | Attribution records |
| `provenance.json` | Provenance record |
| `content/guide.md` | Full brewing water chemistry guide |
| `content/mineral-chart.json` | Ion contributions per mineral addition |
| `content/water-profiles.json` | Classic regional water profiles |
| `content/adjustment-workflow.json` | Structured water adjustment workflow |
| `evaluations/test-cases.json` | 7 test cases covering the guide content |

## How to Use This as a Reference

This pack is a fully-formed example of the OKPF format. When building your own pack:

1. Copy the directory structure
2. Update `manifest.json` with your own `id`, `name`, `domain`, `version`, and `content` entries
3. Update `license.json` to reflect your chosen license
4. Replace the content files with your own expertise
5. Add evaluation test cases to verify knowledge quality

## Validating This Pack

```bash
# Using the OKPF validator (once available)
okpf validate examples/brewing/

# Or validate the manifest schema manually
python -m jsonschema -i examples/brewing/manifest.json schemas/v0.1.0/manifest.schema.json
```
