# Registry Indexes

OKPF itself is not a marketplace or registry. It defines a portable package format.

Future registries may expose simple machine-readable indexes so tools can discover available packs. This is informational and not required for OKPF v0.1.0.

Example:

```json
{
  "okpf_registry_version": "0.1.0",
  "packs": [
    {
      "id": "org.example.brewing-basics",
      "title": "Brewing Basics",
      "version": "0.1.0",
      "url": "https://example.org/packs/brewing-basics.kpack",
      "sha256": "..."
    }
  ]
}
```

Validators are not required to fetch registry indexes or resolve remote package URLs.
