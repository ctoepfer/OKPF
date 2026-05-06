# Example Pack: Mechanic Diagnostics (Placeholder)

**Domain:** Automotive Repair  
**Status:** Placeholder — contributions welcome

---

## About This Pack (Planned)

This knowledge pack will cover systematic diagnostic procedures for common automotive problems. The goal is to encode the kind of expert reasoning a skilled mechanic uses when troubleshooting — not just repair steps, but the diagnostic thinking behind them.

## Planned Content

- **Symptom-to-diagnosis decision trees** — Starting from a symptom (e.g., "engine won't start", "brake pedal pulsates"), mapping to likely causes via structured logic
- **Diagnostic procedures** — Step-by-step procedures with tools required, safety considerations, and what each step rules in or out
- **OBD-II code reference** — Common diagnostic trouble codes with human-expert interpretation
- **Mechanic reasoning transcripts** — Recorded or reconstructed expert reasoning for complex cases
- **Safety checklists** — Pre-work and post-work verification checklists
- **Evaluation test cases** — Diagnostic scenarios with expected outcomes

## Example Topics

- Engine cranks but won't start
- Intermittent stalling
- Abnormal brake feel or noise
- Coolant loss without visible leak
- Electrical gremlins (intermittent faults)
- Transmission shift quality issues

## How to Contribute

If you have automotive expertise and want to contribute, see [CONTRIBUTING.md](../../CONTRIBUTING.md).

A valid contribution could be:
1. A single complete diagnostic procedure (e.g., "no-start diagnosis for a carbureted engine")
2. A structured decision tree for a symptom category
3. A set of evaluation test cases based on real cases (anonymized)

## Pack Structure (When Complete)

```
mechanic-diagnostics/
├── manifest.json
├── license.json
├── contributors.json
├── provenance.json
├── content/
│   ├── no-start-diagnosis.md
│   ├── brake-diagnosis.md
│   ├── obd2-codes.json
│   └── diagnostic-workflow.json
└── evaluations/
    └── test-cases.json
```
