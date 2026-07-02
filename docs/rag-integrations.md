<!-- SPDX-License-Identifier: Apache-2.0 -->

# Loading `rag.jsonl` into common frameworks

These snippets are illustrative, not tested against installed libraries —
none of these packages are OKPF dependencies (OKPF Core stays
infrastructure- and vendor-neutral; see [docs/rag-export.md](rag-export.md)
for the field contract these snippets rely on). Install whichever
framework you actually use.

First, generate the export:

```bash
PYTHONPATH=reference/python python3 -m okpf export-rag examples/software-onboarding rag.jsonl
```

## Plain JSONL (no framework)

```python
import json

with open("rag.jsonl", encoding="utf-8") as f:
    for line in f:
        row = json.loads(line)
        if not row["usage_policy"].get("allow_rag", True):
            continue
        index_chunk(
            text=row["text"],
            id=row["chunk_id"],
            metadata={k: v for k, v in row.items() if k != "text"},
        )
```

## LangChain

```python
# pip install langchain-core
import json
from langchain_core.documents import Document

documents = []
with open("rag.jsonl", encoding="utf-8") as f:
    for line in f:
        row = json.loads(line)
        if not row["usage_policy"].get("allow_rag", True):
            continue
        documents.append(
            Document(
                page_content=row["text"],
                metadata={
                    "id": row["chunk_id"],
                    "source": row["artifact_path"],
                    "citation": row["citation"],
                    "license": row["license"],
                    "package_id": row["package_id"],
                    "package_version": row["package_version"],
                },
            )
        )
# vector_store.add_documents(documents)
```

## LlamaIndex

```python
# pip install llama-index-core
import json
from llama_index.core import Document

documents = []
with open("rag.jsonl", encoding="utf-8") as f:
    for line in f:
        row = json.loads(line)
        if not row["usage_policy"].get("allow_rag", True):
            continue
        documents.append(
            Document(
                text=row["text"],
                doc_id=row["chunk_id"],
                metadata={
                    "source": row["artifact_path"],
                    "citation": row["citation"],
                    "license": row["license"],
                },
            )
        )
# index = VectorStoreIndex.from_documents(documents)
```

## Generic vector store upsert (e.g. an OpenAI-compatible store)

```python
import json

with open("rag.jsonl", encoding="utf-8") as f:
    rows = [json.loads(line) for line in f]

rows = [r for r in rows if r["usage_policy"].get("allow_rag", True)]

vector_store.upsert(
    ids=[r["chunk_id"] for r in rows],
    texts=[r["text"] for r in rows],
    metadatas=[
        {
            "sha256": r["sha256"],
            "citation": r["citation"],
            "package_id": r["package_id"],
            "package_version": r["package_version"],
            "license_type": (r["license"] or {}).get("type"),
        }
        for r in rows
    ],
)
```

Because `chunk_id` is deterministic and identity-based, re-running
`export-rag` after a content edit and re-upserting is a safe update, not a
duplicate insert — compare each row's `sha256` to skip unchanged chunks.
