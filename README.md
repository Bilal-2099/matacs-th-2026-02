# AI Proposal Triage Design

**Candidate:** Bilal Raza  
**Assessment reference:** `MATACS-TH-2026-02`  
**Actual time spent:** 57 mins

## Project overview

This repository contains my design response for an AI-assisted proposal-triage workflow. The approach uses AI to extract structured information from proposal documents, then applies deterministic Python rules to check mandatory requirements and calculate weighted scores. A human reviewer remains responsible for resolving flagged cases and making the final procurement decision.

The prototype is a small local script, not a deployed application.

## Repository contents

- [`WRITEUP.md`](WRITEUP.md) — design answers, scoring approach, review process, and safeguards.
- [`diagram/proposal-triage-flow.png`](diagram/proposal-triage-flow.png) — process-flow diagram.
- [`PROMPTS.md`](PROMPTS.md) — prompt used for proposal-field extraction.
- [`ranking.json`](ranking.json) — resulting proposal statuses, rankings, scores, and reasons.
- [`prototype/evaluate_proposals.py`](prototype/evaluate_proposals.py) — deterministic eligibility checks and scoring script.
- `prototype/` — sanitized input data used by the local prototype, if included.

## How to run the prototype

From the repository root, run:

```bash
python prototype/evaluate_proposals.py
```

The script reads `AI_analyze.json` from the current working directory by default and writes ranking.json there. To run it directly from the repository root, either place a copy of the sample input there or update the script's input and output paths to point to `prototype/AI_analyze.json` and `prototype/ranking.json`, respectively.

## Key design decisions

- **AI extracts; code decides.** AI is used to structure proposal information and identify missing or uncertain evidence. Python applies the explicit eligibility rules and weighted scoring formulas consistently.
- **Mandatory requirements are gates.** A proposal that fails a mandatory requirement is not included in the scored ranking. A proposal with an unresolved timeline is flagged for human review rather than assigned an assumed completion time.
- **Evidence and uncertainty matter.** Missing evidence is not treated as proof that a requirement is satisfied. Reviewers should be able to trace a result back to the extracted fields and source document in a controlled environment.
- **Human oversight is required.** The output supports review; it does not make the final procurement decision.

## AI-use disclosure

I used AI assistance to reason through the design, review scoring logic, and draft parts of the documentation. I reviewed the proposed logic and checked calculations rather than treating AI output as automatically correct.

For example, I checked the rounding of Proposal C's score against the underlying unrounded criterion values. The total is approximately 70.3376, which correctly rounds to 70.3 to one decimal place. This illustrates why calculated outputs should be validated against the implementation rather than inferred from displayed, rounded components.

AI-generated extraction and analysis are not treated as authoritative. The prototype's rules and outputs should be verified, and a human reviewer must investigate flagged or uncertain cases before any procurement decision.

## Limitations

This is a design exercise and a small local prototype. It is not production-ready. A production system would need stronger input validation, versioned criteria and weights, secure document handling, persistent audit logs, access controls, tests for edge cases, and a documented human-review process. Any real proposal documents and identifying information should be kept out of this public repository.
