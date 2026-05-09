# Summit Pale Ale Recipe Pack

An OKPF knowledge pack containing a complete homebrew recipe for Summit Pale Ale — a 5-gallon American Pale Ale showcasing Cascade and Centennial hops.

This pack demonstrates multiple artifact roles: a recipe document for RAG retrieval, structured ingredient data, a prompt template for recipe adjustment, and evaluation questions for benchmarking.

## Contents

| File | Role | Description |
|------|------|-------------|
| `content/recipe.md` | `rag_source` | Full recipe: grain bill, hops, yeast, mash, fermentation |
| `content/ingredients.json` | `data` | Machine-readable structured ingredient data |
| `prompts/recipe-adjustment.md` | `prompt_template` | LLM prompt template for recipe adjustment questions |
| `evals/basic-recipe-questions.jsonl` | `evaluation` | 8 evaluation questions (beginner + intermediate) |

## Recipe Summary

| Parameter | Value |
|-----------|-------|
| Style | American Pale Ale |
| Batch size | 5 US gallons |
| OG | 1.052 |
| FG | 1.012 |
| ABV | ~5.2% |
| IBU | 38 |

## Using this pack with a RAG system

1. Chunk `content/recipe.md` into sections (each heading makes a natural chunk boundary)
2. Embed chunks and store in a vector database
3. Use `prompts/recipe-adjustment.md` as the system prompt template
4. Use `evals/basic-recipe-questions.jsonl` to benchmark retrieval quality

## Validating this pack

From the repository root:

```bash
python reference/python/okpf_validate.py examples/homebrew-recipe-pack
```

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — see `license.json` for machine-readable details. This is an original recipe; attribution is appreciated but not legally required for home brewing use.
